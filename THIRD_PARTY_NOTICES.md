# Component notices and modifications

PicoConsole Super Pack 0.6 combines GPLv3 programs with GPL-compatible permissive components. The combined firmware is distributed under GNU GPL version 3; original component licences and notices are retained. This document does not relicense unrelated files in upstream repositories.

| Component | Authors / source | Licence text |
|---|---|---|
| Launcher, board backends, build/port scripts, Minefield, Reversi, Memory Pairs, Simon, original Sokoban puzzles | PicoConsole contributors, 2026 | LICENSE / LICENSES/GPL-3.0.txt |
| TinyJoypad ports and bitmap resources (20 games) | Daniel C / TinyJoypad; original per-file notices retained; https://www.tinyjoypad.com | GPLv3-or-later, COPYING.txt in each prepared game |
| Selected PicoLibSDK games, drawing routines and fonts | Miroslav Nemecek, 2023-2025; https://github.com/Panda381/PicoLibSDK | LICENSES/Unlicense.txt and PicoLibSDK-licence-statement.txt; third-party exceptions excluded by asset-policy.json |
| Crisp Game Lib and portable SDL game collection | ABA Games (copyright 2022), joyrider3774 and portable-backend contributors; https://github.com/joyrider3774/crisp-game-lib-portable-sdl | LICENSES/Crisp-MIT.txt |
| Pocket Gamer (12 selected games) | Grgo Mariani; https://github.com/GrgoMariani/Raspberry-Pico-Pocket-Gamer | GPLv3, firmware/pocket/LICENSE in prepared source |
| Pico SDK | Raspberry Pi (Trading) Ltd. and source-specific contributors; https://github.com/raspberrypi/pico-sdk | LICENSES/Pico-SDK-BSD-3-Clause.txt; source-specific notices retained |
| TinyUSB | hathach (tinyusb.org), Raspberry Pi and source-specific contributors; https://github.com/hathach/tinyusb | LICENSES/TinyUSB-MIT.txt; source-specific notices retained |
| printf implementation | Marco Paland, copyright 2014 | LICENSES/printf-MIT.txt |
| CMSIS Cortex-M headers | Arm Limited; copyright notices retained in bundled headers | LICENSES/Apache-2.0.txt |
| LCD initialisation reference | Waveshare team; https://github.com/waveshare/Pico_code | GPLv3 (repository root licence); port source is GPLv3 |
| GCC runtime / libstdc++ | Free Software Foundation and contributors | GPLv3 with LICENSES/GCC-Runtime-Exception-3.1.txt; general-purpose compiler is not bundled |
| Newlib C library | Multiple authors including Red Hat, Berkeley, David M. Gay and Arm; see full notice list | LICENSES/Newlib-NOTICES.txt; no assertion that every entry is linked into this ARM build |

## PicoConsole modifications, 2026-10-11

- Shared launcher, USB diagnostics, cooperative return, Waveshare GPIO/SPI display and high-contrast menu.
- PicoLibSDK: namespace isolation, audio disabled, absent storage/multiplayer paths removed, upright Arkanoid/Pinball, brighter outlines, selected software renderers/fonts.
- Sokoban: every imported puzzle set and intro replaced by 128 original reverse-pull-generated puzzles with replay-verified solutions.
- Fifteen2: all pictures removed, digits puzzle retained. Eggs, Flappy, Pacman and Zoom excluded conservatively because asset permissions were not established.
- Crisp: Waveshare backend, virtual cursor/buttons, bounded high-score storage and smaller spatial collision grid with upstream fallback retained. Main game logic remains upstream.
- Pocket Gamer: shared-RAM integration, RGB565 conversion, controls and readable square-screen layouts, larger 2048 numbers, and signed full-column handling in Connect Four.
- New original games use procedural shapes/numbers and the credited PicoLibSDK drawing fonts; no imported sprites, sounds or puzzle sets.

Original author notices remain in prepared source. Credits are not endorsements. Game names may have separate trademark protection; no affiliation with original commercial game publishers is claimed. Detailed inclusion/exclusion decisions: docs/LICENSE_AUDIT.md. Exact source revisions: dependencies.lock.json.

For binary redistribution, include this document and LICENSES, and make the matching complete source bundle available alongside the UF2. Keep the UF2 and source release manifests together. Git submodule references identify origins but do not replace corresponding-source availability.

## Additional collections in 0.4

The selected TinyJoypad SDL ports are by joyrider3774 and the original authors listed per game in tools/tiny-games.json. The selected Gamebuino SDL ports are by joyrider3774 and the original authors in tools/gamebuino-games.json. Only whitelisted source files are prepared. Full mixed-licence upstream mirrors are excluded from release archives.

Tiny additions retain MIT notices for obono, datacute, Winston Lu and Lorandil, the Unlicense for Meteor Storm, and GPLv3 notices for Daniel C and other authors. Exact upstream notices are in LICENSES/TinyExtra-*.txt and prepared source.

Gamebuino games retain MIT, GPLv3, LGPLv3 and Unlicense notices in LICENSES/Gamebuino-*.txt and prepared source. The Gamebuino compatibility API and fonts derive from Aurelien Rodot (copyright 2014), LGPLv3-or-later; its declaration and full LGPL text accompany the source. Firebuino is LGPLv3. Tetrino includes MIT code by Laurens Rodriguez Oscanoa (2011/2013) and Joffrey Carlier (2014). Dark Tower is GPLv3-or-later by Marcus Hutchings (2018).

PicoConsole changes: standalone C backends replace SDL, RAM-only EEPROM, audio stubs, constant tables in flash, shared game RAM, square-screen scaling, white text, upright falling-block controls/rendering and enlarged Number Place digits. All modified files are marked with the modification date. Desktop checks do not replace Pico hardware validation.

## Menu previews in 0.6, 2026-10-12

Five taller menu rows include compressed monochrome derivatives of the curated
games' own rendered graphics. The editable PNG artwork and provenance are in
assets/menu-previews; the corresponding game component licences and notices
continue to apply. No separate cover art or excluded games/assets were imported.
PicoConsole framing, compression and menu-rendering changes are GPLv3-or-later.

## Launcher additions in 0.5, 2026-10-12

Original PicoConsole library navigation, Favorites and Recent views, stable game identifiers, checksummed alternating flash records, and shared menu renderer are GPLv3-or-later. The final 8 KB of flash is reserved for the launcher profile. Game score/EEPROM backends remain unchanged. Native checks simulate interrupted saves and render the same menu code; physical flash and controls require separate Pico validation.
