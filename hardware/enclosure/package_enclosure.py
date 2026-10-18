"""Package verified enclosure geometry, editable sources and previews locally."""
from pathlib import Path
import json, zipfile, hashlib

root=Path(__file__).resolve().parent
report=json.loads((root/'mesh-validation.json').read_text())
assert hashlib.sha256((root/'picoconsole_pebble.scad').read_bytes()).hexdigest()==report['source_sha256'],'Source changed since validation'
assert len(report['parts'])==10
for name,info in report['parts'].items():
 data=(root/'print'/(name+'.stl')).read_bytes()
 assert hashlib.sha256(data).hexdigest()==info['sha256'],name+' changed since validation'
assert len(report['nominal_collision_checks'])==6
out=root.parents[1]/'dist'/'enclosure';out.mkdir(parents=True,exist_ok=True)
files=[root/name for name in ['README.md','LICENSE','picoconsole_pebble.scad','build_enclosure.py',
       'render_enclosure.py','render_scale.py','compose_scale.py','compare_enclosure.py','package_enclosure.py','dimensions.json','mesh-validation.json']]
files+=sorted((root/'print').glob('*.stl'))+sorted((root/'print').glob('*.3mf'))
files+=sorted(p for p in (root/'preview').rglob('*') if p.suffix in ('.png','.blend','.md','.json'))
assert len(list((root/'print').glob('*.3mf')))==2
assert (root/'preview'/'pebble-assembly.blend').exists()
entries=[(p,p.relative_to(root).as_posix()) for p in files]
repo=root.parents[1]
entries += [(p,'credits/LICENSES/'+p.relative_to(repo/'LICENSES').as_posix()) for p in sorted((repo/'LICENSES').rglob('*')) if p.is_file()]
entries += [(repo/'THIRD_PARTY_NOTICES.md','credits/THIRD_PARTY_NOTICES.md'),
            (repo/'docs/images/screenshots/README.md','credits/screenshots-README.md'),
            (repo/'docs/images/screenshots/provenance.json','credits/screenshots-provenance.json'),
            (repo/'assets/menu-previews/provenance.json','credits/menu-previews-provenance.json')]
manifest=''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+name+'\n' for p,name in entries)
target=out/'picoconsole-pebble-mini-v0.2.zip'
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p,name in entries:z.write(p,'picoconsole-pebble-mini-v0.2/'+name)
 z.writestr('picoconsole-pebble-mini-v0.2/SHA256SUMS.txt',manifest)
with zipfile.ZipFile(target) as z:assert z.testzip() is None
print(str(target));print(f'{target.stat().st_size:,} bytes; {len(entries)} files plus checksums; archive integrity passed')
