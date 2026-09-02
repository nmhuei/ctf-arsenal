import os, sys
sys.path.append('/mnt/data/sratslla/sratslla-sea-hkcert-ctf/files')
from aes import AES
no_op=lambda *x: None

def enc_actual(k,p,mode):
 c=AES(k)
 if mode=='ark': c._add_round_key=no_op
 if mode=='sb': c._sub_bytes=no_op
 if mode=='sr': c._shift_rows=no_op
 if mode=='mc': c._mix_columns=no_op
 return c.encrypt(p)

def inv_ark(ct):
 c=AES(b'\0'*16); c._add_round_key=no_op
 return c.decrypt(ct)

def inv_sb_linear(y):
 # y = E_k(P)^E_k(0), no subbytes. Use zero-key no-sub cipher to invert linear layer.
 c=AES(b'\0'*16); c._sub_bytes=no_op; c._inv_sub_bytes=no_op
 offset=c.encrypt(b'\0'*16)
 return c.decrypt(bytes(a^b for a,b in zip(y, offset)))

def recover(k):
 # ark secret
 p0=b''.join(k[i:i+1]*4 for i in range(4))
 c0=enc_actual(k,p0,'ark')
 r0=inv_ark(c0)
 print('ark block plaintext',r0.hex(), 'chunk', r0[0],r0[4],r0[8],r0[12])
 # wait p0 = k0*4 k1*4 k2*4 k3*4 -> bytes 0-3 all k0, 4-7 all k1
 k0=bytes([r0[0], r0[4], r0[8], r0[12]])
 # sb data0 and secret
 c00=enc_actual(k,b'\0'*16,'sb')
 p1=b''.join(k[i:i+1]*4 for i in range(4,8))
 c1=enc_actual(k,p1,'sb')
 y=bytes(a^b for a,b in zip(c1,c00))
 r1=inv_sb_linear(y)
 k1=bytes([r1[0],r1[4],r1[8],r1[12]])
 print('sb plaintext',r1.hex(), 'chunk', k1.hex())
 return k0+k1
if __name__=='__main__':
 k=os.urandom(16)
 print('key',k.hex())
 print('rec first8',recover(k).hex())
