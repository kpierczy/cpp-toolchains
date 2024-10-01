# ====================================================================================================================================
# @file       from_source.py
# @author     Krzysztof Pierczyk (you@you.you)
# @maintainer Krzysztof Pierczyk (you@you.you)
# @date       Tuesday, 1st October 2024 7:01:52 pm
# @modified   Tuesday, 1st October 2024 7:14:28 pm by Krzysztof Pierczyk (you@you.you)
# 
# 
# @copyright Your Company © 2024
# ====================================================================================================================================

# ============================================================ Imports ============================================================= #

# Standard imports
import pathlib
from importlib.machinery import SourceFileLoader
from copy import deepcopy
# Conan imports
from conan.tools.layout import basic_layout
from conan.tools.files import copy
from conan.tools.gnu import AutotoolsToolchain
# Package imports
from gnu_toolchain.components import Binutils
from gnu_toolchain.components import Gcc
from gnu_toolchain.components import Gdb

# ======================================================== FromSourceDriver ======================================================== #

class FromSourceDriver():

    def __init__(self, conanfile):
        self.conanfile = conanfile
        
    # ---------------------------------------------------------------------------- #

    def _get_url_for(self, component):
        return str(
            getattr(
                self.conanfile.options,
                f'with_{component}_url',
            )
        ).format(
            version = getattr(
                self.conanfile.options,
                f'with_{component}_version',
            )
        )

    def _get_urls_for_libc(self):

        supported_libcs = [
            'newlib',
        ]

        return {
            libc : self._get_url_for(libc) for libc in supported_libcs
        }

    @property
    def _config_provider(self):

        # If config has not been loaded, load it
        if not hasattr(self, '_config_provider_cache'):

            config = str(self.conanfile.options.with_config)

            # Check if self.conanfile.options.with_config points to an existing file relative to the data/ directory
            in_data_config = pathlib.Path(self.conanfile.recipe_folder) / "data" / str(self.conanfile.options.with_config)
            if in_data_config.exists():
               config = in_data_config.as_posix()

            self._config_provider_cache = SourceFileLoader(
                'config_module',
                config,
            ).load_module().Config(
                self.conanfile
            )

        return self._config_provider_cache

    @property
    def _config(self):
        return self._config_provider.make()
    
    @property
    def _common_config(self):

        # If common config has not been loaded, load it
        if not hasattr(self, '_common_config_cache'):
            self._common_config_cache = deepcopy(self._config)
            del self._common_config_cache["components"]

        return self._common_config_cache

    def _get_config_for(self, component):
        return self._config["components"][component]
    
    def _make_component(self, type, name, **kwargs):
        return type(
            common_config = self._common_config,
            config        = self._get_config_for(name),
            url           = self._get_url_for(name),
            **kwargs
        )

    @property
    def _binutils(self):
        return self._make_component(Binutils, "binutils")

    @property
    def _gcc(self):
        return self._make_component(Gcc, "gcc",
            libc_urls = self._get_urls_for_libc()
        )
    
    @property
    def _gdb(self):
        return self._make_component(Gdb, "gdb")
        
    # ---------------------------------------------------------------------------- #

    def configure(self):

        # Force C++11 (see GCC prerequisites)
        self.conanfile.settings.compiler.cppstd = 11

    def requirements(self):

        # Get the dependencies configuration
        config = self._config["components"]["dependencies"]

        def get_options(dep):
            return config.get("common", { }).get("options", { }) | config.get(dep, { }).get("options", { })

        # Specify dependencies
        self.conanfile.requires(f"zlib/{self.conanfile.options.with_zlib_version}",         options = get_options("zlib"))
        self.conanfile.requires(f"gmp/{self.conanfile.options.with_gmp_version}",           options = get_options("gmp"))
        self.conanfile.requires(f"mpfr/{self.conanfile.options.with_mpfr_version}",         options = get_options("mpfr"))
        self.conanfile.requires(f"mpc/{self.conanfile.options.with_mpc_version}",           options = get_options("mpc"))
        self.conanfile.requires(f"isl/{self.conanfile.options.with_isl_version}",           options = get_options("isl"))
        self.conanfile.requires(f"elfutils/{self.conanfile.options.with_elfutils_version}", options = get_options("elfutils"))
        self.conanfile.requires(f"expat/{self.conanfile.options.with_expat_version}",       options = get_options("expat"))

    def layout(self):
        basic_layout(self.conanfile, src_folder = "src")

    def generate(self):
        AutotoolsToolchain(
            self.conanfile,
        ).generate()

    def build(self):
        self._binutils.build(self.conanfile)
        self._gcc.build(self.conanfile)
        self._gdb.build(self.conanfile)

    def package(self):
        copy(self, '*', src = 'install', dst = self.conanfile.package_folder)
    
    def package_info(self):
        pass

# ================================================================================================================================== #
