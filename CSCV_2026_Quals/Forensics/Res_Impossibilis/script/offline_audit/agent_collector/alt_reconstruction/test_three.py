import json,zlib,ctypes,time
from pathlib import Path
OUT=Path('script/offline_audit/agent_collector/alt_reconstruction');suffix=Path('script/offline_audit/root_files/37_AlternateServices.partial.txt').read_bytes();hypos=json.loads((OUT/'record_hypotheses.json').read_text());lib=ctypes.CDLL(str(OUT.resolve()/'zip_state.so'));lib.setup();lib.verify.argtypes=[ctypes.c_char_p,ctypes.c_size_t];tested=0;crc_hits=[];found=[];start=time.time()
def line(row,ex):
 host=row['host'];a=row['attr'];return f'https:{host}:443:.:{a}:3\t0\t20704\thttps:{host}:443:{host}:443::n:{ex}:h3:y:1788840424:n:{a}:|n:y:\n'.encode()
def epochs(host):
 base=1788926800 if 'mozilla' in host or 'facebook' in host or 'transcend' in host else 1791432400
 return range(base+20,base+226)
for i,h in enumerate(hypos):
 r1,r2,r3=h['records'];a=[line(r1,e) for e in epochs(r1['host'])];b=[line(r2,e) for e in epochs(r2['host'])];es=[e for e in epochs(r3['host']) if e%100==42]
 for e3 in es:
  last=line(r3,e3)[:-66];assert line(r3,e3)[-66:]==suffix[:66]
  for x in a:
   for y in b:
    prefix=x+y+last;assert len(prefix)==681;tested+=1
    if zlib.crc32(suffix,zlib.crc32(prefix))!=0x25489b76:continue
    okay=bool(lib.verify(prefix,len(prefix)));crc_hits.append({'hypothesis':i,'expiry3':e3,'state_match':okay,'prefix':prefix.decode()})
    if okay:
     blob=prefix+suffix;(OUT/'AlternateServices.txt').write_bytes(blob);found.append(i)
 print('hypothesis',i,'tested',tested,'elapsed',round(time.time()-start,2),flush=True)
(OUT/'test_three_result.json').write_text(json.dumps({'tested':tested,'elapsed':time.time()-start,'crc_hits':crc_hits,'verified':found,'limits':'Hostname keys from observed DNS/recoveredrecords and8namedMozillaGooglehypotheses; expiry206secondrangesderivedfromobservedTTLfamilies.'},indent=2));print('verified',found,'crc_only',len(crc_hits))
