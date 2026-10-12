"""Generate current pack documentation. SPDX-License-Identifier: GPL-3.0-only"""
from pathlib import Path
import json,collections
root=Path(__file__).resolve().parents[1]
g=json.loads((root/'tools/native_catalog.json').read_text());m=json.loads((root/'dist/build-manifest.json').read_text())
counts=collections.Counter(x['group'] for x in g)
verification=[]
lp=root/'logs/library-host/report.json';lr=json.loads(lp.read_text()) if lp.exists() else {}
if lr.get('result')=='passed' and all(m['source_sha256'].get(k)==v for k,v in lr.get('source_sha256',{}).items()):
 verification.append('Passed desktop library navigation, save/reload, catalog migration, interrupted-save recovery and shared menu rendering checks. Pico flash persistence and button navigation remain pending.')
for collection in ('tiny','gamebuino'):
 p=root/'logs'/(collection+'-host')/'report.json';r=json.loads(p.read_text()) if p.exists() else {}
 same=r.get('result')=='passed' and all(m['source_sha256'].get(k)==v for k,v in r.get('source_sha256',{}).items())
 verification.append(f"Passed desktop input/rendering checks for {len(r['checks'])} {collection} additions (3,600 logical frames per game)." if same else f'{collection} desktop checks pending for these sources.')
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
(root/'docs/NATIVE_PACK.md').write_text(f'''# Curated native pack 0.6

**{len(g)} native games** for Pico 2 and Waveshare Pico-LCD-1.3, with no ROMs, microSD or speaker required.

Includes {counts['TINYGAME']} TinyJoypad games, {counts['GAME']} selected PicoPad games, {counts['CRISP']} Crisp games, {counts['POCKET']} Pocket Gamer games, {counts['ORIGINAL']} original PicoConsole games, {counts['TINYEXTRA']} additional TinyJoypad games and {counts['GAMEBUINO']} Gamebuino games. See [all games and controls](INSTALLED_GAMES.md).

## Controls and visibility

- Menu: up/down selects, hold to scroll, left/right changes page, A or joystick press opens.
- **B switches All / Favorites / Recent. X stars or unstars the selected game.** Favorites have a gold star. Recent keeps the last 20 distinct games, newest first; replaying a game moves it to the top. Each view remembers its navigation position while powered on. Empty views explain how to populate them.
- **Y in the menu jumps back to All.** Favorites and history are saved automatically in internal flash, including across restarts. Saves use two alternating checksummed records in the final 8 KB; an interrupted write can fall back to the previous record. Stable game IDs preserve entries when the catalog is reordered or extended. A full flash erase removes these lists; normal UF2 updates stop before the reserved sectors.
- **Y returns to the menu in every game.**
- Arkanoid: A/B launches; left/right moves the bottom paddle. Pinball: left/right operates bottom flippers; A/B launches.
- Each game row has a compressed, tinted background preview derived from a captured game screen. The full playfield keeps its original aspect ratio, accompanied by a foreground close-up; selected per-game frames and viewports avoid title screens and score-only crops. Previews fade toward the text and white names have a black outline. Left/right pages move five games. Favorites and Recent use the same previews.
- The menu has one compact header, five rows, 16-pixel white names, bright selection and white/yellow hints.
- Crisp and original games use the whole square screen. Connect Four, Tic Tac Toe, Math and Tetramino have adapted full-screen layouts. 2048 has larger numbers. Some lettering baked into original game art remains small.
- TinyJoypad Tetromino and Gamebuino Tetrino are rotated with matching controls for upright play. Number Place has an enlarged board and digits. New monochrome games use white pixels and high-contrast shading.
- The extra DISPLAY / BUTTONS diagnostic is not counted as a game.

## Capacity

Flash: **{m['binary_flash_bytes']:,} / 4,194,304 bytes ({m['binary_flash_bytes']/4194304*100:.2f}%)**, leaving **{4194304-m['binary_flash_bytes']:,} bytes**. UF2 container size is larger than the flash image. Only additions with reviewed compatible terms and working desktop checks are included.

The library profile reserves **8,192 bytes** of that remainder; **{4194304-8192-m['binary_flash_bytes']:,} bytes** remain available for firmware growth. The linker and UF2 payload checks enforce this boundary.

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
# README.md is hand-maintained; builds regenerate reference docs only.
print('Updated documentation for',len(g),'games.')
