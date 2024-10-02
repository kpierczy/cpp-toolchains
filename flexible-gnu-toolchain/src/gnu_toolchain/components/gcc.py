# ====================================================================================================================================
# @file       gcc.py
# @author     Krzysztof Pierczyk (you@you.you)
# @maintainer Krzysztof Pierczyk (you@you.you)
# @date       Tuesday, 1st October 2024 11:40:43 am
# @modified   Wednesday, 2nd October 2024 1:02:02 pm by Krzysztof Pierczyk (you@you.you)
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

    def _extend_path(self,
        conanfile,
    ):

        """Extends Path with the <prefix>/bin directory if not already present"""

        bin_dir = self.get_dirs(conanfile).prefixed_install_dir / 'bin'

        # If the path does not contain the install directory, prepend it
        if not bin_dir.as_posix() in os.environ["PATH"]:
            os.environ["PATH"] = f"{bin_dir.as_posix()}{os.pathsep}{os.environ['PATH']}"

    def build(self,
        conanfile,
    ):
        # Build the LibC, if present
        if self.description.libc is not None:

            # Get copy of the libc descriptor
            libc_descriptor = self.description.libc

            # Resolve target files path patterns, if present
            if self.description.libc.target_files is not None:
                libc_descriptor.target_files = self._resolve_libc_target_files(
                    conanfile,
                    libc_descriptor.target_files
                )

            # Build the LibC
            libc_descriptor.make_driver(
                target      = self.target,
                pkg_version = self.pkg_version,
            ).build(
                conanfile,
            )

        # Add basic GCC options
        self.description.config += [
            
            f"--with-pkgversion={self.pkg_version}",

            f"--with-gmp={conanfile.dependencies["gmp"].package_folder}",
            f"--with-mpfr={conanfile.dependencies["mpfr"].package_folder}",
            f"--with-mpc={conanfile.dependencies["mpc"].package_folder}",
            f"--with-isl={conanfile.dependencies["isl"].package_folder}",
            f"--with-libelf={conanfile.dependencies["elfutils"].package_folder}",
            
            f"--libexecdir=${{prefix}}/lib",
            f"--with-python-dir=share/gcc-{self.target}",
            
        ]

        # Compute rel between in-tree and out-of-tree build dirs
        off_install_rel_to_install = self.get_dirs(conanfile).off_install_rel_to_install

        # Add options depending on whether we build in-tree or out-of-tree
        if self.description.target_files is None:
            self.description.config += [

                f"--with-sysroot=${{prefix}}/{self.target}",

            ]
        else:
            self.description.config += [

                f"--prefix={off_install_rel_to_install.as_posix()}",
                f"--with-sysroot=${{prefix}}/{off_install_rel_to_install.as_posix()}/{self.target}",

            ]

        # Pick targets to be built
        targets = { } if self.description.full_build else {
            'target' :         'all-gcc',
            'install_target' : 'install-gcc',
        }

        # Create symbolic link to the <install_dir> from <install_dir>/<target>/usr
        install_dir = self.get_dirs(conanfile).prefixed_install_dir
        usr_dir = install_dir / self.target / 'usr'
        if usr_dir.exists():
            usr_dir.unlink()
        usr_dir.symlink_to(install_dir)

        # Build the project
        super().build(conanfile,
                      
            **targets,
                      
            doc_install_targets = [
                'install-html install-pdf',
            ],

        )

        # Prepend PATH with the new GCC
        self._extend_path(conanfile)
        
    # ---------------------------------------------------------------------------- #

    def _get_multilib_dirs(self,
                           conanfile
    ):
        gcc_path = self.get_dirs(conanfile).prefixed_install_dir / 'bin' / f'{self.target}-gcc'

        # Run the GCC to get the list of multilib dirs
        result = subprocess.run([
            gcc_path.as_posix(), '-print-multi-lib'
        ],
            check  = True,
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE,
        )

        multilib_dirs = []

        # Parse the output (replce the (;.*) suffix of each line with the '*' wildcard)
        for line in result.stdout.decode().splitlines():
            multilib_dirs.append(re.sub(r';.*', '*', line))

        return multilib_dirs    

    def _resolve_libc_target_files(self,
        conanfile,
        target_files,
    ):
        # Prepare mappings
        mappings = {
            '{multilib_dir}' : self._get_multilib_dirs(conanfile),
        }
        
        result = { }

        # Resolve the target files
        for src, dst in target_files.items():
            for pattern, mappings in mappings.items():
                for mapping in mappings:

                    # Resolve the src and dst paths
                    resolved_src = pathlib.Path(src.as_posix().replace(pattern, mapping))
                    resolved_dst = pathlib.Path(dst.as_posix().replace(pattern, mapping))
                    # If something has changed, add the resolved pair to the result
                    if (src != resolved_src) or (dst != resolved_dst):
                        result[resolved_src] = resolved_dst

        return result

# ================================================================================================================================== #
