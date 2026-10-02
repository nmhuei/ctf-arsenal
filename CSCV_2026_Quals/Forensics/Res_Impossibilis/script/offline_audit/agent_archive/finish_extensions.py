from pathlib import Path
import sys,json,zlib,mmap,struct
P=Path(__file__).resolve().parent;H=P.parent;sys.path.insert(0,str(H));from recover_archive_central import crypt;from verify_zip_evidence import INITIAL,TABLE,decrypt
raw=bytearray((P/'pte_archive.zip').read_bytes());known=bytearray((P/'pte_known.bin').read_bytes());pages=[]
with (H.parent/'evidence/mem.clean').open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as m:
 for fo,lo in [(0x1592040,45036),(0x2abe040,40940)]:
  data=crypt(m[fo:fo+4096],lo);assert all(not known[i] or raw[i]==v for i,v in enumerate(data,lo));raw[lo:lo+4096]=data;known[lo:lo+4096]=b'\x01'*4096;pages.append({'memory':hex(fo),'logical':lo})
def update(s,p):
 a,b,c=s;a=(a>>8)^TABLE[(a^p)&255];b=((b+(a&255))*134775813+1)&0xffffffff;c=(c>>8)^TABLE[(c^(b>>24))&255];return a,b,c
def kb(s):
 t=(s[2]&65535)|2;return((t*(t^1))>>8)&255
state=(0x8e9c88b6,0xa4ea559b,0xa6fbb0aa);out=bytearray()
for c in raw[49093:49132]:
 p=c^kb(state);out.append(p);state=update(state,p)
assert state==(0x20d4d4db,0x4d3336ef,0x18c00cf1);assert out[36:]==b'}",';uuid=out[:36];print('BingGUID',uuid.decode(),flush=True)
plain=(P/'extensions_template.json').read_bytes().replace(b'00000000-0000-0000-0000-000000000000',uuid);assert len(plain)==37583;assert zlib.crc32(plain)==0x20a2f078;json.loads(plain)
start=13855;header=decrypt(raw[start:start+12]);state=INITIAL;enc=bytearray()
for p in header+plain:enc.append(p^kb(state));state=update(state,p)
assert all(not known[i] or raw[i]==v for i,v in enumerate(enc,start));observed=sum(known[start:start+len(enc)]);raw[start:start+len(enc)]=enc;known[start:start+len(enc)]=b'\x01'*len(enc)
(P/'27_extensions.json').write_bytes(plain);(P/'extensions_recovered_archive.zip').write_bytes(raw);(P/'extensions_recovered_known.bin').write_bytes(known);report={'bing_guid':uuid.decode(),'length':len(plain),'crc32':hex(zlib.crc32(plain)),'verified':True,'matched_observed_zip_cipher_bytes':observed,'new_memory_pages':pages,'known_archive_bytes':sum(known)};(P/'extensions_final_report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
