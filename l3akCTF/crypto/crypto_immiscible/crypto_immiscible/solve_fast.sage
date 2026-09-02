import json
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# Load public parameters
with open('/home/light/Workspace/CTF/l3akCTF/crypto/crypto_immiscible/crypto_immiscible/public.json') as f:
    data = json.load(f)

polys_data = data['polynomials']
target = data['target']
enc_flag = bytes.fromhex(data['encrypted_flag'])

P = 79
N = 8

# Create Polynomial Ring over GF(79)
R = PolynomialRing(GF(P), 'x', N)
x = R.gens()

def parse_poly(poly_dict):
    res = GF(P)(poly_dict['const'])
    for i, c in enumerate(poly_dict['linear']):
        res += GF(P)(c) * x[i]
    for i, j, c in poly_dict['quad']:
        res += GF(P)(c) * x[i] * x[j]
    return res

print("[+] Constructing quadratic polynomial system over GF(79)...")
eqs = []
for k, poly_dict in enumerate(polys_data):
    p = parse_poly(poly_dict)
    eqs.append(p - GF(P)(target[k]))

print(f"[+] System contains {len(eqs)} quadratic equations in {N} variables.")
print("[+] Computing Gröbner basis (without degree 79 field equations)...")

I = Ideal(eqs)
gb = I.groebner_basis()

print("[+] Gröbner basis computed!")
print("GB:", gb)

variety = I.variety()
print(f"[+] Found {len(variety)} solution(s):")

for sol in variety:
    secret_sig = [int(sol[x[i]]) for i in range(N)]
    print(f"[+] Candidate secret signature: {secret_sig}")
    
    key = hashlib.sha256(bytes(secret_sig)).digest()
    cipher = AES.new(key, AES.MODE_ECB)
    try:
        pt = unpad(cipher.decrypt(enc_flag), 16)
        print("\n" + "="*50)
        print(f"[*] SUCCESS! FLAG: {pt.decode()}")
        print("="*50 + "\n")
    except Exception as e:
        print(f"[-] Decryption failed for signature {secret_sig}: {e}")
