import pefile, pathlib, hashlib, struct
KEY=b'On_My_0wN'
def rc4(key,data):
    S=list(range(256)); j=0
    out=bytearray()
    for i in range(256):
        j=(j+S[i]+key[i%len(key)])&255
        S[i],S[j]=S[j],S[i]
    i=j=0
    for c in data:
        i=(i+1)&255; j=(j+S[i])&255; S[i],S[j]=S[j],S[i]
        out.append(c ^ S[(S[i]+S[j])&255])
    return bytes(out)
pe=pefile.PE('REZero.exe')
for e in pe.DIRECTORY_ENTRY_RESOURCE.entries:
    name=str(e.name) if e.name else str(e.id)
    for e2 in e.directory.entries:
        name2=str(e2.name) if e2.name else str(e2.id)
        for e3 in e2.directory.entries:
            data=e3.data.struct
            raw=pe.get_memory_mapped_image()[data.OffsetToData:data.OffsetToData+data.Size]
            print('res',name,name2,e3.id,'rva',hex(data.OffsetToData),'size',data.Size,'sha',hashlib.sha256(raw).hexdigest()[:16])
            open(f'res_{name}_{name2}_{e3.id}.bin','wb').write(raw)
            if name=='EMILIA':
                dec=rc4(KEY,raw)
                open('EMILIA_decrypted.bin','wb').write(dec)
                print('decrypted',len(dec),dec[:16].hex(), 'sha256', hashlib.sha256(dec).hexdigest())
