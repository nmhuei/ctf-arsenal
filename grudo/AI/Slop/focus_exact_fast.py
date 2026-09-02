from llama_cpp import Llama
import numpy as np, struct, itertools
llm=Llama(model_path='models/qwen2.5-0.5b-instruct-q4_k_m.gguf', n_ctx=2048, logits_all=True, verbose=False, n_threads=6)

def load(fn):
    f=open(fn,'rb'); assert f.read(4)==b'LGTS'
    n,nv,temp,tp,mp,tk=struct.unpack('<IIfffI',f.read(24)); steps=[]
    for _ in range(n):
        target=struct.unpack('<i',f.read(4))[0]
        logits=np.frombuffer(f.read(4*nv),dtype=np.float32).copy()
        steps.append((target,logits))
    return steps

def int2bits(x,n): return [int(c) for c in reversed(f'{int(x):0{n}b}')]
def bits2int(bits): return sum(int(b)*(1<<i) for i,b in enumerate(bits))
def same(a,b):
    for i,(x,y) in enumerate(zip(a,b)):
        if x!=y: return i
    return len(a)

def stego_decode(steps,prec,topk,temp=1.0,rounder='rint',final=True):
    cur=[0,1<<prec]; out=[]; infos=[]
    for si,(target,logits) in enumerate(steps):
        order=np.argsort(-logits)
        rank=int(np.where(order==target)[0][0])
        z=logits[order].astype(np.float64)/temp; z-=z[0]
        p=np.exp(z); p/=p.sum(); rng=cur[1]-cur[0]
        tmp=np.nonzero(p < 1/rng)[0]
        k=topk if len(tmp)==0 else min(max(2,int(tmp[0])),topk)
        k=min(k,len(p))
        if rank>=k: return None
        vals=p[:k]/p[:k].sum()*rng
        if rounder=='rint': ints=np.rint(vals).astype(object)
        elif rounder=='floor': ints=np.floor(vals).astype(object)
        elif rounder=='ceil': ints=np.ceil(vals).astype(object)
        else: raise ValueError(rounder)
        cum=np.cumsum(ints,dtype=object)
        over=[i for i,x in enumerate(cum) if x>rng]
        if over: cum=cum[:over[0]]; k=over[0]
        if rank>=len(cum) or not len(cum): return None
        cum[-1]+=rng-cum[-1]
        cum=[int(x)+cur[0] for x in cum]
        bot=cum[rank-1] if rank>0 else cur[0]; top=cum[rank]
        if top<=bot: return None
        bb=list(reversed(int2bits(bot,prec))); tb=list(reversed(int2bits(top-1,prec)))
        n=same(bb,tb)
        nb=bb if (final and si==len(steps)-1) else tb[:n]
        out+=nb; infos.append((si,rank,k,n,''.join(map(str,nb))))
        cur=[bits2int(reversed(bb[n:]+[0]*n)), bits2int(reversed(tb[n:]+[1]*n))+1]
    return out,infos

def lm_bits_to_text(bits, ctx, prec=64, topk=60000, temp=1.0, rounder='rint', max_steps=200, mask=None):
    cur=[0,1<<prec]; i=0; out=[]
    llm.reset(); llm.eval(list(ctx))
    for step in range(max_steps):
        logits=np.array(llm._scores[llm.n_tokens-1],dtype=np.float64)
        if mask:
            for t in mask:
                if 0<=t<len(logits): logits[t]=-1e20
        order=np.argsort(-logits)
        z=logits[order]/temp; z-=z[0]
        p=np.exp(z); p/=p.sum(); rng=cur[1]-cur[0]
        tmp=np.nonzero(p < 1/rng)[0]
        k=topk if len(tmp)==0 else min(max(2,int(tmp[0])),topk)
        k=min(k,len(p))
        vals=p[:k]/p[:k].sum()*rng
        if rounder=='rint': ints=np.rint(vals).astype(object)
        elif rounder=='floor': ints=np.floor(vals).astype(object)
        elif rounder=='ceil': ints=np.ceil(vals).astype(object)
        cum=np.cumsum(ints,dtype=object)
        over=[j for j,x in enumerate(cum) if x>rng]
        if over: cum=cum[:over[0]]; k=over[0]
        if not len(cum): return out,'EMPTY_CUM',i
        cum[-1]+=rng-cum[-1]
        cum=[int(x)+cur[0] for x in cum]
        mbits=bits[i:i+prec]
        if len(mbits)<prec: mbits=mbits+[0]*(prec-len(mbits))
        midx=bits2int(reversed(mbits))
        sel=0
        while sel<len(cum) and cum[sel]<=midx: sel+=1
        if sel>=len(cum): return out,'SEL_OOB',i
        token=int(order[sel]); out.append(token)
        bot=cum[sel-1] if sel>0 else cur[0]; top=cum[sel]
        bb=list(reversed(int2bits(bot,prec))); tb=list(reversed(int2bits(top-1,prec)))
        n=same(bb,tb); i+=n
        cur=[bits2int(reversed(bb[n:]+[0]*n)), bits2int(reversed(tb[n:]+[1]*n))+1]
        llm.eval([token])
        text=llm.detokenize(out).decode('utf-8','replace')
        print('step',step,'consumed',i,'tok',token,'sel',sel,'n',n,'tail=',repr(text[-120:]),flush=True)
        if i>=len(bits):
            return out,text,i
    return out,llm.detokenize(out).decode('utf-8','replace'),i

# exact known promising outer
bits,infos=stego_decode(load('header_full_temp1.bin'),24,2048,1.0,'rint',True)
print('OUTER bits len',len(bits),'infos',infos)
print('OUTER bits',''.join(map(str,bits)))
for ctxname,ctx in {'bos':[llm.token_bos()],'eos':[llm.token_eos()],'bos_grodno':llm.tokenize(b'grodno{',add_bos=True,special=True)}.items():
  print('\n===CTX',ctxname,ctx,'===')
  out,text,cons=lm_bits_to_text(bits,ctx,prec=64,topk=60000,temp=1.0,rounder='rint',max_steps=200)
  print('RESULT',ctxname,'cons',cons,'tokens',out)
  print(repr(text))
