# Curated native pack 0.5

**366 native games** for Pico 2 and Waveshare Pico-LCD-1.3, with no ROMs, microSD or speaker required.

Includes 20 TinyJoypad games, 16 selected PicoPad games, 266 Crisp games, 12 Pocket Gamer games 4 original PicoConsole games, 21 additional TinyJoypad games and 27 Gamebuino games. See [all games and controls](INSTALLED_GAMES.md).

## Controls and visibility

- Menu: up/down selects, hold to scroll, left/right changes page, A or joystick press opens.
- **B switches All / Favorites / Recent. X stars or unstars the selected game.** Favorites have a gold star. Recent keeps the last 20 distinct games, newest first; replaying a game moves it to the top. Each view remembers its navigation position while powered on. Empty views explain how to populate them.
- **Y in the menu jumps back to All.** Favorites and history are saved automatically in internal flash, including across restarts. Saves use two alternating checksummed records in the final 8 KB; an interrupted write can fall back to the previous record. Stable game IDs preserve entries when the catalog is reordered or extended. A full flash erase removes these lists; normal UF2 updates stop before the reserved sectors.
- **Y returns to the menu in every game.**
- Arkanoid: A/B launches; left/right moves the bottom paddle. Pinball: left/right operates bottom flippers; A/B launches.
- The menu has one compact header, seven rows, 16-pixel white names, bright selection and white/yellow hints.
- Crisp and original games use the whole square screen. Connect Four, Tic Tac Toe, Math and Tetramino have adapted full-screen layouts. 2048 has larger numbers. Some lettering baked into original game art remains small.
- TinyJoypad Tetromino and Gamebuino Tetrino are rotated with matching controls for upright play. Number Place has an enlarged board and digits. New monochrome games use white pixels and high-contrast shading.
- The extra DISPLAY / BUTTONS diagnostic is not counted as a game.

## Capacity

Flash: **4,080,724 / 4,194,304 bytes (97.29%)**, leaving **113,580 bytes**. UF2 container size is larger than the flash image. Only additions with reviewed compatible terms and working desktop checks are included.

The library profile reserves **8,192 bytes** of that remainder; **105,388 bytes** remain available for firmware growth. The linker and UF2 payload checks enforce this boundary.

Static RAM: 478,428 bytes; shared game area: 139,312 bytes; stack: 32,768 bytes; heap capacity before allocation: 13,092 bytes. Only one game runs at a time. Linker/ELF checks verify that overlapping game sections do not overlap core state.

## Changes and limitations

- All imported Sokoban puzzles are removed. 128 original deterministic puzzles replace them; their solutions are replay-verified during preparation.
- Fifteen2 contains its digits puzzle only. Four recreations with unclear asset provenance are excluded. Details: [licence and asset review](LICENSE_AUDIT.md).
- Added Minefield, Reversi, Memory Pairs and Simon with original procedural graphics, plus CPU/two-player Tic Tac Toe, Math Challenge, Tetramino and two-player Connect Four.
- Audio and persistent scores are disabled. Ants is local-only. Crisp's smaller collision grid retains its overflow fallback, but crowded games can slow down. SPI display speed limits frame rate.

## Build and publish

[Build instructions](BUILD.md). The build verifies pinned dependencies, regenerates ports, rejects excluded assets, validates RAM/flash layout and writes `dist/pico_console.uf2` plus `dist/build-manifest.json`. Normal system clock: 150 MHz.

Publish the matching source archive and notices produced by `tools/package_release.py` alongside the UF2. Licence texts are in `LICENSES/`; credits and modifications are in `THIRD_PARTY_NOTICES.md`. No GitHub repository has been created or pushed automatically.

## Verification

Passed desktop library navigation, save/reload, catalog migration, interrupted-save recovery and shared menu rendering checks. Pico flash persistence and button navigation remain pending. Passed desktop input/rendering checks for 21 tiny additions (3,600 logical frames per game). Passed desktop input/rendering checks for 27 gamebuino additions (3,600 logical frames per game). Current-image launch/return checks are pending. Current-image selected gameplay/orientation checks are pending. Reports are in `logs/final-smoke/report.json` and `logs/final-play/report.json`; each records the UF2 hash it tested. Captures are software-rendered display pixels, not LCD photographs. The earlier menu and joystick were physically confirmed by the user; full physical playthroughs and high-difficulty performance have not been verified.
