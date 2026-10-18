"""Export the parametric original enclosure with OpenSCAD; no third-party geometry."""
from pathlib import Path
import argparse, subprocess, concurrent.futures, json, hashlib, struct, collections, zipfile
import xml.etree.ElementTree as ET

root=Path(__file__).resolve().parent
parser=argparse.ArgumentParser()
parser.add_argument('--openscad',default='openscad')
parser.add_argument('--skip-export',action='store_true',help='Reuse existing STLs while iterating validation; do not use for final packaging')
args=parser.parse_args()
out=root/'print';out.mkdir(exist_ok=True)
logdir=root.parents[1]/'logs'/'enclosure';logdir.mkdir(parents=True,exist_ok=True)
parts={
 'front':{'part':'front'},
 'rear-pico2':{'part':'rear','board':'pico2'},
 'rear-marble':{'part':'rear','board':'marble'},
 'button-retainer':{'part':'retainer'},
 **{f'button-{name}':{'part':'cap','key':i} for i,name in enumerate('ABXY')},
 'joystick-2.10':{'part':'joystick','socket':2.10},
 'fit-coupon':{'part':'coupon'},
}
def export(item):
 name,params=item
 command=[args.openscad,'--export-format','binstl','-o',str(out/(name+'.stl'))]
 for key,value in params.items():command+=['-D',key+'='+json.dumps(value)]
 command.append(str(root/'picoconsole_pebble.scad'))
 result=subprocess.run(command,text=True,capture_output=True)
 (logdir/(name+'.log')).write_text(result.stdout+result.stderr,encoding='utf-8')
 if result.returncode:raise RuntimeError(name+': '+result.stderr)
 print('Exported '+name,flush=True)
 return name
if not args.skip_export:
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(export,parts.items()))

def inspect(path):
 data=path.read_bytes();n=struct.unpack_from('<I',data,80)[0]
 assert len(data)==84+n*50
 edges=collections.Counter();vertices=[];volume=0.0;degenerate=0;links=collections.defaultdict(set)
 for i in range(n):
  v=struct.unpack_from('<12fH',data,84+i*50)[3:12]
  points=[tuple(round(c,5) for c in v[j:j+3]) for j in (0,3,6)]
  vertices.extend(points)
  a,b,c=points
  cross=(b[1]*c[2]-b[2]*c[1],b[2]*c[0]-b[0]*c[2],b[0]*c[1]-b[1]*c[0])
  volume+=sum(a[j]*cross[j] for j in range(3))/6
  u=tuple(b[j]-a[j] for j in range(3));w=tuple(c[j]-a[j] for j in range(3))
  area2=(u[1]*w[2]-u[2]*w[1])**2+(u[2]*w[0]-u[0]*w[2])**2+(u[0]*w[1]-u[1]*w[0])**2
  if len(set(points))<3 or area2<1e-14:degenerate+=1
  for j in range(3):
   u,w=points[j],points[(j+1)%3];edges[tuple(sorted((u,w)))]+=1
   links[u].add(w);links[w].add(u)
 bounds=[[min(v[j] for v in vertices),max(v[j] for v in vertices)] for j in range(3)]
 bad=sum(count!=2 for count in edges.values())
 assert bad==0 and degenerate==0 and volume>0,(path.name,bad,degenerate,volume)
 assert bounds[2][0]>=-.01,(path.name,'below print bed')
 remaining=set(links);components=0
 while remaining:
  components+=1;stack=[remaining.pop()]
  while stack:
   for neighbor in links[stack.pop()]:
    if neighbor in remaining:remaining.remove(neighbor);stack.append(neighbor)
 assert components==1,(path.name,'disconnected solids',components)
 return {'triangles':n,'bounds_mm':bounds,'size_mm':[round(b-a,3) for a,b in bounds],
         'volume_mm3':round(volume,2),'nonmanifold_edges':bad,'degenerate_faces':degenerate,
         'connected_components':components,
         'sha256':hashlib.sha256(data).hexdigest()}
