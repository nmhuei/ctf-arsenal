#!/usr/bin/env python3
"""
Phase 2: Inverse avalanche & finalization separation
"""

from xxh3_model import MASK64, PRIME64_1, PRIME64_2, avalanche

C = 0x165667919E3779F9
C_INV = pow(C, -1, 1 << 64)

def unavalanche(h: int) -> int:
    h = h ^ (h >> 32)
    h = (h * C_INV) & MASK64
    h = h ^ (h >> 37)
    return h

def get_desired_merge_state(target_digest: bytes, length: int) -> tuple[int, int]:
    """
    Given a 16-byte target digest and the payload length,
    returns (target_sum_low, target_sum_high) such that:
    Term0_low + Term1_low + Term2_low + Term3_low == target_sum_low (mod 2^64)
    Term0_high + Term1_high + Term2_high + Term3_high == target_sum_high (mod 2^64)
    """
    assert len(target_digest) == 16
    target_high = int.from_bytes(target_digest[:8], 'big')
    target_low = int.from_bytes(target_digest[8:], 'big')

    desired_merged_low = unavalanche(target_low)
    desired_merged_high = unavalanche(target_high)

    start_low = (length * PRIME64_1) & MASK64
    start_high = (~(length * PRIME64_2)) & MASK64

    target_sum_low = (desired_merged_low - start_low) & MASK64
    target_sum_high = (desired_merged_high - start_high) & MASK64

    return target_sum_low, target_sum_high

if __name__ == "__main__":
    TARGET = b"Give me the flag"
    t_low, t_high = get_desired_merge_state(TARGET, 320)
    print(f"For length 320, TARGET={TARGET}:")
    print(f"  Target sum low:  0x{t_low:016x}")
    print(f"  Target sum high: 0x{t_high:016x}")
