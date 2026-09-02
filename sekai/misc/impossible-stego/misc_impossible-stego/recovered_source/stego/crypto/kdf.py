"""
kdf.py — HKDF-SHA256 key schedule, bound to the cover image.

The master pseudorandom key is extracted from the baked-in ROOT_SECRET salted
with EXTRACT_SALT.  Per-purpose sub-keys are then expanded with HKDF-Expand,
where each `info` string additionally encodes the cover image's geometry
(width x height x channels).  This image-binding means a payload embedded in one
image cannot be re-derived against another, and the whole schedule shifts for
every distinct image size.
"""

import hashlib
import hmac
import struct

from .. import secret


def _hkdf_extract(salt: bytes, ikm: bytes) -> bytes:
    return hmac.new(salt, ikm, hashlib.sha256).digest()


def _hkdf_expand(prk: bytes, info: bytes, length: int) -> bytes:
    out = bytearray()
    block = b""
    counter = 1
    while len(out) < length:
        block = hmac.new(prk, block + info + bytes([counter]), hashlib.sha256).digest()
        out += block
        counter += 1
    return bytes(out[:length])


class KeySchedule:
    """Derives every sub-key the pipeline needs, bound to image geometry."""

    def __init__(self, width: int, height: int, channels: int = secret.CARRIER_CHANNELS):
        self._geom = struct.pack("<III", width, height, channels)
        self._prk = _hkdf_extract(
            secret.EXTRACT_SALT, secret.ROOT_SECRET + self._geom
        )

    def derive(self, label: bytes, length: int) -> bytes:
        info = secret.EXPAND_SALT + b"|" + label + b"|" + self._geom
        return _hkdf_expand(self._prk, info, length)

    # Convenience accessors --------------------------------------------------
    def cipher_key(self) -> bytes:
        return self.derive(secret.LABEL_CIPHER, 32)

    def nonce(self) -> bytes:
        return self.derive(secret.LABEL_NONCE, 12)

    def mac_key(self) -> bytes:
        return self.derive(secret.LABEL_MAC, 32)

    def sbox_key(self) -> bytes:
        return self.derive(secret.LABEL_SBOX, 32)

    def whiten_key(self) -> bytes:
        return self.derive(secret.LABEL_WHITEN, 32)

    def scatter_key(self) -> bytes:
        return self.derive(secret.LABEL_SCATTER, 32)
