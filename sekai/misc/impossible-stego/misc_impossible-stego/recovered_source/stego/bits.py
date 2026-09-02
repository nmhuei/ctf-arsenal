"""bits.py — little-endian bit (de)serialization helpers."""


def bytes_to_bits(data: bytes):
    for byte in data:
        for i in range(8):
            yield (byte >> i) & 1


def bits_to_bytes(bits) -> bytes:
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
    if cnt:
        out.append(acc)
    return bytes(out)
