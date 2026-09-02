from llama_cpp import Llama
import numpy as np
llm=Llama(model_path='models/qwen2.5-0.5b-instruct-q4_k_m.gguf', n_ctx=8192, logits_all=True, verbose=False, n_threads=6)
bits=[int(c) for c in '101000011001011010100010010100101101110011001100110111001011100111001000101111010010000010100111100000000000']

def int2bits(x,n): return [int(c) for c in reversed(f'{int(x):0{n}b}')]
def bits2int(bits): return sum(int(b)*(1<<i) for i,b in enumerate(bits))
def same(a,b):
    for i,(x,y) in enumerate(zip(a,b)):
        if x!=y: return i
    return len(a)

def decode(ctx,prec=64,topk=60000,temp=1.0,max_steps=300):
    cur=[0,1<<prec]; i=0; out=[]; ctx=list(ctx)
    for st in range(max_steps):
        llm.reset(); llm.eval(ctx)
        logits=np.array(llm._scores[len(ctx)-1],dtype=np.float64)
        order=np.argsort(-logits)
        z=logits[order]/temp; z-=z[0]; p=np.exp(z); p/=p.sum(); rng=cur[1]-cur[0]
        tmp=np.nonzero(p < 1/rng)[0]
        k=topk if len(tmp)==0 else min(max(2,int(tmp[0])),topk); k=min(k,len(p))
        vals=p[:k]/p[:k].sum()*rng; ints=np.rint(vals).astype(object); cum=np.cumsum(ints,dtype=object)
        over=[j for j,x in enumerate(cum) if x>rng]
        if over: cum=cum[:over[0]]; k=over[0]
        cum[-1]+=rng-cum[-1]; cum=[int(x)+cur[0] for x in cum]
        mbits=bits[i:i+prec]
        if len(mbits)<prec: mbits=mbits+[0]*(prec-len(mbits))
        midx=bits2int(reversed(mbits))
        sel=0
        while sel<len(cum) and cum[sel]<=midx: sel+=1
        token=int(order[sel]); out.append(token)
        bot=cum[sel-1] if sel else cur[0]; top=cum[sel]
        bb=list(reversed(int2bits(bot,prec))); tb=list(reversed(int2bits(top-1,prec))); n=same(bb,tb); i+=n
        cur=[bits2int(reversed(bb[n:]+[0]*n)), bits2int(reversed(tb[n:]+[1]*n))+1]
        ctx.append(token)
        if st%20==0 or n>0:
            text=llm.detokenize(out).decode('utf-8','replace')
            print('step',st,'i',i,'n',n,'tok',token,'sel',sel,'tail',repr(text[-250:]),flush=True)
            if 'grodno{' in text.lower() or 'flag{' in text.lower():
                print('FOUND',text); return
    text=llm.detokenize(out).decode('utf-8','replace')
    print('\nFINAL TEXT:\n'+text)

decode([llm.token_bos()])
