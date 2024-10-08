# ====================================================================================================================================
# @file       gcc.py
# @author     Krzysztof Pierczyk (you@you.you)
# @maintainer Krzysztof Pierczyk (you@you.you)
# @date       Wednesday, 2nd October 2024 6:29:53 am
# @modified   Tuesday, 8th October 2024 4:04:29 pm by Krzysztof Pierczyk (you@you.you)
# 
# 
# @copyright Your Company © 2024
# ====================================================================================================================================

# ============================================================ Imports ============================================================= #

# Package imports
from gnu_toolchain.description.components.common import CommonDescription
from gnu_toolchain.components.gcc import Gcc

# ========================================================= GccDescription ========================================================= #

class GccDescription(CommonDescription):
    
    # Name of the component (used internally by the build chain)
    component_name = 'gcc'
    # Default name for the GCC build stage
    name = 'gcc'
    # Default dependency name
    dep_name = 'gcc'

    # Default libc associated with the GCC build stage
    libc = None
    # Build full GCC by default
    full_build = True

    # Associated driver
    driver = Gcc
    
    # ------------------------------------------------------------------ #

    def __init__(self,
        conanfile,
    ):
        super().__init__(conanfile)

        # Construct lib descriptor from the Li
        if hasattr(self, 'Libc'):
            self.libc = self.Libc(conanfile)

# ================================================================================================================================== #
