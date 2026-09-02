import itertools,base64,zlib,gzip,bz2,lzma,re
seqs={
'full':[32,2805,11116,369,264,12406,35481,19174,510,50590,476,40320,4087,2640,541,5591,11],
'cont':[50590,476,40320,4087,2640,541,5591,11],
'header':[32,2805,11116,369,264,12406,35481,19174,510],
}

def outs_from_nums(nums):
    yield 'mod256', bytes(n%256 for n in nums)
    yield 'lowhigh', b''.join(bytes([n&255,(n>>8)&255]) for n in nums)
    yield 'highlow', b''.join(bytes([(n>>8)&255,n&255]) for n in nums)
    for base in [min(nums), nums[0], 0, 32, 151643]:
        vals=[(n-base)%256 for n in nums]
        yield f'minus{base}', bytes(vals)
    vals=[nums[0]]+[nums[i]-nums[i-1] for i in range(1,len(nums))]
    yield 'diff_mod', bytes(v%256 for v in vals)
    yield 'absdiff_mod', bytes(abs(v)%256 for v in vals)

def tr(b):
    yield 'raw',b
    for fnn,fn in [('zlib',zlib.decompress),('gzip',gzip.decompress),('bz2',bz2.decompress),('lzma',lzma.decompress)]:
        try: yield fnn,fn(b)
        except: pass
    try: yield 'b64',base64.b64decode(b,validate=False)
    except: pass
    for k in range(256):
        xb=bytes(x^k for x in b)
        if b'grod' in xb or b'flag' in xb.lower(): yield f'xor{k}', xb

def score(b): return sum(32<=x<127 or x in (9,10,13) for x in b)/max(1,len(b))
for name,seq in seqs.items():
    for revname,s in [('fwd',seq),('rev',seq[::-1])]:
        for oname,b in outs_from_nums(s):
            for tname,out in tr(b):
                if b'grod' in out or b'flag' in out.lower() or (len(out)>6 and score(out)>.9 and any(c in out for c in b'{}_')):
                    print(name,revname,oname,tname,out)
print('done')
