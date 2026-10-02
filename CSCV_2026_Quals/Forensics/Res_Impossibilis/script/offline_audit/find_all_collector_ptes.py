from pathlib import Path
import mmap,struct,json

ROOT=Path(__file__).resolve().parents[2]
MEM=ROOT/"script/evidence/mem.clean"
cands=json.loads((ROOT/"script/offline_audit/elf_candidates.json").read_text())["candidates"]
foffs=sorted({int(x["offset"],16) for x in cands if x["size"]==23360})

with MEM.open("rb") as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as m:
    segs=[];o=0
    while o<len(m):
        magic,ver,s,e,res=struct.unpack_from("<IIQQQ",m,o); assert magic==0x4c694d45
        segs.append((s,e+1,o+32));o+=32+e-s+1
    def f2p(x):
        for s,e,fo in segs:
            if fo<=x<fo+e-s:return s+x-fo
    def p2f(x):
        for s,e,fo in segs:
            if s<=x<e:return fo+x-s
    def sample_phys(p,n=24):
        x=p2f(p)
        return m[x:x+n].hex() if x is not None else ""

    out=[]
    for fo in foffs:
        phys=f2p(fo)
        if phys is None: continue
        pref=struct.pack("<Q",phys)[2:6];pos=0;hits=[]
        while True:
            hit=m.find(pref,pos)
            if hit<0:break
            pos=hit+1;c=hit-2;cp=f2p(c)
            if cp is None or cp%8:continue
            v=struct.unpack_from("<Q",m,c)[0]
            if (v&0x000ffffffffff000)!=(phys&~0xfff) or not(v&1):continue
            near=[]
            for j in range(-3,8):
                vv=struct.unpack_from("<Q",m,c+8*j)[0];p=vv&0x000ffffffffff000
                near.append([j,hex(vv),hex(p),sample_phys(p)])
            hits.append({"pte_file":hex(c),"pte_phys":hex(cp),"value":hex(v),"near":near})
        out.append({"elf_file":hex(fo),"elf_phys":hex(phys),"hits":hits})
        print(hex(fo),hex(phys),"hits",len(hits),flush=True)
    (ROOT/"script/offline_audit/all_collector_ptes.json").write_text(json.dumps(out,indent=2))
