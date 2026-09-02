"""
Explore ALL possible gateway targets systematically.
We know 'search' and 'help' work. Let's enumerate more.
"""
from client import GhostClient

c = GhostClient()
c.bootstrap()

# Extensive target list
targets = [
    # Known working
    "search", "help",
    # Common CRUD operations
    "list", "get", "create", "update", "delete", "read", "write",
    # Archive/data related
    "archive", "query", "lookup", "fetch", "find", "browse", "scan",
    "download", "upload", "import", "export",
    # Admin/system
    "admin", "config", "settings", "system", "status", "info",
    "health", "ping", "echo", "debug", "test", "version",
    # Auth related
    "login", "logout", "auth", "session", "token", "register",
    "user", "users", "profile", "account", "whoami", "me",
    # Flag/secret
    "flag", "secret", "key", "keys", "vault", "store",
    # Logs/audit
    "log", "logs", "audit", "history", "events", "trace",
    # File/data ops
    "file", "files", "data", "blob", "object", "document",
    "pcap", "capture", "traffic", "packet", "packets",
    # Bootstrap/setup
    "bootstrap", "init", "setup", "install", "reset",
    # Misc
    "execute", "run", "eval", "shell", "command", "cmd",
    "encrypt", "decrypt", "sign", "verify", "hash",
    "notify", "alert", "message", "send", "receive",
    "stat", "stats", "metrics", "monitor", "dashboard",
    "report", "summary", "overview", "index",
    # Ghost-specific
    "ghost", "zero", "phantom", "spectre", "shadow",
    "archive-query", "archive_query", "archiveQuery",
    "knowledge", "knowledgeBase", "knowledge_base",
    "frontdesk", "front-desk", "front_desk",
    "gateway", "dispatch", "route", "handler",
    "ticket", "exchange", "redeem", "claim",
]

results = {}
for t in targets:
    res = c.request(t, {"q": "test"})
    err = res.get("error", "")
    ok = res.get("ok", False)
    
    if ok:
        results[t] = f"OK: {str(res)[:100]}"
    elif "operation unavailable" in str(err):
        pass  # Default for unknown targets
    else:
        results[t] = f"DIFFERENT: {err}"

print("=== Targets with non-standard responses ===")
for t, r in sorted(results.items()):
    print(f"  {t:25s} -> {r}")
