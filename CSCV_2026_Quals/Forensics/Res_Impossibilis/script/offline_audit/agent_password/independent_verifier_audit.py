#!/usr/bin/env python3
"""Cross-check password states and archive bytes without the existing decryptor."""
from pathlib import Path
import ctypes
import hashlib
import json
import random
import struct
import subprocess
import zipfile
import zlib

HERE=Path(__file__).resolve().parent
AUDIT=HERE.parent
INITIAL=(0x12345678,0x23456789,0x34567890)
TARGET=(0x670e8462,0x306591b4,0x8372919d)

def raw_crc(value, byte):
    # zlib's public CRC uses complemented state; ZIP's update uses raw state.
    return zlib.crc32(bytes([byte]),value ^ 0xffffffff) ^ 0xffffffff

def update(keys, byte):
    x,y,z=keys
    x=raw_crc(x,byte)
    y=((y+(x & 255))*134775813+1) & 0xffffffff
    z=raw_crc(z,y >> 24)
    return x,y,z

def derive(password):
    keys=INITIAL
    for byte in password: keys=update(keys,byte)
    return keys

def stdlib_cells(decryptor):
    outer=dict(zip(decryptor.__code__.co_freevars,decryptor.__closure__))
    updater=outer['update_keys'].cell_contents
    return dict(zip(updater.__code__.co_freevars,updater.__closure__))

def stdlib_decrypt(data, keys):
    # Preserve standard-library arithmetic, supplying the already recovered
    # initial state through its Python closure instead of inventing a password.
    decryptor=zipfile._ZipDecrypter(b'')
    cells=stdlib_cells(decryptor)
    for i,key in enumerate(keys): cells[f'key{i}'].cell_contents=key
    return decryptor(data)

def independent_decrypt(data):
    keys=TARGET
    out=bytearray()
    for cipherbyte in data:
        t=keys[2] | 2
        byte=cipherbyte ^ (((t*(t^1)) >> 8) & 255)
        out.append(byte)
        keys=update(keys,byte)
    return bytes(out)

subprocess.run(['cc','-O3','-Wall','-Wextra','-shared','-fPIC',
                '-o',str(HERE/'verifier_probe.so'),str(HERE/'verifier_probe.c')],check=True)
probe=ctypes.CDLL(str(HERE/'verifier_probe.so'));probe.setup()
probe.derive_exact_keys.argtypes=[ctypes.c_char_p,ctypes.c_size_t,ctypes.POINTER(ctypes.c_uint32)]
original=ctypes.CDLL(str(AUDIT/'password_verifier.so'));original.setup()
original.check_password.argtypes=[ctypes.c_char_p,ctypes.c_size_t]
rng=random.Random(20260925)
passwords=[b'',b'password',b'\0',b'abc\0def','mật_khẩu_🔐'.encode()]
passwords += [bytes([b]) for b in range(256)]
passwords += [bytes(rng.randrange(256) for _ in range(n)) for n in range(129)]
for p in passwords:
    expected=derive(p)
    cells=stdlib_cells(zipfile._ZipDecrypter(p))
    observed=tuple(cells[f'key{i}'].cell_contents for i in range(3))
    out=(ctypes.c_uint32*3)();probe.derive_exact_keys(p,len(p),out)
    assert tuple(out)==expected==observed,(p.hex(),expected,tuple(out),observed)
    assert bool(original.check_password(p,len(p)))==(expected==TARGET)

archive_path=AUDIT/'agent_archive/merged_archive.zip'
known_path=AUDIT/'agent_archive/merged_known.bin'
archive=archive_path.read_bytes();known=known_path.read_bytes()
entries=[]
with zipfile.ZipFile(archive_path) as zf:
    for index,info in enumerate(zf.infolist()):
        o=info.header_offset
        row=dict(index=index,name=info.filename,flags=info.flag_bits,method=info.compress_type,
                 complete=False)
        if not all(known[o:o+30]): entries.append(row);continue
        h=struct.unpack_from('<4s5H3I2H',archive,o)
        assert h[0]==b'PK\x03\x04'
        start=o+30+h[9]+h[10];end=start+info.compress_size
        if not all(known[o:end]): entries.append(row);continue
        cipher=archive[start:end]
        plain=independent_decrypt(cipher)
        assert plain==stdlib_decrypt(cipher,TARGET)
        payload=plain[12:]
        if info.compress_type==8:payload=zlib.decompress(payload,-15)
        else:assert info.compress_type==0
        assert len(payload)==info.file_size
        assert zlib.crc32(payload)==info.CRC
        checkbyte=(h[4]>>8) if info.flag_bits & 8 else info.CRC>>24
        assert plain[11]==checkbyte
        row.update(complete=True,header=plain[:12].hex(),crc32=f'{zlib.crc32(payload):08x}',
                   plaintext_size=len(payload),header_check_valid=True,
                   stdlib_decryption_equal=True)
        entries.append(row)

report=dict(password_vectors=len(passwords),password_arithmetic_matches=True,
            methods=['Original C source arithmetic','Python standard library zipfile',
                     'Independent zlib complemented-state recurrence'],
            original_shared_verifier_decisions_match=True,
            archive_sha256=hashlib.sha256(archive).hexdigest(),
            known_mask_sha256=hashlib.sha256(known).hexdigest(),
            archive_members=len(entries),verified_members=sum(e['complete'] for e in entries),
            keys=[f'{k:08x}' for k in TARGET],entries=entries,
            original_password_recovered=False)
(HERE/'independent_verifier_results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='entries'},indent=2))
