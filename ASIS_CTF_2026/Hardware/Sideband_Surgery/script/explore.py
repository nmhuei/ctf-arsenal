import numpy as np

total_bytes = 298828800
num_samples = total_bytes // 8

print(f"Total complex64 samples: {num_samples}")

# Let's read with memmap
data = np.memmap('challenge/Sideband_Surgery/challenge.raw', dtype=np.complex64, mode='r')

print("Shape:", data.shape)
print("Data head:", data[:10])

# Find where imaginary part becomes non-zero or where signal starts
q_nonzero = np.where(data.imag != 0)[0]
if len(q_nonzero) > 0:
    print(f"First non-zero imag at index: {q_nonzero[0]}")
else:
    print("No non-zero imag found")

# Check power / magnitude statistics
mags = np.abs(data[:1000000])
print(f"First 1M samples max mag: {mags.max()}, mean mag: {mags.mean()}")
