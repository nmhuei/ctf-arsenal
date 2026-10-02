#!/usr/bin/env python3
import struct
from collections import defaultdict

PCAP_PATH = "challenge/here"

def plot_svg():
    coords = defaultdict(list)
    with open(PCAP_PATH, "rb") as f:
        hdr = f.read(24)
        while True:
            rec = f.read(16)
            if len(rec) < 16: break
            ts_sec, ts_usec, l, _ = struct.unpack("<IIII", rec)
            d = f.read(l)
            if len(d) < 42: continue
            p = d[42:]
            if len(p) >= 10 and p[0] == 0xFD:
                pay_len = p[1]
                sysid = p[5]
                msgid = p[7] | (p[8]<<8) | (p[9]<<16)
                if msgid == 33: # GLOBAL_POSITION_INT
                    lat, lon = struct.unpack("<ii", p[14:22])
                    coords[sysid].append((lon / 1e7, lat / 1e7))

    all_lons = [pt[0] for pts in coords.values() for pt in pts]
    all_lats = [pt[1] for pts in coords.values() for pt in pts]
    min_x, max_x = min(all_lons), max(all_lons)
    min_y, max_y = min(all_lats), max(all_lats)
    print(f"X (Lon): {min_x} to {max_x}")
    print(f"Y (Lat): {min_y} to {max_y}")

    width = 1200
    height = 800
    margin = 50

    colors = {1: "red", 2: "blue", 3: "green", 4: "orange"}

    def transform(x, y):
        sx = margin + (x - min_x) / (max_x - min_x) * (width - 2 * margin)
        sy = height - margin - (y - min_y) / (max_y - min_y) * (height - 2 * margin)
        return sx, sy

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" style="background-color: #1e1e1e;">']
    
    for sysid, pts in coords.items():
        color = colors.get(sysid, "white")
        path_data = []
        for i, (x, y) in enumerate(pts):
            sx, sy = transform(x, y)
            cmd = "M" if i == 0 else "L"
            path_data.append(f"{cmd}{sx:.1f},{sy:.1f}")
        svg.append(f'<path d="{" ".join(path_data)}" fill="none" stroke="{color}" stroke-width="1.5" opacity="0.8" />')

    svg.append('</svg>')

    with open("script/trajectories_global_pos.svg", "w") as f:
        f.write("\n".join(svg))
    print("[+] Saved script/trajectories_global_pos.svg")

if __name__ == "__main__":
    plot_svg()
