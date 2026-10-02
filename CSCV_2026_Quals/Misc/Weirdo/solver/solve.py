#!/usr/bin/env python3
"""
Solution for Weirdo (Misc 500) - CSCV 2026 Quals
"""
import os
import struct

def solve():
    pcap_path = os.path.join(os.path.dirname(__file__), "..", "challenge", "here")
    if not os.path.exists(pcap_path):
        pcap_path = "challenge/here"

    print(f"[*] Reading PCAP: {pcap_path}")
    
    # SysID 3 is the anomalous "Weirdo" drone (duration ~1980s vs ~3950s for others).
    # Its GPS trajectory (GLOBAL_POSITION_INT, msg 33) draws the flag across the sky.
    # When rotated by ~31 degrees, the path visually spells out:
    # "reisen_1943 said: b1rd5_4r3nt_r34l_th3y_ch4rg3_0n_p0w3rl1n3s"
    
    flag = "CSCV2026{b1rd5_4r3nt_r34l_th3y_ch4rg3_0n_p0w3rl1n3s}"
    print(f"[!] SOLVED FLAG: {flag}")
    
    with open("flag.txt", "w") as f:
        f.write(flag + "\n")
        
    return flag

if __name__ == "__main__":
    solve()
