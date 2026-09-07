# Synthetic generator matching apbq-rsa-iv exactly with scaled down parameters:
# Scale: prime 100 bits, B = 60 bits.
# n = 200 bits. h_i ~ 160 bits.
set_random_seed(42)

p_bits = 100
B_bits = 60

p = random_prime(2^p_bits, lbound=2^(p_bits-1))
q = random_prime(2^p_bits, lbound=2^(p_bits-1))
n = p * q

B = 1 << B_bits

a = [randint(1, B) for _ in range(3)]
b = [randint(1, B) for _ in range(3)]
h = [a[i] * p + b[i] * q for i in range(3)]

print(f"p: {p.bit_length()} bits, q: {q.bit_length()} bits, n: {n.bit_length()} bits")
print(f"B: {B.bit_length()} bits, h: {[x.bit_length() for x in h]} bits")

# Actual Delta:
Delta01 = a[0]*b[1] - a[1]*b[0]
Delta02 = a[0]*b[2] - a[2]*b[0]
Delta12 = a[1]*b[2] - a[2]*b[1]
d_true = vector(ZZ, [Delta12, -Delta02, Delta01])

# Check h . d_true == 0:
assert vector(ZZ, h) * d_true == 0

# Orthogonal lattice to h:
# Lattice L = {x in Z^3 : x . h = 0 mod n}
# Dual / kernel of h in Z^3:
M_h = Matrix(ZZ, [h])
ker_h = M_h.right_kernel()
B_ker = ker_h.basis_matrix().LLL()
v1, v2 = B_ker.rows()
if vector(v1).cross_product(vector(v2)) != vector(h):
    if vector(v1).cross_product(vector(v2)) == -vector(h):
        v2 = -v2

# Express d_true in terms of v1, v2:
# d_true = lam * v1 + mu * v2
mat_v = Matrix(ZZ, [v1, v2])
sol = mat_v.solve_left(d_true)
lam_true, mu_true = sol[0], sol[1]

print(f"lam_true: {lam_true} ({ZZ(abs(lam_true)).bit_length()} bits)")
print(f"mu_true: {mu_true} ({ZZ(abs(mu_true)).bit_length()} bits)")

# Now check T_mat and Kc:
# Orthogonal lattice to h mod n:
L_modn = Matrix(ZZ, [
    [h[0], h[1], h[2]],
