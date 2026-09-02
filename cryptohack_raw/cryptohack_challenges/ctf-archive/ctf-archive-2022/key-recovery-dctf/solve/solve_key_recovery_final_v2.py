#!/usr/bin/env python3
import os, sys, socket, hashlib, re, time
from kr_common import *
from test_main_recovery import MAIN, cand, upd, peel_b2, peel_b1

SEL=[('nibs',p) for p in [(10,16),(8,14),(11,18),(4,17),(13,20),(0,10),(22,24),(1,20),(2,18),(2,9),(8,24)]]
MASKS=[(65535,65535,64507),(65535,65535,47103),(65535,65535,64476),(65535,65535,61178),(65535,65535,65469),(65535,65535,53247),(65535,65535,38879),(65535,65535,65343),(65535,65535,65007),(65535,65535,65007),(65535,65535,65151)]

def ns(out_nib):
    s=P_box_inv[out_nib]; return s//2,s%2

def ac3(dom,constraints):
    changed=True
    while changed:
        changed=False
        for x,y,allowed in constraints:
            dx,dy=dom[x],dom[y]
            nx={a for a in dx if any((a,b) in allowed for b in dy)}
            ny={b for b in dy if any((a,b) in allowed for a in nx)}
            if len(nx)<len(dx): dom[x]=nx; changed=True
            if len(ny)<len(dy): dom[y]=ny; changed=True
            if not nx or not ny: return False
    return True

def pair_allowed_next(obs_structs,next_mask_idx,pos,dom):
    s0,n0=ns(2*pos); s1,n1=ns(2*pos+1)
    inds=[i for i,m in enumerate(MASKS) if (m[next_mask_idx]>>pos)&1]
    pre=[]
    for idx in inds:
        obs=obs_structs[idx]
        d0={}
        for g in dom[s0]:
            arr=[]
            for x in obs:
                b=Sinv[x[s0]^g]; v=(b>>4) if n0==0 else (b&15); arr.append(P_nib[v])
            d0[g]=arr
        d1={}
        for g in dom[s1]:
            arr=[]
            for x in obs:
                b=Sinv[x[s1]^g]; v=(b>>4) if n1==0 else (b&15); arr.append(P_nib[v])
            d1[g]=arr
        pre.append((d0,d1,len(obs)))
    allowed=set()
    for a in list(dom[s0]):
        for b in list(dom[s1]):
            kc=set(range(256))
            for d0,d1,n in pre:
                vals=[(d0[a][i]<<4)|d1[b][i] for i in range(n)]
                kc &= cand(vals)
                if not kc: break
            if kc: allowed.add((a,b))
    return (s0,s1), allowed

def solve_layer(obs_structs,direct_mask_idx,next_mask_idx,limit=20000,verbose=False,name=''):
    dom=[set(range(256)) if i in MAIN else {0} for i in range(16)]
    for obs,m in zip(obs_structs,MASKS): upd(dom,obs,m[direct_mask_idx])
    if verbose: print(f'[{name}] direct sizes:', [len(dom[i]) for i in range(16)], flush=True)
    constraints=[]; pending=set(MAIN)
    while pending:
        pos=min(pending,key=lambda p: len(dom[ns(2*p)[0]])*len(dom[ns(2*p+1)[0]]))
        if verbose: print(f'[{name}] add constraint pos {pos}, product {len(dom[ns(2*pos)[0]])*len(dom[ns(2*pos+1)[0]])}', flush=True)
        (x,y),allow=pair_allowed_next(obs_structs,next_mask_idx,pos,dom)
        constraints.append((x,y,allow)); pending.remove(pos)
        if not ac3(dom,constraints): return []
    sols=[]
    def rec(d):
        if len(sols)>=limit: return
        d=[set(s) for s in d]
        if not ac3(d,constraints): return
        if all(len(d[i])==1 for i in MAIN):
            k=bytearray(16)
            for i in MAIN: k[i]=next(iter(d[i]))
            sols.append(bytes(k)); return
        v=min([i for i in MAIN if len(d[i])>1], key=lambda i: len(d[i]))
        for val in list(d[v]):
            nd=[set(s) for s in d]; nd[v]={val}; rec(nd)
            if len(sols)>=limit: return
    # For K3 we prefer to retry the remote connection when the candidate graph is unlucky.
    if name == 'k3':
        prod=1
        for i in MAIN:
            prod *= len(dom[i])
            if prod > limit:
                if verbose: print(f'[k3] candidate product {prod} > retry cap', flush=True)
                return []
    rec(dom)
    if verbose: print(f'[{name}] solutions:', len(sols), flush=True)
    return sols

