from pathlib import Path
import json,struct,sys,mmap
P=Path(__file__).resolve().parent;H=P.parent;sys.path.insert(0,str(H));from verify_zip_evidence import decrypt
r=json.loads((H/'archive_central_records.json').read_text());raw=bytearray((P/'merged_archive.zip').read_bytes());known=bytearray((P/'merged_known.bin').read_bytes());rows=json.loads((P/'pte_results.json').read_text());ref=next(x for x in rows if x['target']=='0x20de1d000');pages=[]
with (H.parent/'evidence/mem.clean').open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as m:
 for e in ref['neighbors']:
  i=e['i']
  if not 1<=i<=5:continue
  fo=int(e['file'],16);lo=12240+i*4096;length=2848 if i==5 else 4096;hi=lo+length;data=m[fo:fo+length];assert all(not known[j] or raw[j]==v for j,v in enumerate(data,lo));raw[lo:hi]=data;known[lo:hi]=b'\x01'*length;pages.append({'logical':lo,'memory':e['file'],'pte':e['pte'],'source':'consecutive_page_table_mapping'})
x=r[27];start=x['local_offset']+30+len(x['name']);end=start
while end<len(known) and known[end]:end+=1
plain=decrypt(raw[start:end])[12:];decoded=plain.decode('utf-8');assert decoded.startswith('{"schemaVersion":33,');(P/'27_extensions.partial.json').write_bytes(plain);(P/'pte_archive.zip').write_bytes(raw);(P/'pte_known.bin').write_bytes(known)
report={'known':sum(known),'new_pages':pages,'extensions_prefix_bytes':len(plain),'utf8_valid':True,'extensions_complete':False,'crc_verified':False,'tail':decoded[-180:]};(P/'pte_merge_report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
