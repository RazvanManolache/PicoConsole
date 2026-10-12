"""Enforce the curated asset boundary and record notices. GPL-3.0-only."""
from pathlib import Path
import argparse,json,hashlib,re,sys
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--prepared',action='store_true');a=p.parse_args()
games=json.loads((ROOT/'tools/native_catalog.json').read_text())
policy=json.loads((ROOT/'tools/asset-policy.json').read_text())
ids={g['id'] for g in games}
sys.path.insert(0,str(ROOT/'tools/python-libs'))
from PIL import Image
previews=ROOT/'assets/menu-previews';provenance=json.loads((previews/'provenance.json').read_text())
assert set(provenance)==ids
assert {p.name for p in previews.iterdir()}=={g+'.png' for g in ids}|{'provenance.json','README.md'},'Unreviewed menu artwork'
for g in games:
 path=previews/(g['id']+'.png');record=provenance[g['id']]
 assert record['group']==g['group']
 assert hashlib.sha256(path.read_bytes()).hexdigest()==record['png_sha256']
 with Image.open(path) as im:assert im.size==(112,32) and im.mode=='1'
 assert record['capture'].startswith(('logs/final-play/','logs/expanded-smoke/','logs/native-smoke/','logs/tiny-host/','logs/gamebuino-host/','logs/preview-native/','logs/preview-extra/'))
 if 'game_source_sha256' in record:
  source_files=sorted(p for p in (ROOT/'firmware/games'/g['id']).rglob('*') if p.is_file())
  digest=hashlib.sha256(b''.join(p.relative_to(ROOT).as_posix().encode()+b'\0'+p.read_bytes().replace(b'\r\n',b'\n') for p in source_files)).hexdigest()
  assert digest==record['game_source_sha256'],f'Preview source changed: {g["id"]}'
 if g['id'] in ('pad_sokoban','pad_fifteen2'):
  assert record['capture'].startswith('logs/preview-native/') and 'game_source_sha256' in record,'Replacement artwork must use the current curated game'
assert not ids.intersection(policy['excluded_games']), 'Excluded game returned to catalog'
files=list((ROOT/'firmware').rglob('*'))
for path in files:
 if not path.is_file():continue
 rel=path.relative_to(ROOT).as_posix()
 if rel.startswith('firmware/games/pad_sokoban/'):
  assert not path.name.startswith(('levels_','port_src_levels_')),f'Imported puzzle file: {rel}'
 if rel.startswith('firmware/games/pad_fifteen2/img/'):
  assert path.name in ('digits.cpp','tiles.cpp'),f'Unreviewed picture asset: {rel}'
 if rel.startswith('firmware/games/'):
  assert not any('/'+g+'/' in rel for g in policy['excluded_games']),f'Excluded file: {rel}'
 if path.suffix in ('.cpp','.c','.h','.inc'):
  text=path.read_text(errors='replace')
  assert not re.search(r'non[- ]commercial|CC[- ]BY[- ]NC|NoDerivs|author is notified',text,re.I),f'Restrictive notice: {rel}'
assert 'PicoConsole' in (ROOT/'firmware/games/pad_sokoban/src/levels.cpp').read_text()
assert 'CleanLevels' in (ROOT/'firmware/games/pad_sokoban/src/levels.cpp').read_text()
assert not re.search('GirlWithKitten|KittensInBox', (ROOT/'firmware/games/pad_fifteen2/src/main.cpp').read_text())
licenses=ROOT/'LICENSES'
for name in ('GPL-3.0.txt','LGPL-3.0.txt','Gamebuino-Tetrino-MIT.txt','TinyExtra-Obono.txt','TinyExtra-BullsAndCows.txt','TinyExtra-LaserPong.txt','TinyExtra-TinyDungeon.txt','TinyExtra-MeteorStorm.txt','Crisp-MIT.txt','Pico-SDK-BSD-3-Clause.txt','TinyUSB-MIT.txt','printf-MIT.txt','Apache-2.0.txt','Unlicense.txt','GCC-Runtime-Exception-3.1.txt','Newlib-NOTICES.txt'):
 assert (licenses/name).is_file(),f'Missing licence: {name}'
extra=json.loads((ROOT/'tools/tiny-games.json').read_text())
assert {p.name for p in (ROOT/'firmware/tiny/games').glob('*.c')}=={g['folder'] for g in extra},'Unreviewed extra game source'
assert all(g['licence'] in ('MIT','GPL-3.0','Unlicense') for g in extra)
gb=json.loads((ROOT/'tools/gamebuino-games.json').read_text())
assert {p.name for p in (ROOT/'firmware/gamebuino/games').glob('*.c')}=={g['folder'] for g in gb},'Unreviewed Gamebuino source'
assert all(g['licence'] in ('MIT','GPL-3.0','LGPL-3.0','Unlicense') for g in gb)
for record in json.loads((ROOT/'tools/gamebuino-licences.json').read_text()).values():
 assert 'error' not in record
 assert (licenses/record['file']).is_file()
