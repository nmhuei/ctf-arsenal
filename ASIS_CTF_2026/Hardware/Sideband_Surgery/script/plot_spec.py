import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import scipy.signal

data = np.memmap('challenge/Sideband_Surgery/challenge.raw', dtype=np.complex64, mode='r')
seg_len = 9338400

m0 = data[:seg_len].real - 0.5

# Let's plot a spectrogram of m0 for samples 0 to 1,000,000
plt.figure(figsize=(12, 6))
f, t, Sxx = scipy.signal.spectrogram(m0[100000:600000], fs=1.0, nperseg=2048, noverlap=1024)
# keep only f between 0.005 and 0.012
mask = (f >= 0.005) & (f <= 0.012)
plt.pcolormesh(t, f[mask], 10 * np.log10(Sxx[mask, :] + 1e-12), shading='gouraud', cmap='viridis')
plt.ylabel('Frequency (f/fs)')
plt.xlabel('Time (samples)')
plt.title('Spectrogram of m0 [100k : 600k]')
plt.colorbar(label='dB')
plt.savefig('script/spectrogram_m0.png', dpi=150)
plt.close()
print("Saved script/spectrogram_m0.png")
