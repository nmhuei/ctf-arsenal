import numpy as np,struct,re,zlib,base64,heapq,itertools

def load(fn):
 f=open(fn,'rb'); assert f.read(4)==b'LGTS'; n,nv,temp,tp,mp,tk=struct.unpack('<IIfffI',f.read(24)); steps=[]
 for _ in range(n):
  target=struct.unpack('<i',f.read(4))[0]
  logits=np.frombuffer(f.read(4*nv),dtype=np.float32).copy(); steps.append((target,logits))
 return steps

def huff_codes(weights):
 # stable first-min twice. heap by weight, insertion counter; appending pair gives increasing counter.
 counter=0; heap=[]; codes={i:[] for i in range(len(weights))}
 for i,w in enumerate(weights): heap.append((int(w),counter,[i])); counter+=1
 heapq.heapify(heap)
 if len(heap)==1: return {0:[]}
 while len(heap)>1:
  w1,c1,leaves1=heapq.heappop(heap); w2,c2,leaves2=heapq.heappop(heap)
  # C++ huffman_decode returns leaf-to-root: append bit to end each combine
  for leaf in leaves1: codes[leaf].append(0)
  for leaf in leaves2: codes[leaf].append(1)
  heapq.heappush(heap,(w1+w2,counter,leaves1+leaves2)); counter+=1
 return codes

def huff_codes_root(weights):
 counter=0; heap=[]; codes={i:[] for i in range(len(weights))}
 for i,w in enumerate(weights): heap.append((int(w),counter,[i])); counter+=1
 heapq.heapify(heap)
 while len(heap)>1:
  w1,c1,l1=heapq.heappop(heap); w2,c2,l2=heapq.heappop(heap)
  for leaf in l1: codes[leaf]=[0]+codes[leaf]
  for leaf in l2: codes[leaf]=[1]+codes[leaf]
  heapq.heappush(heap,(w1+w2,counter,l1+l2)); counter+=1
 return codes

def step(logits,target,history,top_k,top_p,temp,rp,rev=True):
 vals=logits.astype(np.float64).copy()/temp
 if rp!=1.0:
  for t in set(history[-64:]): vals[t]=vals[t]*rp if vals[t]<0 else vals[t]/rp
 order=np.argsort(-vals)
 if top_k>0: order=order[:min(top_k,len(order))]
 z=vals[order]; z-=z.max(); probs=np.exp(z); probs=probs/probs.sum()
 if top_p<1.0:
  cs=np.cumsum(probs); cut=int(np.argmax(cs>=top_p))+1 if np.any(cs>=top_p) else len(probs)
  order=order[:cut]; probs=probs[:cut]; probs=probs/probs.sum()
 pos=np.where(order==target)[0]
 if len(pos)==0: return None
 pos=int(pos[0]); weights=[int(np.ceil(float(p)*65536)) for p in probs]
 return (huff_codes(weights) if rev else huff_codes_root(weights))[pos]

def bytes_from_bits(bits):
 for rev,b in [('fwd',bits),('revall',bits[::-1])]:
  for off in range(8):
   s=b[off:]
   for bo in ['msb','lsb']:
    out=[]
    for i in range(0,len(s)//8*8,8):
     ch=s[i:i+8]; out.append(int(''.join(map(str,ch)),2) if bo=='msb' else sum(bit<<j for j,bit in enumerate(ch)))
    if out: yield rev,off,bo,bytes(out)

def hamming_decode(bits):
 s=''.join(map(str,bits)); out=[]
 for i in range(0,len(s),7):
  ch=s[i:i+7]
  if len(ch)<7: continue
  b=[int(c) for c in ch]; e=(b[0]^b[2]^b[4]^b[6])+2*(b[1]^b[2]^b[5]^b[6])+4*(b[3]^b[4]^b[5]^b[6])
  if e: b[e-1]^=1
  out += [b[2],b[4],b[5],b[6]]
 return out

def check(label,bits):
 for vname,b in [('raw',bits),('ham',hamming_decode(bits)),('revham',hamming_decode(bits[::-1]))]:
  for rev,off,bo,data in bytes_from_bits(b):
   variants=[('raw',data)]
   for nm,fn in [('zlib',zlib.decompress),('b64',lambda d:base64.b64decode(d+b'='*((4-len(d)%4)%4)) )]:
    try: variants.append((nm,fn(data.strip())))
    except Exception: pass
   for nm,d in variants:
    txt=d.decode('utf-8','ignore'); low=txt.lower()
    if 'grodno{' in low:
     print('FLAG',label,vname,rev,off,bo,nm,repr(txt),d.hex(),flush=True); raise SystemExit
    if 'flag' in low or 'grod' in low or re.search(r'[A-Za-z0-9_{}]{12,}',txt):
     print('HIT',label,vname,rev,off,bo,nm,repr(txt[:120]),d[:40].hex(),flush=True)

files={
 'bos_full_temp1.bin':[151643],
 'chat_empty_full_temp1.bin':[],
 'header_full_temp1.bin':[32,2805,11116,369,264,12406,35481,19174,510],
 'bos_header_temp1.bin':[151643,32,2805,11116,369,264,12406,35481,19174,510],
}
for fn,h0 in files.items():
 print('CASE',fn,flush=True); steps=load(fn)
 for top_k in [0,40,50,100,256,512,1024,2048,4096,8192,16384,32768,50000,65536,151936]:
  for top_p in [1.0,0.95,0.9,0.8,0.5]:
   for temp in [0.8,1.0]:
    for rp in [1.0,1.1]:
     for rev in [True,False]:
      hist=list(h0); bits=[]; ok=True
      for target,logits in steps:
       b=step(logits,target,hist,top_k,top_p,temp,rp,rev)
       if b is None: ok=False; break
       bits+=b; hist.append(target)
      if ok and len(bits)>=16: check((fn,top_k,top_p,temp,rp,'rev' if rev else 'root',len(bits)),bits)
print('done')
