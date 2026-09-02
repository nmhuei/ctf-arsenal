import math
import decimal

with open('../output_b0bbcffd6c89c7f6ec66b8be6669bf2d.txt') as f:
    lines = f.readlines()

hint = int(lines[0].split('=')[1].strip())
D = int(lines[1].split('=')[1].strip())
n = int(lines[2].split('=')[1].strip())

decimal.getcontext().prec = 1000

D_dec = decimal.Decimal(D)
n_dec = decimal.Decimal(n)
hint_dec = decimal.Decimal(hint)

sqrt_n = n_dec.sqrt()
X_approx = hint_dec / D_dec
X2_approx = X_approx ** 2
p_plus_q_approx = X2_approx - 2 * sqrt_n

S_approx = int(p_plus_q_approx)
# Roots of x^2 - S x + n = 0
disc = S_approx**2 - 4*n
print(f"disc > 0? {disc > 0}")
if disc > 0:
    sqrt_disc = math.isqrt(disc)
    p_approx = (S_approx + sqrt_disc) // 2
    q_approx = n // p_approx
    print(f"p_approx bit len: {p_approx.bit_length()}")
    print(f"q_approx bit len: {q_approx.bit_length()}")
    print(f"n % p_approx == 0? {n % p_approx == 0}")
    print(f"n - p_approx * q_approx: {n - p_approx * q_approx}")
    print(f"abs(n - p_approx * q_approx) bit len: {abs(n - p_approx * q_approx).bit_length()}")
