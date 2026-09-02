from llama_cpp import Llama
import numpy as np, math
llm=Llama(model_path='models/qwen2.5-0.5b-instruct-q4_k_m.gguf', n_ctx=1024, logits_all=True, verbose=False, n_threads=4)
toks=llm.tokenize(open('message.txt','rb').read(), add_bos=False, special=True)
header=toks[:9]; cont=toks[9:]
print('tokens', toks)
ctx=header.copy()
for mode in ['full','prev']:
    print('\nMODE',mode)
    if mode=='full': ctx=header.copy()
    else: ctx=header.copy()
    ranks=[]
    for i,t in enumerate(cont):
        llm.reset(); llm.eval(ctx)
        logits=np.array(llm._scores[len(ctx)-1], dtype=np.float64)
        z=logits-logits.max(); p=np.exp(z); p/=p.sum()
        rank=int((logits>logits[t]).sum()+1)
        ranks.append(rank-1)
        print(i,t,llm.detokenize([t]),'rank0',rank-1,'rank1',rank,'p',p[t],'-log2',-math.log2(p[t]))
        if mode=='full': ctx.append(t)
        else: ctx=[t]
    print('rank0seq',ranks)
