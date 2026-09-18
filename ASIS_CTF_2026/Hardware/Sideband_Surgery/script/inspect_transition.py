import numpy as np

data = np.memmap('challenge/Sideband_Surgery/challenge.raw', dtype=np.complex64, mode='r')

idx = 9578321
print(f"Around index {idx}:")
for i in range(idx - 10, idx + 20):
    print(f"{i}: {data[i]}")

