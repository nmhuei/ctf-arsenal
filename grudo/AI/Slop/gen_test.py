from llama_cpp import Llama
llm=Llama(model_path='models/qwen2.5-0.5b-instruct-q4_k_m.gguf', n_ctx=512, verbose=False, n_threads=4)
prompt='A short recipe for a winter vegetable soup:\n'
for params in [dict(temperature=1.0,top_k=0,top_p=1.0,min_p=0.0),dict(temperature=0.8,top_k=0,top_p=1.0,min_p=0.0),dict(temperature=1.0,top_k=-1,top_p=1.0,min_p=0.0),dict(temperature=1.0,top_k=4096,top_p=1.0,min_p=0.0)]:
 print('PARAM',params)
 for seed in [0,1,42,123,123456789]:
  r=llm.create_completion(prompt, max_tokens=8, seed=seed, echo=True, stop=[], **params)
  print(seed, repr(r['choices'][0]['text']))
