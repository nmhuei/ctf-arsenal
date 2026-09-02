from pathlib import Path
from analyze_vm import parse_init
b=Path('challenge_1.dec').read_bytes(); w,pc=parse_init(b)
base=min(dst for _,dst in w)
print('base',hex(base),'n',len(w),'after',hex(pc))
for idx,(addr,dst) in enumerate(sorted(w, key=lambda x:x[1])[:40]):
 print(idx,hex(dst-base),hex(addr))
print('...')
for idx,(addr,dst) in list(enumerate(sorted(w, key=lambda x:x[1])))[-20:]:
 print(idx,hex(dst-base),hex(addr))
