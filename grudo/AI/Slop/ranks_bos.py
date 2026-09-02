from llama_cpp import Llama
import numpy as np
llm=Llama(model_path='models/qwen2.5-0.5b-instruct-q4_k_m.gguf', n_ctx=256, logits_all=True, verbose=False, n_threads=4)
out=llm.tokenize(open('message.txt','rb').read(), add_bos=False, special=True)
ctx=[llm.token_bos()]
rs=[]
for t in out:
    llm.reset(); llm.eval(ctx)
    logits=np.array(llm._scores[len(ctx)-1])
    r=int((logits>logits[t]).sum()+1)
    rs.append(r)
    ctx.append(t)
print(rs)
print('chars1',''.join(chr(r) if 32<=r<127 else '?' for r in rs))
print('chars0',''.join(chr(r-1) if 32<=r-1<127 else '?' for r in rs))
