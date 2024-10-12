# ====================================================================================================================================
# @file       binutils.py
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
from gnu_toolchain.description.components.common import CommonDescription
from gnu_toolchain.components.binutils import Binutils

# ======================================================= BinutilsDescription ====================================================== #

class BinutilsDescription(CommonDescription):
    
    # Name of the component (used internally by the build chain)
    component_name = 'binutils'
    # Default name for the binutils build
    name = 'binutils'
    # Default dependency name
    dep_name = 'binutils'

    # Associated driver
    driver = Binutils

# ================================================================================================================================== #
