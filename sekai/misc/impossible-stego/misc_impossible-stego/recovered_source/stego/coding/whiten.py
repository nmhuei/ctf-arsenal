"""
whiten.py — position-dependent byte whitening.

A second diffusion layer applied after the S-box.  Each byte is XORed with a
position-dependent pad derived from the whitening key, so two identical
plaintext bytes at different offsets encode to different values.  Symmetric:
the same operation reverses it.
"""

from ..crypto.chacha20 import ChaCha20

# Distinct nonce constant so the whitening pad never coincides with the payload
# cipher's keystream even though both are ChaCha20-based.
_WHITEN_NONCE = bytes.fromhex("5713c9a04e2bd6f188305a6c")


def _pad(whiten_key: bytes, length: int) -> bytes:
    return ChaCha20(whiten_key, _WHITEN_NONCE).keystream(length)


def whiten(whiten_key: bytes, data: bytes) -> bytes:
    pad = _pad(whiten_key, len(data))
    return bytes(b ^ p for b, p in zip(data, pad))


def unwhiten(whiten_key: bytes, data: bytes) -> bytes:
    return whiten(whiten_key, data)  # XOR is its own inverse
