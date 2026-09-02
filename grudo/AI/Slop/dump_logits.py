from llama_cpp import Llama
import struct
import numpy as np

MODEL='models/qwen2.5-0.5b-instruct-q4_k_m.gguf'
MSG=open('message.txt','rb').read()
llm=Llama(model_path=MODEL, n_ctx=1024, logits_all=True, verbose=False, n_threads=4)
toks=llm.tokenize(MSG, add_bos=False, special=True)
print('tokens', toks)

# cases: known prefix header and generated continuation; BOS generating whole message; empty chat generating whole message
cases=[]
header=toks[:9]
cases.append(('header_full_temp1', header, toks[9:], 1.0, 0, 1.0, 0.0))
cases.append(('header_full_temp08', header, toks[9:], 0.8, 0, 1.0, 0.0))
cases.append(('bos_full_temp1', [llm.token_bos()], toks, 1.0, 0, 1.0, 0.0))
cases.append(('bos_full_temp08', [llm.token_bos()], toks, 0.8, 0, 1.0, 0.0))
chat_empty=llm.tokenize(b'<|im_start|>system\nYou are Qwen, created by Alibaba Cloud. You are a helpful assistant.<|im_end|>\n<|im_start|>user\n<|im_end|>\n<|im_start|>assistant\n', add_bos=False, special=True)
cases.append(('chat_empty_full_temp1', chat_empty, toks, 1.0, 0, 1.0, 0.0))
cases.append(('chat_empty_full_temp08', chat_empty, toks, 0.8, 0, 1.0, 0.0))

for name,prefix,targets,temp,top_k,top_p,min_p in cases:
    path=f'{name}.bin'
    ctx=list(prefix)
    with open(path,'wb') as f:
        f.write(b'LGTS')
        f.write(struct.pack('<IIfffI', len(targets), llm.n_vocab(), float(temp), float(top_p), float(min_p), int(top_k)))
        for i,t in enumerate(targets):
            llm.reset(); llm.eval(ctx)
            logits=np.asarray(llm._scores[len(ctx)-1], dtype=np.float32)
            assert logits.shape[0]==llm.n_vocab()
            f.write(struct.pack('<i', int(t)))
            f.write(logits.tobytes(order='C'))
            ctx.append(t)
    print('wrote', path, 'steps', len(targets), 'prefixlen', len(prefix), 'targets', targets)
