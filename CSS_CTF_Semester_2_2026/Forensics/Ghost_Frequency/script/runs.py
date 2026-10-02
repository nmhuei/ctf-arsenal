import wave,numpy as np
from collections import Counter
p='/home/light/Workspace/CTF/CSS_CTF_Semester_2_2026/Forensics/Ghost_Frequency/challenge/KBR17_blackbox.wav'
a=np.frombuffer(wave.open(p,'rb').readframes(5529608),dtype='<i2').reshape(-1,2)[:,1]
fs=48000;n=480;s=[]
for i in range(0,len(a)-n,n):
 y=a[i:i+n]*np.hanning(n); sp=np.abs(np.fft.rfft(y)); fr=np.fft.rfftfreq(n,1/fs); m=(fr>900)&(fr<2500); f=fr[m][np.argmax(sp[m])]; s.append(2300 if f>1700 else 1100)
r=[];cur=s[0];count=0
for x in s:
 if x==cur: count+=1
 else: r.append((cur,count));cur=x;count=1
r.append((cur,count));print(len(s),len(r));print(r[:100]);print(Counter(c for _,c in r).most_common(20))
