"""USB helper for the native console. Dependencies stay in tools/python-libs."""
from pathlib import Path
import sys, time, json, argparse, struct
sys.path.insert(0, str(Path(__file__).resolve().parent / 'python-libs'))
import serial
from serial.tools.list_ports import comports

class Console:
    def __init__(self, port=None):
        if not port:
            matches=[p.device for p in comports() if p.vid==0x2e8a and p.pid==9]
            if len(matches)!=1:
                raise RuntimeError(f'Expected one running Pico, found {matches}')
            port=matches[0]
        self.io=serial.Serial(port,115200,timeout=5,write_timeout=5)
        time.sleep(.15)
        self.io.reset_input_buffer()
    def close(self): self.io.close()
    def command(self, text):
        self.io.write((text+'\n').encode())
        line=self.io.readline().decode().strip()
        if not line: raise TimeoutError(f'No reply to {text!r}')
        return line
    def status(self): return json.loads(self.command('status'))
    def shot(self, path):
        header=self.command('shot').split()
        assert header[:4]==['FRAME','240','240','RGB565LE'],header
        raw=self.io.read(int(header[4]))
        assert len(raw)==115200, f'Truncated framebuffer: {len(raw)} bytes'
        assert self.io.readline()==b'\n'
        assert self.io.readline()==b'END_FRAME\n'
        from PIL import Image
        pixels=[]
        for (v,) in struct.iter_unpack('<H',raw):
            r=(v>>11)&31; g=(v>>5)&63; b=v&31
            pixels.append(((r<<3)|(r>>2),(g<<2)|(g>>4),(b<<3)|(b>>2)))
        im=Image.new('RGB',(240,240)); im.putdata(pixels)
        path=Path(path); path.parent.mkdir(parents=True,exist_ok=True); im.save(path)
        return raw

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('command',nargs='?',default='status')
    p.add_argument('--shot',type=Path)
    p.add_argument('--port')
    args=p.parse_args()
    con=Console(args.port)
    try:
        if args.shot: con.shot(args.shot); print(args.shot)
        else: print(con.command(args.command))
    finally: con.close()
