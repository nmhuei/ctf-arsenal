import numpy as np

data = np.memmap('challenge/Sideband_Surgery/challenge.raw', dtype=np.complex64, mode='r')
seg_len = 9338400
fs = 240000

m0 = data[:seg_len].real - 0.5
seg1 = data[1*seg_len : 2*seg_len]

# Instantaneous frequency of seg1:
phase1 = np.unwrap(np.angle(seg1))
f_rf1 = np.diff(phase1) / (2 * np.pi) * fs
f_rf1 = np.append(f_rf1, f_rf1[-1])

# Let's compare m0 and f_rf1 in the slice [1000000 : 1010000]
s = slice(1000000, 1010000)
print("m0 slice: min=", m0[s].min(), "max=", m0[s].max())
print("f_rf1 slice: min=", f_rf1[s].min(), "max=", f_rf1[s].max(), "mean=", f_rf1[s].mean())

# Polyfit to find scaling:
p = np.polyfit(f_rf1[s], m0[s], 1)
print("m0 ~ a * f_rf1 + b:", p)
