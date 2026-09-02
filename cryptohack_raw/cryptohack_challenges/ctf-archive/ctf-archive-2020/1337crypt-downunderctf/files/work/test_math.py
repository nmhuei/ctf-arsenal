import math

# Load hint, D, n from output
with open('../output_b0bbcffd6c89c7f6ec66b8be6669bf2d.txt') as f:
    lines = f.readlines()

hint = int(lines[0].split('=')[1].strip())
D = int(lines[1].split('=')[1].strip())
n = int(lines[2].split('=')[1].strip())

print(f"hint bit length: {hint.bit_length()}")
print(f"D bit length: {D.bit_length()}")
print(f"n bit length: {n.bit_length()}")

# n ~ 2674 bits => sqrt(n) ~ 1337 bits
# D ~ 84 bits
# hint ~ 753 bits

# Let's check (hint^2 - 2 * D^2 * sqrt(n)) / D^2
# Using high precision decimal or integer arithmetic
import decimal
decimal.getcontext().prec = 1000

D_dec = decimal.Decimal(D)
n_dec = decimal.Decimal(n)
hint_dec = decimal.Decimal(hint)

sqrt_n = n_dec.sqrt()
X_approx = hint_dec / D_dec
X2_approx = X_approx ** 2
p_plus_q_approx = X2_approx - 2 * sqrt_n

print(f"p + q approx: {p_plus_q_approx}")
