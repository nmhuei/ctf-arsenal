#!/usr/bin/env python3
import struct
from collections import defaultdict

PCAP_PATH = "challenge/here"

# We want to extract for each drone:
# timestamps, lat, lon, alt, relative_alt from msg 33 (GLOBAL_POSITION_INT)
# and msg 24 (GPS_RAW_INT), and msg 124 (GPS2_RAW)

def analyze_positions():
    print("[*] Extracting position data...")
    data_33 = defaultdict(list)
    data_24 = defaultdict(list)
    data_124 = defaultdict(list)
    
    with open(PCAP_PATH, "rb") as f:
        hdr = f.read(24)
        while True:
            rec = f.read(16)
            if len(rec) < 16: break
            ts_sec, ts_usec, l, _ = struct.unpack("<IIII", rec)
            t = ts_sec + ts_usec * 1e-6
            d = f.read(l)
            if len(d) < 42: continue
            p = d[42:]
            if len(p) >= 10 and p[0] == 0xFD:
                pay_len = p[1]
                sysid = p[5]
                msgid = p[7] | (p[8]<<8) | (p[9]<<16)
                payload = p[10:10+pay_len]
                
                if msgid == 33: # GLOBAL_POSITION_INT
                    # uint32 time_boot_ms, int32 lat, int32 lon, int32 alt, int32 relative_alt, int16 vx, int16 vy, int16 vz, uint16 hdg
                    if len(payload) >= 28:
                        time_boot, lat, lon, alt, rel_alt, vx, vy, vz, hdg = struct.unpack("<IiiiihhhH", payload[:28])
                        data_33[sysid].append((t, time_boot, lat, lon, alt, rel_alt, vx, vy, vz, hdg))
                        
                elif msgid == 24: # GPS_RAW_INT
                    # uint64 time_usec, int32 lat, int32 lon, int32 alt, uint16 eph, uint16 epv, uint16 vel, uint16 cog, uint8 fix_type, uint8 sats
                    if len(payload) >= 30:
                        time_usec, lat, lon, alt, eph, epv, vel, cog, fix_type, sats = struct.unpack("<QiiiHHHHBB", payload[:30])
                        data_24[sysid].append((t, time_usec, lat, lon, alt, eph, epv, vel, cog, fix_type, sats))

                elif msgid == 124: # GPS2_RAW
                    # uint64 time_usec, int32 lat, int32 lon, int32 alt, uint16 eph, uint16 epv, uint16 vel, uint16 cog, uint8 fix_type, uint8 sats, uint8 dgps_numch, uint32 dgps_age
                    if len(payload) >= 35:
                        time_usec, lat, lon, alt, eph, epv, vel, cog, fix_type, sats = struct.unpack("<QiiiHHHHBB", payload[:30])
                        data_124[sysid].append((t, time_usec, lat, lon, alt, eph, epv, vel, cog, fix_type, sats))

    for sysid in sorted(data_33.keys()):
        pts = data_33[sysid]
        print(f"\n[+] SysID {sysid} - GLOBAL_POSITION_INT: {len(pts)} points")
        lats = [p[2] / 1e7 for p in pts]
        lons = [p[3] / 1e7 for p in pts]
        alts = [p[4] / 1000.0 for p in pts]
        rel_alts = [p[5] / 1000.0 for p in pts]
        print(f"    Lat range: {min(lats):.7f} to {max(lats):.7f}")
        print(f"    Lon range: {min(lons):.7f} to {max(lons):.7f}")
        print(f"    Alt range: {min(alts):.2f}m to {max(alts):.2f}m")
        print(f"    Rel Alt range: {min(rel_alts):.2f}m to {max(rel_alts):.2f}m")

    for sysid in sorted(data_24.keys()):
        pts = data_24[sysid]
        print(f"\n[+] SysID {sysid} - GPS_RAW_INT: {len(pts)} points")
        fix_types = set(p[9] for p in pts)
        sat_counts = set(p[10] for p in pts)
        print(f"    Fix types: {fix_types}, Sats: {min(sat_counts)}..{max(sat_counts)}")

    for sysid in sorted(data_124.keys()):
        pts = data_124[sysid]
        print(f"\n[+] SysID {sysid} - GPS2_RAW: {len(pts)} points")
        fix_types = set(p[9] for p in pts)
        sat_counts = set(p[10] for p in pts)
        print(f"    Fix types: {fix_types}, Sats: {min(sat_counts)}..{max(sat_counts)}")

if __name__ == "__main__":
    analyze_positions()
