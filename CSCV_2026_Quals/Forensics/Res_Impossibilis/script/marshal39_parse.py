#!/usr/bin/env python3
import struct
from pathlib import Path

class Ref:
    def __init__(self,i): self.i=i
    def __repr__(self): return f'Ref({self.i})'
class Code:
    def __init__(self,**kw): self.__dict__.update(kw)
    def __repr__(self): return f"Code(name={self.name!r}, firstlineno={self.firstlineno}, consts={len(self.consts) if isinstance(self.consts,(tuple,list)) else self.consts!r})"
class P:
    def __init__(self,b,base=0):self.b=b;self.p=0;self.base=base
    def need(self,n):
        if self.p+n>len(self.b): raise EOFError((self.base+self.p,n))
    def u8(self):self.need(1);x=self.b[self.p];self.p+=1;return x
    def i32(self):self.need(4);x=struct.unpack_from('<i',self.b,self.p)[0];self.p+=4;return x
    def u32(self):self.need(4);x=struct.unpack_from('<I',self.b,self.p)[0];self.p+=4;return x
    def i64(self):self.need(8);x=struct.unpack_from('<q',self.b,self.p)[0];self.p+=8;return x
    def raw(self,n):self.need(n);x=self.b[self.p:self.p+n];self.p+=n;return x
    def obj(self,depth=0):
        if depth>100: raise ValueError('depth')
        at=self.p; tb=self.u8(); flag=bool(tb&0x80); t=chr(tb&0x7f)
        if t=='0': return ('NULL',)
        if t=='N': return None
        if t=='F': return False
        if t=='T': return True
        if t=='S': return StopIteration
        if t=='.': return Ellipsis
        if t=='i': return self.i32()
        if t=='I': return self.i64()
        if t=='l':
            n=self.i32(); sign=-1 if n<0 else 1; n=abs(n); v=0
            for j in range(n):
                d=struct.unpack('<H',self.raw(2))[0]; v += d << (15*j)
            return sign*v
        if t=='f':
            n=self.u8(); return float(self.raw(n).decode('ascii'))
        if t=='g': return struct.unpack('<d',self.raw(8))[0]
        if t=='x':
            n1=self.u8();a=float(self.raw(n1).decode());n2=self.u8();b=float(self.raw(n2).decode());return complex(a,b)
        if t=='y': return complex(*struct.unpack('<dd',self.raw(16)))
        if t=='s':
            n=self.i32(); return self.raw(n)
        if t in 'tuaA':
            n=self.i32(); return self.raw(n).decode('utf-8','replace')
        if t in 'zZ':
            n=self.u8(); return self.raw(n).decode('utf-8','replace')
        if t=='r': return Ref(self.i32())
        if t=='(':
            n=self.i32(); return tuple(self.obj(depth+1) for _ in range(n))
        if t==')':
            n=self.u8(); return tuple(self.obj(depth+1) for _ in range(n))
        if t=='[':
            n=self.i32(); return [self.obj(depth+1) for _ in range(n)]
        if t=='{':
            d=[]
            while True:
                k=self.obj(depth+1)
                if k==('NULL',): break
                v=self.obj(depth+1);d.append((k,v))
            return dict(d)
        if t in '<>':
            n=self.i32(); vals=[self.obj(depth+1) for _ in range(n)]; return (set(vals) if t=='<' else frozenset(vals))
        if t=='c':
            vals=[self.i32() for _ in range(6)]
            code=self.obj(depth+1); consts=self.obj(depth+1); names=self.obj(depth+1); varnames=self.obj(depth+1); freevars=self.obj(depth+1); cellvars=self.obj(depth+1); filename=self.obj(depth+1); name=self.obj(depth+1); firstlineno=self.i32(); lnotab=self.obj(depth+1)
            return Code(argcount=vals[0],posonly=vals[1],kwonly=vals[2],nlocals=vals[3],stack=vals[4],flags=vals[5],code=code,consts=consts,names=names,varnames=varnames,freevars=freevars,cellvars=cellvars,filename=filename,name=name,firstlineno=firstlineno,lnotab=lnotab,start=self.base+at,end=self.base+self.p)
        raise ValueError(f'unknown type {t!r} byte={tb:02x} at {self.base+at:#x}')

def short(v,limit=260):
    if isinstance(v,bytes):
        if len(v)>80:return f'bytes[{len(v)}] {v[:32].hex()}...'
        return repr(v)
    if isinstance(v,Code): return repr(v)
    s=repr(v)
    return s if len(s)<=limit else s[:limit]+'...'

if __name__=='__main__':
    path=Path('script/evidence/mem.clean')
    lo=0x7e64000; hi=0x7e66510
    with path.open('rb') as f:f.seek(lo);buf=f.read(hi-lo)
    for rel,b in enumerate(buf):
        if (b&0x7f)!=ord('c'): continue
        p=P(buf[rel:],lo+rel)
        try:
            o=p.obj()
        except Exception: continue
        if isinstance(o,Code) and o.end<=hi and ('synthesize' in str(o.name) or o.end==hi):
            print('CANDIDATE',hex(o.start),hex(o.end),o)
            print(' fields',o.argcount,o.posonly,o.kwonly,o.nlocals,o.stack,hex(o.flags))
            print(' name',o.name,'filename',o.filename,'varnames',o.varnames)
            print(' consts type',type(o.consts).__name__,'len',len(o.consts) if isinstance(o.consts,(tuple,list)) else None)
            if isinstance(o.consts,(tuple,list)):
                for i,c in enumerate(o.consts):print(f' CONST[{i:02}]',short(c))
