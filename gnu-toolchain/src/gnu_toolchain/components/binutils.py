# ====================================================================================================================================
# @file       binutils.py
# @author     Krzysztof Pierczyk (you@you.you)
# @maintainer Krzysztof Pierczyk (you@you.you)
# @date       Tuesday, 1st October 2024 11:40:43 am
# @modified   Tuesday, 1st October 2024 5:44:57 pm by Krzysztof Pierczyk (you@you.you)
# 
# 
# @copyright Your Company © 2024
# ====================================================================================================================================

# ============================================================= Imports ============================================================ #

# Private imports
from gnu_toolchain.utils.common import merge_dicts
from gnu_toolchain.utils.autotools import build as autotools_build

# ============================================================ Binutils ============================================================ #

class Binutils:
    
    def __init__(self, 
        common_config: dict,
        config: dict,
        url: str,
    ):
        # Keep the config and the url
        self.config = merge_dicts(common_config, config)
        self.url    = url

    def build(self,
        conanfile,
    ):
        # Extend the config
        self.config["config-options"] += [
            f"--with-sysroot=${{prefix}}/{self.config['target']}" 
        ]

        # ------------------------------------------------------------
        # @note We copy installed content content to <target>
        #    directory for future use (these binutils will be used by
        #    final-GCC that is built with --with-sysroot pointing to
        #    the <target> directory)
        # ------------------------------------------------------------
        
        # Build the project
        autotools_build(
            conanfile      = conanfile,
            name           = "binutils",
            url            = self.url,
            config         = self.config,
            copy_to_target = True,
            extra_install_targets = [
                'install-html',
                'install-pdf',
            ] if conanfile.options.with_doc else [ ],
        )

# ================================================================================================================================== #
