import struct, numpy as np, random, base64, zlib, gzip, bz2, lzma
from decimal import Decimal, getcontext, ROUND_FLOOR, ROUND_HALF_DOWN
getcontext().prec=300

def load(path):
    with open(path,'rb') as f:
        assert f.read(4)==b'LGTS'
        nsteps,nvocab,temp,top_p,min_p,top_k=struct.unpack('<IIfffI', f.read(24))
        steps=[]
        for _ in range(nsteps):
            target=struct.unpack('<i', f.read(4))[0]
            logits=np.frombuffer(f.read(4*nvocab), dtype=np.float32).copy().astype(np.float64)/temp
            order=np.argsort(-logits)
            z=logits[order]-logits[order[0]]; p=np.exp(z); p/=p.sum()
            rank=int(np.where(order==target)[0][0])
            steps.append((rank,p))
    return steps

def decimal_mod(a,m): return a - m*(a/m).to_integral_value(rounding=ROUND_FLOOR)
def round_half_down(v): return v.to_integral_value(rounding=ROUND_HALF_DOWN)

def decode_rrc(steps, bit_length=128, topk=None, key=42, use_str=True):
    MAX=Decimal(2)**bit_length
    L=Decimal(0); R=MAX
    Lhist=[]; Dhist=[]; ohist=[]
    prng=random.Random(key)
    for rank,p_all in steps:
        k=len(p_all) if topk is None or topk<0 else min(topk,len(p_all))
        if rank>=k: return None
        top=p_all[:k]
        cs=np.cumsum(top,dtype=np.float64); cs=cs/cs[-1]
        # Decimal(str(...)) as reference code
        b0=Decimal(0) if rank==0 else Decimal(str(float(cs[rank-1])))
        b1=Decimal(str(float(cs[rank])))
        Lhist.append(L); Dhist.append(R-L); ohist.append(Decimal(prng.random()))
        Delta=R-L; L,R = L + b0*Delta, L + b1*Delta
    mid=(L+R)/2
    for t in range(len(steps)-1,-1,-1):
        mid=Lhist[t] + decimal_mod(mid-Lhist[t]-ohist[t]*Dhist[t], Dhist[t])
    d=round_half_down(mid)
    bits=bin(int(d))[2:].zfill(bit_length)
    return bits

def variants(bits):
    for srcname,src in [('bits',bits),('revall',bits[::-1])]:
        for off in range(8):
            if len(src)-off>=8:
                bs=bytes(int(src[i:i+8],2) for i in range(off,len(src)-7,8))
                yield srcname,off,'normal',bs
                bs2=bytes(int(src[i:i+8][::-1],2) for i in range(off,len(src)-7,8))
                yield srcname,off,'byterev',bs2

def trydec(b):
    yield b
    for fn in [zlib.decompress,gzip.decompress,bz2.decompress,lzma.decompress]:
        try: yield fn(b)
        except Exception: pass
    try: yield base64.b64decode(b,validate=False)
    except Exception: pass

def score(b): return sum(32<=x<127 or x in (9,10,13) for x in b)/max(1,len(b))

def show(label,bits,force=False):
    found=[]; good=[]
    for src,off,kind,bs in variants(bits):
        for bb in trydec(bs):
            if b'grodno{' in bb or b'grod' in bb or b'flag' in bb.lower(): found.append((src,off,kind,bb))
        if len(bs)>=6 and score(bs)>0.9: good.append((src,off,kind,bs))
    if found or force or good:
        print('\n'+label,'len',len(bits),'bits',bits[:160])
        for x in found or good[:8] or list(variants(bits))[:1]: print(x[:3],x[3][:160])
        return bool(found)
    return False

cases={'header1':'header_full_temp1.bin','bos1':'bos_full_temp1.bin','chat1':'chat_empty_full_temp1.bin','header08':'header_full_temp08.bin'}
for cname,fn in cases.items():
    steps=load(fn)
    print('CASE',cname,'ranks',[x[0] for x in steps])
    for bitlen in [64,80,88,96,104,112,120,128,136,144,160,192,256]:
      for topk in [2048,4096,8192,16384,32768,50000,65536,100000,151936,-1]:
        for key in [42,0,1,123,1337,2024,2025,9217,314159,271828]:
          bits=decode_rrc(steps,bitlen,topk,key)
          if bits is None: continue
          force=(cname=='header1' and bitlen in [80,96,128] and topk in [2048,4096,50000,151936,-1] and key==42)
          if show(f'{cname} bitlen={bitlen} topk={topk} key={key}',bits,force):
            raise SystemExit
