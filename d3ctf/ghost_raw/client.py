import requests
import json
import base64
import time
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

BASE_URL = "https://rsnfg2lzhxprnrolji5kuaicz3e.cloud.d3c.tf"

def b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode('utf-8').rstrip('=')

def b64url_decode(s: str) -> bytes:
    padded = s + '=' * ((4 - len(s) % 4) % 4)
    return base64.urlsafe_b64decode(padded)

def canonical_json(val):
    if val is None or isinstance(val, (int, float, str, bool)):
        return json.dumps(val, separators=(',', ':'))
    if isinstance(val, list):
        return '[' + ','.join(canonical_json(x) for x in val) + ']'
    if isinstance(val, dict):
        keys = sorted([k for k, v in val.items() if v is not None])
        items = [json.dumps(k) + ':' + canonical_json(val[k]) for k in keys]
        return '{' + ','.join(items) + '}'
    raise ValueError(f"Unsupported type: {type(val)}")

def int_to_b64url(val: int, length: int) -> str:
    b = val.to_bytes(length, 'big')
    return b64url_encode(b)

def b64url_to_int(s: str) -> int:
    b = b64url_decode(s)
    return int.from_bytes(b, 'big')

class GhostClient:
    def __init__(self):
        self.session = requests.Session()
        self.seq = 0

    def bootstrap(self):
        # 1. Guest session
        resp = self.session.post(f"{BASE_URL}/api/session/guest", headers={"Accept": "application/json"})
        resp.raise_for_status()
        self.token = resp.json()["token"]

        # 2. ECDH P-256 keypair
        self.priv_key = ec.generate_private_key(ec.SECP256R1())
        pub_key = self.priv_key.public_key()
        numbers = pub_key.public_numbers()
        
        jwk = {
            "kty": "EC",
            "crv": "P-256",
            "x": int_to_b64url(numbers.x, 32),
            "y": int_to_b64url(numbers.y, 32),
            "ext": True
        }

        # 3. Transport bootstrap
        resp = self.session.post(
            f"{BASE_URL}/api/transport/bootstrap",
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            },
            json={"clientPublicKey": jwk}
        )
        resp.raise_for_status()
        res_data = resp.json()
        self.sid = res_data["sid"]

        # Server public key
        server_jwk = res_data["serverPublicKey"]
        server_x = b64url_to_int(server_jwk["x"])
        server_y = b64url_to_int(server_jwk["y"])
        server_pub_numbers = ec.EllipticCurvePublicNumbers(server_x, server_y, ec.SECP256R1())
        server_pub_key = server_pub_numbers.public_key()

        # Shared secret
        shared_secret = self.priv_key.exchange(ec.ECDH(), server_pub_key)

        salt = b64url_decode(res_data["salt"])

        # HKDF c2s and s2c
        hkdf_c2s = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            info=b"ghost-packet:c2s",
        )
        c2s_bytes = hkdf_c2s.derive(shared_secret)

        hkdf_s2c = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            info=b"ghost-packet:s2c",
        )
        s2c_bytes = hkdf_s2c.derive(shared_secret)

        self.c2s_aes = AESGCM(c2s_bytes)
        self.s2c_aes = AESGCM(s2c_bytes)

    def request(self, target: str, body):
        self.seq += 1
        ts = int(time.time() * 1000)

        aad_obj = {
            "direction": "c2s",
            "seq": self.seq,
            "sid": self.sid,
            "ts": ts,
            "v": 1
        }
        aad_bytes = canonical_json(aad_obj).encode('utf-8')

        payload_obj = {
            "target": target,
            "body": body
        }
        payload_bytes = canonical_json(payload_obj).encode('utf-8')

        iv = os.urandom(12)
        ct = self.c2s_aes.encrypt(iv, payload_bytes, aad_bytes)

        req_body = {
            "v": 1,
            "sid": self.sid,
            "seq": self.seq,
            "ts": ts,
            "iv": b64url_encode(iv),
            "ct": b64url_encode(ct)
        }

        resp = self.session.post(
            f"{BASE_URL}/api/gateway",
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            },
            json=req_body
        )
        
        res_json = resp.json()
        if not resp.ok or "ct" not in res_json:
            return res_json

        res_iv = b64url_decode(res_json["iv"])
        res_ct = b64url_decode(res_json["ct"])

        res_aad_obj = {
            "direction": "s2c",
            "seq": res_json["seq"],
            "sid": res_json["sid"],
            "ts": res_json["ts"],
            "v": res_json["v"]
        }
        res_aad_bytes = canonical_json(res_aad_obj).encode('utf-8')

        pt_bytes = self.s2c_aes.decrypt(res_iv, res_ct, res_aad_bytes)
        return json.loads(pt_bytes.decode('utf-8'))

if __name__ == "__main__":
    client = GhostClient()
    client.bootstrap()
    res = client.request("search", {"q": ""})
    print(json.dumps(res, indent=2))
