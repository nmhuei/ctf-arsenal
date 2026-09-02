from client import GhostClient

c = GhostClient()
c.bootstrap()

tests = [
    "json_tree('{\"a\":1}')",
    "json_each('{\"a\":1}')",
    "generate_series(1, 3)",
]

for t in tests:
    q = f"' UNION SELECT 1, 2, 3 FROM {t}--"
    res = c.request("search", {"q": q})
    err = res.get("error") if not res.get("ok") else "OK"
    print(f"{t:30s} -> {err}")
