from pathlib import Path
import mmap,struct,sys,json
ROOT=Path(__file__).resolve().parents[2]
MEM=ROOT/"script/evidence/mem.clean"
TARGET=int(sys.argv[1],0)&~0xfff
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
    def sample(p,n=32):
        z=p2f(p);return m[z:z+n].hex() if z is not None else ""
    pref=struct.pack("<Q",TARGET)[2:6];pos=0;out=[]
    while True:
        hit=m.find(pref,pos)
        if hit<0:break
        pos=hit+1;c=hit-2;cp=f2p(c)
        if cp is None or cp%8:continue
        v=struct.unpack_from("<Q",m,c)[0]
        if (v&0x000ffffffffff000)!=TARGET or not(v&1):continue
        near=[]
        for j in range(-8,17):
            vv=struct.unpack_from("<Q",m,c+8*j)[0];p=vv&0x000ffffffffff000
            near.append({"j":j,"pte":hex(vv),"phys":hex(p),"sample":sample(p)})
        out.append({"pte_file":hex(c),"pte_phys":hex(cp),"value":hex(v),"near":near})
    print(json.dumps(out,indent=2))
