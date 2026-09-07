#!/usr/bin/env python3
import os
import random
import xxhash
from xxh3_model import xxh3_128_long

print("[*] Running 1000 test cases for xxh3_model against python-xxhash...")

for t in range(1000):
    length = random.randint(241, 2048)
    data = os.urandom(length)
    seed = random.getrandbits(64)
    expected = xxhash.xxh3_128(data, seed=seed).digest()
    actual = xxh3_128_long(data, seed=seed)
    if expected != actual:
        print(f"[-] FAILED at test {t}: length={length}, seed={seed}")
        print(f"    Expected: {expected.hex()}")
        print(f"    Actual:   {actual.hex()}")
        exit(1)

print("[+] PASS: 1000/1000 tests passed successfully!")
