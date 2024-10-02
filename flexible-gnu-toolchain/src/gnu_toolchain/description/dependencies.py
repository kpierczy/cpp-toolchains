# ====================================================================================================================================
# @file       dependencies.py
# @author     Krzysztof Pierczyk (you@you.you)
# @maintainer Krzysztof Pierczyk (you@you.you)
# @date       Wednesday, 2nd October 2024 6:29:53 am
# @modified   Wednesday, 2nd October 2024 8:14:45 am by Krzysztof Pierczyk (you@you.you)
# 
# 
# @copyright Your Company © 2024
# ====================================================================================================================================

# ============================================================ Imports ============================================================= #

# Package imports
from gnu_toolchain.utils.common import merge_dicts

# ===================================================== DependenciesDescription ==================================================== #

class DependenciesDescription():

    def get_options(self,
        dependency
    ) -> dict:

        """Default implementation of the dependencies options getter. It returns
        merged values of the `common_options` and the `options` for the given
        dependency.
        """

        return merge_dicts(
            getattr(self, 'common_options', { }),
            getattr(self, 'options',        { }).get(dependency, { }),
        )

# ================================================================================================================================== #