def allowed_k1_k0_pos(data,b1_structs,pos,dom,quick=96):
    s0,n0=ns(2*pos); s1,n1=ns(2*pos+1)
    obs=[]; sp=[]
    for (pts,_),b1 in zip(data,b1_structs):
        obs.extend(b1); sp.extend([S[p[pos]] for p in pts])
    N=len(obs); q=min(quick,N)
    d0={}
    for g in dom[s0]:
        arr=[]
        for x in obs:
            b=Sinv[x[s0]^g]; v=(b>>4) if n0==0 else (b&15); arr.append(P_nib[v])
        d0[g]=arr
    d1={}
    for g in dom[s1]:
        arr=[]
        for x in obs:
            b=Sinv[x[s1]^g]; v=(b>>4) if n1==0 else (b&15); arr.append(P_nib[v])
        d1[g]=arr
    allowed=set(); kval={}
    for a,A in d0.items():
        for b,B in d1.items():
            first=((A[0]<<4)|B[0])^sp[0]
            ok=True
            for i in range(1,q):
                if (((A[i]<<4)|B[i])^sp[i])!=first: ok=False; break
            if not ok: continue
            for i in range(q,N):
                if (((A[i]<<4)|B[i])^sp[i])!=first: ok=False; break
            if ok:
                allowed.add((a,b)); kval[(a,b)]=first
    return (s0,s1),allowed,kval

def recover_k1_k0(data,b1_structs,limit=128,verbose=False):
    dom=[set(range(256)) if i in MAIN else {0} for i in range(16)]
    for obs,m in zip(b1_structs,MASKS): upd(dom,obs,m[0])
    constraints=[]; maps={}; pending=set(MAIN)
    while pending:
        pos=min(pending,key=lambda p: len(dom[ns(2*p)[0]])*len(dom[ns(2*p+1)[0]]))
        if verbose: print('[k1/k0] add pos',pos,'product',len(dom[ns(2*pos)[0]])*len(dom[ns(2*pos+1)[0]]), flush=True)
        (x,y),allow,kval=allowed_k1_k0_pos(data,b1_structs,pos,dom)
        if not allow: return []
        constraints.append((x,y,allow)); maps[pos]=((x,y),kval); pending.remove(pos)
        if not ac3(dom,constraints): return []
    sols=[]
    def rec(d):
        if len(sols)>=limit: return
        d=[set(s) for s in d]
        if not ac3(d,constraints): return
        if all(len(d[i])==1 for i in MAIN):
            k1=bytearray(16); k0=bytearray(16)
            for i in MAIN: k1[i]=next(iter(d[i]))
            for pos,((x,y),mp) in maps.items(): k0[pos]=mp[(k1[x],k1[y])]
            sols.append((bytes(k0),bytes(k1))); return
        v=min([i for i in MAIN if len(d[i])>1], key=lambda i: len(d[i]))
        for val in list(d[v]):
            nd=[set(s) for s in d]; nd[v]={val}; rec(nd)
            if len(sols)>=limit: return
    rec(dom)
    return sols

def brute_missing(k0,k1,k2,k3):
    kb=bytearray(k0)
    for a in range(256):
        kb[3]=a
        for b in range(256):
            kb[15]=b
            h=hashlib.sha512(bytes(kb)).digest()
            ok=True
            for r,kk in enumerate([k1,k2,k3]):
                ch=h[16*r:16*(r+1)]
                for i in MAIN:
                    if ch[i]!=kk[i]: ok=False; break
                if not ok: break
            if ok: return bytes(kb)
    return None

def solve_from_blocks(data, val_data=None, verbose=False):
    if val_data is None: val_data=[]
    k3s=solve_layer([cts for _,cts in data],2,1,limit=256,verbose=verbose,name='k3')
    for k3 in k3s:
        b2=[peel_b2(cts,k3) for _,cts in data]
        k2s=solve_layer(b2,1,0,limit=50000,verbose=verbose,name='k2')
        if verbose: print('[+] trying k2 candidates:', len(k2s), flush=True)
        for idx,k2 in enumerate(k2s):
            b1=[peel_b1(cts,k3,k2) for _,cts in data]
            val_b1=[peel_b1(cts,k3,k2) for _,cts in val_data]
            outs=recover_k1_k0(data+val_data,b1+val_b1,verbose=False)
            for k0,k1 in outs:
                full=brute_missing(k0,k1,k2,k3)
                if full:
                    keys=ks(full)
                    all_data=data+val_data
                    if all(enc_keys(keys,p)==c for pts,cts in all_data for p,c in zip(pts,cts)):
                        return full
    return None

