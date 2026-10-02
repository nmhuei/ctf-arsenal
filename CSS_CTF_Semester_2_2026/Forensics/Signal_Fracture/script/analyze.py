import subprocess, binascii, struct, hashlib, os
from pathlib import Path
pcap='/tmp/Signal_Fracture_extract/KBR17_uplink.pcap'
# get payloads from tshark
out=subprocess.check_output(['tshark','-r',pcap,'-T','fields','-e','udp.payload'], text=True)
records=[]
for line in out.splitlines():
    if line.startswith('4e584652'):
        b=bytes.fromhex(line)
        magic,sess,seq,total,length,crc=struct.unpack('>4sIHHII',b[:20])
        records.append((seq, b[20:20+length], hashlib.sha256(b[20:20+length]).hexdigest()))
print('PCAP')
for r in records: print(r[0], r[2], len(r[1]))
for f in ['/tmp/signal_files/30','/tmp/signal_files/31','/tmp/signal_files/32']:
    b=open(f,'rb').read()
    print('BLOB',f,len(b))
    # raw may contain records
    for i in range(len(b)-20):
        if b[i:i+4]==b'NXFR':
            magic,sess,seq,total,length,crc=struct.unpack('>4sIHHII',b[i:i+20])
            p=b[i+20:i+20+length]
            print(' ',seq,hashlib.sha256(p).hexdigest(),len(p))
