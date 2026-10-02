from pathlib import Path
import mmap, hashlib

root = Path(__file__).resolve().parents[2]
mem = root / "script/evidence/mem.clean"
outdir = root / "script/offline_audit"

# Last PLT entry for relocation #26:
# VA 0x4011d0 -> GOT 0x4050e8, then push 0x1a, then jump back to PLT0 0x401020.
sig = bytes.fromhex("ff25123f0000681a000000e940feffff")

hits = []
with mem.open("rb") as f, mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as m:
    pos = 0
    while True:
        pos = m.find(sig, pos)
        if pos < 0:
            break
        page0 = pos - 0x1d0
        blob = bytes(m[page0:page0+0x1000]) if page0 >= 0 else b""
        # Validate all 27 standard x86-64 PLT slots at VA 0x401030..0x4011d0.
        ok = len(blob) == 0x1000
        good = 0
        if ok:
            for i in range(27):
                off = 0x30 + 0x10*i
                va = 0x401030 + 0x10*i
                got = 0x405018 + 8*i
                disp = (got - (va + 6)) & 0xffffffff
                back = (0x401020 - (va + 16)) & 0xffffffff
                expect = b"\xff\x25" + disp.to_bytes(4,"little") + b"\x68" + i.to_bytes(4,"little") + b"\xe9" + back.to_bytes(4,"little")
                if blob[off:off+16] == expect:
                    good += 1
                else:
                    ok = False
                    break
        hits.append((pos, page0, good, ok, hashlib.sha256(blob).hexdigest() if blob else ""))
        pos += 1

print("signature_hits", len(hits))
for h in hits:
    print("hit=0x%x page0=0x%x plt_good=%d full_plt=%s sha256=%s" % h)
    if h[3]:
        p = outdir / ("collector_rx_page0_%x.bin" % h[1])
        p.write_bytes(bytes(m[0:0])) if False else None

# Re-open only for validated carves, avoiding retaining the huge mmap.
with mem.open("rb") as f, mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as m:
    for _, page0, _, ok, _ in hits:
        if ok:
            (outdir / ("collector_rx_page0_%x.bin" % page0)).write_bytes(m[page0:page0+0x1000])
