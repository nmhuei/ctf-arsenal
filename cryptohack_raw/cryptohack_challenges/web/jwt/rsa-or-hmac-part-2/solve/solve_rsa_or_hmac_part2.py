#!/usr/bin/env python3
import base64, ctypes, ctypes.util, hashlib, hmac, json, ssl, urllib.request
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

BASE = "https://web.cryptohack.org/rsa-or-hmac-2/"

def b64url_decode(s):
    if isinstance(s, str):
        s = s.encode()
    return base64.urlsafe_b64decode(s + b'=' * ((4 - len(s) % 4) % 4))

def b64url_encode(b):
    return base64.urlsafe_b64encode(b).rstrip(b'=')

def http_get_json(url):
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(url, context=ctx, timeout=20) as resp:
        return json.loads(resp.read().decode())

def emsa_pkcs1_v1_5_sha256(msg, k=256):
    T = bytes.fromhex('3031300d060960864801650304020105000420') + hashlib.sha256(msg).digest()
    return b'\x00\x01' + b'\xff' * (k - len(T) - 3) + b'\x00' + T

# GMP bindings
libgmp = ctypes.CDLL(ctypes.util.find_library('gmp'))
class mpz_t(ctypes.Structure):
    _fields_ = [('_mp_alloc', ctypes.c_int), ('_mp_size', ctypes.c_int), ('_mp_d', ctypes.POINTER(ctypes.c_ulong))]
for fn, args in {
    '__gmpz_init': [ctypes.POINTER(mpz_t)],
    '__gmpz_import': [ctypes.POINTER(mpz_t), ctypes.c_size_t, ctypes.c_int, ctypes.c_size_t, ctypes.c_int, ctypes.c_size_t, ctypes.c_void_p],
    '__gmpz_pow_ui': [ctypes.POINTER(mpz_t), ctypes.POINTER(mpz_t), ctypes.c_ulong],
    '__gmpz_sub': [ctypes.POINTER(mpz_t), ctypes.POINTER(mpz_t), ctypes.POINTER(mpz_t)],
    '__gmpz_gcd': [ctypes.POINTER(mpz_t), ctypes.POINTER(mpz_t), ctypes.POINTER(mpz_t)],
    '__gmpz_get_str': [ctypes.c_char_p, ctypes.c_int, ctypes.POINTER(mpz_t)],
}.items():
    getattr(libgmp, fn).argtypes = args
libgmp.__gmpz_get_str.restype = ctypes.c_char_p

def mpz_from_bytes(b):
    z = mpz_t()
    libgmp.__gmpz_init(ctypes.byref(z))
    buf = ctypes.create_string_buffer(b)
    libgmp.__gmpz_import(ctypes.byref(z), len(b), 1, 1, 1, 0, buf)
    z._buf = buf
    return z

def mpz_hex(z):
    s = libgmp.__gmpz_get_str(None, 16, ctypes.byref(z))
    return ctypes.cast(s, ctypes.c_char_p).value.decode()

def recover_modulus(tokens, e=65537):
    vals = []
    for tok in tokens:
        h, p, s = tok.split('.')
        sig = mpz_from_bytes(b64url_decode(s))
        em = mpz_from_bytes(emsa_pkcs1_v1_5_sha256((h + '.' + p).encode()))
        out = mpz_t()
        libgmp.__gmpz_init(ctypes.byref(out))
        libgmp.__gmpz_pow_ui(ctypes.byref(out), ctypes.byref(sig), e)
        libgmp.__gmpz_sub(ctypes.byref(out), ctypes.byref(out), ctypes.byref(em))
        vals.append(out)
    g = vals[0]
    for v in vals[1:]:
        ng = mpz_t()
        libgmp.__gmpz_init(ctypes.byref(ng))
        libgmp.__gmpz_gcd(ctypes.byref(ng), ctypes.byref(g), ctypes.byref(v))
        g = ng
    return int(mpz_hex(g), 16)

def json_compact(obj):
    return json.dumps(obj, separators=(',', ':')).encode()

def forge_hs256(secret, payload):
    header = {'alg': 'HS256', 'typ': 'JWT'}
    h = b64url_encode(json_compact(header))
    p = b64url_encode(json_compact(payload))
    msg = h + b'.' + p
    sig = hmac.new(secret, msg, hashlib.sha256).digest()
    return (msg + b'.' + b64url_encode(sig)).decode()

def main():
    sessions = []
    for name in ["alice", "bob", "charlie"]:
        tok = http_get_json(BASE + f"create_session/{name}/")["session"]
        sessions.append(tok)
        print(f"[+] got RS256 session for {name}")
    n = recover_modulus(sessions, 65537)
    print("[+] recovered modulus bits:", n.bit_length())
    pub_pem = rsa.RSAPublicNumbers(65537, n).public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.PKCS1
    )
    print("[+] reconstructed public key header:", pub_pem.splitlines()[0].decode())
    forged = forge_hs256(pub_pem, {"username": "admin", "admin": True})
    print("[+] forged HS256 token")
    out = http_get_json(BASE + "authorise/" + forged + "/")
    print(json.dumps(out))
    if "response" in out:
        print("FLAG_RESPONSE:", out["response"])

if __name__ == "__main__":
    main()
