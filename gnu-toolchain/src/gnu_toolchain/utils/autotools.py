# ====================================================================================================================================
# @file       system.py
# @author     Krzysztof Pierczyk (you@you.you)
# @maintainer Krzysztof Pierczyk (you@you.you)
# @date       Tuesday, 1st October 2024 12:16:57 pm
# @modified   Tuesday, 1st October 2024 7:57:08 pm by Krzysztof Pierczyk (you@you.you)
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
from conan.errors import ConanException
from conan.tools.files import copy, download, ftp_download, unzip
from conan.tools.gnu import AutotoolsToolchain, Autotools
# Private imports
from gnu_toolchain.utils.system import get_host_triplet

# =============================================================== get ============================================================== #

def get(
    conanfile,
    url,
    destination,
    **kwargs,
):
    """
    Custom reimplementation of the `conan.tools.files.get` function that avoids
    redownloading/reunzipping sources if they are already present in the Conan.
    """

    # Deduce file name from the url
    url_base = url[0] if isinstance(url, (list, tuple)) else url
    if "?" in url_base or "=" in url_base:
        raise ConanException("Cannot deduce file name from the url: '{}'. Use 'filename' parameter.".format(url_base))
    filename = os.path.basename(url_base)
    
    src_dir_name = str(filename) \
        .removesuffix('.tar.gz') \
        .removesuffix('.tar.xz') \
        .removesuffix('.tar.bz2')
    
    # Compute src directory
    src_dir = pathlib.Path(destination) / src_dir_name

    # Download the file, if not already downloaded
    if not pathlib.Path(filename).exists():
        conanfile.output.info(f"Dowloading '{filename}' from '{url}' into '{src_dir.as_posix()}'...")
        if url.startswith("ftp://"):
            host, ftp_filename = url.removeprefix("ftp://").split("/", 1)
            ftp_download(conanfile, host, filename=ftp_filename)
        else:
            download(conanfile, url, filename=filename)
    else:
        conanfile.output.info(f"'{filename}' already downloaded. Skipping...")

    # Unzip the file, if not already unzipped
    tag_file = src_dir / '.downloaded'
    if not tag_file.exists():
        unzip(conanfile, filename, destination=destination, **kwargs)
        tag_file.touch()
    else:
        conanfile.output.info(f"'{filename}' already unzipped. Skipping...")

    return src_dir

# ============================================================ get_dirs ============================================================ #

def get_dirs(
    conanfile,
    target: str,
    name: str = None,
):
    class Object(object):
        pass

    result = Object()
    
    # Compile common paths
    setattr(result, 'src_dir',         pathlib.Path(conanfile.build_folder) / "src")
    setattr(result, 'download_dir',    pathlib.Path(conanfile.build_folder) / "download")
    setattr(result, 'install_dir',     pathlib.Path(conanfile.build_folder) / "install")
    setattr(result, 'target_dir',      pathlib.Path(conanfile.build_folder) / "target")
    setattr(result, 'doc_install_dir', result.install_dir                   / 'share' / 'doc' / f'gcc-{target}')
    # Create common directories
    result.download_dir.mkdir(parents = True, exist_ok = True)
    result.install_dir.mkdir (parents = True, exist_ok = True)
    result.target_dir.mkdir  (parents = True, exist_ok = True)

    if name is not None:

        # Compile target paths
        setattr(result, 'build_dir', pathlib.Path(conanfile.build_folder) / "build" / name)
        # Create target directories
        result.build_dir.mkdir(parents = True, exist_ok = True)

    return result
        
# ============================================================== build ============================================================= #

def build(
    conanfile,
    name: str,
    url: str,
    config : dict,
    copy_to_target : bool = False,
    target : str = None,
    skip_doc : bool = False,
    extra_install_files: dict = {},
    extra_targets: list = [],
    install_target : str = 'install',
    install_to_target : bool = False,
    extra_install_targets: list = [],
):
    """Downloads, configures and builds the autotools project"""

    # Compile paths
    paths = get_dirs(conanfile, config['target'], name)

    # Clone the sources into <build>/src/binutils
    with contextlib.chdir(paths.download_dir):
        paths.src_dir = get(conanfile, url, destination = paths.src_dir.as_posix())

    # Check if the project has been already built
    build_tag = paths.build_dir / '.built'
    if build_tag.exists():
        conanfile.output.info(f"'{name}' has been already built. Skipping...")
        return False
    
    # Clean the build directory
    if paths.build_dir.exists():
        shutil.rmtree(paths.build_dir.as_posix(), ignore_errors = True)
        paths.build_dir.mkdir(parents = True, exist_ok = True)

    conanfile.output.info(f"Configuring '{name}'...")

    # Create the autotools driver
    autotools = Autotools(conanfile)

    # Extend the config with standard options
    config["config-options"] += [
        f"--build={get_host_triplet(conanfile)}",
        f"--host={get_host_triplet(conanfile)}",
        f"--target={config['target']}"]
    # If documentation requested, add the option
    if conanfile.options.with_doc and not skip_doc:
        config["config-options"] += [
            f"--infodir={paths.doc_install_dir}/info",
            f"--mandir={paths.doc_install_dir}/man",
            f"--htmldir={paths.doc_install_dir}/html",
            f"--pdfdir={paths.doc_install_dir}/pdf",
        ]

    # Configure the project in the build directory
    with contextlib.chdir(paths.build_dir):
        autotools.configure(
            build_script_folder = paths.src_dir.as_posix(),
            args = config["config-options"]
        )

    conanfile.output.info(f"Building '{name}'...")

    # Build the project
    with contextlib.chdir(paths.build_dir):

        # Apply build options
        if 'build-options' in config:
            os.environ['CXXFLAGS'] = ' '.join(config['build-options'])
        # Extend environment
        if 'env' in config:
            os.environ.update(config['env'])

        try:

            # Build the project
            autotools.make(target = target)
            # Build extra targets if needed
            if extra_targets:
                autotools.make(target = ' '.join(extra_targets))

        except Exception as e:
            conanfile.output.error(f"Failed to build '{name}' ({e})")
            raise

        # Install extra files if needed
        for pattern, dst in extra_install_files.items():
            copy(conanfile, pattern, src = paths.build_dir, dst = dst)

    conanfile.output.info(f"Installing '{name}'...")

    # Configure the project in the build directory
    with contextlib.chdir(paths.build_dir):

        # Pick destdir
        if not install_to_target:
            destdir = f'DESTDIR={paths.install_dir.as_posix()}'
        else:
            destdir = f'DESTDIR={paths.target_dir.as_posix()}'

        install_args = [
            destdir,
        ]

        try:

            # Install the project
            autotools.install(
                target = install_target,
                args = install_args)
            # Install extra targets if needed
            if extra_install_targets:
                autotools.install(
                    target = ' '.join(extra_install_targets),
                    args = install_args,
                )

        except Exception as e:
            conanfile.output.error(f"Failed to install '{name}' ({e})")
            raise

    # Copy the results to the target directory
    if copy_to_target:
        copy(conanfile, '*', src = paths.install_dir, dst = paths.target_dir)

    # Remove useless compilation results
    if 'cleanup' in config:
        for path in config['cleanup']:
            path = paths.install_dir / path
            try:
                if path.is_file():
                    path.unlink()
                else:
                    shutil.rmtree(path.as_posix())
            except Exception as e:
                conanfile.output.warning(f"Failed to remove '{path.as_posix()}' ({e})")

    # Create the build tag
    build_tag.touch()

    return True

# ================================================================================================================================== #
