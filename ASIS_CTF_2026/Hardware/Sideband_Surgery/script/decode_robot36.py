import numpy as np
from PIL import Image
import scipy.signal

data = np.memmap('challenge/Sideband_Surgery/challenge.raw', dtype=np.complex64, mode='r')
seg_len = 9338400

m0 = data[:seg_len].real - 0.5
fs = 240000

# Let's compute instantaneous frequency of m0 using Hilbert transform
analytic = scipy.signal.hilbert(m0)
# Instantaneous frequency in Hz
inst_freq = np.diff(np.unwrap(np.angle(analytic))) * fs / (2 * np.pi)
inst_freq = np.append(inst_freq, inst_freq[-1])

# Smooth frequency slightly (e.g. 50 samples ~ 0.2 ms)
b, a = scipy.signal.butter(2, 3000 / (fs / 2), btype='low')
filt_freq = scipy.signal.filtfilt(b, a, inst_freq)

# In Robot 36, after VIS stop bit (~1.91s), sync pulses occur every 150 ms (36,000 samples)
# A sync pulse is 1200 Hz for 9 ms (2160 samples)
# Let's find sync pulses:
sync_mask = (filt_freq < 1300)

# Let's find sync pulses between t=1.8s and 38.0s
start_sample = int(1.8 * fs)
end_sample = int(38.0 * fs)

# Cross-correlate with a 9ms 1200Hz boxcar
box = np.ones(int(0.009 * fs))
corr = np.convolve(sync_mask.astype(float), box, mode='same')

# Expected distance between lines: 150 ms = 36000 samples
line_period = int(0.150 * fs)
print(f"Line period: {line_period} samples")

# Let's find peaks in corr separated by ~line_period
peaks, _ = scipy.signal.find_peaks(corr[start_sample:end_sample], distance=line_period - 1000, height=len(box)*0.7)
peaks += start_sample

print(f"Found {len(peaks)} sync peaks!")
if len(peaks) > 0:
    print(f"First peak at {peaks[0]} ({peaks[0]/fs:.4f}s), intervals between peaks:")
    diffs = np.diff(peaks)
    print(diffs[:20])

# Now, for each of the 240 lines, extract the Y scan:
# Sync pulse is 9ms (2160 samples), sync porch is 3ms (720 samples) -> start of Y is sync_start + 12ms (2880 samples)
# Y scan duration is 88ms (21120 samples)
# Let's extract 320 pixels from the 21120 samples:
img = np.zeros((len(peaks), 320), dtype=np.uint8)

y_offset = int(0.012 * fs)
y_samples = int(0.088 * fs)

for line_idx, peak in enumerate(peaks):
    # Center of sync pulse is peak, so sync starts at peak - len(box)/2
    sync_start = peak - len(box) // 2
    line_start = sync_start + y_offset
    line_end = line_start + y_samples
    if line_end < len(filt_freq):
        line_data = filt_freq[line_start:line_end]
        # Resample to 320 pixels
        pixels = scipy.signal.resample(line_data, 320)
        # Scale 1500..2300 Hz to 0..255
        pix_vals = np.clip((pixels - 1500) / (2300 - 1500) * 255, 0, 255)
        img[line_idx] = pix_vals.astype(np.uint8)

Image.fromarray(img).save('script/decoded_m0_gray.png')
print(f"Saved script/decoded_m0_gray.png with shape {img.shape}")
