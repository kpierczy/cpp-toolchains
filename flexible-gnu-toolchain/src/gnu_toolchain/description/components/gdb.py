# ====================================================================================================================================
# @file       gdb.py
# @author     Krzysztof Pierczyk (you@you.you)
# @maintainer Krzysztof Pierczyk (you@you.you)
# @date       Wednesday, 2nd October 2024 6:29:53 am
# @modified   Tuesday, 8th October 2024 4:04:32 pm by Krzysztof Pierczyk (you@you.you)
# 
# 
# @copyright Your Company © 2024
# ====================================================================================================================================

# ============================================================ Imports ============================================================= #

# Package imports
from gnu_toolchain.description.components.common import CommonDescription
from gnu_toolchain.components.gdb import Gdb

# ========================================================= GdbDescription ========================================================= #

class GdbDescription(CommonDescription):
    
    # Name of the component (used internally by the build chain)
    component_name = 'gdb'
    # Default name for the GDB build
    name = 'gdb'
    # Default dependency name
    dep_name = 'gdb'

    # Associated driver
    driver = Gdb

# ================================================================================================================================== #
