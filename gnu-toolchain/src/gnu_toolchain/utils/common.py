# ====================================================================================================================================
# @file       common.py
# @author     Krzysztof Pierczyk (you@you.you)
# @maintainer Krzysztof Pierczyk (you@you.you)
# @date       Tuesday, 1st October 2024 12:16:57 pm
# @modified   Tuesday, 1st October 2024 12:32:27 pm by Krzysztof Pierczyk (you@you.you)
# 
# 
# @copyright Your Company © 2024
# ====================================================================================================================================

# ============================================================ Imports ============================================================= #

# System imports
import builtins

# =========================================================== merge_dicts ========================================================== #

def merge_dicts(
    d1 : dict,
    d2 : dict,
    list_policy : str = 'append',
    dict_policy : str = 'recursive',
):
    """Merge two dictionaries into a new one. The way the `lists` are merged
    is controlled by the `list_policy` parameter:

    - 'append' (default) - lists are concatenated,
    - 'replace' - d2 values are used instead of d1 values,

    The way the `dicts` are merged is controlled by the `dict_policy` parameter:

    - 'recursive' (default) - the function is called recursively for each dict,
    - 'update' - values from d1 and d2 are merged using the `|` operator.

    Args
    ----
    d1 : dict
        First dictionary to be merged.
    d2 : dict
        Second dictionary to be merged.
    list_policy : str
        Policy for merging lists.
    dict_policy : str
        Policy for merging dictionaries.

    Returns
    -------
    dict
        Merged dictionary.
    """

    # Prepare the result
    result = {}

    # Merge the dictionaries
    for key in set(d1.keys()) | set(d2.keys()):

        # If the key is only present in the first dictionary, pick it
        if key not in d2:
            result[key] = d1[key]
        # If the key is only present in the second dictionary, pick it
        elif key not in d1:
            result[key] = d2[key]
        # If the key is present in both dictionaries, merge the values
        else:

            if type(d1[key]) != type(d2[key]):
                raise ValueError(f"Values of the key '{key}' in the dictionaries are of different types")
            
            match type(d1[key]):
                
                case builtins.dict:

                    if dict_policy == 'recursive':
                        result[key] = merge_dicts(d1[key], d2[key], list_policy, dict_policy)
                    elif dict_policy == 'update':
                        result[key] = d1[key] | d2[key]
                    else:
                        raise ValueError(f"Unknown dict_policy: '{dict_policy}'")
                    
                case builtins.list:

                    if list_policy == 'append':
                        result[key] = d1[key] + d2[key]
                    elif list_policy == 'replace':
                        result[key] = d2[key]
                    else:
                        raise ValueError(f"Unknown list_policy: '{list_policy}'")
                    
                case _:
                    result[key] = d2[key]

    return result

# ================================================================================================================================== #
