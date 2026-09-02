from llama_cpp import Llama
import numpy as np
llm=Llama(model_path='models/qwen2.5-0.5b-instruct-q4_k_m.gguf', n_ctx=128, logits_all=True, verbose=False, n_threads=4)
toks=llm.tokenize(b'A short', add_bos=False)
print(toks)
llm.eval(toks[:1])
print('n_tokens', llm.n_tokens)
print('scores type', type(llm._scores), getattr(llm._scores,'shape',None), llm._scores[:2,:5] if hasattr(llm._scores,'shape') else None)
print('last logits ctx len', len(llm._ctx.get_logits()))
print('first 5', llm._ctx.get_logits()[:5])
