import ast,re,hashlib,math
from pathlib import Path
from fpylll import IntegerMatrix, LLL
from Crypto.Cipher import AES
from hashlib import sha256
import sympy as sp
q=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
text=Path('files/output_2b76e1402ecd70095a243a705fbc9b17.txt').read_text()
sigs=ast.literal_eval(re.search(r'sigs = (\[.*\])',text).group(1))
ct=ast.literal_eval(re.search(r'ct = (b.*)',text).group(1)); nonce=ast.literal_eval(re.search(r'nonce = (b.*)',text).group(1))
msgs=[
    b"https://www.youtube.com/watch?v=kv4UD4ICd_0",
    b"https://www.youtube.com/watch?v=IijOKxLclxE",
    b"https://www.youtube.com/watch?v=GH6akWYAtGc",
    b"https://www.youtube.com/watch?v=Y3JhUFAa9bk",
    b"https://www.youtube.com/watch?v=FGID8CJ1fUY",
    b"https://www.youtube.com/watch?v=_BfmEjHVYwM",
    b"https://www.youtube.com/watch?v=zH7wBliAhT0",
    b"https://www.youtube.com/watch?v=NROQyBPX9Uo",
    b"https://www.youtube.com/watch?v=ylH6VpJAoME",
    b"https://www.youtube.com/watch?v=hI34Bhf5SaY",
    b"https://www.youtube.com/watch?v=bef23j792eE",
    b"https://www.youtube.com/watch?v=ybvXNOWX-dI",
    b"https://www.youtube.com/watch?v=dt3p2HtLzDA",
    b"https://www.youtube.com/watch?v=1Z4O8bKoLlU",
    b"https://www.youtube.com/watch?v=S53XDR4eGy4",
    b"https://www.youtube.com/watch?v=ZK64DWBQNXw",
    b"https://www.youtube.com/watch?v=tLL8cqRmaNE",
]
zs=[int.from_bytes(hashlib.sha256(m).digest(),'big')%q for m in msgs]
us=[]; vs=[]
for (r_c,s_c),(r_n,s_n),z_c,z_n in zip(sigs[:-1],sigs[1:],zs[:-1],zs[1:]):
    u=(r_n*pow(s_n,-1,q)-r_c*pow(s_c,-1,q))%q
    v=(z_n*pow(s_n,-1,q)-z_c*pow(s_c,-1,q))%q
    us.append(u); vs.append(v)
# Build Sage-equivalent block matrix: [[14x4 M, I14], [q*I4, 0]] = 18x18, scale first 4 columns.
Mcols=[us[:-2], vs[:-2], us[1:-1], vs[1:-1]]  # each len14
rows=[]
for i in range(14):
    row=[Mcols[c][i] for c in range(4)] + [1 if i==j else 0 for j in range(14)]
    rows.append(row)
for i in range(4):
    row=[0]*18
    row[i]=q
    rows.append(row)
S=2**1000
for row in rows:
    for c in range(4): row[c]*=S
A=IntegerMatrix.from_matrix(rows)
print('[*] running LLL...')
LLL.reduction(A, delta=0.99)
combos=[]
for ri in range(A.nrows):
    row=[int(A[ri,c]) for c in range(A.ncols)]
    if row[:4]==[0,0,0,0] and any(row[4:]):
        comb=row[4:]
        # verify annihilation
        ok=True
        for arr in [us[:-2],vs[:-2],us[1:-1],vs[1:-1]]:
            if sum(c*a for c,a in zip(comb,arr))%q !=0: ok=False
        if ok:
            combos.append(comb)
            print('[*] combo',len(combos),'normbits',sum(x*x for x in comb).bit_length())
print('[*] combos',len(combos))
# Use first 11 like writeup; if more/less, try subsets/prefixes.
def int_kernel(mat):
    M=sp.Matrix(mat)
    ns=M.nullspace()
    if not ns:
        return []
    out=[]
    for v in ns:
        den=1
        for x in v:
            den=sp.ilcm(den, x.q)
        ints=[int(x*den) for x in v]
        g=0
        for x in ints: g=math.gcd(g,abs(x))
        if g: ints=[x//g for x in ints]
        out.append(ints)
    return out
for take in range(min(11,len(combos)), len(combos)+1):
    eqs=[]
    for comb in combos[:take]:
        for off in range(2):
            row=[0]*15
            for j,c in enumerate(comb):
                row[off+j]+=c
            eqs.append(row)
    ker=int_kernel(eqs)
    print('[*] take',take,'kernel dim',len(ker))
    if len(ker)==0: continue
    for kv in ker:
        print('[*] ker bits',max(abs(x).bit_length() for x in kv), 'first',kv[:3])
        for mm in [-1,1]:
            rec=[mm*x for x in kv]
            if us[0]%q==0: continue
            d=((rec[0]-vs[0])%q)*pow(us[0],-1,q)%q
            pt=AES.new(sha256(str(d).encode()).digest(),AES.MODE_CTR,nonce=nonce).decrypt(ct)
            print('[*] sign',mm,'d',d,'pt',pt)
            if b'crypto{' in pt or b'HITCON{' in pt or all(32<=b<127 or b in (9,10,13) for b in pt):
                print('FLAG',pt.decode(errors='replace'))
                raise SystemExit
