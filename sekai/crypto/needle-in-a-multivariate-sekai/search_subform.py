import os, hashlib, random, time, sys
from sage.all import *
from sage.quadratic_forms.quadratic_form import QuadraticForm
pari.allocatemem(2**30)
os.chdir('crypto_needle-in-a-multivariate-sekai')
pk=load('pk.sobj')['pk']; R=matrix(ZZ, pari.qflllgram(pari(pk))); A=R.T*pk*R
n=144
t=Integer(int.from_bytes(b'\x01'+hashlib.sha256(b'STAGE OF SEKAI').digest(),'big'))

def makeQ(idx):
    coeff=[]; m=len(idx)
    for ii,i in enumerate(idx):
        coeff.append(QQ(A[i,i]))
        for jj in range(ii+1,m):
            j=idx[jj]; coeff.append(QQ(2*A[i,j]))
    return QuadraticForm(QQ,m,coeff)

def check(idx,x):
    D=lcm([a.denominator() for a in x])
    if D==1:
        y=vector(ZZ,n)
        for pos,val in zip(idx,x): y[pos]=ZZ(val)
        sig=R*y
        if sig*pk*sig==t:
            print('FOUND subset',idx)
            print('y nonzero',[ (i,int(y[i])) for i in range(n) if y[i] ])
            open('solution_subform.txt','w').write(' '.join(map(str,sig)))
            sys.exit(0)
    return D

# try contiguous, random short subsets
attempt=0
for m in [4,5,6,7,8,10,12]:
    for fixed in range(0,n-m+1):
        if attempt>1000: break
        idx=list(range(fixed,fixed+m)); attempt+=1
        try:
            Q=makeQ(idx); x=Q.solve(QQ(t)); D=check(idx,x)
            print('hit rational m',m,'idx',idx,'D bits',D.nbits())
        except Exception as e:
            pass
    print('done contig m',m,'attempt',attempt)

for m in [4,5,6,7,8,10,12,16]:
  for _ in range(2000):
    idx=sorted(random.sample(range(n),m)); attempt+=1
    try:
        Q=makeQ(idx); x=Q.solve(QQ(t)); D=check(idx,x)
        print('hit rational m',m,'D bits',D.nbits(),'idx',idx[:10])
    except Exception as e:
        pass
    if attempt%100==0: print('attempt',attempt,'m',m,flush=True)
print('not found')
