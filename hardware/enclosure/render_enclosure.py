"""Render the exported printable meshes with Blender 4.5 (run with blender -b --python)."""
import bpy, math, json
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'preview'; OUT.mkdir(exist_ok=True)
HEADER=json.loads((ROOT/'dimensions.json').read_text())['nominal_values_requiring_measurement']['header_gap_main_component_plane_to_lcd_underside']
LCD=6.4+HEADER;FACE=LCD+5.4;MAIN=4.8
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.render.engine='CYCLES'; scene.cycles.samples=40
scene.render.resolution_x=1500;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.world.color=(.22,.22,.22)
scene.view_settings.view_transform='AgX'

def material(name,rgb,rough=.36):
 m=bpy.data.materials.new(name);m.diffuse_color=(*rgb,1);m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*rgb,1);bs.inputs['Roughness'].default_value=rough
 return m
navy=material('Midnight blue front',(.035,.07,.14))
teal=material('Teal rear',(.025,.38,.34))
white=material('White paint in engraved labels',(.92,.97,1))
dark=material('Retainer',(.09,.10,.12))
green=material('A leaf green',(.29,.72,.20))
orange=material('B orange',(1,.38,.07))
blue=material('X sky blue',(.10,.43,.95))
pink=material('Y berry',(.86,.12,.31))
yellow=material('Joystick honey',(.95,.59,.08))
pcb=material('PCB',(.018,.19,.12));glass=material('LCD glass',(.006,.009,.014),.2)
metal=material('Connector steel',(.4,.45,.5),.23)

def stl(name,mat,location=(0,0,0),rotate=False,paint_depth=None):
 bpy.ops.wm.stl_import(filepath=str(ROOT/'print'/(name+'.stl')))
 o=bpy.context.object;o.name=name;o.data.materials.append(mat)
 if paint_depth is not None:
  o.data.materials.append(white)
  for p in o.data.polygons:
   if abs(p.center.z-paint_depth)<.005 and p.normal.z<-.99:p.material_index=1
 if rotate:o.rotation_euler.x=math.pi
 o.location=location
 return o

front=stl('front',navy,(0,0,FACE),True)
rear=stl('rear-marble',teal)
retainer=stl('button-retainer',dark,(23.1,0,LCD+1.6))
caps=[stl('button-'+name,mat,(21.9,(1.5-i)*5.7,FACE+.7),True,.42)
      for i,(name,mat) in enumerate(zip('ABXY',[green,orange,blue,pink]))]
joy=stl('joystick-2.10',yellow,(-19.3,0,LCD+5.1))

def box(name,center,size,mat):
 bpy.ops.mesh.primitive_cube_add(size=1,location=center)
 o=bpy.context.object;o.name=name;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 o.data.materials.append(mat);return o
lcd=box('LCD PCB - simplified envelope',(0,0,LCD-.8),(52,26.5,1.6),pcb)
gl=box('LCD glass - nominal',(1.8,0,LCD+1.8),(29.5,26.5,3.6),glass)
main=box('Marble PCB - simplified envelope',(0,0,MAIN-.8),(50.86,21,1.6),pcb)
usb=box('USB-C nominal keepout',(-24.0,0,MAIN+1.6),(7,9,3.2),metal)
sd=box('SD socket nominal keepout',(20,1.17,MAIN+1),(15.5,14,2),metal)
# Nominal header envelopes explain the depth of the existing sandwich stack.
for row in [-8.89,8.89]:
 box('Header plastic - nominal',(0,row,MAIN+(HEADER-1.4)/2),(48.6,2.5,HEADER-1.4),dark)
 for i in range(20):
  box('Header pin - nominal',(-24.13+2.54*i,row,MAIN+HEADER+.1),(.64,.64,2.8),metal)
for x in [-19.3,21.9]:
 box('Control envelope',(x,0,LCD+1.2),(5,5,2.4),dark)

# A real launcher screenshot on the display, rather than an invented screen.
image_path=ROOT/'preview/reference/menu-all.png'
screenmat=material('Actual PicoConsole launcher',(.1,.1,.1))
nt=screenmat.node_tree;bs=nt.nodes.get('Principled BSDF');tex=nt.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(image_path));tex.interpolation='Closest'
nt.links.new(tex.outputs['Color'],bs.inputs['Base Color']);nt.links.new(tex.outputs['Color'],bs.inputs['Emission Color']);bs.inputs['Emission Strength'].default_value=.75
bpy.ops.mesh.primitive_plane_add(size=23.4,location=(0,0,LCD+3.64));screen=bpy.context.object;screen.name='Real menu screenshot';screen.data.materials.append(screenmat)

floor=material('Studio floor',(.12,.15,.19),.8)
ground=box('Studio floor',(0,0,-2),(2000,2000,2),floor)
def aim(o,at):o.rotation_euler=(Vector(at)-o.location).to_track_quat('-Z','Y').to_euler()
for name,loc,power,size in [('Key',(-50,-60,150),125000,100),('Fill',(80,30,90),80000,90),('Rim',(-70,80,80),110000,80)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.shape='DISK';o.data.size=size;aim(o,(0,0,15))
bpy.ops.object.camera_add(location=(100,-135,190));cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=95;aim(cam,(0,0,11));scene.camera=cam

def render(name):
 scene.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)

render('assembled')
# A top view makes the small engraved letters and functional symbols inspectable.
cam.location=(0,0,190);cam.data.ortho_scale=110;aim(cam,(0,0,0));render('controls')
# Save the exterior view. Internal objects are clearance helpers, not component
# CAD; deliberately do not publish an exploded render of them.
cam.location=(100,-135,190);cam.data.ortho_scale=95;aim(cam,(0,0,11))
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'pebble-assembly.blend'))
print('Rendered actual STL geometry; electronics are nominal envelopes, not fit proof.')
