# ====================================================================================================================================
# @file       system.py
# @author     Krzysztof Pierczyk (you@you.you)
# @maintainer Krzysztof Pierczyk (you@you.you)
# @date       Tuesday, 1st October 2024 12:16:57 pm
# @modified   Monday, 7th October 2024 9:34:50 pm by Krzysztof Pierczyk (you@you.you)
# 
# 
# @copyright Your Company © 2024
# ====================================================================================================================================

# ============================================================= Imports ============================================================ #

# System imports
import pathlib
import shutil
import os
import contextlib
import re
# Conan imports
from conan.tools.files import copy
from conan.tools.gnu import Autotools
# Private imports
from gnu_toolchain.utils.files import get

# ========================================================== Helper types ========================================================== #

class _Object(object):
    pass

# ======================================================== get_standard_dirs ======================================================= #

def get_standard_dirs():

    result = _Object()
    
    # Compile common dirs
    setattr(result, 'src',       pathlib.Path("src"))
    setattr(result, 'download',  pathlib.Path("download"))
    setattr(result, 'build',     pathlib.Path("build"))
    setattr(result, 'prefix',    pathlib.Path("install") / "final")
    setattr(result, 'offprefix', pathlib.Path("install") / "temp")

    return result
        
# ======================================================== AutotoolsPackage ======================================================== #

