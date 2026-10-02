#!/usr/bin/env python3
"""Res Impossibilis password recovery helper.
Uses the provided exact ZIPCrypto state verifier against memory-derived candidates.
"""
from pathlib import Path
import ctypes, re, subprocess, json

ROOT=Path(__file__).resolve().parents[1]
AUDIT=ROOT/'script/offline_audit'
MEM=ROOT/'script/evidence/mem.clean'
lib=ctypes.CDLL(str(AUDIT/'password_verifier.so'))
lib.setup()
lib.check_password.argtypes=[ctypes.c_char_p, ctypes.c_size_t]
lib.check_password.restype=ctypes.c_int

def valid(x):
    return lib.check_password(x,len(x))==1

candidates=[]
# Extract strings using the system tool (fast over ~1GB memory image).
for line in subprocess.check_output(['strings','-a','-n','8',str(MEM)], text=True, errors='ignore').splitlines():
    b=line.encode()
    if len(b)>=8 and len(b)<=256:
        candidates.append(b)

# Add obvious encoded tokens from memory.
seen=set()
for c in candidates:
    if c in seen: continue
    seen.add(c)
    if valid(c):
        print('Recovered password:',c.decode(errors='replace'))
        password=c.decode(errors='replace')
        flag=f'cscv2026{{tommyxiaomihackerbox@gmail.com_9ec3d41b5db1baee571dbe1bebff4774b85d61e046edce96a86dd489644ce2e7_{password}_730f0c0eadc0edb118e4fdc6fbee892e}}\n'
        (ROOT/'flag.txt').write_text(flag)
        raise SystemExit

(ROOT/'solver'/'result.json').write_text(json.dumps({'tested':len(seen),'hit':None},indent=2))
print('No verified archive password recovered; tested',len(seen),'memory strings')
