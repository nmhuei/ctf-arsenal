import numpy as np
from PIL import Image

for i in range(4):
    im = np.array(Image.open(f'script/master_seg{i}.png'))
    # Clean noise: only consider lines 80 to 160 and cols 40 to 280
    roi = im[80:160, 40:280]
    black_mask = (roi < 128)
    rows, cols = np.where(black_mask)
    if len(rows) > 0:
        min_r, max_r = 80 + np.min(rows), 80 + np.max(rows)
        min_c, max_c = 40 + np.min(cols), 40 + np.max(cols)
        print(f"Seg {i}: rows [{min_r:3d}..{max_r:3d}] (height={max_r-min_r+1}), cols [{min_c:3d}..{max_c:3d}] (width={max_c-min_c+1})")
    else:
        print(f"Seg {i}: no black pixels")
