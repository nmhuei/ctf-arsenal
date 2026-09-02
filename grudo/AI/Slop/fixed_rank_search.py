import base64,zlib,gzip,bz2,lzma,itertools,re,math
seqs={
'header0':[48,69,1993,75,155,121,26,0],
'header1':[49,70,1994,76,156,122,27,1],
'bos0':[2167,483,335,0,0,124,5,0,57,57,65,1927,55,141,149,28,0],
'bos1':[2168,484,336,1,1,125,6,1,58,58,66,1928,56,142,150,29,1],
'chat0':[37,194,1316,0,1,92,5,0,6,254,112,2984,80,201,132,29,0],
'chat1':[38,195,1317,1,2,93,6,1,7,255,113,2985,81,202,133,30,1]
}

def gray_inv(n):
    x=0
    while n:
        x ^= n; n >>=1
    return x

def bits_of(n,w,msb=True):
    s=bin(n & ((1<<w)-1))[2:].zfill(w)
    return s if msb else s[::-1]
def bytes_vars(bits):
    for sname,s in [('bits',bits),('revall',bits[::-1])]:
        for off in range(8):
            if len(s)-off>=8:
                yield (sname,off,'normal',bytes(int(s[i:i+8],2) for i in range(off,len(s)-7,8)))
                yield (sname,off,'byterev',bytes(int(s[i:i+8][::-1],2) for i in range(off,len(s)-7,8)))
def transforms(b):
    yield ('raw',b)
    # strip leading/trailing nulls
    yield ('strip0',b.strip(b'\x00'))
    for fnname,fn in [('zlib',zlib.decompress),('gzip',gzip.decompress),('bz2',bz2.decompress),('lzma',lzma.decompress)]:
        try: yield (fnname,fn(b))
        except Exception: pass
    try: yield ('b64',base64.b64decode(b,validate=False))
    except Exception: pass
    for k in range(256):
        xb=bytes(x^k for x in b)
        if b'grod' in xb or b'flag' in xb.lower(): yield (f'xor{k}',xb)

def score(b): return sum(32<=x<127 or x in (9,10,13) for x in b)/max(1,len(b))
for name,seq in seqs.items():
    for mode in ['rank','rankminus','gray','gray_inv','delta','delta_abs']:
        if mode=='rank': vals=seq
        elif mode=='rankminus': vals=[x-1 for x in seq]
        elif mode=='gray': vals=[x^(x>>1) for x in seq]
        elif mode=='gray_inv': vals=[gray_inv(x) for x in seq]
        elif mode=='delta': vals=[seq[0]]+[seq[i]-seq[i-1] for i in range(1,len(seq))]
        else: vals=[seq[0]]+[abs(seq[i]-seq[i-1]) for i in range(1,len(seq))]
        for w in range(1,33):
            for msb in [True,False]:
                bits=''.join(bits_of(v,w,msb) for v in vals)
                for vinfo in bytes_vars(bits):
                    b=vinfo[3]
                    for tname,out in transforms(b):
                        if b'grodno{' in out or b'grod' in out or re.search(rb'[a-z0-9_]{3,}\{',out):
                            print('FOUNDISH',name,mode,w,msb,vinfo[:3],tname,out)
                        elif len(out)>=6 and score(out)>.95:
                            # print only if contains braces-ish or lower letters enough
                            if any(c in out for c in b'{}_') or sum(97<=x<=122 for x in out)>=5:
                                print('PRINT',name,mode,w,msb,vinfo[:3],tname,out)
print('done')
