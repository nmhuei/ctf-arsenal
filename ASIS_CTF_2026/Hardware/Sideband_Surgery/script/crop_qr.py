import numpy as np
from PIL import Image

imgs = {}
for name in ['seg0', 'seg1_fixed', 'seg2', 'seg3']:
    im = np.array(Image.open(f'script/decoded_{name}.png'))
    # Skip line 0 glitch
    # Crop to lines 85:155, cols 50:270
    crop = im[85:155, 50:270]
    imgs[name] = crop
    Image.fromarray(crop).save(f'script/crop_{name}.png')

print("Saved crops. Let's check min pixel value in each crop:")
for name in imgs:
    print(f"{name}: min={imgs[name].min()}, max={imgs[name].max()}, mean={imgs[name].mean():.1f}")
