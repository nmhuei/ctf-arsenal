import numpy as np

data = np.memmap('challenge/Sideband_Surgery/challenge.raw', dtype=np.complex64, mode='r')

# Let's find the exact boundaries where variance or nature changes
# Check every 100000 samples
step = 100000
stats = []
for i in range(0, len(data), step):
    chunk = data[i:i+step]
    stats.append((i, float(np.mean(chunk.real)), float(np.var(chunk.real)), 
                     float(np.mean(chunk.imag)), float(np.var(chunk.imag))))

# Print when there are big jumps
for i in range(1, len(stats)):
    prev = stats[i-1]
    curr = stats[i]
    if abs(curr[2] - prev[2]) > 0.05 or abs(curr[4] - prev[4]) > 0.05:
        print(f"Jump near {curr[0]}: prev={prev}, curr={curr}")
