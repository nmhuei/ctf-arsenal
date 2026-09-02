F = GF(2^142 - 111)

# Load Stage 1 output
with open("../files/output_cf02c7213620d9c21818cf5f12d6bff5.txt") as f:
    lines = f.read().splitlines()
s_list = eval(lines[2])
s = [F(x) for x in s_list]

from sage.matrix.berlekamp_massey import berlekamp_massey
poly = berlekamp_massey(s)
print("Poly:", poly)

# poly factors:
# (x^2 + a*x + b) * (x^2 + c*x + d) * (x^3 + 31337)^3 * P_3(x)
factors = poly.factor()
P1, _ = factors[0] # x^2 + ...
P2, _ = factors[1] # x^2 + ...
P3_base, _ = factors[2] # x^3 + 31337
P4, _ = factors[3] # degree 7

# Let's define the square-free part of the polynomial:
poly_red = P1 * P2 * P3_base * P4
# The multiplicity part:
H = poly / poly_red
print("H:", H)

# Let's verify for a root of P1
# We can work in the extension field K = F.extension(P1, 'a')
# Wait, F.extension(P1, 'a') creates GF(p^2)
K.<a> = F.extension(P1)
# Note: P1(a) = 0, so a is a root of P1
print("a:", a)

# Let's compute R(x) = poly_red(x) / (x - a) in K[x]
Kx.<x> = K[]
R = Kx(poly_red) // (x - a)
operator = R * Kx(H)

# Now we need the coefficients of the operator.
# The operator has degree 19 (since poly has degree 20)
coeffs = operator.coefficients(sparse=False)
deg = operator.degree()
print("Operator degree:", deg)

# Compute t(0) = sum(coeffs[i] * s[i])
t_0 = sum(coeffs[i] * s[i] for i in range(deg + 1))

# But we need t_0(0) as well. How do we compute f(n) for n = 0, 1, 2, ...?
# We know the initial terms f(n) for n < 20:
COEFFS = [-poly[i] for i in range(20)] # coefficients of the recurrence f(n) = sum(COEFFS[i] * f(n - 20 + i))
# wait! poly = x^20 + c_19 x^19 + ... + c_0.
# So f(n) + c_19 f(n-1) + ... + c_0 f(n-20) = 0
# Let's compute f(n) for n up to 50:
f_vals = []
for n in range(50):
    if n < 20:
        val = F(int(10000*sin(n)))
    else:
        val = -sum(poly[i] * f_vals[i] for i in range(20))
    f_vals.append(val)

t_init = sum(coeffs[i] * f_vals[i] for i in range(deg + 1))
print("t_0 (shifted):", t_0)
print("t_init:", t_init)
u = t_0 / t_init
print("u = a^ITERS:", u)
