from llama_cpp import Llama
llm=Llama(model_path='models/qwen2.5-0.5b-instruct-q4_k_m.gguf', n_ctx=1024, logits_all=False, verbose=False, n_threads=4)
msg=open('message.txt','rb').read(); toks=llm.tokenize(msg,add_bos=False,special=True)
header=toks[:9]; cont=toks[9:]
contexts={'header':(header,cont),'bos':([llm.token_bos()],toks)}
paramsets={
'default':{},
'def_topp1':{'top_p':1.0,'top_k':40,'min_p':0.05,'temperature':0.8},
't1_top0':{'temperature':1.0,'top_k':0,'top_p':1.0,'min_p':0.0},
't08_top0':{'temperature':0.8,'top_k':0,'top_p':1.0,'min_p':0.0},
't1_top4096':{'temperature':1.0,'top_k':4096,'top_p':1.0,'min_p':0.0},
't08_top4096':{'temperature':0.8,'top_k':4096,'top_p':1.0,'min_p':0.0},
}
# make prompt from tokens as bytes
def det(ts): return llm.detokenize([int(x) for x in ts])
for cname,(pre,targets) in contexts.items():
  for pname,params in paramsets.items():
    ctx=list(pre); outchars=[]; ok=True; allc=[]
    for step,t in enumerate(targets):
      prompt=det(ctx).decode('utf-8', errors='ignore')
      cand=[]
      for seed in range(256):
        r=llm.create_completion(prompt, max_tokens=1, seed=seed, echo=False, stop=[], **params)
        gen=r['choices'][0]['text'].encode('utf-8',errors='surrogatepass')
        gt=llm.tokenize(gen,add_bos=False,special=True)
        # create_completion text may include bytes weird; compare tokenized first token, or raw detokenize target
        if gt and gt[0]==t:
          cand.append(seed)
      allc.append(cand)
      if len(cand)==1: outchars.append(chr(cand[0]) if 32<=cand[0]<127 else f'\\x{cand[0]:02x}')
      else: outchars.append('['+','.join(str(c) for c in cand[:20])+('...' if len(cand)>20 else '')+']')
      ctx.append(t)
    print('\n',cname,pname)
    print('counts',[len(c) for c in allc])
    print('cands',allc)
    print('str',''.join(outchars))
