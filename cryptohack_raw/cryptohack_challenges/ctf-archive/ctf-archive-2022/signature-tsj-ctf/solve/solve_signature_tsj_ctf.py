#!/usr/bin/env python3
from ast import literal_eval
from hashlib import sha256
from fpylll import IntegerMatrix, LLL
from Crypto.Cipher import AES

# secp256k1 group order
q = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
BITS = 256
M = 6

def recover_private_key(sigs):
    A, b = [], []
    for z, r, s in sigs:
        row = []
        for i in range(BITS):
            zi = (z >> i) & 1
            # k = d xor z = z + sum_i (1 - 2*z_i) * d_i * 2^i
            row.append(((s * (1 - 2 * zi) - r) * ((1 << i) % q)) % q)
        A.append(row)
        b.append((z - s * z) % q)

    # Use t_i = 2*d_i - 1 in {-1, 1} so the solution vector is very short.
    C = [(2 * b[j] - sum(A[j])) % q for j in range(M)]

    dim = BITS + M + 1
    rows = []

    # Modulus rows.
    for j in range(M):
        row = [0] * dim
        row[BITS + j] = q
        rows.append(row)

    # Bit rows.
    for i in range(BITS):
        row = [0] * dim
        row[i] = 1
        for j in range(M):
            row[BITS + j] = A[j][i]
        rows.append(row)

    # Embedded target row.
    row = [0] * dim
    for j in range(M):
        row[BITS + j] = C[j]
    row[-1] = 1
    rows.append(row)

    B = IntegerMatrix.from_matrix(rows)
    LLL.reduction(B, delta=0.99, eta=0.501, method='wrapper')

    for idx in range(B.nrows):
        v = [int(B[idx, c]) for c in range(dim)]
        first, mids, last = v[:BITS], v[BITS:BITS + M], v[-1]
        if abs(last) != 1 or any(x != 0 for x in mids):
            continue
        if not all(abs(x) == 1 for x in first):
            continue

        # LLL may return the vector or its negation, so test both signs.
        for sign in (1, -1):
            bits = [(sign * x + 1) // 2 for x in first]
            if not all(x in (0, 1) for x in bits):
                continue
            d = sum(bits[i] << i for i in range(BITS))
            if 0 <= d < q and all((s * (d ^ z) - r * d - z) % q == 0 for z, r, s in sigs):
                return d
    raise RuntimeError('private key not found')

def decrypt_flag(d, ct):
    key = sha256(str(d).encode()).digest()[:16]
    known = b'Congrats! This is your flag: '

    # CTR encryption of the first known plaintext block gives the first keystream block.
    ks0 = bytes(c ^ p for c, p in zip(ct[:16], known[:16]))
    counter_block = AES.new(key, AES.MODE_ECB).decrypt(ks0)

    # PyCryptodome's default CTR layout is 8-byte nonce + 8-byte big-endian counter.
    nonce = counter_block[:8]
    initial_value = int.from_bytes(counter_block[8:], 'big')
    pt = AES.new(key, AES.MODE_CTR, nonce=nonce, initial_value=initial_value).decrypt(ct)
    return key, nonce, initial_value, pt

def main(path='signature-tsj-ctf/files/output_5537b3046f6fff95e2e175d6494321fa.txt'):
    lines = open(path, 'r').read().splitlines()
    sigs = [tuple(map(int, line.split())) for line in lines[:6]]
    ct = literal_eval(lines[6])

    d = recover_private_key(sigs)
    key, nonce, initial_value, pt = decrypt_flag(d, ct)

    print(f'd = {d}')
    print(f'd_hex = {hex(d)}')
    print(f'AES key = {key.hex()}')
    print(f'nonce = {nonce.hex()}')
    print(f'initial_value = {initial_value}')
    print(pt.decode())

if __name__ == '__main__':
    import sys
    main(sys.argv[1] if len(sys.argv) > 1 else '/mnt/data/signature-tsj-ctf/files/output_5537b3046f6fff95e2e175d6494321fa.txt')
