import numpy as np

data = np.memmap('challenge/Sideband_Surgery/challenge.raw', dtype=np.complex64, mode='r')
seg_len = 9338400

m0 = data[:seg_len].real - 0.5

# Let's detect transitions between tone 1 (~0.0079) and tone 2 (~0.00958)
# We can use quadrature demodulation with a carrier around the center frequency:
f_center = (0.007911 + 0.009577) / 2.0  # ~ 0.008744
print(f"Center frequency: {f_center}")

# Downconvert m0 to baseband:
t = np.arange(len(m0))
baseband = m0 * np.exp(-1j * 2 * np.pi * f_center * t)

# Lowpass filter the baseband signal
# Cutoff at 0.0015 (well above the deviation of ~0.00083, but below 2*fc)
import scipy.signal
b, a = scipy.signal.butter(4, 0.002, btype='low')
bb_filt = scipy.signal.filtfilt(b, a, baseband[:500000])

# Phase derivative gives frequency offset from f_center
phase = np.unwrap(np.angle(bb_filt))
freq_dev = np.diff(phase) / (2 * np.pi)

# Let's inspect freq_dev
print("freq_dev min:", freq_dev[10000:100000].min(), "max:", freq_dev[10000:100000].max())

# Find zero crossings of freq_dev (where it transitions between +deviation and -deviation)
zc = np.where(np.diff(np.signbit(freq_dev[10000:500000])))[0]
diffs = np.diff(zc)

print("Differences between zero crossings (sample lengths of symbols):")
# Let's look at a histogram of diffs
hist, bin_edges = np.histogram(diffs, bins=50)
for count, edge in zip(hist, bin_edges):
    if count > 5:
        print(f"  duration ~ {edge:.1f} samples: count = {count}")

# Print the smallest common duration
min_diffs = diffs[(diffs > 100) & (diffs < 10000)]
print("Smallest intervals:", np.sort(min_diffs)[:30])
