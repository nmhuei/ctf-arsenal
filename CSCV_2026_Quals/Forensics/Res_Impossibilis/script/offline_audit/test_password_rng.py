from pathlib import Path
import ctypes
import itertools
import json
import string

HERE=Path(__file__).resolve().parent
lib=ctypes.CDLL(str(HERE/'password_verifier.so'));lib.setup()
lib.find_password.argtypes=[ctypes.c_char_p,ctypes.c_size_t,ctypes.POINTER(ctypes.c_size_t),ctypes.POINTER(ctypes.c_size_t)]
libc=ctypes.CDLL('libc.so.6');libc.srand.argtypes=[ctypes.c_uint];libc.rand.restype=ctypes.c_int
alphabets=[string.ascii_lowercase,string.ascii_uppercase,string.digits,
           string.ascii_lowercase+string.digits,string.ascii_uppercase+string.digits,
           string.ascii_letters+string.digits+'!@#$%^&*',string.ascii_letters+string.digits+'_-',
           ''.join(map(chr,range(32,127))),''.join(map(chr,range(33,127))),
           '0123456789abcdef','abcdef0123456789','0123456789ABCDEF',
           'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789']
for parts in itertools.permutations([string.ascii_lowercase,string.ascii_uppercase,string.digits]):
    alphabets.append(''.join(parts))
count=0;hits=[]
for seed in range(1788884900,1788885301):
    libc.srand(seed);randoms=[libc.rand() for _ in range(96)]
    sequences=[('alphabet-'+alphabet,bytes(ord(alphabet[v%len(alphabet)]) for v in randoms)) for alphabet in alphabets]
    sequences.extend([
        ('low8-hex',bytes(v&255 for v in randoms[:48]).hex().encode()),
        ('low8-HEX',bytes(v&255 for v in randoms[:48]).hex().upper().encode()),
        ('rand32-hex',''.join(f'{v:08x}' for v in randoms[:12]).encode()),
        ('rand-decimal',''.join(str(v) for v in randoms[:12]).encode()),
    ])
    for label,value in sequences:
        count+=1;start=ctypes.c_size_t();length=ctypes.c_size_t()
        if lib.find_password(value,len(value),ctypes.byref(start),ctypes.byref(length)):
            password=value[start.value:start.value+length.value]
            hits.append({'seed':seed,'generator':label,'offset':start.value,'password':password.decode()})
            (HERE/'archive_password.txt').write_bytes(password)
report={'seeds':[1788884900,1788885300],'generated_sequences':count,'all_substrings_up_to':128,'matches':hits}
(HERE/'password_rng_results.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
