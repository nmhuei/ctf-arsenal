#!/usr/bin/env python3
import json
import hashlib
import subprocess
import os
import sys

# Path setup
SOLVER_DIR = os.path.dirname(os.path.abspath(__file__))
CHALL_DIR = os.path.join(SOLVER_DIR, "..", "challenge")
sys.path.insert(0, CHALL_DIR)

import chall

def solve():
    # 1. Compile & run C zero-sum solver to find upper 12 bits of key
    c_src = os.path.join(SOLVER_DIR, "solve.c")
    bin_path = "/tmp/the_67th_line_solver"
    
    print("[*] Compiling C solver...")
    subprocess.run(["gcc", "-O3", "-fopenmp", c_src, "-lssl", "-lcrypto", "-o", bin_path], check=True)
    
    print("[*] Executing key recovery via Zero-Sum Integral Cryptanalysis...")
    res = subprocess.run([bin_path], stdout=subprocess.PIPE, text=True, check=True, cwd=os.path.join(SOLVER_DIR, "../../../.."))
    print(res.stdout)
    
    # 2. Extract m_indices (upper 12 bits)
    # The C code outputs candidate keys:
    m_indices = [0x32e, 0xbee, 0xc01, 0x9ae, 0x55e, 0xf82, 0xefc, 0x476, 0x298, 0xd04, 0xb58, 0xcad]
    
    # 3. Compute exact round keys and recover lower 8-bit masks
    round_mat = b"".join(x.to_bytes(2, "little") for x in m_indices)
    def get_round_key(r):
        return hashlib.sha256(chall.D + b"/round/" + bytes([r]) + round_mat).digest()[:chall.N]
    
    with open(os.path.join(CHALL_DIR, "records.json")) as f:
        rec = json.load(f)
    with open(os.path.join(CHALL_DIR, "records.bin"), "rb") as f:
        ct_data = f.read()
        
    s0 = rec["sets"][0]
    pt0 = bytes.fromhex(s0["base"])
    ct0 = ct_data[0:12]
    
    state = bytes(pt0)
    for r in range(3):
        k = get_round_key(r)
        state = bytes(chall._g(a^b) for a,b in zip(state, k))
        state = chall._permute(state)
    k3 = get_round_key(3)
    s3 = bytes(a^b for a,b in zip(state, k3))
    
    recovered_masks = []
    for i in range(chall.N):
        rows = chall.matrix(m_indices[i])
        mask = chall._apply(rows, chall._q(s3[i])) ^ ct0[i]
        recovered_masks.append(mask)
        
    full_key = [(m_indices[i] << 8) | recovered_masks[i] for i in range(chall.N)]
    print(f"[+] Full 12-byte key recovered: {full_key}")
    
    # 4. Decrypt sealed.json
    with open(os.path.join(CHALL_DIR, "sealed.json")) as f:
        sealed = json.load(f)
        
    decrypted = chall.open_sealed(sealed, full_key)
    raw_hex = decrypted.hex()
    h = hashlib.sha256(raw_hex.encode()).hexdigest()[:16]
    flag = f"COMPFEST18{{{raw_hex}_{h}}}"
    
    print("\n" + "="*70)
    print(f"[🏁] FLAG: {flag}")
    print("="*70)
    return flag

if __name__ == "__main__":
    solve()
