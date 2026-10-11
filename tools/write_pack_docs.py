"""Generate current pack documentation. SPDX-License-Identifier: GPL-3.0-only"""
from pathlib import Path
import json,collections
root=Path(__file__).resolve().parents[1]
g=json.loads((root/'tools/native_catalog.json').read_text());m=json.loads((root/'dist/build-manifest.json').read_text())
counts=collections.Counter(x['group'] for x in g)
verification=[]
for name,label in [('final-smoke','launch/return'),('final-play','selected gameplay/orientation')]:
 p=root/'logs'/name/'report.json';r=json.loads(p.read_text()) if p.exists() else {}
 verification.append(f"Passed {len(r['checks'])} {label} checks." if r.get('result')=='passed' and r.get('uf2_sha256')==m['uf2_sha256'] else f'Current-image {label} checks are pending.')
controls={'pocket_3':'Joystick selects square, A toggles','pocket_7':'Left/right selects column, Down/A drops','pocket_8':'Pass-and-play: left/right selects, Down/A drops','pocket_9':'Joystick slides tiles','pocket_11':'Joystick turns','pocket_13':'Up/down starts and moves paddle','pocket_14':'Left/right starts and moves bottom paddle','pocket_6':'Up/down walks, left/right turns','pocket_1':'Joystick selects square, A places; CPU opponent','pocket_2':'Joystick selects square, A places; pass-and-play','pocket_4':'Joystick selects answer, A confirms','pocket_5':'Left/right moves, Down drops, A/Up rotates'}
lines=['# Installed games','',f'{len(g)} native games. Menu order below matches the device.','', '| Number | Game | Collection | Controls |','|---:|---|---|---|']
for i,x in enumerate(g,1):
 c=x['controls']
 if x['group']=='CRISP':c='A/B action; joystick directions/cursor; X secondary action'
 if x['group']=='POCKET':c=controls[x['id']]+'; B/X restarts'
 if x['group']=='ORIGINAL':c+='; X restarts'
 lines.append(f"| {i} | {x['title']} | {x['group']} | {c} |")
lines+=['','**Y returns to the menu in every game.** Two-player games share the device in turns. Full playthroughs have not been performed.','']
(root/'docs/INSTALLED_GAMES.md').write_text('\n'.join(lines))
(root/'docs/NATIVE_PACK.md').write_text(f'''# Curated native pack 0.3

**{len(g)} native games** for Pico 2 and Waveshare Pico-LCD-1.3, with no ROMs, microSD or speaker required.

Includes {counts['TINYGAME']} TinyJoypad games, {counts['GAME']} selected PicoPad games, {counts['CRISP']} Crisp games, {counts['POCKET']} Pocket Gamer games and {counts['ORIGINAL']} original PicoConsole games. See [all games and controls](INSTALLED_GAMES.md).

## Controls and visibility

- Menu: up/down selects, hold to scroll, left/right changes page, A or joystick press opens.
- **Y returns to the menu in every game.**
- Arkanoid: A/B launches; left/right moves the bottom paddle. Pinball: left/right operates bottom flippers; A/B launches.
- The menu has one compact header, seven rows, 16-pixel white names, bright selection and white/yellow hints.
- Crisp and original games use the whole square screen. Connect Four, Tic Tac Toe, Math and Tetramino have adapted full-screen layouts. 2048 has larger numbers. Some lettering baked into original game art remains small.
- The extra DISPLAY / BUTTONS diagnostic is not counted as a game.

## Capacity

Flash: **{m['binary_flash_bytes']:,} / 4,194,304 bytes ({m['binary_flash_bytes']/4194304*100:.2f}%)**, leaving **{4194304-m['binary_flash_bytes']:,} bytes**. UF2 container size is larger than the flash image. This curated pack leaves space for further reviewed additions; excluded material is not restored to fill bytes.

Static RAM: {m['ram']['static_ram_bytes']:,} bytes; shared game area: {m['ram']['shared_game_ram_bytes']:,} bytes; stack: {m['ram']['stack_reserved_bytes']:,} bytes; heap capacity before allocation: {m['ram']['heap_capacity_bytes']:,} bytes. Only one game runs at a time. Linker/ELF checks verify that overlapping game sections do not overlap core state.

## Changes and limitations

- All imported Sokoban puzzles are removed. 128 original deterministic puzzles replace them; their solutions are replay-verified during preparation.
- Fifteen2 contains its digits puzzle only. Four recreations with unclear asset provenance are excluded. Details: [licence and asset review](LICENSE_AUDIT.md).
- Added Minefield, Reversi, Memory Pairs and Simon with original procedural graphics, plus CPU/two-player Tic Tac Toe, Math Challenge, Tetramino and two-player Connect Four.
- Audio and persistent scores are disabled. Ants is local-only. Crisp's smaller collision grid retains its overflow fallback, but crowded games can slow down. SPI display speed limits frame rate.

## Build and publish

[Build instructions](BUILD.md). The build verifies pinned dependencies, regenerates ports, rejects excluded assets, validates RAM/flash layout and writes `dist/pico_console.uf2` plus `dist/build-manifest.json`. Normal system clock: 150 MHz.

Publish the matching source archive and notices produced by `tools/package_release.py` alongside the UF2. Licence texts are in `LICENSES/`; credits and modifications are in `THIRD_PARTY_NOTICES.md`. No GitHub repository has been created or pushed automatically.

## Verification

{' '.join(verification)} Reports are in `logs/final-smoke/report.json` and `logs/final-play/report.json`; each records the UF2 hash it tested. Captures are software-rendered display pixels, not LCD photographs. The earlier menu and joystick were physically confirmed by the user; full physical playthroughs and high-difficulty performance have not been verified.
''')
(root/'README.md').write_text(f'''# PicoConsole Super Pack

**{len(g)} native games** on a Raspberry Pi Pico 2 with the Waveshare Pico-LCD-1.3 (240×240 LCD, joystick and four buttons). No ROMs or SD card required.

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
''')
print('Updated documentation for',len(g),'games.')
