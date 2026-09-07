#!/usr/bin/env python3
"""
Phase 8: Payload builder
Assembles the full 320-byte payload from the 8 words of stripe 4.
"""

def build_payload(words: list[int]) -> bytes:
    """
    Given 8 64-bit words [w0, w1, ..., w7] for stripe 4,
    returns the complete 320-byte payload (4 zero stripes + stripe 4).
    """
    assert len(words) == 8, "Must provide exactly 8 words"
    stripe4 = bytearray()
    for w in words:
        stripe4.extend((w & 0xffffffffffffffff).to_bytes(8, 'little'))
    
    payload = b'\x00' * 256 + bytes(stripe4)
    assert len(payload) == 320
    assert len(payload) > 256
    return payload

if __name__ == "__main__":
    p = build_payload([0] * 8)
    print(f"Built payload of length {len(p)}: {p[:32].hex()}...{p[-32:].hex()}")
