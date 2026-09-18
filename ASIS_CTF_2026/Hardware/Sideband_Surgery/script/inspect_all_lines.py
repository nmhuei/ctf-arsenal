import numpy as np

data = np.memmap('challenge/Sideband_Surgery/challenge.raw', dtype=np.complex64, mode='r')
seg_len = 9338400
fs = 240000

# Let's inspect decoded_seg0, line by line
img0 = np.array(Image.open('script/decoded_seg0.png'))

print("Seg 0 line min values:")
for i in range(0, 240, 10):
    print(f"Line {i:3d}: min={img0[i].min()}, max={img0[i].max()}, mean={img0[i].mean():.1f}")