report={name:inspect(out/(name+'.stl')) for name in parts}

def collision_check(test):
 target=logdir/(test+'.stl')
 if target.exists():target.unlink()
 command=[args.openscad,'--export-format','binstl','-o',str(target),'-D','part='+json.dumps(test)]
 if test=='check-fastener-ports':command+=['-D','board="marble"']
 result=subprocess.run(command+[str(root/'picoconsole_pebble.scad')],text=True,capture_output=True)
 (logdir/(test+'.log')).write_text(result.stdout+result.stderr,encoding='utf-8')
 # OpenSCAD returns 1 for a valid empty top-level geometry, which is expected here.
 empty='Current top level object is empty.' in (result.stdout+result.stderr) and not target.exists()
 assert empty,(test,'unexpected intersection or CAD failure',result.stderr)
 print('PASS '+test,flush=True)
 return test,'PASS: zero volumetric overlap at nominal dimensions'
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
 checks=dict(pool.map(collision_check,['check-shells','check-caps','check-lcd','check-retainer','check-hardware','check-fastener-ports']))

NS='http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
ET.register_namespace('',NS)
def tag(n):return '{'+NS+'}'+n
def plate(variant):
 model=ET.Element(tag('model'),{'unit':'millimeter','{http://www.w3.org/XML/1998/namespace}lang':'en-US'})
 ET.SubElement(model,tag('metadata'),{'name':'Title'}).text='PicoConsole Pebble Mini v0.2 / '+variant
 resources=ET.SubElement(model,tag('resources'));build=ET.SubElement(model,tag('build'))
 layout=[('front',35,22),('rear-'+variant,35,62),('button-retainer',85,20),
         *[(f'button-{n}',85,45+i*10) for i,n in enumerate('ABXY')],
         ('joystick-2.10',85,95),('fit-coupon',35,120)]
 for oid,(name,x,y) in enumerate(layout,1):
  obj=ET.SubElement(resources,tag('object'),{'id':str(oid),'type':'model','name':name})
  mesh=ET.SubElement(obj,tag('mesh'));verts=ET.SubElement(mesh,tag('vertices'));tris=ET.SubElement(mesh,tag('triangles'))
  data=(out/(name+'.stl')).read_bytes();n=struct.unpack_from('<I',data,80)[0];lookup={}
  for i in range(n):
   v=struct.unpack_from('<12fH',data,84+i*50)[3:12];ids=[]
   for j in (0,3,6):
    p=tuple(round(c,5) for c in v[j:j+3])
    if p not in lookup:
     lookup[p]=len(lookup);ET.SubElement(verts,tag('vertex'),dict(zip(('x','y','z'),map(str,p))))
    ids.append(lookup[p])
   ET.SubElement(tris,tag('triangle'),dict(zip(('v1','v2','v3'),map(str,ids))))
  ET.SubElement(build,tag('item'),{'objectid':str(oid),'transform':f'1 0 0 0 1 0 0 0 1 {x} {y} 0'})
 with zipfile.ZipFile(out/('pebble-'+variant+'.3mf'),'w',zipfile.ZIP_DEFLATED) as z:
  z.writestr('[Content_Types].xml','<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
  z.writestr('_rels/.rels','<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
  z.writestr('3D/3dmodel.model',ET.tostring(model,encoding='utf-8',xml_declaration=True))
 return {'objects':len(layout),'units':'millimeter','profile':'geometry only; choose your printer and supports in the slicer'}
plates={v:plate(v) for v in ['pico2','marble']}
(root/'mesh-validation.json').write_text(json.dumps({'prototype':True,'hardware_fit':'not physically verified','source_sha256':hashlib.sha256((root/'picoconsole_pebble.scad').read_bytes()).hexdigest(),'parts':report,'nominal_collision_checks':checks,'print_plates':plates},indent=2)+'\n')
print('PASS: 10 closed, single-solid meshes; nominal collision checks; two 3MF plates.')
