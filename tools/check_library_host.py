"""Check favorites/history, interrupted saves and actual menu rendering offline.
SPDX-License-Identifier: GPL-3.0-or-later
"""
from pathlib import Path
import argparse,hashlib,json,re,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--gxx',required=True);a=p.parse_args()
out=ROOT/'logs/library-host';out.mkdir(parents=True,exist_ok=True)
(out/'report.json').write_text(json.dumps(dict(result='running'))+'\n')
stub=out/'stubs'
def put(name,text):
 path=stub/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text)
put('hardware/flash.h','''#pragma once
#include <cstdint>
#include <cstddef>
#define FLASH_SECTOR_SIZE 4096
#define FLASH_PAGE_SIZE 256
void flash_range_erase(uint32_t,size_t);
void flash_range_program(uint32_t,const uint8_t*,size_t);
''')
put('hardware/regs/addressmap.h','''#pragma once
#include <cstdint>
extern uint8_t flash_image[4*1024*1024];
#define XIP_BASE reinterpret_cast<uintptr_t>(flash_image)
''')
put('pico/stdlib.h','#pragma once\n#define PICO_FLASH_SIZE_BYTES (4*1024*1024)\n#define PICO_OK 0\n')
put('pico/flash.h','#pragma once\n#include <cstdint>\nint flash_safe_execute(void (*)(void*),void*,uint32_t);\n')
fonts=(ROOT/'firmware/compat/fonts.cpp').read_text();data=re.search(r'FontCond6x8\[2048\][^=]*=\s*\{(.*?)\};',fonts,re.S)[1]
games=json.loads((ROOT/'tools/native_catalog.json').read_text())
keys=(ROOT/'firmware/games/menu_keys.inc').read_text()
put('catalog.h','static const uint32_t catalog_keys[]={\n'+keys+'};\nstatic const char* titles[]={'+','.join(json.dumps(g['title']) for g in games)+'};\nstatic const uint8_t font[]={'+data+'};\n')
sources=[ROOT/'firmware'/name for name in ('library.cpp','library_flash.cpp','library_screen.cpp')]
exe=out/'check-library.exe'
cmd=[a.gxx,'-std=c++17','-O1','-g','-Wall','-Wextra','-Wno-misleading-indentation','-static','-I'+str(stub),'-I'+str(ROOT/'firmware'),str(ROOT/'tools/check_library.cpp'),*[str(s) for s in sources],'-o',str(exe)]
subprocess.run(cmd,check=True,cwd=ROOT)
result=subprocess.check_output([str(exe),str(out)],text=True,cwd=ROOT,timeout=60);print(result,end='')
sys.path.insert(0,str(ROOT/'tools/python-libs'));from PIL import Image
for path in out.glob('*.rgb565'):
 raw=path.read_bytes();rgb=[]
 for i in range(0,len(raw),2):
  c=int.from_bytes(raw[i:i+2],'little');rgb.append((((c>>11)&31)*255//31,((c>>5)&63)*255//63,(c&31)*255//31))
 img=Image.new('RGB',(240,240));img.putdata(rgb);img.resize((480,480),Image.Resampling.NEAREST).save(path.with_suffix('.png'))
tracked=sources+[ROOT/'firmware'/n for n in ('library.h','library_flash.h','library_screen.h','console.cpp','games/menu_keys.inc','CMakeLists.txt','console_memmap.ld')]
report=dict(result='passed',scope='Desktop navigation, persistence, simulated interrupted flash writes and shared menu rendering; Pico flash, USB and physical controls pending.',summary=result.strip(),source_sha256={s.relative_to(ROOT).as_posix():hashlib.sha256(s.read_bytes()).hexdigest() for s in tracked})
report['test_source_sha256']={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in ('tools/check_library.cpp','tools/check_library_host.py')}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
