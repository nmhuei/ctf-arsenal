"""
pipeline.py — the full embed/extract orchestration.

Embed transforms, in order:

    message
      -> build_frame            (MAGIC|VER|LEN|DATA|CRC32)
      -> ChaCha20 encrypt       (image-bound key + nonce)
      -> keyed S-box substitute (confusion)
      -> positional whitening   (diffusion)
      -> append HMAC tag        (authentication)
      -> scatter bits into RGB carrier slots via keyed Fisher-Yates
      -> +/-1 matched LSB write  (alpha untouched)

Extract reverses every step, authenticates with the tag, and validates the
frame's CRC and magic.  All keys derive from the baked-in secret bound to the
image geometry — there is no passphrase.
"""

from .crypto import KeySchedule, ChaCha20, Csprng, compute_tag, verify_tag
from .coding import build_frame, parse_frame, Sbox, whiten, unwhiten
from .coding.frame import HEADER_LEN, CRC_LEN, parse_header, FrameError
from .image import Carrier, slot_order, embed_bits, extract_bits
from .bits import bytes_to_bits, bits_to_bytes
from . import secret


class StegoError(Exception):
    pass


def _coin_seed(schedule: KeySchedule) -> bytes:
    # Direction of each +/-1 nudge; need not be recoverable, only deterministic.
    return schedule.derive(b"stego/v2/match-coin", 32)


def _forward_code(schedule: KeySchedule, frame: bytes) -> bytes:
    """frame -> chacha -> sbox -> whiten."""
    ct = ChaCha20(schedule.cipher_key(), schedule.nonce()).encrypt(frame)
    ct = Sbox(schedule.sbox_key()).apply(ct)
    ct = whiten(schedule.whiten_key(), ct)
    return ct


def _reverse_code(schedule: KeySchedule, blob: bytes) -> bytes:
    """whiten -> sbox -> chacha (position-aligned, so prefixes work too)."""
    x = unwhiten(schedule.whiten_key(), blob)
    x = Sbox(schedule.sbox_key()).invert(x)
    x = ChaCha20(schedule.cipher_key(), schedule.nonce()).decrypt(x)
    return x


def embed(in_path: str, out_path: str, message: bytes) -> None:
    carrier = Carrier(in_path)
    schedule = KeySchedule(carrier.width, carrier.height, carrier.channels)

    coded = _forward_code(schedule, build_frame(message))
    blob = coded + compute_tag(schedule.mac_key(), coded)

    nbits = len(blob) * 8
    if nbits > carrier.capacity_bits:
        raise StegoError(
            f"message too large: needs {nbits} bits, capacity {carrier.capacity_bits}"
        )

    order = slot_order(schedule.scatter_key(), carrier.capacity_bits)
    coin = Csprng(_coin_seed(schedule))
    embed_bits(carrier, order, bytes_to_bits(blob), coin)
    carrier.save(out_path)


def extract(in_path: str) -> bytes:
    carrier = Carrier(in_path)
    schedule = KeySchedule(carrier.width, carrier.height, carrier.channels)
    order = slot_order(schedule.scatter_key(), carrier.capacity_bits)

    # Step 1: recover just the header to learn the payload length.
    header_cipher = bits_to_bytes(extract_bits(carrier, order, HEADER_LEN * 8))
    try:
        header_plain = _reverse_code(schedule, header_cipher)
        data_len = parse_header(header_plain)
    except FrameError as exc:
        raise StegoError(f"no recoverable payload ({exc})") from None

    frame_len = HEADER_LEN + data_len + CRC_LEN
    blob_len = frame_len + secret.TAG_LEN
    if blob_len * 8 > carrier.capacity_bits:
        raise StegoError("declared length exceeds image capacity")

    # Step 2: read the whole blob, authenticate, then decode.
    blob = bits_to_bytes(extract_bits(carrier, order, blob_len * 8))
    coded, tag = blob[:frame_len], blob[frame_len:]
    if not verify_tag(schedule.mac_key(), coded, tag):
        raise StegoError("authentication failed (not a valid stego image)")

    try:
        frame = _reverse_code(schedule, coded)
        return parse_frame(frame)
    except FrameError as exc:
        raise StegoError(f"frame decode failed ({exc})") from None
