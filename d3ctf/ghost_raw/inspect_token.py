from client import GhostClient
import json
import base64

c = GhostClient()
c.bootstrap()
print("Token:", c.token)

try:
    parts = c.token.split('.')
    print("Parts:", len(parts))
    for p in parts:
        padded = p + '=' * ((4 - len(p) % 4) % 4)
        try:
            print("  Decoded:", base64.urlsafe_b64decode(padded))
        except Exception:
            pass
except Exception as e:
    print(e)
