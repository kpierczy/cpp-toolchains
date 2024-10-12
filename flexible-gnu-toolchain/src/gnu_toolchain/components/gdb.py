# ====================================================================================================================================
# @file       gdb.py
# @author     Krzysztof Pierczyk (krzysztof.pierczyk@gmail.com)
# @maintainer Krzysztof Pierczyk (krzysztof.pierczyk@gmail.com)
# @date       Tuesday, 1st October 2024 11:40:43 am
# @modified   Sunday, 13th October 2024 1:04:14 am by Krzysztof Pierczyk (krzysztof.pierczyk@gmail.com)
# 
# 
# @copyright Your Company © 2024
# ====================================================================================================================================

# ============================================================= Imports ============================================================ #

# System imports
import pathlib
import os
# Private imports
from gnu_toolchain.utils.autotools import AutotoolsPackage

# =============================================================== Gdb ============================================================== #

class Gdb(AutotoolsPackage):
    
    def build(self):
        
        # Extend the config with the GDB specific options
        self.description.config += [
            
            f"--with-pkgversion={self.pkg_version}",
            f"--program-prefix={self.target}-",

            f"--with-gmp={pathlib.Path(self.conanfile.dependencies['gmp'].package_folder).as_posix()}",
            f"--with-mpfr={pathlib.Path(self.conanfile.dependencies['mpfr'].package_folder).as_posix()}",
            f"--with-mpc={pathlib.Path(self.conanfile.dependencies['mpc'].package_folder).as_posix()}",
            f"--with-isl={pathlib.Path(self.conanfile.dependencies['isl'].package_folder).as_posix()}",

            f"--with-expat",
            f"--with-libexpat-prefix={pathlib.Path(self.conanfile.dependencies['expat'].package_folder).as_posix()}",
            f"--with-libgmp-prefix={pathlib.Path(self.conanfile.dependencies['gmp'].package_folder).as_posix()}",

            f"--with-system-gdbinit={self.dirs.prefix.as_posix()}/{self._get_host_triplet(self.conanfile)}/{self.target}/lib/gdbinit",
            
        ]

        # Compile components to be disabled on current platform
        disabled_modules = {
            
            'Windows' : [ 'sim', 'tui' ],

        }.get(str(self.conanfile.settings.os), None)
        
        # Disable components
        if disabled_modules and not self._has_step_tag('configure'):
            self.conanfile.output.warning(f"Building GDB on {self.conanfile.settings.os}. The following components will be disabled:")
            for module in disabled_modules:
                self.conanfile.output.warning(f"  - {module}")
                self.description.config += [ f"--disable-{module}" ]

        # Extend the environment to let the GDB find the zlib
        os.environ["CFLAGS"]  = f"{os.environ.get('CFLAGS', '')}  -I{pathlib.Path(self.conanfile.dependencies['zlib'].package_folder).as_posix()}/include"
        os.environ["LDFLAGS"] = f"{os.environ.get('LDFLAGS', '')} -L{pathlib.Path(self.conanfile.dependencies['zlib'].package_folder).as_posix()}/lib"

        # Build the project with Python integration
        super().build(
            
            doc_install_targets = [
                'install-html install-pdf',
            ] if self.conanfile.settings.os != 'Windows' else [
                'install-pdf',
            ],

            # Force C++17 from GDB 15.0 onwards
            envs = {
                'CXXFLAGS' : f'{os.environ.get("CXXFLAGS", "")} ' + (
                    '-std=gnu++17'
                        if (self.description.version.major >= 15) else
                    ''
                )
            },
            
        )
                                          
# ================================================================================================================================== #
