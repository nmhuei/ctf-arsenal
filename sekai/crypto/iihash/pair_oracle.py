#!/usr/bin/env python3
"""
Phase 4: Pair contribution oracle
Computes the (Term_low, Term_high) contribution for any lane pair.
"""

from xxh3_model import mix2Accs, SECRET_MERGEACCS_START, SECRET_DEFAULT_SIZE, ACC_NB

def merge_pair(pair_idx: int, acc_even: int, acc_odd: int, secret: bytes) -> tuple[int, int]:
    """
    Computes (Term_low, Term_high) for lane pair pair_idx (0, 1, 2, or 3)
    given accumulators (acc_even, acc_odd) and the derived secret.
    """
    assert 0 <= pair_idx < 4
    low_offset = SECRET_MERGEACCS_START + 16 * pair_idx
    high_offset = SECRET_DEFAULT_SIZE - (ACC_NB * 8) - SECRET_MERGEACCS_START + 16 * pair_idx

    term_low = mix2Accs([acc_even, acc_odd], 0, secret, low_offset)
    term_high = mix2Accs([acc_even, acc_odd], 0, secret, high_offset)
    return term_low, term_high

if __name__ == "__main__":
    from xxh3_model import derive_secret
    secret = derive_secret(0)
    for i in range(4):
        t_l, t_h = merge_pair(i, 0, 0, secret)
        print(f"Pair {i} with (0, 0): Term_low=0x{t_l:016x}, Term_high=0x{t_h:016x}")