def make_data_from_encrypt(encrypt_func, extra_blocks=184):
    base=os.urandom(16); data=[]; allpts=[]; counts=[]
    for st in SEL:
        pts=make_pts(base,st); data.append([pts,None]); allpts.extend(pts); counts.append(len(pts))
    val_pts=[os.urandom(16) for _ in range(extra_blocks)]
    allpts2=allpts+val_pts
    ct=encrypt_func(b''.join(allpts2))
    if len(ct)!=len(allpts2)*16: raise ValueError('bad ciphertext length')
    off=0
    for row,n in zip(data,counts):
        row[1]=[ct[16*(off+i):16*(off+i+1)] for i in range(n)]; off+=n
    val_cts=[ct[16*(off+i):16*(off+i+1)] for i in range(extra_blocks)]
    return [(pts,cts) for pts,cts in data], [(val_pts,val_cts)]

def selftest(trials=3):
    for t in range(trials):
        key=os.urandom(16); keys=ks(key)
        def enc(pt): return b''.join(enc_keys(keys,pt[i:i+16]) for i in range(0,len(pt),16))
        data,val_data=make_data_from_encrypt(enc)
        st=time.time(); rec=solve_from_blocks(data,val_data,verbose=(t==0)); dt=time.time()-st
        print('trial',t,'ok',rec==key,'time',round(dt,2),'rec',rec.hex() if rec else None,'true',key.hex(), flush=True)
        if rec!=key: return False
    return True

# robust remote tube
class Tube:
    def __init__(self, host, port, timeout=20):
        self.s = socket.create_connection((host, int(port)), timeout=timeout)
        self.s.settimeout(timeout)
        self.buf = b''

    def sendline(self, x):
        if isinstance(x, str):
            x = x.encode()
        self.s.sendall(x + b'\n')

    def recv_until(self, marker, timeout=20):
        self.s.settimeout(timeout)
        while marker not in self.buf:
            chunk = self.s.recv(4096)
            if not chunk:
                out, self.buf = self.buf, b''
                return out
            self.buf += chunk
        i = self.buf.index(marker) + len(marker)
        out, self.buf = self.buf[:i], self.buf[i:]
        return out

    def recv_all_available(self, timeout=3):
        self.s.settimeout(timeout)
        chunks = [self.buf]
        self.buf = b''
        while True:
            try:
                chunk = self.s.recv(4096)
                if not chunk:
                    break
                chunks.append(chunk)
            except socket.timeout:
                break
        return b''.join(chunks)


def remote(host, port):
    t = Tube(host, port, timeout=20)

    def encrypt(pt):
        t.recv_until(b'> ')
        t.sendline('1')
        t.recv_until(b'format:')
        t.sendline(pt.hex())
        out = t.recv_until(b'> ')
        m = re.search(rb'Here you go:\s*([0-9a-fA-F]+)', out)
        if not m:
            raise RuntimeError(out.decode(errors='replace'))
        return bytes.fromhex(m.group(1).decode())

    data, val_data = make_data_from_encrypt(encrypt)
    key = solve_from_blocks(data, val_data, verbose=True)
    if not key:
        raise RuntimeError('key not recovered')

    print('[+] recovered key:', key.hex(), flush=True)

    # Submit in the SAME connection. A new netcat/python connection has a new random key.
    t.sendline('3')
    prompt = t.recv_until(b'format:')
    if b'format:' not in prompt:
        print(prompt.decode(errors='replace'), end='', flush=True)
        raise RuntimeError('server did not ask for key')
    t.sendline(key.hex())
    out = t.recv_all_available(timeout=5)
    print(out.decode(errors='replace'), end='', flush=True)

if __name__=='__main__':
    if len(sys.argv)==1:
        selftest(2)
    elif sys.argv[1]=='remote':
        remote(sys.argv[2],sys.argv[3])
    else:
        selftest(int(sys.argv[1]))
