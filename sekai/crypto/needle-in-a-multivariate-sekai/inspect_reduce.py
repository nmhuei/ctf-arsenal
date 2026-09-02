import os, ast
from sage.all import *
os.chdir('crypto_needle-in-a-multivariate-sekai')
pk=load('pk.sobj')['pk']
print('start')
Gp = pari(pk)
R = pari.qflllgram(Gp)  # transformation? maybe columns
print(type(R), R.matsize())
RZ = matrix(ZZ, R)
print('R dims',RZ.dimensions(), 'det', RZ.det())
for expr,name in [(RZ*pk*RZ.transpose(),'RpkRt'),(RZ.transpose()*pk*RZ,'RtpkR')]:
 d=[expr[i,i].nbits() for i in range(144)]
 print(name,min(d),max(d),d[:20])
 print('sym',expr==expr.transpose())
