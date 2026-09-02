from llama_cpp import Llama
import numpy as np, zlib, gzip, bz2, lzma, base64, sys
llm=Llama(model_path='models/qwen2.5-0.5b-instruct-q4_k_m.gguf', n_ctx=1024, logits_all=True, verbose=False, n_threads=4)
full=llm.tokenize(open('message.txt','rb').read(), add_bos=False, special=True)
header=full[:9]; cont=full[9:]
V=llm.n_vocab()

def int2bits(x,n):
    return [int(c) for c in reversed(f'{int(x):0{n}b}')]
def bits2int(bits):
    res=0
    for i,b in enumerate(bits): res += int(b)*(1<<i)
    return res
def num_same(a,b):
    c=0
    for x,y in zip(a,b):
        if x==y: c+=1
        else: break
    return c
def tokb(t): return llm.detokenize([int(t)])
def toks(b): return llm.tokenize(b, add_bos=False, special=True)
def score(b): return sum(32<=x<127 or x in (9,10,13) for x in b)/max(1,len(b))
def variants(bits):
    s=''.join(map(str,bits))
    for sname,src in [('bits',s),('revall',s[::-1])]:
      for off in range(8):
        if len(src)-off>=8:
          bs=bytes(int(src[i:i+8],2) for i in range(off,len(src)-7,8)); yield sname,off,'normal',bs
          bs2=bytes(int(src[i:i+8][::-1],2) for i in range(off,len(src)-7,8)); yield sname,off,'byterev',bs2

def show(label,bits,log,force=False):
    found=[]; good=[]
    for v in variants(bits):
        bs=v[3]
        outs=[bs]
        for fn in [zlib.decompress,gzip.decompress,bz2.decompress,lzma.decompress]:
            try: outs.append(fn(bs))
            except Exception: pass
        try: outs.append(base64.b64decode(bs,validate=False))
        except Exception: pass
        for out in outs:
            if b'grodno{' in out or b'grod' in out or b'flag' in out.lower(): found.append(v[:3]+(out,))
        if len(bs)>=5 and score(bs)>0.88: good.append(v)
    if found or good or force:
        print('\n'+label,'len',len(bits),''.join(map(str,bits))[:300])
        for x in found or good[:8] or list(variants(bits))[:2]: print(x[:3],x[3][:160])
        print('log')
        for row in log: print(' ',row)
        return bool(found)
    return False

def decode(context, inp0, precision=16, topk=50000, temp=1.0, max_steps=100):
    max_val=1<<precision; cur=[0,max_val]
    inp=list(inp0); prev=list(context); message=[]; log=[]; i=0
    while i < len(inp) and i < max_steps:
        llm.reset(); llm.eval(prev)
        logits=np.array(llm._scores[len(prev)-1], dtype=np.float64)
        # no explicit GPT2 masks; optionally could mask special empty tokens? try not
        order=np.argsort(-logits)
        sorted_logits=logits[order]/temp
        z=sorted_logits-sorted_logits[0]; probs=np.exp(z); probs=probs/probs.sum()
        rng=cur[1]-cur[0]
        threshold=1/rng
        tmp=np.nonzero(probs < threshold)[0]
        if len(tmp)==0: k=topk
        else: k=min(max(2,int(tmp[0])), topk)
        k=min(k,len(probs))
        probs_int=probs[:k]/probs[:k].sum()*rng
        probs_int=np.rint(probs_int).astype(np.int64)
        cum=np.cumsum(probs_int)
        over=np.nonzero(cum > rng)[0]
        if len(over)>0:
            cut=int(over[0]); cum=cum[:cut]; k=cut
        if k<=0 or len(cum)==0: return None, [('empty',i)]
        cum[-1] += rng-int(cum[-1])
        cum=cum+cur[0]
        t=int(inp[i]); pos=np.where(order==t)[0]
        rank=int(pos[0]) if len(pos) else 10**9
        orig_rank=rank; corrected=''
        if rank >= k:
            true=tokb(t)
            # scan top k candidates only exactly like paper, skip empty prop to avoid loops
            fixed=False
            for rank_idx in range(k):
                prop=tokb(order[rank_idx])
                if prop==b'':
                    continue
                if len(prop) <= len(true) and true.startswith(prop):
                    rank=rank_idx
                    suffix=true[len(prop):]
                    inp[i]=int(order[rank_idx])
                    suff=toks(suffix)
                    inp[i+1:i+1]=suff
                    corrected=f'prefix {prop!r}+{suffix!r}->{suff}'
                    fixed=True
                    break
                elif len(prop) > len(true) and prop.startswith(true):
                    whole=true; num_extra=1
                    while len(whole)<len(prop) and i+num_extra<len(inp):
                        whole += tokb(inp[i+num_extra]); num_extra += 1
                    if prop == whole[:len(prop)]:
                        rank=rank_idx
                        inp[i]=int(order[rank_idx])
                        for _ in range(1,num_extra):
                            if i+1 < len(inp): del inp[i+1]
                        if len(whole)>len(prop):
                            suffix=whole[len(prop):]
                            inp[i+1:i+1]=toks(suffix)
                        corrected=f'long {true!r}->{prop!r}'
                        fixed=True
                        break
            if not fixed:
                rank=0; corrected=f'UNFIXED true={true!r} orig_rank={orig_rank} k={k}'
        if rank>=len(cum):
            return None, [('rank>=cum',i,rank,k,orig_rank,corrected)]
        bottom=int(cum[rank-1]) if rank>0 else cur[0]
        top=int(cum[rank])
        bot_bits=list(reversed(int2bits(bottom,precision)))
        top_bits=list(reversed(int2bits(top-1,precision)))
        same=num_same(bot_bits,top_bits)
        if i==len(inp)-1:
            new_bits=bot_bits
        else:
            new_bits=top_bits[:same]
        message += new_bits
        new_bot=bot_bits[same:]+[0]*same
        new_top=top_bits[same:]+[1]*same
        cur=[bits2int(reversed(new_bot)), bits2int(reversed(new_top))+1]
        log.append((i,t,tokb(t),'orig_rank',orig_rank,'k',k,'rank',rank,'bits',''.join(map(str,new_bits)), 'corr', corrected,'inp_len',len(inp),'cur',cur))
        prev=[int(inp[i])]
        i+=1
    return message,log

for cname,ctx,inp in [('header',header,cont),('bos',[llm.token_bos()],full)]:
  for temp in [1.0,0.8]:
    for precision in list(range(4,41))+[48,56,64]:
      for topk in [50000,151936,100000,65536,32768,16384,8192,4096,2048,1024,512,256,128,64,32,16,8,4,2]:
        r=decode(ctx,inp,precision,topk,temp)
        if r[0] is None: continue
        bits,log=r
        force=(cname=='header' and temp==1.0 and precision in [8,12,16,24,32,40] and topk in [50000,151936])
        if show(f'{cname} temp={temp} prec={precision} topk={topk}',bits,log,force):
            sys.exit(0)
print('done')
