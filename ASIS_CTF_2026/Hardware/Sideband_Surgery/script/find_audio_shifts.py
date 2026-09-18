import numpy as np
import scipy.signal

data = np.memmap('challenge/Sideband_Surgery/challenge.raw', dtype=np.complex64, mode='r')
seg_len = 9338400
fs = 240000

# 4 audio signals:
a0 = data[:seg_len].real - 0.5
phase1 = np.unwrap(np.angle(data[1*seg_len : 2*seg_len]))
a1 = np.diff(phase1) / (2 * np.pi) * fs
a1 = np.append(a1, a1[-1])
a2 = data[2*seg_len : 3*seg_len].real
a3 = data[3*seg_len : 4*seg_len].real

audios = [a0, a1, a2, a3]

# Before sample 3,500,000, all 4 audio signals are transmitting the EXACT same header!
# Let's cross-correlate 200,000 samples from the header (e.g. 500,000 to 700,000)
# to find the EXACT integer and sub-sample shift between audios!
chunk0 = a0[500000:700000]

print("Cross-correlating header to find relative offsets to audio[0]:")
for i in range(4):
    chunk_i = audios[i][490000:710000]
    corr = scipy.signal.correlate(chunk_i, chunk0, mode='valid')
    lags = np.arange(-10000, 10001)
    best_lag = lags[np.argmax(corr)]
    max_c = np.max(corr) / (np.linalg.norm(chunk0) * np.linalg.norm(chunk_i[best_lag+10000 : best_lag+10000+len(chunk0)]))
    print(f"  audio[{i}] vs audio[0] in header: lag = {best_lag}, norm_corr = {max_c:.6f}")

# Also check during the QR code! (between 4,000,000 and 5,000,000)
# Let's check sync pulses during the QR code:
# Lines 90 to 140
for line in [95, 105, 115, 125, 135]:
    # In each audio, find the exact minimum (center of 1200 Hz sync pulse)
    center_est = 494416 + line * 36000 + 1080
    print(f"\nLine {line} (around sample {center_est}):")
    for i in range(4):
        search_window = audios[i][center_est - 100 : center_est + 100]
        # Hilbert inst freq in window
        analytic = scipy.signal.hilbert(search_window)
        f_inst = np.diff(np.unwrap(np.angle(analytic))) * fs / (2 * np.pi)
        min_f_idx = np.argmin(f_inst)
        min_f_sample = center_est - 100 + min_f_idx
        print(f"  audio[{i}] line {line} sync min at: {min_f_sample}")
