# Building and publishing

## Prerequisites

Python 3.10 or later, Git, CMake 3.20+, Ninja and an ARM GNU `arm-none-eabi` compiler. The verified toolchain is Arm GNU 14.2.Rel1 (GCC 14.2.1). Install tools separately or use existing portable installations; this project does not install compilers globally.

From a clone, run:

```sh
python tools/build.py
```

The build initialises the four Git submodules and only the Pico SDK's required TinyUSB submodule. It verifies revisions against `dependencies.lock.json`, rejects tracked changes inside dependencies, installs pinned helper packages into ignored `tools/python-libs` if needed, generates curated game copies and builds the UF2. It never flashes hardware.

Windows wrapper:

```powershell
./tools/build.ps1
```

If tools are not on PATH:

```sh
python tools/build.py --toolchain /path/to/arm-gnu/bin --cmake /path/to/cmake --ninja /path/to/ninja
```

On Windows, use Windows paths and quote paths containing spaces. `PICO_TOOLCHAIN_PATH`, `CMAKE_COMMAND` and `NINJA_COMMAND` are also supported. `--build-dir build-other` selects another output directory. `--offline` prevents dependency initialisation and package installation; dependencies and Python packages must already be present. The PowerShell equivalents are `-Toolchain`, `-CMake`, `-Ninja`, `-Python`, `-BuildDir` and `-Offline`.

Outputs: `dist/pico_console.uf2`, `dist/build-manifest.json`, generated game list and licence review. Prepared ports are ignored by Git and regenerated from tracked scripts and pinned submodules. Original code and licences in dependencies remain unchanged.

## Reloading

Hold BOOTSEL while plugging in the board. Verify `INFO_UF2.TXT` identifies **RP2350**, then copy `dist/pico_console.uf2` to its USB drive. The running console also accepts `python tools/console_usb.py boot` when its local pyserial dependency is available. Reloading resets the game in progress.

## Public binary release

```sh
python tools/package_release.py --build-dir build --ninja /path/to/ninja
```

Upload the resulting UF2, source ZIP, notices ZIP and release manifest from `dist/release/` together. The source ZIP contains prepared, human-readable modified game sources, build scripts, licence texts, dependency revision records and the SDK/TinyUSB source/header/configuration files required for this build. It omits unrelated upstream games, all imported Sokoban levels, picture puzzles, ROMs, unused vendor ports and compiler binaries.

Extract the source ZIP and run:

```sh
python tools/build.py --prepared
```

This path uses the included prepared sources and requires no Git checkout or source download. General-purpose compiler/build tools and pinned Python helper packages are still prerequisites; use `--offline` when those packages have already been installed locally. `release-source-files.json` hashes all bundled files before building, so changes to source-bundle content are detected.

GitHub's automatic source ZIP does **not** contain submodule source. Publish the generated source bundle alongside each binary and retain the matching release tag. Submodules identify exact revisions; they do not remove your responsibility to provide corresponding source. See the [GPL FAQ on matching source](https://www.gnu.org/licenses/gpl-faq.en.html#DistributeExtendedBinary).

The build normalises embedded project paths to support matching UF2 output from different checkout directories with the same toolchain. Rebuilding with another compiler may produce a different binary. Hardware tests record the UF2 hash they exercised and are separate from a successful build.

After rebuilding the extracted archive, record a successful byte-for-byte comparison by running the packager in the original checkout with `--verified-rebuild /path/to/extracted/dist/pico_console.uf2` and the same `--build-dir` and `--ninja` options. The packager refuses a mismatching UF2. Release 0.3 was checked this way with an offline, isolated source-archive build using GCC 14.2.1.
