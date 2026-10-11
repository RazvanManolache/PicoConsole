"""Portable PicoConsole UF2 build. SPDX-License-Identifier: GPL-3.0-only"""
from pathlib import Path
import argparse,os,shutil,subprocess,sys,json

ROOT=Path(__file__).resolve().parents[1]
def run(*args,**kw):
    print('+',' '.join(str(x) for x in args),flush=True)
    subprocess.run([str(x) for x in args],cwd=ROOT,check=True,**kw)

def executable(value,name):
    found=value or shutil.which(name)
    if not found:raise SystemExit(f'{name} is required. Add it to PATH or pass --{name.split("-")[0]}. See docs/BUILD.md.')
    return str(Path(found).resolve())

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--toolchain',default=os.getenv('PICO_TOOLCHAIN_PATH'),help='ARM GNU bin directory; otherwise use PATH')
    p.add_argument('--cmake',default=os.getenv('CMAKE_COMMAND'))
    p.add_argument('--ninja',default=os.getenv('NINJA_COMMAND'))
    p.add_argument('--build-dir',default='build')
    p.add_argument('--prepared',action='store_true',help='Build a self-contained release source bundle without regenerating ports')
    p.add_argument('--offline',action='store_true',help='Do not initialise dependencies or install Python packages')
    a=p.parse_args()
    compiler=Path(a.toolchain)/('arm-none-eabi-gcc.exe' if os.name=='nt' else 'arm-none-eabi-gcc') if a.toolchain else shutil.which('arm-none-eabi-gcc')
    if not compiler or not Path(compiler).is_file():raise SystemExit('ARM GNU arm-none-eabi-gcc is required; use --toolchain /path/to/bin. See docs/BUILD.md.')
    cmake=executable(a.cmake,'cmake');ninja=executable(a.ninja,'ninja')
    sys.path.insert(0,str(ROOT/'tools/python-libs'))
    try:import elftools
    except ImportError:
        if a.offline:raise SystemExit('Install tools/requirements.txt before an offline build.')
        run(sys.executable,'-m','pip','install','--target',ROOT/'tools/python-libs','-r',ROOT/'tools/requirements.txt')
    if not a.prepared:
        if not a.offline:
            run('git','submodule','update','--init','--','upstream/PicoLibSDK','upstream/crisp-sdl','upstream/pocket-gamer','upstream/pico-sdk','upstream/tinyjoypad-sdl','upstream/gamebuino-sdl')
            run('git','-C',ROOT/'upstream/pico-sdk','submodule','update','--init','--','lib/tinyusb')
        lock=json.loads((ROOT/'dependencies.lock.json').read_text())
        for name,dep in lock.items():
            path=ROOT/dep['path']
            actual=subprocess.check_output(['git','-C',str(path),'rev-parse','HEAD'],text=True).strip()
            assert actual==dep['commit'],f'{name}: dependency revision differs from the reviewed version'
            dirty=subprocess.check_output(['git','-C',str(path),'status','--porcelain','--untracked-files=no'],text=True)
            assert not dirty,f'{name}: tracked dependency files have changes'
        (ROOT/'tools/native_catalog.json').write_bytes((ROOT/'tools/base_catalog.json').read_bytes())
        for script in ('prepare_crisp','prepare_pocket','prepare_tiny','prepare_gamebuino','prepare_native','prepare_draw','prepare_linker','audit_release'):
            run(sys.executable,ROOT/'tools'/f'{script}.py')
    else:
        import hashlib
        for name,digest in json.loads((ROOT/'release-source-files.json').read_text()).items():
            assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,f'Source bundle changed: {name}'
        run(sys.executable,ROOT/'tools/audit_release.py','--prepared')
    build=Path(a.build_dir);build=build if build.is_absolute() else ROOT/build
    env=os.environ.copy();env['PICO_SDK_PATH']=str(ROOT/'upstream/pico-sdk');env['PICO_TOOLCHAIN_PATH']=str(Path(compiler).parent)
    env['PATH']=str(Path(compiler).parent)+os.pathsep+env['PATH'];env['PICOCONSOLE_BUILD_DIR']=str(build)
    run(cmake,'-S',ROOT/'firmware','-B',build,'-G','Ninja',f'-DCMAKE_MAKE_PROGRAM={ninja}',f'-DPython3_EXECUTABLE={sys.executable}','-DCMAKE_BUILD_TYPE=Release','-DCMAKE_EXPORT_COMPILE_COMMANDS=ON',env=env)
    run(cmake,'--build',build,'--parallel',str(min(os.cpu_count() or 4,8)),env=env)
    (ROOT/'dist').mkdir(exist_ok=True)
    run(sys.executable,ROOT/'tools/make_uf2.py',build/'pico_console.bin',ROOT/'dist/pico_console.uf2',env=env)
    run(sys.executable,ROOT/'tools/record_build.py',env=env)
    if not a.prepared:
        run(sys.executable,ROOT/'tools/write_pack_docs.py')
    print('Built dist/pico_console.uf2. No hardware was flashed.',flush=True)

if __name__=='__main__':main()
