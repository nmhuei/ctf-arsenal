import struct, numpy as np, math, itertools, zlib, gzip, bz2, lzma, base64

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

def int2bits(x, precision):
    return [(int(x)>>i)&1 for i in range(precision)]  # LSB first, matches utils likely when reversed used

def bits2int(bits_iter):
    x=0
    for i,b in enumerate(bits_iter):
        x |= (int(b)&1)<<i
    return x

def num_same_from_beg(a,b):
    c=0
    for x,y in zip(a,b):
        if x==y: c+=1
        else: break
    return c

def decode_saac(steps, precision=16, topk=50000, final_bottom=True, rank_base=0, round_mode='rint'):
    max_val=1<<precision
    cur=[0,max_val]
    message=[]; infos=[]
    for si,(rank0,p_all) in enumerate(steps):
        rank=rank0+rank_base
        rng=cur[1]-cur[0]
        threshold=1.0/rng
        below=np.nonzero(p_all < threshold)[0]
        if len(below)==0: k=topk
        else: k=min(max(2,int(below[0])), topk)
        # also no more than vocab
        k=min(k,len(p_all))
        if rank<0 or rank>=k:
            return None, [('rank>=k',si,rank,k,threshold)]
        probs=p_all[:k]
        vals=probs/probs.sum()*rng
        if round_mode=='floor': ints=np.floor(vals).astype(object)
        elif round_mode=='ceil': ints=np.ceil(vals).astype(object)
        else: ints=np.rint(vals).astype(object)
        cum=np.cumsum(ints, dtype=object)
        # remove overfill; code uses cum_probs[:overfill_index[0]] (excludes first overfill)
        over=[i for i,x in enumerate(cum) if x>rng]
        if over:
            cut=over[0]
            cum=cum[:cut]
            k=cut
            if rank>=k: return None, [('rank>=k_after_over',si,rank,k,rng)]
        if len(cum)==0: return None, [('empty',si)]
        cum[-1] += rng-cum[-1]
        cum=[int(x)+cur[0] for x in cum]
        bottom = cum[rank-1] if rank>0 else cur[0]
        top = cum[rank]
        if top<=bottom: return None, [('zero_range',si,rank,k,bottom,top)]
        bot_bits=list(reversed(int2bits(bottom, precision)))
        top_bits=list(reversed(int2bits(top-1, precision)))
        same=num_same_from_beg(bot_bits, top_bits)
        if final_bottom and si==len(steps)-1:
            new_bits=bot_bits
        else:
            new_bits=top_bits[:same]
        message += new_bits
        new_bot_bits=bot_bits[same:]+[0]*same
        new_top_bits=top_bits[same:]+[1]*same
        cur[0]=bits2int(reversed(new_bot_bits))
        cur[1]=bits2int(reversed(new_top_bits))+1
        infos.append((si,rank,k,same,rng,bottom,top))
    return ''.join(str(x) for x in message), infos

def variants(bits):
    for srcname,src in [('bits',bits),('revall',bits[::-1])]:
        for off in range(8):
            if len(src)-off>=8:
                bs=bytes(int(src[i:i+8],2) for i in range(off,len(src)-7,8))
                yield srcname,off,'normal',bs
                bs2=bytes(int(src[i:i+8][::-1],2) for i in range(off,len(src)-7,8))
                yield srcname,off,'byterev',bs2

def try_decodings(b):
    cands=[b]
    for fn in [zlib.decompress,gzip.decompress,bz2.decompress,lzma.decompress]:
        try: cands.append(fn(b))
        except Exception: pass
    try: cands.append(base64.b64decode(b, validate=False))
    except Exception: pass
    return cands

def printable_score(b):
    return sum(32<=x<127 or x in (9,10,13) for x in b)/max(1,len(b))

def show(label,bits,infos,force=False):
    found=[]; good=[]
    for srcname,off,kind,bs in variants(bits):
        for bb in try_decodings(bs):
            if b'grodno{' in bb or b'grod' in bb or b'flag' in bb.lower(): found.append((srcname,off,kind,bb))
        if len(bs)>=5 and printable_score(bs)>0.85: good.append((srcname,off,kind,bs))
    if found or force or good:
        print('\n'+label,'len',len(bits),'bits',bits[:200])
        for item in found or good[:6] or list(variants(bits))[:1]: print(item[:3], item[3][:120])
        print('infos',infos)
        return bool(found)
    return False

cases={'header1':'header_full_temp1.bin','header08':'header_full_temp08.bin','bos1':'bos_full_temp1.bin','bos08':'bos_full_temp08.bin','chat1':'chat_empty_full_temp1.bin','chat08':'chat_empty_full_temp08.bin'}
for cname,fn in cases.items():
    steps=load(fn)
    print('CASE',cname,'positions',[x[0] for x in steps])
    for precision in list(range(8,33))+[40,48,56,64]:
      for topk in [50000,0,151936,100000,65536,32768,16384,8192,4096,2048]:
        if topk==0: tk=len(steps[0][1])
        else: tk=topk
        for final_bottom in [True,False]:
          for round_mode in ['rint','floor','ceil']:
            bits,infos=decode_saac(steps,precision=precision,topk=tk,final_bottom=final_bottom,round_mode=round_mode)
            if bits is None: continue
            force=(cname.startswith('header') and precision in [16,24,32] and topk in [50000,0,151936] and final_bottom and round_mode=='rint')
            if show(f'{cname} prec={precision} topk={tk} finalbottom={final_bottom} round={round_mode}',bits,infos,force=force):
                raise SystemExit
