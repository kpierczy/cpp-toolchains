# ====================================================================================================================================
# @file       prebuilt.py
# @author     Krzysztof Pierczyk (you@you.you)
# @maintainer Krzysztof Pierczyk (you@you.you)
# @date       Tuesday, 1st October 2024 7:01:52 pm
# @modified   Tuesday, 1st October 2024 7:12:31 pm by Krzysztof Pierczyk (you@you.you)
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
        version,
    ):
        self.conanfile = conanfile
        self.version   = version
        
    # ---------------------------------------------------------------------------- #

    def configure(self):
        raise NotImplementedError("PrebuiltDriver.configure() is not implemented")

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
