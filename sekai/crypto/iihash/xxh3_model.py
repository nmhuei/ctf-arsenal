#!/usr/bin/env python3
"""
XXH3-128 long mode model (for length > 240 bytes)
Exact match with official xxHash v0.8.2 / python-xxhash
"""

PRIME32_1 = 0x9E3779B1
PRIME32_2 = 0x85EBCA77
PRIME32_3 = 0xC2B2AE3D

PRIME64_1 = 0x9E3779B185EBCA87
PRIME64_2 = 0xC2B2AE3D27D4EB4F
PRIME64_3 = 0x165667B19E3779F9
PRIME64_4 = 0x85EBCA77C2B2AE63
PRIME64_5 = 0x27D4EB2F165667C5

MASK64 = 0xFFFFFFFFFFFFFFFF
MASK32 = 0xFFFFFFFF

kSecret = bytes([
    0xb8, 0xfe, 0x6c, 0x39, 0x23, 0xa4, 0x4b, 0xbe, 0x7c, 0x01, 0x81, 0x2c, 0xf7, 0x21, 0xad, 0x1c,
    0xde, 0xd4, 0x6d, 0xe9, 0x83, 0x90, 0x97, 0xdb, 0x72, 0x40, 0xa4, 0xa4, 0xb7, 0xb3, 0x67, 0x1f,
    0xcb, 0x79, 0xe6, 0x4e, 0xcc, 0xc0, 0xe5, 0x78, 0x82, 0x5a, 0xd0, 0x7d, 0xcc, 0xff, 0x72, 0x21,
    0xb8, 0x08, 0x46, 0x74, 0xf7, 0x43, 0x24, 0x8e, 0xe0, 0x35, 0x90, 0xe6, 0x81, 0x3a, 0x26, 0x4c,
    0x3c, 0x28, 0x52, 0xbb, 0x91, 0xc3, 0x00, 0xcb, 0x88, 0xd0, 0x65, 0x8b, 0x1b, 0x53, 0x2e, 0xa3,
    0x71, 0x64, 0x48, 0x97, 0xa2, 0x0d, 0xf9, 0x4e, 0x38, 0x19, 0xef, 0x46, 0xa9, 0xde, 0xac, 0xd8,
    0xa8, 0xfa, 0x76, 0x3f, 0xe3, 0x9c, 0x34, 0x3f, 0xf9, 0xdc, 0xbb, 0xc7, 0xc7, 0x0b, 0x4f, 0x1d,
    0x8a, 0x51, 0xe0, 0x4b, 0xcd, 0xb4, 0x59, 0x31, 0xc8, 0x9f, 0x7e, 0xc9, 0xd9, 0x78, 0x73, 0x64,
    0xea, 0xc5, 0xac, 0x83, 0x34, 0xd3, 0xeb, 0xc3, 0xc5, 0x81, 0xa0, 0xff, 0xfa, 0x13, 0x63, 0xeb,
    0x17, 0x0d, 0xdd, 0x51, 0xb7, 0xf0, 0xda, 0x49, 0xd3, 0x16, 0x55, 0x26, 0x29, 0xd4, 0x68, 0x9e,
    0x2b, 0x16, 0xbe, 0x58, 0x7d, 0x47, 0xa1, 0xfc, 0x8f, 0xf8, 0xb8, 0xd1, 0x7a, 0xd0, 0x31, 0xce,
    0x45, 0xcb, 0x3a, 0x8f, 0x95, 0x16, 0x04, 0x28, 0xaf, 0xd7, 0xfb, 0xca, 0xbb, 0x4b, 0x40, 0x7e,
])

STRIPE_LEN = 64
SECRET_CONSUME_RATE = 8
ACC_NB = 8
SECRET_DEFAULT_SIZE = 192
SECRET_LASTACC_START = 7
SECRET_MERGEACCS_START = 11

def rotl64(val: int, amt: int) -> int:
    amt %= 64
    return ((val << amt) | (val >> (64 - amt))) & MASK64

def mul128_fold64(lhs: int, rhs: int) -> int:
    prod = lhs * rhs
    return ((prod & MASK64) ^ (prod >> 64)) & MASK64

def avalanche(h: int) -> int:
    h = (h ^ (h >> 37)) & MASK64
    h = (h * 0x165667919E3779F9) & MASK64
    h = (h ^ (h >> 32)) & MASK64
    return h

