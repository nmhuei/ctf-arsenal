"""
scatter.py — keyed, multi-round pseudorandom ordering of carrier slots.

Produces the sequence of carrier-slot indices into which payload bits are
written.  Rather than a single shuffle, the order is the *composition* of four
independent, differently-flavoured keyed permutations.  Each stage is a
bijection over the full slot space, so their composition is guaranteed to be a
valid permutation of [0, capacity) — but reconstructing the combined ordering
without the per-round sub-keys means peeling all four layers in the right
order.

    round 0  block interleave   chop into a keyed number of blocks, permute them
    round 1  keyed rotation      global rotate + per-window rotations
    round 2  Feistel index mix   cycle-walking Feistel network over index space
    round 3  Fisher-Yates        a final full keyed shuffle

Each round's sub-key is derived from the schedule's scatter key via the
domain-separated labels in secret.LABEL_SCATTER_ROUNDS.
"""

import hashlib
import struct

from ..crypto.csprng import Csprng
from .. import secret


# --------------------------------------------------------------------------- #
# Per-round sub-key derivation
# --------------------------------------------------------------------------- #
def _round_seed(scatter_key: bytes, round_index: int) -> bytes:
    label = secret.LABEL_SCATTER_ROUNDS[round_index]
    return hashlib.sha256(scatter_key + b"|" + label).digest()


# --------------------------------------------------------------------------- #
# Round 0 — block interleave
# --------------------------------------------------------------------------- #
def _block_interleave(seq, seed: bytes):
    n = len(seq)
    if n < 4:
        return seq
    rng = Csprng(seed)
    # Keyed block count in [64, 256], clamped to the sequence length.
    nblocks = min(n, 64 + rng.randbelow(193))
    base, extra = divmod(n, nblocks)
    # Contiguous block boundaries (first `extra` blocks are one element larger).
    bounds = []
    start = 0
    for b in range(nblocks):
        size = base + (1 if b < extra else 0)
        bounds.append((start, start + size))
        start += size
    order = rng.permutation(nblocks)
    out = []
    for b in order:
        lo, hi = bounds[b]
        out.extend(seq[lo:hi])
    return out


# --------------------------------------------------------------------------- #
# Round 1 — keyed rotation (global + per-window)
# --------------------------------------------------------------------------- #
def _keyed_rotate(seq, seed: bytes):
    n = len(seq)
    if n < 2:
        return seq
    rng = Csprng(seed)
    # Global rotation.
    shift = rng.randbelow(n)
    seq = seq[shift:] + seq[:shift]
    # Per-window rotations: each fixed-size window is rotated by its own amount.
    window = 1 + rng.randbelow(max(1, n // 8 or 1))
    out = []
    for lo in range(0, n, window):
        chunk = seq[lo:lo + window]
        if len(chunk) > 1:
            r = rng.randbelow(len(chunk))
            chunk = chunk[r:] + chunk[:r]
        out.extend(chunk)
    return out


# --------------------------------------------------------------------------- #
# Round 2 — cycle-walking Feistel index permutation
# --------------------------------------------------------------------------- #
def _feistel_permutation(seq, seed: bytes):
    n = len(seq)
    if n < 2:
        return seq

    # Smallest *even* bit-width whose 2**b is >= n, so both Feistel halves are
    # equal width.  Domain D = 2**b is in [n, 4n).
    b = 1
    while (1 << b) < n:
        b += 1
    if b % 2:
        b += 1
    half = b // 2
    mask = (1 << half) - 1

    # Derive cheap, keyed round constants (4 rounds).
    rounds = 4
    digest = hashlib.sha256(seed).digest()
    mul = [(struct.unpack_from("<I", digest, 4 * r)[0] | 1) & mask for r in range(rounds)]
    add = [struct.unpack_from("<I", digest, 4 * (r + rounds))[0] & mask for r in range(rounds)]

    def permute_pow2(x: int) -> int:
        left = (x >> half) & mask
        right = x & mask
        for r in range(rounds):
            f = ((right * mul[r]) ^ (right >> 1) ^ add[r]) & mask
            left, right = right, (left ^ f) & mask
        return (left << half) | right

    # Cycle-walking restricts the 2**b-domain bijection to [0, n).
    def feistel_index(x: int) -> int:
        y = permute_pow2(x)
        while y >= n:
            y = permute_pow2(y)
        return y

    return [seq[feistel_index(i)] for i in range(n)]


# --------------------------------------------------------------------------- #
# Round 3 — final Fisher-Yates shuffle
# --------------------------------------------------------------------------- #
def _fisher_yates(seq, seed: bytes):
    n = len(seq)
    rng = Csprng(seed)
    seq = list(seq)
    for i in range(n - 1, 0, -1):
        j = rng.randbelow(i + 1)
        seq[i], seq[j] = seq[j], seq[i]
    return seq


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #
def slot_order(scatter_key: bytes, capacity_bits: int):
    """Return a permutation of [0, capacity_bits) giving slot write order.

    Built as the composition of four keyed bijections (see module docstring).
    """
    order = list(range(capacity_bits))
    order = _block_interleave(order, _round_seed(scatter_key, 0))
    order = _keyed_rotate(order, _round_seed(scatter_key, 1))
    order = _feistel_permutation(order, _round_seed(scatter_key, 2))
    order = _fisher_yates(order, _round_seed(scatter_key, 3))
    return order
