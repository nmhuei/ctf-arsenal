#!/usr/bin/env python3
"""Bounded mathematical ZIPCrypto preimage construction, not original recovery."""
from pathlib import Path
import sys,json,time,random,zlib
import z3
HERE=Path(__file__).resolve().parent
INITIAL=(0x12345678,0x23456789,0x34567890)
TARGET=(0x670e8462,0x306591b4,0x8372919d)
A=0x08088405;MASK=0xffffffff

def crc_numeric(v,b):
    v^=b
    for _ in range(8):v=(v>>1)^((-(v&1))&0xedb88320)
    return v

def numeric(p,initial=INITIAL):
    x,y,z=initial
    for c in p:
        x=crc_numeric(x,c);y=((y+(x&255))*A+1)&MASK;z=crc_numeric(z,y>>24)
    return x,y,z

def crc_symbolic(v,b):
    v=v^z3.ZeroExt(24,b)
    for _ in range(8):v=z3.LShR(v,1)^((-(v&1))&0xedb88320)
    return v

def build(length,timeout,target=TARGET,pinned=None):
    solver=z3.SolverFor('QF_BV');solver.set(timeout=timeout,random_seed=17)
    p=[z3.BitVec(f'p{i}',8)for i in range(length)]
    states=[tuple(z3.BitVec(f'{a}{i}',32)for a in 'xyz')for i in range(length+1)]
    solver.add(*[a==b for a,b in zip(states[0],INITIAL)])
    for i,c in enumerate(p):
        solver.add(z3.UGE(c,32),z3.ULE(c,126))
        if pinned is not None:solver.add(c==pinned[i])
        x,y,z=states[i];nx,ny,nz=states[i+1]
        solver.add(nx==crc_symbolic(x,c),ny==(y+z3.ZeroExt(24,z3.Extract(7,0,nx)))*A+1,nz==crc_symbolic(z,z3.Extract(31,24,ny)))
    solver.add(*[a==b for a,b in zip(states[-1],target)])
    return solver,p

def controls():
    rng=random.Random(20260925)
    for _ in range(100):
        v=rng.getrandbits(32);b=rng.randrange(256)
        assert z3.simplify(crc_symbolic(z3.BitVecVal(v,32),z3.BitVecVal(b,8))).as_long()==crc_numeric(v,b)
        assert crc_numeric(v,b)==(zlib.crc32(bytes([b]),v^MASK)^MASK)
    p=b'Printable-Control!';s,_=build(len(p),5000,numeric(p),p)
    assert s.check()==z3.sat
    bad=list(numeric(p));bad[2]^=1;s,_=build(len(p),5000,bad,p)
    assert s.check()==z3.unsat
    return {'crc_cases':100,'pinned_password_sat':True,'wrong_target_unsat':True}

if __name__=='__main__':
    length=int(sys.argv[1]);limit=int(sys.argv[2]);control=controls()
    s,p=build(length,limit);(HERE/f'length{length}.smt2').write_text(s.to_smt2())
    began=time.monotonic();status=s.check();elapsed=time.monotonic()-began
    result={'length':length,'alphabet':'ASCII32..126','timeout_ms':limit,'solver_version':z3.get_version_string(),'controls':control,'status':str(status),'elapsed_seconds':elapsed,'target':[f'{x:08x}'for x in TARGET],'equivalent_only':True}
    if status==z3.sat:
        model=s.model();password=bytes(model.eval(c).as_long()for c in p);state=numeric(password)
        assert state==TARGET
        result.update(password_hex=password.hex(),password_ascii=password.decode('ascii'),independently_verified_state=[f'{x:08x}'for x in state])
        (HERE/f'length{length}.password.bin').write_bytes(password)
    elif status==z3.unknown:result['reason_unknown']=s.reason_unknown()
    result['statistics']=str(s.statistics());(HERE/f'length{length}.result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
