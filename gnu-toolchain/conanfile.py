# ====================================================================================================================================
# @file       conanfile.py
# @author     Krzysztof Pierczyk (krzysztof.pierczyk@gmail.com)
# @maintainer Krzysztof Pierczyk (krzysztof.pierczyk@gmail.com)
# @date       Tuesday, 1st October 2024 9:10:18 am
# @modified   Tuesday, 1st October 2024 8:49:26 pm by Krzysztof Pierczyk (you@you.you)
# 
# 
# @copyright Krzysztof Pierczyk © 2024
# ====================================================================================================================================

import pathlib
import sys

# Add src/ directory to the sys.path
sys.path.append(str(pathlib.Path(__file__).parent / "src"))

# ========================================================== Requirements ========================================================== #

from sys import version_info

# Require Python version >= 3.12
assert version_info >= (3, 12), "Python 3.12 or newer is required"

# Require Conan version >= 2.0.0
required_conan_version = '>=2.0.0'

# ============================================================ Imports ============================================================= #

# Conan imports
from conan import ConanFile
# Package imports
from gnu_toolchain.from_source import FromSourceDriver
from gnu_toolchain.prebuilt    import PrebuiltDriver

# ============================================================ Script ============================================================== #

class GnuToolchainConan(ConanFile):
    
    name        = 'gnu-toolchain'
    version     = '0.0.1'
    license     = 'MIT'
    author      = 'Krzysztof Pierczyk'
    description = 'Conan package providing fully functional GNU toolchain'
    homepage    = 'https://github.com/kpierczy/cpp-toolchains/gnu-toolchain'
    topics      = [ 'gcc', 'g++', 'binutils', 'libc', 'libstdc++' ]

    # ------------------------------------------------------------------ #
    
    settings = [ 'os', 'compiler', 'build_type', 'arch' ]

    # ------------------------------------------------------------------ #

    options = {

        'prebuilt' : [ True, False ],

        # Common config
        'with_config' : [ 'ANY' ],
        'with_doc'    : [ True, False ],

        # Dependencies versions
        "with_zlib_version"     : [ 'ANY' ],
        "with_gmp_version"      : [ 'ANY' ],
        "with_mpfr_version"     : [ 'ANY' ],
        "with_mpc_version"      : [ 'ANY' ],
        "with_isl_version"      : [ 'ANY' ],
        "with_elfutils_version" : [ 'ANY' ],
        "with_expat_version"    : [ 'ANY' ],
        # Versions
        "with_binutils_version" : [ 'ANY' ],
        "with_gcc_version"      : [ 'ANY' ],
        "with_glibc_version"    : [ 'ANY' ],
        "with_newlib_version"   : [ 'ANY' ],
        "with_gdb_version"      : [ 'ANY' ],
                
        # Source
        "with_binutils_url" : [ 'ANY' ],
        "with_gcc_url"      : [ 'ANY' ],
        "with_glibc_url"    : [ 'ANY' ],
        "with_newlib_url"   : [ 'ANY' ],
        "with_gdb_url"      : [ 'ANY' ],
        
    }

    default_options = {

        'prebuilt' : False,
        
        # Common config
        'with_config' : None,
        'with_doc'    : True,

        # Dependencies versions
        "with_zlib_version"     : "[>=1.2.11]",
        "with_gmp_version"      : "[>=6.2.1]",
        "with_mpfr_version"     : "[>=4.1.0 <=4.2.0]",
        "with_mpc_version"      : "[>=1.2.1]",
        "with_isl_version"      : "[>=0.18]",
        "with_elfutils_version" : "[>=0.186]",
        "with_expat_version"    : "[>=2.4.6]",
        # Versions
        "with_binutils_version" : "2.43",
        "with_gcc_version"      : "14.2.0",
        "with_glibc_version"    : "2.34",
        "with_newlib_version"   : "4.2.0.20211231",
        "with_gdb_version"      : "11.1",
                
        # Source
        "with_binutils_url" : "https://ftp.gnu.org/gnu/binutils/binutils-{version}.tar.gz",
        "with_gcc_url"      : "https://ftp.gnu.org/gnu/gcc/gcc-{version}/gcc-{version}.tar.gz",
        "with_glibc_url"    : "https://ftp.gnu.org/gnu/glibc/glibc-{version}.tar.gz",
        "with_newlib_url"   : "ftp://sourceware.org/pub/newlib/newlib-{version}.tar.gz",
        "with_gdb_url"      : "https://ftp.gnu.org/gnu/gdb/gdb-{version}.tar.gz",
        
    }

    # ------------------------------------------------------------------ #

    exports = [
        "data/*.py",
        "src/**/*.py",
    ]

    # ---------------------------------------------------------------------------- #

    @property
    def _impl(self):
        if self.options.prebuilt:
            return PrebuiltDriver(self, version = self.options.with_gcc_version)
        else:
            return FromSourceDriver(self)

    # ---------------------------------------------------------------------------- #

    def configure(self):
        self._impl.configure()

    def requirements(self):
        self._impl.requirements()

    def layout(self):
        self._impl.layout()

    def generate(self):
        self._impl.generate()

    def build(self):
        self._impl.build()

    def package(self):
        self._impl.package()

    def package_info(self):
        self._impl.package_info()
        
    def package_id(self):

        # Compiler and build type are not important for prebuilt packages
        self.info.settings.rm_safe("compiler")
        self.info.settings.rm_safe("build_type")

        # For prebuilt packages, remove all options except for the 'prebuilt' and 'with_gcc_version'
        if self.info.options.prebuilt:
            for opt in GnuToolchainConan.options.keys():
                if opt != 'prebuilt' and opt != 'with_gcc_version':
                    self.info.options.rm_safe(opt)

# ================================================================================================================================== #
