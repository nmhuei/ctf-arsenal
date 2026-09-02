#!/usr/bin/env python3
import json,re,socket,time
from cryptography.hazmat.primitives.ciphers import Cipher,algorithms,modes
B=1<<128
class J:
 def __init__(s,h,p,t=20): s.s=socket.create_connection((h,p),timeout=t); s.s.settimeout(t); s.b=b''
 def rs(s,w=2):
  e=time.time()+w; o=[]
  while time.time()<e:
   try:
    d=s.s.recv(4096)
    if not d: break
    o.append(d); s.b+=d
    if b'}\n' in s.b or b'}\r\n' in s.b: break
   except socket.timeout: break
  return b''.join(o)
 def sj(s,o): s.s.sendall(json.dumps(o,separators=(',',':')).encode()+b'\n')
 def rj(s):
  while b'\n' not in s.b: s.b+=s.s.recv(4096)
  l,s.b=s.b.split(b'\n',1)
  while l and not l.lstrip().startswith(b'{'):
   while b'\n' not in s.b: s.b+=s.s.recv(4096)
   l,s.b=s.b.split(b'\n',1)
  return json.loads(l)
def dec(k,c):
 d=Cipher(algorithms.AES(k),modes.ECB()).decryptor(); return d.update(c)+d.finalize()
def unpad(x):
 k=x[-1]
 if not(1<=k<=16 and x[-k:]==bytes([k])*k): raise ValueError('pad')
 return x[:-k]
def l2b(n,nl=None):
 s=b'\0' if n==0 else n.to_bytes((n.bit_length()+7)//8,'big')
 return s if nl is None else s.rjust(nl,b'\0')
def inv(a,m): return pow(a,-1,m)
def fmt(n):
 nb=l2b(n); return len(nb).to_bytes(2,'big')+nb
def solve(h='socket.cryptohack.org',p=13410):
 j=J(h,p,30)
 ban=j.rs(2).decode(errors='replace'); print(ban,end='')
 mat,up,rec=[json.loads(x) for x in re.findall(r'(?m)^\{.*\}$',ban)]
 n,e,pv=rec['share_key']; q=n//pv; phi=(pv-1)*(q-1); d=inv(e,phi); u=inv(pv,q)
 ulen=len(l2b(u)); qbytes=l2b(q,ulen); ubytes=l2b(u,ulen)
 fd=next(i for i,(a,b) in enumerate(zip(ubytes,qbytes)) if a!=b)
 pt=fmt(pv)+fmt(q)+fmt(d)+fmt(u)
 idx=0; bd={}
 for nm,val in [('p',pv),('q',q),('d',d),('u',u)]:
  nb=l2b(val); bd[nm]=(idx,idx+2+len(nb),len(nb)); idx+=2+len(nb)
 us,ue,_=bd['u']; ds=us+2; chosen=None
 for blk in range((idx+15)//16):
  s=blk*16; ee=s+16; rel=s-ds
  if s>=ds and ee<=ue and rel>fd:
   chosen=blk; break
 assert chosen is not None
 sk=bytes.fromhex(mat['share_key_enc']); blklist=[sk[i:i+16] for i in range(0,len(sk),16)]
 blklist[chosen]=bytes.fromhex(up['node_key_enc'])
 modshare=b''.join(blklist).hex()
 j.b=b''; j.sj({'action':'wait_login'}); print('[+] wait_login',j.rj())
 c=2
 while True:
  mp=pow(c,d%(pv-1),pv); mq=pow(c,d%(q-1),q); t=(mq-mp)%q
  if t: break
  c+=1
 j.sj({'action':'send_challenge','SID_enc':l2b(c,256).hex(),'share_key_enc':modshare,'master_key_enc':mat['master_key_enc']})
 r=j.rj(); print('[+] send_challenge',r)
 Y=int(r['SID'],16) if r['SID'] else 0
 x=(mp-(Y<<128))%pv; assert x < B
 y=(Y<<128)+x
 umod=((y-mp)//pv)*inv(t,q)%q
 off=chosen*16-ds; lim=1<<(8*ulen)
 for cand in [umod, umod+q]:
  if cand>=lim: continue
  ub=l2b(cand,ulen); node=ub[off:off+16]
  try:
   filept=unpad(dec(node,bytes.fromhex(up['file_enc'])))
   print('[+] node_key',node.hex())
   print('[+] file',filept.decode(errors='replace'))
   m=re.search(rb'crypto\{[^}]+\}',filept)
   print('FLAG:',m.group().decode() if m else 'FLAG_NOT_FOUND')
   return
  except Exception:
   pass
 raise Exception('node key recovery failed')
if __name__=='__main__': solve()
