from sage.all import ZZ, matrix, identity_matrix, gcd, prime_range
from zipfile import ZipFile
import json, time
from pathlib import Path
root=Path(__file__).resolve().parents[1]
with ZipFile(root/'challenge/here') as z:
 data=json.loads(z.read('chimera_student/output_chimera.txt'))
samples=data['attestations']
# Integer relations cancel every bit of token XOR challenge, including its constant.
A=matrix(ZZ, [[1]+[(c>>j)&1 for j in range(128)] for c,v in samples])
B=identity_matrix(ZZ,len(samples)).augment(A*2**32)
t=time.time()
print('LLL start',B.dimensions(),flush=True)
R=B.LLL()
relations=[list(row[:len(samples)]) for row in R if not any(row[len(samples):])]
print('relations',len(relations),'seconds',time.time()-t,flush=True)
N=ZZ(0)
for i,rel in enumerate(relations):
 assert not any(matrix(ZZ,[rel])*A)
 left=ZZ(1); right=ZZ(1)
 for w,(_,v) in zip(rel,samples):
  if w>0: left*=ZZ(v)**w
  elif w<0: right*=ZZ(v)**(-w)
 N=gcd(N,left-right)
 if i>=1:
  for ell in prime_range(10000):
   while N % ell == 0: N //= ell
 print('gcd',i,'bits',N.nbits(),'maxcoeff',max(abs(w) for w in rel),flush=True)
 if N.nbits()==768:
  break
assert N.nbits()==768
assert all(v<N for _,v in samples)
(root/'script/modulus.json').write_text(json.dumps({'N':int(N),'relations':[[int(x) for x in row] for row in relations]},indent=2))
print('N =',N,flush=True)
