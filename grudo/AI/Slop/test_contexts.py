from llama_cpp import Llama
import numpy as np, re
llm=Llama(model_path='models/qwen2.5-0.5b-instruct-q4_k_m.gguf', n_ctx=1024, logits_all=True, verbose=False, n_threads=4)
msg=open('message.txt','rb').read()
out=llm.tokenize(msg, add_bos=False, special=True)
print('out',out)

def ids(s): return llm.tokenize(s.encode(), add_bos=False, special=True)
def rank_after(ctx, token):
    llm.reset(); llm.eval(ctx)
    logits=np.array(llm._scores[len(ctx)-1], dtype=np.float32)
    return int((logits>logits[token]).sum()+1)

def ranks_for_ctx(ctx, n=8):
    ctx=list(ctx); rs=[]
    for t in out[:n]:
        rs.append(rank_after(ctx,t)); ctx.append(t)
    return rs

def qwen_chat(user, system='You are Qwen, created by Alibaba Cloud. You are a helpful assistant.'):
    s=f"<|im_start|>system\n{system}<|im_end|>\n<|im_start|>user\n{user}<|im_end|>\n<|im_start|>assistant\n"
    return ids(s)

def qwen_user(user):
    s=f"<|im_start|>user\n{user}<|im_end|>\n<|im_start|>assistant\n"
    return ids(s)

prompts=[
'',
'Write a short recipe for a winter vegetable soup.',
'Write a short recipe for a winter vegetable soup:',
'A short recipe for a winter vegetable soup:',
'Generate a short recipe for a winter vegetable soup.',
'Tell me a short recipe for a winter vegetable soup.',
'Give me a short recipe for a winter vegetable soup.',
'Write me a short recipe for a winter vegetable soup.',
'Can you write a short recipe for a winter vegetable soup?',
]
for p in prompts:
    for name,ctx in [('raw', ids(p)),('chat', qwen_chat(p) if p else qwen_chat('')),('userchat', qwen_user(p) if p else qwen_user(''))]:
        if len(ctx)==0: continue
        rs=ranks_for_ctx(ctx,8)
        print(name,repr(p),'ctxlen',len(ctx),'ranks',rs,'chars',''.join(chr(r-1) if 32<=r-1<127 else '?' for r in rs),'/', ''.join(chr(r) if 32<=r<127 else '?' for r in rs))
