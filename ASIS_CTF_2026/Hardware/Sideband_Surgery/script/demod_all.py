import numpy as np

data = np.memmap('challenge/Sideband_Surgery/challenge.raw', dtype=np.complex64, mode='r')
seg_len = 9338400

# 1. Segment 0 (AM):
# s0(t) = Ac + m(t)
m0 = data[0*seg_len : 1*seg_len].real - 0.5

# 2. Segment 1 (FM):
# s1(t) = A * exp(j * (2*pi*int(m(t)) + phi0))
# Instantaneous frequency: angle(s[n] * conj(s[n-1])) / (2*pi)
seg1 = data[1*seg_len : 2*seg_len]
# unwrap angle or diff
phase1 = np.unwrap(np.angle(seg1))
m1 = np.diff(phase1) / (2 * np.pi)
# pad to length seg_len
m1 = np.append(m1, m1[-1])

# 3. Segment 2 (SSB-LSB):
# Carrier at 0. Since it's negative frequencies, s2(t) = m(t) - j*Hilbert(m(t))
seg2 = data[2*seg_len : 3*seg_len]
m2 = seg2.real

# 4. Segment 3 (SSB-USB):
# Carrier at 0. Positive frequencies, s3(t) = m(t) + j*Hilbert(m(t))
seg3 = data[3*seg_len : 4*seg_len]
m3 = seg3.real

print("Extracted demodulated signals. Let's compare statistics:")
for idx, (name, m) in enumerate([("m0 (AM)", m0), ("m1 (FM)", m1), ("m2 (LSB)", m2), ("m3 (USB)", m3)]):
    print(f"{name}: min={m.min():.4f}, max={m.max():.4f}, mean={m.mean():.4f}, std={m.std():.4f}")

# Check correlation between m0, m1, m2, m3!
# Let's take 100,000 samples from the middle
s = slice(1000000, 1100000)
c01 = np.corrcoef(m0[s], m1[s])[0, 1]
c02 = np.corrcoef(m0[s], m2[s])[0, 1]
c03 = np.corrcoef(m0[s], m3[s])[0, 1]
c23 = np.corrcoef(m2[s], m3[s])[0, 1]

print(f"Correlations: c(m0, m1)={c01:.4f}, c(m0, m2)={c02:.4f}, c(m0, m3)={c03:.4f}, c(m2, m3)={c23:.4f}")
