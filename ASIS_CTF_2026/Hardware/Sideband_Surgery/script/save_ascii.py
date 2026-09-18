import numpy as np
from PIL import Image

imgs = [np.array(Image.open(f'script/master_seg{i}.png')) for i in range(4)]

with open('script/all_segments_ascii.txt', 'w') as f:
    for idx in range(4):
        f.write(f"\n{'='*30} SEGMENT {idx} {'='*30}\n")
        im = imgs[idx]
        for r in range(88, 150):
            # Sample every 2 pixels across columns 50 to 270
            line = "".join(["#" if p < 128 else "." for p in im[r, 50:270:2]])
            f.write(f"r={r:3d}: {line}\n")

print("Saved script/all_segments_ascii.txt")
