#!/usr/bin/env python3
"""
stego.py — recoverable, hard-to-reverse string-in-image steganography.

The hiding scheme is intentionally layered so that the embedded data is
practically impossible to locate or interpret without this source code:

  1. Key derivation      A 32-byte master key is derived with PBKDF2-HMAC-SHA256
                         from a program-internal secret combined with an optional
                         user passphrase.  Several independent sub-keys are then
                         derived from it via domain-separated hashing.

  2. Payload framing     The plaintext is wrapped as
                             MAGIC(4) | LEN(4) | DATA(LEN) | CRC32(4)
                         so extraction is self-verifying.

  3. Encryption          The whole frame is XOR-encrypted with a SHA-256
                         counter-mode keystream.  Recovered bits are noise to
                         anyone without the key.

  4. Pseudorandom scatter A keyed Fisher-Yates permutation chooses *which*
                         pixel/channel slots carry bits and in *what order*.
                         There is no sequential LSB run to detect.

  5. Matched embedding   Each carrier channel is nudged by at most +/-1 (LSB
                         "matching", not overwrite).  The LSB still equals the
                         payload bit (so it is recoverable), but the change is
                         minimal and statistically natural.

Only the R, G, B channels are used (alpha is never touched), so transparency
is preserved exactly and the visible result is essentially identical.

Usage:
    python3 stego.py embed   <in.png> <out.png> "secret text" [-p PASSPHRASE]
    python3 stego.py embed   <in.png> <out.png> --infile msg.txt [-p PASSPHRASE]
    python3 stego.py extract <out.png> [-p PASSPHRASE]
"""

import argparse
import hashlib
import hmac
import struct
import sys
import zlib

from PIL import Image

# --------------------------------------------------------------------------- #
# Program-internal secret.  This is the "you can't guess it without the source"
# anchor.  Combined with the optional passphrase during key derivation.
# --------------------------------------------------------------------------- #
_PROGRAM_SECRET = bytes.fromhex(
    "9f3c1ad77be20415c6a8e0d2473b5f81"
    "2e6498af0c7d13569b8e4a210fcd7e35"
)
_PBKDF2_SALT = b"stego::v1::pbkdf2::salt::do-not-change"
_PBKDF2_ITERS = 200_000
_MAGIC = b"SkG1"                    # frame magic, 4 bytes
_CHANNELS = 3                       # use R, G, B only (never alpha)


# --------------------------------------------------------------------------- #
# Key schedule
# --------------------------------------------------------------------------- #
def _master_key(passphrase: str) -> bytes:
    """Derive the 32-byte master key from the program secret + passphrase."""
    material = _PROGRAM_SECRET + passphrase.encode("utf-8")
    return hashlib.pbkdf2_hmac("sha256", material, _PBKDF2_SALT, _PBKDF2_ITERS)


def _subkey(master: bytes, label: bytes) -> bytes:
    """Domain-separated sub-key derivation."""
    return hmac.new(master, label, hashlib.sha256).digest()


def _keystream(key: bytes, nbytes: int):
    """SHA-256 counter-mode keystream of at least `nbytes` bytes."""
    out = bytearray()
    counter = 0
    while len(out) < nbytes:
        out += hashlib.sha256(key + struct.pack("<Q", counter)).digest()
        counter += 1
    return bytes(out[:nbytes])


class _Rng:
    """Deterministic CSPRNG yielding uniform integers, seeded from a sub-key."""

    def __init__(self, key: bytes):
        self._key = key
        self._counter = 0
        self._buf = b""
        self._pos = 0

    def _refill(self):
        self._buf = hashlib.sha256(self._key + struct.pack("<Q", self._counter)).digest()
        self._counter += 1
        self._pos = 0

    def _next_u64(self) -> int:
        if self._pos + 8 > len(self._buf):
            self._refill()
        val = struct.unpack_from("<Q", self._buf, self._pos)[0]
        self._pos += 8
        return val

    def randbelow(self, n: int) -> int:
        """Unbiased integer in [0, n) via rejection sampling."""
        if n <= 0:
            raise ValueError("n must be positive")
        if n == 1:
            return 0
        # Largest multiple of n that fits in 64 bits, for rejection sampling.
        limit = (1 << 64) - ((1 << 64) % n)
        while True:
            v = self._next_u64()
            if v < limit:
                return v % n

    def bit(self) -> int:
        return self._next_u64() & 1


def _permutation(rng: _Rng, n: int):
    """In-place Fisher-Yates permutation of range(n)."""
    perm = list(range(n))
    for i in range(n - 1, 0, -1):
        j = rng.randbelow(i + 1)
        perm[i], perm[j] = perm[j], perm[i]
    return perm


# --------------------------------------------------------------------------- #
# Frame + crypto helpers
# --------------------------------------------------------------------------- #
def _build_frame(data: bytes) -> bytes:
    body = _MAGIC + struct.pack("<I", len(data)) + data
    return body + struct.pack("<I", zlib.crc32(body) & 0xFFFFFFFF)


def _encrypt(frame: bytes, key: bytes) -> bytes:
    ks = _keystream(key, len(frame))
    return bytes(b ^ k for b, k in zip(frame, ks))


