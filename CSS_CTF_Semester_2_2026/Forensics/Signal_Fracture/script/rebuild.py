import subprocess,struct,hashlib
pcap='/tmp/Signal_Fracture_extract/KBR17_uplink.pcap'
frags={}
for line in subprocess.check_output(['tshark','-r',pcap,'-T','fields','-e','udp.payload'],text=True).splitlines():
    if line.startswith('4e584652'):
        b=bytes.fromhex(line); _,_,seq,_,l,_=struct.unpack('>4sIHHII',b[:20]); frags[seq]=b[20:20+l]
for path in ['/tmp/signal_files/30','/tmp/signal_files/31','/tmp/signal_files/32']:
    b=open(path,'rb').read(); m,s,seq,_,l,_=struct.unpack('>4sIHHII',b[:20]); frags[seq]=b[20:20+l]
for off,seq,l in [(27525120,0,841),(30539776,2,841),(34144256,5,840)]:
    with open('/tmp/Signal_Fracture_extract/KBR17_relay.img','rb') as f:
        f.seek(off+20); frags[seq]=f.read(l)
for i in range(8): print(i,len(frags[i]),hashlib.sha256(frags[i]).hexdigest())
open('/tmp/emergency_burst_17.tar','wb').write(b''.join(frags[i] for i in range(8)))
