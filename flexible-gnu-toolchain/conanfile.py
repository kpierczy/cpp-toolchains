# ====================================================================================================================================
# @file       conanfile.py
# @author     Krzysztof Pierczyk (krzysztof.pierczyk@gmail.com)
# @maintainer Krzysztof Pierczyk (krzysztof.pierczyk@gmail.com)
# @date       Tuesday, 1st October 2024 9:10:18 am
# @modified   Saturday, 12th October 2024 10:52:44 pm by Krzysztof Pierczyk (krzysztof.pierczyk@gmail.com)
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

# Require Python version >= 3.11
assert version_info >= (3, 11), "Python 3.11 or newer is required"

# Require Conan version >= 2.0.0
required_conan_version = '>=2.0.0'

# ============================================================ Imports ============================================================= #

# Conan imports
from conan import ConanFile
from conan.tools.files import copy
# Package imports
from gnu_toolchain.from_source import FromSourceDriver
from gnu_toolchain.prebuilt    import PrebuiltDriver

# ============================================================ Script ============================================================== #

class GnuToolchainConan(ConanFile):
    
    name        = 'flexible-gnu-toolchain'
    version     = '0.0.1'
    license     = 'MIT'
    author      = 'Krzysztof Pierczyk'
    description = 'Conan package providing fully functional GNU toolchain'
    homepage    = 'https://github.com/kpierczy/cpp-toolchains/flexible-gnu-toolchain'
    topics      = [ 'gcc', 'g++', 'binutils', 'libc', 'libstdc++' ]

    # ------------------------------------------------------------------ #
    
    package_type  = 'application'
    settings      = [ 'os', 'compiler', 'build_type', 'arch' ]

    # ------------------------------------------------------------------ #

    options = {

        # Prebuilt or from source
        'prebuilt' : [ True, False ],
        # Toolchain target
        'target' : [ None, 'ANY' ],
        
    } | FromSourceDriver.options | PrebuiltDriver.options

    default_options = {

        # By default, build from source
        'prebuilt' : False,
        # Default target
        'target' : None,

    } | FromSourceDriver.default_options | PrebuiltDriver.default_options

    # ------------------------------------------------------------------ #

    exports = [
        "data/*.py",
        "patches/*",
        "src/**/*.py",
        "license",
    ]

    # ---------------------------------------------------------------------------- #

    @property
    def win_bash(self):
        return (self.settings.os == "Windows") and (not self.options.prebuilt)

    @win_bash.setter
    def win_bash(self, value):
        pass
    
    # ---------------------------------------------------------------------------- #

    @property
    def _impl(self):
        if self.options.prebuilt:
            return PrebuiltDriver(self)
        else:
            return FromSourceDriver(self)
        
    @property
    def _other_impl(self):
        if self.info.options.prebuilt:
            return FromSourceDriver(self)
        else:
            return PrebuiltDriver(self)
        
    # ---------------------------------------------------------------------------- #

    def configure(self):
        self._impl.configure()

    def validate(self):

        # Make sure target is set
        if self.options.target is None:
            raise ValueError("Target must be set!")

        self._impl.validate()
        
    def system_requirements(self):
        self._impl.system_requirements()
        
    def requirements(self):
        self._impl.requirements()

    def layout(self):
        self._impl.layout()

    def generate(self):
        self._impl.generate()

    def build(self):
        self._impl.build()

    def package(self):

        # Install the license
        copy(self, pattern="license", src=self.build_folder, dst=self.package_folder)
        # Install the package
        self._impl.package()

    def package_info(self):
        self._impl.package_info()
        
    def package_id(self):

        # Compiler and build type are not important for prebuilt packages
        self.info.settings.rm_safe("compiler")
        self.info.settings.rm_safe("build_type")
        
        # Remove all options of the unused implementation
        for opt in self._other_impl.options.keys():
            if opt not in self._impl.options.keys():
                self.info.options.rm_safe(opt)

# ================================================================================================================================== #
