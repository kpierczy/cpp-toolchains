# ====================================================================================================================================
# @file       arm-none-eabi.py
# @author     Krzysztof Pierczyk (krzysztof.pierczyk@gmail.com)
# @maintainer Krzysztof Pierczyk (krzysztof.pierczyk@gmail.com)
# @date       Tuesday, 1st October 2024 9:16:08 am
# @modified   Wednesday, 2nd October 2024 12:00:01 pm by Krzysztof Pierczyk (you@you.you)
# 
# 
# @copyright PG Techonologies © 2024
# ====================================================================================================================================

# ============================================================= Imports ============================================================ #

# System imports
import pathlib
# Package imports
from gnu_toolchain.description import *

# ============================================================= Globals ============================================================ #

target = 'arm-none-eabi'

# ========================================================== Dependencies ========================================================== #

class Dependencies(DependenciesDescription):

    common_options = {
        "shared" : False,
    }

    options = {

        "gmp" : {
            "enable_cxx" : True,
        },

    }
    
# ============================================================= Common ============================================================= #

class Common():

    build_options = {

        'Debug' : [
            "-g",
            "-O0",
        ],

        '_' : [
            "-g",
            "-O2",
        ],

    }

# ============================================================ Binutils ============================================================ #

class Binutils(Common, BinutilsDescription):

    config = [
        "--disable-nls",
        "--disable-werror",
        "--disable-sim",
        "--disable-gdb",
        "--enable-interwork",
        "--enable-plugins",
    ]

    # ------------------------------------------------------------
    # @note We copy cache installed content content to off-tree
    #    directory for future use (these binutils will be used by
    #    final-GCC nano build that is run with --with-sysroot
    #    pointing to the off-tree location)
    # ------------------------------------------------------------
    target_files = {        
        pathlib.Path('*') : '',
    }

    cleanup = [
        pathlib.Path('lib'),
    ]

# =============================================================== GCC ============================================================== #
    
class GccCommon(Common, GccDescription):

    config = [

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
        
    ]

class GccBase(GccCommon):

    name = 'gcc_base'

    # Build only the compiler
    full_build = False
    # Skip doc for now (will be built in the Newlib stage)
    without_doc = True

    config = GccCommon.config + [

        # Basic options
        "--enable-languages=c",         # -----------------------------------------------------
        "--with-newlib",        # <---- # For great explenation of these two options 
        "--without-headers",    # <---- # @see https://www.ryanstan.com/withoutHeaders.html
                                        # -----------------------------------------------------
        
    ]

    cleanup = [

        pathlib.Path('bin') / f'{target}-gccbug',
        pathlib.Path('lib') / 'libiberty.a',
        pathlib.Path('include'),

    ]

class GccFinal(GccCommon):

    """
    This stage run builds whole GCC linking against the standard variant of the
    `newlib` library. Build results are installed directly in the package folder.

    Note
    ----
    This version of the libraries is compiled with -O2
    """

    name = 'gcc_newlib'

    config = GccCommon.config + [
            
        # Final options
        "--enable-languages=c,c++",
        "--enable-plugins",
        "--with-newlib",
        "--with-headers=yes",

    ]

    env = {

        # ----------------------------------------------------------------------
        # @note [INHIBIT_LIBC_CFLAGS] variable is set to disable transactional 
        #     memory related code in crtbegin.o. This is a workaround. Better
        #     approach is have a t-* to set this flag via CRTSTUFF_T_CFLAGS
        # ----------------------------------------------------------------------
        "INHIBIT_LIBC_CFLAGS" : "-DUSE_TM_CLONE_REGISTRY=0",

    }

    cleanup = [

        pathlib.Path('bin') / f'{target}-gccbug',
        pathlib.Path('lib') / 'libiberty.a',
        pathlib.Path('include'),
        
        pathlib.Path(target) / 'lib' / '**' / 'libiberty.a',
        pathlib.Path(target) / 'usr',

    ]

    class Libc(Common, NewlibDescription):

        config = [
            "--enable-newlib-io-long-long",
            "--enable-newlib-io-c99-formats",
            "--enable-newlib-reent-check-verify",
            "--enable-newlib-register-fini",
            "--enable-newlib-retargetable-locking",
            "--disable-newlib-supplied-syscalls",
            "--disable-nls",
        ]

        cflags_for_target = [
            "-ffunction-sections",
            "-fdata-sections",
            "-O2",    
        ]

        env = {

            "_" : {

                "CFLAGS_FOR_TARGET" : ' '.join(cflags_for_target),

            },

            'Debug' : {

                "CFLAGS_FOR_TARGET" : ' '.join(
                    cflags_for_target + [
                        "-g"
                    ]
                )
                
            }

        }

