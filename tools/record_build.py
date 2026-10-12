"""Record artifact identity and validate UF2 addressing/family after a build."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, struct, subprocess, os
ROOT=Path(__file__).resolve().parents[1]
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def rev(path):
    if not (path/'.git').exists():
        return next(d['commit'] for d in json.loads((ROOT/'dependencies.lock.json').read_text()).values() if ROOT/d['path']==path)
    return subprocess.check_output(['git','-C',str(path),'rev-parse','HEAD'],text=True).strip()
BUILD=Path(os.environ.get('PICOCONSOLE_BUILD_DIR',ROOT/'build'))
binary=BUILD/'pico_console.bin'
uf2=ROOT/'dist/pico_console.uf2'
blocks=uf2.read_bytes()
binary_data=binary.read_bytes()
assert (len(binary_data)+255)//256*256<=4194304-8192,'Firmware reaches the saved library sectors'
assert len(blocks)%512==0
count=len(blocks)//512
for i in range(count):
    block=blocks[i*512:(i+1)*512]
    a,b,flags,addr,size,index,total,family=struct.unpack('<8I',block[:32])
    assert (a,b,flags,size,index,total,family)==(0x0a324655,0x9e5d5157,0x2000,256,i,count,0xe48bff59)
    assert addr==0x10000000+i*256
    assert struct.unpack('<I',block[508:])[0]==0x0ab16f30
    expected=binary_data[i*256:(i+1)*256].ljust(256,b'\0')
    assert block[32:288]==expected
sources={str(p.relative_to(ROOT)).replace('\\','/'):sha(p)
         for folder in ('firmware','assets/menu-previews') for p in sorted((ROOT/folder).rglob('*')) if p.is_file()}
report={
    'recorded_utc':datetime.now(timezone.utc).isoformat(),
    'firmware':'native-0.6','board':'pico2','platform':'rp2350-arm-s',
    'system_clock_hz':150000000,'flash_limit_bytes':4194304,
    'binary_flash_bytes':binary.stat().st_size,'uf2_blocks':count,
    'library_profile_bytes':8192,'firmware_flash_limit_bytes':4194304-8192,
    'binary_sha256':sha(binary),'uf2_sha256':sha(uf2),
    'pico_sdk_commit':rev(ROOT/'upstream/pico-sdk'),
    'tinyusb_commit':rev(ROOT/'upstream/pico-sdk/lib/tinyusb'),
    'games_upstream_commit':rev(ROOT/'upstream/PicoLibSDK'),
    'crisp_upstream_commit':rev(ROOT/'upstream/crisp-sdl'),
    'pocket_upstream_commit':rev(ROOT/'upstream/pocket-gamer'),
    'game_count':len(json.loads((ROOT/'tools/native_catalog.json').read_text())),
    'compiler':subprocess.check_output(['arm-none-eabi-gcc','--version'],text=True).splitlines()[0],
    'source_sha256':sources,
}
import sys
sys.path.insert(0,str(ROOT/'tools/python-libs'))
from elftools.elf.elffile import ELFFile
with (BUILD/'pico_console.elf').open('rb') as f:
    elf=ELFFile(f); symbols=elf.get_section_by_name('.symtab')
    sym=lambda n:symbols.get_symbol_by_name(n)[0]['st_value']
    overlay=[s for s in elf.iter_sections() if s.name.startswith('.ram_') and s.name!='.ram_vector_table' and s['sh_size']]
    assert all(s['sh_type']=='SHT_NOBITS' and s['sh_addr']==sym('__game_ram_start') for s in overlay)
    assert max(s['sh_size'] for s in overlay)==sym('__game_ram_end')-sym('__game_ram_start')
    assert elf.get_section_by_name('.bss')['sh_addr']>=sym('__game_ram_end')
    assert sym('__end__')<sym('__HeapLimit')<=sym('__StackBottom')
    report['ram']={'static_ram_end':sym('__end__'),'static_ram_bytes':sym('__end__')-0x20000000,'shared_game_ram_bytes':sym('__game_ram_end')-sym('__game_ram_start'),'stack_reserved_bytes':sym('__StackTop')-sym('__StackBottom'),'heap_capacity_bytes':sym('__HeapLimit')-sym('__end__'),'note':'Overlay sections share addresses; arm-size BSS sums cannot represent physical RAM use.'}
(ROOT/'dist/build-manifest.json').write_text(json.dumps(report,indent=2)+'\n')
print('UF2 family/address/payload validated; dist/build-manifest.json saved.')
