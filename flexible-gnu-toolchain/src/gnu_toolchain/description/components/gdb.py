# ====================================================================================================================================
# @file       gdb.py
# @author     Krzysztof Pierczyk (you@you.you)
# @maintainer Krzysztof Pierczyk (you@you.you)
# @date       Wednesday, 2nd October 2024 6:29:53 am
# @modified   Wednesday, 2nd October 2024 12:08:30 pm by Krzysztof Pierczyk (you@you.you)
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
    
    # Default name for the GDB build
    name = 'gdb'
    # Default dependency name
    dep_name = 'gdb'

    # Associated driver
    driver = Gdb

# ================================================================================================================================== #
