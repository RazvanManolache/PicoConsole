"""Convert an SDK-linked RP2350 ARM secure binary to standard UF2 blocks."""
import struct, sys
from pathlib import Path
src, dst = map(Path, sys.argv[1:])
data = src.read_bytes()
assert 0 < len(data) <= 4*1024*1024, 'Image exceeds Pico 2 flash'
count = (len(data)+255)//256
with dst.open('wb') as out:
    for block in range(count):
        payload = data[block*256:(block+1)*256].ljust(256, b'\0')
        header = struct.pack('<8I', 0x0A324655, 0x9E5D5157, 0x2000,
                             0x10000000+block*256, 256, block, count, 0xE48BFF59)
        out.write(header + payload + bytes(220) + struct.pack('<I', 0x0AB16F30))
print(f'{dst}: {len(data):,} flash bytes; {count} RP2350 ARM secure blocks')
