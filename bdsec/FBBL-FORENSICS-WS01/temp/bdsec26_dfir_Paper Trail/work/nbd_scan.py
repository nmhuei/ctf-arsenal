#!/usr/bin/env python3
import argparse, json, os, socket, struct, sys, time

NBDMAGIC = 0x4E42444D41474943
IHAVEOPT = 0x49484156454F5054
NBD_OPT_EXPORT_NAME = 1
NBD_REQUEST_MAGIC = 0x25609513
NBD_REPLY_MAGIC = 0x67446698
NBD_CMD_READ = 0

class NBDClient:
    def __init__(self, socket_path: str):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect(socket_path)
        self.handle = 1
        self.size = 0
        self._handshake()

    def _recv_exact(self, n: int) -> bytes:
        out = bytearray()
        while len(out) < n:
            chunk = self.sock.recv(n - len(out))
            if not chunk:
                raise EOFError(f"socket closed while reading {n} bytes")
            out.extend(chunk)
        return bytes(out)

    def _handshake(self) -> None:
        magic, opts_magic, global_flags = struct.unpack(">QQH", self._recv_exact(18))
        if magic != NBDMAGIC or opts_magic != IHAVEOPT:
            raise RuntimeError(f"unexpected NBD greeting: {magic:x} {opts_magic:x}")
        client_flags = 1  # NBD_FLAG_C_FIXED_NEWSTYLE
        if global_flags & 2:
            client_flags |= 2  # NBD_FLAG_C_NO_ZEROES
        self.sock.sendall(struct.pack(">I", client_flags))
        self.sock.sendall(struct.pack(">QII", IHAVEOPT, NBD_OPT_EXPORT_NAME, 0))
        self.size, self.transmission_flags = struct.unpack(">QH", self._recv_exact(10))
        if not (client_flags & 2):
            self._recv_exact(124)

    def read(self, offset: int, length: int) -> bytes:
        handle = self.handle
        self.handle += 1
        req = struct.pack(">IHHQQI", NBD_REQUEST_MAGIC, 0, NBD_CMD_READ, handle, offset, length)
        self.sock.sendall(req)
        magic, error, reply_handle = struct.unpack(">IIQ", self._recv_exact(16))
        if magic != NBD_REPLY_MAGIC or reply_handle != handle:
            raise RuntimeError("bad NBD reply")
        if error:
            raise OSError(error, f"NBD read failed at {offset}")
        return self._recv_exact(length)

    def close(self) -> None:
        self.sock.close()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--socket", required=True)
    ap.add_argument("--map")
    ap.add_argument("--test", action="store_true")
    ap.add_argument("--chunk", type=int, default=4 * 1024 * 1024)
    ap.add_argument("--output", default="nbd_scan_hits.jsonl")
    ap.add_argument("--pattern", action="append", default=[])
    args = ap.parse_args()

    c = NBDClient(args.socket)
    print(f"NBD size={c.size} flags=0x{c.transmission_flags:x}", flush=True)
    if args.test:
        data = c.read(0, 512)
        print(data[:64].hex())
        c.close()
        return 0

    pats = [p.encode() for p in args.pattern]
    if not pats:
        pats = [
            b"external bank account", b"bank account ID", b"transfer_receipt_may10.pdf",
            b"Rajesh Patel", b"Aman Reza", b"A. Reza", b"beneficiary",
            b"routing number", b"account number", b"payment instructions",
            b"wire instructions", b"SWIFT", b"IFSC", b"SK-PRIVATE-2024-0510",
            b"BDSEC{", b"attacker's real name"
        ]
    pats_lower = [(p, p.lower()) for p in pats]

    if args.map:
        extents = [e for e in json.load(open(args.map)) if e.get("data")]
    else:
        extents = [{"start": 0, "length": c.size}]

    total = sum(e["length"] for e in extents)
    scanned = 0
    started = time.time()
    max_pat = max(len(p) for p in pats)
    with open(args.output, "w", encoding="utf-8") as out:
        for ei, e in enumerate(extents, 1):
            start, length = e["start"], e["length"]
            pos = start
            end = start + length
            tail = b""
            while pos < end:
                n = min(args.chunk, end - pos)
                data = c.read(pos, n)
                combined = tail + data
                low = combined.lower()
                base = pos - len(tail)
                for original, needle in pats_lower:
                    search_at = 0
                    while True:
                        idx = low.find(needle, search_at)
                        if idx < 0:
                            break
                        absolute = base + idx
                        context_start = max(0, idx - 512)
                        context_end = min(len(combined), idx + len(needle) + 1024)
                        context = combined[context_start:context_end]
                        rec = {
                            "offset": absolute,
                            "pattern": original.decode(errors="replace"),
                            "context_latin1": context.decode("latin1", errors="replace"),
                            "context_hex": context.hex(),
                        }
                        out.write(json.dumps(rec, ensure_ascii=False) + "\n")
                        out.flush()
                        print(f"HIT offset={absolute} pattern={original!r}", flush=True)
                        search_at = idx + 1
                tail = combined[-(max_pat + 1024):]
                pos += n
                scanned += n
                if scanned % (512 * 1024 * 1024) < args.chunk:
                    elapsed = max(time.time() - started, 0.001)
                    print(f"progress {scanned}/{total} ({scanned/total:.1%}) {scanned/elapsed/1024/1024:.1f} MiB/s", flush=True)
    c.close()
    print(f"done scanned={scanned} hits_file={args.output}", flush=True)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
