import numpy as np

data = np.memmap('challenge/Sideband_Surgery/challenge.raw', dtype=np.complex64, mode='r')
seg_len = 9338400

m0 = data[:seg_len].real - 0.5

# Let's check instantaneous frequency or zero-crossing rate over time
# In slices of 2000 samples
step = 2000
freqs_est = []
for i in range(1000000, 1500000, step):
    chunk = m0[i : i + step]
    # Zero crossings
    zc = np.where(np.diff(np.signbit(chunk)))[0]
    # Frequency estimate: zc count / (2 * len)
    f_est = len(zc) / (2.0 * step)
    freqs_est.append(f_est)

freqs_est = np.array(freqs_est)
print("Zero crossing frequency estimates (first 30 chunks):")
print(np.round(freqs_est[:30], 6))
print("Unique or histogram of zero crossing frequencies:")
hist, bin_edges = np.histogram(freqs_est, bins=20)
for count, edge in zip(hist, bin_edges):
    if count > 0:
        print(f"  f ~ {edge:.6f}: count = {count}")
