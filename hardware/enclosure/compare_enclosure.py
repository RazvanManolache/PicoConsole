"""Compare orthographic STL renders at identical scale; requires Pillow."""
from pathlib import Path
import sys, zipfile, io, argparse
root=Path(__file__).resolve().parent
sys.path.insert(0,str(root.parents[1]/'tools/python-libs'))
from PIL import Image, ImageDraw, ImageFont
parser=argparse.ArgumentParser()
parser.add_argument('--previous',type=Path,default=root/'preview/reference/v0.1-controls.png',
                    help='Previous 110 mm orthographic render (PNG), or the original v0.1 ZIP')
args=parser.parse_args()
if args.previous.suffix.lower()=='.zip':
 with zipfile.ZipFile(args.previous) as z:
  old=Image.open(io.BytesIO(z.read('picoconsole-pebble-v0.1/preview/controls.png'))).convert('RGB')
else:
 old=Image.open(args.previous).convert('RGB')
new=Image.open(root/'preview/controls.png').convert('RGB')
assert old.size==new.size==(1500,1000)
# Both original renders use a 110 mm orthographic scale: equal pixels/mm.
canvas=Image.new('RGB',(1500,650),(28,36,48));draw=ImageDraw.Draw(canvas)
try:
 title=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',27)
 body=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',21)
except OSError:title=body=ImageFont.load_default()
for i,(img,heading,desc) in enumerate([(old,'Previous v0.1','88 x 46.2 mm; 25.8 mm deep'),(new,'Pebble Mini v0.2','64 x 34 mm; 22.8 mm deep')]):
 canvas.paste(img.resize((750,500),Image.Resampling.LANCZOS),(750*i,75))
 draw.text((750*i+375,25),heading,font=title,fill='white',anchor='mt')
 draw.text((750*i+375,588),desc,font=body,fill=(225,235,247),anchor='mt')
draw.text((750,625),'Same scale. Same electronics and display size.',font=body,fill=(130,224,207),anchor='mt')
canvas.save(root/'preview/size-comparison.png')
print('Saved same-scale comparison; neither design rescaled independently.')
