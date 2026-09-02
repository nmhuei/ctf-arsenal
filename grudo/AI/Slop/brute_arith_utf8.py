import numpy as np, struct, itertools, re, zlib, gzip, bz2, lzma, base64, binascii

def load(fn):
    f=open(fn,'rb'); assert f.read(4)==b'LGTS'
    n,nv,temp,tp,mp,tk=struct.unpack('<IIfffI',f.read(24)); steps=[]
    for _ in range(n):
        target=struct.unpack('<i',f.read(4))[0]
        logits=np.frombuffer(f.read(4*nv),dtype=np.float32).copy(); steps.append((target,logits))
    return steps

def int2bits(x,n): return [int(c) for c in reversed(f'{int(x):0{n}b}')]
def bits2int(bits): return sum(int(b)*(1<<i) for i,b in enumerate(bits))
def same(a,b):
    for i,(x,y) in enumerate(zip(a,b)):
        if x!=y: return i
    return len(a)

def dec(steps,prec,topk,temp=1.0,rounder='rint',final='bottom',rev_order=False):
    cur=[0,1<<prec]; out=[]; infos=[]
    iterable=list(steps)[::-1] if rev_order else list(steps)
    for si,(target,logits) in enumerate(iterable):
        order=np.argsort(-logits)
        rank=int(np.where(order==target)[0][0])
        z=logits[order].astype(np.float64)/temp; z-=z[0]
        p=np.exp(z); p/=p.sum(); rng=cur[1]-cur[0]
        tmp=np.nonzero(p < 1/rng)[0]
        k=topk if len(tmp)==0 else min(max(2,int(tmp[0])),topk)
        k=min(k,len(p))
        if rank>=k: return None
        vals=p[:k]/p[:k].sum()*rng
        if rounder=='rint': ints=np.rint(vals).astype(object)
        elif rounder=='floor': ints=np.floor(vals).astype(object)
        elif rounder=='ceil': ints=np.ceil(vals).astype(object)
        else: raise ValueError
        cum=np.cumsum(ints,dtype=object)
        over=[i for i,x in enumerate(cum) if x>rng]
        if over: cum=cum[:over[0]]; k=over[0]
        if not len(cum) or rank>=len(cum): return None
        cum[-1]+=rng-cum[-1]
        cum=[int(x)+cur[0] for x in cum]
        bot=cum[rank-1] if rank>0 else cur[0]; top=cum[rank]
        if top<=bot: return None
        bb=list(reversed(int2bits(bot,prec))); tb=list(reversed(int2bits(top-1,prec)))
        n=same(bb,tb)
        if si==len(iterable)-1:
            if final=='bottom': nb=bb
            elif final=='top': nb=tb
            elif final=='common': nb=tb[:n]
            elif final=='none': nb=[]
            else: raise ValueError
        else:
            nb=tb[:n]
        out += nb
        cur=[bits2int(reversed(bb[n:]+[0]*n)), bits2int(reversed(tb[n:]+[1]*n))+1]
        infos.append((rank,k,n,''.join(map(str,nb))))
    return out,infos

def bit_variants(bits):
    seqs=[]
    for revall,b in [('fwd',bits),('revall',bits[::-1])]:
      for shift in range(8):
        sub=b[shift:]
        by=[]
        for i in range(0,len(sub)//8*8,8):
          x=0
          for bit in sub[i:i+8]: x=(x<<1)|bit
          by.append(x)
        if by: seqs.append((revall,shift,'msb',bytes(by)))
        by=[]
        for i in range(0,len(sub)//8*8,8):
          x=0
          for j,bit in enumerate(sub[i:i+8]): x|=bit<<j
          by.append(x)
        if by: seqs.append((revall,shift,'lsb',bytes(by)))
    return seqs

def transforms(data):
    outs=[('raw',data)]
    for name,fn in [('zlib',zlib.decompress),('gzip',gzip.decompress),('bz2',bz2.decompress),('lzma',lzma.decompress)]:
        try: outs.append((name,fn(data)))
        except Exception: pass
    try: outs.append(('b64',base64.b64decode(data,validate=False)))
    except Exception: pass
    try: outs.append(('hex',binascii.unhexlify(data.strip())))
    except Exception: pass
    return outs

def score_text(t):
    s=0
    low=t.lower()
    for w in ['grodno{','flag','ctf','secret','debug','default','old','new','{','}']:
        if w in low: s+=20
    s+=sum(1 for c in t if 32<=ord(c)<127)/max(1,len(t))*10
    return s
files=['bos_full_temp1.bin','bos_full_temp08.bin','chat_empty_full_temp1.bin','chat_empty_full_temp08.bin','header_full_temp1.bin','header_full_temp08.bin','bos_header_temp1.bin','eos_header_temp1.bin']
precs=[8,12,16,20,23,24,26,28,29,30,32,36,40,48,56,64]
topks=[2,4,8,16,32,50,64,128,256,512,1024,2048,4096,8192,16384,32768,50000,60000,65536,100000,151936]
temps=[1.0,0.8,0.7,0.5]
rounders=['rint','floor','ceil']
finals=['bottom','top','common','none']
seen=set(); best=[]
for fn in files:
    steps=load(fn)
    print('CASE',fn,'steps',len(steps),flush=True)
    for prec in precs:
      for topk in topks:
       for temp in temps:
        for rd in rounders:
         for final in finals:
          r=dec(steps,prec,topk,temp,rd,final)
          if not r: continue
          bits,infos=r
          if len(bits)<16: continue
          key=(tuple(bits),fn,prec,topk,temp,rd,final)
          for vname,shift,bitord,data in bit_variants(bits):
            for tname,d in transforms(data):
              try: txt=d.decode('utf-8')
              except: txt=d.decode('latin1','ignore')
              if 'grodno{' in txt.lower() or re.search(r'[A-Za-z0-9_{}\-]{6,}',txt):
                sc=score_text(txt)
                if sc>10:
                  rec=(sc,fn,prec,topk,temp,rd,final,vname,shift,bitord,tname,len(bits),repr(txt[:300]))
                  if rec not in best:
                    best.append(rec)
                    if 'grodno{' in txt.lower() or sc>=35:
                      print('HIT',rec,flush=True)
print('\nBEST')
for rec in sorted(best, reverse=True)[:200]: print(rec)
