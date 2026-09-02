from llama_cpp import Llama
import numpy as np
llm=Llama(model_path='models/qwen2.5-0.5b-instruct-q4_k_m.gguf', n_ctx=128, logits_all=True, verbose=False, n_threads=4)
bos=llm.token_bos()
llm.reset(); llm.eval([bos])
log1=np.array(llm._scores[llm.n_tokens-1]).copy()
order=np.argsort(-log1); tok=int(order[0])
llm.eval([tok])
log2_cache=np.array(llm._scores[llm.n_tokens-1]).copy()
llm.reset(); llm.eval([bos,tok])
log2_full=np.array(llm._scores[llm.n_tokens-1]).copy()
print('n_tokens',llm.n_tokens,'tok',tok,'same maxerr',np.max(np.abs(log2_cache-log2_full)), 'top2', np.argsort(-log2_cache)[:5], np.argsort(-log2_full)[:5])
