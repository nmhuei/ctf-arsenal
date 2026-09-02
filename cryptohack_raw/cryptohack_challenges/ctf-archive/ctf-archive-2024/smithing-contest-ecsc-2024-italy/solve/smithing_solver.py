import hashlib, json, socket, sys, re, ast, time

p = 239019556058548081539763731767358519973
n = 239019556058548081524303474453605616589
trace = 15460257313752903385
b_const = 11
FINAL_EXP = (p**12 - 1)//n
# Sage default GF(p^2) modulus inferred: a^2 + a - 1 = 0, i.e. a^2 = 1 - a.
Acoef = p-1  # coefficient of a in a^2
Bcoef = 1    # constant in a^2

class Fp2:
    __slots__=('a','b') # a*alpha + b
    def __init__(self, a=0, b=None):
        if b is None:
            if isinstance(a, Fp2):
                self.a=a.a; self.b=a.b; return
            if isinstance(a, tuple) or isinstance(a, list):
                self.a=int(a[0])%p; self.b=int(a[1])%p; return
            self.a=0; self.b=int(a)%p; return
        self.a=int(a)%p; self.b=int(b)%p
    def __add__(self,o):
        o=to2(o); return Fp2(self.a+o.a, self.b+o.b)
    __radd__=__add__
    def __neg__(self): return Fp2(-self.a, -self.b)
    def __sub__(self,o):
        o=to2(o); return Fp2(self.a-o.a, self.b-o.b)
    def __rsub__(self,o): return to2(o)-self
    def __mul__(self,o):
        o=to2(o); a,b=self.a,self.b; c,d=o.a,o.b
        # (aA+b)(cA+d)=ac A^2 +(ad+bc)A+bd, A^2=-A+1
        return Fp2(a*c*Acoef + a*d + b*c, a*c*Bcoef + b*d)
    __rmul__=__mul__
    def __truediv__(self,o): return self*to2(o).inv()
    def __rtruediv__(self,o): return to2(o)*self.inv()
    def __eq__(self,o):
        o=to2(o); return self.a==o.a and self.b==o.b
    def __bool__(self): return self.a!=0 or self.b!=0
    def __repr__(self): return f"Fp2({self.a},{self.b})"
    def inv(self):
        # inverse via conjugate: alpha' = -1-alpha for alpha^2+alpha-1
        # (a alpha+b)^p = a alpha^p + b = a(-1-alpha)+b = -a alpha + (b-a)
        conj=Fp2(-self.a, self.b-self.a)
        norm=(self*conj).b
        if norm%p==0: raise ZeroDivisionError
        return Fp2(conj.a*pow(norm,-1,p), conj.b*pow(norm,-1,p))
    def __pow__(self,e):
        e=int(e)
        if e<0: return (self.inv())**(-e)
        res=Fp2(0,1); base=self
        while e:
            if e&1: res=res*base
            base=base*base; e//=2
        return res
    def is_zero(self): return self.a==0 and self.b==0
    def to_sage(self):
        aa=self.a%p; bb=self.b%p
        if aa==0: return str(bb)
        if bb==0: return f"{aa}*a"
        return f"{aa}*a + {bb}"

def to2(x): return x if isinstance(x,Fp2) else Fp2(x)

# constants in Fp2
eps = Fp2(50853858759521010453592688907791911225, 156893423039651253351316307339945502422)
Btwist = Fp2(0,b_const) / eps

