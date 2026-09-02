from fractions import Fraction
from pathlib import Path
import zipfile
with zipfile.ZipFile('crypto_brunner-radio.zip') as z:
    Path('total_broadcast.txt').write_bytes(z.read('crypto_brunner-radio/total_broadcast.txt'))
rows=[list(map(int,x.strip())) for x in Path('total_broadcast.txt').read_text().splitlines() if x.strip()]
A=[[int(c%(i+1)==0) for i in range(9)] for c in range(1,101)]
def sol(b):
    a=[[Fraction(v) for v in r]+[Fraction(y)] for r,y in zip(A,b)]
    r=0
    for c in range(9):
        p=next(i for i in range(r,100) if a[i][c])
        a[r],a[p]=a[p],a[r]; q=a[r][c]
        a[r]=[x/q for x in a[r]]
        for i in range(100):
            if i!=r:
                q=a[i][c]; a[i]=[x-q*y for x,y in zip(a[i],a[r])]
        r+=1
    return [int(a[i][-1]) for i in range(9)]
s=[[] for _ in range(9)]
for row in rows:
    for i,b in enumerate(sol(row)): s[i].append(str(b))
msgs=[''.join(chr(int(''.join(x)[i:i+8],2)) for i in range(0,288,8)) for x in s]
flag=next(x for x in msgs if 'brunner{' in x)
Path('flag.txt').write_text(flag)
print('FLAG:',flag)
