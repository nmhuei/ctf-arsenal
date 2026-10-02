import wave,numpy as np,itertools,string
from collections import Counter
p='/home/light/Workspace/CTF/CSS_CTF_Semester_2_2026/Forensics/Ghost_Frequency/challenge/KBR17_blackbox.wav'
a=np.frombuffer(wave.open(p,'rb').readframes(5529608),dtype='<i2').reshape(-1,2)[:,1]
fs=48000;n=960;seq=[]
for i in range(0,len(a)-n,n):
 y=a[i:i+n]*np.hanning(n);sp=np.abs(np.fft.rfft(y));fr=np.fft.rfftfreq(n,1/fs);m=(fr>500)&(fr<2600);seq.append(round(fr[m][np.argmax(sp[m])]/100)*100)
# take active data
seq=[x for x in seq if x!=600]
print('active',len(seq),seq[:30])
syms=[x for x,_ in Counter(seq).most_common(8)];print('syms',syms)
for start in range(0,50):
 chunk=seq[start:start+40]
 if len(chunk)<40: continue
 for perm in itertools.permutations(range(8)):
  mp={syms[i]:format(perm[i],'03b') for i in range(8)}
  bits=''.join(mp[x] for x in chunk)
  for off in range(8):
   data=''.join(chr(int(bits[i:i+8],2)) for i in range(off,len(bits)-7,8))
   score=sum(c in string.ascii_letters+string.digits+'{}_-' for c in data)/len(data)
   if score>0.9:
    print('candidate',start,off,score,mp,repr(data))
print('done')
