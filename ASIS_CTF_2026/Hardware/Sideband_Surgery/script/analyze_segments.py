import numpy as np

data = np.memmap('challenge/Sideband_Surgery/challenge.raw', dtype=np.complex64, mode='r')

seg_len = 9338400

for i in range(4):
    seg = data[i*seg_len : (i+1)*seg_len]
    print(f"=== SEGMENT {i} ===")
    print(f"Real: min={seg.real.min():.4f}, max={seg.real.max():.4f}, mean={seg.real.mean():.4f}, std={seg.real.std():.4f}")
    print(f"Imag: min={seg.imag.min():.4f}, max={seg.imag.max():.4f}, mean={seg.imag.mean():.4f}, std={seg.imag.std():.4f}")
    print(f"Imag nonzero count: {np.count_nonzero(seg.imag)} / {seg_len}")
