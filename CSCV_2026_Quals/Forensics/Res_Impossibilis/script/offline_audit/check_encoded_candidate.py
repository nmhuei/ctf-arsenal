from pathlib import Path
import base64
import ctypes
import hashlib
import json

HERE=Path(__file__).resolve().parent
lib=ctypes.CDLL(str(HERE/'password_verifier.so'))
lib.setup()
lib.check_password.argtypes=[ctypes.c_char_p,ctypes.c_size_t]
lib.find_password.argtypes=[ctypes.c_char_p,ctypes.c_size_t,ctypes.POINTER(ctypes.c_size_t),ctypes.POINTER(ctypes.c_size_t)]
full=base64.b64decode('ekZRRQNoW1cCNX5iBEg2Yj1pelpoUgsQRFRWfFYmI3wPIGkuUiddNTI6PyQbIR43OyIZbkIPNmVi')
values=[full,full[12:]]
words=[b'3601188fbcc04a5da1a59be3b5383dfb',b'centosstream9',b'centosstream9.linuxvmimages.local',
       b'65cc151a88e54d8d98957d1873632f9b',b'audit',b'mega',b'sys_audit_collector',b'CSCV2026',b'1788885121']
keys=set(words)
for word in words:
    keys.update([word.upper(),word[::-1]])
    for function in [hashlib.md5,hashlib.sha1,hashlib.sha256]:
        keys.update([function(word).digest(),function(word).hexdigest().encode()])
for path in ['gemini_password_round2.txt']:
    obj=json.loads((HERE/path).read_text())
    for candidate in obj['candidates']:
        if lib.check_password(candidate.encode(),len(candidate.encode())):
            (HERE/'archive_password.txt').write_text(candidate)
            raise SystemExit('Verified Gemini candidate: '+candidate)

hits=[];tested=0;printable=[]
def test(data,label):
    global tested
    tested+=1
    start=ctypes.c_size_t();length=ctypes.c_size_t()
    if lib.find_password(data,len(data),ctypes.byref(start),ctypes.byref(length)):
        hit=data[start.value:start.value+length.value]
        hits.append({'transform':label,'password_hex':hit.hex()})
        (HERE/'archive_password.txt').write_bytes(hit)
    if all(32<=c<127 for c in data):
        printable.append({'transform':label,'text':data.decode()})
for value in values:
    test(value,'base64-only')
    for byte in range(256):
        test(bytes(x^byte for x in value),f'xor-byte-{byte}')
    for key in keys:
        for shift in range(len(key)):
            test(bytes(x^key[(i+shift)%len(key)] for i,x in enumerate(value)),f'xor-{key.hex()}-shift-{shift}')
    for initial in range(256):
        for step in (1,3,5,7,11,13,17,31):
            test(bytes(x^((initial+i*step)&255) for i,x in enumerate(value)),f'xor-counter-{initial}-{step}')
report={'gemini_round2_tested':80,'decoded_lengths':[len(v) for v in values],
        'transformations_tested':tested,'verified_matches':hits,'fully_printable_results':printable}
(HERE/'encoded_candidate_results.json').write_text(json.dumps(report,indent=2)+'\n')
print({k:v for k,v in report.items() if k!='fully_printable_results'})
print('Fully printable results',len(printable))
