from client import GhostClient
import json

c = GhostClient()
c.bootstrap()

keywords = [
    "pragma", "PRAGMA", "PrAgMa",
    "attach", "ATTACH",
    "detach",
    "load_extension",
    "readfile", "writefile",
    "database", "module", "function",
    "sqlite_master", "sqlite_schema", "sqlite_temp_master",
    "sqlite_temp_schema",
    "sqlite_version",
    "hex", "quote", "unhex", "base64",
    "char", "unicode", "length", "substr",
    "union", "select", "from", "where", "group", "order", "limit",
    "insert", "update", "delete", "drop", "create", "alter",
    "with", "recursive",
    "flag", "FLAG", "d3ctf", "D3CTF"
]

for kw in keywords:
    res = c.request("search", {"q": kw})
    status = "ALLOWED"
    if res.get("error") == "this is not for u":
        status = "BLOCKED"
    elif not res.get("ok"):
        status = f"ERROR: {res.get('error')}"
    print(f"{kw:20s}: {status}")
