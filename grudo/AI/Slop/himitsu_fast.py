import struct, numpy as np, math

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
            target_pos=int(np.where(order==target)[0][0])
            steps.append((target_pos,p))
        return steps

def dec(steps,minp,top_k=0,rev=False):
    bits=''; infos=[]
    for pos_all,p_all in steps:
        n = len(p_all) if top_k==0 else min(top_k,len(p_all))
        p=p_all[:n]; count=max(int((p>=minp).sum()),1)
        if pos_all>=count: return None
        bit_count=count.bit_length()-1
        idx=pos_all
        if bit_count>0:
            if idx >= (1<<bit_count): return None
            b=format(idx, f'0{bit_count}b')
            bits += b[::-1] if rev else b
        infos.append((idx,bit_count,count))
    return bits,infos

def variants(bits):
    for srcname,src in [('bits',bits),('revall',bits[::-1])]:
        for off in range(8):
            if len(src)-off>=8:
                bs=bytes(int(src[i:i+8],2) for i in range(off,len(src)-7,8))
                yield srcname,off,'normal',bs
                bs2=bytes(int(src[i:i+8][::-1],2) for i in range(off,len(src)-7,8))
                yield srcname,off,'byterev',bs2

def printable_score(b):
    if not b: return 0
    return sum(32<=x<127 or x in (10,13,9) for x in b)/len(b)

def show(label,bits,infos,force=False):
    found=[]
    best=[]
    for v in variants(bits):
        bs=v[3]
        if b'grod' in bs or b'flag' in bs or b'ctf' in bs.lower(): found.append(v)
        if printable_score(bs)>0.75 and len(bs)>=5: best.append(v)
    if not (found or force or best): return
    print('\n'+label,'len',len(bits),'bits',bits)
    for v in found or best[:4] or list(variants(bits))[:1]: print(v[:3],v[3][:100])
    print('infos',infos)

cases={'header1':'header_full_temp1.bin','header08':'header_full_temp08.bin','bos1':'bos_full_temp1.bin','bos08':'bos_full_temp08.bin','chat1':'chat_empty_full_temp1.bin','chat08':'chat_empty_full_temp08.bin'}
mins=sorted(set([10**(-k/10) for k in range(5,90)] + [2e-6,1.5e-6,8e-7,5e-7,3e-7,2e-7,1e-7,1e-8,0.0]), reverse=True)
for cname,fn in cases.items():
    steps=load(fn)
    print('case',cname,'steps',len(steps),'target_pos',[x[0] for x in steps])
    for top_k in [0,16384,8192,4096,2048,1024,512,256,128,64,32,16,8,4,2]:
      for minp in mins:
        for rev in [False,True]:
          r=dec(steps,minp,top_k,rev)
          if not r: continue
          bits,infos=r
          force=(cname.startswith('header') and top_k in [0,4096,2048,1024,512] and 50<=len(bits)<=130 and not rev and minp in [1e-06,1e-07,1e-08,0.0])
          show(f'{cname} topk={top_k} minp={minp:.2g} rev={rev}',bits,infos,force)
