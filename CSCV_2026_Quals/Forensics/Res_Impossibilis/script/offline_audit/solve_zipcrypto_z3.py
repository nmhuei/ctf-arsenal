#!/usr/bin/env python3
"""Find a printable preimage for the recovered ZIPCrypto key state.

This is an exploratory verifier: any preimage must still be distinguished from
the original password by independent forensic evidence.
"""
import argparse
import z3

TARGET = (0x670E8462, 0x306591B4, 0x8372919D)
MASK32 = 0xFFFFFFFF
POLY = z3.BitVecVal(0xEDB88320, 32)


def crc_byte(value, byte):
    current = value ^ z3.ZeroExt(24, byte)
    for _ in range(8):
        current = z3.LShR(current, 1) ^ z3.If(
            (current & z3.BitVecVal(1, 32)) == z3.BitVecVal(1, 32),
            POLY,
            z3.BitVecVal(0, 32),
        )
    return current


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("length", type=int)
    parser.add_argument("--alphabet", default="printable", choices=("printable", "alnum", "lower", "hex"))
    parser.add_argument("--timeout-ms", type=int, default=60000)
    args = parser.parse_args()
    alphabets = {
        "printable": bytes(range(32, 127)),
        "alnum": b"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
        "lower": b"abcdefghijklmnopqrstuvwxyz",
        "hex": b"0123456789abcdef",
    }

    chars = [z3.BitVec(f"c{i}", 8) for i in range(args.length)]
    solver = z3.Solver()
    solver.set(timeout=args.timeout_ms)
    for char in chars:
        solver.add(z3.Or(*(char == z3.BitVecVal(value, 8) for value in alphabets[args.alphabet])))

    key0 = z3.BitVecVal(0x12345678, 32)
    key1 = z3.BitVecVal(0x23456789, 32)
    key2 = z3.BitVecVal(0x34567890, 32)
    multiplier = z3.BitVecVal(134775813, 32)
    for char in chars:
        key0 = crc_byte(key0, char)
        key1 = (key1 + (key0 & z3.BitVecVal(0xFF, 32))) * multiplier + z3.BitVecVal(1, 32)
        key2 = crc_byte(key2, z3.Extract(31, 24, key1))
    solver.add(key0 == z3.BitVecVal(TARGET[0], 32))
    solver.add(key1 == z3.BitVecVal(TARGET[1], 32))
    solver.add(key2 == z3.BitVecVal(TARGET[2], 32))
    result = solver.check()
    print(result)
    if result == z3.sat:
        model = solver.model()
        password = bytes(model.eval(char, model_completion=True).as_long() for char in chars)
        print(password.decode("ascii"))


if __name__ == "__main__":
    main()
