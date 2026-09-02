import base64
import json
import os

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def encrypt(value: str, key: bytes, associated_data: str) -> str:
    nonce = os.urandom(12)
    ciphertext = AESGCM(key).encrypt(nonce, value.encode(), associated_data.encode())
    return base64.urlsafe_b64encode(nonce + ciphertext).decode()


def decrypt(token: str, key: bytes, associated_data: str) -> str:
    try:
        raw = base64.urlsafe_b64decode(token.encode())
        return (
            AESGCM(key).decrypt(raw[:12], raw[12:], associated_data.encode()).decode()
        )
    except (ValueError, InvalidTag, UnicodeDecodeError) as exc:
        raise ValueError("ciphertext authentication failed") from exc


def pack(data: dict) -> bytes:
    return json.dumps(data, separators=(",", ":"), sort_keys=True).encode()
