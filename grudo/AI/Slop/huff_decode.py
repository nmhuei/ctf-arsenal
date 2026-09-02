from llama_cpp import Llama
import numpy as np, heapq, math, itertools
llm=Llama(model_path='models/qwen2.5-0.5b-instruct-q4_k_m.gguf', n_ctx=256, logits_all=True, verbose=False, n_threads=4)
out=llm.tokenize(open('message.txt','rb').read(), add_bos=False, special=True)

def target_code_from_logits(logits, target, topn=None, reverse=False):
    # use logits, optionally topn highest only
    if topn is not None:
        idx=np.argpartition(-logits, topn-1)[:topn]
    else:
        idx=np.arange(len(logits))
    # convert to positive weights; relative enough
    z=logits[idx].astype(np.float64)
    z-=z.max()
    weights=np.exp(z)
    # huffman: combine smallest weights; store bitstring for target by tree walk after full build
    target_pos=np.where(idx==target)[0]
    if len(target_pos)==0:
        return None
    heap=[]; counter=itertools.count()
    for token,w in zip(idx,weights):
        heapq.heappush(heap,(float(w), next(counter), int(token)))
    parent={}
    while len(heap)>1:
        w1,c1,n1=heapq.heappop(heap); w2,c2,n2=heapq.heappop(heap)
        new=('n', next(counter))
        if not reverse:
            parent[n1]=(new,'0'); parent[n2]=(new,'1')
        else:
            parent[n1]=(new,'1'); parent[n2]=(new,'0')
        heapq.heappush(heap,(w1+w2, next(counter), new))
    bits=[]; n=int(target)
    while n in parent:
        p,b=parent[n]; bits.append(b); n=p
    return ''.join(reversed(bits))

def bytes_from_bits(bits, offset=0):
    bs=[]
    for i in range(offset,len(bits)-7,8):
        bs.append(int(bits[i:i+8],2))
    return bytes(bs)

def run(ctx, label, topn=None, reverse=False):
    bits=''
    ctx=list(ctx)
    for t in out:
        llm.reset(); llm.eval(ctx)
        logits=np.array(llm._scores[len(ctx)-1])
        code=target_code_from_logits(logits,t,topn=topn,reverse=reverse)
        if code is None:
            return None
        bits+=code
        ctx.append(t)
    print('\n',label,'topn',topn,'rev',reverse,'bitslen',len(bits),'firstbits',bits[:128])
    for off in range(8):
        b=bytes_from_bits(bits,off)
        if b'grodno' in b or off==0:
            print('off',off,b[:80])
    return bits

contexts={'bos':[llm.token_bos()], 'chat_empty': llm.tokenize(b'<|im_start|>system\nYou are Qwen, created by Alibaba Cloud. You are a helpful assistant.<|im_end|>\n<|im_start|>user\n<|im_end|>\n<|im_start|>assistant\n', add_bos=False, special=True)}
for label,ctx in contexts.items():
    for topn in [None, 4096,2048,1024,512,256,128,64,32]:
        for rev in [False, True]:
            try: run(ctx,label,topn,rev)
            except Exception as e: print('ERR',label,topn,rev,e)
