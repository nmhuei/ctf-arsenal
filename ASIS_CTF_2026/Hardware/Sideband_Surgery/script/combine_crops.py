import numpy as np
from PIL import Image

im0 = np.array(Image.open('script/crop_seg0.png'))
im1 = np.array(Image.open('script/crop_seg1_fixed.png'))
im2 = np.array(Image.open('script/crop_seg2.png'))
im3 = np.array(Image.open('script/crop_seg3.png'))

# Pixel-wise minimum (black where any is black)
combined_min = np.minimum(np.minimum(im0, im1), np.minimum(im2, im3))
Image.fromarray(combined_min).save('script/combined_min.png')

# Also binary combination (threshold each at 128)
b0 = (im0 < 128)
b1 = (im1 < 128)
b2 = (im2 < 128)
b3 = (im3 < 128)

b_or = (b0 | b1 | b2 | b3)
b_img = np.where(b_or, 0, 255).astype(np.uint8)
Image.fromarray(b_img).save('script/combined_binary.png')
print("Saved script/combined_min.png and script/combined_binary.png")
