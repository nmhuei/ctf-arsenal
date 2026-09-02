import itertools, math, base64,zlib,gzip,bz2,lzma,re,hashlib
seqs={
'full0':[48,69,1993,75,155,121,26,0],
'full1':[49,70,1994,76,156,122,27,1],
'prev0':[48,22,3498,32230,101002,2075,41082,6],
'prev1':[49,23,3499,32231,101003,2076,41083,7],
'bos0':[2167,483,335,0,0,124,5,0,57,57,65,1927,55,141,149,28,0],
'chat0':[37,194,1316,0,1,92,5,0,6,254,112,2984,80,201,132,29,0],
}
# also token ids
seqs.update({'tokfull':[32,2805,11116,369,264,12406,35481,19174,510,50590,476,40320,4087,2640,541,5591,11],'tokcont':[50590,476,40320,4087,2640,541,5591,11]})

def gray_inv(n):
 x=0
 while n:
  x^=n; n>>=1
 return x

def bits(n,w,order):
 s=bin(n & ((1<<w)-1))[2:].zfill(w)
 return s if order=='msb' else s[::-1]

def bvars(s):
 for sn,src in [('bits',s),('revall',s[::-1])]:
  for off in range(8):
   if len(src)-off>=8:
    bs=bytes(int(src[i:i+8],2) for i in range(off,len(src)-7,8)); yield sn,off,'normal',bs
    bs2=bytes(int(src[i:i+8][::-1],2) for i in range(off,len(src)-7,8)); yield sn,off,'byterev',bs2

def transforms(b):
 yield 'raw',b
 yield 'strip0',b.strip(b'\x00')
 for fnn,fn in [('zlib',zlib.decompress),('gzip',gzip.decompress),('bz2',bz2.decompress),('lzma',lzma.decompress)]:
  try: yield fnn,fn(b)
  except Exception: pass
 for alt in [b, b+b'=', b+b'==']:
  try: yield 'b64',base64.b64decode(alt,validate=False)
  except Exception: pass
 for k in range(256):
  xb=bytes(x^k for x in b)
  if b'grod' in xb or b'flag' in xb.lower() or b'{' in xb: yield f'xor{k}', xb

def score(b): return sum(32<=x<127 or x in (9,10,13) for x in b)/max(1,len(b))
def check(label,b):
 for t,o in transforms(b):
  if b'grodno{' in o or b'grod' in o or b'flag' in o.lower() or re.search(rb'g[a-z0-9_]{2,}\{',o):
   print('FOUND',label,t,o)
   return True
  if len(o)>=5 and score(o)>0.95 and (any(c in o for c in b'{}_') or sum(97<=x<=122 for x in o)>=5):
   print('PRINT',label,t,o)
 return False
for name,seq in seqs.items():
 variants={}
 variants['raw']=seq
 variants['minus1']=[x-1 for x in seq]
 variants['diff']=[seq[0]]+[seq[i]-seq[i-1] for i in range(1,len(seq))]
 variants['absdiff']=[seq[0]]+[abs(seq[i]-seq[i-1]) for i in range(1,len(seq))]
 variants['gray']=[x^(x>>1) for x in seq]
 variants['grayinv']=[gray_inv(x) for x in seq]
 for vname,vals in variants.items():
  # direct mod/endian
  for desc,nums in [('fwd',vals),('rev',vals[::-1])]:
   try: check(f'{name}:{vname}:{desc}:mod256', bytes([n%256 for n in nums]))
   except: pass
   for endian in ['little','big']:
    for width in [2,3,4,5,8]:
     try: check(f'{name}:{vname}:{desc}:{width}:{endian}', b''.join(int(n%(1<<(8*width))).to_bytes(width,endian,signed=False) for n in nums))
     except: pass
  # bit pack fixed width
  for w in range(1,49):
   for order in ['msb','lsb']:
    s=''.join(bits(v,w,order) for v in vals)
    for bv in bvars(s):
     check(f'{name}:{vname}:w{w}:{order}:{bv[:3]}', bv[3])
print('done')
