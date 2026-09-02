"""
csprng.py — deterministic CSPRNG built on ChaCha20.

Given a 32-byte seed it produces an unbounded, reproducible stream of uniform
integers.  Used to drive the keyed S-box construction and the Fisher-Yates
pixel-slot scatter, so both sender and receiver walk the identical sequence.
"""

import struct

from .chacha20 import ChaCha20

# Fixed nonce: the seed itself provides all entropy and is single-use per stream.
_PRNG_NONCE = bytes(12)


class Csprng:
    _CHUNK = 4096  # bytes of keystream pulled per refill

    def __init__(self, seed: bytes):
        if len(seed) != 32:
            raise ValueError("Csprng seed must be 32 bytes")
        self._seed = seed
        # ChaCha20 block counter advances as we consume the stream, so each
        # refill produces fresh keystream rather than re-deriving from zero.
        self._block_counter = 0
        self._buf = b""
        self._pos = 0

    def _refill(self):
        cipher = ChaCha20(self._seed, _PRNG_NONCE, counter=self._block_counter)
        self._buf = cipher.keystream(self._CHUNK)
        self._block_counter += self._CHUNK // 64
        self._pos = 0

    def _next_u32(self) -> int:
        if self._pos + 4 > len(self._buf):
            self._refill()
        val = struct.unpack_from("<I", self._buf, self._pos)[0]
        self._pos += 4
        return val

    def randbelow(self, n: int) -> int:
        """Unbiased integer in [0, n) by rejection sampling."""
        if n <= 0:
            raise ValueError("n must be positive")
        if n == 1:
            return 0
        limit = (1 << 32) - ((1 << 32) % n)
        while True:
            v = self._next_u32()
            if v < limit:
                return v % n

    def bit(self) -> int:
        return self._next_u32() & 1

    def permutation(self, n: int):
        """Fisher-Yates permutation of range(n)."""
        perm = list(range(n))
        for i in range(n - 1, 0, -1):
            j = self.randbelow(i + 1)
            perm[i], perm[j] = perm[j], perm[i]
        return perm
