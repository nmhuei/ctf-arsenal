from Crypto.Util.number import long_to_bytes
import os

# Get path to output file relative to this script
script_dir = os.path.dirname(os.path.abspath(__file__))
output_file = os.path.join(script_dir, '../files/output_b0bbcffd6c89c7f6ec66b8be6669bf2d.txt')

with open(output_file, 'r') as f:
    exec(f.read())

print("[*] Loaded params. Finding approximation of p...")
# get an approximation for p
F.<x> = ZZ[]
poly = x^2 - x*hint + D*D*sqrt(n)
d = poly.roots()
p_approx = int((d[0][0]/D)^2)

print("[*] Computing exact value of p using small_roots...")
# compute the exact value of p
P.<x> = PolynomialRing(Zmod(n), implementation='NTL')
f = x + p_approx
d = f.small_roots(X=2**590, beta=0.4, epsilon=1/32)
if not d:
    print("[-] small_roots failed to find root!")
    exit(1)

p = p_approx + d[0]
assert is_prime(p)
print('[+] Recovered p')

# get the flag
flag_bits = ''.join('0' if kronecker(x, p) == -1 else '1' for x in c)
flag = long_to_bytes(int(flag_bits, 2))
print('[*] Flag:', flag.decode())

# Write flag to flag.txt
with open(os.path.join(script_dir, '../flag.txt'), 'w') as f:
    f.write(flag.decode() + '\n')
print('[+] Saved flag to flag.txt')
