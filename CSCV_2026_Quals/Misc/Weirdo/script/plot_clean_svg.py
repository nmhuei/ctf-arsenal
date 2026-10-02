#!/usr/bin/env python3
import struct
from collections import defaultdict

PCAP_PATH = "challenge/here"

def extract_coords():
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
                    coords[sysid].append((ts_sec + ts_usec*1e-6, lon / 1e7, lat / 1e7))
    return coords

def save_svg(pts_dict, filename, width=3000, height=2000):
    all_lons = [pt[1] for pts in pts_dict.values() for pt in pts]
    all_lats = [pt[2] for pts in pts_dict.values() for pt in pts]
    if not all_lons: return
    min_x, max_x = min(all_lons), max(all_lons)
    min_y, max_y = min(all_lats), max(all_lats)
    dx = max_x - min_x or 1e-9
    dy = max_y - min_y or 1e-9
    margin = 50

    colors = {1: "#e6194b", 2: "#3cb44b", 3: "#0082c8", 4: "#f58231"}

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" fill="#ffffff"/>'
    ]

    def transform(x, y):
        sx = margin + (x - min_x) / dx * (width - 2 * margin)
        sy = height - margin - (y - min_y) / dy * (height - 2 * margin)
        return sx, sy

    for sysid, pts in pts_dict.items():
        c = colors.get(sysid, "#000000")
        path_cmds = []
        for i, pt in enumerate(pts):
            sx, sy = transform(pt[1], pt[2])
            cmd = "M" if i == 0 else "L"
            path_cmds.append(f"{cmd} {sx:.2f} {sy:.2f}")
        svg.append(f'<path d="{" ".join(path_cmds)}" fill="none" stroke="{c}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round" />')

    svg.append('</svg>')
    with open(filename, "w") as f:
        f.write("\n".join(svg))
    print(f"[+] Saved {filename}")

if __name__ == "__main__":
    coords = extract_coords()
    # Save individual sysids
    for s in [1, 2, 3, 4]:
        save_svg({s: coords[s]}, f"script/sys_{s}.svg")
    save_svg(coords, "script/sys_all.svg")
