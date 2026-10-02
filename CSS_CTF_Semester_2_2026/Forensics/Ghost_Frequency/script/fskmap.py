import wave,numpy as np,itertools
p='/home/light/Workspace/CTF/CSS_CTF_Semester_2_2026/Forensics/Ghost_Frequency/challenge/KBR17_blackbox.wav'
a=np.frombuffer(wave.open(p,'rb').readframes(5529608),dtype='<i2').reshape(-1,2)[:,1]
fs=48000
n=960
seq=[]
for i in range(0,len(a)-n,n):
 y=a[i:i+n]*np.hanning(n)
 sp=np.abs(np.fft.rfft(y)); fr=np.fft.rfftfreq(n,1/fs)
 m=(fr>500)&(fr<2600)
 f=round(fr[m][np.argmax(sp[m])]/100)*100
 seq.append(f)
syms=[600,1100,1200,1600,1700,1800,2200,2300]
print('len',len(seq))
for perm in itertools.permutations(range(8)):
 mp={syms[i]:format(perm[i],'03b') for i in range(8)}
 bits=''.join(mp.get(x,'000') for x in seq)
 for off in range(8):
  data=''.join(chr(int(bits[i:i+8],2)) for i in range(off,len(bits)-7,8))
  if 'CSS' in data or 'FLAG' in data or 'CTF' in data:
   print(mp,off,repr(data[:300]))
   found=True
   break
 else:
  found=False
 if found:
  break
print('done')
