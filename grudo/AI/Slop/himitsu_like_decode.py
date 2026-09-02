from llama_cpp import Llama
import numpy as np, itertools, string
llm=Llama(model_path='models/qwen2.5-0.5b-instruct-q4_k_m.gguf', n_ctx=1024, logits_all=True, verbose=False, n_threads=4)
toks=llm.tokenize(open('message.txt','rb').read(), add_bos=False, special=True)

def token_bytes(t):
    return llm.detokenize([int(t)])

def decode_case(prefix, targets, temp=1.0, min_prob=1e-6, top_k=0, resolve=True, reverse=False):
    bits=''; ctx=list(prefix)
    infos=[]
    for t in targets:
        llm.reset(); llm.eval(ctx)
        logits=np.array(llm._scores[len(ctx)-1], dtype=np.float64)/temp
        order=np.argsort(-logits)
        if top_k and top_k>0: order=order[:top_k]
        z=logits[order]-logits[order[0]]; p=np.exp(z); p=p/p.sum()
        cand_len=max(int((p>=min_prob).sum()),1)
        cand_order=order[:cand_len]
        new=[]
        if resolve:
            toks_b=[token_bytes(x) for x in cand_order]
            for i,b in enumerate(toks_b):
                bad=False
                for j,c in enumerate(toks_b):
                    if i!=j and c.startswith(b): bad=True; break
                if not bad: new.append(i)
        else:
            new=list(range(cand_len))
        bit_count=len(new).bit_length()-1
        try:
            sorted_pos=int(np.where(cand_order==t)[0][0])
            enc_index=new.index(sorted_pos)
        except Exception:
            return None
        if bit_count==0:
            infos.append((t,sorted_pos,enc_index,bit_count,len(new)))
            ctx.append(t); continue
        if enc_index >= (1<<bit_count):
            return None
        b=format(enc_index, f'0{bit_count}b')
        if reverse: b=b[::-1]
        bits+=b
        infos.append((t,sorted_pos,enc_index,bit_count,len(new)))
        ctx.append(t)
    return bits,infos

def show_bits(label,bits,infos):
    print('\n',label,'bitslen',len(bits),'bits',bits[:160])
    for off in range(8):
        bs=bytes(int(bits[i:i+8],2) for i in range(off,len(bits)-7,8))
        # try also reversed bits per byte
        if b'grod' in bs or b'flag' in bs or off==0:
            print('off',off,bs[:80])
    # reverse entire bitstream
    rb=bits[::-1]
    for off in range(8):
        bs=bytes(int(rb[i:i+8],2) for i in range(off,len(rb)-7,8))
        if b'grod' in bs or b'flag' in bs:
            print('revoff',off,bs[:80])
    print('infos',infos)

def ids(s): return llm.tokenize(s.encode(), add_bos=False, special=True)
contexts={
 'header':(toks[:9],toks[9:]),
 'bos':([llm.token_bos()],toks),
 'chat_empty':(ids('<|im_start|>system\nYou are Qwen, created by Alibaba Cloud. You are a helpful assistant.<|im_end|>\n<|im_start|>user\n<|im_end|>\n<|im_start|>assistant\n'),toks),
 'empty_prev':(toks[:1],toks[1:]),
}
mins=[1e-2,5e-3,1e-3,5e-4,1e-4,5e-5,1e-5,5e-6,2e-6,1e-6,5e-7,1e-7,1e-8]
for cname,(pre,targ) in contexts.items():
  for temp in [1.0,0.8]:
    for resolve in [True,False]:
      for mp in mins:
        for rev in [False,True]:
          r=decode_case(pre,targ,temp=temp,min_prob=mp,resolve=resolve,reverse=rev)
          if not r: continue
          bits,infos=r
          # print all plausible lengths between 40 and 200, plus if grodno found
          found=False
          for off in range(8):
            if b'grod' in bytes(int(bits[i:i+8],2) for i in range(off,len(bits)-7,8)):
              found=True
          if found or (cname=='header' and 60<=len(bits)<=120 and mp in [1e-5,5e-6,2e-6,1e-6,1e-7] and not rev and temp==1.0):
            show_bits(f'{cname} temp={temp} resolve={resolve} minp={mp} revbits={rev}',bits,infos)
