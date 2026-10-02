#!/usr/bin/env python3
"""Check recovered AES schedule keys against passive TLS 1.3 records.

For a supplied AES key, recover J0 = AES^-1(tag XOR GHASH(AAD,ciphertext)).
TLS's 96-bit nonce requires J0 = nonce || 00000001. This is a 32-bit
consistency filter, not an independent 128-bit test after choosing the nonce.
Record structure and shared IV/sequence consistency provide further evidence.
No key brute force and no network operations.
"""
from pathlib import Path
import hashlib
import json
import struct
from Crypto.Cipher import AES, _mode_gcm

HERE=Path(__file__).resolve().parent
AUDIT=HERE.parents[1]
CAPTURE=AUDIT/'agent_archive/tls87'
GHASH_BACKEND=_mode_gcm._ghash_clmul or _mode_gcm._ghash_portable

def padded(data):return data+b'\0'*((-len(data))%16)

def recover_j0(key,aad,ciphertext,tag):
    aes=AES.new(key,AES.MODE_ECB)
    h=aes.encrypt(bytes(16))
    gh=_mode_gcm._GHASH(h,GHASH_BACKEND)
    gh.update(padded(aad)+padded(ciphertext)+struct.pack('>QQ',8*len(aad),8*len(ciphertext)))
    masked=bytes(a^b for a,b in zip(tag,gh.digest()))
    return aes.decrypt(masked)

def self_test():
    key=bytes(range(16));nonce=bytes(range(12))
    plaintext=b'GET /fixture HTTP/1.1\r\n\r\n\x17'
    aad=b'\x17\x03\x03'+(len(plaintext)+16).to_bytes(2,'big')
    gcm=AES.new(key,AES.MODE_GCM,nonce=nonce);gcm.update(aad)
    ciphertext,tag=gcm.encrypt_and_digest(plaintext)
    j0=recover_j0(key,aad,ciphertext,tag)
    assert j0==nonce+b'\0\0\0\1'
    check=AES.new(key,AES.MODE_GCM,nonce=j0[:12]);check.update(aad)
    assert check.decrypt_and_verify(ciphertext,tag)==plaintext
    wrong=recover_j0(bytes(reversed(key)),aad,ciphertext,tag)
    assert wrong[12:]!=b'\0\0\0\1'
    corrupted=bytes([tag[0]^1])+tag[1:]
    assert recover_j0(key,aad,ciphertext,corrupted)[12:]!=b'\0\0\0\1'
    return dict(passed=True,j0_hex=j0.hex(),wrong_key_rejected=True,corrupt_tag_rejected=True)

fixture=self_test()
hello=(AUDIT/'tls75_server.bin').read_bytes()[9:127]
sid_length=hello[34]
server_hello={'cipher_suite':'0x'+hello[35+sid_length:37+sid_length].hex()}
assert server_hello['cipher_suite']=='0x1301'
keys={};source_128=set();excluded_256=0
for line in (AUDIT/'aes_scan/aes_keys.txt').read_text().splitlines():
    if not line or line.startswith('#'):continue
    fields=line.split('\t');key=bytes.fromhex(fields[1])
    if len(key)!=16:excluded_256+=1;continue
    source_128.add(key)
    variants={
        'original':key,
        'reverse_all_bytes':key[::-1],
        'reverse_bytes_in_u32':b''.join(key[i:i+4][::-1] for i in range(0,16,4)),
        'reverse_u32_order':b''.join(key[i:i+4] for i in range(12,-1,-4))}
    for kind,value in variants.items():
        keys.setdefault(value,[]).append(dict(memory_offset=fields[0],variant=kind))

tested=0;counter_matches=[];authenticated=[];record_counts={}
for direction in ['client','server']:
    stream=(AUDIT/f'tls75_{direction}.bin').read_bytes()
    records=json.loads((CAPTURE/f'tls75_{direction}_records.json').read_text())
    encrypted=[r for r in records if r['content_type']==23]
    record_counts[direction]=len(encrypted)
    for r in encrypted:
        aad=stream[r['offset']:r['payload_offset']]
        data=stream[r['payload_offset']:r['end']]
        assert len(aad)==5 and len(data)==r['length'] and len(data)>=17
        ciphertext,tag=data[:-16],data[-16:]
        for key,origins in keys.items():
            tested+=1;j0=recover_j0(key,aad,ciphertext,tag)
            if j0[12:]!=b'\0\0\0\1':continue
            row=dict(direction=direction,record_index=r['index'],record_offset=r['offset'],
                     key_hex=key.hex(),nonce_hex=j0[:12].hex(),origins=origins)
            counter_matches.append(row)
            gcm=AES.new(key,AES.MODE_GCM,nonce=j0[:12]);gcm.update(aad)
            try:plain=gcm.decrypt_and_verify(ciphertext,tag)
            except ValueError:continue
            stripped=plain.rstrip(b'\0')
            content_type=stripped[-1] if stripped else None
            payload=stripped[:-1]
            path=HERE/f'tls75_authenticated_{direction}_record_{r["index"]:02d}.bin'
            path.write_bytes(plain)
            authenticated.append(dict(**row,plaintext_path=path.name,
                plaintext_length=len(plain),inner_content_type=content_type,
                inner_content_type_valid=content_type in (21,22,23),
                content_length=len(payload),content_prefix_hex=payload[:64].hex()))

groups={}
for row in authenticated:groups.setdefault((row['direction'],row['key_hex']),[]).append(row)
consistency=[]
for (direction,key),rows in groups.items():
    rows.sort(key=lambda r:r['record_index'])
    # Common application epoch begins at index3, after the Finished at index2.
    # Other epochs can be recognized from relative XOR of consecutive nonces.
    epoch_tests=[]
    for base in range(0,4):
        ivs={bytes(a^b for a,b in zip(bytes.fromhex(r['nonce_hex']),
              (r['record_index']-base).to_bytes(12,'big'))).hex()
             for r in rows if r['record_index']>=base}
        epoch_tests.append(dict(record_index_for_sequence_zero=base,
                               distinct_iv_candidates=len(ivs),ivs=sorted(ivs)))
    consistency.append(dict(direction=direction,key_hex=key,records=len(rows),epoch_tests=epoch_tests))

report=dict(fixture=fixture,cipher_suite=server_hello['cipher_suite'],
    source_unique_aes128_keys=len(source_128),aes256_rows_excluded=excluded_256,
    key_variants=len(keys),record_counts=record_counts,key_record_tests=tested,
    j0_counter_matches=counter_matches,authenticated_records=authenticated,
    nonce_consistency=consistency,
    interpretation='Each tag-derived J0 suffix match is a 32-bit consistency filter; require independent structure/multiple-record evidence.',
    capture_hashes={d:hashlib.sha256((AUDIT/f'tls75_{d}.bin').read_bytes()).hexdigest() for d in ['client','server']})
(HERE/'tls75_gcm_schedule_results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ('j0_counter_matches','authenticated_records','nonce_consistency')},indent=2))
print('J0 matches:',len(counter_matches),'authenticated records:',len(authenticated))
