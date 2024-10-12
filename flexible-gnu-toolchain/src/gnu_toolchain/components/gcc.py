# ====================================================================================================================================
# @file       gcc.py
# @author     Krzysztof Pierczyk (krzysztof.pierczyk@gmail.com)
# @maintainer Krzysztof Pierczyk (krzysztof.pierczyk@gmail.com)
# @date       Tuesday, 1st October 2024 11:40:43 am
# @modified   Sunday, 13th October 2024 12:41:02 am by Krzysztof Pierczyk (krzysztof.pierczyk@gmail.com)
# 
# 
# @copyright Your Company © 2024
# ====================================================================================================================================

# ============================================================= Imports ============================================================ #

# Standard imports
import os
import subprocess
import re
import pathlib
# Private imports
from gnu_toolchain.utils.autotools import AutotoolsPackage

# =============================================================== Gcc ============================================================== #

class Gcc(AutotoolsPackage):

    def _extend_path(self):

        """Extends Path with the <prefix>/bin directory if not already present"""

        bin_dir = self.dirs.prefix / 'bin'

        # If the path does not contain the install directory, prepend it
        if not bin_dir.as_posix() in os.environ["PATH"]:
            os.environ["PATH"] = f"{bin_dir.as_posix()}{os.pathsep}{os.environ['PATH']}"

    def build(self):

        # Build the LibC, if present
        if self.description.libc is not None:

            # Get copy of the libc descriptor
            libc_descriptor = self.description.libc

            # Resolve target files path patterns, if present
            if self.description.libc.target_files is not None:
                libc_descriptor.target_files = self._resolve_target_files(
                    libc_descriptor.target_files
                )

            # Build the LibC
            libc_descriptor.make_driver(
                conanfile   = self.conanfile,
                target      = self.target,
                pkg_version = self.pkg_version,
            ).build()

        # Resolve target files path patterns, if present
        if self.description.target_files is not None:
            self.description.target_files = self._resolve_target_files(
                self.description.target_files
            )

        # Add basic GCC options
        self.description.config += [
            
            f"--with-pkgversion={self.pkg_version}",

            f"--with-gmp={pathlib.Path(self.conanfile.dependencies['gmp'].package_folder).as_posix()}",
            f"--with-mpfr={pathlib.Path(self.conanfile.dependencies['mpfr'].package_folder).as_posix()}",
            f"--with-mpc={pathlib.Path(self.conanfile.dependencies['mpc'].package_folder).as_posix()}",
            f"--with-isl={pathlib.Path(self.conanfile.dependencies['isl'].package_folder).as_posix()}",
            
            f"--libexecdir={self.dirs.prefix.as_posix()}/lib",
            f"--with-python-dir=share/gcc-{self.target}",
            
        ]

        # Add non-Windows specific options
        if self.conanfile.settings.os != 'Windows':
            self.description.config += [
                f"--with-libelf={pathlib.Path(self.conanfile.dependencies['elfutils'].package_folder).as_posix()}",
            ]

        # Add options depending on whether we build in-tree or out-of-tree
        if self.description.target_files is None:
            self.description.config += [
                f"--with-sysroot={self.dirs.prefix.as_posix()}/{self.target}",
            ]
        else:
            self.description.config += [
                f"--with-sysroot={self.dirs.offprefix.as_posix()}/{self.target}",
            ]

        # Pick targets to be built
        targets = { } if self.description.full_build else {
            'target' :         'all-gcc',
            'install_target' : 'install-gcc',
        }

        # Create symbolic link to the <install_dir> from <install_dir>/<target>/usr
        usr_dir = self.dirs.prefix / self.target / 'usr'
        if usr_dir.exists():
            usr_dir.unlink()
        try:
            usr_dir.symlink_to(self.dirs.prefix)
        except Exception as e:
            self.conanfile.output.error(
                f"Failed to create symbolic link to the <install_dir> from <install_dir>/<target>/usr ({e}). " + 
                f"If you are on Windows, you may need to enable Developer Mode in the Windows Settings. for symlink creation to work.")
            raise

        # Build the project
        super().build(
                      
            **targets,
                      
            doc_install_targets = [
                'install-html install-pdf',
            ] if self.conanfile.settings.os != 'Windows' else [
                'install-html',
            ],

            # GCC does not handle parallel doc installation very well on Linux
            doc_install_args = ([ '-j1' ] if (self.conanfile.settings.os == 'Linux') else None),

            # Force C++11 (see GCC prerequisites, @note MSYS/MinGW GCC requires GNU extensions to make __POSIX_VISIBLE defined)
            envs = {
                'CXXFLAGS' : f'{os.environ.get("CXXFLAGS", "")} ' + (
                    '-std=gnu++11'
                        if (self.conanfile.settings.os == 'Windows') else
                    '-std=c++11'
                )
            },

        )

        # Prepend PATH with the new GCC
        self._extend_path()
        
    # ---------------------------------------------------------------------------- #

    def _get_multilib_dirs(self):

        gcc_path = self.dirs.prefix / 'bin' / f'{self.target}-gcc'

        # Run the GCC to get the list of multilib dirs
        result = subprocess.run([
            gcc_path.as_posix(), '-print-multi-lib'
        ],
            check  = True,
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE,
        )

        multilib_dirs = []
        
        # Parse the output (remove ';' and everything after it; prepend with the <target>/lib)
        for line in result.stdout.decode().splitlines():
            multilib_dir_pattern = re.sub(r';.*', '', line)
            if multilib_dir_pattern == '.':
                multilib_dir_pattern = f'{self.target}/lib'
            else:
                multilib_dir_pattern = f'{self.target}/lib/{multilib_dir_pattern}'
            multilib_dirs.append(multilib_dir_pattern)

        return multilib_dirs    

    def _resolve_target_files(self,
        target_files,
    ):
        # Prepare mappings
        mappings = {
            '{multilib_dir}' : self._get_multilib_dirs(),
        }
        
        result = { }

        # Resolve the target files
        for src, dst in target_files.items():
            for pattern, replacements in mappings.items():
                for replacement in replacements:
                    
                    # Resolve the src and dst paths
                    resolved_src = src.replace(pattern, replacement)
                    resolved_dst = dst.replace(pattern, replacement)
                    # Add the resolved pair to the result
                    result[resolved_src] = resolved_dst

        return result

# ================================================================================================================================== #
