# PicoConsole Super Pack

**318 native games** on a Raspberry Pi Pico 2 with the Waveshare Pico-LCD-1.3 (240×240 LCD, joystick and four buttons). No ROMs or SD card required.

The launcher has large, high-contrast text, seven game rows and hold-to-scroll navigation. Arkanoid and Pinball play upright with left/right controls. Press **Y** to return to the menu.

- [Game list and controls](docs/INSTALLED_GAMES.md)
- [Pack details, capacity and verification](docs/NATIVE_PACK.md)
- [Build the UF2](docs/BUILD.md)
- [Licence and asset review](docs/LICENSE_AUDIT.md)
- [Credits and component notices](THIRD_PARTY_NOTICES.md)

## Build

Install Python 3.10+, Git, CMake, Ninja and an ARM GNU `arm-none-eabi` toolchain (tested with 14.2.1). Then run:

```sh
python tools/build.py
```

The build initialises only the pinned dependencies it needs, installs pinned Python helper packages locally if missing, prepares the curated ports and creates `dist/pico_console.uf2`. It does not flash a device. Windows wrapper: `./tools/build.ps1`. Tool paths can be supplied explicitly; see the build guide.

To load manually, hold BOOTSEL while connecting the Pico 2, verify `INFO_UF2.TXT` identifies RP2350 and copy the UF2 to that drive.

## Sources and licences

The combined firmware and PicoConsole additions are GPLv3. Original MIT, BSD, Unlicense and GPL notices remain in force for their components. Dependencies are Git submodules pinned in `.gitmodules` and `dependencies.lock.json`; they are not edited by the port scripts.

The public build excludes imported Sokoban level sets, all Fifteen2 picture puzzles and four recreations with unclear asset provenance. Source notices and asset references were reviewed; this does not independently establish every upstream author's ownership or clear game-name trademarks. See the recorded review.

For each public binary release, run `tools/package_release.py` and upload its matching source bundle and notices alongside the UF2. A GitHub-generated repository ZIP omits submodule content and is not a substitute for that release bundle.

Audio and saved scores are not enabled. Some games retain small lettering in their original art. Earlier private source downloads, ROM folders, build outputs, local tools and old test logs are excluded from Git.
