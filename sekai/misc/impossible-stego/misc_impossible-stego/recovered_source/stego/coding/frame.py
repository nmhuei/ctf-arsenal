"""
frame.py — the on-image payload frame.

Layout (all integers little-endian), before encryption:

    MAGIC   (4)   identity check after decrypt
    VERSION (1)   format version
    LEN     (4)   length of DATA in bytes
    DATA    (LEN) the user's message bytes
    CRC32   (4)   integrity check over MAGIC..DATA

The encrypted form of this frame is what gets authenticated and dispersed.
"""

import struct
import zlib

from .. import secret


class FrameError(Exception):
    pass


_HEADER = struct.Struct("<4sBI")          # MAGIC, VERSION, LEN
HEADER_LEN = _HEADER.size                  # 9 bytes
CRC_LEN = 4


def build_frame(data: bytes) -> bytes:
    head = _HEADER.pack(secret.MAGIC, secret.VERSION, len(data))
    body = head + data
    crc = zlib.crc32(body) & 0xFFFFFFFF
    return body + struct.pack("<I", crc)


def parse_header(frame_prefix: bytes):
    """Return (data_len,) from at least HEADER_LEN bytes; validate magic/version."""
    if len(frame_prefix) < HEADER_LEN:
        raise FrameError("truncated header")
    magic, version, data_len = _HEADER.unpack_from(frame_prefix, 0)
    if magic != secret.MAGIC:
        raise FrameError("bad magic")
    if version != secret.VERSION:
        raise FrameError(f"unsupported version {version}")
    return data_len


def parse_frame(frame: bytes) -> bytes:
    data_len = parse_header(frame)
    expected = HEADER_LEN + data_len + CRC_LEN
    if len(frame) < expected:
        raise FrameError("truncated frame")
    body = frame[: HEADER_LEN + data_len]
    (crc,) = struct.unpack_from("<I", frame, HEADER_LEN + data_len)
    if (zlib.crc32(body) & 0xFFFFFFFF) != crc:
        raise FrameError("CRC mismatch")
    return body[HEADER_LEN:]
