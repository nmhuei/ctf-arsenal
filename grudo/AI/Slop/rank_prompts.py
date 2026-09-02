from llama_cpp import Llama
import numpy as np
llm=Llama(model_path='models/qwen2.5-0.5b-instruct-q4_k_m.gguf', n_ctx=2048, logits_all=True, verbose=False, n_threads=4)
msg=open('message.txt','rb').read(); toks=llm.tokenize(msg,add_bos=False,special=True)

def ids(s): return llm.tokenize(s.encode(),add_bos=False,special=True)
def chat(user,system='You are Qwen, created by Alibaba Cloud. You are a helpful assistant.'):
 return ids(f'<|im_start|>system\n{system}<|im_end|>\n<|im_start|>user\n{user}<|im_end|>\n<|im_start|>assistant\n')
def ranks(ctx,targets,n=12):
 out=[]; ctx=list(ctx)
 for t in targets[:n]:
  llm.reset(); llm.eval(ctx)
  logits=np.array(llm._scores[len(ctx)-1])
  out.append(int((logits>logits[t]).sum()+1))
  ctx.append(t)
 return out
prompts=[
'',
'I received a very strange message. It seems the sender has undergone AI-ization',
'I received a very strange message. It seems the sender has undergone AI-ization\n',
'Will be useful:\n\nModel: Qwen/Qwen2.5-0.5B-Instruct-GGUF\nRevision: 9217f5db79a29953eb74d5343926648285ec7e67\nFile: qwen2.5-0.5b-instruct-q4_k_m.gguf\nRuntime: llama-cpp-python==0.3.16\n\n',
'Flag format: grodno{}\n',
'AI-ization', 'Slop', 'Message:', 'The message is:', 'Decode the following message:', 'A short recipe for a winter vegetable soup:\n'
]
for p in prompts:
 for typ,ctx in [('raw',ids(p) if p else [llm.token_bos()]),('chat',chat(p))]:
  rs=ranks(ctx,toks,12)
  print(typ,repr(p),'ctxlen',len(ctx),'ranks',rs,'rank0',rs[0])
