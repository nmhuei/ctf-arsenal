import numpy as np,struct,zlib,gzip,bz2,lzma,base64,binascii,re,itertools,hashlib
keys=[b'Qwen',b'Qwen2.5',b'qwen2.5-0.5b-instruct-q4_k_m.gguf',b'9217f5db79a29953eb74d5343926648285ec7e67',b'llama-cpp-python==0.3.16',b'hckerror',b'Slop',b'AI-ization',b'grodno',b'message.txt']

def load(fn):
 f=open(fn,'rb'); assert f.read(4)==b'LGTS'; n,nv,temp,tp,mp,tk=struct.unpack('<IIfffI',f.read(24)); steps=[]
 for _ in range(n):
  target=struct.unpack('<i',f.read(4))[0]; logits=np.frombuffer(f.read(4*nv),dtype=np.float32).copy(); steps.append((target,logits))
 return steps

def int2bits(x,n): return [int(c) for c in reversed(f'{int(x):0{n}b}')]
def bits2int(bits): return sum(int(b)*(1<<i) for i,b in enumerate(bits))
def same(a,b):
 for i,(x,y) in enumerate(zip(a,b)):
  if x!=y: return i
 return len(a)
def arith(steps,prec,topk,temp=1.0,rd='rint',final='bottom'):
 cur=[0,1<<prec]; out=[]
 for si,(target,logits) in enumerate(steps):
  order=np.argsort(-logits); rank=int(np.where(order==target)[0][0]); z=logits[order].astype(np.float64)/temp; z-=z[0]; p=np.exp(z); p/=p.sum(); rng=cur[1]-cur[0]
  tmp=np.nonzero(p < 1/rng)[0]; k=topk if len(tmp)==0 else min(max(2,int(tmp[0])),topk); k=min(k,len(p))
  if rank>=k: return None
  vals=p[:k]/p[:k].sum()*rng
  ints=(np.rint(vals) if rd=='rint' else np.floor(vals) if rd=='floor' else np.ceil(vals)).astype(object)
  cum=np.cumsum(ints,dtype=object); over=[i for i,x in enumerate(cum) if x>rng]
  if over: cum=cum[:over[0]]; k=over[0]
  if not len(cum) or rank>=len(cum): return None
  cum[-1]+=rng-cum[-1]; cum=[int(x)+cur[0] for x in cum]
  bot=cum[rank-1] if rank else cur[0]; top=cum[rank]
  if top<=bot: return None
  bb=list(reversed(int2bits(bot,prec))); tb=list(reversed(int2bits(top-1,prec))); n=same(bb,tb)
  if si==len(steps)-1:
   nb=bb if final=='bottom' else tb if final=='top' else tb[:n] if final=='common' else []
  else: nb=tb[:n]
  out+=nb
  cur=[bits2int(reversed(bb[n:]+[0]*n)), bits2int(reversed(tb[n:]+[1]*n))+1]
 return out

def bits_to_bytes(bits):
 for rev,b in [('fwd',bits),('rev',bits[::-1])]:
  for off in range(8):
   s=b[off:]
   for order in ['msb','lsb']:
    by=[]
    for i in range(0,len(s)//8*8,8):
     ch=s[i:i+8]; by.append(int(''.join(map(str,ch)),2) if order=='msb' else sum(bit<<j for j,bit in enumerate(ch)))
    if by: yield f'{rev}/off{off}/{order}',bytes(by)

def variants(data):
 yield 'raw',data
 for x in range(256): yield f'xor{x:02x}',bytes(c^x for c in data)
 for key in keys:
  yield 'xorkey:'+key[:10].decode('latin1','ignore'),bytes(c^key[i%len(key)] for i,c in enumerate(data))
 for name,fn in [('b64',lambda d:base64.b64decode(d+ b'='*((4-len(d)%4)%4))),('hex',binascii.unhexlify),('zlib',zlib.decompress),('gzip',gzip.decompress),('bz2',bz2.decompress),('lzma',lzma.decompress)]:
  try: yield name,fn(data.strip())
  except Exception: pass

def check(label,data):
 for vname,d in variants(data):
  low=d.lower()
  if b'grodno{' in low:
   print('FLAGHIT',label,vname,d[:500]); raise SystemExit
  # Try second-level compression after XOR/raw
  for cname,fn in [('zlib',zlib.decompress),('gzip',gzip.decompress),('bz2',bz2.decompress),('lzma',lzma.decompress)]:
   try:
    dd=fn(d); low2=dd.lower()
    if b'grodno{' in low2:
     print('FLAGHIT',label,vname,cname,dd[:500]); raise SystemExit
   except Exception: pass

files=['bos_full_temp1.bin','chat_empty_full_temp1.bin','header_full_temp1.bin','bos_header_temp1.bin','eos_header_temp1.bin','bos_full_temp08.bin','chat_empty_full_temp08.bin']
precs=[16,20,23,24,26,28,29,30,32,36,40,48,56,64]
topks=[2,4,8,16,32,40,50,64,128,256,512,1024,2048,4096,8192,16384,32768,50000,60000,65536,100000,151936]
temps=[1.0,0.8]
count=0
for fn in files:
 steps=load(fn); print('case',fn,flush=True)
 for prec in precs:
  for topk in topks:
   for temp in temps:
    for rd in ['rint','floor','ceil']:
     for final in ['bottom','top','common','none']:
      bits=arith(steps,prec,topk,temp,rd,final)
      if not bits or len(bits)<32: continue
      for bname,data in bits_to_bytes(bits):
       count+=1; check((fn,prec,topk,temp,rd,final,bname),data)
print('done no flag',count)
