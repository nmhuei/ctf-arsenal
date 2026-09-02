from llama_cpp import Llama
import struct, numpy as np, math
llm=Llama(model_path='models/qwen2.5-0.5b-instruct-q4_k_m.gguf', n_ctx=512, logits_all=True, verbose=False, n_threads=4)
msg=open('message.txt','rb').read(); toks=llm.tokenize(msg, add_bos=False, special=True)
header=toks[:9]; cont=toks[9:]
print('bos',llm.token_bos())
for name,prefix,targets,temp in [
 ('bos_header_temp1',[llm.token_bos()]+header,cont,1.0),
 ('bos_header_temp08',[llm.token_bos()]+header,cont,0.8),
 ('eos_header_temp1',[llm.token_eos()]+header,cont,1.0),
 ('eos_header_temp08',[llm.token_eos()]+header,cont,0.8),
]:
 ctx=list(prefix); ranks=[]
 with open(name+'.bin','wb') as f:
  f.write(b'LGTS'); f.write(struct.pack('<IIfffI',len(targets),llm.n_vocab(),temp,1.0,0.0,0))
  for t in targets:
   llm.reset(); llm.eval(ctx)
   logits=np.asarray(llm._scores[len(ctx)-1], dtype=np.float32)
   rank=int((logits>logits[t]).sum()+1); ranks.append(rank-1)
   f.write(struct.pack('<i',int(t))); f.write(logits.tobytes())
   ctx.append(t)
 print(name,'ranks0',ranks)
