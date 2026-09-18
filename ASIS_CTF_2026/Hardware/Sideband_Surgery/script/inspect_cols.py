import numpy as np
from PIL import Image

for i in range(4):
    im = np.array(Image.open(f'script/master_seg{i}.png'))
    crop = im[90:150, 50:270]
    print(f"=== Seg {i} ===")
    print("  col 50..100 min:", crop[:, :50].min(), "max:", crop[:, :50].max(), "mean:", crop[:, :50].mean())
    print("  col 100..160 min:", crop[:, 50:110].min(), "max:", crop[:, 50:110].max(), "mean:", crop[:, 50:110].mean())
    print("  col 160..210 min:", crop[:, 110:160].min(), "max:", crop[:, 110:160].max(), "mean:", crop[:, 110:160].mean())
    print("  col 210..270 min:", crop[:, 160:].min(), "max:", crop[:, 160:].max(), "mean:", crop[:, 160:].mean())
