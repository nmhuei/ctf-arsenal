import numpy as np
import scipy.signal

data = np.memmap('challenge/Sideband_Surgery/challenge.raw', dtype=np.complex64, mode='r')
seg_len = 9338400

m0 = data[:seg_len].real - 0.5
fs = 240000

# Let's look at the audio around 1.0s to 2.0s:
t_start = int(1.0 * fs)
t_end = int(2.0 * fs)
raw_vis = m0[t_start:t_end]

# Filter around 1000 - 2000 Hz:
# In normalized frequency for fs=240000: 1000 Hz = 1000/120000 = 0.00833
# Instantaneous frequency via Hilbert transform:
analytic = scipy.signal.hilbert(raw_vis)
inst_f = np.diff(np.unwrap(np.angle(analytic))) * fs / (2 * np.pi)

# Smooth over 1ms window (240 samples):
kernel = np.ones(240) / 240
smooth_f = np.convolve(inst_f, kernel, mode='same')

t_axis = np.linspace(1.0, 2.0, len(smooth_f))

# Find the 1200 Hz break or 1200 Hz start bit:
# Let's print out the frequency every 10ms (2400 samples):
for i in range(0, len(smooth_f), 2400):
    t_sec = 1.0 + i / fs
    f_val = smooth_f[i]
    print(f"t = {t_sec:.3f}s: f = {f_val:.1f} Hz")
