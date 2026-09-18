import numpy as np

data = np.memmap('challenge/Sideband_Surgery/challenge.raw', dtype=np.complex64, mode='r')
seg_len = 9338400

m0 = data[:seg_len].real - 0.5

# Look at 1000 samples from index 1,000,000
chunk = m0[1000000 : 1001000]

print("chunk min:", chunk.min(), "max:", chunk.max(), "mean:", chunk.mean())

# Let's see if chunk is binary or multi-level or sinusoidal or audio
# Print a text-based ASCII plot of 100 samples
print("ASCII plot of 80 samples:")
for i in range(80):
    val = chunk[i]
    # val ranges roughly from -0.32 to +0.32
    stars = int((val + 0.35) / 0.7 * 60)
    print(f"{i:3d} [{val:+0.3f}] |" + " " * max(0, stars) + "*")
