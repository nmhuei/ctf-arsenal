from sage.all import ZZ, QQ, matrix, prod, lcm
from pathlib import Path
from zipfile import ZipFile
import json, time
root=Path(__file__).resolve().parents[1]
N=ZZ(json.loads((root/'script/modulus.json').read_text())['N'])
with ZipFile(root/'challenge/here') as z:
 samples=json.loads(z.read('chimera_student/output_chimera.txt'))['attestations']
A=matrix(QQ, [[1]+[(c>>j)&1 for j in range(128)] for c,v in samples[:129]])
print('matrix rank',A.rank(),flush=True)
inv=A.inverse()
token=0;t=time.time()
for j in range(128):
 row=inv[j+1];d=row.denominator();weights=[ZZ(v*d) for v in row]
 y=ZZ(1)
 for w,(_,v) in zip(weights,samples):y=y*pow(ZZ(v),w,N)%N
 positive=pow(ZZ(3),ZZ(d)*2**j,N)
 negative=pow(positive,-1,N)
 assert positive!=negative
 if y==negative:token|=1<<j
 else:assert y==positive,(j,y)
print('token',token,'seconds',time.time()-t,flush=True)
assert all(pow(3,token^c,N)==v for c,v in samples)
(root/'script/token.json').write_text(json.dumps({'token':token,'verified_samples':len(samples)}))
print('verified all',len(samples),'attestations',flush=True)
