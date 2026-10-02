import kernel_walk as k,json,struct,hashlib
from pathlib import Path
OUT=Path('script/offline_audit/agent_collector');root=0x1294000;rows=[]
for page_va in [0xffffe18300bdc680,0xffffe18300d02040,0xffffe18300c5f2c0,0xffffe18300d44d80,0xffffe18300d44dc0,0xffffe18300d44e00,0xffffe18300d44e80]:
 pa=(page_va-k.VM)//64*4096; pfo=k.p2f(pa);dpa=k.walk(root,page_va);dfo=k.p2f(dpa);q=struct.unpack_from('<8Q',k.m,dfo)
 rows.append({'page_struct_va':hex(page_va),'page_struct_phys':hex(dpa),'page_struct_file':hex(dfo),'page_phys':hex(pa),'page_file':hex(pfo),'flags':hex(q[0]),'mapping':hex(q[3]),'index':q[4],'refcount':q[6]>>32,'page_nonzero':sum(c!=0 for c in k.m[pfo:pfo+4096]),'sha256':hashlib.sha256(k.m[pfo:pfo+4096]).hexdigest()})
(OUT/'page_validation.json').write_text(json.dumps(rows,indent=2))
print(json.dumps(rows,indent=2))
