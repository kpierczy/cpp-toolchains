# ====================================================================================================================================
# @file       binutils.py
# @author     Krzysztof Pierczyk (you@you.you)
# @maintainer Krzysztof Pierczyk (you@you.you)
# @date       Tuesday, 1st October 2024 11:40:43 am
# @modified   Wednesday, 2nd October 2024 9:45:47 am by Krzysztof Pierczyk (you@you.you)
# 
# 
# @copyright Your Company © 2024
# ====================================================================================================================================

# ============================================================= Imports ============================================================ #

# Private imports
from gnu_toolchain.utils.autotools import AutotoolsPackage

# ============================================================ Binutils ============================================================ #

class Binutils(AutotoolsPackage):

    def build(self,
        conanfile,
    ):
        # Extend the config
        self.description.config += [
            f"--with-pkgversion={self.pkg_version}",
            f"--with-sysroot=${{prefix}}/{self.target}" 
        ]
        
        # Build the project
        super().build(conanfile,
                      
            doc_install_targets = [
                'install-html install-pdf',
            ],
            
        )

# ================================================================================================================================== #
