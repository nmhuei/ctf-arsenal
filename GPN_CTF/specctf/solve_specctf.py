#!/usr/bin/env python3
from struct import pack

MASK = (1 << 64) - 1
MUL = 0xf451af975d152cad
XOR = 0xc2ceaade1a351c23
ENC = [
    0xd4274db9b97175e5,
    0x7c56450361466e9a,
    0xd3a0f1efa162aeed,
    0x44cde0d9c2d3a245,
    0x80ed0ad29bd8aa41,
    0x991653a7bfbbe2ff,
]

def unxorshr(y: int, shift: int = 33) -> int:
    x = 0
    for i in range(63, -1, -1):
        bit = (y >> i) & 1
        if i + shift < 64:
            bit ^= (x >> (i + shift)) & 1
        x |= bit << i
    return x & MASK

def hashy(x: int) -> int:
    x &= MASK
    x ^= x >> 33
    x = (x * MUL) & MASK
    x ^= x >> 33
    x ^= XOR
    x ^= x >> 33
    return x & MASK

def inv_hash(y: int) -> int:
    inv_mul = pow(MUL, -1, 1 << 64)
    x = unxorshr(y, 33)
    x ^= XOR
    x = unxorshr(x, 33)
    x = (x * inv_mul) & MASK
    x = unxorshr(x, 33)
    return x

blocks = [inv_hash(v) for v in ENC]
flag = b''.join(pack('<Q', b) for b in blocks)
print(flag.decode())

# Proof: re-hash each recovered block and compare against ENC.
assert all(hashy(b) == e for b, e in zip(blocks, ENC))
print('[ok] every recovered 8-byte block hashes back to ENC')
