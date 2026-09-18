import numpy as np
import scipy.signal

data = np.memmap('challenge/Sideband_Surgery/challenge.raw', dtype=np.complex64, mode='r')
seg_len = 9338400

m0 = data[:seg_len].real - 0.5
fs = 240000

# Downsample to 48000 Hz for easier processing
decim = 5
fs_audio = fs // decim  # 48000 Hz
audio0 = scipy.signal.decimate(m0, decim)

# Save as WAV file to listen or analyze
import wave
audio_int16 = np.int16(audio0 / np.max(np.abs(audio0)) * 32767)
with wave.open('script/seg0.wav', 'w') as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(fs_audio)
    wf.writeframes(audio_int16.tobytes())

print(f"Saved script/seg0.wav ({len(audio0)/fs_audio:.2f} seconds)")

# Let's inspect the first 3 seconds of audio to find the VIS code
# In the first 3 seconds:
# Leader tone at 1900 Hz, Break at 1200 Hz, VIS bits around 1100/1300 Hz
t_slice = audio0[: 3 * fs_audio]

# Compute spectrogram with fine time resolution
f, t, Sxx = scipy.signal.spectrogram(t_slice, fs=fs_audio, nperseg=512, noverlap=256)

# Find peak frequency vs time
peak_freq = f[np.argmax(Sxx, axis=0)]

# Print time ranges where peak_freq is near 1900, 1200, 1100, 1300
print("Sample of peak frequencies in first 3 seconds:")
for time_idx in range(0, len(t), 20):
    print(f"  t = {t[time_idx]:.3f}s: freq = {peak_freq[time_idx]:.1f} Hz")
