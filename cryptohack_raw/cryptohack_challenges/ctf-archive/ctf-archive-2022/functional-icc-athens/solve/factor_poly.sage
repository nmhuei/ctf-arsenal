F = GF(2^142 - 111)
# Load polynomial
with open("../files/output_cf02c7213620d9c21818cf5f12d6bff5.txt") as f:
    lines = f.read().splitlines()
s_list = eval(lines[2])
s = [F(x) for x in s_list]

from sage.matrix.berlekamp_massey import berlekamp_massey
poly = berlekamp_massey(s)
print("Factorization of poly:")
print(poly.factor())
