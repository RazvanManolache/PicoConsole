"""Render dimensioned everyday references beside the actual exterior STL scene.
Run with Blender 4.5 after render_enclosure.py. GPL-3.0-or-later.
"""
from pathlib import Path
import bpy, math, json
from mathutils import Vector

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'preview'
bpy.ops.wm.open_mainfile(filepath=str(OUT/'pebble-assembly.blend'))
scene=bpy.context.scene
scene.cycles.samples=64
scene.render.resolution_x=1800
scene.render.resolution_y=1000
scene.render.resolution_percentage=100
cam=scene.camera
bpy.data.objects['Studio floor'].location.z=-1

def material(name,color,metallic=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF')
 bs.inputs['Base Color'].default_value=(*color,1)
 bs.inputs['Metallic'].default_value=metallic
 bs.inputs['Roughness'].default_value=.36
 return m

cardmat=material('Reference card - plain purple',(.18,.13,.35))
ink=material('Reference lettering',(.95,.97,1))
ink_bs=ink.node_tree.nodes.get('Principled BSDF')
ink_bs.inputs['Emission Color'].default_value=(.95,.97,1,1)
ink_bs.inputs['Emission Strength'].default_value=.8
gold=material('Reference coin ring',(.64,.43,.12),.8)
silver=material('Reference coin centre',(.58,.62,.66),.8)
cellmat=material('Generic AA jacket',(.10,.13,.18),.25)
orange=material('Generic AA positive band',(.92,.36,.07))

def rounded(name,width,height,depth,radius,mat):
 outline=[]
 for x,y,a in [(width/2-radius,height/2-radius,0),(-width/2+radius,height/2-radius,90),
               (-width/2+radius,-height/2+radius,180),(width/2-radius,-height/2+radius,270)]:
  for i in range(17):
   angle=math.radians(a+i*90/16)
   outline.append((x+radius*math.cos(angle),y+radius*math.sin(angle)))
 n=len(outline)
 verts=[(x,y,z) for z in (0,depth) for x,y in outline]
 faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
 faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
 obj=bpy.data.objects.new(name,mesh);scene.collection.objects.link(obj);obj.data.materials.append(mat)
 return obj

def text(name,body,xyz,size,mat=ink,vertical=False,align='CENTER'):
 curve=bpy.data.curves.new(name,'FONT');curve.body=body;curve.size=size
 curve.align_x=align;curve.align_y='CENTER';curve.extrude=0
 obj=bpy.data.objects.new(name,curve);scene.collection.objects.link(obj)
 obj.location=xyz
 if vertical:obj.rotation_euler.x=math.pi/2
 obj.data.materials.append(mat)
 return obj

def cylinder(name,radius,depth,xyz,mat,axis_x=False):
 bpy.ops.mesh.primitive_cylinder_add(vertices=128,radius=radius,depth=depth,location=xyz)
 obj=bpy.context.object;obj.name=name
 if axis_x:obj.rotation_euler.y=math.pi/2
 obj.data.materials.append(mat)
 for face in obj.data.polygons:face.use_smooth=len(face.vertices)==4
 return obj

def line(name,a,b,r=.10):
 a,b=Vector(a),Vector(b)
 obj=cylinder(name,r,(b-a).length,(a+b)/2,ink)
 obj.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler()
 return obj

# A deliberately generic ID-1 card; no bank branding or payment credentials.
card=rounded('Bank card size reference',85.60,53.98,.76,3.18,cardmat)
card.location=(-72,13,0)
card_objects=[card,
 text('Card label','BANK CARD',(-72,30,.78),4.8),
 text('Card dimensions','85.6 x 53.98 mm',(-72,-1,.78),3.2)]
chip=rounded('Generic card chip',10,7,.03,1,gold);chip.location=(-100,13,.76);card_objects.append(chip)
for y in (15,12):
 card_objects.append(line('Chip line',(-104,y,.81),(-96,y,.81),.07))
for obj in card_objects:obj.location.x-=6

# Stylised coin: only the external dimensions reproduce the EUR 1 specification.
coin_objects=[cylinder('1 euro reference rim',23.25/2,2.33,(72,18,2.33/2),gold),
 cylinder('1 euro reference centre',8.2,.02,(72,18,2.34),silver),
 text('Coin label','1',(72,18,2.36),9,gold),
 text('Coin unit','EURO',(72,13.2,2.36),2.1,gold)]

def battery(x,y):
 # Published E91 maximum outer envelope: 50.5 mm overall, 14.5 mm diameter.
 return [cylinder('AA jacket',7.24,49.5,(x-.5,y,7.25),cellmat,True),
         cylinder('AA positive band',7.25,6,(x+21.20,y,7.25),orange,True),
         cylinder('AA positive terminal',2.75,1,(x+24.75,y,7.25),silver,True),
         text('AA label','AA 1.5 V',(x-2,y-7.27,7.25),4.6,vertical=True),
         text('AA polarity','+',(x+21,y-7.27,7.25),4,vertical=True)]

aa_objects=battery(14,-39)
overview_labels=[text('Console label','PEBBLE MINI / 64 x 34 mm',(0,-23,.04),3.3),
 text('Coin description','1 EURO / 23.25 mm',(72,-1,.04),2.7),
 text('AA description','AA BATTERY / 50.5 mm',(14,-52,.04),3.0)]

def aim(at):cam.rotation_euler=(Vector(at)-cam.location).to_track_quat('-Z','Y').to_euler()
def render(name):
 scene.render.filepath=str(OUT/name);bpy.ops.render.render(write_still=True)

cam.data.type='ORTHO';cam.data.ortho_scale=275
cam.location=(65,-145,235);aim((-20,0,5))
render('everyday-scale.png')

for obj in card_objects+coin_objects+overview_labels:obj.hide_render=True
for obj in aa_objects:obj.location.x+=61;obj.location.y+=39
scene.render.resolution_y=620
cam.location=(30,-240,12);cam.data.ortho_scale=200;aim((30,0,12))
bpy.data.objects['Studio floor'].hide_render=True
line('Shared baseline',(-64,-25,0),(126,-25,0),.08)

def dimension(x,height,label,align):
 y=-25
 line('Dimension shaft',(x,y,0),(x,y,height),.08)
 for z in (0,height):line('Dimension tick',(x-1.7,y,z),(x+1.7,y,z),.10)
 text('Dimension '+label,label,(x+(-2 if align=='RIGHT' else 2),y,height/2),3.1,
      vertical=True,align=align)

dimension(-39,22.8,'22.8', 'RIGHT')
dimension(-53,27.5,'27.5', 'RIGHT')
dimension(108,14.5,'14.5', 'LEFT')
text('Body label','PEBBLE MINI',(0,-25,35),3.7,vertical=True)
text('Battery label','AA BATTERY',(75,-25,25),3.7,vertical=True)
text('Shared floor caption','Shared baseline. Same scale. Dimensions in mm.',(30,-25,-12),3.1,vertical=True)
render('depth-scale.png')

# Reference models are generated by this script and are deliberately absent
# from the printable parts / print plates.
(OUT/'scale-dimensions.json').write_text(json.dumps({
 'projection':'orthographic; objects share one scene and scale within each view',
 'console_body_mm':[64,34,22.8], 'console_with_cap_mm':[64,34,27.5],
 'id1_card_mm':[85.6,53.98,.76], 'euro1_outer_mm':[23.25,2.33],
 'aa_max_outer_mm':[50.5,14.5], 'reference_shapes':'simplified, original generic models',
 'hardware_fit_verified':False},indent=2)+'\n')
print('Rendered exterior with everyday references at shared physical scale.')
