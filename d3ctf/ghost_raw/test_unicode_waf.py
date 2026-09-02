from client import GhostClient

c = GhostClient()
c.bootstrap()

# Test unicode escape in JSON vs unicode chars in SQLite
unicode_tests = [
    # Fullwidth letters
    "ｐｒａｇｍａ_database_list",
    "pragma＿database_list",
    "pragma\u200b_database_list",
    "pragma\u200c_database_list",
    "pragma\u200d_database_list",
    "pragma\ufeff_database_list",
    "pragma\u00a0_database_list",
    # Alternative table function syntax
    "sqlite_master",
    "sqlite_schema",
]

for s in unicode_tests:
    q = f"' UNION SELECT 1, 2, 3 FROM {s}--"
    res = c.request("search", {"q": q})
    err = res.get("error", "OK")
    print(f"{repr(s):35s} -> {err}")
