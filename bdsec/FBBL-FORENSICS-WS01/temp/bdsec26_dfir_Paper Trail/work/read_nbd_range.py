#!/usr/bin/env python3
import re, subprocess, sys
uri, off_s, len_s, out = sys.argv[1:]
off, length = int(off_s), int(len_s)
cmd=['qemu-io','-r','-f','raw','-c',f'read -v {off} {length}',uri]
p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True,text=True)
buf=bytearray()
for line in p.stdout.splitlines():
    m=re.match(r'^[0-9a-fA-F]+:\s+((?:[0-9a-fA-F]{2}\s+){1,16})',line)
    if m:
        buf.extend(bytes.fromhex(m.group(1)))
open(out,'wb').write(buf[:length])
print(f'wrote {len(buf[:length])} bytes to {out}')
