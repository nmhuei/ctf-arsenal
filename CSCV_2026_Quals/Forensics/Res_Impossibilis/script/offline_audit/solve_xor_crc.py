"""Solve CRC32-linear constraints for repeating-XOR encodings, verify all ZIP keys."""
from pathlib import Path
import base64
import ctypes
import json
from verify_zip_evidence import TABLE

HERE=Path(__file__).resolve().parent
lib=ctypes.CDLL(str(HERE/'password_verifier.so'));lib.setup()
lib.xor_family.argtypes=[ctypes.c_char_p,ctypes.c_size_t,ctypes.c_uint,ctypes.c_uint64,
    ctypes.POINTER(ctypes.c_uint64),ctypes.c_uint,ctypes.c_void_p,ctypes.POINTER(ctypes.c_uint64)]

def crc(data):
    state=0x12345678
    for byte in data:state=(state>>8)^TABLE[(state^byte)&255]
    return state

def linear_family(cipher,keylen):
    variables=keylen*8
    initial=crc(cipher)
    target=initial^0x670e8462
    columns=[]
    for bit in range(variables):
        modified=bytearray(cipher)
        for i in range(bit//8,len(cipher),keylen):modified[i]^=1<<(bit%8)
        columns.append(crc(modified)^initial)
    rows=[sum(((c>>i)&1)<<j for j,c in enumerate(columns)) | (((target>>i)&1)<<variables)
          for i in range(32)]
    rank=0;pivots=[]
    for col in range(variables):
        selected=next((i for i in range(rank,32) if (rows[i]>>col)&1),None)
        if selected is None:continue
        rows[rank],rows[selected]=rows[selected],rows[rank]
        for i in range(32):
            if i!=rank and ((rows[i]>>col)&1):rows[i]^=rows[rank]
        pivots.append(col);rank+=1
        if rank==32:break
    mask=(1<<variables)-1
    if any((row&mask)==0 and (row>>variables)&1 for row in rows):return None
    particular=sum(((rows[i]>>variables)&1)<<col for i,col in enumerate(pivots))
    basis=[]
    for free in set(range(variables))-set(pivots):
        basis.append((1<<free)|sum(((rows[i]>>free)&1)<<col for i,col in enumerate(pivots)))
    return particular,basis

full=base64.b64decode('ekZRRQNoW1cCNX5iBEg2Yj1pelpoUgsQRFRWfFYmI3wPIGkuUiddNTI6PyQbIR43OyIZbkIPNmVi')
report=[]
for name,cipher in [('full',full),('suffix60',full[12:])]:
    for keylen in range(1,8):
        family=linear_family(cipher,keylen)
        row={'source':name,'plaintext_length':len(cipher),'xor_key_bytes':keylen}
        if family is None:
            row['crc_consistent']=False
        else:
            particular,basis=family;row.update(crc_consistent=True,free_bits=len(basis))
            # Verify the affine model before enumerating candidates.
            for key in [particular]+[particular^b for b in basis]:
                assert crc(bytes(v^((key>>(8*(i%keylen)))&255) for i,v in enumerate(cipher)))==0x670e8462
            vectors=(ctypes.c_uint64*len(basis))(*basis)
            out=ctypes.create_string_buffer(len(cipher));found=ctypes.c_uint64()
            result=lib.xor_family(cipher,len(cipher),keylen,particular,vectors,len(basis),out,ctypes.byref(found))
            row['result']=result
            if result==1:
                row['password']=out.raw.decode();row['xor_key']=found.value.to_bytes(keylen,'little').hex()
                (HERE/'archive_password.txt').write_bytes(out.raw)
        report.append(row);print(row,flush=True)
(HERE/'xor_crc_results.json').write_text(json.dumps(report,indent=2)+'\n')
