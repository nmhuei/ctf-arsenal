load('test_sol2_w0.sage')

# w_dir:
w0_dir = w0_from_x3
w1_dir = QQ(w1)
w2_dir = QQ(w2)

w_dir = vector(QQ, [w0_dir, w1_dir, w2_dir])
print("w_dir:", w_dir)

# Scale w_dir to make it integer:
denom = lcm([x.denominator() for x in w_dir])
w_int = vector(ZZ, [ZZ(x * denom) for x in w_dir])
print("w_int:", w_int)
print("w_int bit lengths:", [abs(x).bit_length() for x in w_int])

# Test J(w_int) mod n:
ks = [(L[i][0] * pow(int(h0), -1, n)) % n for i in range(3)]
J_val = (ks[0]*w_int[0] + ks[1]*w_int[1] + ks[2]*w_int[2]) % n
print("J_val == 0 mod n:", J_val == 0)

# Check gcd with n:
for val in [J_val, J_val - 1, J_val + 1]:
    g = gcd(val, n)
    if 1 < g < n:
        print(f"[!] FACTORED N DIRECTLY FROM J_val! g = {g}")
        exit(0)

# What about s mod n:
# s^2 = H0^2 / (w_dir . L)_0^2 mod n
w_dot_L = w_dir * L
print("w_dot_L:", [RR(abs(x)).log(2).n() for x in w_dot_L])
print("H:", [RR(abs(x)).log(2).n() for x in H])

# In Zmod(n):
Zn = Zmod(n)
H0_mod = Zn(H[0])
wL0_mod = Zn(w_dot_L[0])

# s^2 mod n:
s_sq_mod = (H0_mod / wL0_mod)^2
print("s_sq_mod:", s_sq_mod)

# Test J(s * w_dir) mod n:
# J(w) = +- 1 mod p, -+ 1 mod q.
# J(s * w_dir) = s * J(w_dir)
# (s * J(w_dir))^2 = 1 mod n
# s^2 * J(w_dir)^2 = 1 mod n
J_dir_mod = Zn(ks[0]*w_dir[0] + ks[1]*w_dir[1] + ks[2]*w_dir[2])
prod = s_sq_mod * (J_dir_mod^2)
print("s^2 * J^2 == 1 mod n:", prod == 1)
print("prod:", prod)
