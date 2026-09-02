from math import isqrt

N = 2597749519984520018193538914972744028780767067373210633843441892910830749749277631182596420937027368405416666234869030284255514216592219508067528406889067888675964979055810441575553504341722797908073355991646423732420612775191216409926513346494355434293682149298585

def unpair(z):
    w = (isqrt(8*z + 1) - 1) // 2
    j = z - w * (w + 1) // 2
    i = w - j
    return i, j

def decode(z, length):
    if length == 1:
        return [z]

    left_len = length - length // 2
    right_len = length // 2

    a, b = unpair(z)

    return decode(a, left_len) + decode(b, right_len)

for length in range(1, 200):
    arr = decode(N, length)

    if all(32 <= x < 127 for x in arr):
        s = bytes(arr)
        if b"zh3r0{" in s:
            print("length =", length)
            print(s.decode())
            break
