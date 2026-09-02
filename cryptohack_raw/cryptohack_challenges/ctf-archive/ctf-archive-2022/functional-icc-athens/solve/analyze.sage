F = GF(2^142 - 111)
p = F.order()
print("p =", p)
print("p - 1 factorization:")
try:
    print(factor(p - 1))
except Exception as e:
    print("Factor failed:", e)

# Load polynomial
with open("../files/output_cf02c7213620d9c21818cf5f12d6bff5.txt") as f:
    lines = f.read().splitlines()
s_list = eval(lines[2])
s = [F(x) for x in s_list]

from sage.matrix.berlekamp_massey import berlekamp_massey
poly = berlekamp_massey(s)
print("Roots of poly in F:")
roots = poly.roots()
print(roots)
