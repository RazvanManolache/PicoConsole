"""Adapt the MIT-licensed native Crisp game collection for the shared console."""
from pathlib import Path
import re, json, shutil
# Preserve timestamps so unchanged ports do not rebuild.
_original_write_text=Path.write_text
def _stable_write(self, text, **kw):
    encoding=kw.get('encoding','utf-8')
    if self.exists() and self.read_text(encoding=encoding)==text:return len(text)
    return _original_write_text(self,text,**kw)
Path.write_text=_stable_write
def _stable_copy(src,dst):
    src,dst=Path(src),Path(dst)
    data=src.read_bytes()
    if not dst.exists() or dst.read_bytes()!=data:dst.write_bytes(data)
shutil.copyfile=_stable_copy
ROOT=Path(__file__).resolve().parents[1]
src=ROOT/'upstream/crisp-sdl/src'
dest=ROOT/'firmware/crisp'; dest.mkdir(exist_ok=True)
for group in ('lib','games'):
    (dest/group).mkdir(exist_ok=True)
    for p in (src/group).iterdir():
        if p.suffix in ('.c','.h'):
            text=p.read_text()
            if p.name=='cglp.h':text=text.replace('char title[100];','char title[24];')
            if p.name=='cglp.c':text=text.replace('100*sizeof(char)','sizeof(hiScores[i].title)').replace('#define GRID_CELL_CAPACITY 512','#define GRID_CELL_CAPACITY 4')
            (dest/group/p.name).write_text(text)
shutil.copyfile(ROOT/'upstream/crisp-sdl/LICENSE.txt',dest/'LICENSE.txt')
approved=re.findall(r'^\s*(addGame\w+)\(\);', (src/'lib/menuGameList.c').read_text(),re.M)
allgames={}
for p in sorted((src/'games').glob('*.c')):
    text=p.read_text(); names=re.findall(r'void\s+(addGame\w+)\s*\(',text)
    if not names:continue
    title=re.search(r'\btitle\s*=\s*"([^"]+)"',text)
    if title:allgames[names[0]]=(p,title[1])
path=ROOT/'tools/native_catalog.json'; catalog=json.loads(path.read_text())
catalog=[g for g in catalog if g['group']!='CRISP']
register='#include "cglp.h"\n'
for name in approved:register+='extern void '+name+'();\n'
register+='void addGames() {\n'+'\n'.join('  '+n+'();' for n in approved)+'\n}\n'
(dest/'lib/menuGameList.c').write_text(register)
# A small grid preserves exact collision behavior through upstream's overflow fallback.
p=dest/'lib/cglp.c'; text=p.read_text().replace('#define GRID_CELL_CAPACITY 512','#define GRID_CELL_CAPACITY 4');p.write_text(text)
wrappers=[]
for index,name in enumerate(approved,1):
    p,title=allgames[name]; ident='crisp_'+name[7:].lower()
    catalog.append(dict(id=ident,folder=p.name,group='CRISP',title=title.replace(chr(92)+'n',' ').upper(),rotate=0,controls='A ACTION / STICK CURSOR',crisp_index=index))
    wrappers.append('namespace '+ident+' { void run() { crisp_run('+str(index)+'); } }')
(dest/'entries.inc').write_text('\n'.join(wrappers)+'\n')
path.write_text(json.dumps(catalog,indent=2)+'\n')
(dest/'sources.cmake').write_text('file(GLOB CRISP_SOURCES "${CMAKE_CURRENT_LIST_DIR}/lib/*.c" "${CMAKE_CURRENT_LIST_DIR}/games/*.c")\n')
print(f'Prepared {len(approved)} extra native Crisp games, with joystick cursor controls.')
