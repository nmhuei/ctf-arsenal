"""Audit only RAM-observed headers; do not treat reconstructed headers as evidence."""
from pathlib import Path
import sys, json, struct, datetime
P=Path(__file__).resolve().parent; H=P.parent
sys.path.insert(0,str(H))
from verify_zip_evidence import decrypt
archive=(P/'pte_archive.zip').read_bytes(); known=(P/'pte_known.bin').read_bytes()
records=json.loads((H/'archive_central_records.json').read_text())
# Independent implementation of glibc's default TYPE_3 additive generator.
def glibc_random(seed,n):
    state=[seed or 1]
    for i in range(1,31): state.append((16807*state[-1])%2147483647)
    state.extend(state[:3])
    for i in range(34,344+n): state.append((state[i-31]+state[i-3])&0xffffffff)
    return [(v>>1)&0x7fffffff for v in state[344:]]
seed=1788885121; rng=glibc_random(seed,11*len(records)); results=[]
for i,r in enumerate(records):
    o=r['local_offset']; start=o+30+len(r['name'].encode())
    if not all(known[o:start+12]): continue
    local=struct.unpack_from('<4s5H3I2H',archive,o)
    assert local[0]==b'PK\x03\x04' and local[10]==0
    header=decrypt(archive[start:start+12]); crc=int(r['crc32'],16)
    expected=bytes(v&255 for v in rng[11*i:11*(i+1)])
    row={'index':i,'name':r['name'],'header':header.hex(),'rand_offset':11*i,'random11_match':header[:11]==expected,'crc_high_byte_match':header[11]==crc>>24,'two_crc_bytes_match':header[10:]==(crc>>16).to_bytes(2,'little')}
    assert row['random11_match'] and row['crc_high_byte_match']; results.append(row)
central=[]; off=62443
while off<65386:
    assert all(known[off:off+46]); f=struct.unpack_from('<4s6H3I5H2I',archive,off); assert f[0]==b'PK\x01\x02'
    central.append({'made_by':f[1],'needed':f[2],'flags':f[3],'method':f[4],'time':hex(f[5]),'date':hex(f[6]),'extra_length':f[11],'comment_length':f[12],'disk':f[13],'internal_attrs':f[14],'external_attrs':f[15]})
    off+=46+f[10]+f[11]+f[12]
assert off==65386 and len(central)==39
report={'source_archive':'pte_archive.zip: RAM-observed pages only','seed':seed,'seed_as_unix_utc':datetime.datetime.fromtimestamp(seed,datetime.timezone.utc).isoformat(),'observed_headers':len(results),'observed_random_bytes':11*len(results),'header_indices':[r['index']for r in results],'not_independently_observed_indices':sorted(set(range(39))-{r['index']for r in results}),'matches':results,'two_crc_counterexamples':sum(not r['two_crc_bytes_match']for r in results),'unique_central_fingerprints':[dict(t)for t in set(tuple(x.items())for x in central)],'header_timestamp_decoded':'2022-09-01 13:00:00 (DOS local time; all entries)','seed_role':'effective header PRNG seed; not a password derivation result','password_formation_identified':False}
(P/'zip_writer_fingerprint.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items()if k!='matches'},indent=2))
