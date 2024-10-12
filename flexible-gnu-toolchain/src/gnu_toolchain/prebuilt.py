# ====================================================================================================================================
# @file       prebuilt.py
# @author     Krzysztof Pierczyk (krzysztof.pierczyk@gmail.com)
# @maintainer Krzysztof Pierczyk (krzysztof.pierczyk@gmail.com)
# @date       Tuesday, 1st October 2024 7:01:52 pm
# @modified   Saturday, 12th October 2024 10:52:44 pm by Krzysztof Pierczyk (krzysztof.pierczyk@gmail.com)
# 
# 
# @copyright Your Company © 2024
# ====================================================================================================================================

# ============================================================ Imports ============================================================= #

# Standard imports
import pathlib

# ========================================================= PrebuiltDriver ========================================================= #

class PrebuiltDriver():

    def __init__(self,
        conanfile,
    ):
        self.conanfile = conanfile

    # ------------------------------------------------------------------ #

    options = { }
    
    default_options = { }
        
    # ---------------------------------------------------------------------------- #

    def validate(self):
        raise NotImplementedError("PrebuiltDriver.validate() is not implemented")

    def configure(self):
        raise NotImplementedError("PrebuiltDriver.configure() is not implemented")

    def system_requirements(self):
        raise NotImplementedError("PrebuiltDriver.system_requirements() is not implemented")
    
    def requirements(self):
        raise NotImplementedError("PrebuiltDriver.requirements() is not implemented")

    def layout(self):
        raise NotImplementedError("PrebuiltDriver.layout() is not implemented")

    def generate(self):
        raise NotImplementedError("PrebuiltDriver.generate() is not implemented")

    def build(self):
        raise NotImplementedError("PrebuiltDriver.build() is not implemented")

    def package(self):
        raise NotImplementedError("PrebuiltDriver.package() is not implemented")
    
    def package_info(self):
        raise NotImplementedError("PrebuiltDriver.package_info() is not implemented")

# ================================================================================================================================== #
