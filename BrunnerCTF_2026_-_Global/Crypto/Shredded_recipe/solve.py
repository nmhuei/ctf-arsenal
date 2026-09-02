#!/usr/bin/env python3
import z3
v=open("crypto_shredded-recipe/output.txt").read().split();p,a,b,c,d=map(int,v)
s=z3.Solver();s.set(timeout=300000)
bs=[z3.Int("b%d"%i) for i in range(54)]
for q in bs:s.add(q>=32,q<=126)
for i,x in enumerate(b"brunner{"):s.add(bs[i]==x)
s.add(bs[53]==125)
x=sum(bs[i]*256**(17-i//3) for i in range(0,54,3));y=sum(bs[i]*256**(17-i//3) for i in range(1,54,3));z=sum(bs[i]*256**(17-i//3) for i in range(2,54,3))
s.add((a*x+b*y+c*z-d)%p==0)
print(s.check())
m=s.model();f=bytes([m[q].as_long() for q in bs]).decode();print("FLAG: "+f);open("flag.txt","w").write(f)
