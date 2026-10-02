import wave,numpy as np
p='/home/light/Workspace/CTF/CSS_CTF_Semester_2_2026/Forensics/Ghost_Frequency/challenge/KBR17_blackbox.wav'
w=wave.open(p,'rb'); a=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').reshape(-1,2)[:,0]
fs=48000
def tone(t0,ms=30):
 x=a[int(t0*fs/1000):int((t0+ms)*fs/1000)]*np.hanning(int(ms*fs/1000)); sp=np.abs(np.fft.rfft(x)); fr=np.fft.rfftfreq(len(x),1/fs); m=(fr>800)&(fr<2300); return round(fr[m][np.argmax(sp[m])])
for base in [900,1200,1500,1800,2100,2400,2700,3000,3300,3600,3900]:
 print(base,[tone(base+i*30) for i in range(10)])
