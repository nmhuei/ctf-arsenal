#!/usr/bin/env python3
import json,re,socket,time,random,math,hashlib
from decimal import Decimal,getcontext
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
def pmat(t):
 s=t.decode(errors='replace')
 for l in s.splitlines():
  l=l.strip()
  if l.startswith('{') and 'share_key_enc' in l: return json.loads(l)
 return json.loads(re.search(r'\{.*share_key_enc.*\}',s,re.S).group(0))
def l2b(n): return b'\0' if n==0 else n.to_bytes((n.bit_length()+7)//8,'big')
def unpad(d): return d[:-d[-1]]
def decaes(k,c):
 try:
  from Crypto.Cipher import AES
  return AES.new(k,AES.MODE_ECB).decrypt(c)
 except:
  from cryptography.hazmat.primitives.ciphers import Cipher,algorithms,modes
  z=Cipher(algorithms.AES(k),modes.ECB()).decryptor(); return z.update(c)+z.finalize()
def lll(Bv,delta=Decimal('0.75'),prec=900):
 getcontext().prec=prec;Bv=[list(map(int,r)) for r in Bv];n=len(Bv);m=len(Bv[0])
 def gs():
  bs=[[Decimal(0)]*m for _ in range(n)];mu=[[Decimal(0)]*n for _ in range(n)];no=[Decimal(0)]*n
  for i in range(n):
   bs[i]=[Decimal(z) for z in Bv[i]]
   for j in range(i):
    if no[j]!=0:
     mu[i][j]=sum(Decimal(Bv[i][k])*bs[j][k] for k in range(m))/no[j]
     if mu[i][j]:
      for k in range(m): bs[i][k]-=mu[i][j]*bs[j][k]
   no[i]=sum(z*z for z in bs[i])
  return mu,no
 k=1;mu,no=gs();it=0
 while k<n:
  it+=1
  for j in range(k-1,-1,-1):
   q=int(mu[k][j].to_integral_value(rounding='ROUND_HALF_EVEN'))
   if q:
    Bv[k]=[Bv[k][i]-q*Bv[j][i] for i in range(m)];mu,no=gs()
  if no[k]>=(delta-mu[k][k-1]*mu[k][k-1])*no[k-1]: k+=1
  else: Bv[k],Bv[k-1]=Bv[k-1],Bv[k];mu,no=gs();k=max(k-1,1)
  if it>10000: raise Exception('lll')
 return Bv
def cfac(M,N):
 R=[[N*N,0,0,0],[N*M,N*B,0,0],[M*M,2*M*B,B*B,0],[0,M*M*B,2*M*B*B,B*B*B]]
 import sympy as sp
 x=sp.symbols('x')
 for r in lll(R):
  c=[r[i]//(B**i) for i in range(4)]
  while c and c[-1]==0: c.pop()
  if len(c)<=1: continue
  p=sp.Poly(sum(int(c[i])*x**i for i in range(len(c))),x,domain=sp.ZZ); rt=[]
  if p.degree()==1:
   a,b=p.nth(1),p.nth(0)
   if a and (-b)%a==0: rt=[int((-b)//a)]
  try: rt+=[int(z) for z in p.ground_roots().keys()]
  except: pass
  for z in rt:
   if 0<=z<B:
    g=math.gcd(M+z,N)
    if 1<g<N: return g
 raise Exception('cfac')
def solve(h='socket.cryptohack.org',p=13409):
 j=J(h,p,30); ban=j.rs(2); print(ban.decode(errors='replace'),end=''); m=pmat(ban); j.b=b''
 n,e=map(int,m['share_key_pub']); raw=bytes.fromhex(m['share_key_enc']); blk=[raw[i:i+16] for i in range(0,len(raw),16)]; idx=list(range(41)); idx[9]=1
 j.sj({'action':'wait_login'}); print('[+] wait_login',j.rj())
 s=random.randrange(1<<500,1<<501); c=pow(s,e,n)
 j.sj({'action':'send_challenge','SID_enc':l2b(c).rjust(256,b'\0').hex(),'share_key_enc':b''.join(blk[i] for i in idx).hex(),'master_key_enc':m['master_key_enc']})
 r=j.rj(); print('[+] send_challenge',r)
 Y=int(r['SID'],16) if r['SID'] else 0; P=cfac(Y*B-s,n); Q=n//P
 print('[+] factors ok',P*Q==n)
 j.sj({'action':'get_encrypted_flag'}); ef=bytes.fromhex(j.rj()['encrypted_flag'])
 for a,b in [(P,Q),(Q,P)]:
  k=hashlib.sha256(l2b(a)+l2b(b)).digest()
  try: pt=unpad(decaes(k,ef))
  except: continue
  if pt.startswith(b'crypto{') and pt.endswith(b'}'):
   print('[+] encrypted_flag',ef.hex());print('[+] key',k.hex());print('FLAG:',pt.decode());return
 raise Exception('flag')
if __name__=='__main__': solve()
