import random, math, re, sys, time

class FactorFound(Exception):
    def __init__(self,g): self.g=g

def inv_mod(a,n):
    a%=n
    g=math.gcd(a,n)
    if g!=1:
        if 1<g<n: raise FactorFound(g)
        raise ZeroDivisionError
    return pow(a,-1,n)

def add(P,Q,b,n):
    if P is None: return Q
    if Q is None: return P
    x1,y1=P; x2,y2=Q
    if (x1-x2)%n==0 and (y1+y2)%n==0:
        # point at infinity over components where both equal; denominator may reveal factor if x equal only on some factors
        g=math.gcd((x1-x2)%n,n)
        if 1<g<n: raise FactorFound(g)
        return None
    if (x1-x2)%n==0 and (y1-y2)%n==0:
        den=(2*y1)%n
        lam=((3*x1*x1)%n)*inv_mod(den,n)%n # a=0
    else:
        den=(x2-x1)%n
        lam=((y2-y1)%n)*inv_mod(den,n)%n
    x3=(lam*lam-x1-x2)%n
    y3=(lam*(x1-x3)-y1)%n
    return (x3,y3)

def mul(k,P,b,n):
    R=None
    Q=P
    while k:
        if k&1:
            R=add(R,Q,b,n)
        k//=2
        if k:
            Q=add(Q,Q,b,n)
    return R

def attack(N, trials=1000):
    for i in range(1,trials+1):
        x=random.randrange(2,N-1)
        y=random.randrange(2,N-1)
        b=(y*y - x*x*x) % N
        if math.gcd(6*b,N)!=1:
            g=math.gcd(6*b,N)
            if 1<g<N: return g
            continue
        P=(x,y)
        try:
            R=mul(N,P,b,N)
        except FactorFound as e:
            return e.g
        except ZeroDivisionError:
            continue
        # sometimes if [N]P == O modulo a factor but no inversion failure, try gcd of coordinates? no
        if i%50==0:
            print('trial',i, flush=True)
    return None

def main():
    text=open('/mnt/data/sus_solve/sus-imaginaryctf/files/output_40405e631cc5fb305df7d8f892af9974.txt').read()
    N=int(re.search(r'n = (\d+)',text).group(1)); e=int(re.search(r'e = (\d+)',text).group(1)); c=int(re.search(r'c = (\d+)',text).group(1))
    print('N bits',N.bit_length())
    t=time.time(); g=attack(N, trials=2000)
    print('time',time.time()-t)
    if not g:
        print('not found'); return
    print('factor bits',g.bit_length(),g)
    # determine factors
    co=N//g
    # if g=q likely, recover p from sqrt(4q-3)
    facs=[]
    # Try if g is q
    for qcand in [g,co]:
        D=4*qcand-3
        s=math.isqrt(D)
        if s*s==D:
            p=(s-1)//2
            q=qcand
            if p>1 and N%(p*q)==0:
                r=N//(p*q)
                print('p',p); print('q',q); print('r bits',r.bit_length())
                phi=(p-1)*(q-1)*(r-1)
                d=pow(e,-1,phi)
                m=pow(c,d,N)
                print(m.to_bytes((m.bit_length()+7)//8, "big"))
                return
    # maybe g=p or r or qr: factor co by relation
    print('got factor not directly q')
main()
