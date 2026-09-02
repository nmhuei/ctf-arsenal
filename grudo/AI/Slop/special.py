from llama_cpp import Llama
import numpy as np
llm=Llama(model_path='models/qwen2.5-0.5b-instruct-q4_k_m.gguf', n_ctx=64, logits_all=True, verbose=False)
for attr in ['token_bos','token_eos','token_nl','n_vocab']:
    try:
        print(attr, getattr(llm,attr)())
    except Exception as e: print(attr,e)
for s in ['<|endoftext|>','<|im_start|>','<|im_end|>','<|vision_start|>']:
    toks=llm.tokenize(s.encode(), add_bos=False, special=True)
    print(s,toks,[llm.detokenize([t]) for t in toks])
# rank A after bos/eos/endoftext if any
for ctx in [[llm.token_bos()],[llm.token_eos()], llm.tokenize(b'<|endoftext|>', add_bos=False, special=True)]:
    llm.reset(); llm.eval(ctx)
    logits=np.array(llm._scores[len(ctx)-1])
    print('ctx',ctx,'rank A', int((logits>logits[32]).sum()+1), 'top', [(int(t),llm.detokenize([int(t)])) for t in np.argsort(-logits)[:5]])
