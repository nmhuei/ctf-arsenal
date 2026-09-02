from llama_cpp import Llama
import numpy as np, math
model='models/qwen2.5-0.5b-instruct-q4_k_m.gguf'
msg=open('message.txt','rb').read()
print('msg bytes',msg)
llm=Llama(model_path=model, n_ctx=256, logits_all=True, verbose=False, n_threads=4)
# tokenization variants
for add_bos in [True, False]:
    toks=llm.tokenize(msg, add_bos=add_bos, special=True)
    print('\nadd_bos',add_bos,'ntok',len(toks),toks)
    for i,t in enumerate(toks):
        print(i,t,repr(llm.detokenize([t])))
