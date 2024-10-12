# ====================================================================================================================================
# @file       binutils.py
# @author     Krzysztof Pierczyk (krzysztof.pierczyk@gmail.com)
# @maintainer Krzysztof Pierczyk (krzysztof.pierczyk@gmail.com)
# @date       Tuesday, 1st October 2024 11:40:43 am
# @modified   Saturday, 12th October 2024 10:52:44 pm by Krzysztof Pierczyk (krzysztof.pierczyk@gmail.com)
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
