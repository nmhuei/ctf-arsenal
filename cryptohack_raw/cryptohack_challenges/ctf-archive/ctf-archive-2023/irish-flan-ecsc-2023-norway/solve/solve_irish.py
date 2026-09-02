#!/usr/bin/env python3
import re, ast, hashlib, math
from pathlib import Path
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

OUT = Path(__file__).parent/'../files/output_258aece3f0028897e45f735c1a500fdf.txt'
if not OUT.exists():
    OUT = Path('output_258aece3f0028897e45f735c1a500fdf.txt')

class Q:
    __slots__=('a','b','c','d','n')
    def __init__(self,a,b,c,d,n):
        self.n=n; self.a=a%n; self.b=b%n; self.c=c%n; self.d=d%n
    def tup(self): return (self.a,self.b,self.c,self.d)
    def __add__(self,o): return Q(self.a+o.a,self.b+o.b,self.c+o.c,self.d+o.d,self.n)
    def __sub__(self,o): return Q(self.a-o.a,self.b-o.b,self.c-o.c,self.d-o.d,self.n)
    def __neg__(self): return Q(-self.a,-self.b,-self.c,-self.d,self.n)
    def __mul__(self,o):
        n=self.n
        if isinstance(o,int): return Q(self.a*o,self.b*o,self.c*o,self.d*o,n)
        a,b,c,d=self.a,self.b,self.c,self.d
        e,f,g,h=o.a,o.b,o.c,o.d
        return Q(a*e-b*f-c*g-d*h,
                 a*f+b*e+c*h-d*g,
                 a*g-b*h+c*e+d*f,
                 a*h+b*g-c*f+d*e,n)
    def inv(self):
        n=self.n
        norm=(self.a*self.a+self.b*self.b+self.c*self.c+self.d*self.d)%n
        invnorm=pow(norm,-1,n)
        return Q(self.a*invnorm,-self.b*invnorm,-self.c*invnorm,-self.d*invnorm,n)
    def __eq__(self,o): return self.tup()==o.tup() and self.n==o.n
    def __str__(self):
        n=self.n
        return f"({self.a} (mod {n}),{self.b} (mod {n}),{self.c} (mod {n}),{self.d} (mod {n}))"

def parse_output(path):
    s=Path(path).read_text()
    n=int(re.search(r'Public key:\s*(\d+),',s).group(1))
    coeffs=[int(x) for x in re.findall(r'(\d+) \(mod '+re.escape(str(n))+r'\)',s)]
    assert len(coeffs)==20, len(coeffs)
    alpha=Q(*coeffs[0:4],n)
    beta =Q(*coeffs[4:8],n)
    gamma=Q(*coeffs[8:12],n)
    mu   =Q(*coeffs[12:16],n)
    eps  =Q(*coeffs[16:20],n)
    idx=s.index('Encryption: ')+len('Encryption: ')
    ct=None
    for end in range(idx+2, min(len(s),idx+1000)):
        if s[end:end+2]==',(':
            try:
                val=ast.literal_eval(s[idx:end])
                if isinstance(val, bytes):
                    ct=val; break
            except Exception:
                pass
    assert ct is not None
    return n,alpha,beta,gamma,ct,mu,eps

def find_delta(n, alpha, gamma, eps):
    # δ is a power of γ, hence δ ∈ span(1,γ): δ = A + Bγ.
    one=Q(1,0,0,0,n)
    U=(alpha-eps).tup()             # coefficients of A
    V=(alpha*gamma - gamma*eps).tup() # coefficients of B
    # Need A*U_i + B*V_i = 0 mod n. Try A=1 where V_i is invertible.
    for ui,vi in zip(U,V):
        g=math.gcd(vi,n)
        if g==1:
            t=(-ui*pow(vi,-1,n))%n
            delta=one + gamma*t
            if alpha*delta == delta*eps:
                return delta, ('A=1', t)
        elif 1<g<n:
            print('[!] nontrivial gcd from V:', g)
    # Try B=1 where U_i is invertible: A = -V_i/U_i
    for ui,vi in zip(U,V):
        g=math.gcd(ui,n)
        if g==1:
            A=(-vi*pow(ui,-1,n))%n
            delta=one*A + gamma
            if alpha*delta == delta*eps:
                return delta, ('B=1', A)
        elif 1<g<n:
            print('[!] nontrivial gcd from U:', g)
    raise ValueError('could not recover delta')

def main():
    n,alpha,beta,gamma,ct,mu,eps=parse_output(OUT)
    print('[+] n bits:', n.bit_length())
    print('[+] ct bytes:', len(ct))
    delta,how=find_delta(n,alpha,gamma,eps)
    print('[+] recovered delta up to scalar using', how[0])
    # κ = δ^-1 β δ, μ = κ*k*κ => k = κ^-1 μ κ^-1
    kappa=delta.inv()*beta*delta
    k=kappa.inv()*mu*kappa.inv()
    print('[+] k =', str(k)[:120]+'...')
    K=hashlib.sha256(str(k).encode()).digest()
    dec=Cipher(algorithms.AES(K), modes.CBC(b'\0'*16)).decryptor()
    pt=dec.update(ct)+dec.finalize()
    padlen=pt[-1]
    if 1 <= padlen <= 16 and pt.endswith(bytes([padlen])*padlen):
        pt=pt[:-padlen]
    print('[+] plaintext:', pt)

if __name__=='__main__': main()
