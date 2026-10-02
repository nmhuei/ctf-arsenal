from pathlib import Path
import sys,struct,json,subprocess
sys.path.insert(0,'script/offline_audit/agent_collector');import kernel_walk as k
OUT=Path('script/offline_audit/agent_collector/password_followup');ino=0xffff979067d175a0;fi=k.p2f(ino-k.DM);ptr=struct.unpack_from('<Q',k.m,fi-0xc0)[0];fo=k.p2f(ptr-k.DM);lo,hi=struct.unpack_from('<QQ',k.m,fo);start=(lo>>54)|((hi&~((1<<22)-1))>>12);mp=struct.unpack_from('<Q',k.m,fi-0x120)[0];mf=k.p2f(mp-k.DM);agblocks=struct.unpack_from('<I',k.m,mf+84)[0];aglog=k.m[mf+124];blocklog=k.m[mf+120];agno=start>>aglog;agbno=start&((1<<aglog)-1);linear=agno*agblocks+agbno;sector=linear<<(blocklog-9)
targets={'fsblock':start,'linear_block':linear,'logical_sector':sector};report={'inode':hex(ino),'extent_ptr':hex(ptr),'extent_lo':hex(lo),'extent_hi':hex(hi),'file_block':lo&((1<<54)-1),'blocks':hi&((1<<21)-1),'unwritten':bool(hi&(1<<21)),'agblocks':agblocks,'agblklog':aglog,'blocksize':1<<blocklog,'agno':agno,'agbno':agbno,'targets':{x:hex(y) for x,y in targets.items()}}
(OUT/'auditlog_extent.json').write_text(json.dumps(report,indent=2));print(report,flush=True)
patterns={}
for name,value in targets.items():
 for order in ['<','>']:patterns[name+order]=struct.pack(order+'Q',value)
pat='|'.join(''.join('\\x%02x'%c for c in b) for b in patterns.values());proc=subprocess.run(['rg','-aob','--no-unicode',pat,'script/evidence/mem.clean'],capture_output=True);rows=[]
for line in proc.stdout.splitlines():
 if b':' not in line:continue
 a,b=line.split(b':',1);off=int(a);tags=[x for x,y in patterns.items() if b==y];rows.append({'file':hex(off),'tags':tags,'context':k.m[off-96:off+160].hex()})
(OUT/'auditlog_block_refs.json').write_text(json.dumps(rows,indent=2));print('hits',len(rows));print(rows[:15])
