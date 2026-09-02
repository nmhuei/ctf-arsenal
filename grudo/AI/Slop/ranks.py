from llama_cpp import Llama
import numpy as np, math
model='models/qwen2.5-0.5b-instruct-q4_k_m.gguf'
msg=open('message.txt','rb').read()
llm=Llama(model_path=model, n_ctx=256, logits_all=True, verbose=False, n_threads=4)
toks=llm.tokenize(msg, add_bos=False, special=True)
print('toks', toks)
for i in range(1,len(toks)):
    llm.reset()
    llm.eval(toks[:i])
    logits=np.array(llm._scores[i-1], dtype=np.float64)
    target=toks[i]
    rank=int((logits>logits[target]).sum()+1)
    top=np.argsort(-logits)[:12]
    print('\nstep',i,'prefix',repr(llm.detokenize(toks[:i])),'target',target,repr(llm.detokenize([target])),'rank',rank,'logit',float(logits[target]))
    print('top:',[(int(t),repr(llm.detokenize([int(t)])),float(logits[int(t)])) for t in top])
