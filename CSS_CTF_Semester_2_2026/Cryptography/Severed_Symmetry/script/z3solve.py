import json,z3,time
D=json.load(open('challenge/out.txt'))
ps=D['public_key']; p=17
x=[z3.Int(f'x{i}') for i in range(32)]
s=z3.Solver()
for v in x:s.add(v>=0,v<p)
for packed,y in zip(ps['polynomials'], D['ciphertext']['blocks'][0]):
    e=0
    for c,mon in packed:
        term=c
        for i in mon: term*=x[i]
        e+=term
    s.add(e%p==y)
print('solve')
t=time.time(); print(s.check(), time.time()-t)
if s.check()==z3.sat:
 print([s.model()[v] for v in x])
