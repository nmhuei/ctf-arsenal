#!/usr/bin/env python3
from pathlib import Path
from PIL import Image

IN = Path('./knitted-flag/pattern.k')
OUT = Path('./knitted_flag_proof.png')

lines = IN.read_text().splitlines()
rows = []
cur = []
curdir = None
for line in lines:
    p = line.split()
    if p and p[0] == 'knit':
        direction = p[1]
        if cur and (direction != curdir or len(cur) >= 20):
            rows.append(cur)
            cur = []
        curdir = direction
        bed = p[2][0]
        needle = int(p[2][1:])
        cur.append((bed, needle))
    else:
        if cur:
            rows.append(cur)
            cur = []
            curdir = None
if cur:
    rows.append(cur)

# Each valid knitted course has 20 stitches. Back-bed stitches form black pixels.
mat = []
for row in rows:
    if len(row) == 20:
        pixels = ['f'] * 20
        for bed, needle in row:
            if 1 <= needle <= 20:
                pixels[needle - 1] = bed
        mat.append(pixels)

# Skip the cast-on/plain setup rows, transpose rows->x, needle->y, then flip vertically.
bitmap_rows = mat[3:]
scale = 6
w, h = len(bitmap_rows), 20
img = Image.new('RGB', (w * scale, h * scale), 'white')
px = img.load()
for x, row in enumerate(bitmap_rows):
    for y in range(20):
        black = row[19 - y] == 'b'
        color = (0, 0, 0) if black else (255, 255, 255)
        for dx in range(scale):
            for dy in range(scale):
                px[x * scale + dx, y * scale + dy] = color
img.save(OUT)

flag = 'GPNCTF{con6RatulaT10n5_you_hAVe_unDer5tOoD_kNItOUt_and_UnrAV3LEd_TH3_7AB13c1OTHS}'
print(flag)
print(f'proof image: {OUT}')
