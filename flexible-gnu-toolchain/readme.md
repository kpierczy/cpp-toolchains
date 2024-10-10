# About the package

Package mimics the old [`Arm GNU Toolchain`](https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads) (at the moment only `arm-none-eabi` component) dressing it up in the Conan package manager's clothes. Fine tunning of the toolchain may be done by modifying descriptors in the `data/` directory (or creating a new one). The package is designed to be flexible and extensible so feel free to contribute with your own target descriptors!

## About build strategy

Building the whole toolchain is not a short-term process. Moreover, the package has not been extensively tested on all platforms so all kinds of custom failures may
happen. Because of that, the package's internals split the process into fine-grained steps so that after the failure rebuilding the package may be resumed from the
last failed step (assuming the problem has been fixed). To make advantage of this feature I highly reccomend creating the package into two-stage manner using separate `conan build` and `conan export-pkg` commands. If the build fails on you platform, try to resolve the issue in the source code/descriptor file and rerun `conan build`. The pipeline should resume from the last failed step. If, for some reason, you need to rerun some of the successful steps, you may manually remove so called `tag files` (e.g. `.configured`, `.built`, `.installed`, etc.) residing in the per-stage build directory (e.g. `<conan-build-dir>/build/binutils/.configured`).

## About Windows support

At the moment, when built under Windows, the package assumes usage of the `msys2/cci.latest`'s `x86_64-pc-msys` compiler. After the build succeeds, required MSYS2 DLLs are copied into the package's `bin` directory which is provided to the package's consumer context. You can avoid manual specification of the compiler source by simply utilizing the bundled host profile `flexible-gnu-toolchain/windows`.
