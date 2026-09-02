from llama_cpp import Llama
import numpy as np
from decimal import Decimal, getcontext
getcontext().prec=500
llm=Llama(model_path='models/qwen2.5-0.5b-instruct-q4_k_m.gguf', n_ctx=1024, logits_all=True, verbose=False, n_threads=4)
toks=llm.tokenize(open('message.txt','rb').read(), add_bos=False, special=True)

def probs(logits,temp=1.0,top_k=0,top_p=1.0,min_p=0.0,descending=True):
    z=logits.astype(np.float64)/temp
    idx=np.arange(len(z))
    if top_k and top_k>0 and top_k<len(idx): idx=np.argpartition(-z, top_k-1)[:top_k]
    idx=idx[np.argsort(-z[idx] if descending else z[idx])]
    zz=z[idx]-z[idx].max(); p=np.exp(zz); p=p/p.sum()
    if top_p<1:
        cs=np.cumsum(p); j=np.searchsorted(cs,top_p,'left'); keep=np.arange(len(p))<=j
        idx=idx[keep]; p=p[keep]; p=p/p.sum()
    if min_p>0:
        keep=p>=p.max()*min_p; idx=idx[keep]; p=p[keep]; p=p/p.sum()
    return idx,p

def common_bits(lo,hi,maxbits=400):
    bits=''
    a=lo; b=hi
    for _ in range(maxbits):
        a*=2; b*=2
        abit = 1 if a>=1 else 0
        bbit = 1 if b>=1 else 0
        # hi is exclusive; use hi-epsilon issue ignored with high precision
        if abit!=bbit: break
        bits += '1' if abit else '0'
        if abit: a-=1; b-=1
    return bits

def bytes_from_bits(bits):
    outs=[]
    for off in range(8):
        bs=bytes(int(bits[i:i+8],2) for i in range(off,len(bits)-7,8))
        outs.append((off,bs))
    return outs

def run(label,prefix,targets,params):
    lo=Decimal(0); hi=Decimal(1); ctx=list(prefix)
    for t in targets:
        llm.reset(); llm.eval(ctx)
        idx,p=probs(np.array(llm._scores[len(ctx)-1]),**params)
        pos=np.where(idx==t)[0]
        if len(pos)==0:
            print(label,params,'not allowed',t); return
        pos=int(pos[0]); c0=Decimal(str(float(p[:pos].sum()))); c1=Decimal(str(float(p[:pos+1].sum())))
        rng=hi-lo; hi=lo+rng*c1; lo=lo+rng*c0
        ctx.append(t)
    bits=common_bits(lo,hi)
    print('\n',label,params,'common_len',len(bits),'bits',bits[:160])
    for off,bs in bytes_from_bits(bits):
        if b'grod' in bs or b'flag' in bs or off==0:
            print('off',off,bs[:80])

def ids(s): return llm.tokenize(s.encode(), add_bos=False, special=True)
contexts={
 'header':(toks[:9],toks[9:]),
 'bos':([llm.token_bos()],toks),
 'chat_empty':(ids('<|im_start|>system\nYou are Qwen, created by Alibaba Cloud. You are a helpful assistant.<|im_end|>\n<|im_start|>user\n<|im_end|>\n<|im_start|>assistant\n'),toks),
}
params_list=[]
for desc in [True,False]:
 for temp in [1.0,0.8]:
  for filt in [(0,1.0,0.0),(4096,1.0,0.0),(0,0.95,0.0),(0,1.0,0.05),(0,0.95,0.05)]:
   params_list.append(dict(temp=temp,top_k=filt[0],top_p=filt[1],min_p=filt[2],descending=desc))
for label,(pre,targ) in contexts.items():
 for par in params_list:
  run(label,pre,targ,par)
