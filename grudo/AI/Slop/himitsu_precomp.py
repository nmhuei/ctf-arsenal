import struct, numpy as np
from llama_cpp import Llama
llm=Llama(model_path='models/qwen2.5-0.5b-instruct-q4_k_m.gguf', n_ctx=16, logits_all=True, verbose=False, n_threads=1)

def load(path):
    with open(path,'rb') as f:
        assert f.read(4)==b'LGTS'
        nsteps,nvocab,temp,top_p,min_p,top_k=struct.unpack('<IIfffI', f.read(24))
        steps=[]
        for _ in range(nsteps):
            target=struct.unpack('<i', f.read(4))[0]
            logits=np.frombuffer(f.read(4*nvocab), dtype=np.float32).copy()
            steps.append((target,logits))
    return steps

def dec(steps, temp=1.0, minp=1e-6, top_k=0, rev=False, resolve=False):
    bits=''; infos=[]
    for target,logits0 in steps:
        logits=logits0.astype(np.float64)/temp
        order=np.argsort(-logits)
        if top_k and top_k>0: order=order[:top_k]
        z=logits[order]-logits[order[0]]; p=np.exp(z); p=p/p.sum()
        count=max(int((p>=minp).sum()),1)
        cand=order[:count]
        if resolve:
            # remove token bytes that are prefixes of another candidate; O(n^2) but only use for moderate count
            bs=[llm.detokenize([int(x)]) for x in cand]
            new=[]
            for i,b in enumerate(bs):
                if any(i!=j and c.startswith(b) for j,c in enumerate(bs)):
                    continue
                new.append(i)
            bit_count=len(new).bit_length()-1
            posarr=np.where(cand==target)[0]
            if len(posarr)==0: return None
            sp=int(posarr[0])
            if sp not in new: return None
            idx=new.index(sp)
        else:
            posarr=np.where(cand==target)[0]
            if len(posarr)==0: return None
            idx=int(posarr[0]); bit_count=count.bit_length()-1
        if bit_count>0:
            if idx >= (1<<bit_count): return None
            b=format(idx, f'0{bit_count}b')
            bits+=b[::-1] if rev else b
        infos.append((target,idx,bit_count,count))
    return bits,infos

def decode_bytes(bits):
    outs=[]
    for srcname,src in [('bits',bits),('revall',bits[::-1])]:
        for off in range(8):
            if len(src)-off>=8:
                bs=bytes(int(src[i:i+8],2) for i in range(off,len(src)-7,8))
                outs.append((srcname,off,'normal',bs))
                bs2=bytes(int(src[i:i+8][::-1],2) for i in range(off,len(src)-7,8))
                outs.append((srcname,off,'byterev',bs2))
    return outs

def show(label,bits,infos,force=False):
    found=False
    for srcname,off,kind,bs in decode_bytes(bits):
        if b'grod' in bs or b'flag' in bs or b'grodno' in bs:
            found=True
    if not (found or force): return
    print('\n'+label,'len',len(bits),'bits',bits)
    for srcname,off,kind,bs in decode_bytes(bits):
        if b'grod' in bs or b'flag' in bs or (off==0 and kind=='normal' and srcname=='bits'):
            print(srcname,off,kind,bs[:100])
    print('infos',infos)

cases={'header1':('header_full_temp1.bin',1.0), 'header08':('header_full_temp08.bin',0.8), 'bos1':('bos_full_temp1.bin',1.0), 'bos08':('bos_full_temp08.bin',0.8), 'chat1':('chat_empty_full_temp1.bin',1.0), 'chat08':('chat_empty_full_temp08.bin',0.8)}
mins=[]
for e in np.linspace(-1,-8,71): mins.append(10**e)
mins += [2e-6,1.5e-6,8e-7,5e-7,3e-7,2e-7,1e-7,1e-8,0.0]
mins=sorted(set(mins), reverse=True)
for cname,(fn,temp) in cases.items():
    steps=load(fn)
    for top_k in [0,8192,4096,2048,1024,512,256,128,64,32,16]:
      for minp in mins:
        for rev in [False,True]:
          r=dec(steps,temp=temp,minp=minp,top_k=top_k,rev=rev,resolve=False)
          if not r: continue
          bits,infos=r
          force=(cname.startswith('header') and top_k in [0,4096,2048] and 60<=len(bits)<=120 and not rev and minp in [1e-06,1e-07,1e-08,0.0])
          show(f'{cname} topk={top_k} minp={minp:.2g} rev={rev} noresolve',bits,infos,force=force)
# selected resolve tests with candidate sizes around 2k-8k
for cname,(fn,temp) in {'header1':cases['header1'], 'header08':cases['header08']}.items():
    steps=load(fn)
    for top_k in [0,4096,2048,1024,512,256]:
      for minp in [1e-4,5e-5,1e-5,5e-6,2e-6,1e-6,5e-7,1e-7,0.0]:
        for rev in [False,True]:
          r=dec(steps,temp=temp,minp=minp,top_k=top_k,rev=rev,resolve=True)
          if r: show(f'{cname} topk={top_k} minp={minp:g} rev={rev} resolve',r[0],r[1],force=True)
