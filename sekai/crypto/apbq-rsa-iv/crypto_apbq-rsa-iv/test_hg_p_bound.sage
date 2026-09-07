# Linear polynomial F(u1, u2) = u0 + R1 * u1 + R2 * u2 mod p
# Inhomogeneous in (u1, u2): u0 is the "constant" or 3-variable homogeneous?
# In Coppersmith for linear modular forms:
# Shift polynomials:
# g_{i, j, k}(u0, u1, u2) = u1^i * u2^j * F^k * n^(max(m - k, 0))
# For homogeneous in (u0, u1, u2) of total degree m:
# All monomials u0^a * u1^b * u2^c with a + b + c = m!
# How many monomials? (m + 2)*(m + 1)/2!
# For m = 2: 6 monomials!
# For m = 3: 10 monomials!
# For m = 4: 15 monomials!
# For m = 5: 21 monomials!
# For m = 6: 28 monomials!

# Let's test m from 2 to 6:
n_bits = 2048
p_bits = 1024
X_bits = 285

for m in range(2, 8):
    # Monomials of degree m in 3 variables:
    monos = []
    for a in range(m, -1, -1):
        for b in range(m - a, -1, -1):
            c = m - a - b
            monos.append((a, b, c))
    dim = len(monos)
    
    # Shifts:
    # For k = 0 .. m:
    # F^k * (monomials of degree m - k in u1, u2) with factor n^(t_k)?
    # For root mod p:
    # F(u) = p * K. So F(u)^k is divisible by p^k!
    # If we multiply by n^(m - k) = (p * q)^(m - k) = p^(m - k) * q^(m - k),
    # then the polynomial is divisible by p^k * p^(m - k) = p^m!
    # Target norm: p^m = 2^(p_bits * m)!
    
    # Det calculation:
    # Sum of powers of n:
    # For k from 0 to m:
    # Number of shifts for each k:
    # (m - k + 1) shifts?
    # Total shifts = sum_{k=0}^m (m - k + 1) = (m + 2)*(m + 1)/2 = dim!
    # Each of those (m - k + 1) shifts has factor n^(m - k)!
    sum_n_powers = sum((m - k + 1) * (m - k) for k in range(m + 1))
    
    # Sum of X weights:
    # Each of the dim monomials has degree m, so weight X^m!
    sum_X_powers = dim * m
    
    # Determinant of lattice:
    det_bits = sum_n_powers * n_bits + sum_X_powers * X_bits
    
    # Target: LLL shortest vector norm <= 2^(det_bits / dim)
    # Coppersmith condition: det_bits / dim < p_bits * m!
    minkowski_bits = det_bits / dim
    target_bits = p_bits * m
    margin = target_bits - minkowski_bits
    
    print(f"m = {m}: dim = {dim}, target = {target_bits}, minkowski = {minkowski_bits:.1f}, margin = {margin:.1f} bits")
