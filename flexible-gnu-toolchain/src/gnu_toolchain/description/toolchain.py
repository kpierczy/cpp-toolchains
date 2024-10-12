# ====================================================================================================================================
# @file       toolchain.py
# @author     Krzysztof Pierczyk (krzysztof.pierczyk@gmail.com)
# @maintainer Krzysztof Pierczyk (krzysztof.pierczyk@gmail.com)
# @date       Wednesday, 2nd October 2024 6:29:53 am
# @modified   Saturday, 12th October 2024 10:52:44 pm by Krzysztof Pierczyk (krzysztof.pierczyk@gmail.com)
# 
# 
# @copyright Your Company © 2024
# ====================================================================================================================================

# ============================================================ Imports ============================================================= #



# ====================================================== ToolchainDescription ====================================================== #

class ToolchainDescription:
    
    def __init__(self,
        conanfile,
    ):
        self.conanfile = conanfile

    def get_package_version(self) -> str:

        """Formats the package version using the `with_gcc_version` option."""

        return self.pkg_version.format(
            version = self.conanfile.options.with_gcc_version
        )

# ================================================================================================================================== #
