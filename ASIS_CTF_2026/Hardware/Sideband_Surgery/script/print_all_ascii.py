import numpy as np
from PIL import Image

imgs = [np.array(Image.open(f'script/master_seg{i}.png')) for i in range(4)]

# The QR region runs from row 88 to 150, col 50 to 270
for idx in range(4):
    print(f"\n==================== SEGMENT {idx} ====================")
    im = imgs[idx]
    for r in range(88, 150):
        # We can sample every 2 columns to make it fit on terminal:
        line = "".join(["#" if p < 128 else "." for p in im[r, 50:270:2]])
        # Check if line has any black:
        if "#" in line:
            print(f"r={r:3d}: {line}")
