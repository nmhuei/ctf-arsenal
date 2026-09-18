import numpy as np
from PIL import Image

for name in ['seg0', 'seg1_fixed', 'seg2', 'seg3']:
    img = np.array(Image.open(f'script/decoded_{name}.png'))
    lines_with_black = [i for i in range(len(img)) if np.min(img[i, 20:-20]) < 128]
    print(f"{name}: inner lines with black: {lines_with_black[:5]} ... {lines_with_black[-5:] if len(lines_with_black) > 5 else []}")
    print(f"  total lines with black in middle: {len(lines_with_black)}")
