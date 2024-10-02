# ====================================================================================================================================
# @file       toolchain.py
# @author     Krzysztof Pierczyk (you@you.you)
# @maintainer Krzysztof Pierczyk (you@you.you)
# @date       Wednesday, 2nd October 2024 6:29:53 am
# @modified   Wednesday, 2nd October 2024 12:08:12 pm by Krzysztof Pierczyk (you@you.you)
# 
# 
# @copyright Your Company © 2024
# ====================================================================================================================================

# ======================================================== CommonDescription ======================================================= #

class CommonDescription:

    # List of files to be copied to the package directory (installed directly to the package directory if None)
    target_files = None
    # List of files to be removed after installation
    cleanup_files = None

    # By default buid doc
    without_doc = False
    
    # ------------------------------------------------------------------ #

    def __init__(self,
        conanfile,
    ):
        self.conanfile = conanfile

        # Pick source of the component name
        dep_name = getattr(self, 'dep_name', self.name)

        # Parse version of the component
        self.version = getattr(conanfile.options, f'with_{dep_name}_version', None)
        # Parse URL of the component
        self.url = str(getattr(conanfile.options, f'with_{dep_name}_url')).format(
            version = self.version   
        )

    def make_driver(self, **kwargs):
        return self.driver(
            description = self,
            **kwargs
        )

    # ------------------------------------------------------------------ #
            
    def get_config(self) -> list:
        return self._get_build_typed_descriptor(
            'config'
        )
    
    def get_build_options(self) -> list:
        return self._get_build_typed_descriptor(
            'build_options'
        )
    
    def get_env(self) -> dict:
        return self._get_build_typed_descriptor(
            'env',
            default = { }
        )

    # ------------------------------------------------------------------ #

    def _get_build_typed_descriptor(self,
        member,
        default = [ ]
    ):

        """Picks the configuration of the component from the `member` object
        based on the `self.conanfile.settings.build_type` parameter. If it is
        a dictionary, the method picks the value of the `build_type` key or the
        value of the '_' key if the `build_type` key is not present (in case of
        both lacking, the method returns an empty list).

        Otherwise, the method returns the `member` object itself.
        """

        object = getattr(self, member, None)

        if isinstance(object, dict):
            return object.get(
                str(self.conanfile.settings.build_type),
                object.get('_', default)
            )
        else:
            return object

# ================================================================================================================================== #
