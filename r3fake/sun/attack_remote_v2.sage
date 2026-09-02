#!/usr/bin/env sage
"""
SinGen Remote Attack — direct attempt
Recover d from biased-nonce signatures using SageMath LLL.
"""
import json, hashlib, base64, os, sys

# Load signatures
with open("/tmp/sigs_remote.json") as f: sigs = json.load(f)
N = len(sigs)
print(f"[*] Loaded {N} signatures")

ORDER = 8948962207650232551656602815159153422162609644098354511344597187200057010413418528378981730643524959857451398370029280583094215613882043973354392115544169

from sage.all import *
F = GF(ORDER)

# Prepare data
a_vals = [F(int(sigs[i]["a"])) for i in range(N)]
b_vals = [F(int(sigs[i]["b"])) for i in range(N)]

# The lattice: find d such that for each equation:
# k_i = a_i * d + b_i (mod ORDER)
# k_i = P_i * 2^128 + T_i, T_i < 2^128
#
# Since T_i is always a valid 128-bit value for ANY d,
# the ACTUAL constraint is on P_i = SHA384(salt || account_i).
# This is NOT a lattice constraint.
#
# BUT we can try the following approach:
# For the correct (d, salt):
#   k_i // 2^128 = SHA384(salt || account_i)
#   This means the 384-bit TOP of k_i is a SHA384 output.
#
# Without knowing salt, we CAN'T verify this constraint.
# BUT we can use the FACT that SHA384 outputs are
# deterministically related through the shared salt.
#
# APPROACH: Find d such that P_i = k_i >> 128 are
# consistent with SOME 256-bit salt.
# This requires searching 2^256 salt values - INFEAISIBLE.
#
# INSTEAD: Use the lattice to find d where all T_i are
# SIMULTANEOUSLY small.
#
# T_i = (a_i * d + b_i) mod ORDER mod 2^128
# For ANY d: T_i < 2^128 (always true - it's a mod 2^128!)
#
# So this doesn't constrain d either.
#
# CONCLUSION: The biased nonce alone doesn't determine d.
# The SHA384 salt constraint is the ONLY thing that makes d unique.
# Without it, the system is underdetermined.

print("[*] Trying standard HNP CVP...")

# The standard HNP lattice for finding d when nonces have known bits
# L = { (a_i * d + y_i * ORDER) for d, y_i in Z }

# Build the lattice
L = matrix(ZZ, N+1, N+1)
for i in range(N):
    L[i,i] = ORDER
    L[i,N] = int(a_vals[i])
L[N,N] = 1

# Target: (-b_0, -b_1, ..., -b_{N-1}, 0)
target = vector(ZZ, [int(-b_vals[i]) for i in range(N)] + [0])

print("[*] Running LLL reduction...")
L_lll = L.LLL()
print("[*] Done (LLL)")

# Check short vectors
found = False
for row in L_lll:
    d_cand = int(row[N])
    if d_cand == 0: continue
    d_cand = abs(d_cand)

    # Compute k_i for this d
    k_vals = [int(a_vals[i] * F(d_cand) + b_vals[i]) for i in range(N)]

    # Check: for the CORRECT d, T_i = k_i mod 2^128 should be...
    # Actually T_i is ALWAYS < 2^128 for any d.
    # The REAL constraint is P_i = k_i >> 128.

    # Check if P_i < 2^384 (always true) and P_i > 0 (almost always)
    P_vals = [k >> 128 for k in k_vals]
    if all(0 < p < (1 << 384) for p in P_vals):
        found = True
        print(f"\n[!] Candidate d in LLL: {hex(d_cand)[:40]}...")
        print(f"    P values: {[hex(p)[:20] for p in P_vals]}")

        # Test against local key
        local_path = "/home/light/Workspace/CTF/r3fake/sun/data/state.json"
        if os.path.exists(local_path):
            state = json.load(open(local_path))
            local_d = int(state["signing_scalar"], 16)
            if d_cand == local_d:
                print("    [✓] MATCHES LOCAL KEY (rare - confirms formulation)")
                # Forge token!
                from ecdsa.curves import BRAINPOOLP512r1
                G = BRAINPOOLP512r1.generator
                admin = "whale@whale-tw.com"
                msg = "SinGen Said: At sunrise, when it answers over my signal, I sit by the sun."
                while True:
                    kk = int.from_bytes(os.urandom(64), "big") % ORDER
                    if not kk: continue
                    pt = kk * G
                    rv = int(pt.x()) % ORDER
                    if not rv: continue
                    cp = json.dumps({"account":admin,"message":msg},ensure_ascii=False,sort_keys=True,separators=(",",":"))
                    zv = int.from_bytes(hashlib.sha512(cp.encode()).digest(),"big")
                    sv = int(pow(kk,-1,ORDER) * (zv + rv * d_cand) % ORDER)
                    if sv: break
                bb = lambda x: base64.urlsafe_b64encode(x).rstrip(b"=").decode()
                token = f"singen.{bb(cp.encode())}.{bb(rv.to_bytes(64,'big')+sv.to_bytes(64,'big'))}"
                print(f"\n[+] Token: {token[:80]}...")
                try:
                    BASE = open("/tmp/instance_url.txt").read().strip()
                    r = requests.post(f"{BASE}/verify", data={"token": token})
                    import re
                    m = re.search(r'NHNC\{[^}]+\}', r.text)
                    if m: print(f"\n[🏁] FLAG: {m.group(0)}")
                except: pass
                break

if not found:
    print("[-] No valid candidate in LLL output")
    print("[*] Trying BKZ with block_size=10...")
    L_bkz = L.BKZ(block_size=10)
    for row in L_bkz:
        d_cand = abs(int(row[N]))
        if d_cand == 0: continue
        print(f"\n[!] BKZ found: {hex(d_cand)[:40]}...")

# Alternative: try ALL rows of L_lll for d values
print("\n[*] Checking ALL LLL rows for potential d values...")
for idx, row in enumerate(L_lll):
    d_val = int(row[N])
    if d_val < 0: d_val += ORDER
    if d_val >= ORDER or d_val < 1: continue
    print(f"  Row {idx}: d={hex(d_val)[:20]}...")

print("\n[*] DONE - No key recovered via lattice")
print("[*] The SHA384 salt constraint is needed!")
print("[*] The challenge likely requires a different approach.")
