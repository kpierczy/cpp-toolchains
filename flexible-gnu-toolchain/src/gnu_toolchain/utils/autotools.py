# ====================================================================================================================================
# @file       system.py
# @author     Krzysztof Pierczyk (you@you.you)
# @maintainer Krzysztof Pierczyk (you@you.you)
# @date       Tuesday, 1st October 2024 12:16:57 pm
# @modified   Wednesday, 2nd October 2024 1:02:42 pm by Krzysztof Pierczyk (you@you.you)
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
    setattr(result, 'src_dir',         pathlib.Path("src"))
    setattr(result, 'download_dir',    pathlib.Path("download"))
    setattr(result, 'build_dir',       pathlib.Path("build"))
    setattr(result, 'install_dir',     pathlib.Path("install") / "final")
    setattr(result, 'off_install_dir', pathlib.Path("install") / "temp")
    # Extra paths for convenience
    setattr(result, 'off_install_rel_to_install', pathlib.Path("..") / result.off_install_dir.stem)

    return result
        
# ======================================================== AutotoolsPackage ======================================================== #

class AutotoolsPackage:

    def __init__(self,
        prefix,
        target,
        pkg_version,
        description,
    ):
        self.prefix      = prefix
        self.target      = target
        self.pkg_version = pkg_version
        self.description = description
    
    # ------------------------------------------------------------------ #

    def get_dirs(self,
        conanfile,
    ):
        result = get_standard_dirs()
        
        # Compile common dirs
        setattr(result, 'src_dir',                  pathlib.Path(conanfile.build_folder) / result.src_dir)
        setattr(result, 'download_dir',             pathlib.Path(conanfile.build_folder) / result.download_dir)
        setattr(result, 'build_dir',                pathlib.Path(conanfile.build_folder) / result.build_dir / self.description.name)
        setattr(result, 'install_dir',              pathlib.Path(conanfile.build_folder) / result.install_dir)
        setattr(result, 'off_install_dir',          pathlib.Path(conanfile.build_folder) / result.off_install_dir)
        setattr(result, 'prefixed_install_dir',     pathlib.Path(result.install_dir.as_posix()     + self.prefix))
        setattr(result, 'prefixed_off_install_dir', pathlib.Path(result.off_install_dir.as_posix() + self.prefix))
        # Extra paths for convenience
        setattr(result, 'doc_install_dir_rel', pathlib.Path("share") / "doc" / f"gcc-{self.target}")

        return result

    def build(self,
        
        conanfile,
        
        target        : str = None,
        doc_targets   : list = [],
        extra_targets : list = [],

        install_target        : str = 'install',
        doc_install_targets   : list = [],
        extra_install_targets : list = [],
        extra_install_files   : dict = {},
        
    ):
        """Downloads, configures and builds the autotools project"""

        # Compile dirs
        dirs = self._prepare_dirs(conanfile)

        # Clone the sources into <build>/src/binutils
        self._clone_sources(conanfile, dirs)

        # Create the autotools driver
        autotools = Autotools(conanfile)

        # Check if the project has been already built
        if self._has_build_tag(dirs):
            
            conanfile.output.info(f"'{self.description.name}' has been already built. Skipping...")

        # Else, configure and build the project
        else:

            conanfile.output.success(f"Cleaning '{self.description.name}' build directory...")

            # Clean the build directory just in case
            self._clean_build_dir(dirs)

            conanfile.output.success(f"Configuring '{self.description.name}'...")

            # Configure the project in the build directory
            try:
                self._configure_project(
                    conanfile,
                    dirs,
                    autotools
                )
            except Exception as e:
                conanfile.output.error(f"Failed to configure '{self.description.name}' ({e})")
                raise

            conanfile.output.success(f"Building '{self.description.name}'...")

            # Build the project
            try:
                self._build_project(
                    conanfile,
                    dirs,
                    autotools,
                    build_target = target,
                    doc_targets = doc_targets,
                    extra_targets = extra_targets,
                )
            except Exception as e:
                conanfile.output.error(f"Failed to build '{self.description.name}' ({e})")
                raise

            # Create the build tag
            self._make_build_tag(dirs)

        # Check if the project has been already installed
        if self._has_install_tag(dirs):

            conanfile.output.info(f"'{self.description.name}' has been already installed. Skipping...")

        # Else, install the project
        else:

            conanfile.output.success(f"Installing '{self.description.name}'...")

            # Install the project
            try:
                self._install_project(
                    conanfile,
                    dirs,
                    autotools,
                    install_target = install_target,
                    doc_install_targets = doc_install_targets,
                    extra_install_targets = extra_install_targets,
                    extra_install_files = extra_install_files,
                )
            except Exception as e:
                conanfile.output.error(f"Failed to install '{self.description.name}' ({e})")
                raise
        
            # Cleanup the installation
            try:
                self._cleanup_project(
                    conanfile,
                    dirs
                )
            except Exception as e:
                conanfile.output.warning(f"Failed to cleanup '{self.description.name}' installation ({e})")

            # Create the install tag
            self._make_install_tag(dirs)

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
            case _:
                raise ValueError(f"Unsupported OS: '{conanfile.settings.os}'")

        return f"{arch}-{system}"

    @staticmethod
    def _make_dirs(
        dirs,
        skip = [ 'src_dir' ]
    ):
        for name, path in dirs.__dict__.items():
            if (name not in skip) and (path.is_absolute()):
                path.mkdir(parents = True, exist_ok = True)

    def _get_common_config(self,
        conanfile,
        dirs,
    ):
        return [
            
            f"--build={self._get_host_triplet(conanfile)}",
            f"--host={self._get_host_triplet(conanfile)}",
            f"--target={self.target}",

            f"--infodir=${{prefix}}/{dirs.doc_install_dir_rel}/info",
            f"--mandir=${{prefix}}/{dirs.doc_install_dir_rel}/man",
            f"--htmldir=${{prefix}}/{dirs.doc_install_dir_rel}/html",
            f"--pdfdir=${{prefix}}/{dirs.doc_install_dir_rel}/pdf",
            
        ]
    
    def _has_build_tag(self,
        dirs,
    ):
        return (dirs.build_dir / '.built').exists()

    def _make_build_tag(self,
        dirs,
    ):
        (dirs.build_dir / '.built').touch()

    def _has_install_tag(self,
        dirs,
    ):
        return (dirs.build_dir / '.installed').exists()
    
    def _make_install_tag(self,
        dirs,
    ):
        (dirs.build_dir / '.installed').touch()

    def _prepare_dirs(self,
        conanfile,
    ):
        # Compile dirs
        dirs = self.get_dirs(conanfile)
        # Create directories
        self._make_dirs(dirs)

        return dirs
    
    def _clone_sources(self,
        conanfile,
        dirs,
    ):
        # Clone the sources into <build>/src/binutils
        with contextlib.chdir(dirs.download_dir):
            dirs.src_dir = get(conanfile, self.description.url, destination = dirs.src_dir.as_posix())

    def _clean_build_dir(self,
        dirs,
    ):
        # Clean the build directory
        if dirs.build_dir.exists():
            shutil.rmtree(dirs.build_dir.as_posix(), ignore_errors = True)
            dirs.build_dir.mkdir(parents = True, exist_ok = True)

    def _configure_project(self,
        conanfile,
        dirs,
        autotools,
    ):
        # Get the configuration
        config = self.description.get_config()

        # Extend the config with standard options
        config += self._get_common_config(conanfile, dirs)

        # Configure the project in the build directory
        with contextlib.chdir(dirs.build_dir):
            autotools.configure(
                build_script_folder = dirs.src_dir.as_posix(),
                args = config
            )

        return autotools
    
    def _build_project(self,
        conanfile,
        dirs,
        autotools,
        build_target : str | None = None,
        doc_targets : list = [ ],
        extra_targets : list = [],
    ):
        with contextlib.chdir(dirs.build_dir):

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
            autotools.make(target = build_target)
            # Build extra targets if needed
            if extra_targets:
                for target in extra_targets:
                    autotools.make(target = target)
            # Build doc targets if needed
            if conanfile.options.with_doc and (not self.description.without_doc):
                for target in doc_targets:
                    autotools.make(target = target)
    
    def _install_project(self,
        conanfile,
        dirs,
        autotools,
        install_target        : str = 'install',
        doc_install_targets   : list = [],
        extra_install_targets : list = [],
        extra_install_files   : dict = {},
    ):
        # Configure the project in the build directory
        with contextlib.chdir(dirs.build_dir):

            is_off_build = self.description.target_files is not None

            # Pick destdir
            if is_off_build:
                destdir = f'DESTDIR={dirs.off_install_dir.as_posix()}'
            else:
                destdir = f'DESTDIR={dirs.install_dir.as_posix()}'

            # Compile install args
            install_args = [
                destdir,
            ]

            # Install the project
            autotools.install(
                target = install_target,
                args = install_args)
            # Install extra targets if needed
            if extra_install_targets:
                conanfile.output.success(f"Installing extra targets: {extra_install_targets}")
                for target in extra_install_targets:
                    autotools.install(
                        target = target,
                        args = install_args,
                    )
            # Install doc targets if needed
            if conanfile.options.with_doc and (not self.description.without_doc):
                conanfile.output.success(f"Installing doc targets: {doc_install_targets}")
                for target in doc_install_targets:
                    autotools.install(
                        target = target,
                        args = install_args,
                    )

            # If build is off-the-tree, copy the target files to the target directory
            if is_off_build:
                conanfile.output.success(f"Copying target files to the install directory...")
                for pattern, dst in self.description.target_files.items():
                    copy(conanfile,
                        pattern = pattern.as_posix(),
                        src     = dirs.prefixed_off_install_dir,
                        dst     = dirs.prefixed_install_dir / dst,
                    )

            # Install extra files directly from the build tree if needed
            for pattern, dst in extra_install_files.items():
                conanfile.output.success(f"Copying extra files to the install directory...")
                copy(conanfile,
                    pattern = pattern.as_posix(),
                    src     = dirs.build_dir,
                    dst     = dirs.prefixed_install_dir / dst,
                )

    def _cleanup_project(self,
        conanfile,
        dirs,
    ):
        # Remove useless compilation results
        if self.description.cleanup:
            conanfile.output.success(f"Cleaning up the installation...")
            for path in self.description.cleanup:
                path = dirs.prefixed_install_dir / path
                try:
                    if path.is_file():
                        path.unlink()
                    else:
                        shutil.rmtree(path.as_posix())
                except Exception as e:
                    conanfile.output.warning(f"Failed to remove '{path.as_posix()}' ({e})")

# ================================================================================================================================== #
