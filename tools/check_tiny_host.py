"""Headless native-game rendering/input checks. SPDX-License-Identifier: GPL-3.0-only

Uses the same prepared C games, core, input, bitmap and EEPROM runtime as firmware.
Requires a native desktop GCC; independent from the ARM firmware build toolchain.
Each game runs in its own process with a timeout, so faults cannot hide later games.
This does not test Pico timing, SPI, physical controls or the USB/menu integration.
"""
from pathlib import Path
import argparse,ctypes,hashlib,json,os,random,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--collection',choices=('tiny','gamebuino'),default='tiny');p.add_argument('--gcc');p.add_argument('--game',type=int);p.add_argument('--library');p.add_argument('--frames',type=int,default=3600);a=p.parse_args()
folder=a.collection;api=folder+'_';spec='tiny-games.json' if folder=='tiny' else 'gamebuino-games.json'
out=ROOT/'logs'/(folder+'-host');out.mkdir(parents=True,exist_ok=True)
if a.game is not None:
 sys.path.insert(0,str(ROOT/'tools/python-libs'));from PIL import Image
 dll=ctypes.CDLL(a.library)
 for n in ("select","input","update","render","game_title"):setattr(dll,"tiny_"+n,getattr(dll,api+n))
 dll.tiny_game_title.restype=ctypes.c_char_p
 fb=(ctypes.c_ushort*(320*240))();r=random.Random(2350400+a.game)
 dll.tiny_select(a.game);title=dll.tiny_game_title(a.game).decode();hashes=set();captures=[]
 for f in range(a.frames):
  # Attract, confirm, release, directional movement, held actions, then fuzz.
  if f<120:k=0
  elif f<150:k=16
  elif f<180:k=0
  elif f<660:k=[1,0,2,0,4,0,8,0,16,0,32,0][(f-180)//40]
  elif f%13==0:k=r.choice([0,1,2,4,8,16,32,17,20,24,33,36,40,64])
  dll.tiny_input(k);dll.tiny_update()
  if f%30==0 or f in (119,179,659,a.frames-1):
   dll.tiny_render(fb,320);pix=bytes(255 if fb[y*320+40+x] else 0 for y in range(240) for x in range(240));hashes.add(hashlib.sha256(pix).hexdigest())
   if f in (119,179,659,a.frames-1):
    name=f'{a.game:02d}-{f:04d}.png';Image.frombytes('L',(240,240),pix).resize((480,480),Image.Resampling.NEAREST).save(out/name);captures.append(name)
 assert len(hashes)>1,(title,'No changing game pixels')
 result=dict(index=a.game,title=title,result='passed',frames=a.frames,distinct_frame_hashes=len(hashes),captures=captures)
 (out/f'{a.game:02d}.json').write_text(json.dumps(result,indent=2)+'\n');print(title,'PASS',len(hashes));sys.exit(0)
assert a.gcc,'Pass --gcc /path/to/native/gcc'
library=out/('tiny-host.dll' if os.name=='nt' else 'tiny-host.so')
sources=[ROOT/'firmware'/folder/'runtime.c',ROOT/'firmware'/folder/'selection.c',*sorted((ROOT/'firmware'/folder/'core').glob('*.c')),*sorted((ROOT/'firmware'/folder/'games').glob('*.c'))]
cmd=[a.gcc,'-shared','-O1','-g','-std=c11','-I'+str(ROOT/'firmware'/folder/'core'),'-o',str(library),*[str(s) for s in sources],'-lm']
if os.name=='nt':cmd.insert(1,'-static-libgcc')
else:cmd.insert(1,'-fPIC')
with (out/'compile.log').open('w') as log:subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True)
games=json.loads((ROOT/'tools'/spec).read_text());checks=[]
for i,g in enumerate(games):
 subprocess.run([sys.executable,str(Path(__file__).resolve()),'--collection',folder,'--game',str(i),'--library',str(library),'--frames',str(a.frames)],cwd=ROOT,check=True,timeout=60)
 checks.append(json.loads((out/f'{i:02d}.json').read_text()))
report=dict(result='passed',scope='Desktop C input/rendering checks; hardware launch/return, timing and physical play remain pending.',checks=checks,source_sha256={s.relative_to(ROOT).as_posix():hashlib.sha256(s.read_bytes()).hexdigest() for s in sources})
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS',len(checks),'native games')
