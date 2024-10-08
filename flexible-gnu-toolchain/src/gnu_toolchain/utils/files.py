# ====================================================================================================================================
# @file       files.py
# @author     Krzysztof Pierczyk (you@you.you)
# @maintainer Krzysztof Pierczyk (you@you.you)
# @date       Tuesday, 1st October 2024 12:16:57 pm
# @modified   Tuesday, 8th October 2024 6:41:48 pm by Krzysztof Pierczyk (you@you.you)
# 
# 
# @copyright Your Company © 2024
# ====================================================================================================================================

# ============================================================= Imports ============================================================ #

# System imports
import pathlib
import contextlib
import os
# External imports
import patch_ng
# Conan imports
from conan.errors import ConanException
from conan.tools.files import download, ftp_download, unzip

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

# ================================================================================================================================== #
