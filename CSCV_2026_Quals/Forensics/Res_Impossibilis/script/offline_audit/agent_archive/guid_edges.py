from pathlib import Path
import sys,json,struct,subprocess,mmap,re,zlib
P=Path(__file__).resolve().parent;H=P.parent;sys.path.insert(0,str(H));from verify_zip_evidence import TABLE,INITIAL,decrypt;from recover_archive_central import crypt
INV={x>>24:i for i,x in enumerate(TABLE)};MI=pow(134775813,-1,1<<32)
def uncrc(v,p):
 i=INV[v>>24];return (((v^TABLE[i])<<8)|(i^p))&0xffffffff
def reverse(state,p):
 a,b,c=state;return uncrc(a,p),(((b-1)*MI)-(a&255))&0xffffffff,uncrc(c,b>>24)
def update(state,p):
 a,b,c=state;a=(a>>8)^TABLE[(a^p)&255];b=((b+(a&255))*134775813+1)&0xffffffff;c=(c>>8)^TABLE[(c^(b>>24))&255];return a,b,c
def keybyte(state):
 c=state[2];t=(c&65535)|2;return((t*(t^1))>>8)&255
end=(0x20d4d4db,0x4d3336ef,0x18c00cf1);after_guid=end;trailer=[]
for p in b'},"'[:0]:pass
for p in reversed(b'}",'):
 before=reverse(after_guid,p);trailer.append(p^keybyte(before));assert update(before,p)==after_guid;after_guid=before
trailer=bytes(reversed(trailer));print('ZIPciphertrailer',trailer.hex(),'afterGUID',list(map(hex,after_guid)),flush=True)
raw=(P/'pte_archive.zip').read_bytes();header=decrypt(raw[13855:13867]);template=(P/'extensions_template.json').read_bytes();uuid=template.index(b'00000000-0000-0000-0000-000000000000');state=INITIAL;enc=bytearray()
for p in header+template[:uuid]:enc.append(p^keybyte(state));state=update(state,p)
assert state==(0x8e9c88b6,0xa4ea559b,0xa6fbb0aa);before_guid=state;sigmap={}
for layer in ('zip','mega'):
 for n in (4,8,16):
  sig=bytes(enc[-n:]);logical=49093-n;sig=sig if layer=='zip' else crypt(sig,logical)
  if b'\n' not in sig:sigmap[sig]=(logical,layer)
 for n in (3,8,16):
  b=trailer+raw[49132:49132+n-3];sig=b if layer=='zip' else crypt(b,49129)
  if b'\n' not in sig:sigmap[sig]=(49129,layer)
pat='|'.join(''.join(f'\\x{x:02x}' for x in s) for s in sigmap)
# JSON provides correct offsets for mixed-length signatures, even embedded CR.
r=subprocess.run(['rg','--text','--json','--no-unicode','--regexp',pat,str(H.parent/'evidence/mem.clean')],capture_output=True);assert r.returncode in(0,1),r.stderr;rows=[];verified=[]
with (H.parent/'evidence/mem.clean').open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as m:
 for line in r.stdout.splitlines():
  obj=json.loads(line)
  if obj['type']!='match':continue
  d=obj['data']
  for sm in d['submatches']:
   pos=d['absolute_offset']+sm['start'];length=sm['end']-sm['start'];sig=m[pos:pos+length];logical,layer=sigmap[sig];origin=pos+49093-logical;cipher=m[origin:origin+39];cipher=cipher if layer=='zip' else crypt(cipher,49093);s=before_guid;plain=bytearray()
   for c in cipher:p=c^keybyte(s);plain.append(p);s=update(s,p)
   row={'memory':hex(pos),'logical':logical,'layer':layer,'length':length,'guid_plain':plain.hex(),'endkeys_match':s==end};rows.append(row)
   if re.fullmatch(rb'[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\}",',plain) and s==end:
    candidate=template.replace(b'00000000-0000-0000-0000-000000000000',plain[:36]);assert zlib.crc32(candidate)==0x20a2f078;verified.append(row);(P/'27_extensions.json').write_bytes(candidate);print('VERIFIED',row,flush=True)
(P/'guid_edge_results.json').write_text(json.dumps({'trailer':trailer.hex(),'after_guid_keys':list(map(hex,after_guid)),'hits':rows,'verified':verified},indent=2));print('HITS',len(rows),'VERIFIED',len(verified))
