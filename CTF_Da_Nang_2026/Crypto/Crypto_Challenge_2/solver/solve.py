#!/usr/bin/env python3
import socket
import re
import sys
import numpy as np
from fpylll import IntegerMatrix, LLL

HOST = "222.255.138.122"
PORT = 10173
N = 50
Q = 10007
M = 90

def centered(x):
    x = int(x) % Q
    if x > Q // 2:
        x -= Q
    return x

def decode_bits(bits):
    flag_bytes = []
    for i in range(0, len(bits), 8):
        byte = 0
        for j in range(8):
            byte |= (bits[i + j] << j)
        flag_bytes.append(byte)
    return bytes(flag_bytes).decode("utf-8", errors="ignore")

def solve(host=HOST, port=PORT):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    def recv_until(prompt=b"> "):
        data = b""
        while prompt not in data:
            chunk = s.recv(4096)
            if not chunk:
                break
            data += chunk
        return data.decode(errors="ignore")

    recv_until(b"> ")

    # Check samples left
    s.sendall(b"params\n")
    params_resp = recv_until(b"> ")
    m_left = int(re.search(r"samples_left=([0-9]+)", params_resp).group(1))
    print(f"[*] Samples left on server: {m_left}")

    num_samples = min(M, m_left)
    A_list = []
    b_list = []

    print(f"[*] Collecting {num_samples} LWE samples...")
    for _ in range(num_samples):
        s.sendall(b"sample\n")
        resp = recv_until(b"> ")
        m = re.search(r"A=([0-9,]+);\s*b=([0-9]+)", resp)
        if m:
            a_vals = [int(x) for x in m.group(1).split(",")]
            b_val = int(m.group(2))
            A_list.append(a_vals)
            b_list.append(b_val)

    A = np.array(A_list)
    b = np.array(b_list)

    print(f"[*] Constructing Kannan embedding lattice ({len(A_list) + N + 1}x{len(A_list) + N + 1})...")
    dim = len(A_list) + N + 1
    mat = IntegerMatrix(dim, dim)

    for i in range(len(A_list)):
        mat[i, i] = int(Q)

    for j in range(N):
        for i in range(len(A_list)):
            mat[len(A_list) + j, i] = int(A[i, j])
        mat[len(A_list) + j, len(A_list) + j] = 1

    for i in range(len(A_list)):
        mat[len(A_list) + N, i] = int(b[i])
    mat[len(A_list) + N, len(A_list) + N] = 1

    print("[*] Running LLL reduction...")
    LLL.reduction(mat)

    recovered_s = None
    for r in range(dim):
        row = [mat[r, c] for c in range(dim)]
        if abs(row[-1]) == 1:
            sign = 1 if row[-1] == -1 else -1
            cand_s = [sign * row[len(A_list) + j] for j in range(N)]
            cand_e = [-sign * row[i] for i in range(len(A_list))]
            if all(abs(x) <= 3 for x in cand_s) and all(abs(x) <= 1 for x in cand_e):
                diff = (np.dot(A, cand_s) + cand_e) % Q
                if np.array_equal(diff, b):
                    print(f"[+] Secret vector recovered successfully from row {r}!")
                    recovered_s = np.array(cand_s)
                    break

    if recovered_s is None:
        print("[-] Failed to identify secret vector.")
        return None

    # Request encrypted flag
    print("[*] Requesting encrypted flag ciphertext...")
    s.sendall(b"encrypt\n")
    enc_resp = recv_until(b"> ")

    ciphertexts = []
    for line in enc_resp.splitlines():
        m = re.search(r"A=([0-9,]+);\s*b=([0-9]+)", line)
        if m:
            a_vals = [int(x) for x in m.group(1).split(",")]
            b_val = int(m.group(2))
            ciphertexts.append((np.array(a_vals), b_val))

    print(f"[*] Decrypting {len(ciphertexts)} ciphertext bits...")
    decrypted_bits = []
    for a_vec, b_val in ciphertexts:
        val = centered(b_val - np.dot(a_vec, recovered_s))
        if abs(val) < Q // 4:
            decrypted_bits.append(0)
        else:
            decrypted_bits.append(1)

    flag = decode_bits(decrypted_bits)
    print(f"\n[+] Extracted Flag: {flag}")
    return flag

if __name__ == "__main__":
    if len(sys.argv) > 2:
        solve(sys.argv[1], int(sys.argv[2]))
    else:
        solve()
