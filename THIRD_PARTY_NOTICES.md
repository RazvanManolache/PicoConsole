# Component notices and modifications

PicoConsole Super Pack 0.3 combines GPLv3 programs with GPL-compatible permissive components. The combined firmware is distributed under GNU GPL version 3; original component licences and notices are retained. This document does not relicense unrelated files in upstream repositories.

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
