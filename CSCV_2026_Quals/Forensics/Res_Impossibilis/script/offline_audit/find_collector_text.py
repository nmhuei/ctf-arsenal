from pathlib import Path
import mmap,struct,json
root=Path(__file__).resolve().parents[2];out=[]
with (root/'script/evidence/mem.clean').open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as m:
 pos=0
 while True:
  pos=m.find(b'\x68\x1a\0\0\0',pos)
  if pos<0:break
  hit=pos;pos+=5
  if m[hit-16:hit-11]!=b'\x68\x19\0\0\0':continue
  before=m[hit-16:hit];after=m[hit+5:hit+16]
  # PLT entry jumps through the last GOT slot at virtual 0x4050e8.
  jmp=m.rfind(b'\xff\x25',hit-12,hit)
  if jmp<0:continue
  disp=struct.unpack_from('<i',m,jmp+2)[0];vaddr=0x4050e8-disp-6;base=jmp-(vaddr-0x401000)
  if not 0x401000<=vaddr<0x401400:continue
  row={'push26':hex(hit),'jmp':hex(jmp),'vaddr':hex(vaddr),'base':hex(base),'head':m[base:base+64].hex()};out.append(row);print(row,flush=True)
  (root/f'script/offline_audit/text_candidate_{base:x}.bin').write_bytes(m[base:base+0x12f5])
(root/'script/offline_audit/collector_text_candidates.json').write_text(json.dumps(out,indent=2))
