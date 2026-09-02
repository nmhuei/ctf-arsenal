import numpy as np,struct,re,zlib,base64

def load(fn):
 f=open(fn,'rb'); assert f.read(4)==b'LGTS'; n,nv,temp,tp,mp,tk=struct.unpack('<IIfffI',f.read(24)); steps=[]
 for _ in range(n):
  target=struct.unpack('<i',f.read(4))[0]
  logits=np.frombuffer(f.read(4*nv),dtype=np.float32).copy(); steps.append((target,logits))
 return steps

# C++ make_huffman_code: each leaf value=i, repeatedly take first min, first min, pair(left=n1,right=n2), append pair.
def make_tree(weights):
 nodes=[['leaf',w,i] for i,w in enumerate(weights)]
 while len(nodes)>1:
  i_min=min(range(len(nodes)), key=lambda i:nodes[i][1])
  n1=nodes.pop(i_min)
  i_min=min(range(len(nodes)), key=lambda i:nodes[i][1])
  n2=nodes.pop(i_min)
  nodes.append(['pair',n1[1]+n2[1],n1,n2])
 return nodes[0]

def huff_decode_path(node,idx):
 # exact huffman_decode: recurse left then append false, recurse right append true. This returns leaf-to-root for depth>1.
 if node[0]=='leaf':
  return [] if node[2]==idx else None
 r=huff_decode_path(node[2],idx)
 if r is not None: return r+[0]
 r=huff_decode_path(node[3],idx)
 if r is not None: return r+[1]
 return None

def huff_decode_path_root(node,idx,path=[]):
 if node[0]=='leaf': return path if node[2]==idx else None
 r=huff_decode_path_root(node[2],idx,path+[0])
 if r is not None: return r
 return huff_decode_path_root(node[3],idx,path+[1])

def step_bits(logits,target,history,top_k=40,top_p=0.95,temp=0.8,repeat_penalty=1.0,repeat_last_n=64,revcode=True):
 vals=logits.astype(np.float64).copy()/temp
 if repeat_penalty!=1.0 and repeat_last_n!=0:
  last=history[-repeat_last_n:] if repeat_last_n>0 else history
  for t in set(last):
   if vals[t]<0: vals[t]*=repeat_penalty
   else: vals[t]/=repeat_penalty
 order=np.argsort(-vals)
 if top_k>0: order=order[:min(top_k,len(order))]
 # probs over top_k
 z=vals[order]; z-=z.max(); probs=np.exp(z); probs=probs/probs.sum()
 if top_p<1.0:
  cs=np.cumsum(probs)
  cut=int(np.argmax(cs>=top_p))+1 if np.any(cs>=top_p) else len(probs)
  order=order[:cut]; probs=probs[:cut]
  probs=probs/probs.sum()
 pos=np.where(order==target)[0]
 if len(pos)==0: return None
 pos=int(pos[0])
 weights=[int(np.ceil(float(p)*65536.0)) for p in probs]
 if len(weights)==1: return []
 tree=make_tree(weights)
 return huff_decode_path(tree,pos) if revcode else huff_decode_path_root(tree,pos)

def bytes_from_bits(bits):
 for rev,b in [('fwd',bits),('revall',bits[::-1])]:
  for off in range(8):
   s=b[off:]
   for bo in ['msb','lsb']:
    out=[]
    for i in range(0,len(s)//8*8,8):
     ch=s[i:i+8]
     out.append(int(''.join(map(str,ch)),2) if bo=='msb' else sum(bit<<j for j,bit in enumerate(ch)))
    if out: yield rev,off,bo,bytes(out)

def hamming_decode(bitstr):
 out=''
 for i in range(0,len(bitstr),7):
  ch=bitstr[i:i+7]
  if len(ch)<7: continue
  bits=[int(c) for c in ch]
  s1=bits[0]^bits[2]^bits[4]^bits[6]; s2=bits[1]^bits[2]^bits[5]^bits[6]; s3=bits[3]^bits[4]^bits[5]^bits[6]
  pos=s1+2*s2+4*s3
  if pos: bits[pos-1]^=1
  out+=f'{bits[2]}{bits[4]}{bits[5]}{bits[6]}'
 return [int(c) for c in out]

def check(label,bits):
 bitstr=''.join(map(str,bits))
 variants=[('rawbits',bits),('hamming',hamming_decode(bitstr)),('rev_hamming',hamming_decode(bitstr[::-1]))]
 for vname,b in variants:
  for rev,off,bo,data in bytes_from_bits(b):
   datas=[('raw',data)]
   for name,fn in [('zlib',zlib.decompress),('b64',lambda d:base64.b64decode(d+b'='*((4-len(d)%4)%4)) )]:
    try: datas.append((name,fn(data.strip())))
    except Exception: pass
   for dname,d in datas:
    txt=d.decode('utf-8','ignore')
    low=txt.lower()
    if b'grodno{' in d.lower() or 'grodno{' in low:
     print('FLAG',label,vname,rev,off,bo,dname,repr(txt),d.hex()); raise SystemExit
    if 'flag' in low or 'grod' in low or re.search(r'[A-Za-z0-9_{}]{10,}',txt):
     print('HIT',label,vname,rev,off,bo,dname,repr(txt[:160]),d[:40].hex())

# token histories for each dump. Need know targets lengths.
files={
 'bos_full_temp1.bin':[],
 'chat_empty_full_temp1.bin':[],
 'header_full_temp1.bin':[32,2805,11116,369,264,12406,35481,19174,510],
 'bos_header_temp1.bin':[151643,32,2805,11116,369,264,12406,35481,19174,510],
 'eos_header_temp1.bin':[151645,32,2805,11116,369,264,12406,35481,19174,510],
}
# for bos_full, history should start with BOS maybe dump was generated with context [bos] then target whole msg
files['bos_full_temp1.bin']=[151643]
# chat_empty_full was generated with Qwen chat wrapper? inspect dump context from script maybe use empty chat tokens; unknown but logits include context; history not required unless repeat_penalty !=1
for fn,hist0 in files.items():
 steps=load(fn); print('CASE',fn,'steps',len(steps))
 for top_k in [0,40,50,100,500,2048,8192,50000,151936]:
  for top_p in [1.0,0.95,0.9,0.8,0.5]:
   for temp in [0.8,1.0,0.7]:
    for rp in [1.0,1.1]:
     for revcode in [True,False]:
      bits=[]; hist=list(hist0); ok=True
      for target,logits in steps:
       b=step_bits(logits,target,hist,top_k,top_p,temp,rp,64,revcode)
       if b is None: ok=False; break
       bits+=b; hist.append(target)
      if ok and len(bits)>=16:
       check((fn,top_k,top_p,temp,rp,'revcode' if revcode else 'rootcode',len(bits)),bits)
print('done')
