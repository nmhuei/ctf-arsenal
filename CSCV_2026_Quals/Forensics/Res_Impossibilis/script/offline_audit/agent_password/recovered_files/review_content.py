#!/usr/bin/env python3
"""Read verified archive members, inspect inert bytes, and check bounded tokens."""
from pathlib import Path
from collections import Counter
import base64
import ctypes
import hashlib
import json
import re
import struct
import zipfile
import zlib

HERE=Path(__file__).resolve().parent
AUDIT=HERE.parents[1]
RECOVERED=AUDIT/'recovered39'
manifest_bytes=(RECOVERED/'manifest.json').read_bytes()
manifest=json.loads(manifest_bytes)
lib=ctypes.CDLL(str(AUDIT/'password_verifier.so'));lib.setup()
lib.find_password.argtypes=[ctypes.c_char_p,ctypes.c_size_t,
    ctypes.POINTER(ctypes.c_size_t),ctypes.POINTER(ctypes.c_size_t)]
lib.check_password.argtypes=[ctypes.c_char_p,ctypes.c_size_t]
candidates={}
counts=Counter()
decoded_text=[]
files=[]

def add(data,origin,kind):
    if isinstance(data,str):data=data.encode()
    if not data or len(data)>65536:return
    counts[kind]+=1
    candidates.setdefault(data,dict(origin=origin,kind=kind))

def walk(obj,origin):
    if isinstance(obj,dict):
        for key,value in obj.items():add(str(key),origin,'json_key');walk(value,origin)
    elif isinstance(obj,list):
        for v in obj:walk(v,origin)
    elif isinstance(obj,str):add(obj,origin,'json_value')
    elif obj is not None:add(json.dumps(obj),origin,'json_scalar')

for entry in manifest['entries']:
    if entry['status']!='verified':continue
    path=RECOVERED/entry['output'];data=path.read_bytes()
    assert len(data)==entry['plain_size'] and zlib.crc32(data)==int(entry['crc32'],16)
    files.append(dict(index=entry['index'],name=path.name,size=len(data),
                      sha256=hashlib.sha256(data).hexdigest()))
    add(data,path.name,'whole_member')
    try:walk(json.loads(data),path.name)
    except (ValueError,UnicodeDecodeError):pass
    for line in data.splitlines():
        add(line,path.name,'line')
        for sep in (b'=',b':'):
            if sep in line:add(line.split(sep,1)[1].strip(),path.name,'assignment_rhs')
    for token in re.findall(rb'[^\s\x00]+',data):add(token,path.name,'text_token')
    for token in re.findall(rb'[A-Za-z0-9+/_=-]{8,}',data):add(token,path.name,'encoded_token')

# Two finite decode rounds; no execution, URL access, decompression, or guesses.
for depth in range(2):
    current=list(candidates.items())
    for value,source in current:
        if len(value)>8192:continue
        compact=value.strip()
        decodings=[]
        hx=compact[2:] if compact.startswith(b'0x') else compact
        if len(hx)>=8 and len(hx)%2==0 and re.fullmatch(rb'[0-9A-Fa-f]+',hx):
            decodings.append(('hex',bytes.fromhex(hx.decode())))
        if len(compact)>=8 and len(compact)%4!=1 and re.fullmatch(rb'[A-Za-z0-9+/_-]+={0,2}',compact):
            try:
                b=base64.b64decode(compact+b'='*((-len(compact))%4),altchars=b'-_',validate=True)
                decodings.append(('base64',b))
            except ValueError:pass
        for enc,decoded in decodings:
            add(decoded,source['origin'],f'decoded_{enc}_round{depth+1}')
            if b'FLAG{' in decoded or b'fake' in decoded or b'NOT_VALID' in decoded:
                if all(32<=b<=126 for b in decoded):
                    decoded_text.append(dict(origin=source['origin'],encoding=enc,text=decoded.decode()))

hits=[]
for value,source in candidates.items():
    start,length=ctypes.c_size_t(),ctypes.c_size_t()
    if lib.find_password(value,len(value),ctypes.byref(start),ctypes.byref(length)):
        p=value[start.value:start.value+length.value]
        hits.append(dict(**source,password_hex=p.hex(),offset=start.value,length=length.value))

tls=[]
captured=set()
with (AUDIT/'soc_tls_clienthellos.tsv').open() as f:
    headings=f.readline().rstrip('\n').split('\t');column=headings.index('tls.handshake.random')
    for line in f:
        fields=line.rstrip('\n').split('\t')
        if len(fields)>column:
            captured.update(re.findall(r'[0-9a-fA-F]{64}',fields[column]))
for line in (RECOVERED/'14_sslkeylog_debug.txt').read_text().splitlines():
    if not line or line.startswith('#'):continue
    label,random,secret=line.split()
    tls.append(dict(label=label,random_hex_length=len(random),secret_hex_length=len(secret),
                    hex_valid=bool(re.fullmatch('[0-9a-fA-F]+',random+secret)),
                    random=random,random_present_in_capture=random in captured))

kdbx=(RECOVERED/'15_backup_credentials.kdbx').read_bytes()
kdbx_report=dict(length=len(kdbx),signatures=[hex(v) for v in struct.unpack_from('<II',kdbx)],
                 format_version=hex(struct.unpack_from('<I',kdbx,8)[0]),first_field_id=kdbx[12],
                 first_field_size=struct.unpack_from('<I',kdbx,13)[0],remaining_field_bytes=len(kdbx)-17)
kdbx_report['first_field_overruns_file']=kdbx_report['first_field_size']>kdbx_report['remaining_field_bytes']
xlsx_path=RECOVERED/'08_q3_financial_audit_confidential.xlsx'
xlsx_report=dict(length=xlsx_path.stat().st_size,is_zip=zipfile.is_zipfile(xlsx_path),
                 content_repr=repr(xlsx_path.read_bytes()))
vpn=[]
for line in (RECOVERED/'13_vpn_profile.conf').read_text().splitlines():
    if line.startswith(('PrivateKey','PublicKey')):
        name,value=line.split(' = ',1);data=base64.b64decode(value)
        vpn.append(dict(field=name,decoded_bytes=len(data),decoded_text=data.decode()))

report=dict(manifest_sha256=hashlib.sha256(manifest_bytes).hexdigest(),verified_files=len(files),
            members=files,candidate_source_counts=dict(counts),unique_candidate_sequences=len(candidates),
            candidate_byte_sum=sum(map(len,candidates)),maximum_substring_length=128,
            match_criterion='Exact 670e8462 306591b4 8372919d ZIPCrypto state',matches=hits,
            declared_backup_password_matches=bool(lib.check_password(b'Winter2026!CorporateAccess#',
                len(b'Winter2026!CorporateAccess#'))),
            decoded_markers=list({json.dumps(r,sort_keys=True):r for r in decoded_text}.values()),
            captured_client_random_count=len(captured),tls_keylog=tls,kdbx=kdbx_report,xlsx=xlsx_report,
            vpn_keys=vpn)
(HERE/'content_review_results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ('members','decoded_markers')},indent=2))
