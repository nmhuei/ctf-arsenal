from pathlib import Path
import json,struct
P=Path(__file__).resolve().parent
FIELDS=['frame','time','src','sport','dst','dport','seq','ack','flags','tcp_len','payload','hs_type','hs_version','hs_random','hs_suites','sni','alpn','supported_version']
packets=[]
for line in (P/'packets.tsv').read_text().splitlines():
 values=line.split('\t');values+=['']*(len(FIELDS)-len(values));row=dict(zip(FIELDS,values));row['frame']=int(row['frame']);row['seq']=int(row['seq']);row['flags']=int(row['flags'],16);row['tcp_len']=int(row['tcp_len']);row['data']=bytes.fromhex(row.pop('payload'));assert len(row['data'])==row['tcp_len'];row['direction']='client' if row['src']=='192.168.76.131' else 'server';packets.append(row)
assert {p['src'] for p in packets}=={'192.168.76.131','89.44.168.33'}
report={'stream':75,'pcap':'script/evidence/network.pcapng','packet_count':len(packets),'first_time':packets[0]['time'],'last_time':packets[-1]['time'],'directions':{},'tshark_handshakes':[{k:v for k,v in p.items() if k!='data'} for p in packets if p['hs_type']]}

def intervals(mask,wanted=0):
 out=[];start=None
 for i,b in enumerate(mask+bytes([1-wanted])):
  if b==wanted and start is None:start=i
  if b!=wanted and start is not None:out.append([start,i]);start=None
 return out

def parse_hello(data,server=False):
 version=data[:2].hex();random=data[2:34].hex();n=data[34];sid=data[35:35+n].hex();pos=35+n;out={'legacy_version':version,'random':random,'session_id':sid}
 if server:out['cipher_suite']=f'0x{int.from_bytes(data[pos:pos+2],"big"):04x}';out['compression']=data[pos+2];pos+=3
 else:
  n=int.from_bytes(data[pos:pos+2],'big');pos+=2;out['cipher_suites']=[f'0x{int.from_bytes(data[j:j+2],"big"):04x}' for j in range(pos,pos+n,2)];pos+=n;n=data[pos];pos+=1;out['compressions']=list(data[pos:pos+n]);pos+=n
 ex=[]
 if pos<len(data):
  length=int.from_bytes(data[pos:pos+2],'big');pos+=2;end=pos+length;assert end==len(data)
  while pos<end:
   typ,n=struct.unpack_from('>HH',data,pos);pos+=4;val=data[pos:pos+n];pos+=n;e={'type':typ,'length':n,'hex':val.hex()}
   if typ==0:
    q=2;names=[]
    while q<len(val):t=val[q];l=int.from_bytes(val[q+1:q+3],'big');q+=3;names.append(val[q:q+l].decode(errors='replace'));q+=l
    e['server_names']=names
   if typ==16:
    q=2;protocols=[]
    while q<len(val):l=val[q];q+=1;protocols.append(val[q:q+l].decode());q+=l
    e['alpn']=protocols
   if typ==43:e['supported_versions']=val.hex()
   ex.append(e)
 out['extensions']=ex;return out

for direction in ['client','server']:
 ps=[p for p in packets if p['direction']==direction];syn=[p for p in ps if p['flags']&2];assert syn,'No SYN anchor';base=(syn[0]['seq']+1)&0xffffffff;size=max(((p['seq']+(1 if p['flags']&2 else 0)-base)&0xffffffff)+len(p['data']) for p in ps if p['data']);assert size<10000000
 raw=bytearray(size);known=bytearray(size);overlap=0;conflicts=[];segments=[]
 for p in ps:
  if not p['data']:continue
  begin=(p['seq']+(1 if p['flags']&2 else 0)-base)&0xffffffff;end=begin+len(p['data']);segments.append({'frame':p['frame'],'offset':begin,'length':len(p['data']),'time':p['time']})
  for i,b in enumerate(p['data'],begin):
   if known[i]:
    overlap+=1
    if raw[i]!=b:conflicts.append({'frame':p['frame'],'offset':i,'previous':raw[i],'new':b})
   raw[i]=b;known[i]=1
 gaps=intervals(known);assert not conflicts;assert not gaps;(P/f'{direction}.bin').write_bytes(raw);records=[];pos=0;hs=bytearray();encrypted=False
 while pos<len(raw):
  assert pos+5<=len(raw);typ,version,n=struct.unpack_from('>BHH',raw,pos);assert typ in (20,21,22,23,24);assert pos+5+n<=len(raw);payload=raw[pos+5:pos+5+n];record={'index':len(records),'offset':pos,'content_type':typ,'legacy_version':f'0x{version:04x}','length':n,'payload_offset':pos+5,'end':pos+5+n,'after_ccs':encrypted};records.append(record)
  if typ==22 and not encrypted:hs+=payload
  if typ==20:encrypted=True
  pos+=5+n
 handshakes=[];q=0
 while q<len(hs):
  assert q+4<=len(hs);typ=hs[q];n=int.from_bytes(hs[q+1:q+4],'big');assert q+4+n<=len(hs);data=hs[q+4:q+4+n];item={'type':typ,'length':n}
  if typ in (1,2):item['hello']=parse_hello(data,typ==2)
  handshakes.append(item);q+=4+n
 dr={'size':size,'base_raw_sequence':base,'payload_packet_count':len(segments),'duplicate_payload_bytes':overlap,'conflicting_bytes':conflicts,'gaps':gaps,'segments':segments,'tls_records':records,'handshakes':handshakes};report['directions'][direction]=dr
 (P/f'{direction}_records.json').write_text(json.dumps(records,indent=2))
(P/'metadata.json').write_text(json.dumps(report,indent=2));print(json.dumps({'packets':len(packets),'directions':{d:{'size':r['size'],'duplicate_payload_bytes':r['duplicate_payload_bytes'],'records':len(r['tls_records']),'handshakes':r['handshakes']} for d,r in report['directions'].items()}},indent=2))
