from client import GhostClient

c = GhostClient()
c.bootstrap()

test_strings = [
    "pragma",
    "PRAGMA",
    "pragma_table_info",
    "pragma_database_list",
    "pragma\x00_database_list",
    "pragma\n_database_list",
    "pragma\r_database_list",
    "pragma\t_database_list",
    "pragma%5fdatabase_list",
    "pragma_compile_options",
    "pragma_module_list",
    "pragma_function_list",
]

for s in test_strings:
    res = c.request("search", {"q": s})
    err = res.get("error", "OK")
    print(f"{repr(s):30s} -> {err}")
