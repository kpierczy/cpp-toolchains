# ====================================================================================================================================
# @file       arm-none-eabi.py
# @author     Krzysztof Pierczyk (krzysztof.pierczyk@gmail.com)
# @maintainer Krzysztof Pierczyk (krzysztof.pierczyk@gmail.com)
# @date       Tuesday, 1st October 2024 9:16:08 am
# @modified   Tuesday, 1st October 2024 8:29:16 pm by Krzysztof Pierczyk (you@you.you)
# 
# 
# @copyright PG Techonologies © 2024
# ====================================================================================================================================

# ============================================================= Imports ============================================================ #

# System imports
import pathlib

# ============================================================ Script ============================================================== #

class Config:

    def __init__(self,
        conanfile
    ):
        self.target      = "arm-none-eabi"
        self.pkg_version = f"GNU ARM Embedded Toolchain {str(conanfile.options.with_gcc_version)}"
        self.build_type  = conanfile.settings.build_type

    def _make_common(self):
        return {
            
            "target" : self.target,

            "build-options" : [

                *([
                    "-g",
                    "-O2",
                ] if self.build_type == "Release" else [ ]),

                *([
                    "-g",
                    "-O0",
                ] if self.build_type == "Debug" else [ ]),

            ],
        }
    
    def _make_dependencies(self):
        return {

            "common" : {
                "options" : {
                    "shared" : False,
                }
            },

            "gmp" : {
                "options" : {
                    "enable_cxx" : True,
                }
            },
            
        }
    
    def _make_binutils(self):
        return {

            "config-options" : [

                "--disable-nls",
                "--disable-werror",
                "--disable-sim",
                "--disable-gdb",
                "--enable-interwork",
                "--enable-plugins",
                f"--with-pkgversion={self.pkg_version}",
                    
            ],

            "cleanup" : [
                pathlib.Path('lib'),
            ],

        }
    
    def _make_compiler_common_config_options(self):
        return [

            # Package version
            f"--with-pkgversion={self.pkg_version}",
                
            # Lib static libraries to the compiler
            "--with-host-libstdcxx=-static-libgcc -Wl,-Bstatic,-lstdc++,-Bdynamic -lm",

            # ---------------------------------------------------------------------------
            # @brief Resulting toolchain will be compiled with multilib support (e.g.
            #    libc, libc++, libgcc, libgloss, etc. compiled for many target
            #    architectures) targetting Cortex-M and Cortex-R cores. If Cortex-A
            #    support is needed, modify multilib option to:
            #
            #       --with-multilib-list=rmprofile,aprofile
            #
            # @note Execute `arm-none-eabi-gcc -print-multi-lib` to list included
            #   architectures. Paths to the variant folders are printed relative to
            #   'arm-none-eabi/lib' directory
            # ---------------------------------------------------------------------------
            "--with-multilib-list=rmprofile",

            # Common config
            "--disable-libgomp",
            "--disable-libmudflap",
            "--disable-libquadmath",
            "--disable-libssp",
            "--disable-nls",
            "--disable-shared",
            "--disable-threads",
            "--disable-tls",
            "--with-gnu-as",
            "--with-gnu-ld",
            "--enable-checking=release",
            
        ]

    def _make_compiler_base(self):
        return {

            "config-options" : [

                # Common GCC options
                *self._make_compiler_common_config_options(),

                # Basic options
                "--enable-languages=c",         # -----------------------------------------------------
                "--with-newlib",        # <---- # For great explenation of these two options 
                "--without-headers",    # <---- # @see https://www.ryanstan.com/withoutHeaders.html
                                                # -----------------------------------------------------
                
            ],

            "cleanup" : [
                pathlib.Path('bin') / f'{self.target}-gccbug',
                pathlib.Path('lib') / 'libiberty.a',
                pathlib.Path('include'),
            ],

        }
    
    def _make_compiler_newlib_final(self):

        # ---------------------------------------------------------------------------
        # @brief 'compiler_newlib_final' run builds whole GCC (simple 'make') with the
        #    sysroot configured to the --prefix installation location. As a result,
        #    the compiler's libraries (especially libc++, but also libgcc, libgloss,
        #    etc.) are linekd to the 'classic' version of the Newlib library.
        #
        # @note This version of the libraries is compiled with -O2
        # ---------------------------------------------------------------------------
        
        return {

            "config-options" : [

                # Common GCC options
                *self._make_compiler_common_config_options(),
                
                # Final options
                "--enable-languages=c,c++",
                "--enable-plugins",
                "--with-newlib",
                "--with-headers=yes",

            ],

            "env" : {

                # ----------------------------------------------------------------------
                # @note [INHIBIT_LIBC_CFLAGS] variable is set to disable transactional 
                #     memory related code in crtbegin.o. This is a workaround. Better
                #     approach is have a t-* to set this flag via CRTSTUFF_T_CFLAGS
                # ----------------------------------------------------------------------
                "INHIBIT_LIBC_CFLAGS" : "-DUSE_TM_CLONE_REGISTRY=0",


            },
            
        }
    
    def _make_compiler_newlib_nano_final(self):
    
        # ---------------------------------------------------------------------------
        # @brief The 'compiler_newlib_nano_final' run builds whole GCC (simple 'make') 
        #    with the sysroot configured to the external newlib-nano installation 
        #    location. As a result, the compiler's libraries (especially libc++, but 
        #    also libgcc, libgloss, etc.) are linekd to the 'nano' version of the
        #    library. Resulting files, i.e.:
        #
        #      - static libraries [arm-none-eabi/lib(/arm:/thumb)]
        #      - startup files, e.g. (crt0) [arm-none-eabi/lib]
        #      - GCC spec files [arm-none-eabi/lib]
        #
        #    are copied into the target --prefix location.
        #
        # @note This version of the libraries is compiled with -Os
        # ---------------------------------------------------------------------------

        return {

            "config-options" : [

                # Common GCC options
                *self._make_compiler_common_config_options(),

                # Final options
                "--enable-languages=c,c++",
                "--disable-libstdcxx-verbose",
                "--with-newlib",
                "--with-headers=yes",

            ],

            "env" : {

                "CFLAGS_FOR_TARGET" : """
                    -g
                    -Os
                    -ffunction-sections
                    -fdata-sections
                    -fno-exceptions
                """,

            },

        }
        
    def _make_newlib(self):
        return {

            "config-options" : [
                "--enable-newlib-io-long-long",
                "--enable-newlib-io-c99-formats",
                "--enable-newlib-reent-check-verify",
                "--enable-newlib-register-fini",
                "--enable-newlib-retargetable-locking",
                "--disable-newlib-supplied-syscalls",
                "--disable-nls",
            ],

            "env" : {

                "CFLAGS_FOR_TARGET" : """
                    -ffunction-sections
                    -fdata-sections
                    -O2
                """ + ("""
                    -g
                """ if self.build_type == "Debug" else ""),

            },

        }
    
    def _make_newlib_nano(self):
        
        # ---------------------------------------------------------------------------
        # @brief In this script (which is functionally improved equivalent of the 
        #    original ARM bash building scripts wrt resulting toolchain) the 'libc'
        #    build step is used to build "Classic Newlib" library targetting bigger
        #    cores (Cortex-A), while 'libc_aux' step builds so called "Newlib Nano".
        #    Important note here is that both libraries **are compiled from the
        #    source code base** and differ only in terms of options options passed
        #    to Autotools during configuration. The "Newlib Nano" thing is in general
        #    a fancy name for the library variant introduced by ARM at some revision
        #    of their "ARM Embedded Toolchain".
        #
        #    To versions of the library are accompanied by two dedicated spec files
        #    (nano.specs and nosys.specs in arm-none-eabi/lib) which guide gcc
        #    compiler in decision of:
        #
        #      - which variant of C library should application be linked against
        #        (arm-none-eabi/lib/libc.a or arm-none-eabi/lib/libc_nano.a)
        #      - which variant of rdimon [1] library should application be linked 
        #        against (arm-none-eabi/lib/libc.a or arm-none-eabi/lib/libc_nano.a)
        #      - what should be search order of standard includes directories
        #        (nano version prepends search list with arm-none-eabi/include
        #        /newlib-nano folder)
        #
        #    Newlib Nano version is build by the script in the external (wrt to the
        #    target --prefix directory) location. Resulting files are used by the
        #    'gcc_final_aux' step to build libstdc++ library in the 'nano' version.
        #
        # @note [1] 'rdimon' library implements ARM-defined semihosting mechanism
        #    for Cortex-M (see https://github.com/ARM-software/abi-aa/blob/main/
        #    semihosting/semihosting.rst). It is part of the 'libgloss' library
        #    (implementing platform-specific code)
        # @see https://mcuoneclipse.com/2023/01/28/which-embedded-gcc-standard-
        #    library-newlib-newlib-nano/
        # @see https://community.arm.com/arm-community-blogs/b/embedded-blog/
        #    posts/shrink-your-mcu-code-size-with-gcc-arm-embedded-4-7
        #
        # @note This version of the library is compiled with -Os
        # ---------------------------------------------------------------------------

        return {

            "config-options" : [
                "--disable-newlib-supplied-syscalls",
                "--enable-newlib-reent-check-verify",
                "--enable-newlib-reent-small",
                "--enable-newlib-retargetable-locking",
                "--disable-newlib-fvwrite-in-streamio",
                "--disable-newlib-fseek-optimization",
                "--disable-newlib-wide-orient",
                "--enable-newlib-nano-malloc",
                "--disable-newlib-unbuf-stream-opt",
                "--enable-lite-exit",
                "--enable-newlib-global-atexit",
                "--enable-newlib-nano-formatted-io",
                "--disable-nls",
            ],

            "env" : {

                "CFLAGS_FOR_TARGET" : """
                    -ffunction-sections
                    -fdata-sections
                    -Os
                """ + ("""
                    -g
                """ if self.build_type == "Debug" else ""),

            },

        }

    def _make_gdb(self):

        return {

            "config-options" : [
                "--disable-nls"
                "--disable-sim"
                "--disable-gas"
                "--disable-binutils"
                "--disable-ld"
                "--disable-gprof"
                "--with-lzma=no"
                "--with-gdb-datadir=arm-none-eabi/share/gdb"
                f"--with-pkgversion=${self.pkg_version}"
            ],

        }

    def make(self):
        return {

            **self._make_common(),

            # Components
            "components" : {

                "dependencies" : self._make_dependencies(),
                
                "binutils" : self._make_binutils(),
                
                "gcc" : {
                    "base" : self._make_compiler_base(),
                    "full" : [
                        {
                            "name"        : "standard",
                            "config"      : self._make_compiler_newlib_final(),
                            "libc_name"   : "newlib",
                            "libc_config" : self._make_newlib(),
                        },
                        {
                            "name"        : "nano",
                            "config"      : self._make_compiler_newlib_nano_final(),
                            "libc_name"   : "newlib",
                            "libc_config" : self._make_newlib_nano(),
                        },
                    ],
                },

                "gdb" : self._make_gdb(),

            },
        }

# ================================================================================================================================== #
