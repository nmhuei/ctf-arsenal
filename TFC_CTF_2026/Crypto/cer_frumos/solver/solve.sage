from sage.all import *
import time, os, sys
from hashlib import sha256
from Crypto.Cipher import AES
import random

chall_dir = "/home/light/Workspace/CTF/TFC_CTF_2026/Crypto/cer_frumos/challenge"
with open(os.path.join(chall_dir, "out.txt")) as f:
    lines = [line.strip() for line in f if line.strip()]

outputs = [int(line) for line in lines[:-1]]
enc_flag_hex = lines[-1].split(': ')[1].strip()
enc_flag = bytes.fromhex(enc_flag_hex)

def temper_bits(w):
    w = list(w)
    orig = list(w)
    for i in range(32):
        if i + 11 < 32:
            w[i] ^= orig[i + 11]
    orig = list(w)
    C1 = 0x9D2C5680
    for i in range(32):
        if (C1 >> i) & 1 and i >= 7:
            w[i] ^= orig[i - 7]
    orig = list(w)
    C2 = 0xEFC60000
    for i in range(32):
        if (C2 >> i) & 1 and i >= 15:
            w[i] ^= orig[i - 15]
    orig = list(w)
    for i in range(32):
        if i + 18 < 32:
            w[i] ^= orig[i + 18]
    return w

def twist_inplace_bits(mt):
    N = 624
    M = 397
    A = 0x9908b0df
    mt = [list(w) for w in mt]

    def update_word(kk, other_idx, next_idx):
        b0 = mt[next_idx][0]
        new_w = [0] * 32
        for b in range(32):
            bit = mt[other_idx][b]
            if b == 30:
                bit ^= mt[kk][31]
            elif b < 30:
                bit ^= mt[next_idx][b + 1]
            if (A >> b) & 1:
                bit ^= b0
            new_w[b] = bit
        mt[kk] = new_w

    for kk in range(N - M):
        update_word(kk, kk + M, kk + 1)
    for kk in range(N - M, N - 1):
        update_word(kk, kk + (M - N), kk + 1)
    update_word(N - 1, M - 1, 0)
    return mt

S_sym = [[(1 << (k * 32 + b)) for b in range(32)] for k in range(624)]
idx = 0
eqs = []

def get_word():
    global idx, S_sym
    if idx == 624:
        S_sym = twist_inplace_bits(S_sym)
        idx = 0
    w = temper_bits(S_sym[idx])
    idx += 1
    return w

for i in range(len(outputs)):
    x = outputs[i]
    wA = get_word()
    wB = get_word()
    wC = get_word()

    for b in range(32):
        eqs.append((wA[b], (x >> b) & 1))
    for j in range(16):
        eqs.append((wB[j + 16], (x >> (32 + j)) & 1))

num_vars = 19968
take_eqs = len(eqs)
M = matrix(GF(2), take_eqs, num_vars)
Y = vector(GF(2), [eq[1] for eq in eqs])

for r in range(take_eqs):
    mask = eqs[r][0]
    while mask:
        lsb = mask & -mask
        c = lsb.bit_length() - 1
        mask ^= lsb
        M[r, c] = 1

sol = M.solve_right(Y)

recovered_words = []
for k in range(624):
    w_val = 0
    for b in range(32):
        if sol[k * 32 + b] == 1:
            w_val |= (1 << b)
    recovered_words.append(w_val)

my_state = (3, tuple(recovered_words) + (0,), None)
random.setstate(my_state)

for i in range(len(outputs)):
    x_test = random.getrandbits(48)
    random.getrandbits(16)

for i in range(10):
    x = random.getrandbits(32)

key = sha256(str(random.getrandbits(64)).encode()).digest()
nonce = sha256(str(random.getrandbits(64)).encode()).digest()[:16]

cipher = AES.new(key, AES.MODE_CBC, iv=nonce)
dec = cipher.decrypt(enc_flag)
pad = dec[-1]
flag = dec[:-pad].decode()
print("RECOVERED FLAG:", flag)

flag_path = "/home/light/Workspace/CTF/TFC_CTF_2026/Crypto/cer_frumos/flag.txt"
with open(flag_path, "w") as f:
    f.write(flag)
