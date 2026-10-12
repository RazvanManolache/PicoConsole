"""Capture native C game playfields after repeated title/menu confirmations.
SPDX-License-Identifier: GPL-3.0-or-later
Requires the DLLs from check_tiny_host.py, and writes local artwork inputs only.
"""
from pathlib import Path
import argparse,ctypes,json,os,subprocess,sys,shutil
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--collection',choices=('tiny','gamebuino'));p.add_argument('--game',type=int);p.add_argument('--dll-dir',help='Native compiler bin directory if DLL dependencies are not on PATH');a=p.parse_args()
sys.path.insert(0,str(ROOT/'tools/python-libs'));from PIL import Image
if a.game is None:
 for collection,spec in [('tiny','tiny-games.json'),('gamebuino','gamebuino-games.json')]:
  for i,g in enumerate(json.loads((ROOT/'tools'/spec).read_text())):
   print(g['id'],flush=True);subprocess.run([sys.executable,__file__,'--collection',collection,'--game',str(i),*(['--dll-dir',a.dll_dir] if a.dll_dir else [])],check=True,timeout=30)
 sys.exit()
collection=a.collection;out=ROOT/'logs/preview-extra';out.mkdir(exist_ok=True)
spec='tiny-games.json' if collection=='tiny' else 'gamebuino-games.json'
game=json.loads((ROOT/'tools'/spec).read_text())[a.game]
compiler=shutil.which('gcc')
if os.name=='nt' and (a.dll_dir or compiler):dll_path=os.add_dll_directory(a.dll_dir or str(Path(compiler).parent))
library=ROOT/'logs'/(collection+'-host')/(collection+'-host.dll')
if not library.exists():library=library.with_name('tiny-host.dll')
dll=ctypes.CDLL(str(library))
select=getattr(dll,collection+'_select');input=getattr(dll,collection+'_input');update=getattr(dll,collection+'_update');render=getattr(dll,collection+'_render')
fb=(ctypes.c_ushort*(320*240))();select(a.game)
for frame in range(1200):
 # Let title animations settle, confirm nested choices, then retain a stable scene.
 k=16 if 120<=frame<600 and frame%90<5 else 0
 if game['id']=='tj_snakegame85' and frame==150:k=8
 input(k);update()
 if frame in (179,209,239,299,449,599,749,899,1199) or 179<=frame<=449 and frame%15==14:
  render(fb,320);pix=bytes(255 if fb[y*320+40+x] else 0 for y in range(240) for x in range(240))
  Image.frombytes('L',(240,240),pix).save(out/(game['id']+f'-{frame:04d}.png'))
