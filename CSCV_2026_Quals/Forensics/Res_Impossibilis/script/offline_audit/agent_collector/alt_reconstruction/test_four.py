import json,zlib,ctypes,time
from pathlib import Path
OUT=Path('script/offline_audit/agent_collector/alt_reconstruction');suffix=Path('script/offline_audit/root_files/37_AlternateServices.partial.txt').read_bytes();hypos=json.loads((OUT/'record_hypotheses4.json').read_text());lib=ctypes.CDLL(str(OUT.resolve()/'zip_state.so'));lib.setup();lib.verify.argtypes=[ctypes.c_char_p,ctypes.c_size_t];crc_hits=[];found=[];start=time.time();pairs=0;implicit=0

def line(row,ex):
 h=row['host'];a=row['attr'];return f'https:{h}:443:.:{a}:3\t0\t20704\thttps:{h}:443:{h}:443::n:{ex}:h3:y:1788840424:n:{a}:|n:y:\n'.encode()
def epochs(host):
 base=1788926800 if 'mozilla' in host or 'facebook' in host or 'transcend' in host else 1791432400
 return list(range(base+20,base+226))
for i,h in enumerate(hypos):
 rows=h['records'];es=[epochs(r['host']) for r in rows];records=[[line(r,e) for e in values] for r,values in zip(rows,es)];base=[x[0] for x in records];lasts=[j for j,e in enumerate(es[-1]) if e%100==42]
 for ilast in lasts:
  last=records[-1][ilast];assert last[-66:]==suffix[:66];prefix=b''.join(base[:-1])+last[:-66];assert len(prefix)==681
  baseline=prefix+suffix;crc=zlib.crc32(baseline);deltas=[]
  for rno in range(3):
   ds=[]
   for candidate in records[rno]:
    parts=base[:-1].copy();parts[rno]=candidate;b=b''.join(parts)+last[:-66]+suffix;ds.append(zlib.crc32(b)^crc)
   deltas.append(ds)
  # CRC32 is affine; independently check a combined change before searching.
  test=b''.join(records[j][j+1] for j in range(3))+last[:-66]+suffix
  assert zlib.crc32(test)==crc^deltas[0][1]^deltas[1][2]^deltas[2][3]
  back={d:j for j,d in enumerate(deltas[2])};target=crc^0x25489b76
  for j,d1 in enumerate(deltas[0]):
   t=target^d1
   for l,d2 in enumerate(deltas[1]):
    k=back.get(t^d2)
    if k is None:continue
    p=records[0][j]+records[1][l]+records[2][k]+last[:-66];b=p+suffix;assert zlib.crc32(b)==0x25489b76
    okay=bool(lib.verify(p,681));ex=[es[0][j],es[1][l],es[2][k],es[-1][ilast]];crc_hits.append({'hypothesis':i,'epochs':ex,'state_match':okay,'prefix':p.decode()})
    if okay:(OUT/'AlternateServices.txt').write_bytes(b);found.append({'hypothesis':i,'epochs':ex})
  pairs+=len(es[0])*len(es[1]);implicit+=len(es[0])*len(es[1])*len(es[2])
 if i%50==0:print('hypothesis',i,'pairs',pairs,'crc_hits',len(crc_hits),'elapsed',round(time.time()-start,2),flush=True)
(OUT/'test_four_result.json').write_text(json.dumps({'hypotheses':len(hypos),'pair_checks':pairs,'bounded_epoch_combinations':implicit,'elapsed':time.time()-start,'crc_hits':crc_hits,'verified':found,'method':'CRC32 affine combination of three independently bounded10digitexpiryfields; all hits checked against full96-bitZIPstateatplaintext681. No arbitrary byte patches.'},indent=2));print('verified',found,'CRC-only',len(crc_hits),'elapsed',time.time()-start)
