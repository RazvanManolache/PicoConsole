"""Pack editable game-screen thumbnails for the five-row menu.
SPDX-License-Identifier: GPL-3.0-or-later
Normal builds use tracked PNG sources. --capture imports local software
captures once; no local test logs or unrelated upstream artwork are required
to build the release. PNGs retain the selected game's component terms.
"""
from pathlib import Path
import argparse,collections,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/python-libs'))
from PIL import Image,ImageOps,ImageChops,ImageFilter
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--capture',action='store_true');a=p.parse_args()
games=json.loads((ROOT/'tools/native_catalog.json').read_text());folder=ROOT/'assets/menu-previews';folder.mkdir(parents=True,exist_ok=True)
W,H=112,32
meta_path=folder/'provenance.json';meta=json.loads(meta_path.read_text()) if meta_path.exists() else {}
def rle(data):
 out=bytearray();i=0
 def run(at):
  n=1
  while at+n<len(data) and n<130 and data[at+n]==data[at]:n+=1
  return n
 while i<len(data):
  n=run(i)
  if n>=3:out.extend((128+n-3,data[i]));i+=n
  else:
   start=i;i+=n
   while i<len(data) and i-start<128 and run(i)<3:i+=min(run(i),128-(i-start))
   out.append(i-start-1);out.extend(data[start:i])
 return bytes(out)
def unpack(data):
 if data[0]==0:return data[1:]
 out=bytearray();i=1
 while i<len(data):
  n=data[i];i+=1
  if n&128:out.extend([data[i]]*((n&127)+3));i+=1
  else:out.extend(data[i:i+n+1]);i+=n+1
 return bytes(out)
framing=json.loads((ROOT/'tools/preview-framing.json').read_text())
assert set(framing)<={g['id'] for g in games}

