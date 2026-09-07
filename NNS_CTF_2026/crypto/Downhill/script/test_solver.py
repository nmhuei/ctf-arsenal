#!/usr/bin/env python3
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "solver"))
import solve


def test_cyclic_convolution():
    assert solve.cyclic_convolve([1, 2, 0], [3, 4, 5]) == [13, 13, 14]


def test_sparse_binary_shape():
    assert solve.is_binary_sparse_f([1, 0, 1, 0], 2)
    assert not solve.is_binary_sparse_f([1, 2, 0, 0], 2)


def test_key_derivation_matches_challenge():
    f = [1, 0, 1, 0]
    assert solve.derive_key(f).hex() == "507503b51960cceda8d924904fb85377fe7d177fb8dfcf56b24e4557644ed486"


def test_aes_decrypt_and_unpad():
    key = bytes.fromhex("00112233445566778899aabbccddeeff")
    ciphertext = solve.encrypt_for_test(key, b"NNS{offline}")
    assert solve.decrypt_flag(key, ciphertext) == b"NNS{offline}"


if __name__ == "__main__":
    for name in sorted(globals()):
        if name.startswith("test_"):
            globals()[name]()
    print("self-tests passed")
