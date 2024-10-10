# ====================================================================================================================================
# @file       system.py
# @author     Krzysztof Pierczyk (you@you.you)
# @maintainer Krzysztof Pierczyk (you@you.you)
# @date       Tuesday, 1st October 2024 12:16:57 pm
# @modified   Thursday, 10th October 2024 1:29:05 pm by Krzysztof Pierczyk (you@you.you)
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

        # Create the autotools driver
        autotools = Autotools(self.conanfile)
        # Track if the project has been modified
        modified = False

        # Clone the sources into <build>/src/binutils
        try:
            self._clone_sources()
        except Exception as e:
            self.conanfile.output.error(f"Failed to clone sources of '{self.description.name}' ({e})")
            raise

        # Check if the project has been already configured
        try:
            if self._configure_project(
                autotools
            ):
                modified = True
        except Exception as e:
            self.conanfile.output.error(f"Failed to configure '{self.description.name}' ({e})")
            raise
        
        # Check if the project has been already built
        try:
            if self._build_project(
                autotools,
                build_target = target,
                build_args = build_args,
                doc_targets = doc_targets,
                extra_targets = extra_targets,
            ):
                modified = True
        except Exception as e:
            self.conanfile.output.error(f"Failed to build '{self.description.name}' ({e})")
            raise

        # Check if the project has been already installed
        try:
            if self._install_project(
                autotools,
                install_target = install_target,
                install_args = install_args,
                doc_install_targets = doc_install_targets,
                extra_install_targets = extra_install_targets,
                extra_install_files = extra_install_files,
            ):
                modified = True
        except Exception as e:
            self.conanfile.output.error(f"Failed to install '{self.description.name}' ({e})")
            raise

        # Cleanup the installation
        try:
            if self._cleanup_project():
                modified = True
        except Exception as e:
            self.conanfile.output.warning(f"Failed to cleanup '{self.description.name}' installation ({e})")

        return modified
    
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
    
    # ------------------------------------------------------------------ #

    @property
    def _steps(self):
        return {
            'configure': {
                'tag'                : self.dirs.build / '.configured', 
                'present_continuous' : 'configuring',
                'present_perfect'    : 'configured',
            },
            'build': {
                'tag'                : self.dirs.build / '.built',
                'present_continuous' : 'building',
                'present_perfect'    : 'built',
            },
            'extra-build': {
                'tag'                : self.dirs.build / '.extra-built',
                'present_continuous' : 'building extras',
                'present_perfect'    : 'extras-built',
            },
            'doc-build': {
                'tag'                : self.dirs.build / '.doc-built',
                'present_continuous' : 'building doc',
                'present_perfect'    : 'doc-built',
            },
            'install': {
                'tag'                : self.dirs.build / '.installed',
                'present_continuous' : 'installing',
                'present_perfect'    : 'installed',
            },
            'extra-install': {
                'tag'                : self.dirs.build / '.extra-installed',
                'present_continuous' : 'installing extras',
                'present_perfect'    : 'extras-installed',
            },
            'doc-install': {
                'tag'                : self.dirs.build / '.doc-installed',
                'present_continuous' : 'installing doc',
                'present_perfect'    : 'doc-installed',
            },
            'manual-install': {
                'tag'                : self.dirs.build / '.manual-installed',
                'present_continuous' : 'installing manually',
                'present_perfect'    : 'manually-installed',
            },
            'cleanup': {
                'tag'                : self.dirs.build / '.cleaned',
                'present_continuous' : 'cleaning up',
                'present_perfect'    : 'cleaned',
            },
        }

    def _with_step_tag(self, step):
        
        class _StepTag:

            def __init__(self, autotools_package, step):
                self._autotools_package = autotools_package
                self._step = step
            
            def __enter__(self):
                return self

            def exists(self):
                return self._autotools_package._steps[self._step]['tag'].exists()

            def __exit__(self, etype, value, traceback):

                # If we exit with an exception, remove the tag
                if etype is not None:
                    if self.exists():
                        self._autotools_package._steps[self._step]['tag'].unlink()
                        raise value
                        
                # Otherwise, create the tag
                self._autotools_package._steps[self._step]['tag'].touch()

        return _StepTag(self, step)
    
    def _to_present_perfect(self, step):
        return self._steps[step]['present_perfect']
    
    def _to_present_continuous(self, step):
        return self._steps[step]['present_continuous']

    def _run_step(self,
        step,
        process
    ):
        with self._with_step_tag(step) as step_guard:
            
            if step_guard.exists():
                self.conanfile.output.info(f"'{self.description.name}' has been already {self._to_present_perfect(step)}. Skipping...")
                return False

            self.conanfile.output.success(f"{self._to_present_continuous(step).capitalize()} '{self.description.name}'...")

            process()

            self.conanfile.output.success(f"'{self.description.name}' has been {self._to_present_perfect(step)} successfully.")

            return True
    
    def _clone_sources(self):
        
        # Clone the sources into <build>/src/binutils
        with contextlib.chdir(self.dirs.download):
            self.dirs.src = get(
                conanfile      = self.conanfile,
                url            = self.description.url,
                component_name = self.description.component_name,
                version        = self.description.version,
                destination    = self.dirs.src.as_posix(),
            )

    def _configure_project(self,
        autotools : Autotools,
    ):
        def process():

            # Clean the build directory just in case
            if self.dirs.build.exists():
                shutil.rmtree(self.dirs.build.as_posix(), ignore_errors = True)
                self.dirs.build.mkdir(parents = True, exist_ok = True)
            
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
        
        return self._run_step('configure', process)
    
    def _build_project(self,
        autotools : Autotools,
        build_target  : str | None = None,
        build_args    : list | None = None,
        doc_targets   : list = [ ],
        extra_targets : list = [],
    ):      
        modified = False

        # Get the build options & env
        build_options = self.description.get_build_options()
        env           = self.description.get_env()
        # Apply build options
        if build_options:
            os.environ['CXXFLAGS'] = ' '.join(build_options)
        # Extend environment
        if env:
            os.environ.update(env)

        with contextlib.chdir(self.dirs.build):

            def make_target(target):
                autotools.make(target = target, args = build_args)

            def process_build():
                make_target(build_target)

            def process_build_extras():
                for target in extra_targets:
                    make_target(target)

            def process_build_doc():
                for target in doc_targets:
                    make_target(target)

            # Build the project
            if self._run_step('build', process_build):
                modified = True
            # Build extra targets if needed
            if extra_targets:
                if self._run_step('extra-build', process_build_extras):
                    modified = True
            # Build doc targets if needed
            if self.conanfile.options.with_doc and (not self.description.without_doc):
                if doc_targets:
                    if self._run_step('doc-build', process_build_doc):
                        modified = True

        return modified
    
    def _install_project(self,
        autotools : Autotools,
        install_target        : str = 'install',
        install_args          : list | None = None,
        doc_install_targets   : list = [],
        extra_install_targets : list = [],
        extra_install_files   : dict = {},
    ):
        modified = False

        # Configure the project in the build directory
        with contextlib.chdir(self.dirs.build):

            def make_target(target):
                autotools.make(target = target, args = install_args)

            def process_install():
                make_target(install_target)

            def process_extra_install():
                for target in extra_install_targets:
                    make_target(target)

            def process_doc_install():
                for target in doc_install_targets:
                    make_target(target)

            def process_manual_install():

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

            # Install the project
            if self._run_step('install', process_install):
                modified = True
            # Install extra targets if needed
            if extra_install_targets:
                if self._run_step('extra-install', process_extra_install):
                    modified = True
            # Install doc targets if needed
            if self.conanfile.options.with_doc and (not self.description.without_doc):
                if doc_install_targets:
                    if self._run_step('doc-install', process_doc_install):
                        modified = True
            # Install some files manually if needed
            if self._run_step('manual-install', process_manual_install):
                modified = True

        return modified

    def _cleanup_project(self):

        def process_cleanup():
            for path in self.description.cleanup:
                path = self.dirs.prefix / path
                try:
                    if path.is_file():
                        path.unlink()
                    else:
                        shutil.rmtree(path.as_posix())
                except Exception as e:
                    self.conanfile.output.warning(f"Failed to remove '{path.as_posix()}' ({e})")

        # Cleanup the installation
        if self.description.cleanup:
            return self._run_step('cleanup', process_cleanup)

        return False

# ================================================================================================================================== #
