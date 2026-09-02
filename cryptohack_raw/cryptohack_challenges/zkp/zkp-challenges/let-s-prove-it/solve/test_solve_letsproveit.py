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
        self.v = self.R.getrandbits(BITS >> 1)
        t = pow(g, self.v, p)
        c = bytes_to_long(hashlib.sha3_256(long_to_bytes(t ^ y ^ g)).digest()) ** 2
        r = (self.v - c * self.FLAG) % (p - 1)
        return (t, r), (g, y), p

def get_prime_from_seed(nonce: bytes, seed: bytes) -> int:
    R = random.Random(nonce + seed)
    while True:
        n = R.getrandbits(BITS) | 1
        if isPrime(n, randfunc=lambda x: long_to_bytes(R.getrandbits(x))):
            return n

def undo_xor_nonce(x: int, nonce: bytes) -> bytes:
    try:
        s = x.to_bytes(39, 'big')
    except OverflowError:
        s = long_to_bytes(x)
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

    # Reconstruct prime
    calc_p1 = get_prime_from_seed(nonce, seedA)
    assert calc_p1 == p1

    # c = sha3_256(t ^ y ^ g) ** 2
    c = bytes_to_long(hashlib.sha3_256(long_to_bytes(t1 ^ y1 ^ g1)).digest()) ** 2

    # Solve: c * FLAG - v = p - 1 - r
    # v = c * FLAG - (p - 1 - r)
    # Since 0 <= v < 2^512:
    # (p - 1 - r) <= c * FLAG < (p - 1 - r) + 2^512
    # FLAG is in range [(p - 1 - r) // c, (p - 1 - r + 2^512) // c]
    K = p1 - 1 - r1
    flag_min = K // c
    flag_max = (K + (1 << 512)) // c
    
    print(f"c size: {c.bit_length()} bits")
    print(f"flag range: from {flag_min} to {flag_max} (diff: {flag_max - flag_min})")

    for x in range(flag_min - 5, flag_max + 5):
        raw = undo_xor_nonce(x, nonce)
        flag = strip_inserted_nonprintable(raw)
        if flag.startswith(b"crypto{") and flag.endswith(b"}"):
            print(f"[+] Recovered: {flag.decode()}")
            break

if __name__ == "__main__":
    main()
