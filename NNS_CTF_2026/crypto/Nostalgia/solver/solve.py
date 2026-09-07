#!/usr/bin/env python3
from Crypto.Cipher import AES
from hashlib import sha256
from datetime import datetime, timezone

ct = bytes.fromhex('85c43735b8442a69843bdc2ca0fb2d41eb548057c43b912704abdf2e27a8d8bc97017ec30b5d100498f12183c9e2ebed')

m = 2**32
a = 16843009
b = 826366247

cur_a = 1
cur_b = 0
for _ in range(1337):
    cur_a = (cur_a * a) % m
    cur_b = (cur_b * a + b) % m

def solve():
    dt = datetime(2026, 9, 3, 13, 23, 32, tzinfo=timezone.utc)
    center_ts = int(dt.timestamp())

    for delta in range(0, 1000000):
        for sign in (1, -1):
            ts = center_ts + sign * delta
            seed_final = (cur_a * ts + cur_b) % m
            key = sha256(str(seed_final).encode()).digest()
            cipher = AES.new(key, AES.MODE_ECB)
            pt_block = cipher.decrypt(ct[:16])
            if pt_block.startswith(b'NNS{') or pt_block.startswith(b'NSS{'):
                full_pt = cipher.decrypt(ct)
                pad_len = full_pt[-1]
                flag = full_pt[:-pad_len].decode()
                print('FLAG:', flag)
                return flag

if __name__ == '__main__':
    solve()
