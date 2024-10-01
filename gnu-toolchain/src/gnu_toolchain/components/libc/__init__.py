# ====================================================================================================================================
# @file       __init__.py
# @author     Krzysztof Pierczyk (you@you.you)
# @maintainer Krzysztof Pierczyk (you@you.you)
# @date       Tuesday, 1st October 2024 11:46:51 am
# @modified   Tuesday, 1st October 2024 7:02:47 pm by Krzysztof Pierczyk (you@you.you)
# 
# 
# @copyright Your Company © 2024
# ====================================================================================================================================

# ============================================================ Imports ============================================================= #

# Private imports
from gnu_toolchain.components.libc.newlib import Newlib

# ======================================================= pick_library_driver ====================================================== #

def pick_library_driver(lib_name):
    match lib_name:
        case 'newlib': return Newlib
        case _:
            raise ValueError(f"Unknown library driver: {lib_name}")

# ================================================================================================================================== #
