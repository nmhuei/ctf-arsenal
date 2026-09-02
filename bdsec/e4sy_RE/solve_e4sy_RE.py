#!/usr/bin/env python3
"""BDSec CTF 2026 - e4sy_RE solver.

The 41-char branch of main() does, for i in 0..40:
    v32 = input[i] ^ key_part_b[i & 7] ^ key_part_a[i & 7]
    v70[(13 * i) % 41] = (((11 * i) & 0xff) ^ 0x23) + ROL1(v32, i % 7 + 1)   # byte add mod 256
then compares v70 (byte-wise) against expected.3 (41 bytes @ file offset 0x2420).

Inverse (all byte ops mod 256):
    val = expected[(13 * i) % 41] - (((11 * i) & 0xff) ^ 0x23)
    v32 = ROR1(val, i % 7 + 1)
    flag[i] = v32 ^ key_part_b[i & 7] ^ key_part_a[i & 7]
"""

import subprocess

EXPECTED = bytes.fromhex(
    "2305 791b 6cc1 840f 88b2 7deb a07e f432 "
    "c6f5 70c1 c526 bf16 dd42 363a 6a6a 4517 "
    "f44c cd84 ae27 8cc8 38"
)
KEY_B = bytes.fromhex("5b75 b47b cb5d 73e6")  # key_part_b @ 0x2450
KEY_A = bytes.fromhex("19a4 c752 6e01 9bf0")  # key_part_a @ 0x2458


def rol1(x: int, n: int) -> int:
    x &= 0xFF
    n %= 8
    return ((x << n) | (x >> (8 - n))) & 0xFF if n else x


def ror1(x: int, n: int) -> int:
    return rol1(x, 8 - (n % 8))


def solve() -> bytes:
    assert len(EXPECTED) == 41 and len(KEY_A) == 8 and len(KEY_B) == 8
    flag = bytearray(41)
    for i in range(41):
        target = EXPECTED[(13 * i) % 41]
        const = ((11 * i) & 0xFF) ^ 0x23
        val = (target - const) & 0xFF
        v32 = ror1(val, i % 7 + 1)
        flag[i] = v32 ^ KEY_B[i & 7] ^ KEY_A[i & 7]
    return bytes(flag)


def forward(flag: bytes) -> bytes:
    """Recompute the forward transform to prove the inverse is exact."""
    v70 = bytearray(41)
    for i in range(41):
        v32 = flag[i] ^ KEY_B[i & 7] ^ KEY_A[i & 7]
        v70[(13 * i) % 41] = ((((11 * i) & 0xFF) ^ 0x23) + rol1(v32, i % 7 + 1)) & 0xFF
    return bytes(v70)


if __name__ == "__main__":
    flag = solve()
    print("flag      :", flag.decode(errors="replace"))
    print("forward== :", forward(flag).hex() == EXPECTED.hex())
    print("expected :", EXPECTED.hex())
    print("got      :", forward(flag).hex())

    # Verify against the real binary (copy in /tmp/re/e4sy/).
    try:
        p = subprocess.run(
            ["/tmp/re/e4sy/e4sy_RE.bdsec"], input=flag + b"\n",
            capture_output=True, timeout=10,
        )
        out = p.stdout.decode(errors="replace")
        print("--- binary output (stdout) ---")
        print(out)
        print("--- binary output (stderr) ---")
        print(p.stderr.decode(errors="replace"))
    except FileNotFoundError:
        print("(binary copy not found; skipped live verification)")


# ---------------------------------------------------------------------------
# Appendix: the 24 / 26 / 29-char branches are ALSO real, accepted "flags".
# Every length branch has its own constant array (ELF symbols, addr == file off):
#   expected.0 @ 0x23c0 (24)   expected.1 @ 0x23e0 (26)   expected.2 @ 0x2400 (29)
# They are distinct decoy flags; only the 41-char branch (expected.3 @ 0x2420,
# + key parts @ 0x2450/0x2458) carries the competition flag "BDSEC{...}".
# Success-labels: 41-char -> "Excellent work, reverse engineer!",
#                 others    -> "Congratulations! You found a flag!".
# ---------------------------------------------------------------------------
BIN = "/home/light/Workspace/CTF/bdsec/e4sy_RE/e4sy_RE.bdsec"  # read-only


def _decoy_29() -> bytes:
    """branch v9==29: first 16 bytes ROL2(s+xmmword_2480)^xmmword_24D0 == expected.2[0..15]
    (= xmmword_2490), next 13 bytes ROL2((81+3k)+s[16+k])^0xA7 == expected.2[16..28]."""
    b = open(BIN, "rb").read()
    exp2 = b[0x2400:0x2400 + 29]                 # expected.2 == xmmword_2490 || unk_2410
    x2480 = b[0x2480:0x2480 + 16]                # xmmword_2480 (addend, bytes 0-15)
    x24d0 = b"\xa7" * 16                          # xmmword_24D0 (xor mask, bytes 0-15)
    f = bytearray(29)
    for i in range(16):
        f[i] = (ror1(exp2[i] ^ x24d0[i], 2) - x2480[i]) & 0xFF
    for k in range(13):
        f[16 + k] = (ror1(exp2[16 + k] ^ 0xA7, 2) - (81 + 3 * k)) & 0xFF
    return bytes(f)


def _decoy_26() -> bytes:
    M = 0xCCCCCCCCCCCCCCCD
    exp1 = open(BIN, "rb").read()[0x23E0:0x23E0 + 26]
    f = bytearray(26)
    for i in range(26):
        n = (i - (i // 5 + (((M * i) >> 64) & 0xFC)) + 1) & 0xFF
        f[i] = rol1(exp1[(5 * i) % 26], n % 8) ^ ((61 + 7 * i) & 0xFF)
    return bytes(f)


def _decoy_24() -> bytes:
    exp0 = open(BIN, "rb").read()[0x23C0:0x23C0 + 24]
    prev, f = 107, bytearray(24)
    for i in range(24):
        sx = (ror1(exp0[i], 3) - prev) & 0xFF
        f[i] = sx ^ ((85 + 17 * i) & 0xFF)
        prev = (prev + sx) & 0xFF
        prev = rol1(prev, 3)
    return bytes(f)


def solve_decoys():
    return _decoy_24(), _decoy_26(), _decoy_29()
