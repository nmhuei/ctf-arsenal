import numpy as np

data = np.memmap('challenge/Sideband_Surgery/challenge.raw', dtype=np.complex64, mode='r')

seg_len = 9338400

# Let's inspect Segment 0: it is purely real!
# Range: [0.18, 0.82], mean 0.50
# Let's see: what if we subtract 0.5?
seg0 = data[:seg_len].real - 0.5

# Let's look at zero crossings or autocorrelation of seg0
# Autocorrelation to find symbol rate / frame rate / line rate
lags = np.arange(1, 100000)
# Use a slice of 500,000 samples from the middle
s = seg0[1000000:1500000]
s = s - np.mean(s)
auto = np.correlate(s[:50000], s[:50000], mode='full')
auto = auto[len(auto)//2:]

# Find prominent peaks in autocorrelation
import scipy.signal
peaks, props = scipy.signal.find_peaks(auto[:20000], distance=10, height=auto[0]*0.05)
print("Seg 0 autocorrelation peaks (first 20000 lags):")
for p in peaks[:20]:
    print(f"  lag = {p}, auto = {auto[p]/auto[0]:.4f}")

# Also check PSD peaks spacing
print("\nCheck if there are harmonic spikes in Seg 0:")
fft_s = np.abs(np.fft.rfft(seg0[1000000:1000000+262144]))
freqs = np.fft.rfftfreq(262144)
top_fft = scipy.signal.find_peaks(fft_s, height=np.max(fft_s)*0.1, distance=10)[0]
for idx in top_fft[:20]:
    print(f"  f/fs = {freqs[idx]:.6f}, mag = {fft_s[idx]:.1f}")
