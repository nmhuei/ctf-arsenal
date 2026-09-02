import numpy as np,struct,zlib,gzip,bz2,lzma,base64,binascii,itertools,re

def load_ranks(fn):
 f=open(fn,'rb'); assert f.read(4)==b'LGTS'
 n,nv,temp,tp,mp,tk=struct.unpack('<IIfffI',f.read(24)); ranks=[]; ids=[]
 for _ in range(n):
  target=struct.unpack('<i',f.read(4))[0]
  logits=np.frombuffer(f.read(4*nv),dtype=np.float32)
  # 0-based rank, ties by stable? use > count equals sorted pos both
  rank=int((logits>logits[target]).sum())
  ranks.append(rank); ids.append(target)
 return ranks,ids

def hamming_decode(encoded_bits):
 data_bits=''
 for i in range(0,len(encoded_bits),7):
  chunk=encoded_bits[i:i+7]
  if len(chunk)<7: continue
  bits=[int(b) for b in chunk]
  s1=bits[0]^bits[2]^bits[4]^bits[6]
  s2=bits[1]^bits[2]^bits[5]^bits[6]
  s3=bits[3]^bits[4]^bits[5]^bits[6]
  pos=s1+2*s2+4*s3
  if pos: bits[pos-1]^=1
  data_bits += f'{bits[2]}{bits[4]}{bits[5]}{bits[6]}'
 return data_bits

def bytes_from_bits(s, bitorder='msb'):
 out=[]
 for i in range(0,len(s)//8*8,8):
  chunk=s[i:i+8]
  if bitorder=='msb': out.append(int(chunk,2))
  else: out.append(sum(int(b)<<j for j,b in enumerate(chunk)))
 return bytes(out)

def try_dec(data):
 outs=[]
 for name,fn in [('raw',lambda x:x),('zlib',zlib.decompress),('gzip',gzip.decompress),('bz2',bz2.decompress),('lzma',lzma.decompress)]:
  try: outs.append((name,fn(data)))
  except Exception: pass
 try: outs.append(('b64-zlib',zlib.decompress(base64.b64decode(data))))
 except Exception: pass
 return outs
files=['bos_full_temp1.bin','bos_full_temp08.bin','chat_empty_full_temp1.bin','chat_empty_full_temp08.bin','header_full_temp1.bin','bos_header_temp1.bin','eos_header_temp1.bin']
for fn in files:
 ranks,ids=load_ranks(fn)
 print('CASE',fn,'ranks',ranks)
 for b in range(1,19):
  for mode in ['zero','mod','low','raw']:
   vals=[]
   ok=True
   for r in ranks:
    if mode=='zero': v=r if r<(1<<b) else 0
    elif mode=='mod': v=r%(1<<b)
    elif mode=='low': v=r & ((1<<b)-1)
    elif mode=='raw':
     if r>=(1<<b): ok=False; break
     v=r
    vals.append(format(v,f'0{b}b'))
   if not ok: continue
   bitstr=''.join(vals)
   variants=[]
   for name,s in [('direct',bitstr),('rev_tokens',''.join(vals[::-1])),('rev_bits',bitstr[::-1])]:
    for off in range(8):
     ss=s[off:]
     variants.append((name,off,'plain',ss))
     variants.append((name,off,'hamming',hamming_decode(ss)))
   for name,off,hmode,s in variants:
    for bord in ['msb','lsb']:
     data=bytes_from_bits(s,bord)
     for decname,d in try_dec(data):
      txt=d.decode('utf-8','ignore')
      low=txt.lower()
      if 'grodno{' in low or 'flag' in low or re.search(r'g.{0,3}r.{0,3}o.{0,3}d',low) or (sum(32<=c<127 for c in d)/max(1,len(d))>0.8 and len(d)>5):
       print('HIT',fn,'b',b,mode,name,off,hmode,bord,decname,repr(txt[:200]),'hex',data[:30].hex())
print('done')
