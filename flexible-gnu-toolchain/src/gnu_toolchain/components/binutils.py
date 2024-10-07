# ====================================================================================================================================
# @file       binutils.py
# @author     Krzysztof Pierczyk (you@you.you)
# @maintainer Krzysztof Pierczyk (you@you.you)
# @date       Tuesday, 1st October 2024 11:40:43 am
# @modified   Monday, 7th October 2024 7:22:08 pm by Krzysztof Pierczyk (you@you.you)
# 
# 
# @copyright Your Company © 2024
# ====================================================================================================================================

# ============================================================= Imports ============================================================ #

# Private imports
from gnu_toolchain.utils.autotools import AutotoolsPackage

# ============================================================ Binutils ============================================================ #

class Binutils(AutotoolsPackage):

    def build(self):

        # Extend the config
        self.description.config += [
            f"--with-pkgversion={self.pkg_version}",
            f"--with-sysroot={self.dirs.prefix.as_posix()}/{self.target}" 
        ]
        
        # Build the project
        super().build(
                      
            doc_install_targets = [
                'install-html install-pdf',
            ],
            
        )

# ================================================================================================================================== #
