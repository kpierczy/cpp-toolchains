# ====================================================================================================================================
# @file       files.py
# @author     Krzysztof Pierczyk (you@you.you)
# @maintainer Krzysztof Pierczyk (you@you.you)
# @date       Tuesday, 1st October 2024 12:16:57 pm
# @modified   Wednesday, 2nd October 2024 7:36:31 am by Krzysztof Pierczyk (you@you.you)
# 
# 
# @copyright Your Company © 2024
# ====================================================================================================================================

# ============================================================= Imports ============================================================ #

# System imports
import pathlib
import os
# Conan imports
from conan.errors import ConanException
from conan.tools.files import download, ftp_download, unzip

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

# ================================================================================================================================== #
