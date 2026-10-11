"""Give mutually exclusive games one shared RAM area and a 32KB call stack."""
from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
s=(root/'upstream/pico-sdk/src/rp2_common/pico_crt0/rp2350/memmap_default.ld').read_text()
s=s.replace('LENGTH = 512k','LENGTH = 480k\n    MAIN_STACK(rwx) : ORIGIN = 0x20078000, LENGTH = 32k')
games=json.loads((root/'tools/native_catalog.json').read_text())
over='    __game_ram_start = ALIGN(.,8);\n    OVERLAY __game_ram_start : {\n'
for g in games:
 pattern='*games/'+g['id']+'/*.obj' if g['group']!='CRISP' else '*crisp/games/'+g['folder']+'.obj'
 if g['group']=='POCKET':pattern='*pocket/*.obj'
 over+='        .ram_'+g['id']+' { '+pattern+'(.bss .bss.* COMMON) . = ALIGN(8); }\n'
over+='    } > RAM\n    __game_ram_end = .;\n\n'
s=s.replace('    .tbss (NOLOAD)',over+'    .tbss (NOLOAD)')
s=s.replace('    .tbss (NOLOAD)', '    .tbss __game_ram_end (NOLOAD)')
s=s.replace('    .bss (NOLOAD)', '    .bss __tls_end (NOLOAD)')
s=s.replace('    .heap (NOLOAD):', '    ASSERT(ADDR(.bss) >= __game_ram_end, "Game RAM overlaps core RAM")\n    .heap (NOLOAD):')
s=s.replace('} > SCRATCH_Y\n\n    .flash_end','} > MAIN_STACK\n\n    .flash_end')
s=s.replace('__StackTop = ORIGIN(SCRATCH_Y) + LENGTH(SCRATCH_Y);','__StackTop = ORIGIN(MAIN_STACK) + LENGTH(MAIN_STACK);')
p=root/'firmware/console_memmap.ld'
if not p.exists() or p.read_text()!=s:p.write_text(s)
