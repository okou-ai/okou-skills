#!/usr/bin/env python3
"""Original by Okou. Reproducible 512x512 monochrome noise; Python stdlib only.
No source imagery, random library, network, timestamps, or upstream imports.
PNG uses uncompressed DEFLATE blocks for byte-stability across zlib versions.
"""
from pathlib import Path
import struct
import zlib

def chunk(kind, data):
    return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff)

def generate():
    state = 0x4F4B4F55  # Fixed seed: ASCII OKOU
    rows = bytearray()
    for y in range(512):
        rows.append(0)  # PNG scanline filter None
        for x in range(512):
            state = (1664525 * state + 1013904223) & 0xffffffff
            value = 255 if (state >> 24) >= 128 else 0
            rows.append(value)
    data = bytes(rows)
    stream = bytearray(b'\x78\x01')
    for start in range(0, len(data), 65535):
        block = data[start:start + 65535]
        stream.append(1 if start + len(block) == len(data) else 0)
        n = len(block)
        stream.extend(struct.pack('<HH', n, n ^ 65535))
        stream.extend(block)
    stream.extend(struct.pack('>I', zlib.adler32(data) & 0xffffffff))
    return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', 512, 512, 8, 0, 0, 0, 0)) + chunk(b'IDAT', bytes(stream)) + chunk(b'IEND', b'')

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True, help='new PNG path outside the installed skill')
    args = parser.parse_args()
    out = Path(args.out).resolve()
    if out.is_relative_to(Path(__file__).resolve().parent.parent):
        parser.error('do not write into the installed skill')
    with out.open('xb') as stream:
        stream.write(generate())
    print(out)
