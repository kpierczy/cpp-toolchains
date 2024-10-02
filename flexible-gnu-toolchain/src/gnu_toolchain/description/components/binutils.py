# ====================================================================================================================================
# @file       binutils.py
# @author     Krzysztof Pierczyk (you@you.you)
# @maintainer Krzysztof Pierczyk (you@you.you)
# @date       Wednesday, 2nd October 2024 6:29:53 am
# @modified   Wednesday, 2nd October 2024 12:08:08 pm by Krzysztof Pierczyk (you@you.you)
# 
# 
# @copyright Your Company © 2024
# ====================================================================================================================================

# ============================================================ Imports ============================================================= #

# Package imports
from gnu_toolchain.description.components.common import CommonDescription
from gnu_toolchain.components.binutils import Binutils

# ======================================================= BinutilsDescription ====================================================== #

class BinutilsDescription(CommonDescription):
    
    # Default name for the binutils build
    name = 'binutils'
    # Default dependency name
    dep_name = 'binutils'

    # Associated driver
    driver = Binutils

# ================================================================================================================================== #
