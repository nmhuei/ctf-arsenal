import numpy as np
import scipy.signal

data = np.memmap('challenge/Sideband_Surgery/challenge.raw', dtype=np.complex64, mode='r')
seg_len = 9338400
fs = 240000

m0 = data[:seg_len].real - 0.5
analytic = scipy.signal.hilbert(m0)
inst_f = np.diff(np.unwrap(np.angle(analytic))) * fs / (2 * np.pi)
inst_f = np.append(inst_f, inst_f[-1])

b, a = scipy.signal.butter(2, 3000 / (fs / 2), btype='low')
filt_f = scipy.signal.filtfilt(b, a, inst_f)

# Find VIS stop bit (around 1.88s to 1.91s, freq ~1200)
# Then first line sync is 9ms at 1200 Hz
# Let's inspect filt_f around 400,000 to 550,000
sync_idx = np.where(filt_f < 1300)[0]
# Find where sync pulses occur
# Each sync pulse is ~2160 samples of 1200 Hz
# Let's find falling edges into sync:
falling = np.where((filt_f[:-1] >= 1300) & (filt_f[1:] < 1300))[0]

# Filter falling edges that stay below 1300 for at least 1500 samples (to be a real sync pulse)
valid_syncs = []
for idx in falling:
    if idx + 2000 < len(filt_f):
        if np.mean(filt_f[idx+200 : idx+1800] < 1300) > 0.9:
            valid_syncs.append(idx)

valid_syncs = np.array(valid_syncs)
print(f"Total valid syncs found: {len(valid_syncs)}")
diffs = np.diff(valid_syncs)
print("First 10 sync falling edge intervals:")
print(diffs[:10])

# Linear regression on sync falling edges to find the exact master clock (slope and intercept)
line_indices = np.arange(len(valid_syncs))
# Reject any outliers if diff is not around 36000
mask = np.ones(len(valid_syncs), dtype=bool)
for i in range(1, len(valid_syncs)):
    if abs(valid_syncs[i] - valid_syncs[i-1] - 36000) > 50:
        print(f"Sync anomaly at index {i}: diff = {valid_syncs[i] - valid_syncs[i-1]}")

slope, intercept = np.polyfit(line_indices, valid_syncs, 1)
print(f"Master line clock: period = {slope:.6f} samples, line 0 at {intercept:.2f}")
