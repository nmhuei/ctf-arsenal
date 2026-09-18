import numpy as np
from PIL import Image

im1 = np.array(Image.open('script/master_seg1.png'))
# Top row of content is around line 89
print("Inspecting lines 89 to 95 of im1:")
for r in range(89, 96):
    line = "".join(["#" if p < 128 else "." for p in im1[r, 50:270]])
    print(f"r={r:3d}: {line}")
