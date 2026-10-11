import shutil
"""Reuse PicoLibSDK's software image renderers, retaining their source notices."""
from pathlib import Path
import re
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
base=ROOT/'upstream/PicoLibSDK'
dest=ROOT/'firmware/compat'; dest.mkdir(exist_ok=True)
for name in ('lib_mat2d.h','lib_draw.h'):
    text=(base/'_lib/inc'/name).read_text()
    (dest/name).write_text(text)
source=(base/'_lib/src/lib_draw.c').read_text()+'\n'+(base/'_lib/src/lib_mat2d.c').read_text()
functions={}
pat=re.compile(r'^(?:void|u8|u16|u32|int|float|Bool)\s+(\w+)\s*\([^;{}]*\)\s*\{',re.M)
for m in pat.finditer(source):
    pos=m.end(); depth=1
    while depth:
        if source[pos]=='{':depth+=1
        if source[pos]=='}':depth-=1
        pos+=1
    if m[1] not in functions:functions[m[1]]=source[m.start():pos]
names=set('Mat2D_PrepDrawImg SelFontUpdate SelFont8x8 SelFont8x14 SelFont8x16 SelFont6x8 SelFont5x8 DrawRect DrawFrame DrawClear DrawClearCol DrawPoint DrawText DrawText2 DrawTextW DrawTextBg DrawTextBg2 DrawImg DrawImgPal DrawImg4Pal DrawBlitPal DrawBlit4Pal DrawRectShadow DrawBlit1Shadow DrawImgRle DrawImg4Rle DrawImgPalDbl DrawTile4PalMap DrawImg4PalMat'.split())
changed=True
while changed:
    changed=False
    for name in tuple(names):
        for call in re.findall(r'\b(\w+)\s*\(',functions.get(name,'')):
            if call in functions and call not in names:names.add(call); changed=True
selected='\n\n'.join(functions[n] for n in sorted(names) if n in functions)
selected=re.sub(r'(void DrawText(?:2|W|Bg|Bg2)?\([^{}]*\)\s*\{)', r'\1\n if(col==COL_GRAY || col==COL_DKGRAY || col==COL_LTGRAY) col=COL_WHITE;', selected)
globals='''
const u8* pDrawFont=FontBold8x16;
int DrawFontHeight=16,DrawFontWidth=8;
u8 DrawPrintPosNum=40,DrawPrintRowNum=15,DrawPrintPos=0,DrawPrintRow=0,DrawPrintInv=0,DrawPrintSize=0;
COLTYPE DrawPrintCol=0xffff;
'''
(dest/'draw.cpp').write_text('// PicoConsole extraction and high-contrast text modifications, 2026-10-11.\n'+source[:source.index('#include')]+ '\n#include "../console.h"\n'+globals+selected+'\n')
fonts=[]
for fname in ('font_bold_8x8','font_bold_8x14','font_bold_8x16','font_cond_6x8','font_tiny_5x8'):
    text=(base/'_font'/f'{fname}.c').read_text(); text=text[text.index('const u8 Font'):]
    text=text.replace('const u8 Font','extern const u8 Font',1)
    fonts.append(text)
(dest/'fonts.cpp').write_text('// Fonts from Panda381/PicoLibSDK; Unlicense.\n#include "../console.h"\n'+'\n'.join(fonts))
print('Prepared original software draw routines and fonts.')
