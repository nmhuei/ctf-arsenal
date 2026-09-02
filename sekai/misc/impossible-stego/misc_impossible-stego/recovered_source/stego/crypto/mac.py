"""
mac.py — message authentication via truncated HMAC-SHA256.

Authenticates the encrypted frame so extraction can tell, in constant time,
whether the recovered bits form a genuine payload produced by this algorithm.
"""

import hashlib
import hmac

from .. import secret


def compute_tag(mac_key: bytes, data: bytes) -> bytes:
    return hmac.new(mac_key, data, hashlib.sha256).digest()[: secret.TAG_LEN]


def verify_tag(mac_key: bytes, data: bytes, tag: bytes) -> bool:
    return hmac.compare_digest(compute_tag(mac_key, data), tag)