class Fp12:
    __slots__=('c',)  # list of 6 Fp2 coefficients, sum c[i] z^i, z^6=eps
    def __init__(self, c=0):
        if isinstance(c,Fp12):
            self.c=c.c[:]; return
        if isinstance(c,Fp2):
            self.c=[c]+[Fp2(0) for _ in range(5)]; return
        if isinstance(c,(list,tuple)):
            cc=[to2(x) for x in c]
            if len(cc)>6:
                # reduce
                arr=[Fp2(0) for _ in range(6)]
                for i,ci in enumerate(cc):
                    if i<6: arr[i]=arr[i]+ci
                    else: arr[i%6]=arr[i%6]+ci*(eps**(i//6))
                cc=arr
            self.c=cc+[Fp2(0) for _ in range(6-len(cc))]
            return
        self.c=[Fp2(0,int(c))]+[Fp2(0) for _ in range(5)]
    def __add__(self,o):
        o=to12(o); return Fp12([self.c[i]+o.c[i] for i in range(6)])
    __radd__=__add__
    def __neg__(self): return Fp12([-x for x in self.c])
    def __sub__(self,o):
        o=to12(o); return Fp12([self.c[i]-o.c[i] for i in range(6)])
    def __rsub__(self,o): return to12(o)-self
    def __mul__(self,o):
        o=to12(o)
        tmp=[Fp2(0) for _ in range(11)]
        for i in range(6):
            ai=self.c[i]
            if not ai: continue
            for j in range(6):
                bj=o.c[j]
                if bj: tmp[i+j]=tmp[i+j]+ai*bj
        for k in range(10,5,-1):
            if tmp[k]:
                tmp[k-6]=tmp[k-6]+tmp[k]*eps
        return Fp12(tmp[:6])
    __rmul__=__mul__
    def __truediv__(self,o): return self*to12(o).inv()
    def __rtruediv__(self,o): return to12(o)*self.inv()
    def __eq__(self,o):
        o=to12(o); return all(self.c[i]==o.c[i] for i in range(6))
    def __bool__(self): return any(bool(x) for x in self.c)
    def __repr__(self): return 'Fp12('+repr(self.c)+')'
    def __pow__(self,e):
        e=int(e)
        if e<0: return (self.inv())**(-e)
        res=Fp12(1); base=self
        while e:
            if e&1: res=res*base
            base=base*base; e//=2
        return res
    def inv(self):
        # Invert by solving the 6x6 Fp2-linear system self * x = 1.
        # This is much faster than exponentiating by p^12-2 in pure Python.
        # Build columns M[:,j] = self * z^j.
        M=[]
        for row in range(6):
            M.append([None]*7)
        for j in range(6):
            prod = self * Fp12([Fp2(0)]*j + [Fp2(1)])
            for i in range(6):
                M[i][j]=prod.c[i]
        for i in range(6):
            M[i][6]=Fp2(1 if i==0 else 0)
        # Gaussian elimination over Fp2.
        for col in range(6):
            piv=None
            for r in range(col,6):
                if M[r][col]:
                    piv=r; break
            if piv is None:
                raise ZeroDivisionError
            if piv!=col:
                M[col],M[piv]=M[piv],M[col]
            invp=M[col][col].inv()
            for j in range(col,7):
                M[col][j]=M[col][j]*invp
            for r in range(6):
                if r==col: continue
                fac=M[r][col]
                if fac:
                    for j in range(col,7):
                        M[r][j]=M[r][j]-fac*M[col][j]
        return Fp12([M[i][6] for i in range(6)])
    def to_sage(self):
        terms=[]
        for i,coef in enumerate(self.c):
            if not coef: continue
            cs=coef.to_sage()
            if i==0:
                terms.append(f"({cs})")
            elif i==1:
                terms.append(f"({cs})*z")
            else:
                terms.append(f"({cs})*z^{i}")
        return ' + '.join(terms) if terms else '0'

def to12(x):
    if isinstance(x,Fp12): return x
    if isinstance(x,Fp2): return Fp12(x)
    return Fp12(x)

ZERO2=Fp2(0); ONE2=Fp2(1)
ZERO12=Fp12(0); ONE12=Fp12(1)

class Point:
    __slots__=('x','y','inf','field')
    def __init__(self,x=None,y=None,inf=False,field=Fp2):
        self.inf=inf; self.field=field
        if inf:
            self.x=None; self.y=None
        else:
            self.x=x; self.y=y
    def is_inf(self): return self.inf
    def __neg__(self):
        if self.inf: return self
        return Point(self.x, -self.y, field=self.field)
    def __add__(self,Q):
        P=self
        if P.inf: return Q
        if Q.inf: return P
        if P.x==Q.x:
            if P.y + Q.y == P.field(0):
                return Point(inf=True,field=P.field)
            # double
            lam=(P.field(3)*P.x*P.x)/(P.field(2)*P.y)
        else:
            lam=(Q.y-P.y)/(Q.x-P.x)
        x3=lam*lam-P.x-Q.x
        y3=lam*(P.x-x3)-P.y
        return Point(x3,y3,field=P.field)
    def __sub__(self,Q): return self + (-Q)
    def __rmul__(self,k):
        k=int(k)
        if k<0: return (-self).__rmul__(-k)
        R=Point(inf=True,field=self.field); B=self
        while k:
            if k&1: R=R+B
            B=B+B; k//=2
        return R
    def __eq__(self,Q):
        if self.inf or Q.inf: return self.inf and Q.inf
        return self.x==Q.x and self.y==Q.y
    def __repr__(self):
        if self.inf: return 'O'
        return f"Point({self.x},{self.y})"

# Base field Fp as ints wrapped? We can use Fp2 with a=0 for G1 too and Fp12 after embedding.
def parse_fp2(s):
    if isinstance(s,int): return Fp2(0,s)
    s=str(s).strip()
    # parse forms like '123*a + 456', '123*a', '456'
    ss=s.replace(' ','')
    aa=0; bb=0
    if 'a' in ss:
        # split top-level plus/minus; easier regex for coeff*a and remaining integer
        m=re.search(r'([+-]?\d+)\*a', ss)
        if not m:
            if ss.startswith('a'): aa=1
            else: raise ValueError('bad fp2 '+s)
        else:
            aa=int(m.group(1))%p
            rest=ss[:m.start()]+ss[m.end():]
            if rest.startswith('+'): rest=rest[1:]
            if rest:
                bb=int(rest)%p
        # if pattern is 'coeff*a+const', rest works only if coeff*a in middle? likely enough
        # robust: remove the coeff*a term
        rest=ss[:m.start()]+ss[m.end():]
        rest=rest.replace('++','+').replace('+-','-')
        if rest in ('','+'): bb=0
        else: bb=int(rest)%p
    else:
        bb=int(ss)%p
    return Fp2(aa,bb)

def fp2_from_json(x):
    return parse_fp2(x)

G1 = Point(Fp2(0,1), Fp2(0,133660577740454676305948404600566797994), field=Fp2)
G2 = Point(Fp2(100774561144590475569157120930767342387,218728496724280042701446122970647661523),
           Fp2(115367896606755692925113233629944781384,211093354487559124632805793736258741445), field=Fp2)

# Determine twist order candidate
h_candidates = [
    p+1+trace,
    p-1-trace,
    p-1+trace,
]

def is_on_twist(P):
    if P.inf: return True
    return P.y*P.y == P.x*P.x*P.x + Btwist

def test_h():
    print('eps',eps,'Btwist',Btwist)
    print('G2 on twist', is_on_twist(G2), 'nG2 inf', (n*G2).inf)
    for h in h_candidates:
        print('cand h',h,'order kills G2?', ((h*n)*G2).inf, 'hG2 inf?', (h*G2).inf)

def frob2(x):
    # not used; Fp2 conjugate = (a alpha+b)^p = -a alpha + (b-a)
    return Fp2(-x.a, x.b-x.a)

# sqrt in Fp2 using Tonelli-Shanks over q=p^2
q2=p*p
# find non-square
_nonres=None
def legendre2(x):
    if not x: return 0
    y=x**((q2-1)//2)
    if y==ONE2: return 1
    if y==-ONE2: return -1
    raise ValueError('unexpected legendre '+repr(y))

def nonsquare2():
    global _nonres
    if _nonres is not None: return _nonres
    candidates=[Fp2(1,0), Fp2(0,2), Fp2(1,1), Fp2(2,0), Fp2(3,0), Fp2(0,3)]
    i=2
    for c in candidates:
        if legendre2(c)==-1:
            _nonres=c; return c
    while True:
        c=Fp2(i,0)
        if legendre2(c)==-1:
            _nonres=c; return c
        c=Fp2(i,1)
        if legendre2(c)==-1:
            _nonres=c; return c
        i+=1

def sqrt2(a):
    a=to2(a)
    if not a: return Fp2(0)
    if legendre2(a)!=1: return None
    # q-1 = 2^s * Q
    Q=q2-1; S=0
    while Q%2==0:
        S+=1; Q//=2
    z=nonsquare2()
    c=z**Q
    x=a**((Q+1)//2)
    t=a**Q
    M=S
    while t!=ONE2:
        i=1
        t2=t*t
        while i<M and t2!=ONE2:
            t2=t2*t2; i+=1
        if i==M:
            raise ValueError('sqrt failure')
        b=c**(1<<(M-i-1))
        x=x*b
        t=t*b*b
        c=b*b
        M=i
    return x

def lift_x_twist(xconst, sign=0):
    x=Fp2(0,xconst)
    rhs=x*x*x + Btwist
    y=sqrt2(rhs)
    if y is None: return None
    if sign: y=-y
    return Point(x,y,field=Fp2)

def H(mbytes):
    return int.from_bytes(hashlib.sha256(mbytes).digest()[:16],'big') % n

def find_h():
    # Test by random deterministic x points: true group order kills all valid points.
    xs=[]
    seed=12345
    for i in range(20):
        x=(seed+i)%p
        P=lift_x_twist(x,0)
        if P: xs.append(P)
    for hc in h_candidates:
        ok=True
        for P in xs[:5]:
            if not ((hc*n)*P).inf:
                ok=False; break
        if ok:
            return hc
    raise RuntimeError('no h')

h_twist = None

def H0(uid, sign=0):
    global h_twist
    if h_twist is None: h_twist=find_h()
    x0=int.from_bytes(hashlib.sha256(uid.encode()).digest(),'big')%p
    while True:
        x0=(x0+1)%p
        P=lift_x_twist(x0,sign)
        if P is None: continue
        Q=h_twist*P
        if not Q.inf and (n*Q).inf:
            return Q

# Pairing implementation
def embed_g1(P):
    if P.inf: return Point(inf=True,field=Fp12)
    return Point(Fp12(P.x), Fp12(P.y), field=Fp12)

def phi_g2(Q):
    if Q.inf: return Point(inf=True,field=Fp12)
    z=Fp12([Fp2(0),Fp2(1)])
    z2=z*z; z3=z2*z
    return Point(z2*Fp12(Q.x), z3*Fp12(Q.y), field=Fp12)

def linefunc(A,B,P):
    # line through A,B evaluated at affine P, divided by vertical line at A+B evaluated at P
    # curve y^2=x^3+b. All in Fp12.
    if A.inf or B.inf: return ONE12
    if A.x==B.x and A.y + B.y == Fp12(0):
        # vertical line x - A.x; divisor? Usually just xP-xA
        return P.x - A.x
    if A==B:
        lam=(Fp12(3)*A.x*A.x)/(Fp12(2)*A.y)
    else:
        lam=(B.y-A.y)/(B.x-A.x)
    C=A+B
    # l/v = (yP-yA-lam(xP-xA))/(xP-xC)
    return (P.y - A.y - lam*(P.x-A.x))/(P.x-C.x)

def miller(P_eval, Q_base, m):
    # f_{m,Q}(P)
    R=Q_base
    f=ONE12
    bits=bin(m)[3:]
    for bit in bits:
        f=f*f*linefunc(R,R,P_eval)
        R=R+R
        if bit=='1':
            f=f*linefunc(R,Q_base,P_eval)
            R=R+Q_base
    return f

def ate_pairing(P_g1_or_fp12, Q_g2, variant='ate'):
    # Computes P.ate_pairing(phi(Q), n,k,trace,p) likely: f_{trace-1, phi(Q)}(P)^(p^12-1)/n
    if isinstance(P_g1_or_fp12.x,Fp2): P=embed_g1(P_g1_or_fp12)
    else: P=P_g1_or_fp12
    Q=phi_g2(Q_g2) if isinstance(Q_g2.x,Fp2) else Q_g2
    if variant=='ate':
        loop=trace-1
        val=miller(P,Q,loop)
    elif variant=='tate_q':
        # f_{n,P}(Q), for experimentation, not used
        val=miller(Q,P,n)
    else:
        raise ValueError
    return val ** FINAL_EXP

def point_from_g1_list(lst):
    return Point(Fp2(0,int(lst[0])), Fp2(0,int(lst[1])), field=Fp2)

def point_from_g2_list(lst):
    return Point(parse_fp2(lst[0]), parse_fp2(lst[1]), field=Fp2)

def point_g2_to_json(P):
    return [P.x.to_sage(), P.y.to_sage()]

def point_g1_to_json(P):
    return [int(P.x.b), int(P.y.b)]

def exploit_from_params(params, C_json=None, uid='tan', sign=0, pairing_variant='ate'):
    P_G1=point_from_g1_list(params['P_G1'])
    Qpub=point_from_g1_list(params['Q'])
    P_G2=point_from_g2_list(params['P_G2'])
    target=f'I, the eternal Admin, keeper of all secrets, hereby decree that you, {uid}, are worthy to glimpse my deepest and most ancient secret: the flag.'
    hh=H(target.encode())
    Qid=H0('admin', sign=sign)
    R=Qpub
    S=Qid + (hh*P_G2)
    sig=[point_g1_to_json(R), point_g2_to_json(S)]
    if C_json is None:
        return target,sig
    C=point_from_g1_list(C_json)
    # D=P_G2, r=e(C,D), t=e(Q,P_G2)/e(P_G1,Qid)
    r=ate_pairing(C, P_G2, pairing_variant)
    eQP=ate_pairing(Qpub, P_G2, pairing_variant)
    eAQ=ate_pairing(P_G1, Qid, pairing_variant)
    t=eQP/eAQ
    return target,sig,[t.to_sage(), r.to_sage()]

# Local self-check of derived equations using our pairing implementation.
def local_check(sign=0):
    import random
    # Deterministic sample private params
    s=12345678901234567890 % n; u=9876543210987654321 % n
    P_G1=u*G1; P_G2=u*G2; Qpub=s*P_G1
    params={'P_G1': point_g1_to_json(P_G1), 'Q': point_g1_to_json(Qpub), 'P_G2': point_g2_to_json(P_G2)}
    uid='tan'
    target,sig=exploit_from_params(params, uid=uid, sign=sign)
    R=point_from_g1_list(sig[0]); S=point_from_g2_list(sig[1]); Qid=H0('admin',sign=sign)
    x=1111111111; y=2222222223; yinv=pow(y,-1,n)
    C=x*y*R
    hmsg=H(target.encode())
    rval=ate_pairing(C, P_G2)
    tval=ate_pairing(Qpub, P_G2) / ate_pairing(P_G1, Qid)
    lhs0=ate_pairing(R,S)**x
    rhs0=(ate_pairing(Qpub,Qid)**x) * (rval**(hmsg*yinv))
    lhs1=(rval**yinv) * (tval**x) * (ate_pairing(P_G1,Qid)**x)
    rhs1=ate_pairing(R+Qpub,P_G2)**x
    print('local_check', lhs0==rhs0, lhs1==rhs1, 'h', h_twist)

def parse_fp12_expr_ours(s):
    # only for our own generated strings; avoid eval.
    # Easier: not needed if local check directly uses values. Placeholder not robust.
    # Use a mini eval with safe objects z,a? Actually do not expose untrusted.
    a=Fp2(1,0); z=Fp12([Fp2(0),Fp2(1)])
    return eval(s.replace('^','**'), {'__builtins__':{}}, {'a':a,'z':z})


def recv_until(sock, token, timeout=120):
    sock.settimeout(timeout)
    data=b''
    tok=token if isinstance(token, bytes) else token.encode()
    while tok not in data:
        chunk=sock.recv(4096)
        if not chunk:
            break
        data += chunk
    return data

def run_remote(host='archive.cryptohack.org', port=25469, uid='tan', sign=0):
    sock=socket.create_connection((host, int(port)), timeout=20)
    banner=recv_until(sock, b'tell me your username: ')
    txt=banner.decode(errors='replace')
    m=re.search(r'\{.*\}', txt)
    if not m:
        raise RuntimeError('could not parse params from banner:\n'+txt)
    params=json.loads(m.group(0))

    # Build the forged signature first. R=Q and S=Qid_admin + H(target)*P_G2.
    target, sig = exploit_from_params(params, uid=uid, sign=sign)

    sock.sendall((uid+'\n').encode())
    _=recv_until(sock, b'give me a signature to verify: ')
    sock.sendall((json.dumps(sig)+'\n').encode())
    _=recv_until(sock, b'what message corresponds to this signature? ')
    sock.sendall((target+'\n').encode())
    _=recv_until(sock, b'who signed it? ')
    sock.sendall(b'admin\n')

    cbuf=recv_until(sock, b't, r? ')
    ctext=cbuf.decode(errors='replace')
    cm=re.search(r'C\s*=\s*(\[[^\n]+\])', ctext)
    if not cm:
        raise RuntimeError('could not parse C from:\n'+ctext)
    C_json=json.loads(cm.group(1))

    _, _, tr = exploit_from_params(params, C_json, uid=uid, sign=sign)
    sock.sendall((json.dumps(tr)+'\n').encode())
    out=b''
    while True:
        try:
            chunk=sock.recv(4096)
        except socket.timeout:
            break
        if not chunk:
            break
        out += chunk
    sock.close()
    return (ctext + out.decode(errors='replace'))

if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='test':
        test_h(); print('h found', find_h()); print('H0', H0('admin',0), H0('admin',1)); local_check(0); sys.exit()
    if len(sys.argv)>1 and sys.argv[1]=='remote':
        host=sys.argv[2] if len(sys.argv)>2 else 'archive.cryptohack.org'
        port=int(sys.argv[3]) if len(sys.argv)>3 else 25469
        uid=sys.argv[4] if len(sys.argv)>4 else 'tan'
        # Sage's lift_x root sign is the only expected ambiguity, so try both.
        for sign in (0,1):
            print(f'[*] trying sign={sign}', file=sys.stderr)
            try:
                out=run_remote(host, port, uid, sign)
                print(out)
                if 'ECSC{' in out or 'crypto{' in out or 'flag' in out.lower():
                    break
            except Exception as e:
                print(f'[!] sign={sign} failed locally/client-side: {e}', file=sys.stderr)
        sys.exit()
    print('Usage: python3 smithing_solver.py test | remote [host] [port] [uid]')
