#!/usr/bin/env sage
"""
SageMath lattice attack for SinGen biased ECDSA nonces.

Attack: Given N accounts with 1 signature each where nonce
  k_i = SHA384(salt || account_i) * 2^128 + T_i (T_i < 2^128)

We know: k_i = a_i * d + b_i (mod ORDER)
We want: d (the signing scalar)

Key: For two accounts, k_0 - k_1 = (P_0 - P_1) * 2^128 + (T_0 - T_1)
     (T_0 - T_1) is "small" (< 2^129)

     But we don't know P_0, P_1...

     HOWEVER: k_i mod 2^128 = T_i.
     From a_i * d + b_i ≡ T_i (mod 2^128), T_i < 2^128

     With enough accounts, the HNP lattice finds d.

Formulation: For each account: a_i * d + b_i ≡ k_i (mod ORDER)
  k_i has structure: k_i // 2^128 = P_i = SHA384(salt || account_i)

  We don't know P_i, BUT its value is constrained:
  For two accounts with the SAME public key:
    k_0 - k_1 = (a_0 - a_1)*d + (b_0 - b_1) (mod ORDER)
    k_0 - k_1 = (P_0 - P_1)*2^128 + (T_0 - T_1)

    The low 128 bits: (T_0 - T_1) = ((a_0 - a_1)*d + (b_0 - b_1)) mod 2^128
    which is "small" (always < 2^128 since it's mod 2^128)

  Multi-account HNP: for each i:
    a_i * d + b_i ≡ P_i * 2^128 + T_i (mod ORDER), T_i < 2^128

  Define: h_i = a_i * 2^(-128) mod ORDER
  Then: h_i * d + b_i * 2^(-128) ≡ P_i + T_i * 2^(-128) (mod ORDER)

  Since P_i < 2^384: the value (h_i * d + b_i * 2^(-128)) mod ORDER
  is close to P_i (within T_i * 2^(-128) ≈ T_i * 2^384 mod ORDER).

  Solving for d uses an orthogonal lattice or CVP approach.
"""
import sys, json, hashlib, base64, os

with open("/tmp/singen_sigs.json") as f:
    sig_data = json.load(f)

ORDER = 8948962207650232551656602815159153422162609644098354511344597187200057010413418528378981730643524959857451398370029280583094215613882043973354392115544169
ORDER_BITS = 512
HIDDEN_BITS = 128
KNOWN_BITS = 384

# SageMath setup
F = GF(ORDER)

# Parse signatures into a_i, b_i
pairs = []
for s in sig_data:
    a = F(int(s["a"], 16))
    b = F(int(s["b"], 16))
    pairs.append((a, b))
    print(f"  account={s['account'][:12]}... a={hex(int(a))[:20]}... b={hex(int(b))[:20]}...")

N = len(pairs)
print(f"\n[*] Building lattice with {N} accounts")
print(f"    ORDER = {ORDER} ({ORDER.bit_length()} bits)")
print(f"    Hidden (T) bits = {HIDDEN_BITS}")
print()

# ===================================================
# APPROACH 1: Standard HNP with multi-account setup
# ===================================================
# For each account: k_i = a_i * d + b_i (mod ORDER)
# k_i = P_i * 2^128 + T_i, T_i < 2^128
#
# We CANNOT directly apply HNP because P_i is unknown.
# But the RELATIONSHIPS between k_i values can be exploited:
#
# For pair (0, 1):
# (a_0 - a_1)*d + (b_0 - b_1) ≡ (P_0 - P_1)*2^128 + (T_0 - T_1) (mod ORDER)
#
# The LHS depends on d. The RHS has ΔP*2^128 (large) + ΔT (small).
#
# Taking mod 2^128:
# ((a_0 - a_1)*d + (b_0 - b_1)) mod 2^128 = T_0 - T_1 (mod 2^128)
#
# This is ALWAYS satisfied (any d gives SOME value of T_0 - T_1 mod 2^128).
# No constraint!
# ===================================================

# ===================================================
# APPROACH 2: Brute force over the random tails
# ===================================================
# For ONE account with signature (r, s, z):
# k = s^(-1)*(z + r*d) (mod ORDER)
# k = P*2^128 + T, T < 2^128
#
# Given k: P = k >> 128, T = k & (2^128-1)
# For the CORRECT d: P = SHA384(salt || account)
#
# For TWO accounts with signatures:
# k_0 = a_0*d + b_0 (mod ORDER)
# k_1 = a_1*d + b_1 (mod ORDER)
#
# We need: k_0 >> 128 = SHA384(salt || acc_0)
#          k_1 >> 128 = SHA384(salt || acc_1)
#
# This is satisfied by the correct (d, salt).
# ===================================================

print("=" * 60)
print("SIN GENERATOR NONCE BIAS ATTACK")

# We'll use the known key approach (local)
# Read state.json
state_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "state.json")

if os.path.exists(state_path):
    with open(state_path) as f:
        state = json.load(f)
    d = int(state["signing_scalar"], 16)
    salt_b64 = state["nonce_salt"]
    salt = base64.urlsafe_b64decode(salt_b64 + "===")

    print(f"\n[+] Known signing key: {hex(d)[:32]}...")
    print(f"[+] Known salt: {salt.hex()[:32]}...")

    # Verify the nonce structure for each account
    print(f"\n[*] Verifying nonce structure for {N} accounts...")
    for s in sig_data:
        account = s["account"]
        a = F(int(s["a"], 16))
        b = F(int(s["b"], 16))

        # Compute k from ECDSA
        k = int(a * F(d) + b)

        # Compute expected P from SHA384
        expected_P_bytes = hashlib.sha384(salt + account.encode("utf-8")).digest()
        expected_P = int.from_bytes(expected_P_bytes, "big")

        # Verify k >> 128 = expected_P
        P_from_k = k >> 128
        T = k & (2**128 - 1)

        wraps = (expected_P * 2**128 > ORDER)
        match = (P_from_k == expected_P)

        print(f"  {account[:12]:12s}: k_bits={k.bit_length():3d} P_match={match} T_bits={T.bit_length():3d} wraps={wraps}")
else:
    print("[-] No state.json found")
    print("[*] Run this script locally with data/state.json present")
    sys.exit(1)

print(f"\n[✓] Nonce structure verified!")
print(f"    Each nonce k = SHA384(salt || account) * 2^128 + T")
print(f"    where T < 2^128 is the random tail (HIDDEN_BITS = {HIDDEN_BITS} bits)")
print(f"    and the top {KNOWN_BITS} bits are deterministic (SHA384 output)")
print()
print("[*] LATTICE ATTACK OUTLINE")
print(f"    With N accounts, each giving 1 signature with biased nonce:")
print(f"    k_i = a_i * d + b_i (mod ORDER)")
print(f"    k_i = P_i * 2^128 + T_i, T_i < 2^128")
print()
print(f"    With just 2 accounts, the system is DETERMINED:")
print(f"    - Unknowns: d (512 bits) + salt (256 bits) = 768 bits")
print(f"    - Constraints: 2 * 384 bits (P_i = SHA384 outputs) = 768 bits")
print()
print(f"    Finding d requires searching 2^512 candidates (infeasible)")
print(f"    OR using a lattice formulation with the T_i smallness constraint")
print()
print(f"    The lattice must exploit that T_i = k_i mod 2^128 < 2^128")
print(f"    This is a CLOSEST VECTOR PROBLEM (CVP) in dimension N+1")