class AutotoolsPackage:

    def __init__(self,
        conanfile,
        target,
        pkg_version,
        description,
    ):
        self.conanfile   = conanfile
        self.target      = target
        self.pkg_version = pkg_version
        self.description = description

        # Compile dirs
        self.dirs = self.make_dirs(
            self.conanfile,
            self.description.name,
            self.target,
        )
    
    # ------------------------------------------------------------------ #

    msys_dlls = [
        'msys-2.0.dll',
        'msys-gcc_s-seh-1.dll',
    ]

    # ------------------------------------------------------------------ #

    @staticmethod
    def make_dirs(
        conanfile,
        build_name = None,
        target = None,
    ):
        result = get_standard_dirs()
        
        # Compile common dirs
        setattr(result, 'src',       pathlib.Path(conanfile.build_folder) / result.src)
        setattr(result, 'download',  pathlib.Path(conanfile.build_folder) / result.download)
        setattr(result, 'build',     pathlib.Path(conanfile.build_folder) / result.build / (build_name if build_name else '.'))
        setattr(result, 'prefix',    pathlib.Path(conanfile.build_folder) / result.prefix)
        setattr(result, 'offprefix', pathlib.Path(conanfile.build_folder) / result.offprefix)
        # Extra paths for convenience
        setattr(result, 'doc',       pathlib.Path("share") / "doc" / f"gcc-{target}")

        return result

    def build(self,
        
        target        : str = None,
        build_args    : list | None = None,
        doc_targets   : list = [],
        extra_targets : list = [],

        install_target        : str = 'install',
        install_args          : list | None = None,
        doc_install_targets   : list = [],
        extra_install_targets : list = [],
        extra_install_files   : dict = {},
        
    ):
        """Downloads, configures and builds the autotools project"""

        # Compile dirs
        self._make_dirs()

        # Clone the sources into <build>/src/binutils
        self._clone_sources()

        # Create the autotools driver
        autotools = Autotools(self.conanfile)

        # Check if the project has been already built
        if self._has_build_tag():
            
            self.conanfile.output.info(f"'{self.description.name}' has been already built. Skipping...")

        # Else, configure and build the project
        else:

            self.conanfile.output.success(f"Cleaning '{self.description.name}' build directory...")

            # Clean the build directory just in case
            self._clean_build_dir()

            self.conanfile.output.success(f"Configuring '{self.description.name}'...")

            # Configure the project in the build directory
            try:
                self._configure_project(
                    autotools
                )
            except Exception as e:
                self.conanfile.output.error(f"Failed to configure '{self.description.name}' ({e})")
                raise

            self.conanfile.output.success(f"Building '{self.description.name}'...")

            # Build the project
            try:
                self._build_project(
                    autotools,
                    build_target = target,
                    build_args = build_args,
                    doc_targets = doc_targets,
                    extra_targets = extra_targets,
                )
            except Exception as e:
                self.conanfile.output.error(f"Failed to build '{self.description.name}' ({e})")
                raise

            # Create the build tag
            self._make_build_tag()

        # Check if the project has been already installed
        if self._has_install_tag():

            self.conanfile.output.info(f"'{self.description.name}' has been already installed. Skipping...")

        # Else, install the project
        else:

            self.conanfile.output.success(f"Installing '{self.description.name}'...")

            # Install the project
            try:
                self._install_project(
                    autotools,
                    install_target = install_target,
                    install_args = install_args,
                    doc_install_targets = doc_install_targets,
                    extra_install_targets = extra_install_targets,
                    extra_install_files = extra_install_files,
                )
            except Exception as e:
                self.conanfile.output.error(f"Failed to install '{self.description.name}' ({e})")
                raise
        
            # Cleanup the installation
            try:
                self._cleanup_project()
            except Exception as e:
                self.conanfile.output.warning(f"Failed to cleanup '{self.description.name}' installation ({e})")

            # Create the install tag
            self._make_install_tag()

        self.conanfile.output.success(f"'{self.description.name}' has been successfully built and installed.")

        return True
    
    # ------------------------------------------------------------------ #

    @staticmethod
    def _get_host_triplet(
        conanfile
    ):
        """Computes GNU triple for the host machine of the Conan package"""
            
        match conanfile.settings.arch:
            case 'x86_64': arch = 'x86_64'
            case _:
                raise ValueError(f"Unsupported architecture: '{conanfile.settings.arch}'")

        match conanfile.settings.os:
            case 'Linux': system = 'linux-gnu'
            case 'Windows': system = 'pc-msys'
            case _:
                raise ValueError(f"Unsupported OS: '{conanfile.settings.os}'")

        return f"{arch}-{system}"
    
    @property
    def _is_off_build(self):
        return self.description.target_files is not None

    def _make_dirs(self,
        skip = [ 'src' ]
    ):
        for name, path in self.dirs.__dict__.items():
            if (name not in skip) and (path.is_absolute()):
                path.mkdir(parents = True, exist_ok = True)

    def _get_common_config(self):

        # Get the prefix
        if self._is_off_build:
            prefix = self.dirs.offprefix
        else:
            prefix = self.dirs.prefix
        # Compute doc directory
        doc_dir = prefix / self.dirs.doc

        # Compile the common configuration
        return [

            f"--build={self._get_host_triplet(self.conanfile)}",
            f"--host={self._get_host_triplet(self.conanfile)}",
            f"--target={self.target}",

            f"--prefix={prefix.as_posix()}",

            f"--bindir={prefix.as_posix()}/bin",
            f"--sbindir={prefix.as_posix()}/bin",
            f"--libdir={prefix.as_posix()}/lib",
            f"--includedir={prefix.as_posix()}/include",
            f"--oldincludedir={prefix.as_posix()}/include",

            f"--infodir={doc_dir.as_posix()}/info",
            f"--mandir={doc_dir.as_posix()}/man",
            f"--htmldir={doc_dir.as_posix()}/html",
            f"--pdfdir={doc_dir.as_posix()}/pdf",
            
        ]
    
    def _has_build_tag(self):
        return (self.dirs.build / '.built').exists()

    def _make_build_tag(self):
        (self.dirs.build / '.built').touch()

    def _has_install_tag(self):
        return (self.dirs.build / '.installed').exists()
    
    def _make_install_tag(self):
        (self.dirs.build / '.installed').touch()
    
    def _clone_sources(self
                       ):
        # Clone the sources into <build>/src/binutils
        with contextlib.chdir(self.dirs.download):
            self.dirs.src = get(self.conanfile, self.description.url, destination = self.dirs.src.as_posix())

    def _clean_build_dir(self):

        # Clean the build directory
        if self.dirs.build.exists():
            shutil.rmtree(self.dirs.build.as_posix(), ignore_errors = True)
            self.dirs.build.mkdir(parents = True, exist_ok = True)

    def _configure_project(self,
        autotools : Autotools,
    ):
        # Get the configuration
        config = self.description.get_config()

        # Extend the config with standard options
        config += self._get_common_config()

        # Configure the project in the build directory
        with contextlib.chdir(self.dirs.build):
            autotools.configure(
                build_script_folder = self.dirs.src.as_posix(),
                args = config
            )

        return autotools
    
    def _build_project(self,
        autotools : Autotools,
        build_target  : str | None = None,
        build_args    : list | None = None,
        doc_targets   : list = [ ],
        extra_targets : list = [],
    ):
        with contextlib.chdir(self.dirs.build):

            # Get the build options & env
            build_options = self.description.get_build_options()
            env           = self.description.get_env()

            # Apply build options
            if build_options:
                os.environ['CXXFLAGS'] = ' '.join(build_options)
            # Extend environment
            if env:
                os.environ.update(env)

            # Build the project
            autotools.make(target = build_target, args = build_args)
            # Build extra targets if needed
            if extra_targets:
                for target in extra_targets:
                    autotools.make(target = target, args = build_args)
            # Build doc targets if needed
            if self.conanfile.options.with_doc and (not self.description.without_doc):
                for target in doc_targets:
                    autotools.make(target = target, args = build_args)
    
    def _install_project(self,
        autotools : Autotools,
        install_target        : str = 'install',
        install_args          : list | None = None,
        doc_install_targets   : list = [],
        extra_install_targets : list = [],
        extra_install_files   : dict = {},
    ):
        # Configure the project in the build directory
        with contextlib.chdir(self.dirs.build):

            # Install the project
            autotools.make(
                target = install_target,
                args = install_args)
            # Install extra targets if needed
            if extra_install_targets:
                self.conanfile.output.success(f"Installing extra targets: {extra_install_targets}")
                for target in extra_install_targets:
                    autotools.make(
                        target = target,
                        args = install_args,
                    )
            # Install doc targets if needed
            if self.conanfile.options.with_doc and (not self.description.without_doc):
                self.conanfile.output.success(f"Installing doc targets: {doc_install_targets}")
                for target in doc_install_targets:
                    autotools.make(
                        target = target,
                        args = install_args,
                    )

            # If build is off-the-tree, copy the target files to the target directory
            if self._is_off_build:
                self.conanfile.output.success(f"Copying target files to the install directory...")
                for pattern, dst in self.description.target_files.items():
                    copy(self.conanfile,
                        pattern = pattern.as_posix(),
                        src     = self.dirs.offprefix,
                        dst     = self.dirs.prefix / dst,
                    )

            # Install extra files directly from the build tree if needed
            for pattern, dst in extra_install_files.items():
                self.conanfile.output.success(f"Copying extra files to the install directory...")
                copy(self.conanfile,
                    pattern = pattern.as_posix(),
                    src     = self.dirs.build,
                    dst     = self.dirs.prefix / dst,
                )

            # For Windows, install msys2 runtime in the /lib directory
            if self.conanfile.settings.os == 'Windows':
                msys_bin = pathlib.Path(self.conanfile.dependencies.build['msys2'].package_folder) / 'bin/msys64/usr/bin'
                for file in self.msys_dlls:
                    shutil.copy(msys_bin / file, self.dirs.prefix / 'bin' / file)
                    assert (self.dirs.prefix / 'bin' / file).exists()

    def _cleanup_project(self):
        
        # Remove useless compilation results
        if self.description.cleanup:
            self.conanfile.output.success(f"Cleaning up the installation...")
            for path in self.description.cleanup:
                path = self.dirs.prefix / path
                try:
                    if path.is_file():
                        path.unlink()
                    else:
                        shutil.rmtree(path.as_posix())
                except Exception as e:
                    self.conanfile.output.warning(f"Failed to remove '{path.as_posix()}' ({e})")

# ================================================================================================================================== #
