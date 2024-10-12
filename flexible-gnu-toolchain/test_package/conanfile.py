# ====================================================================================================================================
# @file       conanfile.py
# @author     Krzysztof Pierczyk (krzysztof.pierczyk@gmail.com)
# @maintainer Krzysztof Pierczyk (krzysztof.pierczyk@gmail.com)
# @date       Saturday, 12th October 2024 10:56:25 pm
# @modified   Saturday, 12th October 2024 11:04:01 pm by Krzysztof Pierczyk (krzysztof.pierczyk@gmail.com)
# 
# 
# @copyright Krzysztof Pierczyk © 2024
# ====================================================================================================================================

# ============================================================ Imports ============================================================= #

# Conan imports
from conan import ConanFile
from conan.tools.layout import basic_layout

# ============================================================ Script ============================================================== #

class GnuToolchainConan(ConanFile):
    
    settings = [ 'os', 'compiler', 'build_type', 'arch' ]

    # ------------------------------------------------------------------ #

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def layout(self):
        basic_layout(self, src_folder="src")
        
    def build(self):
        self.run(' '.join([
            'arm-none-eabi-g++', f'{self.source_folder}/main.cpp',
                '-o', 'package_test',
                '--specs=nosys.specs',
                '--mcpu=cortex-m4',
                '--mthumb',
                '--mfpu=fpv4-sp-d16',
                '--mfloat-abi=hard',
        ]))

# ================================================================================================================================== #
