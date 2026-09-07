#!/usr/bin/env python3
"""
Phase 7, 8, 9, 10: Complete solve script for iihash - XXH3-128 Preimage Attack

Flow:
1. Target: b"Give me the flag"
2. Decompose into desired merge state via inverse avalanche.
3. Solve decoupled HIGH (Pair 0 + Pair 2) and LOW (Pair 1 + Pair 3) equations
   using van Oorschot-Wiener parallel collision search (vow_solver).
4. Construct the 320-byte payload (4 zero stripes + solved stripe 4).
5. Verify with xxhash.xxh3_128(payload, seed).digest() == b"Give me the flag".
6. If connecting to challenge process / remote server, submit payload to Get Flag.
"""

import sys
import os
import argparse
import xxhash
from correction_solver import solve_correction
from payload_builder import build_payload

TARGET_DIGEST = b"Give me the flag"
MIN_PAYLOAD_LEN = 256

def find_preimage(seed: int, target_digest: bytes = TARGET_DIGEST) -> bytes:
    print(f"[*] Starting preimage attack for seed = {hex(seed)}...")
    print(f"[*] Target digest: {target_digest} (hex: {target_digest.hex()})")

    # Phase 6 & 7: Solve for the 8 words of stripe 4
    words = solve_correction(seed, target_digest)
    print(f"[+] Solved stripe 4 words: {[hex(w) for w in words]}")

    # Phase 8: Build final payload
    payload = build_payload(words)
    print(f"[+] Assembled payload: length = {len(payload)} bytes")
    print(f"    Payload hex: {payload.hex()}")

    # Phase 9: Verify
    assert len(payload) > MIN_PAYLOAD_LEN, f"Payload must be > {MIN_PAYLOAD_LEN}"
    computed = xxhash.xxh3_128(payload, seed=seed).digest()
    print(f"[*] Computed digest: {computed}")
    assert computed == target_digest, f"Digest mismatch: {computed.hex()} != {target_digest.hex()}"
    print("[+] *** VERIFICATION PASSED: Preimage matches target digest! ***")

    return payload

def solve_local_challenge():
    """
    Spawns the local challenge.py, retrieves its seed or tests end-to-end,
    and grabs the flag.
    """
    from crypto_iihash.challenge import XXH3Challenge
    print("\n[*] Initializing local XXH3Challenge instance...")
    chall = XXH3Challenge()
    seed = chall.seed
    print(f"[+] Target challenge seed: {hex(seed)}")

    payload = find_preimage(seed)
    
    # Verify with challenge verification logic
    if xxhash.xxh3_128(payload, seed=chall.seed).digest() == TARGET_DIGEST:
        flag_path = os.path.join(os.path.dirname(__file__), "crypto_iihash", "flag.txt")
        print("[+] Challenge flag_mode target verified!")
        if os.path.exists(flag_path):
            print(f"[+] Flag: {open(flag_path).read().strip()}")
    else:
        print("[-] Challenge verification failed.")

def main():
    parser = argparse.ArgumentParser(description="XXH3-128 Preimage Attack Solver")
    parser.add_argument("--seed", type=lambda x: int(x, 0), default=None, help="Target seed (hex or int)")
    parser.add_argument("--test-local", action="store_true", help="Run against local challenge instance")
    args = parser.parse_args()

    if args.test_local:
        solve_local_challenge()
    elif args.seed is not None:
        payload = find_preimage(args.seed)
        print("\n[+] Final Payload (hex):")
        print(payload.hex())
    else:
        # Default test run with a random seed
        import random
        seed = random.getrandbits(64)
        print(f"[*] No seed specified, testing with random seed: {hex(seed)}")
        payload = find_preimage(seed)
        print("\n[+] Final Payload (hex):")
        print(payload.hex())

if __name__ == "__main__":
    main()
