# ====================================================================================================================================
# @file       from_source.py
# @author     Krzysztof Pierczyk (krzysztof.pierczyk@gmail.com)
# @maintainer Krzysztof Pierczyk (krzysztof.pierczyk@gmail.com)
# @date       Tuesday, 1st October 2024 7:01:52 pm
# @modified   Sunday, 13th October 2024 11:39:33 am by Krzysztof Pierczyk (krzysztof.pierczyk@gmail.com)
# 
# 
# @copyright Your Company © 2024
# ====================================================================================================================================

# ============================================================ Imports ============================================================= #

# Standard imports
import pathlib
from importlib.machinery import SourceFileLoader
# Conan imports
from conan.tools.layout import basic_layout
from conan.tools.files import copy
from conan.tools.gnu import AutotoolsToolchain
from conan.tools.system.package_manager import Apt
# Package imports
from gnu_toolchain.components import *
from gnu_toolchain.utils.autotools import AutotoolsPackage

# ======================================================== FromSourceDriver ======================================================== #

class FromSourceDriver():

    def __init__(self, conanfile):
        self.conanfile = conanfile

    # ------------------------------------------------------------------ #

    options = {

        # Common config
        'with_doc' : [ True, False ],

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

        # Common config
        'with_doc' : True,

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
        "with_gdb_version"      : "15.1",
                
        # Source
        "with_binutils_url" : "https://ftp.gnu.org/gnu/binutils/binutils-{version}.tar.gz",
        "with_gcc_url"      : "https://ftp.gnu.org/gnu/gcc/gcc-{version}/gcc-{version}.tar.gz",
        "with_glibc_url"    : "https://ftp.gnu.org/gnu/glibc/glibc-{version}.tar.gz",
        "with_newlib_url"   : "ftp://sourceware.org/pub/newlib/newlib-{version}.tar.gz",
        "with_gdb_url"      : "https://ftp.gnu.org/gnu/gdb/gdb-{version}.tar.gz",
        
    }

    # ---------------------------------------------------------------------------- #

    def configure(self):
        pass

    def validate(self):

        # On Windows only GCC is supported (MinGW)
        if self.conanfile.settings.os == 'Windows':
            if self.conanfile.settings.compiler != 'gcc':
                raise ValueError(f"On Windows only GCC (MinGW) is supported as a host compiler (current compiler: {self.conanfile.settings.compiler})")

    def system_requirements(self):

        if self.conanfile.settings.os == 'Linux':
            Apt(self.conanfile).install([
                "texinfo",
                "texlive",
                "libncurses-dev",
                "python3-dev",
            ], update=True, check=True)

    def requirements(self):

        def requires_dep(dep):

            # Get dependency version
            dep_version = getattr(self.conanfile.options, f"with_{dep}_version")
            # Add dependency
            self.conanfile.requires(f"{dep}/{dep_version}",
                options = self._description.dependencies.get_options(dep)
            )

        # Specify dependencies
        requires_dep('zlib')
        requires_dep('gmp')
        requires_dep('mpfr')
        requires_dep('mpc')
        requires_dep('isl')
        requires_dep('expat')
        # Specify non-Windows specific dependencies
        if self.conanfile.settings.os != 'Windows':
            requires_dep('elfutils')

    def layout(self):
        basic_layout(self.conanfile, src_folder = "src")

    def generate(self):
        
        """
        Note
        ----
        We need to hack some of the internals of the generator to avoid generationg flags that should be 
        specified by the toolchain descriptor itself and that are generated by Conan bye defualt based
        on the package's binary settings. These involve:

           - target architecture flags (-m32, -m64)
           - optimization flags (-Ox)
           - NDEBUG flag
           - C++11 ABI flag (-D_GLIBCXX_USE_CXX11_ABI=0), this one is specially venomous when used
             unawarely as it leads to random linker failures when buiulding full GCC as some of the
             files are built using the new, and some using the old ABI.

        """

        toolchain = AutotoolsToolchain(
            conanfile = self.conanfile,
        )

        # Hack the generator
        toolchain.arch_flag             = None
        toolchain.ndebug                = None
        toolchain.cppstd                = None
        toolchain.gcc_cxx11_abi         = None
        toolchain.build_type_flags      = [ ]
        toolchain.build_type_link_flags = [ ]

        # Generate autotools toolchain
        toolchain.generate()

    def build(self):
        for component_description in self._description.components:
            component_description.make_driver(
                conanfile   = self.conanfile,
                target      = self._description.target,
                pkg_version = self._description.pkg_version,
            ).build()

    def package(self):
        copy(self.conanfile,
            pattern = '*',
            src     = AutotoolsPackage.make_dirs(self.conanfile).prefix.as_posix(),
            dst     = self.conanfile.package_folder,
        )
    
    def package_info(self):
        pass
        
    # ---------------------------------------------------------------------------- #

    @property
    def _description(self):

        # If config has not been loaded, load it
        if not hasattr(self, '_description_cache'):

            description_file = pathlib.Path(self.conanfile.recipe_folder) / "data" / (str(self.conanfile.options.target) + ".py")

            # Check if target description file exists
            if not description_file.exists():
               raise FileNotFoundError(f"Description file for the '{self.conanfile.options.target}' target does not exist!")

            self._description_cache = SourceFileLoader(
                'config_module',
                description_file.as_posix()
            ).load_module().Description(
                self.conanfile
            )

        return self._description_cache

# ================================================================================================================================== #
