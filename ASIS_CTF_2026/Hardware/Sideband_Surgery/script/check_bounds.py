import numpy as np
from PIL import Image

for name in ['seg0', 'seg1_fixed', 'seg2', 'seg3']:
    img = np.array(Image.open(f'script/decoded_{name}.png'))
    # Threshold to binary (white=255, black=0)
    # A line has black pixels if min < 128
    has_black = [i for i in range(len(img)) if np.min(img[i]) < 128]
    if has_black:
        print(f"{name}: black pixels on lines {min(has_black)} to {max(has_black)} (total {len(has_black)} lines)")
        # Also check x bounds
        cols_with_black = np.where(img < 128)[1]
        print(f"  x range: {np.min(cols_with_black)} to {np.max(cols_with_black)}")
    else:
        print(f"{name}: NO black pixels")
