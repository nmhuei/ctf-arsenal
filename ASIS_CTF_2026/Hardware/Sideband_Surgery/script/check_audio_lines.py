import numpy as np

data = np.memmap('challenge/Sideband_Surgery/challenge.raw', dtype=np.complex64, mode='r')
seg_len = 9338400
fs = 240000

a0 = data[:seg_len].real - 0.5
phase1 = np.unwrap(np.angle(data[1*seg_len : 2*seg_len]))
a1 = np.diff(phase1) / (2 * np.pi) * fs
a1 = np.append(a1, a1[-1])
# Normalize a1 amplitude to match a0 (remember a1 was scaled by ~12732)
a1 = a1 * 7.85458e-5

a2 = data[2*seg_len : 3*seg_len].real
a3 = data[3*seg_len : 4*seg_len].real

# Let's check amplitudes/variances of a0, a1, a2, a3 in small blocks (e.g. 36000 samples = 1 line)
print("Line-by-line std dev of audio for lines 90 to 148:")
for line in range(89, 149):
    start = 494416 + line * 36000
    end = start + 36000
    s0 = np.std(a0[start:end])
    s1 = np.std(a1[start:end])
    s2 = np.std(a2[start:end])
    s3 = np.std(a3[start:end])
    # Also check if any signal is flat/zero
    print(f"Line {line:3d}: s0={s0:.4f}, s1={s1:.4f}, s2={s2:.4f}, s3={s3:.4f}")
