import os, hashlib, sys
from sage.all import *
from sage.quadratic_forms.quadratic_form import QuadraticForm
pari.allocatemem(2**31)
os.chdir('crypto_needle-in-a-multivariate-sekai')
pk=load('pk.sobj')['pk']; R=matrix(ZZ, pari.qflllgram(pari(pk))); A=R.T*pk*R
n=144
t=Integer(int.from_bytes(b'\x01'+hashlib.sha256(b'STAGE OF SEKAI').digest(),'big'))
coeff=[]
for i in range(n):
    coeff.append(QQ(A[i,i]))
    for j in range(i+1,n): coeff.append(QQ(2*A[i,j]))
Q=QuadraticForm(QQ, n, coeff)
e=vector(QQ,[1]+[0]*(n-1))
print('check e', Q(e)==A[0,0])
print('solve')
x=Q.solve(QQ(t))
print('got')
D=lcm([a.denominator() for a in x]); print('D bits',D.nbits(),'allint',D==1)
print('val ok',Q(x)==t)
print('first',x[:10])
if D==1:
 y=vector(ZZ,x); sig=R*y; print('verify', sig*pk*sig==t); open('solution_from_qfsolve.txt','w').write(' '.join(map(str,sig)))
else:
 open('qfsolve_rational.txt','w').write(str(list(x)))
