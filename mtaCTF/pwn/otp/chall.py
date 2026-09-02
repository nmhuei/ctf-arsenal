import os
import random
import sys
from Crypto.Util.number import bytes_to_long, getPrime
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from hashlib import sha256

flag = os.getenv('FLAG', 'flag{fake_flag}').encode()
sys.set_int_max_str_digits(0)

class WeirdOTP:
    def __init__(self):
        self.n = getPrime(256)
        self.state = random.randint(1, self.n)
        self.a = [bytes_to_long(os.urandom(32)) for _ in range(20)]
        self.c = bytes_to_long(os.urandom(32))
        random.seed(1337)
        
    def next(self):
        self.state = sum(((random.getrandbits(256) + i) * self.a[i]) for i in range(20)) % self.n
        self.state += pow(self.c, 1337, self.n)
        self.state %= self.n
        
        return self.state

    def get_keystream(self, length):
        keystream = b''
        while len(keystream) < length:
            keystream += self.next().to_bytes(32, 'big')
        return keystream[:length]
    
    def encrypt_message(self, plaintext):
        keystream = self.get_keystream(len(plaintext))
        ciphertext = bytes(a ^ b for a, b in zip(plaintext, keystream))
        return ciphertext.hex()
    
    def reseed(self, new_seed):
        random.seed(new_seed)
        
    def reset(self):
        self.a = [bytes_to_long(os.urandom(32)) for _ in range(20)]

    
def main():
    secret = os.urandom(32)
    otp = WeirdOTP()
    
    cipher = AES.new(sha256(secret).digest(), AES.MODE_ECB)
    flag_ct = cipher.encrypt(pad(flag, 16))
    print("Encrypted flag:", flag_ct.hex())
    
    msgs = [
        b"!@#$%^tung tung tung sahur!@#$%^",
        b"!@#$%^&tralalero tralala!@#$%^&*",
        b"!@#$%^bombardino crocodilo!@#$%^",
        b"!@#$%^&*(lirili larila!@#$%^&*()",
        b"!@#$%^&brr brr patapim!@#$%^&*!!",
        b"!@#$%^chimpanzini bananini!@#$%^",
        b"!@#$%^capuccino assassino!@#$%^&",
        b"!@#$%^ballerina cappuccina!@#$%@",
        b"!@#$%^&*()frigo camelo!@#$%^&*()",
        b"!@#$%^orangutini ananasini!@#$%^",
        b"!@#$%^&bombombini gusini!@#$%^&@",
        b"!@#$%^&*bobrito bandito!@#$%^&*@",
    ]
    
    for i in range(23):
        plaintext = random.choice(msgs)
        print("Ciphertext:", otp.encrypt_message(plaintext))
    otp.reset()
    
    new_seed = int(input("Enter new seed: "))
    otp.reseed(new_seed)
    
    plaintext = bytes.fromhex(input("Enter your plaintext(hex): "))
    assert len(plaintext) <= 32, "Too long"
    print("Ciphertext:", otp.encrypt_message(plaintext))
    otp.reset()
    
    print("Encrypted secret:", otp.encrypt_message(secret))
    print("Good luck!")
        
main()