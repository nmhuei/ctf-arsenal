import numpy as np
from PIL import Image
import scipy.signal

data = np.memmap('challenge/Sideband_Surgery/challenge.raw', dtype=np.complex64, mode='r')
seg_len = 9338400
fs = 240000

def get_freq_series(seg_idx):
    if seg_idx == 0:
        sig = data[:seg_len].real - 0.5
        analytic = scipy.signal.hilbert(sig)
        inst_f = np.diff(np.unwrap(np.angle(analytic))) * fs / (2 * np.pi)
        inst_f = np.append(inst_f, inst_f[-1])
        return inst_f
    elif seg_idx == 1:
        seg1 = data[1*seg_len : 2*seg_len]
        inst_f = np.diff(np.unwrap(np.angle(seg1))) * fs / (2 * np.pi)
        inst_f = np.append(inst_f, inst_f[-1])
        return inst_f
    elif seg_idx == 2:
        sig = data[2*seg_len : 3*seg_len].real
        analytic = scipy.signal.hilbert(sig)
        inst_f = np.diff(np.unwrap(np.angle(analytic))) * fs / (2 * np.pi)
        inst_f = np.append(inst_f, inst_f[-1])
        return inst_f
    elif seg_idx == 3:
        sig = data[3*seg_len : 4*seg_len].real
        analytic = scipy.signal.hilbert(sig)
        inst_f = np.diff(np.unwrap(np.angle(analytic))) * fs / (2 * np.pi)
        inst_f = np.append(inst_f, inst_f[-1])
        return inst_f

box = np.ones(int(0.009 * fs))
line_period = int(0.150 * fs)
y_offset = int(0.012 * fs)
y_samples = int(0.088 * fs)

b, a = scipy.signal.butter(2, 3000 / (fs / 2), btype='low')

for idx in range(4):
    print(f"Decoding segment {idx}...")
    inst_freq = get_freq_series(idx)
    filt_freq = scipy.signal.filtfilt(b, a, inst_freq)
    
    sync_mask = (filt_freq < 1300)
    start_sample = int(1.8 * fs)
    end_sample = int(38.0 * fs)
    corr = np.convolve(sync_mask.astype(float), box, mode='same')
    peaks, _ = scipy.signal.find_peaks(corr[start_sample:end_sample], distance=line_period - 1000, height=len(box)*0.6)
    peaks += start_sample
    print(f"  Seg {idx}: found {len(peaks)} peaks")
    
    img = np.zeros((240, 320), dtype=np.uint8)
    for line_idx, peak in enumerate(peaks[:240]):
        sync_start = peak - len(box) // 2
        line_start = sync_start + y_offset
        line_end = line_start + y_samples
        if line_end < len(filt_freq):
            line_data = filt_freq[line_start:line_end]
            pixels = scipy.signal.resample(line_data, 320)
            pix_vals = np.clip((pixels - 1500) / (2300 - 1500) * 255, 0, 255)
            img[line_idx] = pix_vals.astype(np.uint8)
            
    Image.fromarray(img).save(f'script/decoded_seg{idx}.png')
    print(f"  Saved script/decoded_seg{idx}.png")
