import struct,hashlib
b=open('/tmp/Signal_Fracture_extract/KBR17_relay.img','rb').read()
i=0
while True:
 i=b.find(b'NXFR',i)
 if i<0: break
 if i+20<=len(b):
  m,s,q,t,l,c=struct.unpack('>4sIHHII',b[i:i+20]); p=b[i+20:i+20+l]
  if len(p)==l: print(i,q,hashlib.sha256(p).hexdigest(),l)
 i+=1
