"""Adapt the pinned native game collection without modifying upstream checkouts."""
from pathlib import Path
import re, shutil, hashlib, json
from compress_levels import compress_literals
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
ROOT = Path(__file__).resolve().parents[1]
catalog=json.loads((ROOT/'tools/native_catalog.json').read_text())
manifest=[]

def replace_body(text,name,body):
    pat=re.compile(r'\b(?:void|Bool|u8|s32)\s+'+name+r'\s*\([^;{}]*\)\s*\{')
    for match in reversed(list(pat.finditer(text))):
        start=match.end(); end=start; depth=1
        while depth:
            if text[end]=='{':depth+=1
            if text[end]=='}':depth-=1
            end+=1
        text=text[:start]+'\n'+body+'\n'+text[end-1:]
    return text

for game in catalog:
    ident=game['id']; folder=game['folder']; group=game['group']
    if group in ('CRISP','POCKET','ORIGINAL','TINYEXTRA','GAMEBUINO'):
        game['sources']=[]
        continue
    source=ROOT/'upstream/PicoLibSDK/PicoPad'/group/folder
    dest=ROOT/'firmware/games'/ident
    dest.mkdir(parents=True,exist_ok=True)
    files=[p for p in source.rglob('*') if p.is_file() and p.suffix in ('.cpp','.c','.h') and p.name not in ('config.h','include.h') and 'snd' not in p.parts and 'VegaslotTab' not in p.parts]
    if ident=='pad_sokoban':
        files=[p for p in files if not p.name.startswith('levels_')]
    if ident=='pad_fifteen2':
        files=[p for p in files if 'img' not in p.relative_to(source).parts or p.name in ('digits.cpp','digitsimg.cpp','tiles.cpp','tilesimg.cpp')]
    wrappers=[]
    for src in files:
        rel=src.relative_to(source); target=dest/rel
        target.parent.mkdir(parents=True,exist_ok=True)
        text=src.read_text(encoding='utf-8-sig',errors='replace')
        text=re.sub(r'^\s*#include\s+"(?:../)?include.h".*$', '// Includes supplied by port wrapper',text,flags=re.M)
        if rel.as_posix()=='src/main.cpp':
            text,n=re.subn(r'\bint\s+main\s*\([^)]*\)', 'void run()',text)
            assert n==1,(ident,n)
            if ident=='amania':
                text=text.replace('BootIntro();', '// Launcher replaces the fake disk-loading sequence.')
            if ident=='arkanoid':
                text=text.replace('GROUPE VARIABLE;', 'GROUPE VARIABLE{};')
                text=text.replace('PLAYMUSIC();','// No speaker: skip opening melody.')
                text=text.replace('NEWGAME:;', 'NEWGAME:; console_set_rotated(false);')
                text=text.replace('RsVarNewGame(&VARIABLE);','RsVarNewGame(&VARIABLE); console_set_rotated(true);')
                text=text.replace('if (VARIABLE.Frame%8==0)', 'console_stats(VARIABLE.LEVEL,VARIABLE.live);\nif (VARIABLE.Frame%8==0)')
            if ident=='tpinball':
                text=text.replace('NEWGAME:', 'NEWGAME: console_set_rotated(false);')
                text=text.replace('FIRSTTIME=1;\ndelay(1000);', 'FIRSTTIME=1; console_set_rotated(true);\ndelay(1000);')
                text=text.replace('BallupDate(&ball);', 'console_stats(1,totalBall); BallupDate(&ball);')
            if ident=='pad_ants':
                text=re.sub(r'^.*case [45]: Game\(PLAYER_.*$', '',text,flags=re.M)
                text=text.replace('OpenSelInx = 5','OpenSelInx = 3').replace('OpenSelInx > 5','OpenSelInx > 3')
                text=text.replace('\n}\n\n// main function','\n\tDrawRect(240, HEIGHT-40, 80, 40, COL_BLACK);\n}\n\n// main function')
        if ident=='pad_ants' and rel.as_posix()=='src/game.cpp':
            text=re.sub(r'const sUsbPortPktHello UsbPktHello.*?// parameter foreground color','// USB multiplayer omitted for standalone console.\n// parameter foreground color',text,flags=re.S)
            for ret,name in re.findall(r'\b(void|Bool|u8)\s+(Usb\w+)\s*\([^;{}]*\)\s*\{',text):
                text=replace_body(text,name,'' if ret=='void' else 'return 0;')
        if ident=='pad_pictor' and rel.as_posix()=='src/gamemenu.cpp':
            text=re.sub(r'char HomePath\[.*?int HomePathLen;', '',text,flags=re.S)
            text=replace_body(text,'LoadTop',"memset(Top, ' ', sizeof(Top)); for (int i=0;i<TOP_NUM;i++) Top[i].score=0; return 0;")
            text=replace_body(text,'SaveTop','return False; // No SD card: scores remain in RAM only.')
        if ident in ('arkanoid','tpinball') and rel.as_posix()=='src/main.cpp':
            text=text.replace('color(0,0,31)', 'color(8,36,31)')
        if ident=='pad_pictor' and rel.as_posix()=='src/missile.cpp':
            text=re.sub(r'\b\w+Snd\s*,\s*count_of\(\w+Snd\)', 'nullptr, 0',text)
        if ident=='pad_fifteen2' and rel.as_posix()=='src/main.cpp':
            text=re.sub(r'^\s*\{ (?!DigitsImg).*?Img_Pal.*$', '',text,flags=re.M)
        if ident=='pad_sokoban' and rel.as_posix()=='src/levels.cpp':
            from generate_puzzles import level_definitions
            text=level_definitions(text)
        if ident=='pad_sokoban' and rel.name.startswith('levels_'):
            text=re.sub(r'(?:"[lLrRuUdD]+"\s*)+,', '"",',text)
            text=compress_literals(text)
        if ident=='pad_sokoban' and rel.as_posix()=='src/game.cpp':
            decoder='''
// Level strings use lossless LZSS in flash; expand only the current map.
static char decoded_level[8192];
static const char* decode_level(const char* s) {
 if((u8)*s!=1) return s;
 const u8* p=(const u8*)s+1; unsigned n=p[0]|(p[1]<<8); p+=2;
 if(n>=sizeof(decoded_level)) return "";
 unsigned o=0; while(o<n) { unsigned flags=*p++;
 for(int b=0;b<8 && o<n;++b) {
 if(flags&(1u<<b)) decoded_level[o++]=*p++;
 else { unsigned code=p[0]|(p[1]<<8);p+=2; unsigned d=code>>4;
 for(unsigned j=0;j<(code&15)+3 && o<n;++j) { decoded_level[o]=decoded_level[o-d];++o; }
 } } } decoded_level[o]=0; return decoded_level;
}
'''
            text=decoder+text
            text=text.replace('LevDef = Levels[Level*2];','LevDef = decode_level(Levels[Level*2]);')
        text=re.sub(r'\bwhile\s*\(\s*1\s*\)', 'while ((console_service(), true))',text)
        text=replace_body(text,'Sound','  WaitUs((255u-freq_)*2u*dur);')
        text=replace_body(text,'DigitalControl','  // Audio output is disconnected.')
        text=text.replace('return to_ms_since_boot(get_absolute_time());', 'console_service(); return to_ms_since_boot(get_absolute_time());')
        text='// PicoConsole board/input/layout/storage modifications, 2026-10-11. Original notices retained below.\n'+text
        target.write_text(text,encoding='utf-8')
        manifest.append({'game':ident,'upstream':src.relative_to(ROOT).as_posix(),
                         'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
                         'ported_sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
        if src.suffix in ('.cpp','.c'):
            name='port_'+rel.as_posix().replace('/','_').replace('.cpp','').replace('.c','')+'.cpp'
            (dest/name).write_text('#include "include.h"\nnamespace '+ident+' {\n#include "'+rel.as_posix()+'"\n}\n')
            wrappers.append('games/'+ident+'/'+name)
    inc=source.joinpath('include.h').read_text(errors='replace')
    inc=re.sub(r'^.*#include INCLUDES_H.*$','',inc,flags=re.M)
    includes='#pragma once\n#include "../../console.h"\n#define gpio_get game_gpio_get\nnamespace '+ident+' {\n'+inc+'\n}\n'
    (dest/'include.h').write_text(includes)
    license=source/'COPYING.txt'
    if license.exists():shutil.copyfile(license,dest/'COPYING.txt')
    game['sources']=wrappers

(ROOT/'firmware/games/port-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
registry='#pragma once\n'+'\n'.join('namespace '+g['id']+' { void run(); }' for g in catalog)
registry+='\nconstexpr int GAME_COUNT='+str(len(catalog))+';\n'
(ROOT/'firmware/games/registry.h').write_text(registry)
table='\n'.join('{'+json.dumps(g['title'])+', '+g['id']+'::run, '+str(int(g['group'] in ('TINYGAME','TINYEXTRA')))+', '+str(2 if g['id']=='pocket_3' else int(g['group'] in ('CRISP','ORIGINAL','TINYEXTRA','GAMEBUINO') or g['id'] in ('pocket_9','pocket_7','pocket_8','pocket_1','pocket_2','pocket_4','pocket_5')))+', '+str(g.get('rotate',0))+', "'+g['controls']+'"},' for g in catalog)
(ROOT/'firmware/games/registry.inc').write_text(table+'\n')
cmake='set(NATIVE_GAME_SOURCES\n'+'\n'.join('  '+p for g in catalog for p in g['sources'])+'\n)\n'
(ROOT/'firmware/games/sources.cmake').write_text(cmake)
print(f'Prepared {len(catalog)} native games; retained source notices/licences.')