class GccFinalNano(GccCommon):

    """
    This stage run builds whole GCC linking against `newlib-nano`library 
    which is installed off-the-tree (not in the package folder directly).
    Instead, the resulting files (for boht compiler and the library) are
    copied to the off-tree location and then selectively copied to the
    package folder. 

    Main results of this stage are:

        - minimized version of the `newlib` library (newlib-nano)
        - minimized version of the `libstdc++` library
        - minimized version of the `libgcc` library (as well as `libgloss`, etc.)
        - startup files (e.g. crt0) and GCC spec files
        - GCC spec files for the `newlib-nano` library

    Note
    ----
    This version of the libraries is compiled with -Os
    """

    name = 'gcc_newlib_nano'

    # Skip doc (built in the Newlib stage)
    without_doc = True

    config = GccCommon.config + [

        # Final options
        "--enable-languages=c,c++",
        "--disable-libstdcxx-verbose",
        "--with-newlib",
        "--with-headers=yes",

    ]

    env = {

        "CXXFLAGS_FOR_TARGET" : """
            -g
            -Os
            -ffunction-sections
            -fdata-sections
            -fno-exceptions
        """,

    }

    class Libc(Common, NewlibDescription):
        
        """
        In this script (which is functionally improved equivalent of the 
        original ARM bash building scripts wrt resulting toolchain) the 'libc'
        build step is used to build "Classic Newlib" library targetting bigger
        cores (Cortex-A), while 'libc_aux' step builds so called "Newlib Nano".
        Important note here is that both libraries **are compiled from the
        source code base** and differ only in terms of options options passed
        to Autotools during configuration. The "Newlib Nano" thing is in general
        a fancy name for the library variant introduced by ARM at some revision
        of their "ARM Embedded Toolchain".
        
        To versions of the library are accompanied by two dedicated spec files
        (nano.specs and nosys.specs in arm-none-eabi/lib) which guide gcc
        compiler in decision of:
        
            - which variant of C library should application be linked against
            (arm-none-eabi/lib/libc.a or arm-none-eabi/lib/libc_nano.a)
            - which variant of rdimon [1] library should application be linked 
            against (arm-none-eabi/lib/libc.a or arm-none-eabi/lib/libc_nano.a)
            - what should be search order of standard includes directories
            (nano version prepends search list with arm-none-eabi/include
            /newlib-nano folder)
    
        Newlib Nano version is build by the script in the external (wrt to the
        target --prefix directory) location. Resulting files are used by the
        'gcc_final_aux' step to build libstdc++ library in the 'nano' version.
        
        Note
        ----
        'rdimon' library implements ARM-defined semihosting mechanism
        for Cortex-M (see https://github.com/ARM-software/abi-aa/blob/main/
        semihosting/semihosting.rst). It is part of the 'libgloss' library
        (implementing platform-specific code)

        See
        ----
        https://mcuoneclipse.com/2023/01/28/which-embedded-gcc-standard-library-newlib-newlib-nano/
        https://community.arm.com/arm-community-blogs/b/embedded-blog/posts/shrink-your-mcu-code-size-with-gcc-arm-embedded-4-7

        Note
        ----
        This version of the library is compiled with -Os
        """

        name = 'newlib_nano'    

        # Skip doc (built in the Newlib stage)
        without_doc = True
        
        config = [
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
        ]

        cflags_for_target = [
            "-ffunction-sections",
            "-fdata-sections",
            "-Os",    
        ]

        env = {

            "_" : {

                "CFLAGS_FOR_TARGET" : ' '.join(cflags_for_target),

            },

            'Debug' : {

                "CFLAGS_FOR_TARGET" : ' '.join(
                    cflags_for_target + [
                        "-g"
                    ]
                )
                
            }

        }

        # We trigger the off-install-tree build but do not copy results, these will be copied by the 'GccNewlibNano' build
        target_files = { }

    # Here we copy results of both libc (newlib) and libgcc builds in the 'nano' version
    target_files = {
        
        # Multilibs
        pathlib.Path('{multilib_dir}/libstdc++.a')  : pathlib.Path('{multilib_dir}/libstdc++_nano.a'),
        pathlib.Path('{multilib_dir}/libsupc++.a')  : pathlib.Path('{multilib_dir}/libsupc++_nano.a'),
        pathlib.Path('{multilib_dir}/libc.a')       : pathlib.Path('{multilib_dir}/libc_nano.a'),
        pathlib.Path('{multilib_dir}/libg.a')       : pathlib.Path('{multilib_dir}/libg_nano.a'),
        pathlib.Path('{multilib_dir}/librdimon.a')  : pathlib.Path('{multilib_dir}/librdimon_nano.a'),
        pathlib.Path('{multilib_dir}/nano.specs')   : pathlib.Path('{multilib_dir}/'),
        pathlib.Path('{multilib_dir}/rdimon.specs') : pathlib.Path('{multilib_dir}/'),
        pathlib.Path('{multilib_dir}/nosys.specs')  : pathlib.Path('{multilib_dir}/'),
        pathlib.Path('{multilib_dir}/*crt0.o')      : pathlib.Path('{multilib_dir}/'),

        # LibC headers
        pathlib.Path(target) / 'include/newlib.h' : pathlib.Path(target) / 'include/newlib-nano/newlib.h',

    }

# =============================================================== GDB ============================================================== #

class Gdb(Common, GdbDescription):
            
    config = [

        "--disable-nls",
        "--disable-sim",
        "--disable-gas",
        "--disable-binutils",
        "--disable-ld",
        "--disable-gprof",
        "--with-lzma=no",
        
        f"--with-gdb-datadir={target}/share/gdb",
        
    ]
            
# ============================================================ Script ============================================================== #

class Description(ToolchainDescription):

    def __init__(self,
        conanfile         
    ):

        # Target of the toolchain
        self.target = target
        # Human-readable version of the toolchain
        self.pkg_version = f"GNU ARM Embedded Toolchain {conanfile.options.with_gcc_version}"

        # Dependencies to be installed
        self.dependencies = Dependencies()

        # Components to be built
        self.components = [

            # Binutils
            Binutils(conanfile),

            # GCC base
            GccBase(conanfile),
            # GCC = Newlib LiBC
            GccFinal(conanfile),
            # GCC = Newlib LiBC (nano)
            GccFinalNano(conanfile),

            # GDB
            Gdb(conanfile),
        ]

# ================================================================================================================================== #
