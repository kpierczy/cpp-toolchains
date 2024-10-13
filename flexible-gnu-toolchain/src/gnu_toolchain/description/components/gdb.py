# ====================================================================================================================================
# @file       gdb.py
# @author     Krzysztof Pierczyk (krzysztof.pierczyk@gmail.com)
# @maintainer Krzysztof Pierczyk (krzysztof.pierczyk@gmail.com)
# @date       Wednesday, 2nd October 2024 6:29:53 am
# @modified   Sunday, 13th October 2024 11:12:33 am by Krzysztof Pierczyk (krzysztof.pierczyk@gmail.com)
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

    # Default Python integration
    with_python = False

# ================================================================================================================================== #
