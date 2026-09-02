from llama_cpp import Llama
import numpy as np
llm=Llama(model_path='models/qwen2.5-0.5b-instruct-q4_k_m.gguf', n_ctx=512, logits_all=True, verbose=False, n_threads=4)
prompt='A short recipe for a winter vegetable soup:\n'
params=dict(max_tokens=8, seed=0, echo=False, stop=[], temperature=1.0, top_k=0, top_p=1.0, min_p=0.0)
r=llm.create_completion(prompt, **params)
text=r['choices'][0]['text']
print(repr(text))
ptoks=llm.tokenize(prompt.encode(), add_bos=False, special=True)
gtoks=llm.tokenize(text.encode(), add_bos=False, special=True)
print('ptoks',ptoks)
print('gtoks',gtoks, [llm.detokenize([t]) for t in gtoks])
ctx=ptoks.copy()
positions=[]
for t in gtoks:
    llm.reset(); llm.eval(ctx)
    logits=np.array(llm._scores[len(ctx)-1], dtype=np.float32)
    order=np.argsort(-logits, kind='quicksort')
    pos=int(np.where(order==t)[0][0])
    positions.append(pos)
    ctx.append(t)
print('positions',positions)
