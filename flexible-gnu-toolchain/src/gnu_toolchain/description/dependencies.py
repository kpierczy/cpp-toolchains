# ====================================================================================================================================
# @file       dependencies.py
# @author     Krzysztof Pierczyk (krzysztof.pierczyk@gmail.com)
# @maintainer Krzysztof Pierczyk (krzysztof.pierczyk@gmail.com)
# @date       Wednesday, 2nd October 2024 6:29:53 am
# @modified   Saturday, 12th October 2024 10:52:44 pm by Krzysztof Pierczyk (krzysztof.pierczyk@gmail.com)
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
