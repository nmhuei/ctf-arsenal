import numpy as np
import scipy.signal

data = np.memmap('challenge/Sideband_Surgery/challenge.raw', dtype=np.complex64, mode='r')

seg_len = 9338400

# Let's inspect each segment
for i in range(4):
    seg = data[i*seg_len : (i+1)*seg_len]
    print(f"\n================ SEGMENT {i} ================")
    # Look at a short slice: 100000 samples
    chunk = seg[1000000:1100000]
    
    # Check if amplitude is constant or varying
    amp = np.abs(chunk)
    print(f"Amplitude min={amp.min():.4f}, max={amp.max():.4f}, std={amp.std():.4f}")
    
    # Instantaneous frequency: angle(chunk[1:] * conj(chunk[:-1]))
    # Only for complex
    phase_diff = np.angle(chunk[1:] * np.conj(chunk[:-1]))
    inst_freq = phase_diff / (2 * np.pi)
    print(f"Inst freq: mean={inst_freq.mean():.6f}, std={inst_freq.std():.6f}, min={inst_freq.min():.6f}, max={inst_freq.max():.6f}")
    
    # Check spectrogram of 200,000 samples to see if frequency changes over time
    f, t, Sxx = scipy.signal.spectrogram(chunk, fs=1.0, nperseg=1024, noverlap=512, return_onesided=False)
    # Average power over time
    mean_spec = np.mean(np.abs(Sxx), axis=1)
    top_f_idx = np.argsort(mean_spec)[-5:][::-1]
    print("Dominant frequencies in spectrogram slice:")
    for idx in top_f_idx:
        print(f"  f = {f[idx]:.6f}, power = {mean_spec[idx]:.4f}")
