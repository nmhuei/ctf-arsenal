from pathlib import Path
import mmap, json, hashlib

ROOT=Path(__file__).resolve().parents[2]
MEM=ROOT/"script/evidence/mem.clean"
pat=bytes.fromhex("31ed4989d15e4889e24883e4f050544531c031c9")
out=[]
with MEM.open("rb") as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as m:
    pos=0
    while True:
        hit=m.find(pat,pos)
        if hit<0: break
        pos=hit+1
        for delta,kind in ((0x350,"plain"),(0x354,"endbr")):
            base=hit-delta
            if base<0 or base+0x12f5>len(m): continue
            # Standard ELF init/PLT layout expected from the recovered first page.
            b=m[base:base+0x200]
            if b[:4] != b"\x48\x83\xec\x08": continue
            if b[0x20:0x22] != b"\xff\x35": continue
            if b[0x26:0x28] != b"\xff\x25": continue
            ok=0
            for o in range(0x30,0x1e0,0x10):
                if b[o:o+2]==b"\xff\x25" and b[o+6]==0x68:
                    ok+=1
            if ok < 20: continue
            code=m[base:base+0x12f5]
            row={"hit":hex(hit),"base":hex(base),"kind":kind,"plt_slots":ok,
                 "sha256":hashlib.sha256(code).hexdigest(),
                 "entry":m[base+0x350:base+0x390].hex()}
            out.append(row)
            (ROOT/f"script/offline_audit/true_text_{base:x}.bin").write_bytes(code)
            print(row,flush=True)
print("matches",len(out),flush=True)
(ROOT/"script/offline_audit/true_text_candidates.json").write_text(json.dumps(out,indent=2))
