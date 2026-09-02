from client import GhostClient
import json

c = GhostClient()
c.bootstrap()

targets = [
    "search", "admin", "login", "flag", "status", "debug", "config",
    "system", "eval", "exec", "sql", "query", "user", "guest", "info",
    "help", "ping", "read", "file", "fetch", "graphql", "swagger",
    "openapi", "docs", "route", "routes", "api", "test", "raw",
    "db", "database", "dump", "index", "get", "list", "show",
    "health", "healthz", "recent", "archive", "auth", "session",
    "logs", "log", "pcap", "download"
]

for t in targets:
    try:
        res = c.request(t, {})
        err = res.get("error") if not res.get("ok") else "OK"
        print(f"Target: {t:20s} -> {res}")
    except Exception as e:
        print(f"Target: {t:20s} -> EXC: {e}")
