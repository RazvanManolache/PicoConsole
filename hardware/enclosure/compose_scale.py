"""Combine the two dimensioned scale renders for the README. GPL-3.0-or-later."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parents[1]/'tools/python-libs'))
from PIL import Image, ImageDraw, ImageFont

def font(size,bold=False):
 candidates=[('C:/Windows/Fonts/arialbd.ttf' if bold else 'C:/Windows/Fonts/arial.ttf'),
             ('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')]
 for candidate in candidates:
  try:return ImageFont.truetype(candidate,size)
  except OSError:pass
 return ImageFont.load_default(size=size)

views=[]
for name in ['everyday-scale.png','depth-scale.png']:
 with Image.open(ROOT/'preview'/name) as im:
  views.append(im.convert('RGB').resize((1500,round(im.height*1500/im.width)),Image.Resampling.LANCZOS))
a,b=views
canvas=Image.new('RGB',(1500,a.height+b.height+225),(28,36,48))
draw=ImageDraw.Draw(canvas)
draw.text((35,20),'A tiny console, with familiar company',font=font(32,True),fill='white')
draw.text((35,63),'Bank card, 1 euro coin and AA battery — shared physical scale',font=font(23),fill=(175,225,219))
canvas.paste(a,(0,105))
y=105+a.height
draw.text((35,y+15),'Depth: 22.8 mm body / 27.5 mm with joystick cap',font=font(29,True),fill='white')
canvas.paste(b,(0,y+65))
draw.text((35,canvas.height-38),'Exterior CAD render. Reference objects share scale. Prototype fit unverified.',font=font(21),fill=(210,221,232))
canvas.save(ROOT/'preview/size-and-depth.png')
print('Saved combined footprint and depth reference render.')