def derive_secret(seed: int) -> bytes:
    if seed == 0:
        return kSecret
    sec = bytearray(kSecret)
    for i in range(len(sec) // 16):
        v0 = int.from_bytes(sec[16 * i : 16 * i + 8], 'little')
        v1 = int.from_bytes(sec[16 * i + 8 : 16 * i + 16], 'little')
        v0 = (v0 + seed) & MASK64
        v1 = (v1 - seed) & MASK64
        sec[16 * i : 16 * i + 8] = v0.to_bytes(8, 'little')
        sec[16 * i + 8 : 16 * i + 16] = v1.to_bytes(8, 'little')
    return bytes(sec)

def accumulate_512(acc: list[int], stripe: bytes, secret: bytes) -> None:
    for i in range(ACC_NB):
        input_val = int.from_bytes(stripe[8 * i : 8 * i + 8], 'little')
        acc[i ^ 1] = (acc[i ^ 1] + input_val) & MASK64
        sec_val = int.from_bytes(secret[8 * i : 8 * i + 8], 'little')
        input_val ^= sec_val
        lo = input_val & MASK32
        hi = input_val >> 32
        acc[i] = (acc[i] + lo * hi) & MASK64

def scramble_acc(acc: list[int], secret: bytes) -> None:
    for i in range(ACC_NB):
        acc[i] = (acc[i] ^ (acc[i] >> 47)) & MASK64
        sec_val = int.from_bytes(secret[8 * i : 8 * i + 8], 'little')
        acc[i] = (acc[i] ^ sec_val) & MASK64
        acc[i] = (acc[i] * PRIME32_1) & MASK64

def mix2Accs(acc: list[int], offset: int, secret: bytes, sec_offset: int) -> int:
    s0 = int.from_bytes(secret[sec_offset : sec_offset + 8], 'little')
    s1 = int.from_bytes(secret[sec_offset + 8 : sec_offset + 16], 'little')
    return mul128_fold64(acc[offset] ^ s0, acc[offset + 1] ^ s1)

def mergeAccs(acc: list[int], secret: bytes, sec_offset: int, start: int) -> int:
    result = start & MASK64
    for i in range(4):
        result = (result + mix2Accs(acc, 2 * i, secret, sec_offset + 16 * i)) & MASK64
    return avalanche(result)

def xxh3_128_long(data: bytes, seed: int = 0) -> bytes:
    assert len(data) > 240, "Only long mode (> 240 bytes) supported"
    secret = derive_secret(seed)
    secret_size = len(secret)
    nb_rounds = (secret_size - STRIPE_LEN) // SECRET_CONSUME_RATE # 16
    block_len = STRIPE_LEN * nb_rounds # 1024
    nb_blocks = (len(data) - 1) // block_len
    nb_stripes = ((len(data) - 1) - (block_len * nb_blocks)) // STRIPE_LEN

    acc = [
        PRIME32_3,
        PRIME64_1,
        PRIME64_2,
        PRIME64_3,
        PRIME64_4,
        PRIME32_2,
        PRIME64_5,
        PRIME32_1,
    ]

    for n in range(nb_blocks):
        for s in range(nb_rounds):
            accumulate_512(acc, data[n * block_len + s * STRIPE_LEN : n * block_len + (s + 1) * STRIPE_LEN],
                           secret[s * SECRET_CONSUME_RATE : s * SECRET_CONSUME_RATE + STRIPE_LEN])
        scramble_acc(acc, secret[secret_size - STRIPE_LEN :])

    # last partial block
    base = nb_blocks * block_len
    for s in range(nb_stripes):
        accumulate_512(acc, data[base + s * STRIPE_LEN : base + (s + 1) * STRIPE_LEN],
                       secret[s * SECRET_CONSUME_RATE : s * SECRET_CONSUME_RATE + STRIPE_LEN])

    # last stripe is always accumulated
    p = data[len(data) - STRIPE_LEN :]
    sec_p = secret[secret_size - STRIPE_LEN - SECRET_LASTACC_START :]
    accumulate_512(acc, p, sec_p)

    low64 = mergeAccs(acc, secret, SECRET_MERGEACCS_START, len(data) * PRIME64_1)
    high_start = (~(len(data) * PRIME64_2)) & MASK64
    high_offset = secret_size - (ACC_NB * 8) - SECRET_MERGEACCS_START # 192 - 64 - 11 = 117
    high64 = mergeAccs(acc, secret, high_offset, high_start)

    return high64.to_bytes(8, 'big') + low64.to_bytes(8, 'big')
