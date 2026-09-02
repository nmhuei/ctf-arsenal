from decimal import Decimal, getcontext
import re, math
from sympy import Matrix
from fractions import Fraction

getcontext().prec = 1000

def iroot(n):
    r=math.isqrt(n)
    return r if r*r==n else None

def invmod(a,m):
    return pow(a,-1,m)

def long_to_bytes(n):
    if n==0: return b'\x00'
    return n.to_bytes((n.bit_length()+7)//8,'big')

def dot(u,v): return sum(int(a)*int(b) for a,b in zip(u,v))
def add(u,v): return [int(a)+int(b) for a,b in zip(u,v)]
def mul(c,u): return [int(c)*int(a) for a in u]

def nearest_plane(basis, target):
    # Babai on a 2-dimensional LLL-reduced row basis in Z^3, exact rational GS.
    n=len(basis); m=len(basis[0])
    Bstar=[]; norm=[]
    for i in range(n):
        v=[Fraction(x) for x in basis[i]]
        for j in range(i):
            mu=sum(Fraction(basis[i][k])*Bstar[j][k] for k in range(m))/norm[j]
            v=[v[k]-mu*Bstar[j][k] for k in range(m)]
        Bstar.append(v)
        norm.append(sum(x*x for x in v))
    y=[Fraction(x) for x in target]
    coeff=[0]*n
    for i in reversed(range(n)):
        ci=sum(y[k]*Bstar[i][k] for k in range(m))/norm[i]
        q=ci.numerator//ci.denominator
        rem=ci-q
        if rem > Fraction(1,2): q += 1
        if rem < Fraction(-1,2): q -= 1
        coeff[i]=int(q)
        y=[y[k]-q*Fraction(basis[i][k]) for k in range(m)]
    v=[0]*m
    for c,b in zip(coeff,basis):
        v=add(v,mul(c,b))
    return v

def recover_C_D(A,B,C0):
    N=A*B
    D0=math.isqrt(N-C0*C0)
    R=N-C0*C0-D0*D0
    # actual rounding error is around 71 bits; 75 bits is enough for this output.
    # Try increasing bounds to be robust.
    for Tbits in [75,80,90,100]:
        T=1<<Tbits
        Eres=1<<(2*Tbits+4)
        M=Matrix([[Eres,0,T*2*C0],[0,Eres,T*2*D0]]).lll()
        basis=[list(map(int,M.row(i))) for i in range(M.rows)]
        target=[0,0,T*R]
        center=nearest_plane(basis,target)
        # enumerate a small neighbourhood in reduced-basis coordinates
        for da in range(-5,6):
            for db in range(-5,6):
                v=add(center, add(mul(da,basis[0]), mul(db,basis[1])))
                if v[0] % Eres or v[1] % Eres:
                    continue
                t=v[0]//Eres; u=v[1]//Eres
                if abs(t)>T or abs(u)>T:
                    continue
                C=C0+t; D=D0+u
                if D>=0 and C*C+D*D==N:
                    return C,D
    raise ValueError('failed to recover exact C,D')

def parse(path):
    text=open(path).read()
    n=int(re.search(r'n = (\d+)', text).group(1))
    c=int(re.search(r'c = (\d+)', text).group(1))
    xs=re.search(r'x = \((.*?), (.*?)\)\n', text).groups()
    ys=re.search(r'y = \((.*?), (.*?)\)', text, re.S).groups()
    xr=[Decimal(s) for s in xs]
    yr=[Decimal(s) for s in ys]
    return n,c,xr,yr

def main():
    import sys
    path = sys.argv[1] if len(sys.argv)>1 else '/mnt/data/kaitenzushi/kaitenzushi-hacktm-ctf/files/output_94fa49958535125cc5ea05f5960fc001.txt'
    n,c,xr,yr = parse(path)
    # y is small enough that ||y||^2 rounds exactly.
    B = int((yr[0]*yr[0] + yr[1]*yr[1]).to_integral_value(rounding='ROUND_HALF_EVEN'))
    # Use A + eB = 2n. Although A is not roundable exactly, e is.
    e = int(((Decimal(2*n) - (xr[0]*xr[0] + xr[1]*xr[1])) / Decimal(B)).to_integral_value(rounding='ROUND_HALF_EVEN'))
    A = 2*n - e*B
    C0 = int((xr[0]*yr[0] + xr[1]*yr[1]).to_integral_value(rounding='ROUND_HALF_EVEN'))
    C,Dabs = recover_C_D(A,B,C0)
    print(f'[+] e = {e}')
    print(f'[+] recovered exact Gram: A,B,C,D with D bits {Dabs.bit_length()}')

    candidates=[]
    for D in (Dabs, -Dabs):
        # X = (C/B)Y - (D/B)JY, U=y1^2-y2^2, V=2y1y2
        K = C*C - D*D + e*B*B
        L = 2*C*D
        W2 = K*K + L*L
        W = iroot(W2)
        if W is None:
            continue
        for s in (1,-1):
            if (B*L)%W or (B*K)%W:
                continue
            U = s*(B*L//W)
            V = -s*(B*K//W)
            if U*U + V*V != B*B:
                continue
            if ((B+U)&1) or ((B-U)&1):
                continue
            y1sq=(B+U)//2; y2sq=(B-U)//2
            if y1sq<0 or y2sq<0:
                continue
            ay1=iroot(y1sq); ay2=iroot(y2sq)
            if ay1 is None or ay2 is None:
                continue
            for sy1 in (1,-1):
                for sy2 in (1,-1):
                    y1=sy1*ay1; y2=sy2*ay2
                    if 2*y1*y2 != V:
                        continue
                    num1=C*y1 + D*y2
                    num2=C*y2 - D*y1
                    if num1 % B or num2 % B:
                        continue
                    x1=num1//B; x2=num2//B
                    if x1*x1+e*y1*y1==n and x2*x2+e*y2*y2==n:
                        candidates.append((x1,y1,x2,y2))
    print(f'[+] coordinate candidates: {len(candidates)}')
    seen=set()
    for x1,y1,x2,y2 in candidates:
        key=(x1,y1,x2,y2)
        if key in seen: continue
        seen.add(key)
        # factor from two independent representations
        factors=[]
        for val in (x1*y2-x2*y1, x1*y2+x2*y1, x1*x2+e*y1*y2, x1*x2-e*y1*y2):
            g=math.gcd(abs(val), n)
            if 1<g<n:
                factors=[g,n//g]
                break
        if not factors:
            continue
        p,q=factors
        phi=(p-1)*(q-1)
        d=pow(e,-1,phi)
        m=pow(c,d,n)
        flag_int = m ^ x1 ^ y1 ^ x2 ^ y2
        flag=long_to_bytes(flag_int)
        print('[+] p bits, q bits =', p.bit_length(), q.bit_length())
        print('[+] candidate signs bitlengths:', x1.bit_length(), y1.bit_length(), x2.bit_length(), y2.bit_length())
        print('[+] flag =', flag)

if __name__=='__main__':
    main()
