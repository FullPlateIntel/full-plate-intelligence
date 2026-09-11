#!/usr/bin/env python3
"""Install favicon apple parts 07-42 + brand_favicon.py from CRC-checked payload lines."""
from pathlib import Path
import binascii, base64, zlib, hashlib
ROOT = Path(__file__).resolve().parents[1]
pay = ROOT / "build" / "_payload"
lines = []
for p in sorted(pay.glob("lines_*.txt")):
    lines.extend(p.read_text().splitlines())
chunks = []
for i, line in enumerate(lines):
    if not line.strip():
        continue
    crc_s, chunk = line.split(":", 1)
    crc = binascii.crc32(chunk.encode()) & 0xFFFFFFFF
    assert f"{crc:08x}" == crc_s, (i, crc_s, f"{crc:08x}")
    chunks.append(chunk)
blob = zlib.decompress(base64.b64decode("".join(chunks)))
sizes = [800]*35 + [264, 1548]
names = [f"build/brand-icons/apple-touch-icon-180.png.b64.part{i:02d}" for i in range(7, 43)]
names.append("build/brand_favicon.py")
assert sum(sizes) == len(blob), (sum(sizes), len(blob))
off = 0
for name, sz in zip(names, sizes):
    data = blob[off:off+sz]
    off += sz
    path = ROOT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    print("OK", name, sz, hashlib.md5(data).hexdigest())
print("BLOB_SHA256", hashlib.sha256(blob).hexdigest())
print("ALL_OK")