def _bytes_to_bits(data: bytes):
    for byte in data:
        for i in range(8):
            yield (byte >> i) & 1            # little-endian bit order


def _bits_to_bytes(bits) -> bytes:
    out = bytearray()
    acc = 0
    cnt = 0
    for b in bits:
        acc |= (b & 1) << cnt
        cnt += 1
        if cnt == 8:
            out.append(acc)
            acc = 0
            cnt = 0
    return bytes(out)


# --------------------------------------------------------------------------- #
# Embedding / extraction core
# --------------------------------------------------------------------------- #
def _matched_set(value: int, bit: int, coin: int) -> int:
    """Return a channel value whose LSB == bit, changed by at most +/-1."""
    if (value & 1) == bit:
        return value
    if value == 0:
        return 1
    if value == 255:
        return 254
    return value + 1 if coin else value - 1


def embed(in_path: str, out_path: str, message: bytes, passphrase: str) -> None:
    img = Image.open(in_path).convert("RGBA")
    width, height = img.size
    px = img.load()

    master = _master_key(passphrase)
    cipher_key = _subkey(master, b"cipher")
    perm_key = _subkey(master, b"permute")
    coin_key = _subkey(master, b"coin")

    payload = _encrypt(_build_frame(message), cipher_key)
    bits = list(_bytes_to_bits(payload))

    total_slots = width * height * _CHANNELS
    if len(bits) > total_slots:
        raise ValueError(
            f"message too large: needs {len(bits)} bits, capacity {total_slots}"
        )

    perm = _permutation(_Rng(perm_key), total_slots)
    coin = _Rng(coin_key)

    for bit, slot in zip(bits, perm):
        pixel_idx, channel = divmod(slot, _CHANNELS)
        y, x = divmod(pixel_idx, width)
        r, g, b, a = px[x, y]
        chans = [r, g, b]
        chans[channel] = _matched_set(chans[channel], bit, coin.bit())
        px[x, y] = (chans[0], chans[1], chans[2], a)

    img.save(out_path, "PNG")


def extract(in_path: str, passphrase: str) -> bytes:
    img = Image.open(in_path).convert("RGBA")
    width, height = img.size
    px = img.load()

    master = _master_key(passphrase)
    cipher_key = _subkey(master, b"cipher")
    perm_key = _subkey(master, b"permute")

    total_slots = width * height * _CHANNELS
    perm = _permutation(_Rng(perm_key), total_slots)

    # Keystream is generated once and reused; XOR is symmetric.
    def read_bits(count, start):
        for slot in perm[start:start + count]:
            pixel_idx, channel = divmod(slot, _CHANNELS)
            y, x = divmod(pixel_idx, width)
            yield px[x, y][channel] & 1

    header_len = len(_MAGIC) + 4          # MAGIC + LEN field
    header_bits = header_len * 8
    full_ks = None  # generated lazily once we know total size

    # Read header to discover payload length.
    header_cipher = _bits_to_bytes(read_bits(header_bits, 0))
    header_plain = bytes(
        b ^ k for b, k in zip(header_cipher, _keystream(cipher_key, header_len))
    )
    if header_plain[:4] != _MAGIC:
        raise ValueError("no valid payload found (wrong passphrase or no message)")
    (data_len,) = struct.unpack_from("<I", header_plain, 4)

    frame_len = header_len + data_len + 4   # + CRC32
    total_bits = frame_len * 8
    if total_bits > total_slots:
        raise ValueError("declared payload length exceeds image capacity")

    cipher = _bits_to_bytes(read_bits(total_bits, 0))
    frame = bytes(b ^ k for b, k in zip(cipher, _keystream(cipher_key, frame_len)))

    body, crc = frame[:-4], struct.unpack("<I", frame[-4:])[0]
    if (zlib.crc32(body) & 0xFFFFFFFF) != crc:
        raise ValueError("CRC mismatch (corrupted image or wrong passphrase)")
    data = body[len(_MAGIC) + 4:]
    return data


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def main(argv=None):
    parser = argparse.ArgumentParser(description="Hide/recover a string in an image.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    pe = sub.add_parser("embed", help="hide a string in an image")
    pe.add_argument("input")
    pe.add_argument("output")
    pe.add_argument("message", nargs="?", help="text to hide")
    pe.add_argument("--infile", help="read message from this file instead")
    pe.add_argument("-p", "--passphrase", default="", help="optional passphrase")

    px_ = sub.add_parser("extract", help="recover a hidden string")
    px_.add_argument("input")
    px_.add_argument("-p", "--passphrase", default="", help="optional passphrase")

    args = parser.parse_args(argv)

    if args.cmd == "embed":
        if args.infile:
            with open(args.infile, "rb") as fh:
                msg = fh.read()
        elif args.message is not None:
            msg = args.message.encode("utf-8")
        else:
            parser.error("provide a message argument or --infile")
        embed(args.input, args.output, msg, args.passphrase)
        print(f"Embedded {len(msg)} bytes -> {args.output}")
    elif args.cmd == "extract":
        try:
            data = extract(args.input, args.passphrase)
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            sys.exit(1)
        sys.stdout.buffer.write(data)
        if sys.stdout.isatty():
            sys.stdout.write("\n")


if __name__ == "__main__":
    main()
