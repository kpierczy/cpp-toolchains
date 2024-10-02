# ====================================================================================================================================
# @file       newlib.py
# @author     Krzysztof Pierczyk (krzysztof.pierczyk@gmail.com)
# @maintainer Krzysztof Pierczyk (krzysztof.pierczyk@gmail.com)
# @date       Tuesday, 1st October 2024 9:17:30 am
# @modified   Wednesday, 2nd October 2024 12:24:58 pm by Krzysztof Pierczyk (you@you.you)
# 
# 
# @copyright PG Techonologies © 2024
# ====================================================================================================================================

# ============================================================= Imports ============================================================ #

# System imports
import pathlib
# Private imports
from gnu_toolchain.utils.autotools import AutotoolsPackage

# ============================================================ Script ============================================================== #

class Newlib(AutotoolsPackage):

    '''Builder class for the newlib library'''

    def build(self,
        conanfile,
    ):
        # Get the directories
        dirs = self.get_dirs(conanfile)
        # Build the project
        super().build(conanfile,
        
            extra_install_files = {
                pathlib.Path(self.target) / 'newlib' / 'libc' / 'libc.pdf'  : dirs.doc_install_dir_rel / 'pdf'  / 'libc.pdf',
                pathlib.Path(self.target) / 'newlib' / 'libc' / 'libc.pdf'  : dirs.doc_install_dir_rel / 'pdf'  / 'libc.pdf',
                pathlib.Path(self.target) / 'newlib' / 'libc' / 'libc.html' : dirs.doc_install_dir_rel / 'html' / 'libc.pdf',
                pathlib.Path(self.target) / 'newlib' / 'libc' / 'libc.html' : dirs.doc_install_dir_rel / 'html' / 'libc.pdf',
            },
            
            doc_install_targets = [
                'pdf',
                'html',
            ],
            
        )

# ================================================================================================================================== #
