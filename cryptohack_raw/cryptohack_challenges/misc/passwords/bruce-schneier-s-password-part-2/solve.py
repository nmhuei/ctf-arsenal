import re, json, socket, numpy as np
from Crypto.Util.number import isPrime

pw = '1335555779CCCEGGGGGMMOSSUUYYaaaceikkkkkkkmmooooqqqssuuwwwyy__'

print("Found Password:", pw)
arr = np.array(list(map(ord, pw)), dtype=np.int64)
print(f"NumPy Verification -> Sum: {arr.sum()} (isPrime={isPrime(int(arr.sum()))}), Prod: {arr.prod()}")

sock = socket.create_connection(('socket.cryptohack.org', 13401), timeout=10.0)
f = sock.makefile('rwb')
print("Banner:", f.readline().decode('utf-8', errors='ignore').strip())
f.write((json.dumps({'password': pw}) + '\n').encode('utf-8'))
f.flush()
resp = f.readline().decode('utf-8', errors='ignore').strip()
print("Response:", resp)
with open("flag.txt", "w") as fp:
    fp.write(resp + "\n")
