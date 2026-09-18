import numpy as np
from PIL import Image

imgs = [np.array(Image.open(f'script/master_seg{i}.png')) for i in range(4)]
# Crop to [89:149, 50:270]
crops = [im[89:149, 50:270] for im in imgs]

# Threshold each to boolean (black = True)
blacks = [(c < 128) for c in crops]

# Check overlap between black pixels in the 4 segments:
print("Black pixel counts in each segment:")
for i in range(4):
    print(f"  Seg {i}: {np.sum(blacks[i])} black pixels")

# Check pairwise overlap
for i in range(4):
    for j in range(i+1, 4):
        overlap = np.sum(blacks[i] & blacks[j])
        print(f"  Overlap Seg {i} & Seg {j}: {overlap}")

# Check 3-way overlap
print("3-way overlaps:")
for i in range(4):
    for j in range(i+1, 4):
        for k in range(j+1, 4):
            overlap = np.sum(blacks[i] & blacks[j] & blacks[k])
            print(f"  Overlap {i},{j},{k}: {overlap}")

print("4-way overlap:", np.sum(blacks[0] & blacks[1] & blacks[2] & blacks[3]))

# Total union vs XOR:
union = blacks[0] | blacks[1] | blacks[2] | blacks[3]
xor = blacks[0] ^ blacks[1] ^ blacks[2] ^ blacks[3]
print(f"Total union black pixels: {np.sum(union)}")
print(f"Total XOR black pixels: {np.sum(xor)}")

# Save both images
Image.fromarray(np.where(union, 0, 255).astype(np.uint8)).save('script/qr_union.png')
Image.fromarray(np.where(xor, 0, 255).astype(np.uint8)).save('script/qr_xor.png')
print("Saved script/qr_union.png and script/qr_xor.png")
