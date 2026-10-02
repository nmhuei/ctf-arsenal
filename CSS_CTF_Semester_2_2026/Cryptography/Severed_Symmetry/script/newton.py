import json, random
D=json.load(open('challenge/out.txt')); polys=D['public_key']['polynomials']; c=D['ciphertext']['blocks'][0]; p=17

def calc(x):
 y=[]; J=[]
 for poly in polys:
  s=0; row=[0]*32
  for co,mo in poly:
   t=co
   for i in mo:t*=x[i]
   s+=t
   if len(mo)==1: row[mo[0]]+=co
   elif len(mo)==2 and mo[0]==mo[1]: row[mo[0]]+=2*co*x[mo[0]]
   elif len(mo)==2: row[mo[0]]+=co*x[mo[1]]; row[mo[1]]+=co*x[mo[0]]
  y.append(s%p); J.append([z%p for z in row])
 return y,J

def lin(A,b):
 A=[[(v%p) for v in r]+[bb%p] for r,bb in zip(A,b)]; r=0; piv=[]
 for col in range(32):
  q=next((i for i in range(r,len(A)) if A[i][col]),None)
  if q is None: continue
  A[r],A[q]=A[q],A[r]; inv=pow(A[r][col],-1,p); A[r]=[v*inv%p for v in A[r]]
  for i in range(len(A)):
   if i!=r and A[i][col]:
    f=A[i][col]; A[i]=[(a-f*b)%p for a,b in zip(A[i],A[r])]
  piv.append(col); r+=1
 if any(not any(row[:32]) and row[32] for row in A): return None
 x=[0]*32
 for i,col in enumerate(piv): x[col]=A[i][32]
 return x
for a in range(200):
 x=[random.randrange(p) for _ in range(32)]
 for i in range(50):
  y,J=calc(x)
  if y==c: print(x); raise SystemExit
  d=lin(J,[(u-v)%p for u,v in zip(c,y)])
  if d is None: break
  x=[(u+v)%p for u,v in zip(x,d)]
print('no')
