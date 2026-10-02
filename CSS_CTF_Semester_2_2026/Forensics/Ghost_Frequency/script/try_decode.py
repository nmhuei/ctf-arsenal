import wave,numpy as np,string
p='/home/light/Workspace/CTF/CSS_CTF_Semester_2_2026/Forensics/Ghost_Frequency/challenge/KBR17_blackbox.wav'
a=np.frombuffer(wave.open(p,'rb').readframes(5529608),dtype='<i2').reshape(-1,2)[:,1]
fs=48000
for ms in [5,10,12,15,20,25,30,40,50,60,80,100]:
 n=int(fs*ms/1000); tones=[]
 for i in range(0,len(a)-n,n):
  y=a[i:i+n]*np.hanning(n); sp=np.abs(np.fft.rfft(y)); fr=np.fft.rfftfreq(n,1/fs); m=(fr>900)&(fr<2500); f=fr[m][np.argmax(sp[m])]
  tones.append(1 if f>1700 else 0)
 for inv in [0,1]:
  b=''.join(str(x^inv) for x in tones)
  for rev in [0,1]:
   bb=b[::-1] if rev else b
   for off in range(8):
    data=''.join(chr(int(bb[i:i+8],2)) for i in range(off,len(bb)-7,8))
    score=sum(c in string.printable for c in data[:300])/max(1,len(data[:300]))
    if 'CSS' in data or 'FLAG' in data or score>.95:
     print(ms,inv,rev,off,score,repr(data[:200]))
