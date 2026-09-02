import struct, numpy as np, re, base64, zlib, gzip, bz2, lzma

def load(fn):
    with open(fn,'rb') as f:
        assert f.read(4)==b'LGTS'
        nsteps,nv,temp,tp,mp,tk=struct.unpack('<IIfffI',f.read(24))
        steps=[]
        for _ in range(nsteps):
            target=struct.unpack('<i',f.read(4))[0]
            logits=np.frombuffer(f.read(4*nv),dtype=np.float32).copy().astype(np.float64)
            steps.append((target,logits))
    return steps

def int2bits(inp,num_bits):
    return [int(x) for x in reversed(('{0:0%db}'%num_bits).format(int(inp)))]
def bits2int(bits):
    return sum(int(b)*(1<<i) for i,b in enumerate(bits))
def same(a,b):
    for i,(x,y) in enumerate(zip(a,b)):
        if x!=y: return i
    return len(a)

def decode(steps, precision=26, topk=50, temp=1.0, mask_special=False, add_final=True, round_mode='rint'):
    max_val=1<<precision; cur=[0,max_val]; msg=[]; infos=[]
    for si,(target,logits0) in enumerate(steps):
        logits=logits0.copy()
        # mimic GPT2 mask? For Qwen, try masking eos/bos maybe separately outside
        if mask_special:
            for tid in [151643,151644,151645]:
                if tid < len(logits): logits[tid] = -1e20
        order=np.argsort(-logits)
        rank=int(np.where(order==target)[0][0])
        logits_sorted=logits[order].astype(np.float64)/temp
        z=logits_sorted-logits_sorted[0]; probs=np.exp(z); probs/=probs.sum()
        rng=cur[1]-cur[0]
        tmp=np.nonzero(probs < 1/rng)[0]
        if len(tmp)==0: k=topk
        else: k=min(max(2,int(tmp[0])), topk)
        k=min(k,len(probs))
        if rank>=k:
            return None, [('rank>=k',si,rank,k,target)]
        vals=probs[:k]/probs[:k].sum()*rng
        if round_mode=='floor': ints=np.floor(vals).astype(np.int64)
        elif round_mode=='ceil': ints=np.ceil(vals).astype(np.int64)
        else: ints=np.rint(vals).astype(np.int64)
        cum=np.cumsum(ints)
        over=np.nonzero(cum > rng)[0]
        if len(over)>0:
            cut=int(over[0]); cum=cum[:cut]; k=cut
            if rank>=k: return None,[('rank>=cut',si,rank,k)]
        if len(cum)==0: return None,[('empty',si)]
        cum[-1]+=rng-int(cum[-1]); cum=cum+cur[0]
        bottom=int(cum[rank-1]) if rank>0 else cur[0]
        top=int(cum[rank])
        bbits=list(reversed(int2bits(bottom,precision)))
        tbits=list(reversed(int2bits(top-1,precision)))
        n=same(bbits,tbits)
        newbits=bbits if (add_final and si==len(steps)-1) else tbits[:n]
        msg += newbits
        cur=[bits2int(reversed(bbits[n:]+[0]*n)), bits2int(reversed(tbits[n:]+[1]*n))+1]
        infos.append((si,rank,k,n,''.join(map(str,newbits))))
    return ''.join(map(str,msg)), infos

def variants(bits):
    for name,s in [('bits',bits),('revall',bits[::-1])]:
        for off in range(8):
            if len(s)-off>=8:
                b=bytes(int(s[i:i+8],2) for i in range(off,len(s)-7,8)); yield name,off,'normal',b
                br=bytes(int(s[i:i+8][::-1],2) for i in range(off,len(s)-7,8)); yield name,off,'byterev',br

def transforms(b):
    yield 'raw',b
    yield 'strip0',b.rstrip(b'\0')
    for fnn,fn in [('zlib',zlib.decompress),('gzip',gzip.decompress),('bz2',bz2.decompress),('lzma',lzma.decompress)]:
        try: yield fnn,fn(b)
        except Exception: pass
    for pad in [b'',b'=',b'==']:
        try: yield 'b64',base64.b64decode(b+pad,validate=False)
        except Exception: pass

def score(b): return sum(32<=x<127 or x in (9,10,13) for x in b)/max(1,len(b))
files=['header_full_temp1.bin','bos_header_temp1.bin','eos_header_temp1.bin','header_full_temp08.bin','bos_header_temp08.bin','eos_header_temp08.bin']
for fn in files:
    steps=load(fn)
    print('CASE',fn)
    for precision in range(8,65):
      for topk in [2,4,8,16,32,40,48,50,64,80,100,128,256,512,1024,2048,4096,8192,16384,32768,50000,65536,100000,151936]:
       for temp in [1.0,0.8]:
        for mask in [False,True]:
         for final in [True,False]:
          for rnd in ['rint']:#,'floor','ceil']:
            bits,infos=decode(steps,precision,topk,temp,mask,final,rnd)
            if bits is None: continue
            found=[]; good=[]
            for v in variants(bits):
                for tn,out in transforms(v[3]):
                    if b'grodno{' in out or b'grod' in out or b'flag' in out.lower():
                        found.append((v[:3],tn,out))
                    elif len(out)>=6 and score(out)>0.95 and (b'{' in out or b'}' in out or b'_' in out):
                        good.append((v[:3],tn,out))
            if found or good:
                print('HIT',fn,'prec',precision,'topk',topk,'temp',temp,'mask',mask,'final',final,'len',len(bits),'bits',bits[:160])
                for x in found or good[:5]: print(' ',x)
                print(' infos',infos)
                if found: raise SystemExit
print('done')
