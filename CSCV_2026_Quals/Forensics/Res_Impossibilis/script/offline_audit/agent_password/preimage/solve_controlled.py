#!/usr/bin/env python3
"""Alternative exact model with q_i=low8(X_i) controls."""
from pathlib import Path
import json,time,sys,random
import z3
from solve_printable import INITIAL,TARGET,A,crc_numeric,numeric
HERE=Path(__file__).resolve().parent
TABLE=[crc_numeric(0,i)for i in range(256)]
INV={v&255:i for i,v in enumerate(TABLE)}
assert len(INV)==256

def linear(v,basis,bits):
    out=z3.BitVecVal(0,bits)
    for i,b in enumerate(basis):
        out=out^z3.If(z3.Extract(i,i,v)==1,z3.BitVecVal(b,bits),z3.BitVecVal(0,bits))
    return out

def build(n,limit,target=TARGET,pinned=None):
    s=z3.SolverFor('QF_BV');s.set(timeout=limit,random_seed=29)
    q=[z3.BitVec(f'q{i}',8)for i in range(n)]
    states=[tuple(z3.BitVec(f'{v}{i}',32)for v in 'xyz')for i in range(n+1)]
    s.add(*[a==b for a,b in zip(states[0],INITIAL)]);password=[]
    for i,u in enumerate(q):
        x,y,z=states[i];nx,ny,nz=states[i+1]
        t=linear(u^z3.Extract(15,8,x),[INV[1<<j]for j in range(8)],8)
        p=z3.Extract(7,0,x)^t;password.append(p)
        s.add(z3.UGE(p,32),z3.ULE(p,126))
        if pinned is not None:s.add(p==pinned[i])
        s.add(nx==z3.LShR(x,8)^linear(t,[TABLE[1<<j]for j in range(8)],32))
        s.add(ny==(y+z3.ZeroExt(24,u))*A+1)
        zb=z3.Extract(7,0,z)^z3.Extract(31,24,ny)
        s.add(nz==z3.LShR(z,8)^linear(zb,[TABLE[1<<j]for j in range(8)],32))
    s.add(*[a==b for a,b in zip(states[-1],target)])
    return s,password

if __name__=='__main__':
    rng=random.Random(1703)
    for _ in range(100):
        x=rng.getrandbits(32);q=rng.randrange(256);t=INV[q^((x>>8)&255)];p=(x&255)^t
        nx=(x>>8)^TABLE[t]
        assert nx&255==q and nx==crc_numeric(x,p)
        assert z3.simplify(linear(z3.BitVecVal(q,8),[INV[1<<j]for j in range(8)],8)).as_long()==INV[q]
    fixed=b'Controlled-Model!';s,_=build(len(fixed),5000,numeric(fixed),fixed);assert s.check()==z3.sat
    wrong=list(numeric(fixed));wrong[1]^=1;s,_=build(len(fixed),5000,wrong,fixed);assert s.check()==z3.unsat
    n=int(sys.argv[1]);limit=int(sys.argv[2]);s,p=build(n,limit)
    (HERE/f'controlled{n}.smt2').write_text(s.to_smt2());start=time.monotonic();status=s.check()
    report={'length':n,'alphabet':'ASCII32..126','parameterization':'q_i=low8(X_i)','timeout_ms':limit,'status':str(status),'elapsed_seconds':time.monotonic()-start,'controls':{'random_reconstruction_cases':100,'pinned_sat':True,'wrong_target_unsat':True},'equivalent_only':True}
    if status==z3.sat:
        m=s.model();pw=bytes(m.eval(x).as_long()for x in p);assert numeric(pw)==TARGET
        report.update(password_hex=pw.hex(),password_ascii=pw.decode('ascii'),independent_state=[f'{x:08x}'for x in numeric(pw)])
        (HERE/f'controlled{n}.password.bin').write_bytes(pw)
    elif status==z3.unknown:report['reason_unknown']=s.reason_unknown()
    report['statistics']=str(s.statistics());(HERE/f'controlled{n}.result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
