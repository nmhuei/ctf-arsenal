"""
secret.py — the baked-in algorithmic secrets.

Per design, ALL security lives in the algorithm: there is no passphrase.
Everything an attacker would need to recover the payload is derived from the
constants in this file combined with the cover image's own dimensions.  Without
this exact source, the key schedule, cipher nonce, S-box and scatter pattern
are unknowable.
"""

# 64-byte root secret.  Fed into the HKDF-style key schedule (see crypto.kdf).
ROOT_SECRET = bytes.fromhex(
    "9f3c1ad77be20415c6a8e0d2473b5f812e6498af0c7d13569b8e4a210fcd7e35"
    "0b71d4e8a93c25f6178d6ae0c4b39f52d80a17e36cf4928b5a0e1d7c63840fb9"
)

# Independent salts for the extract/expand phases of key derivation.
EXTRACT_SALT = bytes.fromhex("c4f1e009ab7d3325be6610f29d4a7c81")
EXPAND_SALT = bytes.fromhex("17be40d9c2a85f3361049e7daf28cb50")

# Seed used to grow the keyed bijective S-box (see coding.sbox).
SBOX_SEED = bytes.fromhex("6d2a9fe4c70b15883ad1ce62740bf99e")

# Frame identity.  MAGIC is checked after decryption to confirm a clean recover.
MAGIC = b"\x53\x6b\x47\x32"          # "SkG2"
VERSION = 2

# Domain-separation labels for the key schedule.  Changing any of these
# silently invalidates all previously embedded images.
LABEL_CIPHER = b"stego/v2/chacha20-stream-key"
LABEL_NONCE = b"stego/v2/chacha20-nonce"
LABEL_MAC = b"stego/v2/hmac-authentication"
LABEL_SBOX = b"stego/v2/sbox-permutation"
LABEL_WHITEN = b"stego/v2/positional-whitening"
LABEL_SCATTER = b"stego/v2/pixel-slot-scatter"

# Per-round sub-labels for the multi-stage scatter (see image/scatter.py).
# Each derives an independent sub-key so every shuffle round is keyed
# differently; their composition is still a single bijection over all slots.
LABEL_SCATTER_ROUNDS = (
    b"stego/v2/scatter/round-0/block-interleave",
    b"stego/v2/scatter/round-1/keyed-rotate",
    b"stego/v2/scatter/round-2/feistel-mix",
    b"stego/v2/scatter/round-3/fisher-yates",
)

# Only R, G, B are ever used as carriers; alpha is preserved bit-for-bit.
CARRIER_CHANNELS = 3

# Authentication tag length in bytes (truncated HMAC-SHA256).
TAG_LEN = 16
