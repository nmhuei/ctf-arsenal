from pathlib import Path
import mmap, struct, json

ROOT = Path(__file__).resolve().parents[2]
MEM = ROOT / "script/evidence/mem.clean"
TARGET = 0x34081000

with MEM.open("rb") as f, mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as m:
    segs=[]; off=0
    while off < len(m):
        magic,ver,start,end,res=struct.unpack_from("<IIQQQ",m,off)
        assert magic == 0x4c694d45
        segs.append((start,end+1,off+32))
        off += 32 + end-start+1

    def f2p(o):
        for s,e,fo in segs:
            if fo <= o < fo + (e-s):
                return s + o-fo
    def p2f(p):
        for s,e,fo in segs:
            if s <= p < e:
                return fo + p-s
    def read_phys(p,n=32):
        o=p2f(p)
        return m[o:o+n] if o is not None else b""

    prefix=struct.pack("<Q",TARGET)[2:6]
    pos=0; out=[]
    while True:
        hit=m.find(prefix,pos)
        if hit<0: break
        pos=hit+1
        cand=hit-2
        pp=f2p(cand)
        if pp is None or pp%8: continue
        val=struct.unpack_from("<Q",m,cand)[0]
        if (val & 0x000ffffffffff000) != TARGET or not (val&1): continue
        row={"pte_file":hex(cand),"pte_phys":hex(pp),"value":hex(val),"neighbors":[]}
        for j in range(-4,9):
            q=cand+8*j
            v=struct.unpack_from("<Q",m,q)[0]
            phys=v & 0x000ffffffffff000
            sample=read_phys(phys,32) if v&1 else b""
            row["neighbors"].append({"j":j,"pte":hex(v),"phys":hex(phys),"sample":sample.hex()})
        out.append(row)
    print(json.dumps(out,indent=2))
    (ROOT/"script/offline_audit/collector_ptes_exact.json").write_text(json.dumps(out,indent=2))
