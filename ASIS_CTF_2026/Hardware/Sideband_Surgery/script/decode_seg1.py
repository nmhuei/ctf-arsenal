import numpy as np
from PIL import Image
import scipy.signal

data = np.memmap('challenge/Sideband_Surgery/challenge.raw', dtype=np.complex64, mode='r')
seg_len = 9338400
fs = 240000

print("Demodulating FM seg1 to audio...")
seg1 = data[1*seg_len : 2*seg_len]
phase1 = np.unwrap(np.angle(seg1))
audio1 = np.diff(phase1) / (2 * np.pi) * fs
audio1 = np.append(audio1, audio1[-1])

print("Demodulating audio1 (SSTV subcarrier) via Hilbert...")
analytic1 = scipy.signal.hilbert(audio1)
inst_f1 = np.diff(np.unwrap(np.angle(analytic1))) * fs / (2 * np.pi)
inst_f1 = np.append(inst_f1, inst_f1[-1])

b, a = scipy.signal.butter(2, 3000 / (fs / 2), btype='low')
filt_f1 = scipy.signal.filtfilt(b, a, inst_f1)

box = np.ones(int(0.009 * fs))
line_period = int(0.150 * fs)
y_offset = int(0.012 * fs)
y_samples = int(0.088 * fs)

sync_mask = (filt_f1 < 1300)
start_sample = int(1.8 * fs)
end_sample = int(38.0 * fs)
corr = np.convolve(sync_mask.astype(float), box, mode='same')
peaks, _ = scipy.signal.find_peaks(corr[start_sample:end_sample], distance=line_period - 1000, height=len(box)*0.6)
peaks += start_sample
print(f"Seg 1: found {len(peaks)} sync peaks")

img = np.zeros((240, 320), dtype=np.uint8)
for line_idx, peak in enumerate(peaks[:240]):
    sync_start = peak - len(box) // 2
    line_start = sync_start + y_offset
    line_end = line_start + y_samples
    if line_end < len(filt_f1):
        line_data = filt_f1[line_start:line_end]
        pixels = scipy.signal.resample(line_data, 320)
        pix_vals = np.clip((pixels - 1500) / (2300 - 1500) * 255, 0, 255)
        img[line_idx] = pix_vals.astype(np.uint8)

Image.fromarray(img).save('script/decoded_seg1_fixed.png')
print("Saved script/decoded_seg1_fixed.png")
