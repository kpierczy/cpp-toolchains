# ====================================================================================================================================
# @file       files.py
# @author     Krzysztof Pierczyk (krzysztof.pierczyk@gmail.com)
# @maintainer Krzysztof Pierczyk (krzysztof.pierczyk@gmail.com)
# @date       Tuesday, 1st October 2024 12:16:57 pm
# @modified   Saturday, 12th October 2024 10:52:44 pm by Krzysztof Pierczyk (krzysztof.pierczyk@gmail.com)
# 
# 
# @copyright Your Company © 2024
# ====================================================================================================================================

# ============================================================= Imports ============================================================ #

# System imports
import pathlib
import contextlib
import os
import tempfile
import shutil
# External imports
import patch_ng
# Conan imports
from conan.errors import ConanException
from conan.tools.files import download, ftp_download, unzip, copy

# =============================================================== get ============================================================== #

def get(
    conanfile,
    url,
    component_name,
    version,
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

    # Compute path to the patches dir of the given component
    patches_dir = pathlib.Path(conanfile.recipe_folder) / \
        'patches' /                                       \
            str(conanfile.settings.os).lower() /          \
                component_name /                          \
                    version
    
    # If set of patchfiles for the 
    if not patches_dir.exists():
        conanfile.output.info(f"No patches found in '{patches_dir.as_posix()}'. Skipping...")
    else:
        conanfile.output.info(f"Patches directory for {component_name}/{version} found. Looking for patches...")
        with contextlib.chdir(src_dir):
            for patch in patches_dir.iterdir():
                conanfile.output.info(f"Applying patch '{(patches_dir / patch).as_posix()}'...")
                patchset = patch_ng.fromfile(patch.as_posix())
                if not patchset:
                    raise ConanException(f"Failed to parse patch '{patch.name}'")
                if not patchset.apply():
                    raise ConanException(f"Failed to apply patch '{patch.name}'")

    return src_dir

# ======================================================== copy_with_rename ======================================================== #

def copy_with_rename(
    conanfile,
    pattern,
    src,
    dst,
    **kwargs,
):
    """
    Wraps the `conan.tools.files.copy` function to provide capability of files renaming

    Description
    -----------
    Standard `conan.tools.files.copy` treats the `dst` as the directory. This is unhandy
    when it comes to installation of the target files during the pipeline as we need capability
    to rename some files during the installation. This function differentiates `dst` into
    files and directories depending on the presence of the trailing slash. If the `dst` ends
    with the slash, the function just calls the `conan.tools.files.copy` with the given
    arguments. Otherwise, the function treats the `dst` as the target file name (note that in this case
    the pattern is expected to match at most one file) and renames the file during the installation.
    """

    # Print log message
    conanfile.output.debug(f"Copying:")
    conanfile.output.debug(f" - {pattern}")
    conanfile.output.debug(f" - from {src}")
    conanfile.output.debug(f" - to {dst}")
    
    # If the destination is a directory, just copy the files
    if dst.endswith('/'):

        copied_files = copy(conanfile, pattern=pattern, src=src, dst=dst, **kwargs)

        conanfile.output.debug(f" - {len(copied_files)} file{'s' if len(copied_files) != 1 else ''} copied")

    # Otherwise, treat the destination as the target file name
    else:
        
        # Copy the files to the temporary directory
        with tempfile.TemporaryDirectory() as tmp_dir:

            # Copy the files
            copied_files = copy(conanfile, pattern=pattern, src=src, dst=tmp_dir, **kwargs)

            assert len(copied_files) <= 1, f"Pattern '{pattern}' matches more than one file. Cannot rename the file!"

            # Rename the file
            if copied_files:

                # Create the parent directory if it does not exist
                pathlib.Path(dst).parent.mkdir(
                    parents=True,
                    exist_ok=True
                )
                
                # Copy the file to the destination
                shutil.copy(
                    pathlib.Path(tmp_dir) / copied_files[0],
                    pathlib.Path(dst)
                )

                conanfile.output.debug(f" - copied {copied_files[0]} to {dst}")

    return copied_files

# ================================================================================================================================== #
