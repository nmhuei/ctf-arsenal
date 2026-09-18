import numpy as np
from PIL import Image

imgs = [np.array(Image.open(f'script/master_seg{i}.png')) for i in range(4)]

# Let's crop all 4 to [89:149, 54:266]
# Shape is 60 x 212
crops = [im[89:149, 54:266] for im in imgs]

# Downsample / bin into modules:
# If width is 212 and height is 60:
# How many modules wide and high is an rMQR code?
# Possible rMQR sizes:
# R7, R9, R11, R13, R15, R17
# Let's test module sizes:
print("Height 60 / modules:")
for m in [7, 9, 11, 13, 15, 17]:
    print(f"  {m} modules -> {60/m:.2f} pixels/module")

print("Width 212 / modules:")
for m in [27, 43, 59, 77, 99, 139]:
    print(f"  {m} modules -> {212/m:.2f} pixels/module")
