import wave,numpy as np,string
p='/home/light/Workspace/CTF/CSS_CTF_Semester_2_2026/Forensics/Ghost_Frequency/challenge/KBR17_blackbox.wav'
w=wave.open(p,'rb'); a=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').reshape(-1,2)[:,0]
fs=48000
for ms in [5,10,15,20,25,30,40]:
 n=fs*ms//1000; s=[]
 for i in range(0,len(a)-n,n):
  x=a[i:i+n]*np.hanning(n); sp=np.abs(np.fft.rfft(x)); fr=np.fft.rfftfreq(n,1/fs); m=(fr>800)&(fr<2500); f=fr[m][np.argmax(sp[m])]
  s.append('1' if f>1500 else '0')
 for inv in [False,True]:
  b=''.join('1' if (c=='0')==inv else '0' for c in s)
  for off in range(8):
   data=''.join(chr(int(b[i:i+8],2)) for i in range(off,len(b)-7,8))
   printable=''.join(c if c in string.printable else '.' for c in data[:200])
   if sum(c.isalnum() or c in '{}_' for c in data)/max(1,len(data))>.7:
    print(ms,inv,off,printable)
