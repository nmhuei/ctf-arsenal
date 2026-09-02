"""
chacha20.py — pure-Python ChaCha20 stream cipher (RFC 8439 layout).

Used to encrypt the framed payload before it is dispersed into the image.
Implemented from scratch so the whole transform lives in this source tree.
"""

import struct

_MASK = 0xFFFFFFFF
_CONST = (0x61707865, 0x3320646E, 0x79622D32, 0x6B206574)  # "expand 32-byte k"


def _rotl(v: int, n: int) -> int:
    v &= _MASK
    return ((v << n) | (v >> (32 - n))) & _MASK


def _quarter_round(s, a, b, c, d):
    s[a] = (s[a] + s[b]) & _MASK
    s[d] = _rotl(s[d] ^ s[a], 16)
    s[c] = (s[c] + s[d]) & _MASK
    s[b] = _rotl(s[b] ^ s[c], 12)
    s[a] = (s[a] + s[b]) & _MASK
    s[d] = _rotl(s[d] ^ s[a], 8)
    s[c] = (s[c] + s[d]) & _MASK
    s[b] = _rotl(s[b] ^ s[c], 7)


def _block(key_words, counter, nonce_words):
    state = list(_CONST) + list(key_words) + [counter & _MASK] + list(nonce_words)
    working = state[:]
    for _ in range(10):  # 20 rounds = 10 column + 10 diagonal pairs
        _quarter_round(working, 0, 4, 8, 12)
        _quarter_round(working, 1, 5, 9, 13)
        _quarter_round(working, 2, 6, 10, 14)
        _quarter_round(working, 3, 7, 11, 15)
        _quarter_round(working, 0, 5, 10, 15)
        _quarter_round(working, 1, 6, 11, 12)
        _quarter_round(working, 2, 7, 8, 13)
        _quarter_round(working, 3, 4, 9, 14)
    out = [(working[i] + state[i]) & _MASK for i in range(16)]
    return struct.pack("<16I", *out)


class ChaCha20:
    def __init__(self, key: bytes, nonce: bytes, counter: int = 0):
        if len(key) != 32:
            raise ValueError("ChaCha20 key must be 32 bytes")
        if len(nonce) != 12:
            raise ValueError("ChaCha20 nonce must be 12 bytes")
        self._key_words = struct.unpack("<8I", key)
        self._nonce_words = struct.unpack("<3I", nonce)
        self._counter = counter

    def keystream(self, nbytes: int) -> bytes:
        out = bytearray()
        ctr = self._counter
        while len(out) < nbytes:
            out += _block(self._key_words, ctr, self._nonce_words)
            ctr += 1
        return bytes(out[:nbytes])

    def encrypt(self, data: bytes) -> bytes:
        ks = self.keystream(len(data))
        return bytes(b ^ k for b, k in zip(data, ks))

    # Symmetric.
    decrypt = encrypt
