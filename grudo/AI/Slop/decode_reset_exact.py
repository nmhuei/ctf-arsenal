from llama_cpp import Llama
import numpy as np, struct, re
llm=Llama(model_path='models/qwen2.5-0.5b-instruct-q4_k_m.gguf', n_ctx=4096, logits_all=True, verbose=False, n_threads=6)
bits=[int(c) for c in '101000011001011010100010010100101101110011001100110111001011100111001000101111010010000010100111100000000000']

def int2bits(x,n): return [int(c) for c in reversed(f'{int(x):0{n}b}')]
def bits2int(bits): return sum(int(b)*(1<<i) for i,b in enumerate(bits))
def same(a,b):
    for i,(x,y) in enumerate(zip(a,b)):
        if x!=y: return i
    return len(a)

def step_select(logits,cur,i,prec=64,topk=60000,temp=1.0,mask=None):
    logits=logits.copy()
    if mask:
      for t in mask:
        if 0<=t<len(logits): logits[t]=-1e20
    order=np.argsort(-logits)
    z=logits[order].astype(np.float64)/temp; z-=z[0]
    p=np.exp(z); p/=p.sum(); rng=cur[1]-cur[0]
    tmp=np.nonzero(p < 1/rng)[0]
    k=topk if len(tmp)==0 else min(max(2,int(tmp[0])),topk)
    k=min(k,len(p))
    vals=p[:k]/p[:k].sum()*rng
    ints=np.rint(vals).astype(object)
    cum=np.cumsum(ints,dtype=object)
    over=[j for j,x in enumerate(cum) if x>rng]
    if over: cum=cum[:over[0]]; k=over[0]
    if not len(cum): raise Exception('empty cum')
    cum[-1]+=rng-cum[-1]
    cum=[int(x)+cur[0] for x in cum]
    mbits=bits[i:i+prec]
    if len(mbits)<prec: mbits=mbits+[0]*(prec-len(mbits))
    midx=bits2int(reversed(mbits))
    sel=0
    while sel<len(cum) and cum[sel]<=midx: sel+=1
    if sel>=len(cum): raise Exception('sel oob')
    token=int(order[sel])
    bot=cum[sel-1] if sel>0 else cur[0]; top=cum[sel]
    bb=list(reversed(int2bits(bot,prec))); tb=list(reversed(int2bits(top-1,prec)))
    n=same(bb,tb)
    cur2=[bits2int(reversed(bb[n:]+[0]*n)), bits2int(reversed(tb[n:]+[1]*n))+1]
    return token,sel,n,cur2,k

def decode(ctx,prec=64,topk=60000,temp=1.0,max_steps=300,mask=None):
    ctx=list(ctx); cur=[0,1<<prec]; i=0; out=[]
    for st in range(max_steps):
        llm.reset(); llm.eval(ctx)
        logits=np.array(llm._scores[len(ctx)-1],dtype=np.float64)
        tok,sel,n,cur,k=step_select(logits,cur,i,prec,topk,temp,mask)
        i+=n; ctx.append(tok); out.append(tok)
        text=llm.detokenize(out).decode('utf-8','replace')
        print('step',st,'consumed',i,'tok',tok,'sel',sel,'k',k,'n',n,'tail',repr(text[-160:]),flush=True)
        if 'grodno{' in text and '}' in text[text.find('grodno{'):]:
            print('FLAGTEXT',text); return text,out,i
        if i>=len(bits):
            print('BITS EXHAUSTED')
            return text,out,i
    return llm.detokenize(out).decode('utf-8','replace'),out,i

for name,ctx in {'bos':[llm.token_bos()], 'eos':[llm.token_eos()]}.items():
  print('\n===',name,ctx,'===')
  text,out,i=decode(ctx,64,60000,1.0,200)
  print('FINAL',name,'consumed',i,'tokens',out)
  print(text)
