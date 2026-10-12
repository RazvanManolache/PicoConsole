"""Package a UF2 with matching curated source and notices. GPL-3.0-only."""
from pathlib import Path
import argparse,hashlib,json,subprocess,shutil,zipfile
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--build-dir',default='build');p.add_argument('--ninja',default=shutil.which('ninja'));p.add_argument('--verified-rebuild',type=Path,help='UF2 rebuilt from an extracted prepared source archive');a=p.parse_args()
 assert a.ninja,'Pass --ninja /path/to/ninja'
 build=Path(a.build_dir);build=build if build.is_absolute() else ROOT/build
 m=json.loads((ROOT/'dist/build-manifest.json').read_text())
 assert sha(build/'pico_console.bin')==m['binary_sha256'],'Build directory does not match the UF2 manifest'
 assert sha(ROOT/'dist/pico_console.uf2')==m['uf2_sha256']
 for name,digest in m['source_sha256'].items():assert sha(ROOT/name)==digest,f'Source changed since build: {name}'
 subprocess.run([__import__('sys').executable,str(ROOT/'tools/audit_release.py')],cwd=ROOT,check=True)
 selected=set()
 def add(path):
  path=Path(path)
  if path.is_file():selected.add(path.resolve())
 for d in ('firmware','LICENSES'):
  for path in (ROOT/d).rglob('*'):add(path)
 for name in ('README.md','LICENSE','COPYING.txt','THIRD_PARTY_NOTICES.md','dependencies.lock.json'):
  add(ROOT/name)
 for name in ('BUILD.md','NATIVE_PACK.md','INSTALLED_GAMES.md','LICENSE_AUDIT.md','HARDWARE.md'):add(ROOT/'docs'/name)
 for name in ('build.py','build.ps1','requirements.txt','audit_release.py','asset-policy.json','base_catalog.json','native_catalog.json','prepare_native.py','prepare_crisp.py','prepare_pocket.py','prepare_draw.py','prepare_linker.py','generate_puzzles.py','compress_levels.py','make_uf2.py','record_build.py','write_pack_docs.py','package_release.py','console_usb.py','smoke_catalog.py','check_final_play.py','check_menu.py'):add(ROOT/'tools'/name)
 for name in ('prepare_tiny.py','prepare_gamebuino.py','tiny-games.json','gamebuino-games.json','tiny-licences.json','gamebuino-licences.json','extra-exclusions.json','check_tiny_host.py'):add(ROOT/'tools'/name)
 for name in ('check_library.cpp','check_library_host.py'):add(ROOT/'tools'/name)
 # Exact compiler dependencies provide all headers and assembly includes.
 deps=subprocess.check_output([a.ninja,'-C',str(build),'-t','deps'],text=True)
 sdk=(ROOT/'upstream/pico-sdk').resolve();tiny=sdk/'lib/tinyusb'
 for line in deps.splitlines():
  if line.startswith('    '):
   path=Path(line.strip())
   if path.is_absolute() and path.is_relative_to(sdk):add(path)
 for unit in json.loads((build/'compile_commands.json').read_text()):
  path=Path(unit['file'])
  if path.is_relative_to(sdk):add(path)
 # CMake parses unused INTERFACE targets as well. Preserve configuration and
 # build scripts, but omit unrelated C sources, ROMs and vendor libraries.
 for path in sdk.rglob('*'):
  if not path.is_file() or '.git' in path.parts:continue
  if path.is_relative_to(sdk/'lib'):
   if not path.is_relative_to(tiny):continue
   rel=path.relative_to(tiny).as_posix()
   config=(path.name=='CMakeLists.txt' and rel.startswith('src/')) or (path.suffix=='.cmake' and (rel.startswith('hw/bsp/rp2040/') or rel in ('hw/bsp/family_support.cmake','hw/bsp/family_common.cmake')))
  else:config=path.name=='CMakeLists.txt' or path.suffix in ('.cmake','.in','.py','.ld')
  if config:add(path)
 for path in (sdk/'LICENSE.TXT',tiny/'LICENSE',sdk/'src/rp2_common/pico_printf/LICENSE',sdk/'src/rp2_common/cmsis/stub/CMSIS/LICENSE.txt',sdk/'src/rp2350/boot_stage2/pad_checksum'):add(path)
 assert any(str(x).endswith('family.cmake') for x in selected)
 # No whole PicoLibSDK mirror is needed: modified sources are included above.
 assert all(not p.is_relative_to(ROOT/'upstream/PicoLibSDK') for p in selected)
 files={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(selected)}
 version=m['firmware'].removeprefix('native-')
 out=ROOT/'dist/releases'/version;out.mkdir(parents=True,exist_ok=True)
 prefix='picoconsole-'+version;source=out/f'{prefix}-source.zip'
 with zipfile.ZipFile(source,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for name in files:z.write(ROOT/name,prefix+'/'+name)
  z.writestr(prefix+'/release-source-files.json',json.dumps(files,indent=2)+'\n')
 notices=out/f'{prefix}-notices.zip'
 with zipfile.ZipFile(notices,'w',zipfile.ZIP_DEFLATED) as z:
  for path in sorted((ROOT/'LICENSES').iterdir()):
   if path.is_file():z.write(path,'LICENSES/'+path.name)
  z.write(ROOT/'THIRD_PARTY_NOTICES.md','THIRD_PARTY_NOTICES.md')
 shutil.copyfile(ROOT/'dist/pico_console.uf2',out/f'{prefix}.uf2')
 shutil.copyfile(ROOT/'dist/build-manifest.json',out/'build-manifest.json')
 shutil.copyfile(ROOT/'logs/licence-audit.json',out/'licence-audit.json')
 host_checks={}
 for collection in ('tiny','gamebuino'):
  host=json.loads((ROOT/'logs'/(collection+'-host')/'report.json').read_text())
  assert host['result']=='passed'
  assert all(m['source_sha256'].get(k)==v for k,v in host['source_sha256'].items()),'Host-tested source differs'
  shutil.copyfile(ROOT/'logs'/(collection+'-host')/'report.json',out/(collection+'-desktop-checks.json'))
  host_checks[collection]=len(host['checks'])
 library=json.loads((ROOT/'logs/library-host/report.json').read_text())
 assert library['result']=='passed'
 assert all(m['source_sha256'].get(k)==v for k,v in library['source_sha256'].items()),'Library-tested source differs'
 assert all(sha(ROOT/k)==v for k,v in library['test_source_sha256'].items()),'Library tests changed since running'
 shutil.copyfile(ROOT/'logs/library-host/report.json',out/'library-desktop-checks.json')
 verification='Required before publishing: extract and run build.py --prepared; record its UF2 hash.'
 if a.verified_rebuild:
  digest=sha(a.verified_rebuild)
  assert digest==m['uf2_sha256'],'Source rebuild differs from release UF2'
  verification={'passed':True,'method':'Extracted prepared source; offline build with the recorded compiler; byte-identical UF2','uf2_sha256':digest}
 report={'game_count':m['game_count'],'uf2_sha256':m['uf2_sha256'],'source_files':len(files),'source_zip_sha256':sha(source),'source_rebuild_verification':verification,'desktop_checks':host_checks,'library_checks':library['summary'],'hardware_validation':'Pending: Pico disconnected. Earlier device checks do not validate this image.'}
 (out/'release-manifest.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report,indent=2))

if __name__=='__main__':main()
