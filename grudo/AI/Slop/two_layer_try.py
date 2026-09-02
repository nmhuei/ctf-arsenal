from llama_cpp import Llama
import numpy as np, struct, re, math, sys
llm=Llama(model_path='models/qwen2.5-0.5b-instruct-q4_k_m.gguf', n_ctx=2048, logits_all=True, verbose=False, n_threads=4)
print('bos/eos', llm.token_bos(), llm.token_eos())

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

def stego_decode(steps,prec,topk,temp=1.0,final=True):
    cur=[0,1<<prec]; out=[]; infos=[]
    for si,(target,logits) in enumerate(steps):
        order=np.argsort(-logits); rank=int(np.where(order==target)[0][0])
        z=logits[order].astype(np.float64)/temp; z-=z[0]; p=np.exp(z); p/=p.sum(); rng=cur[1]-cur[0]
        tmp=np.nonzero(p < 1/rng)[0]; k=topk if len(tmp)==0 else min(max(2,int(tmp[0])),topk); k=min(k,len(p))
        if rank>=k: return None
        vals=p[:k]/p[:k].sum()*rng; ints=np.rint(vals).astype(object); cum=np.cumsum(ints,dtype=object)
        over=[i for i,x in enumerate(cum) if x>rng]
        if over: cum=cum[:over[0]]; k=over[0]
        if rank>=len(cum) or len(cum)==0: return None
        cum[-1]+=rng-cum[-1]; cum=[int(x)+cur[0] for x in cum]
        bot=cum[rank-1] if rank>0 else cur[0]; top=cum[rank]
        bb=list(reversed(int2bits(bot,prec))); tb=list(reversed(int2bits(top-1,prec))); n=same(bb,tb)
        nb=bb if (final and si==len(steps)-1) else tb[:n]
        out+=nb; infos.append((si,rank,k,n,''.join(map(str,nb))))
        cur=[bits2int(reversed(bb[n:]+[0]*n)), bits2int(reversed(tb[n:]+[1]*n))+1]
    return out,infos

def lm_decode_bits(bits, context, prec=40, topk=60000, temp=1.0, max_steps=80, stop_tokens=None):
    cur=[0,1<<prec]; i=0; out=[]; ctx=list(context)
    if stop_tokens is None: stop_tokens=set()
    for step in range(max_steps):
        llm.reset(); llm.eval(ctx)
        logits=np.array(llm._scores[len(ctx)-1],dtype=np.float64)
        # mask eog? maybe not; try variants outside maybe
        order=np.argsort(-logits)
        z=logits[order]/temp; z-=z[0]; p=np.exp(z); p/=p.sum(); rng=cur[1]-cur[0]
        tmp=np.nonzero(p < 1/rng)[0]; k=topk if len(tmp)==0 else min(max(2,int(tmp[0])),topk); k=min(k,len(p))
        vals=p[:k]/p[:k].sum()*rng; ints=np.rint(vals).astype(object); cum=np.cumsum(ints,dtype=object)
        over=[j for j,x in enumerate(cum) if x>rng]
        if over: cum=cum[:over[0]]; k=over[0]
        if len(cum)==0: break
        cum[-1]+=rng-cum[-1]; cum=[int(x)+cur[0] for x in cum]
        mbits=bits[i:i+prec]
        if len(mbits)<prec: mbits=mbits+[0]*(prec-len(mbits))
        midx=bits2int(reversed(mbits))
        sel=0
        while sel<len(cum) and cum[sel]<=midx: sel+=1
        if sel>=len(cum): return None,'sel_oob'
        token=int(order[sel]); out.append(token)
        bot=cum[sel-1] if sel>0 else cur[0]; top=cum[sel]
        bb=list(reversed(int2bits(bot,prec))); tb=list(reversed(int2bits(top-1,prec))); n=same(bb,tb)
        i+=n
        cur=[bits2int(reversed(bb[n:]+[0]*n)), bits2int(reversed(tb[n:]+[1]*n))+1]
        ctx.append(token)
        text=llm.detokenize(out).decode('utf-8','ignore')
        if 'grodno{' in text or token in stop_tokens or '<eos>' in text or '}' in text:
            return out,text
        if i>=len(bits)+prec and step>5:
            return out,text
    return out,llm.detokenize(out).decode('utf-8','ignore')

files=['header_full_temp1.bin','bos_header_temp1.bin','eos_header_temp1.bin','header_full_temp08.bin','bos_header_temp08.bin','eos_header_temp08.bin']
outer_params=[]
for prec in [16,20,24,26,28,32,40,48,56,64]:
 for topk in [2048,4096,8192,16384,32768,50000,60000,65536,100000,151936]:
  for temp in [1.0,0.8]: outer_params.append((prec,topk,temp))
contexts={'bos':[llm.token_bos()],'eos':[llm.token_eos()],'bos_grodno':llm.tokenize(b'grodno{',add_bos=True,special=True),'empty_as_bos':[llm.token_bos()]}
for fn in files:
 steps=load(fn)
 print('CASE',fn,flush=True)
 for op in outer_params:
  r=stego_decode(steps,*op)
  if not r: continue
  bits,infos=r
  for revbits_name,bits2 in [('bits',bits),('rev',bits[::-1])]:
   for ctxname,ctx in contexts.items():
    for iprec in [32,40,48,56,64]:
     for itopk in [50000,60000,65536,100000,151936]:
      ans,text=lm_decode_bits(bits2,ctx,prec=iprec,topk=itopk,temp=1.0,max_steps=50)
      if isinstance(text,str) and ('grodno{' in text or 'grod' in text or 'flag' in text.lower()):
       print('FOUNDLIKE',fn,op,revbits_name,ctxname,iprec,itopk,repr(text),ans,infos,flush=True)
       if 'grodno{' in text: raise SystemExit
print('done')
