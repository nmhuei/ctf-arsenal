from llama_cpp import Llama
import numpy as np
from decimal import Decimal, getcontext
getcontext().prec=300
llm=Llama(model_path='models/qwen2.5-0.5b-instruct-q4_k_m.gguf', n_ctx=512, logits_all=True, verbose=False, n_threads=4)
out=llm.tokenize(open('message.txt','rb').read(), add_bos=False, special=True)

def get_probs(logits, temp=1.0, top_k=None, top_p=None, min_p=0.0, descending=True):
    z=logits.astype(np.float64)/temp
    # start with all tokens or top_k
    idx=np.arange(len(z))
    if top_k is not None and top_k>0 and top_k<len(z):
        idx=np.argpartition(-z, top_k-1)[:top_k]
    # sort by descending logits/prob
    order=np.argsort(-z[idx]) if descending else np.argsort(z[idx])
    idx=idx[order]
    zz=z[idx]
    zz-=zz.max()
    p=np.exp(zz)
    p=p/p.sum()
    # top_p nucleus descending only after sorting desc
    if top_p is not None and top_p<1.0:
        cs=np.cumsum(p)
        keep=cs<=top_p
        if len(keep)>0: keep[0]=True
        # include first token crossing
        j=np.searchsorted(cs, top_p, side='left')
        keep[:min(len(keep),j+1)]=True
        idx=idx[keep]; p=p[keep]; p=p/p.sum()
    if min_p and min_p>0:
        keep=p >= p.max()*min_p
        idx=idx[keep]; p=p[keep]; p=p/p.sum()
    return idx,p

def decode(ctx,label,params):
    lo=Decimal(0); hi=Decimal(1)
    ctx=list(ctx)
    ok=True
    for i,t in enumerate(out):
        llm.reset(); llm.eval(ctx)
        logits=np.array(llm._scores[len(ctx)-1])
        idx,p=get_probs(logits, **params)
        pos=np.where(idx==t)[0]
        if len(pos)==0:
            print(label,params,'token not allowed step',i,t); return
        pos=int(pos[0])
        c0=float(p[:pos].sum()); c1=float(p[:pos+1].sum())
        rng=hi-lo
        lo,hi=lo+rng*Decimal(str(c0)), lo+rng*Decimal(str(c1))
        ctx.append(t)
    mid=(lo+hi)/2
    # binary expansion of mid
    x=mid
    bits=''
    for _ in range(240):
        x*=2
        if x>=1:
            bits+='1'; x-=1
        else: bits+='0'
    outs=[]
    for off in range(8):
        b=bytes(int(bits[i:i+8],2) for i in range(off, len(bits)-7, 8))
        if b'grodno' in b or off==0:
            outs.append((off,b[:80]))
    print('\n',label,params,'width_bits~',-(hi-lo).log10()/Decimal(2).log10())
    print('lo', str(lo)[:80], 'hi',str(hi)[:80])
    for off,b in outs: print('off',off,b)

def ids(s): return llm.tokenize(s.encode(), add_bos=False, special=True)
contexts={
 'bos':[llm.token_bos()],
 'raw_empty':[],
 'prompt_header': ids('A short recipe for a winter vegetable soup:\n'),
 'chat_empty': ids('<|im_start|>system\nYou are Qwen, created by Alibaba Cloud. You are a helpful assistant.<|im_end|>\n<|im_start|>user\n<|im_end|>\n<|im_start|>assistant\n'),
}
# raw_empty cannot eval no ctx for first; skip unless prefix one token? handled?
param_list=[]
for desc in [True,False]:
 for temp in [1.0,0.8]:
  for filt in [dict(top_k=None,top_p=None,min_p=0.0), dict(top_k=0,top_p=1.0,min_p=0.0), dict(top_k=40,top_p=0.95,min_p=0.05), dict(top_k=2048,top_p=1.0,min_p=0.0), dict(top_k=4096,top_p=1.0,min_p=0.0)]:
   d={'temp':temp,'descending':desc}; d.update(filt); param_list.append(d)
for label,ctx in contexts.items():
 if not ctx: continue
 for params in param_list:
  decode(ctx,label,params)
