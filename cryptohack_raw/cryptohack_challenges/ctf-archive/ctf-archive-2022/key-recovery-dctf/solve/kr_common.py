import os, hashlib, itertools
S=[80,12,233,22,60,179,30,32,112,114,174,83,207,107,33,237,37,121,161,50,54,57,77,59,152,53,52,204,70,104,163,68,196,189,17,211,178,220,92,137,78,29,96,103,239,213,108,109,111,113,90,162,21,120,23,157,123,195,186,205,132,236,232,145,248,85,134,135,139,140,102,144,249,147,181,130,194,154,175,183,219,28,66,202,91,116,142,106,9,188,203,117,206,208,151,242,82,14,210,217,20,221,227,10,99,156,160,241,67,126,65,45,231,191,46,71,58,245,24,235,218,253,61,64,79,192,8,63,3,122,35,7,81,38,201,40,252,118,254,133,177,73,34,13,180,76,4,62,15,110,165,246,100,98,89,55,250,56,47,86,72,143,173,131,223,39,115,222,166,1,148,16,74,51,200,146,95,6,36,128,69,184,155,153,31,216,215,88,2,240,187,11,167,212,164,43,214,171,49,244,243,0,209,44,197,172,251,84,170,198,168,149,75,26,136,119,230,225,255,42,228,125,185,229,124,25,93,224,5,158,226,87,101,129,176,159,169,193,48,247,234,182,41,238,94,105,18,97,141,199,150,127,138,27,19,190]
Sinv=[0]*256
for i,v in enumerate(S): Sinv[v]=i
P_nib=[0,4,8,12,1,5,9,13,2,6,10,14,3,7,11,15]
P_box=[24,19,12,25,0,9,6,31,26,11,28,5,14,13,20,15,18,21,10,27,4,1,22,3,8,17,16,29,2,23,30,7]
P_box_inv=[4,21,28,23,20,11,6,31,24,5,18,9,2,13,12,15,26,25,16,1,14,17,22,29,0,3,8,19,10,27,30,7]
def xor(a,b): return bytes(x^y for x,y in zip(a,b))
def b2n(x):
    out=[]
    for b in x: out += [b>>4,b&15]
    return out
def n2b(n): return bytes([n[i]*16+n[i+1] for i in range(0,32,2)])
def per(x):
    n=b2n(x); return n2b([P_nib[n[P_box[i]]] for i in range(32)])
def per_inv(x):
    n=b2n(x); return n2b([P_nib[n[P_box_inv[i]]] for i in range(32)])
def sub(x): return bytes(S[a] for a in x)
def sub_inv(x): return bytes(Sinv[a] for a in x)
def ks(k):
    kk=k+hashlib.sha512(k).digest(); return [kk[i:i+16] for i in range(0,64,16)]
def enc_keys(keys,p):
    x=p
    for r in range(3): x=per(xor(sub(x),keys[r]))
    return xor(sub(x),keys[3])
def dec_keys(keys,c):
    x=sub_inv(xor(c,keys[3]))
    for i in range(2,-1,-1): x=sub_inv(xor(per_inv(x),keys[i]))
    return x
def make_pts(base, st):
    kind,idx=st; base=bytearray(base); res=[]
    if kind=='byte':
        for v in range(256):
            p=bytearray(base); p[idx]=v; res.append(bytes(p))
    elif kind=='nib':
        ni=idx
        for v in range(16):
            p=bytearray(base)
            if ni%2==0: p[ni//2]=(p[ni//2]&0x0f)|(v<<4)
            else: p[ni//2]=(p[ni//2]&0xf0)|v
            res.append(bytes(p))
    elif kind=='nibs':
        n1,n2=idx
        for v1 in range(16):
            for v2 in range(16):
                p=bytearray(base)
                for ni,v in [(n1,v1),(n2,v2)]:
                    if ni%2==0: p[ni//2]=(p[ni//2]&0x0f)|(v<<4)
                    else: p[ni//2]=(p[ni//2]&0xf0)|v
                res.append(bytes(p))
    return res
def internal_states(keys,p):
    x=p; outs=[]
    for r in range(3):
        x=per(xor(sub(x),keys[r])); outs.append(x)
    return outs
