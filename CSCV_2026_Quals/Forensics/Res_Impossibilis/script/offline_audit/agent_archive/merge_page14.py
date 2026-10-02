from pathlib import Path
import json,sys,mmap,struct,zlib,ctypes
P=Path(__file__).resolve().parent;H=P.parent;sys.path.insert(0,str(H));from recover_archive_central import crypt;from verify_zip_evidence import INITIAL,TABLE,decrypt
raw=bytearray((P/'extensions_recovered_archive.zip').read_bytes());known=bytearray((P/'extensions_recovered_known.bin').read_bytes());other=(P/'small_derived_archive.zip').read_bytes();oknown=(P/'small_derived_known.bin').read_bytes()
for i,(b,k) in enumerate(zip(other,oknown)):
 if k:assert not known[i] or raw[i]==b;raw[i]=b;known[i]=1
with (H.parent/'evidence/mem.clean').open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as m:data=crypt(m[0x1d6f040:0x1d70040],57324)
assert len(data)==4096
for i,b in enumerate(data,57324):assert not known[i] or raw[i]==b;raw[i]=b;known[i]=1
records=json.loads((H/'archive_central_records.json').read_text());libc=ctypes.CDLL('libc.so.6');libc.srand(1788885121);rng=bytes(libc.rand()&255 for _ in range(429));derived_headers=[]
for i in (36,37):
 r=records[i];head=struct.pack('<4s5H3I2H',b'PK\x03\x04',20,1,0,0x6800,0x5521,int(r['crc32'],16),r['compressed_size'],r['plain_size'],len(r['name']),0)+r['name'].encode();a,b,c=INITIAL;enc=bytearray()
 for p in rng[i*11:i*11+11]+bytes([int(r['crc32'],16)>>24]):
  t=(c&65535)|2;enc.append(p^((t*(t^1)>>8)&255));a=(a>>8)^TABLE[(a^p)&255];b=((b+(a&255))*134775813+1)&0xffffffff;c=(c>>8)^TABLE[(c^(b>>24))&255]
 blob=head+enc;lo=r['local_offset']
 for j,v in enumerate(blob,lo):assert not known[j] or raw[j]==v;raw[j]=v;known[j]=1
 derived_headers.append({'index':i,'offset':lo,'length':len(blob),'source':'directory metadata, fixed observed writer fields, confirmed RNG header stream'})
verified=[]
for i,r in enumerate(records):
 o=r['local_offset'];h=struct.unpack_from('<4s5H3I2H',raw,o);assert h[0]==b'PK\x03\x04';s=o+30+h[9]+h[10];e=s+h[7]
 if all(known[o:e]):
  p=decrypt(raw[s:e])[12:];assert len(p)==h[8];assert zlib.crc32(p)==h[6];verified.append(i)
unknown=[];start=None
for i,v in enumerate(known+b'\1'):
 if not v and start is None:start=i
 if v and start is not None:unknown.append([start,i]);start=None
report={'known':sum(known),'total':len(raw),'unknown_intervals':unknown,'verified_members':verified,'new_page':{'memory':'0x1d6f040','logical':57324,'length':4096,'source':'MEGA AES-CTR decoded RAM'},'derived_headers':derived_headers};(P/'near_complete_archive.zip').write_bytes(raw);(P/'near_complete_known.bin').write_bytes(known);(P/'near_complete_report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
