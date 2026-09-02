from llama_cpp import Llama
import numpy as np, zlib, gzip, bz2, lzma, base64, sys
llm=Llama(model_path='models/qwen2.5-0.5b-instruct-q4_k_m.gguf', n_ctx=1024, logits_all=True, verbose=False, n_threads=4)
full=llm.tokenize(open('message.txt','rb').read(), add_bos=False, special=True)
header=full[:9]; cont=full[9:]
V=llm.n_vocab()

def int2bits(x,n): return [int(c) for c in reversed(f'{x:0{n}b}')]
def tokb(t): return llm.detokenize([int(t)])
def tok_suffix(b): return llm.tokenize(b, add_bos=False, special=True)
def score(b): return sum(32<=x<127 or x in (9,10,13) for x in b)/max(1,len(b))
def variants(bits):
    s=''.join(map(str,bits))
    for sname,src in [('bits',s),('revall',s[::-1])]:
      for off in range(8):
        if len(src)-off>=8:
          bs=bytes(int(src[i:i+8],2) for i in range(off,len(src)-7,8)); yield sname,off,'normal',bs
          bs2=bytes(int(src[i:i+8][::-1],2) for i in range(off,len(src)-7,8)); yield sname,off,'byterev',bs2

def show(label,bits,log,force=False):
    found=[]; good=[]
    for v in variants(bits):
        outs=[v[3]]
        for fn in [zlib.decompress,gzip.decompress,bz2.decompress,lzma.decompress]:
            try: outs.append(fn(v[3]))
            except Exception: pass
        try: outs.append(base64.b64decode(v[3],validate=False))
        except Exception: pass
        for out in outs:
            if b'grodno{' in out or b'grod' in out or b'flag' in out.lower(): found.append(v[:3]+(out,))
        if len(v[3])>=5 and score(v[3])>.85: good.append(v)
    if found or good or force:
        print('\n'+label,'len',len(bits),''.join(map(str,bits)))
        for x in found or good[:8] or list(variants(bits))[:2]: print(x[:3],x[3])
        print('log')
        for row in log: print(' ',row)
        return bool(found)
    return False

def build_bins(bs,seed):
    num=1<<bs; words_per=V/num
    vocab=np.arange(V,dtype=np.int32)
    np.random.seed(seed); np.random.shuffle(vocab)
    b2=[]; w2=np.empty(V,dtype=np.int32)
    for b in range(num):
        arr=vocab[int(b*words_per):int((b+1)*words_per)]
        b2.append(arr); w2[arr]=b
    return b2,w2

def top_by_bins(logits,b2):
    tops=[]
    for arr in b2:
        sub=logits[arr]
        tops.append(int(arr[int(np.argmax(sub))]))
    return tops

def rank_in_bin(logits, arr, t):
    val=logits[t]
    return int((logits[arr] > val).sum())

def decode(prefix, inp0, bs, seed, max_steps=100):
    b2,w2=build_bins(bs,seed)
    inp=list(inp0)
    prev=list(prefix)
    bits=[]; log=[]; i=0
    while i < len(inp) and i<max_steps:
        t=int(inp[i]); bin_num=int(w2[t])
        llm.reset(); llm.eval(prev)
        logits=np.array(llm._scores[len(prev)-1], dtype=np.float32)
        arr=b2[bin_num]
        rank=rank_in_bin(logits,arr,t)
        corrected=False; corr_token=t; note=''
        if rank>0:
            true=tokb(t)
            tops=top_by_bins(logits,b2)
            for bnum,top in enumerate(tops):
                prop=tokb(top)
                if len(prop)<len(true) and true.startswith(prop):
                    suffix=true[len(prop):]
                    inp[i]=top
                    suff=tok_suffix(suffix)
                    inp[i+1:i+1]=suff
                    bin_num=bnum; corr_token=top; corrected=True; note=f'short prefix {prop!r}+{suffix!r}->{suff}'
                    break
                elif len(prop)>len(true) and prop.startswith(true):
                    whole=true; num_extra=1
                    while len(whole)<len(prop) and i+num_extra<len(inp):
                        whole += tokb(inp[i+num_extra]); num_extra += 1
                    if prop == whole[:len(prop)]:
                        inp[i]=top
                        # delete consumed originals after current
                        for _ in range(1,num_extra):
                            if i+1 < len(inp): del inp[i+1]
                        if len(whole)>len(prop):
                            suffix=whole[len(prop):]
                            suff=tok_suffix(suffix)
                            inp[i+1:i+1]=suff
                        bin_num=bnum; corr_token=top; corrected=True; note=f'long merge {true!r}... -> {prop!r}'
                        break
        bits += int2bits(bin_num, bs)
        log.append((i,t,tokb(t),bin_num,rank,'corr' if corrected else '',corr_token,tokb(corr_token),note,'inp_len',len(inp)))
        prev=[int(corr_token)]
        i+=1
    return bits,log

contexts=[('header',header,cont),('bos',[llm.token_bos()],full)]
for cname,pre,inp in contexts:
  for bs in range(1,14):
    for seed in sorted(set([bs,0,1,42,123,1234,1337,2024,2025,9217,16,32,64,128,256,512,1024])):
        bits,log=decode(pre,inp,bs,seed)
        force=(cname=='header' and seed==bs and bs in [4,5,6,7,8])
        if show(f'{cname} bs={bs} seed={seed}',bits,log,force):
            sys.exit(0)
print('done')
