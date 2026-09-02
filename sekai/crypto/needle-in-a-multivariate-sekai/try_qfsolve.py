import os, hashlib, sys
from sage.all import *
from sage.quadratic_forms.quadratic_form import QuadraticForm
os.chdir('crypto_needle-in-a-multivariate-sekai')
pk=load('pk.sobj')['pk']; R=matrix(ZZ, pari.qflllgram(pari(pk))); A=R.T*pk*R
n=144
t=Integer(int.from_bytes(b'\x01'+hashlib.sha256(b'STAGE OF SEKAI').digest(),'big'))
print('build QF')
# try QuadraticForm from matrix? 
Q=QuadraticForm(QQ, A)
print('Q dim',Q.dim())
e=vector(QQ,[1]+[0]*(n-1))
print('check e',Q(e), A[0,0])
print('solve')
x=Q.solve(QQ(t))
print('got', type(x), len(x), x[:5])
print('den lcm bits', lcm([a.denominator() for a in x]).nbits())
val=Q(x); print('val ok', val==t)
# check integer?
print('all int', all(a.denominator()==1 for a in x))
if all(a.denominator()==1 for a in x):
 y=vector(ZZ,x); sig=R*y; print('verify', sig*pk*sig==t); open('solution_from_qfsolve.txt','w').write(' '.join(map(str,sig)))
