"""Exercise final-image gameplay and orientations, saving display captures."""
from console_usb import Console
from pathlib import Path
import json,time,hashlib
root=Path(__file__).resolve().parents[1];out=root/'logs/final-play';out.mkdir(exist_ok=True)
games=json.loads((root/'tools/native_catalog.json').read_text());targets={'tinytris','arkanoid','amania','tmorpion','tpinball','pad_ants','pad_chess','pad_ghostrac','pad_pictor','pad_sokoban','pad_fifteen2','crisp_pakupaku','crisp_lrain'};wanted=[i for i,g in enumerate(games) if g['id'] in targets or g['group'] in ('POCKET','ORIGINAL')]
c=Console();r={'checks':[],'physical_gameplay_verified':False,'uf2_sha256':json.loads((root/'dist/build-manifest.json').read_text())['uf2_sha256']}
try:
 c.command('menu');time.sleep(.3)
 for i in wanted:
  g=games[i];print(i,g['title'],flush=True);c.command(f'launch {i}');time.sleep(.6)
  c.command('press A 200');time.sleep(.6)
  c.command('press A 120');time.sleep(.5)
  a=c.status();first=c.shot(out/(g['id']+'-play.png'))
  c.command('press LEFT 250');time.sleep(.4)
  c.command('press DOWN 160');time.sleep(.25)
  b=c.status();second=c.shot(out/(g['id']+'-move.png'))
  c.command('press Y 200');time.sleep(.3);returned=c.status();assert returned['mode']=='menu',(i,returned)
  if g['id'] in ('arkanoid','tpinball'):assert a['rotated']==1,a
  r['checks'].append({'index':i,'id':g['id'],'before':a,'after':b,'returned':returned,'frames_advanced':b['frames']>a['frames'],'pixels_changed':first!=second,'sha256':hashlib.sha256(second).hexdigest()})
  (out/'report.json').write_text(json.dumps(r,indent=2)+'\n')
 c.shot(out/'menu.png');r['result']='passed';print('PASS',len(wanted),flush=True)
except Exception as e:r['result']='failed';r['error']=str(e);raise
finally:
 (out/'report.json').write_text(json.dumps(r,indent=2)+'\n');c.close()