groups={'TINYGAME':'GPL-3.0-or-later','GAME':'Unlicense (original PicoLibSDK content only)','CRISP':'MIT','POCKET':'GPL-3.0','ORIGINAL':'GPL-3.0-only','TINYEXTRA':'Per-game MIT, GPLv3 or Unlicense; see tools/tiny-games.json','GAMEBUINO':'Per-game MIT, GPLv3, LGPLv3 or Unlicense; see tools/gamebuino-games.json'}
report={'result':'passed','scope':'Reviewed source declarations, asset references and exclusions; not an independent ownership or trademark determination.',
 'dependencies':json.loads((ROOT/'dependencies.lock.json').read_text()),'policy':policy,
 'games':[dict(id=g['id'],title=g['title'],licence=groups[g['group']],asset_review='Original procedural graphics' if g['group']=='ORIGINAL' else 'Original replacement puzzles; upstream drawing assets' if g['id']=='pad_sokoban' else 'Digits only; all pictures removed' if g['id']=='pad_fifteen2' else 'Covered by the recorded upstream declaration; no contrary asset notice found') for g in games],
 'generated_source_hashes':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files if p.is_file()}}
for row,game in zip(report['games'],games):
 if game['group'] in ('TINYEXTRA','GAMEBUINO'):
  row.update(licence=game['licence'],author=game['author'],origin=game['origin'])
report['additional_exclusions']=json.loads((ROOT/'tools/extra-exclusions.json').read_text())
report['menu_previews']={'count':len(provenance),'terms':'Derivative artwork retains each curated game component licence and notices. Editable PNGs and provenance included in matching source archive.','source_hashes':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in previews.iterdir() if p.is_file()}}
(ROOT/'logs').mkdir(exist_ok=True);(ROOT/'logs/licence-audit.json').write_text(json.dumps(report,indent=2)+'\n')
lines=['# Licence and asset review','',report['scope'],'','The combined firmware is distributed under GPLv3. Original component licences and copyright notices remain in force. No claim is made that unrelated upstream files are relicensed.','', '## Excluded from the public build','']
for game,reason in policy['excluded_games'].items():lines.append(f'- `{game}`: {reason}')
lines+=['- Sokoban: all imported puzzle collections and original intro map omitted. 128 original puzzles and solutions replace them, with every solution replay-verified. This also excludes Thinking Rabbit, Yoshio Murase, Loma, Domenech, du Peloux and sets with custom unchanged-only terms.','- Fifteen2: all picture puzzles omitted; only the numeric puzzle is built.','- Audio assets, commercial ROMs, upstream UF2s, unrelated sample programs and local Python packages are excluded from release bundles.','- The unused IBM bitmap font was removed from the port. The drawing fonts are selected from PicoLibSDK under its author declaration.','', '## Retained components','', '| Component | Terms / evidence |','|---|---|','| TinyJoypad (20 games) | GPLv3-or-later notices in code and bitmap headers; Daniel C / TinyJoypad, original notices retained |','| PicoLibSDK selected games/drawing/fonts | Miroslav Nemecek, author Unlicense statement in LICENSES; third-party exceptions excluded as above |','| Pictor | Author additionally states the game and its parts may be reused for any purpose: https://www.breatharian.eu/hw/picolibsdk/index_en.html#pictor |','| Crisp (266 games) | ABA Games and portable backend contributors; MIT notice retained |','| Pocket Gamer (12 games) | Grgo Mariani; upstream GPLv3 text retained |','| PicoConsole originals / port changes | GPLv3; modification notices dated 2026-10-11 |','| Pico SDK / TinyUSB | BSD-3-Clause / MIT, plus source-specific notices, CMSIS Apache-2.0 and printf MIT |','| Waveshare LCD initialisation reference | Waveshare team; Pico_code repository root licence is GPLv3, compatible with this build |','| Compiler runtime / C library | GCC runtime exception and Newlib notices are included; compiler executables are not redistributed |','', '## Limits and release procedure','', 'Review relies on upstream authors\' declarations; it does not independently prove ownership of every sprite or clear game-name trademarks. The excluded recreations are conservative decisions, not findings that their authors infringed copyright. Submodule links alone do not discharge binary-source obligations: publish the matching self-contained source bundle generated by `tools/package_release.py` alongside each UF2. That bundle contains prepared, human-readable modified source and only required build dependencies; it does not copy all of PicoLibSDK.','', 'Dependency revisions: `dependencies.lock.json`. Per-file hashes and per-game review: `logs/licence-audit.json`.','']
lines+=['## Additional collections in 0.4','',f"{len(extra)} TinyJoypad additions and {len(gb)} Gamebuino additions are whitelisted by filename. Per-game authors, origins and terms are recorded in tools/tiny-games.json and tools/gamebuino-games.json. Original MIT, GPLv3, LGPLv3 and Unlicense texts/declarations are in LICENSES/TinyExtra-* and LICENSES/Gamebuino-*. Gamebuino API/fonts derive from Aurelien Rodot, LGPLv3-or-later; LGPL text and matching source are included.",'','The upstream collections contain other titles with missing, non-commercial, conflicting or incompatible declarations. They are not copied into the prepared firmware or release source archive. Built-in note tables may remain in source; separate audio files are omitted.','']
for name,reason in report['additional_exclusions'].items():lines.append(f'- {name}: {reason}')
lines+=['','## Menu artwork in 0.6','','Every catalog game has an editable monochrome PNG derived from its own rendered graphics. Per-game component terms and notices continue to apply. PNGs, provenance, selected viewports, and hashes are included in the matching source bundle. Artwork files are whitelisted against the catalog and checked for dimensions and identity. Sokoban and Fifteen2 previews are captured from the current curated replacement sources, with source hashes checked; no removed puzzle sets or picture assets are reintroduced.','']
(ROOT/'docs/LICENSE_AUDIT.md').write_text('\n'.join(lines))
print(f'Curated asset checks passed for {len(games)} games.')
