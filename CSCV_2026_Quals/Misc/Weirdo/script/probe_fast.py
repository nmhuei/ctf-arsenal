#!/usr/bin/env python3
import struct
from collections import Counter, defaultdict

PCAP_PATH = "challenge/here"

def parse_pcap():
    print("[*] Parsing PCAP...")
    msg_counts = defaultdict(Counter)
    sys_ips = defaultdict(Counter)
    
    with open(PCAP_PATH, "rb") as f:
        global_header = f.read(24)
        if len(global_header) < 24:
            print("[-] Invalid PCAP header")
            return
            
        magic = global_header[:4]
        # Check endianness
        if magic == b'\xd4\xc3\xb2\xa1':
            endian = '<'
        elif magic == b'\xa1\xb2\xc3\xd4':
            endian = '>'
        else:
            print(f"[-] Unknown magic: {magic}")
            return
            
        pkt_idx = 0
        while True:
            rec_hdr = f.read(16)
            if len(rec_hdr) < 16:
                break
            ts_sec, ts_usec, incl_len, orig_len = struct.unpack(endian + 'IIII', rec_hdr)
            pkt_data = f.read(incl_len)
            if len(pkt_data) < incl_len:
                break
                
            pkt_idx += 1
            
            # Ethernet header (14 bytes)
            if len(pkt_data) < 14 + 20 + 8:
                continue
            eth_type = struct.unpack('>H', pkt_data[12:14])[0]
            if eth_type != 0x0800:
                continue
                
            # IPv4 header
            ip_hdr = pkt_data[14:34]
            src_ip = f"{ip_hdr[12]}.{ip_hdr[13]}.{ip_hdr[14]}.{ip_hdr[15]}"
            dst_ip = f"{ip_hdr[16]}.{ip_hdr[17]}.{ip_hdr[18]}.{ip_hdr[19]}"
            proto = ip_hdr[9]
            ihl = (ip_hdr[0] & 0x0F) * 4
            
            if proto != 17: # UDP
                continue
                
            udp_start = 14 + ihl
            udp_hdr = pkt_data[udp_start:udp_start+8]
            src_port, dst_port = struct.unpack('>HH', udp_hdr[:4])
            
            udp_payload = pkt_data[udp_start+8:]
            
            # Parse MAVLink packets inside payload
            # A UDP packet can contain one or more MAVLink packets
            offset = 0
            while offset < len(udp_payload):
                magic_byte = udp_payload[offset]
                if magic_byte == 0xFD: # MAVLink v2
                    if offset + 10 > len(udp_payload):
                        break
                    pay_len = udp_payload[offset+1]
                    incompat = udp_payload[offset+2]
                    compat = udp_payload[offset+3]
                    seq = udp_payload[offset+4]
                    sysid = udp_payload[offset+5]
                    compid = udp_payload[offset+6]
                    msgid = udp_payload[offset+7] | (udp_payload[offset+8] << 8) | (udp_payload[offset+9] << 16)
                    
                    has_sig = 13 if (incompat & 0x01) else 0
                    total_pkt_len = 10 + pay_len + 2 + has_sig
                    
                    msg_counts[sysid][msgid] += 1
                    sys_ips[sysid][src_ip] += 1
                    
                    offset += total_pkt_len
                elif magic_byte == 0xFE: # MAVLink v1
                    if offset + 6 > len(udp_payload):
                        break
                    pay_len = udp_payload[offset+1]
                    seq = udp_payload[offset+2]
                    sysid = udp_payload[offset+3]
                    compid = udp_payload[offset+4]
                    msgid = udp_payload[offset+5]
                    total_pkt_len = 6 + pay_len + 2
                    msg_counts[sysid][msgid] += 1
                    sys_ips[sysid][src_ip] += 1
                    offset += total_pkt_len
                else:
                    offset += 1

    print(f"[+] Total packets processed: {pkt_idx}")
    print("[+] System IDs and their IPs:")
    for sysid, ips in sys_ips.items():
        print(f"    SysID {sysid}: {dict(ips)}")
        
    print("\n[+] Message counts per System ID:")
    for sysid, counts in sorted(msg_counts.items()):
        print(f"\n--- SysID {sysid} (Total msgs: {sum(counts.values())}) ---")
        for msgid, cnt in counts.most_common(20):
            print(f"    MsgID {msgid:5d} (0x{msgid:04x}): {cnt} packets")

if __name__ == "__main__":
    parse_pcap()
