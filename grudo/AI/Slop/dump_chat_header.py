from llama_cpp import Llama
import numpy as np, struct
MODEL='models/qwen2.5-0.5b-instruct-q4_k_m.gguf'
llm=Llama(model_path=MODEL,n_ctx=1024,logits_all=True,verbose=False,n_threads=4)
msg=open('message.txt','rb').read(); toks=llm.tokenize(msg,add_bos=False,special=True)
header=toks[:9]; cont=toks[9:]
header_text=llm.detokenize(header).decode('utf-8')
def ids(s): return llm.tokenize(s.encode(),add_bos=False,special=True)
def chat(user,system='You are Qwen, created by Alibaba Cloud. You are a helpful assistant.'):
 return ids(f'<|im_start|>system\n{system}<|im_end|>\n<|im_start|>user\n{user}<|im_end|>\n<|im_start|>assistant\n')
cases=[('chat_header_temp1',chat(header_text),cont,1.0),('chat_header_temp08',chat(header_text),cont,0.8)]
for name,prefix,targets,temp in cases:
 ctx=list(prefix); print(name,'prefix len',len(ctx),'target',targets,'header',repr(header_text))
 with open(name+'.bin','wb') as f:
  f.write(b'LGTS'); f.write(struct.pack('<IIfffI',len(targets),llm.n_vocab(),float(temp),0.0,1.0,0))
  ranks=[]
  for t in targets:
   llm.reset(); llm.eval(ctx); logits=np.asarray(llm._scores[len(ctx)-1],dtype=np.float32)
   ranks.append(int((logits>logits[t]).sum()))
   f.write(struct.pack('<i',int(t))); f.write(logits.tobytes())
   ctx.append(t)
  print('ranks',ranks)
