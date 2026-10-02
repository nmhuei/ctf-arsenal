from sage.all import *
import json, time
pub=json.load(open('challenge/out.txt'))
p=GF(17)
pars=pub['public_key']['parameters']
polys=pub['public_key']['polynomials']
ct=pub['ciphertext']['blocks'][0]
R=PolynomialRing(p, 'x0,x1,x2,x3,x4,x5,x6,x7,x8,x9,x10,x11,x12,x13,x14,x15,x16,x17,x18,x19,x20,x21,x22,x23,x24,x25,x26,x27,x28,x29,x30,x31', order='degrevlex')
xs=R.gens()
eqs=[]
for packed,y in zip(polys,ct):
    f=R(0)
    for c,mon in packed:
        term=p(c)
        for i in mon: term*=xs[i]
        f+=term
    eqs.append(f-y)
print('start', time.time())
G=Ideal(eqs).groebner_basis()
print('done', time.time(), 'len', len(G))
print(G)
sol=[]
for g in G:
    if g.degree()==1: print(g)
