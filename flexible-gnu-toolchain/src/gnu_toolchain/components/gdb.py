# ====================================================================================================================================
# @file       gdb.py
# @author     Krzysztof Pierczyk (you@you.you)
# @maintainer Krzysztof Pierczyk (you@you.you)
# @date       Tuesday, 1st October 2024 11:40:43 am
# @modified   Monday, 7th October 2024 10:15:09 pm by Krzysztof Pierczyk (you@you.you)
# 
# 
# @copyright Your Company © 2024
# ====================================================================================================================================

# ============================================================= Imports ============================================================ #

# System imports
import pathlib
from copy import deepcopy
# Private imports
from gnu_toolchain.utils.autotools import AutotoolsPackage

# =============================================================== Gdb ============================================================== #

class Gdb(AutotoolsPackage):
    
    def build(self):
        
        # Extend the config with the GDB specific options
        self.description.config += [
            f"--with-libexpat",
            f"--with-libexpat-prefix={pathlib.Path(self.conanfile.dependencies['expat'].package_folder).as_posix()}",
            f"--with-system-gdbinit={self.dirs.prefix.as_posix()}/{self._get_host_triplet(self.conanfile)}/{self.target}/lib/gdbinit",
        ]

        # Cache original description
        original_name   = self.description.name
        original_config = deepcopy(self.description.config)
        # Prepare list of build arguments
        build_args = {
            'doc_install_targets' : [
                'install-html install-pdf',
            ]
        }

        # Build the project without Python integration
        self._build_without_python_integration(
            original_name,
            original_config,
            build_args,
        )

        # Build the project with Python integration
        self._build_with_python_integration(
            original_name,
            original_config,
            build_args,
        )
                
    # ---------------------------------------------------------------------------- #

    def _build_without_python_integration(self,
        original_name,
        original_config,
        build_args,
    ):
        # Set config for the build variant without Python
        self.description.name   = f'{original_name}-no-python'
        self.description.config = original_config + [
            "--with-python=no",
        ]

        # Build the project without Python integration
        super().build(**build_args)

    def _build_with_python_integration(self,
        original_name,
        original_config,
        build_args,
    ):
        # Set config for the build variant without Python
        self.description.name   = original_name
        self.description.config = original_config + [
            f"--with-python=yes",
            f"--program-prefix={self.target}-",
            f"--program-suffix=-py",
        ]

        # Build the project with Python integration
        super().build(**build_args)
                                          
# ================================================================================================================================== #
