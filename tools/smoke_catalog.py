"""Final-image catalog entry/exit check. Gameplay is checked separately."""
from console_usb import Console
from pathlib import Path
import json,time
root=Path(__file__).resolve().parents[1];out=root/'logs/final-smoke';out.mkdir(exist_ok=True)
games=json.loads((root/'tools/native_catalog.json').read_text());r={'checks':[],'physical_display_verified':False,'physical_buttons_verified':False,'uf2_sha256':json.loads((root/'dist/build-manifest.json').read_text())['uf2_sha256']}
# Wait for the ongoing BOOTSEL copy and USB enumeration.
c=None
for _ in range(90):
 try:c=Console();break
 except RuntimeError:time.sleep(1)
assert c,'Pico did not enumerate after flashing'
try:
 c.command('menu');time.sleep(.25)
 for i,g in enumerate(games):
  assert c.command(f'launch {i}').startswith('OK');time.sleep(.06)
  a=c.status();assert a['game']==i,(i,a)
  assert c.command('press Y 100').startswith('OK');time.sleep(.13)
  b=c.status()
  if b['mode']!='menu':
   c.command('press Y 500');time.sleep(.6);b=c.status()
  assert b['mode']=='menu',(i,b)
  r['checks'].append({'index':i,'id':g['id'],'launched':a,'returned':b});print(i,g['title'],flush=True)
  (out/'report.json').write_text(json.dumps(r,indent=2)+'\n')
 r['result']='passed';r['final']=c.status();print('PASS',len(games),flush=True)
except Exception as e:r['result']='failed';r['error']=str(e);raise
finally:
 (out/'report.json').write_text(json.dumps(r,indent=2)+'\n');c.close()
