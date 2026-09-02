from pathlib import Path

def decrypt_file(fn):
    b=Path(fn).read_bytes()
    # constructor: PUSH4 deployed_len PUSH1 0x10 PUSH0 CODECOPY PUSH4 deployed_len PUSH0 RETURN
    dep_len=int.from_bytes(b[1:5],'big')
    runtime=b[16:16+dep_len]
    assert runtime[0]==0x7f and runtime[33]==0x63 and runtime[38]==0x63 and runtime[43]==0x0c
    key=runtime[1:33]
    start=int.from_bytes(runtime[34:38],'big')
    length=int.from_bytes(runtime[39:43],'big')
    enc=runtime[start:start+((length+31)//32)*32]
    dec=bytes(c ^ key[j%32] for j,c in enumerate(enc))[:length]
    return dep_len, key.hex(), start, length, dec

for i in range(1,5):
    dep_len,key,start,length,dec=decrypt_file(f'challenge_{i}.bin')
    Path(f'challenge_{i}.dec').write_bytes(dec)
    print(i, 'dep_len',dep_len,'key',key,'start',start,'len',length,'dec_head',dec[:32].hex(),'dec_tail',dec[-32:].hex())
