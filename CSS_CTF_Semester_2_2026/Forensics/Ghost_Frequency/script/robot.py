import wave, numpy as np
from PIL import Image
p='/home/light/Workspace/CTF/CSS_CTF_Semester_2_2026/Forensics/Ghost_Frequency/challenge/KBR17_blackbox.wav'
w=wave.open(p,'rb'); a=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').reshape(-1,2)[:,0]
fs=48000
# estimate intensity from 1500-2300 Hz tone
def val(pos,dur):
 start=int(pos*fs); end=int((pos+dur)*fs); x=a[start:end]; n=len(x); x=x*np.hanning(n); sp=np.abs(np.fft.rfft(x)); fr=np.fft.rfftfreq(n,1/fs)
 target=(fr>1300)&(fr<2400); f=fr[target][np.argmax(sp[target])]
 return max(0,min(255,int((f-1500)/800*255)))
# after VIS stop around 910ms + gap; find lines
start=0.94
W,H=320,240
rows=[]
line=start
for y in range(H):
    # sync+porch
    line+=0.012
    g=[val(line+i*0.001,0.001) for i in range(88)]
    line+=0.091
    line+=0.004
    b=[val(line+i*0.001,0.001) for i in range(44)]
    line+=0.047
    line+=0.004
    r=[val(line+i*0.001,0.001) for i in range(44)]
    line+=0.047
    # duplicate chroma to width
    def exp(x):
        return np.interp(np.linspace(0,len(x)-1,W),np.arange(len(x)),x)
    Y=exp(g); B=exp(b); R=exp(r)
    # crude YUV
    rows.append(np.stack([R,Y,B],1).astype('uint8'))
img=Image.fromarray(np.array(rows))
img.save('/home/light/Workspace/CTF/CSS_CTF_Semester_2_2026/Forensics/Ghost_Frequency/script/robot.png')
print('saved',line)
