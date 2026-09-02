import base64, json, hashlib
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def b64d(s):
    s = s.strip()
    return base64.b64decode(s + '=' * (-len(s) % 4))

with open('/home/light/Downloads/claude-scratch/ctf_extract/pablo/config.enc') as f:
    cfg = json.load(f)

salt = b64d(cfg['salt'])
nonce = b64d(cfg['nonce'])
ct = b64d(cfg['ciphertext'])
print(f"salt len={len(salt)} nonce len={len(nonce)} ct len={len(ct)}")

candidates = [
    "luongvd", "luongvd:luongvd", "luongvdluongvd", "luongvd:luongvd",
    "TK:luongvd", "MK:luongvd", "luongvd\nluongvd", "username:luongvd password:luongvd",
    "luongvd_", "_luongvd", "LUONGVD", "luongvd ", " luongvd",
]

def derive(password, salt, iters=210000, keylen=32):
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=keylen, salt=salt, iterations=iters)
    return kdf.derive(password.encode())

for pwd in candidates:
    try:
        key = derive(pwd, salt)
        aes = AESGCM(key)
        plain = aes.decrypt(nonce, ct, None)
        print(f"[+] SUCCESS with password {pwd!r}: {len(plain)} bytes")
        print(plain[:100])
        open('/home/light/Downloads/claude-scratch/ctf_extract/pablo/decrypted.bin','wb').write(plain)
        break
    except Exception as e:
        print(f"[-] {pwd!r}: {type(e).__name__}")
