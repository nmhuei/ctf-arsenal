import struct, numpy as np, heapq, itertools, sys

def load(path):
    with open(path,'rb') as f:
        assert f.read(4)==b'LGTS'
        nsteps,nvocab,temp,top_p,min_p,top_k=struct.unpack('<IIfffI', f.read(24))
        steps=[]
        for _ in range(nsteps):
            target=struct.unpack('<i', f.read(4))[0]
            logits=np.frombuffer(f.read(4*nvocab), dtype=np.float32).copy().astype(np.float64)/temp
            order=np.argsort(-logits)
            z=logits[order]-logits[order[0]]; p=np.exp(z); p/=p.sum()
            rank=int(np.where(order==target)[0][0])
            steps.append((rank,p))
    return steps

def code_for_rank(probs, target):
    heap=[]; counter=itertools.count(); parent={}
    for i,fr in enumerate(probs): heapq.heappush(heap,(float(fr), next(counter), i))
    while len(heap)>1:
        f1,c1,n1=heapq.heappop(heap); f2,c2,n2=heapq.heappop(heap)
        m=('n',next(counter)); parent[n1]=(m,'0'); parent[n2]=(m,'1')
        heapq.heappush(heap,(f1+f2,next(counter),m))
    n=target; bits=[]
    while n in parent:
        n,b=parent[n]; bits.append(b)
    return ''.join(reversed(bits))

def variants(bits):
 for srcname,src in [('bits',bits),('revall',bits[::-1])]:
  for off in range(8):
   if len(src)-off>=8:
    for kind,ss in [('normal',src),('byterev',src)]:
     if kind=='normal': bs=bytes(int(ss[i:i+8],2) for i in range(off,len(ss)-7,8))
     else: bs=bytes(int(ss[i:i+8][::-1],2) for i in range(off,len(ss)-7,8))
     yield srcname,off,kind,bs

def score(b): return sum(32<=x<127 or x in (9,10,13) for x in b)/max(1,len(b))
for cname,fn in {'header1':'header_full_temp1.bin','bos1':'bos_full_temp1.bin','chat1':'chat_empty_full_temp1.bin','header08':'header_full_temp08.bin'}.items():
 steps=load(fn); print('CASE',cname,[x[0] for x in steps], flush=True)
 for bpw in range(1,14):
  topn=1<<bpw
  for rev in [False,True]:
   bits=''; infos=[]; ok=True
   for rank,p in steps:
    if rank>=topn: ok=False; break
    c=code_for_rank((p[:topn]/p[:topn].sum()), rank)
    if rev: c=c[::-1]
    bits+=c; infos.append((rank,len(c),c))
   if not ok: continue
   found=[]; good=[]
   for v in variants(bits):
    if b'grod' in v[3] or b'flag' in v[3].lower(): found.append(v)
    if len(v[3])>=5 and score(v[3])>.85: good.append(v)
   if found or good:
    print('\n',cname,'bpw',bpw,'rev',rev,'len',len(bits),'bits',bits[:160], flush=True)
    for x in found or good[:4]: print(x[:3],x[3][:100], flush=True)
    print('infos',infos, flush=True)
    if found: sys.exit(0)
