from llama_cpp import Llama
import numpy as np
llm=Llama(model_path='models/qwen2.5-0.5b-instruct-q4_k_m.gguf', n_ctx=512, logits_all=True, verbose=False, n_threads=4)
out=llm.tokenize(open('message.txt','rb').read(), add_bos=False, special=True)

def probs_idx(logits,temp=1.0,top_k=None,top_p=None,min_p=0.0):
    z=logits.astype(np.float64)/temp
    idx=np.arange(len(z))
    if top_k and top_k>0 and top_k<len(z): idx=np.argpartition(-z,top_k-1)[:top_k]
    order=np.argsort(-z[idx]); idx=idx[order]; z=z[idx]
    z-=z.max(); p=np.exp(z); p/=p.sum()
    if top_p and top_p<1:
        cs=np.cumsum(p); j=np.searchsorted(cs,top_p,'left'); keep=np.arange(len(p))<=j
        idx=idx[keep]; p=p[keep]; p/=p.sum()
    if min_p and min_p>0:
        keep=p>=p.max()*min_p; idx=idx[keep]; p=p[keep]; p/=p.sum()
    return idx,p

def code_adg(idx,p,target,rev=False):
    bits=[]
    idx=idx.copy(); p=p.copy()
    while len(idx)>1:
        cs=np.cumsum(p)
        split=int(np.searchsorted(cs,0.5,'left'))+1
        if split<=0: split=1
        if split>=len(idx): split=len(idx)-1
        # choose split minimizing |mass-.5|
        candidates=[split]
        if split>1: candidates.append(split-1)
        best=min(candidates, key=lambda s: abs(p[:s].sum()-0.5))
        split=best
        left_idx,left_p=idx[:split],p[:split]
        right_idx,right_p=idx[split:],p[split:]
        if target in set(left_idx.tolist()):
            bits.append('1' if rev else '0'); idx=left_idx; p=left_p/left_p.sum()
        else:
            bits.append('0' if rev else '1'); idx=right_idx; p=right_p/right_p.sum()
    return ''.join(bits)

def bfrom(bits,off): return bytes(int(bits[i:i+8],2) for i in range(off,len(bits)-7,8))

def run(label,ctx,params,rev):
    bits=''; ctx=list(ctx)
    for i,t in enumerate(out):
        llm.reset(); llm.eval(ctx)
        idx,p=probs_idx(np.array(llm._scores[len(ctx)-1]),**params)
        if t not in set(idx.tolist()): return
        bits+=code_adg(idx,p,t,rev=rev)
        ctx.append(t)
    print('\n',label,params,'rev',rev,'len',len(bits),'bits',bits[:128])
    for off in range(8):
        b=bfrom(bits,off)
        if b'grodno' in b or off==0:
            print(off,b[:80])

def ids(s): return llm.tokenize(s.encode(), add_bos=False, special=True)
contexts={'bos':[llm.token_bos()], 'chat_empty': ids('<|im_start|>system\nYou are Qwen, created by Alibaba Cloud. You are a helpful assistant.<|im_end|>\n<|im_start|>user\n<|im_end|>\n<|im_start|>assistant\n'), 'prompt_header': ids('A short recipe for a winter vegetable soup:\n')}
for label,ctx in contexts.items():
 for params in [{'temp':1.0,'top_k':None,'top_p':None,'min_p':0.0},{'temp':0.8,'top_k':None,'top_p':None,'min_p':0.0},{'temp':1.0,'top_k':4096,'top_p':1.0,'min_p':0.0},{'temp':0.8,'top_k':4096,'top_p':1.0,'min_p':0.0}]:
  for rev in [False,True]: run(label,ctx,params,rev)
