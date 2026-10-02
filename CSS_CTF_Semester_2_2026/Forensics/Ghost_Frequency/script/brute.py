import wave,numpy as np
p='/home/light/Workspace/CTF/CSS_CTF_Semester_2_2026/Forensics/Ghost_Frequency/challenge/KBR17_blackbox.wav'
w=wave.open(p,'rb'); a=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').reshape(-1,2)[:,0]
fs=48000
s=[]
for i in range(0,len(a)-240,240):
 x=a[i:i+240]*np.hanning(240); sp=np.abs(np.fft.rfft(x)); fr=np.fft.rfftfreq(240,1/fs); m=(fr>800)&(fr<2500); f=fr[m][np.argmax(sp[m])]
 s.append(1 if f>1500 else 0)
for start in range(0,2000,10):
 for n in [2,3,4,5,6,8,10]:
  bits=''.join(str(round(sum(s[i:i+n])/n)) for i in range(start,len(s)-n,n))
  data=''.join(chr(int(bits[i:i+8],2)) for i in range(0,len(bits)-7,8))
  if any(x in data for x in ['CSS','FLAG','CTF']): print(start,n,data)
print('finished')
