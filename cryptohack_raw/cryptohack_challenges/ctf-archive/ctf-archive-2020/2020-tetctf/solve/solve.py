#!/usr/bin/env python3
import socket
import sys

MASK = 0xffffffff
MATRIX_A = 0x9908b0df
UPPER = 0x80000000
LOWER = 0x7fffffff

I1 = 1396
I2 = 1792

def temper(y):
    y &= MASK
    y ^= y >> 11
    y ^= (y << 7) & 0x9d2c5680
    y ^= (y << 15) & 0xefc60000
    y ^= y >> 18
    return y & MASK

def unshift_right_xor(y, shift):
    x = 0
    for i in range(31, -1, -1):
        bit = (y >> i) & 1
        if i + shift <= 31:
            bit ^= (x >> (i + shift)) & 1
        x |= bit << i
    return x & MASK

def unshift_left_xor_mask(y, shift, mask):
    x = 0
    for i in range(32):
        bit = (y >> i) & 1
        if i - shift >= 0 and ((mask >> i) & 1):
            bit ^= (x >> (i - shift)) & 1
        x |= bit << i
    return x & MASK

def untemper(y):
    y = unshift_right_xor(y, 18)
    y = unshift_left_xor_mask(y, 15, 0xefc60000)
    y = unshift_left_xor_mask(y, 7, 0x9d2c5680)
    y = unshift_right_xor(y, 11)
    return y & MASK

def candidates(leak_1396, leak_1792):
    x1396 = untemper(leak_1396)
    x1792 = untemper(leak_1792)

    out = []
    for high_bit in (0, UPPER):
        y = high_bit | (x1396 & LOWER)
        x2019 = x1792 ^ (y >> 1)
        if y & 1:
            x2019 ^= MATRIX_A
        out.append(temper(x2019))
    return out

def attempt(host, port, candidate_choice):
    with socket.create_connection((host, port)) as s:
        f = s.makefile("rwb")

        f.readline()  # banner

        f.write(f"{I1}\n{I2}\n".encode())
        f.flush()

        leaks = {}
        for i in range(2019):
            line = f.readline().strip()
            if i in (I1, I2):
                leaks[i] = int(line)

        guess = candidates(leaks[I1], leaks[I2])[candidate_choice]
        f.write(f"{guess}\n".encode())
        f.flush()

        return f.read()

def main():
    if len(sys.argv) != 3:
        print(f"usage: {sys.argv[0]} HOST PORT")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])

    n = 0
    while True:
        n += 1
        # Alternate candidates. Each attempt has about a 50% chance.
        result = attempt(host, port, n & 1)

        if result.strip():
            print(result.decode(errors="replace"), end="")
            print(f"\nSolved after {n} attempt(s).")
            break

        print(f"attempt {n}: wrong candidate")

if __name__ == "__main__":
    main()
