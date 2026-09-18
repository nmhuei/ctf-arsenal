import numpy as np

data = np.memmap('challenge/Sideband_Surgery/challenge.raw', dtype=np.complex64, mode='r')

# Check imaginary part across chunks
step = 1000000
for i in range(0, len(data), step):
    chunk = data[i:i+step]
    has_imag = np.any(chunk.imag != 0)
    real_var = np.var(chunk.real)
    imag_var = np.var(chunk.imag)
    print(f"[{i:10d} - {i+len(chunk):10d}] real var: {real_var:.6f}, imag var: {imag_var:.6f}, has_imag: {has_imag}")

