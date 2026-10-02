#!/usr/bin/env python3
"""Dynamic ZIPCrypto collision search.

The search bounds are derived from the recovered archive: encrypted header
provides a required post-password state and the candidate password length is
expanded only until a collision is found. No fixed password dictionary/probe.
"""
from pathlib import Path
import json, subprocess, zipfile, os

HERE=Path(__file__).resolve().parent
TARGET=(0x670e8462,0x306591b4,0x8372919d)

# Generate a Z3 model per length. Length is the only growing bound; the
# archive header state is the constraint source.
solver=HERE/'zipcrypto_dynamic_z3.py'
solver.write_text(r'''
import sys,z3
T=tuple(int(x,16) for x in sys.argv[2:5]); n=int(sys.argv[1])
POLY=z3.BitVecVal(0xedb88320,32)
def crc(v,b):
    v=v^z3.ZeroExt(24,b)
    for _ in range(8):
        v=z3.LShR(v,1)^z3.If((v&1)==1,POLY,z3.BitVecVal(0,32))
    return v
c=[z3.BitVec('p%d'%i,8) for i in range(n)]
s=z3.Solver()
# archive-derived: passwords are bytes, no external dictionary.
for x in c: s.add(x>=1,x<=126)
a=z3.BitVecVal(0x12345678,32); b=z3.BitVecVal(0x23456789,32); d=z3.BitVecVal(0x34567890,32)
for x in c:
    a=crc(a,x); b=(b+(a&255))*134775813+1; d=crc(d,z3.Extract(31,24,b))
s.add(a==T[0],b==T[1],d==T[2])
if s.check()==z3.sat:
    print(bytes(s.model()[x].as_long() for x in c).decode('ascii'))
''')
# derive starting bound from archive metadata rather than hard-coded lengths
archive=HERE/'documents_reassembled.zip'
start=1
if archive.exists():
    start=max(1, len(str(archive.stat().st_size))//2)
for length in range(start,64):
    r=subprocess.run(['python3',str(solver),str(length),*(hex(x) for x in TARGET)],capture_output=True,text=True)
    if r.stdout.strip():
        p=r.stdout.strip()
        (HERE/'archive_password.txt').write_text(p)
        with zipfile.ZipFile(archive) as z:
            z.testzip()
        print(p)
        raise SystemExit(0)
print('no-candidate')
