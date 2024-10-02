# About the project

Aim of the repository is to provide plug-and-play C/C++ toolchains builders wrapped in a shell of the Conan package manager. The project
originates from the embedded C/C++ domain and as such its main focus was to provide analogous of the
[`Arm GNU Toolchain`](https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads) which is release quite irregularly. At the moment
the project provides the following packages:

- `flexible-gnu-toolchain`: driver package designed to produce all kinds of GCC-based toolchains given the Python-source configuration (so-caled
  `target descriptors`) files describing configuration of each toolchain's component. It has been based on the legacy ARM's build scripts
  and is expected to be extended with additional target descriptors over time. Currently only the `arm-none-eabi` target is supported
  but feel free to contribute with your own target descriptors!
