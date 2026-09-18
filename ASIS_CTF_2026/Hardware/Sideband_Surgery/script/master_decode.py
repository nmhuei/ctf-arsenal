import numpy as np
from PIL import Image
import scipy.signal

data = np.memmap('challenge/Sideband_Surgery/challenge.raw', dtype=np.complex64, mode='r')
seg_len = 9338400
fs = 240000

# 1. Demodulate all 4 audio signals:
print("Demodulating audio signals...")
audio = []

# Seg 0: AM
audio.append(data[:seg_len].real - 0.5)

# Seg 1: FM
phase1 = np.unwrap(np.angle(data[1*seg_len : 2*seg_len]))
a1 = np.diff(phase1) / (2 * np.pi) * fs
a1 = np.append(a1, a1[-1])
audio.append(a1)

# Seg 2: SSB-LSB
audio.append(data[2*seg_len : 3*seg_len].real)

# Seg 3: SSB-USB
audio.append(data[3*seg_len : 4*seg_len].real)

# Filter parameters:
b, a = scipy.signal.butter(2, 3000 / (fs / 2), btype='low')

# Line clock parameters:
line_period = 36000
line0_sync = 494416
y_start_offset = 2880
y_duration = 21120
width = 320
height = 240

decoded_imgs = []

for idx in range(4):
    print(f"Decoding segment {idx} with master clock...")
    # Compute instantaneous frequency of audio subcarrier
    analytic = scipy.signal.hilbert(audio[idx])
    inst_f = np.diff(np.unwrap(np.angle(analytic))) * fs / (2 * np.pi)
    inst_f = np.append(inst_f, inst_f[-1])
    filt_f = scipy.signal.filtfilt(b, a, inst_f)
    
    img = np.zeros((height, width), dtype=np.float32)
    for k in range(height):
        t_start = line0_sync + k * line_period + y_start_offset
        t_end = t_start + y_duration
        if t_end < len(filt_f):
            line_samples = filt_f[t_start:t_end]
            # Resample to 320
            pixels = scipy.signal.resample(line_samples, width)
            img[k] = pixels
    
    # Scale from 1500..2300 Hz to 0..255
    img_scaled = np.clip((img - 1500.0) / (2300.0 - 1500.0) * 255.0, 0, 255).astype(np.uint8)
    Image.fromarray(img_scaled).save(f'script/master_seg{idx}.png')
    decoded_imgs.append(img_scaled)

print("Saved all 4 master decoded images.")

# Now combine them!
# For a black-on-white image, min pixel value across segments:
combined = np.minimum.reduce(decoded_imgs)
Image.fromarray(combined).save('script/master_combined.png')

# Binary thresholded version
binaries = [(im < 128) for im in decoded_imgs]
combined_bin = np.where(np.any(binaries, axis=0), 0, 255).astype(np.uint8)
Image.fromarray(combined_bin).save('script/master_combined_bin.png')

print("Saved master_combined.png and master_combined_bin.png")
