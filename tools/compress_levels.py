from pathlib import Path
import re,ast,collections
root=Path(__file__).resolve().parents[1]
def encode(data):
 out=bytearray(b'\1'+len(data).to_bytes(2,'little')); i=0; positions=collections.defaultdict(list)
 while i<len(data):
  at=len(out);out.append(0);flags=0
  for bit in range(8):
   if i>=len(data):break
   best=0;dist=0; key=data[i:i+3]
   for j in reversed(positions[key][-96:]):
    d=i-j
    if d>4095:break
    n=0
    while n<18 and i+n<len(data) and data[j+n]==data[i+n]:n+=1
    if n>best:best=n;dist=d
    if best==18:break
   count=best if best>=3 else 1
   if best>=3:
    code=(dist<<4)|(best-3);out.extend(code.to_bytes(2,'little'))
   else:flags|=1<<bit;out.append(data[i])
   for k in range(count):positions[data[i+k:i+k+3]].append(i+k)
   i+=count
  out[at]=flags
 return bytes(out)
def decode(data):
 size=int.from_bytes(data[1:3],'little');out=bytearray();p=3
 while len(out)<size:
  flags=data[p];p+=1
  for b in range(8):
   if len(out)>=size:break
   if flags&(1<<b):out.append(data[p]);p+=1
   else:
    code=int.from_bytes(data[p:p+2],'little');p+=2;d=code>>4
    for _ in range((code&15)+3):out.append(out[-d])
 return bytes(out)
def compress_literals(s):
 def sub(m):
  # Level maps and solutions only, never names or copyright strings.
  strings=re.findall(r'"[^"\\\r\n]*(?:\\.[^"\\\r\n]*)*"',m[0]);data=''.join(ast.literal_eval(t) for t in strings).encode()
  if len(data)<40 or not set(data)<=set(b'x#!| _-$b*B.@p+PlLrRuUdD'):return m[0]
  enc=encode(data);assert decode(enc)==data
  if len(enc)>=len(data):return m[0]
  return '"'+''.join('\\%03o'%x for x in enc)+'"'
 return re.sub(r'(?:"[^"\\\r\n]*(?:\\.[^"\\\r\n]*)*"\s*)+',sub,s)
if __name__=='__main__':
 orig=packed=largest=0
 for p in (root/'upstream/PicoLibSDK/PicoPad/GAME/SOKOBAN/src').glob('levels*.cpp'):
  s=p.read_text();parts=re.findall(r'(?:"[^"\\\r\n]*(?:\\.[^"\\\r\n]*)*"\s*)+',s)
  for m in parts:
   data=''.join(ast.literal_eval(t) for t in re.findall(r'"[^"\\\r\n]*(?:\\.[^"\\\r\n]*)*"',m)).encode()
   orig+=len(data);packed+=min(len(data),len(encode(data)));largest=max(largest,len(data))
 print(orig,packed,'saved',orig-packed,'max literal',largest)
