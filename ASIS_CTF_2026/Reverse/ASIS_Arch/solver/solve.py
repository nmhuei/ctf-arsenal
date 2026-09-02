#!/usr/bin/env python3
"""
ASIS CTF 2026 - ASIS Arch (Reverse, 64 pts)
Solver: Analytical Inversion of the ASISARCH Custom VM 10-Round Cipher
"""

import os
import subprocess
import sys

def rol16(v, n):
    n %= 16
    return ((v << n) | (v >> (16 - n))) & 0xffff

def ror16(v, n):
    n %= 16
    return ((v >> n) | (v << (16 - n))) & 0xffff

def L(x):
    return x ^ rol16(x, 5) ^ rol16(x, 11)

def solve():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    qemu_bin = os.path.join(base_dir, 'challenge', 'ASIS-Arch', 'qemu-asisarch')
    rom_bin = os.path.join(base_dir, 'challenge', 'ASIS-Arch', 'challenge.rom')

    # Read SBOX table from ELF at 0x2160 (256 bytes)
    with open(qemu_bin, 'rb') as f:
        elf = f.read()

    sbox = list(elf[0x2160 : 0x2260])
    inv_sbox = [0] * 256
    for i, v in enumerate(sbox):
        inv_sbox[v] = i

    def sbox_word(w):
        hi = sbox[(w >> 8) & 0xff]
        lo = sbox[w & 0xff]
        return (hi << 8) | lo

    def inv_sbox_word(w):
        hi = inv_sbox[(w >> 8) & 0xff]
        lo = inv_sbox[w & 0xff]
        return (hi << 8) | lo

    # 10 Round keys extracted from ROM instruction stream
    # Each round has 22 16-bit keys for the 22 words of the 44-byte flag
    ROUND_KEYS = [
        [40503, 36366, 48709, 44700, 57043, 53034, 65377, 61368, 8191, 3126, 15373, 11332, 23707, 19666, 32041, 28000, 40359, 36350, 47669, 43532, 55875, 51866],
        [31161, 27008, 22987, 18706, 14685, 10404, 6383, 2102, 63601, 60344, 56195, 52170, 47893, 43868, 39591, 35566, 31273, 27248, 23995, 19842, 15821, 11540],
        [34283, 38354, 42393, 46400, 50447, 54518, 58557, 62564, 1059, 6122, 10193, 14232, 18247, 22286, 26357, 30396, 34427, 38434, 41449, 45520, 49567, 53574],
        [51819, 55890, 59929, 64192, 35471, 39798, 43837, 48100, 19363, 22634, 26705, 30744, 2247, 6286, 10613, 14652, 51707, 55714, 61033, 65104, 36383, 40646],
        [4919, 782, 13125, 9116, 21459, 16938, 29281, 25272, 37631, 33078, 45325, 41284, 53659, 49618, 61481, 57440, 4263, 254, 14133, 9996, 22339, 18330],
        [16962, 21115, 25136, 29417, 678, 4959, 8980, 13261, 50058, 53315, 57464, 61489, 33006, 37031, 41308, 45333, 16850, 20875, 26176, 30329, 1590, 5871],
        [47073, 42968, 38803, 34634, 63237, 59132, 54967, 50798, 13865, 9696, 5595, 1426, 30029, 25860, 21759, 17590, 46193, 42024, 37859, 33754, 62357, 58188],
        [23953, 19880, 32227, 27962, 7541, 3212, 15559, 11294, 56409, 53136, 65451, 61410, 40765, 36724, 48783, 44742, 24065, 20056, 31123, 27050, 6629, 2364],
        [12091, 16130, 3913, 8080, 28639, 32294, 20077, 24244, 44787, 48442, 36097, 40264, 60823, 64990, 52261, 56428, 11435, 15602, 2873, 6912, 27471, 31638],
        [54949, 50844, 63191, 58894, 38465, 34744, 47091, 42794, 22381, 17572, 29855, 25814, 5129, 1088, 13755, 9714, 54581, 50540, 62119, 58014, 37585, 33288]
    ]

    # Target 16-bit words extracted from ROM at 0x7ce3..
    REAL_TARGETS = [
        0x544c, 0x15a0, 0xeb44, 0x09d6, 0xb6ab, 0x496e, 0xfd0a, 0x3806,
        0xf1df, 0x0913, 0xffd8, 0x8549, 0xdebb, 0x5400, 0x261a, 0x5185,
        0xa205, 0xa0b8, 0xbe18, 0xefff, 0xb9b9, 0xe889
    ]

    def decrypt(ciphertext_words):
        w = list(ciphertext_words)
        for k in range(9, -1, -1):
            # Invert Step C: Cellular Automaton Diffusion
            for i in range(21, -1, -1):
                w[i] ^= L(w[(i + 1) % 22]) ^ rol16(L(w[(i + 2) % 22]), k + 1)
            # Invert Step B: Feistel ARX Cascade
            for i in range(21, 0, -1):
                w[i] = (w[i] - w[i - 1] - 0x5a5a) & 0xffff
            w[0] = (w[0] - w[21] - 0x5a5a) & 0xffff
            # Invert Step A: SubBytes & AddRoundKey
            for i in range(22):
                w[i] = inv_sbox_word(w[i] ^ ROUND_KEYS[k][i])
        return w

    recovered_words = decrypt(REAL_TARGETS)

    flag_bytes = bytearray(44)
    for i in range(22):
        w = recovered_words[i]
        flag_bytes[2 * i] = w & 0xff
        flag_bytes[2 * i + 1] = (w >> 8) & 0xff

    flag_str = flag_bytes.decode('utf-8')
    print(f'[+] Flag recovered: {flag_str}')

    # Verify against qemu binary
    if os.path.exists(qemu_bin) and os.path.exists(rom_bin):
        p = subprocess.Popen(
            [qemu_bin, '-M', 'asisboard', '-kernel', rom_bin, '-nographic'],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        out, _ = p.communicate(input=flag_str + '\n', timeout=5)
        if '[+] Access Granted! Flag verified.' in out:
            print('[+] QEMU verification passed: Access Granted!')
        else:
            print('[-] Verification failed!')

    return flag_str

if __name__ == '__main__':
    solve()

