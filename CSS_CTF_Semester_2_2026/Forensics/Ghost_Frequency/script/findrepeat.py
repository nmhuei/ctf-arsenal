from collections import Counter
import wave,numpy as np
p='/home/light/Workspace/CTF/CSS_CTF_Semester_2_2026/Forensics/Ghost_Frequency/challenge/KBR17_blackbox.wav'
a=np.frombuffer(wave.open(p,'rb').readframes(5529608),dtype='<i2').reshape(-1,2)[:,1]
fs=48000;n=960;s=[]
for i in range(0,len(a)-n,n):
 y=a[i:i+n]*np.hanning(n);sp=np.abs(np.fft.rfft(y));fr=np.fft.rfftfreq(n,1/fs);m=(fr>500)&(fr<2600);s.append(round(fr[m][np.argmax(sp[m])]/100)*100)
# ignore leading silence and use all
for L in [50,60,70,80,100,120]:
 c=Counter(tuple(s[i:i+L]) for i in range(len(s)-L) if 600 not in s[i:i+L])
 print(L,c.most_common(2))
