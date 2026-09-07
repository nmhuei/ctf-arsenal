#!/home/light/miniforge3/envs/sage/bin/python
import os
import sys
import random
from hashlib import sha256
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from sage.all import GF, matrix, vector

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

def solve():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    chal_dir = os.path.join(os.path.dirname(script_dir), "challenge")
    out_file = os.path.join(chal_dir, "out.txt")

    with open(out_file, "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    outputs = []
    enc_flag_hex = None
    for line in lines:
        if line.startswith("Enc flag:"):
            enc_flag_hex = line.split("Enc flag:")[1].strip()
        else:
            outputs.append(int(line))

    assert len(outputs) == 625, f"Expected 625 outputs, got {len(outputs)}"
    enc_flag = bytes.fromhex(enc_flag_hex)

    print(f"Loaded {len(outputs)} outputs and enc_flag: {enc_flag_hex}")

    # Initialize symbolic MT19937 state (after first twist)
    # Each bit is represented by 1 << (k * 32 + b)
    S_sym = [[(1 << (k * 32 + b)) for b in range(32)] for k in range(624)]
    idx = 0
    eqs = []

    def get_word():
        nonlocal idx, S_sym
        if idx == 624:
            S_sym = twist_inplace_bits(S_sym)
            idx = 0
        w = temper_bits(S_sym[idx])
        idx += 1
        return w

    print("Collecting symbolic linear equations over GF(2)...")
    for i in range(len(outputs)):
        x = outputs[i]
        wA = get_word()
        wB = get_word()
        wC = get_word() # discarded

        for b in range(32):
            eqs.append((wA[b], (x >> b) & 1))
        for j in range(16):
            eqs.append((wB[j + 16], (x >> (32 + j)) & 1))

    print(f"Collected {len(eqs)} equations.")

    num_vars = 19968
    num_eqs = len(eqs)
    print(f"Constructing GF(2) matrix of size {num_eqs} x {num_vars}...")
    M = matrix(GF(2), num_eqs, num_vars)
    Y = vector(GF(2), [eq[1] for eq in eqs])

    for r in range(num_eqs):
        mask = eqs[r][0]
        while mask:
            lsb = mask & -mask
            c = lsb.bit_length() - 1
            mask ^= lsb
            M[r, c] = 1

    print("Solving linear system using SageMath M4RI...")
    sol = M.solve_right(Y)
    print("System solved successfully!")

    recovered_words = []
    for k in range(624):
        w_val = 0
        for b in range(32):
            bit_val = int(sol[k * 32 + b])
            w_val |= (bit_val << b)
        recovered_words.append(w_val)

    # Reconstruct PRNG state
    my_state = (3, tuple(recovered_words) + (0,), None)
    random.setstate(my_state)

    # Verify that reconstructed PRNG matches observed outputs
    print("Verifying reconstructed PRNG state on outputs...")
    for i in range(len(outputs)):
        x = random.getrandbits(48)
        random.getrandbits(16)
        assert x == outputs[i], f"Mismatch at output {i}!"
    print("All 625 outputs matched perfectly!")

    # Advance PRNG to match challenge script
    for i in range(10):
        x = random.getrandbits(32)

    key = sha256(str(random.getrandbits(64)).encode()).digest()
    nonce = sha256(str(random.getrandbits(64)).encode()).digest()[:16]

    cipher = AES.new(key, AES.MODE_CBC, iv=nonce)
    decrypted = cipher.decrypt(enc_flag)
    print(f"Raw decrypted: {decrypted}")

    # Unpad PKCS#7 or strip trailing padding
    try:
        flag = unpad(decrypted, 16).decode()
    except Exception:
        flag = decrypted.decode(errors="ignore")

    print(f"FLAG: {flag}")

    flag_path = os.path.join(os.path.dirname(script_dir), "flag.txt")
    with open(flag_path, "w") as f:
        f.write(flag.strip() + "\n")
    print(f"Flag saved to {flag_path}")
    return flag

if __name__ == '__main__':
    solve()

