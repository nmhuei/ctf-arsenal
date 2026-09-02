from client import GhostClient

c = GhostClient()
c.bootstrap()

# Let's test letters, symbols, words
words = [
    "pragma", "attach", "detach", "vacuum", "reindex",
    "insert", "update", "delete", "create", "drop", "alter",
    "table", "view", "index", "trigger", "procedure",
    "exec", "eval", "system", "process", "child_process",
    "require", "import", "fs", "path", "net", "http",
    "shadow", "passwd", "flag", "secret", "token", "key",
    "user", "admin", "root", "guest", "sqlite_", "pg_",
    "information_schema", "sys", "mysql", "master",
    "dump", "backup", "log", "logs", "test", "pcap",
    "file", "read", "write", "open", "close", "dir",
    "script", "code", "func", "function", "var", "const", "let",
    "class", "object", "prototype", "__proto__", "constructor",
    "global", "window", "document", "process", "env"
]

for w in words:
    res = c.request("search", {"q": w})
    if not res.get("ok") and res.get("error") == "this is not for u":
        print(f"BLOCKED: {w}")
