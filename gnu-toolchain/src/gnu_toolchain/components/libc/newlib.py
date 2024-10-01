# ====================================================================================================================================
# @file       newlib.py
# @author     Krzysztof Pierczyk (krzysztof.pierczyk@gmail.com)
# @maintainer Krzysztof Pierczyk (krzysztof.pierczyk@gmail.com)
# @date       Tuesday, 1st October 2024 9:17:30 am
# @modified   Tuesday, 1st October 2024 7:18:37 pm by Krzysztof Pierczyk (you@you.you)
# 
# 
# @copyright PG Techonologies © 2024
# ====================================================================================================================================

# ============================================================= Imports ============================================================ #

# System imports
import pathlib
# Private imports
from gnu_toolchain.utils.autotools import build as autotools_build
from gnu_toolchain.utils.autotools import get_dirs as autotools_get_dirs

# ============================================================ Script ============================================================== #

class Newlib:

    '''Builder class for the newlib library'''
    
    def __init__(self, 
        config : dict,
        url : str,             
    ):
        self.config = config
        self.url    = url

    def build(self,
        conanfile,
        name : str,
        **kwargs,
    ):
        # Get the directories
        dirs = autotools_get_dirs(
            conanfile = conanfile,
            target    = self.config['target'],
        )

        # Extend the config with newlib-specific options
        doc_targets = [
            'pdf',
            'html',
        ] if conanfile.options.with_doc else [ ]

        doc_base_dir = pathlib.Path(self.config['target']) / 'newlib'

        # Compile list of doc files to be installed
        doc_files = {
            doc_base_dir / 'libc' / 'libc.pdf'  : dirs.doc_install_dir / 'pdf'  / 'libc.pdf',
            doc_base_dir / 'libc' / 'libc.pdf'  : dirs.doc_install_dir / 'pdf'  / 'libc.pdf',
            doc_base_dir / 'libc' / 'libc.html' : dirs.doc_install_dir / 'html' / 'libc.pdf',
            doc_base_dir / 'libc' / 'libc.html' : dirs.doc_install_dir / 'html' / 'libc.pdf',
        } if conanfile.options.with_doc else { }

        # Build the project
        autotools_build(
            conanfile           = conanfile,
            name                = f"newlib_{name}",
            url                 = self.url,
            config              = self.config,
            extra_install_files = doc_files,
            extra_targets       = doc_targets,
            **kwargs,
        )

# ================================================================================================================================== #
