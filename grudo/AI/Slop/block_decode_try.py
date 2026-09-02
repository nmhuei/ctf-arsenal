import numpy as np, zlib, gzip, bz2, lzma, base64, re
# tokens known
full=[32,2805,11116,369,264,12406,35481,19174,510,50590,476,40320,4087,2640,541,5591,11]
cont=full[9:]
V=151936

def int2bits(x,n): return [int(c) for c in reversed(f'{x:0{n}b}')]
def bvars(bits):
 for sname,s in [('bits',bits),('revall',bits[::-1])]:
  for off in range(8):
   if len(s)-off>=8:
    yield (sname,off,'normal',bytes(int(''.join(map(str,s[i:i+8])),2) for i in range(off,len(s)-7,8)))
    yield (sname,off,'byterev',bytes(int(''.join(map(str,s[i:i+8][::-1])),2) for i in range(off,len(s)-7,8)))
def score(b): return sum(32<=x<127 or x in (9,10,13) for x in b)/max(1,len(b))
def try_show(label,bits):
 found=[]; good=[]
 for v in bvars(bits):
  bs=v[3]
  outs=[bs]
  for fn in [zlib.decompress,gzip.decompress,bz2.decompress,lzma.decompress]:
   try: outs.append(fn(bs))
   except: pass
  try: outs.append(base64.b64decode(bs))
  except: pass
  for out in outs:
   if b'grodno{' in out or b'grod' in out or b'flag' in out.lower(): found.append(v[:3]+(out,))
  if len(bs)>=5 and score(bs)>.85: good.append(v)
 if found or good:
  print('\n',label,'len',len(bits),''.join(map(str,bits)))
  for x in found or good[:6]: print(x[:3],x[3])
  return bool(found)
 return False
for toks_name,toks in [('cont',cont),('full',full)]:
 for bs in range(1,18):
  num_bins=2**bs
  if num_bins>V: break
  words_per_bin=V/num_bins
  # seeds: StegaText uses block size; also try fixed common
  for seed in [bs,0,1,42,123,1234,1337,2024,2025,9217,16,32,64,128,256,512,1024]:
   vocab=np.arange(V)
   np.random.seed(seed); np.random.shuffle(vocab)
   w2b=np.empty(V,dtype=np.int32)
   for b in range(num_bins):
    arr=vocab[int(b*words_per_bin):int((b+1)*words_per_bin)]
    w2b[arr]=b
   bits=[]
   for t in toks: bits += int2bits(int(w2b[t]),bs)
   if try_show(f'{toks_name} block={bs} seed={seed}',bits): raise SystemExit
print('done')
