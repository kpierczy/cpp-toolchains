# ====================================================================================================================================
# @file       system.py
# @author     Krzysztof Pierczyk (you@you.you)
# @maintainer Krzysztof Pierczyk (you@you.you)
# @date       Tuesday, 1st October 2024 12:16:57 pm
# @modified   Saturday, 12th October 2024 1:21:00 pm by Krzysztof Pierczyk (you@you.you)
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
from conan.tools.gnu import Autotools
# Private imports
from gnu_toolchain.utils.files import get, copy_with_rename

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
        
        target        : str         = None,
        build_args    : list | None = None,
        doc_targets   : list        = [],
        extra_targets : list        = [],

        install_target        : str         = 'install',
        install_args          : list | None = None,
        doc_install_targets   : list        = [],
        extra_install_targets : list        = [],
        extra_install_files   : dict        = {},

        clean_target     : str  = 'clean',
        clean_on_rebuild : bool = False,
        
    ):
        """Downloads, configures and builds the autotools project"""

        # Compile dirs
        self._create_dirs()

        # Create the autotools driver
        autotools = Autotools(self.conanfile)

        # Clone the sources into <build>/src/binutils
        self._clone_sources()

        # Check if the project has been already configured
        configured = self._configure_project(
            autotools
        )
        
        # Remove build tags if the project has been configured
        if configured:
            self._remove_all_step_tags_from('build')
        # Check if the project has been already built
        built = self._build_project(
            autotools,
            build_target = target,
            build_args = build_args,
            doc_targets = doc_targets,
            extra_targets = extra_targets,
            clean_target = clean_target,
            clean_build = (not configured) and clean_on_rebuild,
        )

        # Remove install tags if the project has been built
        if built:
            self._remove_all_step_tags_from('install')
        # Check if the project has been already installed
        installed = self._install_project(
            autotools,
            install_target = install_target,
            install_args = install_args,
            doc_install_targets = doc_install_targets,
            extra_install_targets = extra_install_targets,
            extra_install_files = extra_install_files,
        )

        # Remove cleanup tags if the project has been installed
        if installed:
            self._remove_all_step_tags_from('cleanup')
        # Cleanup the installation
        cleaned = self._cleanup_project()

        return (
            configured or
            built or
            installed or
            cleaned
        )
    
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

    @property
    def _common_config(self):

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
                'infinitive'         : 'configure',
                'present_continuous' : 'configuring',
                'present_perfect'    : 'has been configured',
            },
            'build-cleaning': {
                'infinitive'         : 'clean build',
                'present_continuous' : 'cleaning build',
                'present_perfect'    : 'buil has been cleaned',
            },
            'build': {
                'tag'                : self.dirs.build / '.built',
                'infinitive'         : 'build',
                'present_continuous' : 'building',
                'present_perfect'    : 'has been built',
            },
            'extra-build': {
                'tag'                : self.dirs.build / '.built-extra',
                'infinitive'         : 'build extras',
                'present_continuous' : 'building extras',
                'present_perfect'    : 'extras has been built',
            },
            'doc-build': {
                'tag'                : self.dirs.build / '.built-doc',
                'infinitive'         : 'build doc',
                'present_continuous' : 'building doc',
                'present_perfect'    : 'doc has been built',
            },
            'install': {
                'tag'                : self.dirs.build / '.installed',
                'infinitive'         : 'install',
                'present_continuous' : 'installing',
                'present_perfect'    : 'has been installed',
            },
            'extra-install': {
                'tag'                : self.dirs.build / '.installed-extra',
                'infinitive'         : 'install extras',
                'present_continuous' : 'installing extras',
                'present_perfect'    : 'extras has been installed',
            },
            'doc-install': {
                'tag'                : self.dirs.build / '.installed-doc',
                'infinitive'         : 'install doc',
                'present_continuous' : 'installing doc',
                'present_perfect'    : 'doc has been installed',
            },
            'manual-install': {
                'tag'                : self.dirs.build / '.installed-manual',
                'infinitive'         : 'install manuall components',
                'present_continuous' : 'installing manual components',
                'present_perfect'    : 'manual components has been installed',
            },
            'cleanup': {
                'tag'                : self.dirs.build / '.cleaned',
                'infinitive'         : 'cleanup',
                'present_continuous' : 'cleaning up',
                'present_perfect'    : 'has been cleaned',
            },
        }
    
    def _remove_all_step_tags_from(self,
        step
    ):
        assert step in self._steps, f"[AutotoolsPackage][BUG] Unknown step '{step}'!"

        # Get the index of the target step
        target_step_index = list(self._steps.keys()).index(step)
        # Remove all tags after the target step
        for step_index, step in enumerate(list(self._steps.keys())):
            if step_index >= target_step_index:
                if self._steps[step]['tag'].exists():
                    self.conanfile.output.info(f"Removing '{self._steps[step]['tag'].as_posix()}' tag...")
                    self._steps[step]['tag'].unlink()

    def _has_step_tag(self,
        step
    ):
        return self._steps[step]['tag'].exists()

    def _with_step_tag(self, step):
        
        class _StepTag:

            def __init__(self, autotools_package, step):
                self._autotools_package = autotools_package
                self._step = step
            
            def __enter__(self):
                return self

            def exists(self):
                return self._autotools_package._has_step_tag(self._step)

            def __exit__(self, etype, value, traceback):

                # If we exit with an exception, remove the tag
                if etype is not None:
                    if self.exists():
                        self._autotools_package._steps[self._step]['tag'].unlink()
                    raise value
                        
                # Otherwise, create the tag
                self._autotools_package._steps[self._step]['tag'].touch()

        return _StepTag(self, step)
    
    def _to_infinitive(self, step):
        return self._steps[step]['infinitive']
    
    def _to_present_perfect(self, step):
        return self._steps[step]['present_perfect']
    
    def _to_present_continuous(self, step):
        return self._steps[step]['present_continuous']
    
    def _process_step(self,
        process,
        step,
    ):
        self.conanfile.output.success(f"{self._to_present_continuous(step).capitalize()} '{self.description.name}'...")

        try:
            process()
        except Exception as e:
            self.conanfile.output.error(f"Failed to {self._to_infinitive(step)} '{self.description.name}' ({e})")
            raise

        self.conanfile.output.success(f"'{self.description.name}' {self._to_present_perfect(step)} successfully.")

    def _run_step(self,
        step,
        process
    ):
        with self._with_step_tag(step) as step_guard:
            
            if step_guard.exists():
                self.conanfile.output.info(f"'{self.description.name}' {self._to_present_perfect(step)} yet. Skipping...")
                return False
            
            self._process_step(
                process = process,
                step    = step,
            )

            return True

    def _create_dirs(self,
        skip = [ 'src' ]
    ):
        for name, path in self.dirs.__dict__.items():
            if (name not in skip) and (path.is_absolute()):
                path.mkdir(parents = True, exist_ok = True)
    
    def _clone_sources(self):
        
        # Clone the sources into <build>/src/binutils
        with contextlib.chdir(self.dirs.download):
            try:
                self.dirs.src = get(
                    conanfile      = self.conanfile,
                    url            = self.description.url,
                    component_name = self.description.component_name,
                    version        = self.description.version,
                    destination    = self.dirs.src.as_posix(),
                )
            except Exception as e:
                self.conanfile.output.error(f"Failed to clone sources of '{self.description.name}' ({e})")
                raise

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
            config += self._common_config

            # Configure the project in the build directory
            with contextlib.chdir(self.dirs.build):
                autotools.configure(
                    build_script_folder = self.dirs.src.as_posix(),
                    args = config
                )
        
        return self._run_step('configure', process)
    
    def _build_project(self,
        autotools     : Autotools,
        build_target  : str,
        build_args    : list,
        doc_targets   : list,
        extra_targets : list,
        clean_target  : str,
        clean_build   : bool,
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

            def process_clean_build():
                make_target(clean_target)

            def process_build():

                # Clean the build directory just in case
                if clean_build:
                    self._process_step(
                        process = process_clean_build,
                        step    = 'build-cleaning',
                    )
                
                # Build the project
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
        autotools             : Autotools,
        install_target        : str,
        install_args          : list,
        doc_install_targets   : list,
        extra_install_targets : list,
        extra_install_files   : dict,
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
                        copy_with_rename(self.conanfile,
                            pattern = pattern,
                            src     = f'{self.dirs.offprefix.as_posix()}',
                            dst     = f'{self.dirs.prefix.as_posix()}/{dst}',
                        )

                # Install extra files directly from the build tree if needed
                for pattern, dst in extra_install_files.items():
                    self.conanfile.output.success(f"Copying extra files to the install directory...")
                    copy_with_rename(self.conanfile,
                        pattern = pattern.as_posix(),
                        src     = f'{self.dirs.build.as_posix()}',
                        dst     = f'{self.dirs.prefix.as_posix()}/{dst}',
                    )

                # For Windows, install msys2 runtime in the /lib directory if we use it
                if (self.conanfile.settings.os == 'Windows') and ('msys2' in self.conanfile.dependencies.build):
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
            for path in self.description.cleanup_files:
                path = self.dirs.prefix / path
                try:
                    if path.is_file():
                        path.unlink()
                    else:
                        shutil.rmtree(path.as_posix())
                except Exception as e:
                    self.conanfile.output.warning(f"Failed to remove '{path.as_posix()}' ({e})")

        # Cleanup the installation
        if self.description.cleanup_files:
            return self._run_step('cleanup', process_cleanup)

        return False

# ================================================================================================================================== #
