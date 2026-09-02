import requests
import json
import base64

base = "https://rsnfg2lzhxprnrolji5kuaicz3e.cloud.d3c.tf"

for i in range(3):
    r = requests.post(f"{base}/api/session/guest", headers={"Accept": "application/json"})
    t = r.json()["token"]
    p = t.split('.')
    print(f"Token {i}: jti={json.loads(base64.urlsafe_b64decode(p[1]+'=='))['jti']}")
    print(f"  Sig (hex): {base64.urlsafe_b64decode(p[2]+'==').hex()[:40]}...")