def foreground(im):
 colors=collections.Counter(im.resize((56,56)).get_flattened_data())
 # Bucket similar floor/background shades together before choosing a backdrop.
 buckets=collections.Counter()
 for c,n in colors.items():buckets[tuple(v//16 for v in c)]+=n
 bucket=buckets.most_common(1)[0][0];bg=tuple(v*16+8 for v in bucket)
 channels=ImageChops.difference(im,Image.new('RGB',im.size,bg)).split()
 # Max-channel contrast preserves blue/purple pieces that luminance loses.
 diff=ImageChops.lighter(ImageChops.lighter(channels[0],channels[1]),channels[2])
 return ImageOps.autocontrast(diff),colors

def frame_art(im,focus=None,mode=None):
 # Preserve the ENTIRE field on the right; never discard a board to fit a strip.
 gray,colors=foreground(im)
 if mode=='saturated':
  # Textured gray floors must not overwhelm colored walls, boxes and actors.
  gray=Image.new('L',im.size)
  gray.putdata([255 if max(c)-min(c)>=60 else 0 for c in im.get_flattened_data()])
 thumb=Image.new('1',(W,H))
 whole=ImageOps.contain(gray,(64,30),Image.Resampling.LANCZOS)
 whole=whole.point(lambda p:255 if p>=72 else 0).convert('1')
 thumb.paste(whole,(W-whole.width,(H-whole.height)//2))
 # A separate close-up adds legible foreground detail without losing context.
 mask=gray.point(lambda p:255 if p>=80 else 0)
 # Borders have long straight runs; remove those from the focus score.
 reduced=mask.resize((64,64),Image.Resampling.NEAREST);px=reduced.load()
 for y in range(64):
  if sum(bool(px[x,y]) for x in range(64))>52:
   for x in range(64):px[x,y]=0
 for x in range(64):
  if sum(bool(px[x,y]) for y in range(64))>52:
   for y in range(64):px[x,y]=0
 # Score broad connected detail, not the densest individual text line.
 blur=reduced.filter(ImageFilter.GaussianBlur(5));best=(-1,32,32)
 for y in range(12,58,3):
  for x in range(6,59,3):
   score=blur.getpixel((x,y))*(.8+.2*y/64)
   if score>best[0]:best=(score,x,y)
 _,cx,cy=best
 if focus:cx,cy=focus[0]*64/im.width,focus[1]*64/im.height
 cw=min(im.width,round(im.height*.85));ch=max(1,round(cw*32/44))
 x=max(0,min(im.width-cw,round(cx*im.width/64-cw/2)))
 y=max(0,min(im.height-ch,round(cy*im.height/64-ch/2)))
 detail=gray.crop((x,y,x+cw,y+ch)).resize((44,32),Image.Resampling.LANCZOS)
 thumb.paste(detail.point(lambda p:255 if p>=88 else 0).convert('1'),(0,0))
 return thumb,colors,[x,y,x+cw,y+ch]

if a.capture:
 for index,g in enumerate(games):
  group=g['group'];local=[x for x in games if x['group']==group].index(g)
  rule=framing.get(g['id'],{})
  if group in ('TINYGAME','GAME') and (ROOT/'logs/preview-native'/(g['id']+'-14.png')).exists():
   src=ROOT/'logs/preview-native'/(g['id']+'-'+rule.get('frame','14')+'.png')
  elif group in ('TINYEXTRA','GAMEBUINO') and (ROOT/'logs/preview-extra'/(g['id']+'-0449.png')).exists():
   src=ROOT/'logs/preview-extra'/(g['id']+'-'+rule.get('frame','0449')+'.png')
  elif group in ('TINYEXTRA','GAMEBUINO'):
   collection='tiny' if group=='TINYEXTRA' else 'gamebuino'
   src=ROOT/'logs'/(collection+'-host')/f'{local:02d}-0179.png'
  else:
   candidates=[ROOT/'logs'/d/(g['id']+'-play.png') for d in ('final-play','expanded-smoke','native-smoke')]
   src=next(x for x in candidates if x.is_file())
  if src.parent.name=='preview-native' and len(Image.open(src).convert('RGB').getcolors(2) or [])==1:
   src=next(ROOT/'logs'/d/(g['id']+'-play.png') for d in ('final-play','expanded-smoke','native-smoke') if (ROOT/'logs'/d/(g['id']+'-play.png')).exists())
  # Replacement Sokoban levels and numeric Fifteen2 MUST use curated 0.3 captures.
  if g['id'] in ('pad_sokoban','pad_fifteen2'):
   assert src.parent.name in ('final-play','preview-native')
  im=Image.open(src).convert('RGB')
  host=src.parent.name=='preview-native'
  if not host:im=im.resize((240,240),Image.Resampling.NEAREST)
  viewport=rule.get('viewport')
  if viewport is None:
   if host:viewport=(0,0,im.width,im.height)
   elif group=='TINYGAME':viewport=(0,54,240,174)
   elif group=='GAME':viewport=(0,22,240,202)
   elif group=='CRISP':viewport=(0,20,240,240)
   elif group=='TINYEXTRA':viewport=(0,34,240,204) if g['function'] in ('gameAttinyTetromino','gameNumberPlace') else (0,54,240,174)
   elif group=='GAMEBUINO':viewport=(65,18,175,222) if g['function']=='gameTetrino' else (0,60,240,185)
   else:viewport=(0,0,240,240)
  im=im.crop(viewport);thumb,colors,detail=frame_art(im,rule.get('focus'),rule.get('mode'))
  path=folder/(g['id']+'.png');thumb.save(path)
  colorful=[(n,c) for c,n in colors.items() if max(c)-min(c)>45 and max(c)>80]
  tint=max(colorful)[1] if colorful else (64,180,220)
  meta[g['id']]={'capture':src.relative_to(ROOT).as_posix(),'capture_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'viewport':viewport,'detail_crop':detail,'framing':'Whole playfield at original aspect ratio plus supplementary foreground close-up','group':group,'component_terms':'Same terms and notices as this curated game; see LICENSES and THIRD_PARTY_NOTICES.md','tint':tint,'png_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
  if host:
   source_files=sorted(p for p in (ROOT/'firmware/games'/g['id']).rglob('*') if p.is_file())
   meta[g['id']]['game_source_sha256']=hashlib.sha256(b''.join(p.relative_to(ROOT).as_posix().encode()+b'\0'+p.read_bytes().replace(b'\r\n',b'\n') for p in source_files)).hexdigest()
 meta_path.write_text(json.dumps(meta,indent=2)+'\n')
assert set(meta)=={g['id'] for g in games}
assert {x.stem for x in folder.glob('*.png')}==set(meta)
payload=bytearray();offsets=[0];tints=[]
for g in games:
 path=folder/(g['id']+'.png');im=Image.open(path)
 assert im.size==(W,H) and im.mode=='1',path
 assert hashlib.sha256(path.read_bytes()).hexdigest()==meta[g['id']]['png_sha256'],path
 raw=im.tobytes();packed=rle(raw);block=bytes([1])+packed if len(packed)<len(raw) else bytes([0])+raw
 assert unpack(block)==raw
 payload.extend(block);offsets.append(len(payload))
 r,gc,b=meta[g['id']]['tint'];tints.append(((r>>3)<<11)|((gc>>2)<<5)|(b>>3))
text='// Generated from editable PNG thumbnails by prepare_previews.py.\n'
text+='static const uint32_t preview_offsets[]={'+','.join(map(str,offsets))+'};\n'
text+='static const uint16_t preview_tints[]={'+','.join(map(str,tints))+'};\n'
text+='static const uint8_t preview_data[]={\n'+''.join(','.join(str(b) for b in payload[i:i+32])+',\n' for i in range(0,len(payload),32))+'};\n'
dest=ROOT/'firmware/menu_previews.inc'
if not dest.exists() or dest.read_text()!=text:dest.write_text(text)
print(f'Packed {len(games)} previews: {len(payload):,} bitmap bytes + {len(offsets)*4+len(tints)*2:,} index/tint bytes.')
