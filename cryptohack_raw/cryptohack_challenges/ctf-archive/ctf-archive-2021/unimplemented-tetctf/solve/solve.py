from pathlib import Path
from math import gcd, lcm
from collections import namedtuple

Complex = namedtuple('Complex', ['re','im'])

def complex_mult(c1,c2,mod):
    return Complex((c1.re*c2.re - c1.im*c2.im)%mod, (c1.re*c2.im + c1.im*c2.re)%mod)

def complex_pow(c,e,mod):
    res=Complex(1,0)
    while e:
        if e&1: res=complex_mult(res,c,mod)
        c=complex_mult(c,c,mod)
        e//=2
    return res

def unpad(data):
    assert b'\x00' in data
    return data.split(b'\x00',1)[1]

ns={}
exec(Path('/mnt/data/unimplemented-tetctf/files/output_f0813ec299f777b1ee2d3abe4d4e0df4.txt').read_text(), ns)
p,q=ns['private_key']; n=ns['public_key']; ct=ns['ciphertext']
L=(n.bit_length()+7)//8
c=Complex(int.from_bytes(ct[:L],'big'), int.from_bytes(ct[L:],'big'))
e=65537
lam=lcm(p*(p-1), q*(q*q-1))
print('gcd(e,lambda)=', gcd(e,lam))
d=pow(e,-1,lam)
m=complex_pow(c,d,n)
plen=2*((n.bit_length()-1)//8)
half=plen//2
pt = m.re.to_bytes(half,'big') + m.im.to_bytes(half,'big')
print('raw first zero index', pt.find(b'\x00'), 'len', len(pt))
flag=unpad(pt)
print(flag)
