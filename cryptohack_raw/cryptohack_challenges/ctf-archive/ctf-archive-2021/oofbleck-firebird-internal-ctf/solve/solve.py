import base64, string
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

b64 = "0UpFwNytjLbrytWyClHmBvJ3+umnEc1fcycgNeCtX9ZfcmqlCfkndC56aAwKGSjT55DKXCzQkh+TmAhshA08tSZPDLyuf3wdka0t1hRkdHLCPxIBjdGxx5tjF487G5a6"

ct = base64.b64decode(b64)
aes_key = ct[:16]
blocks = [ct[i:i+16] for i in range(16, len(ct), 16)]

word = (string.ascii_letters + string.digits + "_").encode()
wordset = set(word)

def aes_dec(block):
    dec = Cipher(algorithms.AES(aes_key), modes.ECB()).decryptor()
    return dec.update(block) + dec.finalize()

def xor(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

for a in word:
    for b in word:
        for c in word:
            p5 = bytes([a, b, c]) + b"}" + bytes([12]) * 12

            s5 = xor(blocks[4], p5)
            s4 = aes_dec(s5)
            s3 = aes_dec(s4)
            s2 = aes_dec(s3)
            s1 = aes_dec(s2)

            p1 = xor(blocks[0], s1)
            if not p1.startswith(b"firebird{"):
                continue
            if not all(ch in wordset for ch in p1[9:]):
                continue

            p2 = xor(blocks[1], s2)
            p3 = xor(blocks[2], s3)
            p4 = xor(blocks[3], s4)

            if all(ch in wordset for ch in p2 + p3 + p4):
                print((p1 + p2 + p3 + p4 + p5[:4]).decode())
