from pathlib import Path
import sys,struct,json,zlib,ctypes,mmap,subprocess
P=Path(__file__).resolve().parent;H=P.parent;sys.path.insert(0,str(H));from verify_zip_evidence import INITIAL,TABLE,decrypt;from recover_archive_central import crypt
plain=(H/'root_files/31_extension-preferences.json').read_bytes();assert len(plain)==1380 and zlib.crc32(plain)==0x3431d481
raw=bytearray((P/'pte_archive.zip').read_bytes());known=bytearray((P/'pte_known.bin').read_bytes());record=json.loads((H/'archive_central_records.json').read_text())[31];o=record['local_offset'];h=struct.unpack_from('<4s5H3I2H',raw,o);start=o+30+h[9]+h[10];header=decrypt(raw[start:start+12]);a,b,c=INITIAL;out=bytearray()
for p in header+plain:
 t=(c&65535)|2;out.append(p^((t*(t^1)>>8)&255));a=(a>>8)^TABLE[(a^p)&255];b=((b+(a&255))*134775813+1)&0xffffffff;c=(c>>8)^TABLE[(c^(b>>24))&255]
assert all(not known[i] or raw[i]==v for i,v in enumerate(out,start));raw[start:start+len(out)]=out;known[start:start+len(out)]=b'\x01'*len(out)
(P/'32_entries_archive.zip').write_bytes(raw);(P/'32_entries_known.bin').write_bytes(known);sigmap={}
for offset in range(53200,53310,8):
 for layer in ('zip','mega'):
  sig=bytes(raw[offset:offset+16]);sig=sig if layer=='zip' else crypt(sig,offset)
  if b'\n' not in sig:sigmap[sig]=(offset,layer)
pat='|'.join(''.join(f'\\x{x:02x}' for x in s) for s in sigmap)
r=subprocess.run(['rg','--text','--byte-offset','--only-matching','--no-unicode','--replace','X'*16,'--regexp',pat,str(H.parent/'evidence/mem.clean')],capture_output=True);assert r.returncode in(0,1),r.stderr
results=[]
with (H.parent/'evidence/mem.clean').open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as m:
 for line in r.stdout.splitlines():
  pos=int(line.split(b':')[0]);sig=m[pos:pos+16];offset,layer=sigmap[sig];results.append({'memory':hex(pos),'logical':offset,'layer':layer})
(P/'member31_signature_hits.json').write_text(json.dumps(results,indent=2));print('Newderivedbytes',sum(known)-43652,'memoryhits',results)
