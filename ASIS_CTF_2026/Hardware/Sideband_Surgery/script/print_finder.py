import numpy as np
from PIL import Image

im3 = np.array(Image.open('script/crop_seg3.png'))

# Print ASCII of the finder pattern area in im3
finder3 = im3[5:52, 4:35]
print("ASCII of finder pattern in im3:")
for r in range(len(finder3)):
    line = "".join(["#" if p < 128 else "." for p in finder3[r]])
    print(f"{r:2d} {line}")

im0 = np.array(Image.open('script/crop_seg0.png'))
finder0 = im0[20:65, 186:216]
print("\nASCII of finder pattern in im0:")
for r in range(len(finder0)):
    line = "".join(["#" if p < 128 else "." for p in finder0[r]])
    print(f"{r:2d} {line}")
