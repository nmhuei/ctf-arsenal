from hashlib import sha256

from Crypto.Cipher import AES
from Crypto.Util.number import bytes_to_long
from Crypto.Util.Padding import pad
from ecdsa import curves

from solve import (
    decrypt_flag,
    nonce_from_uuid_prefix,
    recover_private_key,
    uuid_prefix_valid,
)


ORDER = curves.NIST256p.order
GENERATOR = curves.NIST256p.generator


def challenge_signature(name: str, secret_key: int, uuid_prefix: str) -> tuple[int, int, bytes]:
    digest = sha256(name.encode()).digest()
    nonce = nonce_from_uuid_prefix(uuid_prefix)
    point = nonce * GENERATOR
    r = point.x() % ORDER
    s = (pow(nonce, -1, ORDER) * (bytes_to_long(digest) + r * secret_key)) % ORDER
    return r, s, digest


def test_uuid_prefix_constraints_and_conversion():
    full_uuid = "01234567-89ab-4cde-8f01-23456789abcd"
    prefix = full_uuid[:32]

    assert len(prefix) == 32
    assert uuid_prefix_valid(prefix)
    assert nonce_from_uuid_prefix(prefix) == bytes_to_long(prefix.encode())

    assert not uuid_prefix_valid(prefix[:14] + "5" + prefix[15:])
    assert not uuid_prefix_valid(prefix[:19] + "7" + prefix[20:])
    assert not uuid_prefix_valid(prefix[:8] + "_" + prefix[9:])


def test_recover_private_key_from_six_challenge_signatures():
    secret_key = 0x123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF
    prefixes = [
        "01234567-89ab-4cde-8f01-23456789",
        "fedcba98-7654-4abc-9def-01234567",
        "deadbeef-cafe-4bad-babe-01234567",
        "13579bdf-2468-4ace-8bdf-abcdef01",
        "aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeee",
        "0123abcd-4567-4def-8abc-98765432",
    ]
    signatures = [
        challenge_signature(f"friend-{i}", secret_key, prefix)
        for i, prefix in enumerate(prefixes)
    ]

    assert recover_private_key(signatures, ORDER) == secret_key


def test_decrypt_flag_uses_fixed_width_secret_key():
    secret_key = 0x123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF
    plaintext = b"NNS{offline-aes-check}"
    encrypted = AES.new(secret_key.to_bytes(32, "big"), AES.MODE_ECB).encrypt(pad(plaintext, 16))

    assert decrypt_flag(bytes_to_long(encrypted), secret_key) == plaintext
