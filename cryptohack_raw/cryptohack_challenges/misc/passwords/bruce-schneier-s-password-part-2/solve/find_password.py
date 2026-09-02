from itertools import combinations_with_replacement, permutations
from sympy import isprime
chars=list(range(48,58))+list(range(65,91))+list(range(97,123))+[95]
for n in range(1,20):
    print("testing", n)
    for a in combinations_with_replacement(chars,n):
        s=sum(a)
        if not isprime(s):
            continue
        p=1
        for x in a:
            p*=x
        if p==s and any(48<=x<=57 for x in a) and any(65<=x<=90 for x in a) and any(97<=x<=122 for x in a):
            print("SET", a, s)
            for r in set(permutations(a)):
                print("PASS", "".join(map(chr,r)))
            raise SystemExit
