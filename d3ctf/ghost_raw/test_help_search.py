"""
The guest-session-help pcap shows a 'help' endpoint.
Let's try 'help' target via encrypted gateway, and also
try various body parameters.
"""
from client import GhostClient
import json

c = GhostClient()
c.bootstrap()

# Try help target with various bodies
print("=== Testing 'help' target ===")
bodies = [
    {},
    {"q": ""},
    {"q": "help"},
    {"q": "flag"},
    {"q": "admin"},
    {"topic": "admin"},
    {"topic": "flag"},
    {"topic": "search"},
    {"command": "help"},
    {"action": "list"},
]

for b in bodies:
    res = c.request("help", b)
    print(f"  help({json.dumps(b):30s}) -> {json.dumps(res)[:200]}")

# Also try the search with different body params
print("\n=== Testing 'search' with different params ===")
search_bodies = [
    {"q": "", "admin": True},
    {"q": "", "role": "admin"},
    {"q": "", "debug": True},
    {"q": "", "verbose": True},
    {"q": "", "limit": 100},
    {"q": "", "offset": 0, "limit": 1000},
    {"q": "", "table": "User"},
    {"q": "", "raw": True},
    {"query": "test"},
    {"search": "test"},
    {"term": "test"},
    {"keyword": "test"},
]

for b in search_bodies:
    res = c.request("search", b)
    err = res.get("error", "")
    ok = res.get("ok", False)
    if ok and res.get("data", {}).get("rows", []):
        print(f"  search({json.dumps(b):40s}) -> HAS DATA: {json.dumps(res)[:200]}")
    elif ok:
        print(f"  search({json.dumps(b):40s}) -> OK (empty)")
    elif "operation unavailable" not in err:
        print(f"  search({json.dumps(b):40s}) -> {err[:100]}")
