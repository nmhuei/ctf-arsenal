from llama_cpp import Llama
import numpy as np
llm=Llama(model_path='models/qwen2.5-0.5b-instruct-q4_k_m.gguf', n_ctx=1024, logits_all=True, verbose=False, n_threads=4)
toks=llm.tokenize(open('message.txt','rb').read(), add_bos=False, special=True)

def dec(prefix,targets,temp,minp,top_k=0,rev=False):
    bits=''; infos=[]; ctx=list(prefix)
    for t in targets:
        llm.reset(); llm.eval(ctx)
        logits=np.array(llm._scores[len(ctx)-1], dtype=np.float64)/temp
        order=np.argsort(-logits)
        if top_k and top_k>0: order=order[:top_k]
        z=logits[order]-logits[order[0]]; p=np.exp(z); p=p/p.sum()
        count=max(int((p>=minp).sum()),1)
        cand=order[:count]
        pos=np.where(cand==t)[0]
        if len(pos)==0: return None
        pos=int(pos[0]); bit_count=count.bit_length()-1
        if bit_count>0:
            if pos >= (1<<bit_count): return None
            b=format(pos, f'0{bit_count}b')
            bits += b[::-1] if rev else b
        infos.append((int(t),pos,bit_count,count))
        ctx.append(int(t))
    return bits, infos

def show(label,bits,infos):
    print('\n'+label, 'len',len(bits),'bits',bits)
    for source,name in [(bits,'bits'),(bits[::-1],'revall')]:
      for off in range(8):
        if len(source)-off>=8:
          bs=bytes(int(source[i:i+8],2) for i in range(off,len(source)-7,8))
          if b'grod' in bs or b'flag' in bs or off==0:
            print(name,'off',off,bs)
          # bit reverse within bytes
          bs2=bytes(int(source[i:i+8][::-1],2) for i in range(off,len(source)-7,8))
          if b'grod' in bs2 or b'flag' in bs2:
            print(name,'byterev off',off,bs2)
    print('infos',infos)

ctxs={'header':(toks[:9],toks[9:]), 'bos':([llm.token_bos()],toks), 'prev':(toks[:1],toks[1:])}
mins=[10**(-k/2) for k in range(2,18)] + [2e-6,1.5e-6,8e-7,5e-7,1e-7,1e-8]
for cname,(pre,targ) in ctxs.items():
 for temp in [1.0,0.8]:
  for minp in mins:
   for top_k in [0,4096,2048,1024,512,256,128,64,32]:
    for rev in [False,True]:
     r=dec(pre,targ,temp,minp,top_k,rev)
     if not r: continue
     bits,infos=r
     found=False
     for off in range(8):
      if len(bits)-off>=8:
       bs=bytes(int(bits[i:i+8],2) for i in range(off,len(bits)-7,8))
       if b'grod' in bs or b'flag' in bs: found=True
     if found or (cname=='header' and temp==1.0 and top_k in [0,4096,2048] and 40<=len(bits)<=160 and not rev):
      show(f'{cname} temp={temp} minp={minp:g} topk={top_k} rev={rev}',bits,infos)
