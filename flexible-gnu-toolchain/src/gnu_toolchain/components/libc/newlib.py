# ====================================================================================================================================
# @file       newlib.py
# @author     Krzysztof Pierczyk (krzysztof.pierczyk@gmail.com)
# @maintainer Krzysztof Pierczyk (krzysztof.pierczyk@gmail.com)
# @date       Tuesday, 1st October 2024 9:17:30 am
# @modified   Saturday, 12th October 2024 10:48:51 pm by Krzysztof Pierczyk (krzysztof.pierczyk@gmail.com)
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

    def build(self):
        
        # Build the project
        super().build(
        
            manual_install_files = {
                pathlib.Path(self.target) / 'newlib' / 'libc' / 'libc.pdf'  : self.dirs.doc / 'pdf'  / 'libc.pdf',
                pathlib.Path(self.target) / 'newlib' / 'libc' / 'libc.pdf'  : self.dirs.doc / 'pdf'  / 'libc.pdf',
                pathlib.Path(self.target) / 'newlib' / 'libc' / 'libc.html' : self.dirs.doc / 'html' / 'libc.pdf',
                pathlib.Path(self.target) / 'newlib' / 'libc' / 'libc.html' : self.dirs.doc / 'html' / 'libc.pdf',
            },
            
            doc_install_targets = [
                'pdf',
                'html',
            ],

            # Newlib does not handle parallel installation very well
            install_args = [ '-j1' ],
            
        )

# ================================================================================================================================== #
