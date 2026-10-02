import kernel_walk as k,struct,json,subprocess,re
from pathlib import Path
OUT=Path('script/offline_audit/agent_collector');terms=[b'firefox\0',b'firefox-bin\0',b'Web Content\0',b'Socket Process\0',b'Privileged Cont',b'coccoc\0',b'bash\0',b'python3\0',b'gnome-shell\0',b'bing@search.mozilla.org','bing@search.mozilla.org'.encode('utf-16le'),b'mozLz40\0']
pat='|'.join(''.join('\\x%02x'%c for c in t) for t in terms)
p=subprocess.run(['rg','-aob','--no-unicode',pat,'script/evidence/mem.clean'],capture_output=True)
rows=[];tasks=[];bing=[];lz=[]
for l in p.stdout.splitlines():
 if b':' not in l:continue
 fo,b=l.split(b':',1);fo=int(fo);term=next((x for x in terms if b==x),None)
 if term is None:continue
 row={'file':hex(fo),'term':term.decode(errors='replace')};rows.append(row)
 if b'bing@' in term or term.startswith(b'b\0i\0n\0g'):
  start=max(0,fo-256);end=fo+1600;context=bytes(k.m[start:end]);out=OUT/f'bing_context_{fo:x}.bin';out.write_bytes(context)
  guids=re.findall(rb'\{?[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\}?',context)
  bing.append({**row,'context_file':str(out),'guids':[g.decode() for g in guids],'context':context.decode(errors='replace')})
 elif term==b'mozLz40\0':lz.append(row)
 else:
  q1,q2=struct.unpack_from('<2Q',k.m,fo-16)
  if q1==q2 and k.DM<=q1<k.DM+0x240000000:
   cf=k.p2f(q1-k.DM);row.update(cred=hex(q1),cred_data=k.m[cf:cf+64].hex() if cf else None,context=k.m[fo-96:fo+96].hex());tasks.append(row)
(OUT/'runtime_specific_hits.json').write_text(json.dumps(rows,indent=2));(OUT/'runtime_task_candidates.json').write_text(json.dumps(tasks,indent=2));(OUT/'bing_contexts.json').write_text(json.dumps(bing,indent=2));(OUT/'moz_lz4_hits.json').write_text(json.dumps(lz,indent=2));
from collections import Counter
print('rawcounts',Counter(r['term'] for r in rows));print('task_candidates',tasks);print('bingcount',len(bing),'guidlists',[(r['file'],r['guids']) for r in bing]);print('mozlz4count',len(lz))
