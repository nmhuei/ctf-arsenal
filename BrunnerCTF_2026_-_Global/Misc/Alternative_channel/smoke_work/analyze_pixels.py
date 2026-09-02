from PIL import Image
import numpy as np

p='smoke_work/misc_alternative-channel/alternative_channel.png'
a=np.array(Image.open(p).convert('RGB'))
print('shape:',a.shape)
for i,name in enumerate('RGB'):
 x=a[:,:,i]
 print(name,"min=",x.min(),"max=",x.max(),"unique=",len(np.unique(x)),"mean=",round(float(x.mean()),2),"std=",round(float(x.std()),2))
 vals,cnt=np.unique(x&1,return_counts=True)
 print(" LSB counts:",dict(zip(vals.tolist(),cnt.tolist())))
for i,name in enumerate('RGB'):
 for bit in range(8):
 plane=((a[:,:,i]>>bit)&1)*255
 Image.fromarray(plane.astype(np.uint8)).save(f"smoke_work/{name}_bit{bit}.png")
for xname,x in [('R_xor_G',a[:,:,0]^a[:,:,1]),('R_xor_B',a[:,:,0]^a[:,:,2]),('G_xor_B',a[:,:,1]^a[:,:,2])]:
 Image.fromarray(x.astype(np.uint8)).save(f"smoke_work/{xname}.png")
 print(xname,"unique=",len(np.unique(x)),"nonzero=",int(np.count_nonzero(x)))
print('saved bit planes and xor images')
