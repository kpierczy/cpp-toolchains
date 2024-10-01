# ====================================================================================================================================
# @file       system.py
# @author     Krzysztof Pierczyk (you@you.you)
# @maintainer Krzysztof Pierczyk (you@you.you)
# @date       Tuesday, 1st October 2024 12:16:57 pm
# @modified   Tuesday, 1st October 2024 12:32:34 pm by Krzysztof Pierczyk (you@you.you)
# 
# 
# @copyright Your Company © 2024
# ====================================================================================================================================

# ======================================================== get_host_triplet ======================================================== #

def get_host_triplet(
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

# ================================================================================================================================== #
