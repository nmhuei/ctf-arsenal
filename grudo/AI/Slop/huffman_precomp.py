import struct, numpy as np, heapq, itertools, zlib, gzip, bz2, lzma, base64

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

def codes_for(probs):
    # approximate code's heap ordering: HeapNode __lt__ only by freq; equal not important.
    heap=[]; counter=itertools.count(); codes={}
    for i,fr in enumerate(probs): heapq.heappush(heap,(float(fr), next(counter), i))
    parent={}
    while len(heap)>1:
        f1,c1,n1=heapq.heappop(heap); f2,c2,n2=heapq.heappop(heap)
        m=('n',next(counter))
        parent[n1]=(m,'0'); parent[n2]=(m,'1')
        heapq.heappush(heap,(f1+f2,next(counter),m))
    for i in range(len(probs)):
        n=i; bits=[]
        while n in parent:
            n,b=parent[n]; bits.append(b)
        codes[i]=''.join(reversed(bits))
    return codes

def decode(steps,bpw,revcode=False):
    topn=1<<bpw; bits=''; infos=[]
    for rank,p in steps:
        if rank>=topn: return None
        q=p[:topn]
        q=q/q.sum()
        c=codes_for(q)[rank]
        if revcode: c=c[::-1]
        bits+=c; infos.append((rank,len(c),c))
    return bits,infos

def variants(bits):
 for srcname,src in [('bits',bits),('revall',bits[::-1])]:
  for off in range(8):
   if len(src)-off>=8:
    bs=bytes(int(src[i:i+8],2) for i in range(off,len(src)-7,8)); yield srcname,off,'normal',bs
    bs2=bytes(int(src[i:i+8][::-1],2) for i in range(off,len(src)-7,8)); yield srcname,off,'byterev',bs2

def score(b): return sum(32<=x<127 or x in (9,10,13) for x in b)/max(1,len(b))
def show(label,bits,infos):
 found=[]; good=[]
 for v in variants(bits):
  if b'grodno{' in v[3] or b'grod' in v[3] or b'flag' in v[3].lower(): found.append(v)
  if len(v[3])>=5 and score(v[3])>.85: good.append(v)
 if found or good:
  print('\n'+label,'len',len(bits),'bits',bits[:160])
  for x in found or good[:6]: print(x[:3],x[3][:120])
  print('infos',infos)
  return bool(found)
 return False
for cname,fn in {'header1':'header_full_temp1.bin','bos1':'bos_full_temp1.bin','chat1':'chat_empty_full_temp1.bin','header08':'header_full_temp08.bin'}.items():
 steps=load(fn); print('CASE',cname,[x[0] for x in steps])
 for bpw in range(1,18):
  for rev in [False,True]:
   r=decode(steps,bpw,rev)
   if r and show(f'{cname} bpw={bpw} rev={rev}',r[0],r[1]): raise SystemExit
