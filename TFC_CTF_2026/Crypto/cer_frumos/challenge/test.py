import random
from secret import flag
from hashlib import sha256
from Crypto.Cipher import AES

random.seed(random.randint(0,2**128))
for i in range(625):
    x = random.getrandbits(48)
    random.getrandbits(16)
    #random.getrandbits(16)
    print(x)
for i in range(10):
    x = random.getrandbits(32)
    #print(f'DEBUG: {x}')
key = sha256(str(random.getrandbits(64)).encode()).digest()
nonce = sha256(str(random.getrandbits(64)).encode()).digest()[:16]
cipher =  AES.new(key, AES.MODE_CBC, iv=nonce)

enc_flag = cipher.encrypt(flag)

print(f'Enc flag: {enc_flag.hex()}')