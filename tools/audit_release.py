"""Enforce the curated asset boundary and record notices. GPL-3.0-only."""
from pathlib import Path
import argparse,json,hashlib,re
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--prepared',action='store_true');a=p.parse_args()
games=json.loads((ROOT/'tools/native_catalog.json').read_text())
policy=json.loads((ROOT/'tools/asset-policy.json').read_text())
ids={g['id'] for g in games}
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
for name in ('GPL-3.0.txt','Crisp-MIT.txt','Pico-SDK-BSD-3-Clause.txt','TinyUSB-MIT.txt','printf-MIT.txt','Apache-2.0.txt','Unlicense.txt','GCC-Runtime-Exception-3.1.txt','Newlib-NOTICES.txt'):
 assert (licenses/name).is_file(),f'Missing licence: {name}'
groups={'TINYGAME':'GPL-3.0-or-later','GAME':'Unlicense (original PicoLibSDK content only)','CRISP':'MIT','POCKET':'GPL-3.0','ORIGINAL':'GPL-3.0-only'}
report={'result':'passed','scope':'Reviewed source declarations, asset references and exclusions; not an independent ownership or trademark determination.',
 'dependencies':json.loads((ROOT/'dependencies.lock.json').read_text()),'policy':policy,
 'games':[dict(id=g['id'],title=g['title'],licence=groups[g['group']],asset_review='Original procedural graphics' if g['group']=='ORIGINAL' else 'Original replacement puzzles; upstream drawing assets' if g['id']=='pad_sokoban' else 'Digits only; all pictures removed' if g['id']=='pad_fifteen2' else 'Covered by the recorded upstream declaration; no contrary asset notice found') for g in games],
 'generated_source_hashes':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files if p.is_file()}}
(ROOT/'logs').mkdir(exist_ok=True);(ROOT/'logs/licence-audit.json').write_text(json.dumps(report,indent=2)+'\n')
lines=['# Licence and asset review','',report['scope'],'','The combined firmware is distributed under GPLv3. Original component licences and copyright notices remain in force. No claim is made that unrelated upstream files are relicensed.','', '## Excluded from the public build','']
for game,reason in policy['excluded_games'].items():lines.append(f'- `{game}`: {reason}')
lines+=['- Sokoban: all imported puzzle collections and original intro map omitted. 128 original puzzles and solutions replace them, with every solution replay-verified. This also excludes Thinking Rabbit, Yoshio Murase, Loma, Domenech, du Peloux and sets with custom unchanged-only terms.','- Fifteen2: all picture puzzles omitted; only the numeric puzzle is built.','- Audio assets, commercial ROMs, upstream UF2s, unrelated sample programs and local Python packages are excluded from release bundles.','- The unused IBM bitmap font was removed from the port. The drawing fonts are selected from PicoLibSDK under its author declaration.','', '## Retained components','', '| Component | Terms / evidence |','|---|---|','| TinyJoypad (20 games) | GPLv3-or-later notices in code and bitmap headers; Daniel C / TinyJoypad, original notices retained |','| PicoLibSDK selected games/drawing/fonts | Miroslav Nemecek, author Unlicense statement in LICENSES; third-party exceptions excluded as above |','| Pictor | Author additionally states the game and its parts may be reused for any purpose: https://www.breatharian.eu/hw/picolibsdk/index_en.html#pictor |','| Crisp (266 games) | ABA Games and portable backend contributors; MIT notice retained |','| Pocket Gamer (12 games) | Grgo Mariani; upstream GPLv3 text retained |','| PicoConsole originals / port changes | GPLv3; modification notices dated 2026-10-11 |','| Pico SDK / TinyUSB | BSD-3-Clause / MIT, plus source-specific notices, CMSIS Apache-2.0 and printf MIT |','| Waveshare LCD initialisation reference | Waveshare team; Pico_code repository root licence is GPLv3, compatible with this build |','| Compiler runtime / C library | GCC runtime exception and Newlib notices are included; compiler executables are not redistributed |','', '## Limits and release procedure','', 'Review relies on upstream authors\' declarations; it does not independently prove ownership of every sprite or clear game-name trademarks. The excluded recreations are conservative decisions, not findings that their authors infringed copyright. Submodule links alone do not discharge binary-source obligations: publish the matching self-contained source bundle generated by `tools/package_release.py` alongside each UF2. That bundle contains prepared, human-readable modified source and only required build dependencies; it does not copy all of PicoLibSDK.','', 'Dependency revisions: `dependencies.lock.json`. Per-file hashes and per-game review: `logs/licence-audit.json`.','']
(ROOT/'docs/LICENSE_AUDIT.md').write_text('\n'.join(lines))
print(f'Curated asset checks passed for {len(games)} games.')
