from pathlib import Path
from Crypto.Hash import keccak
MASK=(1<<256)-1

def mextend(mem, n):
    if len(mem)<n: mem.extend(b'\x00'*(n-len(mem)))
def mload(mem, off):
    mextend(mem, off+32); return int.from_bytes(mem[off:off+32],'big')
def mstore(mem, off, val):
    mextend(mem, off+32); mem[off:off+32]=(val&MASK).to_bytes(32,'big')
def mstore8(mem, off, val):
    mextend(mem, off+1); mem[off]=val&0xff

def calldataload(data, off):
    chunk=data[off:off+32]+b'\x00'*max(0, off+32-len(data))
    return int.from_bytes(chunk[:32],'big')

def run(code, calldata, max_steps=10000000, trace=False):
    pc=0; st=[]; mem=bytearray(); steps=0; handler_base=None
    jumps=[]; ret=None
    while steps<max_steps:
        if pc<0 or pc>=len(code): raise Exception(('pc_oob',pc))
        op=code[pc]; oldpc=pc; pc+=1; steps+=1
        if 0x60<=op<=0x7f:
            n=op-0x5f; st.append(int.from_bytes(code[pc:pc+n],'big')); pc+=n; continue
        if op==0x5f: st.append(0); continue
        if 0x80<=op<=0x8f: st.append(st[-(op-0x7f)]); continue
        if 0x90<=op<=0x9f:
            n=op-0x8f; st[-1],st[-1-n]=st[-1-n],st[-1]; continue
        def pop():
            if not st: raise Exception(('underflow',oldpc,op))
            return st.pop()
        if op==0x00: break
        elif op==0x5b: pass
        elif op==0x01: a=pop(); b=pop(); st.append((a+b)&MASK)
        elif op==0x02: a=pop(); b=pop(); st.append((a*b)&MASK)
        elif op==0x03: a=pop(); b=pop(); st.append((a-b)&MASK)
        elif op==0x04: a=pop(); b=pop(); st.append(0 if b==0 else a//b)
        elif op==0x06: a=pop(); b=pop(); st.append(0 if b==0 else a%b)
        elif op==0x10: a=pop(); b=pop(); st.append(1 if a<b else 0)
        elif op==0x11: a=pop(); b=pop(); st.append(1 if a>b else 0)
        elif op==0x14: a=pop(); b=pop(); st.append(1 if a==b else 0)
        elif op==0x15: a=pop(); st.append(1 if a==0 else 0)
        elif op==0x16: a=pop(); b=pop(); st.append(a&b)
        elif op==0x17: a=pop(); b=pop(); st.append(a|b)
        elif op==0x18: a=pop(); b=pop(); st.append(a^b)
        elif op==0x19: a=pop(); st.append((~a)&MASK)
        elif op==0x1a: i=pop(); x=pop(); st.append(0 if i>=32 else (x>>(8*(31-i)))&0xff)
        elif op==0x1b: sh=pop(); x=pop(); st.append(0 if sh>=256 else (x<<sh)&MASK)
        elif op==0x1c: sh=pop(); x=pop(); st.append(0 if sh>=256 else x>>sh)
        elif op==0x1d:
            sh=pop(); x=pop()
            if sh>=256: st.append(MASK if (x>>255)&1 else 0)
            else:
                if (x>>255)&1: st.append(((x>>sh) | (MASK << (256-sh))) & MASK)
                else: st.append(x>>sh)
        elif op==0x20:
            off=pop(); size=pop(); mextend(mem, off+size); k=keccak.new(digest_bits=256); k.update(bytes(mem[off:off+size])); st.append(int.from_bytes(k.digest(),'big'))
        elif op in (0x30,0x32,0x34): st.append(0)
        elif op==0x33: st.append(0xc0de)
        elif op==0x3d: st.append(0)
        elif op==0x46: st.append(1)
        elif op==0x35: off=pop(); st.append(calldataload(calldata, off))
        elif op==0x36: st.append(len(calldata))
        elif op==0x38: st.append(len(code))
        elif op==0x39:
            dest=pop(); off=pop(); size=pop(); mextend(mem,dest+size); mem[dest:dest+size]=code[off:off+size]+b'\x00'*max(0, off+size-len(code))
        elif op==0x50: pop()
        elif op==0x51: off=pop(); st.append(mload(mem,off))
        elif op==0x52: off=pop(); val=pop(); mstore(mem,off,val)
        elif op==0x53: off=pop(); val=pop(); mstore8(mem,off,val)
        elif op==0x56:
            dest=pop(); jumps.append((oldpc,dest));
            if trace and len(jumps)<2000: print('JUMP',hex(oldpc),'->',hex(dest),'top', [hex(x) for x in st[-5:]])
            pc=dest
        elif op==0x57:
            dest=pop(); cond=pop();
            if cond:
                jumps.append((oldpc,dest));
                if trace and len(jumps)<2000: print('JUMPI',hex(oldpc),'->',hex(dest),'cond',hex(cond),'top',[hex(x) for x in st[-5:]])
                pc=dest
        elif op==0x58: st.append(oldpc)
        elif op==0x59: st.append(len(mem))
        elif op==0xf3:
            off=pop(); size=pop(); mextend(mem,off+size); ret=bytes(mem[off:off+size]); break
        elif op==0xfd:
            print('REVERT at',hex(oldpc),'steps',steps,'last jumps',[(hex(a),hex(b)) for a,b in jumps[-20:]],'stack',[hex(x) for x in st[-10:]])
            raise Exception(('REVERT',oldpc))
        else:
            raise Exception(('unknown',hex(op),hex(oldpc),steps,len(st)))
    return ret,steps,jumps,mem,st,pc

if __name__=='__main__':
 import sys
 idx=int(sys.argv[1]) if len(sys.argv)>1 else 1
 pt=bytes.fromhex(sys.argv[2]) if len(sys.argv)>2 else b'\x00'*16
 code=Path(f'challenge_{idx}.dec').read_bytes()
 calldata=b'\x00'*20+pt
 ret,steps,jumps,mem,st,pc=run(code,calldata,max_steps=50000000,trace='--trace' in sys.argv)
 print('steps',steps,'pc',hex(pc),'ret',ret.hex() if ret else None,'jumps',len(jumps),'mem',len(mem),'stack',len(st))
 print('first jumps', [(hex(a),hex(b)) for a,b in jumps[:20]])
 print('last jumps', [(hex(a),hex(b)) for a,b in jumps[-20:]])
