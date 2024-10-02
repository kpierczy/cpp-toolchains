# ====================================================================================================================================
# @file       toolchain.py
# @author     Krzysztof Pierczyk (you@you.you)
# @maintainer Krzysztof Pierczyk (you@you.you)
# @date       Wednesday, 2nd October 2024 6:29:53 am
# @modified   Wednesday, 2nd October 2024 6:35:24 am by Krzysztof Pierczyk (you@you.you)
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
