import json
from pathlib import Path
import solve_set_oracle_v3_fixed as s

b=s.load_base(Path('solve_checked.py'))


def nested_json(v,n):
    for _ in range(n):
        v=json.dumps(v,ensure_ascii=False,separators=(',',':'))
    return v


def add_raw(typ,n,kind):
    if typ=='impl': prefix='flatten|implode|'
    elif typ=='flat': prefix='flatten|'
    else: prefix=''
    suffix=prefix+'tojson|'*n+'explode|'+('unique|add' if kind=='uniq' else 'add')
    def ev(i,c,typ=typ,n=n,kind=kind):
        if typ=='impl': v=''.join(chr(x) for x in ([i] if c is None else [i,c]))
        elif typ=='flat': v=[i] if c is None else [i,c]
        else: v=[[i]] if c is None else [[i],c]
        v=nested_json(v,n)
        xs=list(map(ord,v))
        return sum(set(xs)) if kind=='uniq' else sum(xs)
    b.FEATURES.append(b.Feature(f'x_{typ}_{n}_{kind}',suffix,ev))

for n in range(0,31):
    for kind in ('add','uniq'): add_raw('impl',n,kind)
for typ in ('flat','rec'):
    for n in range(1,21):
        for kind in ('add','uniq'): add_raw(typ,n,kind)

prefix='jail{'; suffix='}'
body=('a1_b2_c3_d4_e5_f6_g7_h8_i9_j0_k1_l2_m3_n4_o5_p6_q7_r8_s9_'
      't0_u1_v2_w3_x4_y5_z6_hello_world_this_is_a_super_long_flag_for_123')
flag=prefix+body[:122-len(prefix)-len(suffix)]+suffix
charset=b.DEFAULT_CHARSET
chains=s.unique_chains(Path('chains_225.json'))
vals=s.build_value_universe(b,122,charset,len(b.FEATURES))
accepts=s.accept_sets_by_jq('jq',chains,vals)
obs=[]; q=0
for fi,f in enumerate(b.FEATURES):
  for rev in (False,True):
    allvals={f.evaluate(121,None)}
    actual={f.evaluate(121,None)}
    for pos in range(122):
      idx=121-pos if rev else pos
      for c in b.fixed_domain(pos,122,charset): allvals.add(f.evaluate(idx,c))
      actual.add(f.evaluate(idx,ord(flag[pos])))
    nuisance=f.evaluate(121,None)
    for acc in accepts:
      inter=allvals & acc
      if not inter or inter==allvals: continue
      q+=1
      obs.append(s.SetObservation(fi,rev,frozenset(acc),nuisance in acc,bool(actual & acc)))
print('features',len(b.FEATURES),'simulated_queries',q,'observations',len(obs))
d=s.domains_from_obs(b,122,charset,obs)
c=s.constraints_from_obs(b,122,obs,d)
print('domain size',sum(map(len,d.values())),'ambiguous',sum(len(x)>1 for x in d.values()),'constraints',len(c))
sol=s.solve_constraints_z3(122,d,c,limit=3)
print('solutions',sol)
print('truth in first',flag in sol)
