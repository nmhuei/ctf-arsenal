import wave, numpy as np
from scipy.signal import find_peaks, stft
p='/home/light/Workspace/CTF/CSS_CTF_Semester_2_2026/Forensics/Ghost_Frequency/challenge/KBR17_blackbox.wav'
w=wave.open(p,'rb')
a=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').reshape(-1,2)
print(a.shape, a.min(axis=0), a.max(axis=0), np.std(a,axis=0))
for c in range(2):
 f,t,z=stft(a[:,c],fs=48000,nperseg=4096,noverlap=2048)
 mag=np.abs(z).mean(axis=1)
 peaks,_=find_peaks(mag,distance=10)
 top=peaks[np.argsort(mag[peaks])[-20:]]
 print('channel',c,'top freqs', sorted([(round(float(f[x]),1),round(float(mag[x]),1)) for x in top], key=lambda x:-x[1])[:10])
