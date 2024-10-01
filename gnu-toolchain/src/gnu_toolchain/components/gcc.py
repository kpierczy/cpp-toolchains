# ====================================================================================================================================
# @file       gcc.py
# @author     Krzysztof Pierczyk (you@you.you)
# @maintainer Krzysztof Pierczyk (you@you.you)
# @date       Tuesday, 1st October 2024 11:40:43 am
# @modified   Tuesday, 1st October 2024 7:39:42 pm by Krzysztof Pierczyk (you@you.you)
# 
# 
# @copyright Your Company © 2024
# ====================================================================================================================================

# ============================================================= Imports ============================================================ #

# Standard imports
import os
# Private imports
from gnu_toolchain.utils.common import merge_dicts
from gnu_toolchain.utils.autotools import build as autotools_build
from gnu_toolchain.utils.autotools import get_dirs as autotools_get_dirs
from gnu_toolchain.components.libc import pick_library_driver

# =============================================================== Gcc ============================================================== #

class Gcc:
    
    def __init__(self, 
        common_config : dict,
        config : dict,
        url : str,             
        libc_urls : dict,
    ):
        # Keep the config and the url
        self.base_config = {
            'url'    : url,
            'config' : merge_dicts(common_config, config["base"]),
        } if "base" in config else None

        # Track list of built libc's
        self.built_libcs = [ ]
        
        # Compile per-libc configurations
        self.full_config = { }
        for with_libc_descriptor in config["full"]:
            libc_name = with_libc_descriptor.get('libc_name', None)
            self.full_config[with_libc_descriptor['name']] = {
                'url'         : url,
                'config'      : merge_dicts(common_config, with_libc_descriptor["config"]),
                'libc_name'   : libc_name,
                'libc_url'    : libc_urls[libc_name] if libc_name is not None else None,
                'libc_config' : merge_dicts(common_config, with_libc_descriptor.get('libc_config', { })),
            }

    def _build_gcc_base(self,
        conanfile,
        url : str,
        config : dict,
    ):
        # Extend the config
        config["config-options"] += [

            f"--with-gmp={conanfile.dependencies["gmp"].package_folder}",
            f"--with-mpfr={conanfile.dependencies["mpfr"].package_folder}",
            f"--with-mpc={conanfile.dependencies["mpc"].package_folder}",
            f"--with-isl={conanfile.dependencies["isl"].package_folder}",
            f"--with-libelf={conanfile.dependencies["elfutils"].package_folder}",
            
            f"--libexecdir=${{prefix}}/lib",
            f"--with-sysroot=${{prefix}}/{config['target']}",
            f"--with-python-dir=share/gcc-{config['target']}",
            
        ]

        # Build the project
        autotools_build(
            conanfile      = conanfile,
            name           = "gcc_base",
            url            = url,
            config         = config,
            target         = 'all-gcc',
            install_target = 'install-gcc',
        )

        dirs = autotools_get_dirs(conanfile, target = config['target'])

        # Prepend PATH with the new GCC
        os.environ["PATH"] = f"{dirs.install_dir}/bin{os.pathsep}{os.environ['PATH']}"

    def _build_gcc_with_libc(self,
        conanfile,
        name : str,
        url : str,
        config : dict,
        libc_name : str | None,
        libc_url : str | None,
        libc_config : dict,
    ):
        # If the libc is provided
        if libc_name is not None:

            # Build the libc
            pick_library_driver(libc_name)(
                config = libc_config,
                url    = libc_url,
            ).build(
                
                conanfile,
                name = name,

                # Install documentation only for the first libc built
                skip_doc = libc_name in self.built_libcs,
                # For second and next libc's pick <target> as the installation dir
                install_to_target = len(self.built_libcs) > 0,
            )

            # Add the libc to the list of built ones
            self.built_libcs.append(libc_name)
        
    def build(self,
        conanfile,
    ):
        # Build the basic GCC
        if self.base_config is not None:
            self._build_gcc_base(
                conanfile,
                self.base_config["url"],
                self.base_config["config"]
            )
        
        # Build GCC with different libc
        for name in self.full_config.keys():
            self._build_gcc_with_libc(
                conanfile,
                name,
                **self.full_config[name],
            )

# ================================================================================================================================== #
