#!/usr/bin/env python3
import json
import hashlib
import random
import string
import os
from Crypto.Util.number import bytes_to_long, long_to_bytes, isPrime

FLAG = b"crypto{fake_flag_for_testing_12345___}"
BITS = 2 << 9
g = 2

def add_random_nonprintable(byte_str):
    index = random.randint(0, len(byte_str))
    non_printable_byte = random.randint(0, 255)
    while chr(non_printable_byte) in string.printable:
        non_printable_byte = random.randint(0, 255)
    return byte_str[:index] + bytes([non_printable_byte]) + byte_str[index:]

def xor(a, b):
     assert len(a) == len(b)
     return bytes(x ^ y for x, y in zip(a, b))

def xor_nonce(byte_str, nonce):
    start = byte_str[:7]
    end = byte_str[-1:]
    middle = byte_str[7:-1]
    return start + xor(middle, nonce) + bytes(end)

class SimChallenge:
    def __init__(self):
        self.nonce = os.urandom(31)
        self.refresh()
        self.your_turn = 1
        self.v = self.R.getrandbits(BITS >> 1)
        self.FLAG = bytes_to_long(
            xor_nonce(add_random_nonprintable(FLAG), self.nonce)
        )

    def getPrime(self, N):
        while True:
            number = self.R.getrandbits(N) | 1
            if isPrime(number, randfunc=lambda x: long_to_bytes(self.R.getrandbits(x))):
                break
        return number

    def refresh(self, seed=None):
        self.seed = os.urandom(8) if seed == None else seed
        self.R = random.Random(self.nonce + self.seed)

    def fiatShamir(self):
        p = self.getPrime(BITS)
        y = pow(g, self.FLAG, p)
        self.refresh()
        t = pow(g, self.v, p)
        c = bytes_to_long(
            hashlib.sha3_256(
                long_to_bytes(t ^ y ^ g ^ self.R.randint(2, BITS))
            ).digest()
        )
        r = (self.v - c * self.FLAG) % (p - 1)
        return (t, r), (g, y), p

def get_prime_from_seed(nonce: bytes, seed: bytes) -> int:
    R = random.Random(nonce + seed)
    while True:
        n = R.getrandbits(BITS) | 1
        if isPrime(n, randfunc=lambda x: long_to_bytes(R.getrandbits(x))):
            return n

def c_candidates(t: int, y: int):
    out = []
    for z in range(2, BITS + 1):
        c = bytes_to_long(hashlib.sha3_256(long_to_bytes(t ^ y ^ g ^ z)).digest())
        out.append(c)
    return out

def undo_xor_nonce(x: int, nonce: bytes) -> bytes:
    s = long_to_bytes(x, 39)
    return s[:7] + xor(s[7:-1], nonce) + s[-1:]

def strip_inserted_nonprintable(raw: bytes) -> bytes:
    for i, b in enumerate(raw):
        if chr(b) not in string.printable:
            cand = raw[:i] + raw[i + 1:]
            if cand.startswith(b"crypto{") and cand.endswith(b"}") and len(cand) == 38:
                return cand
    for i in range(len(raw)):
        cand = raw[:i] + raw[i + 1:]
        if cand.startswith(b"crypto{") and cand.endswith(b"}") and len(cand) == 38:
            return cand
    return raw

def main():
    chal = SimChallenge()
    nonce = chal.nonce

    # 1. Burn first proof
    chal.fiatShamir()
    chal.your_turn += 1
    
    # 2. Refresh with seed A
    seedA = b"A"*8
    chal.refresh(seedA)
    chal.your_turn = 0

    # 3. Get proof 1 (known seed A)
    (t1, r1), (g1, y1), p1 = chal.fiatShamir()
    chal.your_turn += 1
    
    # 4. Get proof 2 (unknown seed, but needed to increment your_turn)
    (t2, r2), (g2, y2), p2 = chal.fiatShamir()
    chal.your_turn += 1

    # 5. Refresh with seed B
    seedB = b"B"*8
    chal.refresh(seedB)
    chal.your_turn = 0

    # 6. Get proof 3 (known seed B)
    (t3, r3), (g3, y3), p3 = chal.fiatShamir()
    chal.your_turn += 1

    # Reconstruct primes
    calc_p1 = get_prime_from_seed(nonce, seedA)
    calc_p3 = get_prime_from_seed(nonce, seedB)
    assert calc_p1 == p1
    assert calc_p3 == p3

    # Generate candidate c lists
    cs1 = c_candidates(t1, y1)
    cs3 = c_candidates(t3, y3)

    m1 = p1 - 1
    m3 = p3 - 1

    # Determine k1 and k3
    k1 = 0 if r1 < (1 << 900) else 1
    k3 = 0 if r3 < (1 << 900) else 1

    # RHS = (r3 - k3 * m3) - (r1 - k1 * m1)
    rhs = (r3 - k3 * m3) - (r1 - k1 * m1)

    print("Starting optimized solver loop...")
    found = False
    
    # Target prefix bytes
    target_high = bytes_to_long(b"crypto{")
    x_min = target_high << 256
    x_max = (target_high + 1) << 256

    for c1 in cs1:
        for c3 in cs3:
            den = c1 - c3
            if den == 0:
                continue
            
            # (c1 - c3) * x = rhs
            # Check if rhs is divisible by den
            if rhs % den != 0:
                continue
                
            x = rhs // den
            if x_min <= x < x_max:
                raw = undo_xor_nonce(x, nonce)
                flag = strip_inserted_nonprintable(raw)
                if flag.startswith(b"crypto{") and flag.endswith(b"}"):
                    print(f"[+] Found FLAG: {flag.decode()}")
                    found = True
                    break
        if found:
            break

if __name__ == "__main__":
    main()
