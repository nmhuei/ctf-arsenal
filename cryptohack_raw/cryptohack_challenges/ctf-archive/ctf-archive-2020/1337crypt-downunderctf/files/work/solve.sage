import decimal
from Crypto.Util.number import long_to_bytes

print("[+] Reading output file...")
with open('../output_b0bbcffd6c89c7f6ec66b8be6669bf2d.txt') as f:
    lines = f.readlines()

hint = int(lines[0].split('=')[1].strip())
D = int(lines[1].split('=')[1].strip())
n = int(lines[2].split('=')[1].strip())

c = eval(lines[3].split('=')[1].strip())

print(f"[+] n bit length: {n.bit_length()}")
print(f"[+] ciphertexts count: {len(c)}")

# High precision arithmetic to get p_approx
decimal.getcontext().prec = int(1000)

D_dec = decimal.Decimal(str(D))
n_dec = decimal.Decimal(str(n))
hint_dec = decimal.Decimal(str(hint))

sqrt_n = n_dec.sqrt()
X_approx = hint_dec / D_dec
X2_approx = X_approx * X_approx
p_plus_q_approx = X2_approx - decimal.Decimal('2') * sqrt_n

S_approx = int(p_plus_q_approx)

# Find p_approx from x^2 - S_approx * x + n = 0
disc = S_approx*S_approx - 4*n
sqrt_disc = int(decimal.Decimal(str(disc)).sqrt())
p_approx = (S_approx + sqrt_disc) // 2

print(f"[+] p_approx calculated, bit length: {p_approx.bit_length()}")

# Coppersmith small_roots
P = PolynomialRing(Zmod(n), 'x')
x = P.gen()

print("[+] Running Coppersmith small_roots with epsilon=0.02...")

# Try f = x - p_approx and f = x + p_approx
p = None
for f_sign, p_formula in [(x - p_approx, lambda r: p_approx - r), (x + p_approx, lambda r: p_approx + r)]:
    roots = f_sign.small_roots(X=int(2**600), beta=float(0.5), epsilon=float(0.02))
    print(f"    Roots for {f_sign}: {roots}")
    if roots:
        cand_p = int(p_formula(roots[0]))
        if cand_p > 0 and n % cand_p == 0:
            p = cand_p
            break

if not p:
    raise ValueError("Could not find p!")

assert n % p == 0, "p is not a factor of n!"
q = n // p
print(f"[+] Factored n successfully!")
print(f"[+] p = {p}")
print(f"[+] q = {q}")

# Decrypting flag bits
print("[+] Decrypting flag...")
flag_bits = []
for ci in c:
    lp = legendre_symbol(ci, p)
    # If lp == -1 => b = 0; if lp == 1 => b = 1
    if lp == -1:
        flag_bits.append('0')
    else:
        flag_bits.append('1')

bin_str = ''.join(flag_bits)
flag_long = int(bin_str, 2)
flag = long_to_bytes(flag_long)

print(f"[+] FLAG: {flag.decode()}")
