# ====================================================================================================================================
# @file       newlib.py
# @author     Krzysztof Pierczyk (you@you.you)
# @maintainer Krzysztof Pierczyk (you@you.you)
# @date       Wednesday, 2nd October 2024 6:29:53 am
# @modified   Wednesday, 2nd October 2024 12:08:38 pm by Krzysztof Pierczyk (you@you.you)
# 
# 
# @copyright Your Company © 2024
# ====================================================================================================================================

# ============================================================ Imports ============================================================= #

# Package imports
from gnu_toolchain.description.components.common import CommonDescription
from gnu_toolchain.components.libc.newlib import Newlib

# ======================================================== NewlibDescription ======================================================= #

class NewlibDescription(CommonDescription):
    
    # Default name for the Newlib build
    name = 'newlib'
    # Default dependency name
    dep_name = 'newlib'

    # Associated driver
    driver = Newlib

# ================================================================================================================================== #
