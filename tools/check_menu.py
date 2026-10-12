"""Check readable-menu navigation and leave the console at the first page."""
from console_usb import Console
from pathlib import Path
import json,time
root=Path(__file__).resolve().parents[1]
manifest=json.loads((root/'dist/build-manifest.json').read_text())
for name in ['final-smoke','final-play']:
    r=json.loads((root/'logs'/name/'report.json').read_text())
    assert r['result']=='passed' and r['checks']
    if name=='final-smoke':assert len(r['checks'])==manifest['game_count']
    assert r['uf2_sha256']==manifest['uf2_sha256']
c=Console()
try:
    c.command('launch 0');time.sleep(.15);c.command('menu');time.sleep(.25)
    c.command('press Y 100');time.sleep(.2) # Ensure All, regardless of remembered view.
    c.command('press DOWN 700');time.sleep(.85)
    held=c.status();assert held['mode']=='menu' and held['selected']>=2,held
    c.command('press RIGHT 100');time.sleep(.2)
    right=c.status();assert right['selected']==held['selected']+7,right
    c.command('press LEFT 100');time.sleep(.2)
    left=c.status();assert left['selected']==held['selected'],left
    c.command('launch 0');time.sleep(.15);c.command('menu');time.sleep(.25)
    c.command('press Y 100');time.sleep(.2)
    ready=c.status();assert ready['mode']=='menu' and ready['selected']==0,ready
    c.shot(root/'logs/final-play/menu.png')
    (root/'logs/menu-check.json').write_text(json.dumps(dict(result='passed',uf2_sha256=manifest['uf2_sha256'],hold=held,right=right,left=left,ready=ready),indent=2)+'\n')
    print(json.dumps(ready))
finally:c.close()
