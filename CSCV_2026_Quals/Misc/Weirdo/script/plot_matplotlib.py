#!/usr/bin/env python3
import struct
from collections import defaultdict
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

PCAP_PATH = "challenge/here"

def plot_trajectories():
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

    # Plot each sysid individually
    for s in [1, 2, 3, 4]:
        pts = coords[s]
        if not pts: continue
        lons = [p[1] for p in pts]
        lats = [p[2] for p in pts]
        
        plt.figure(figsize=(16, 10), dpi=300)
        plt.plot(lons, lats, color='blue', linewidth=0.8, alpha=0.9)
        plt.title(f"SysID {s} Trajectory ({len(pts)} points)")
        plt.xlabel("Longitude")
        plt.ylabel("Latitude")
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.tight_layout()
        plt.savefig(f"script/traj_sys_{s}.png")
        plt.close()
        print(f"[+] Saved script/traj_sys_{s}.png")

    # Plot all combined
    plt.figure(figsize=(20, 12), dpi=300)
    colors = {1: 'red', 2: 'green', 3: 'blue', 4: 'orange'}
    for s in [1, 2, 3, 4]:
        pts = coords[s]
        if not pts: continue
        plt.plot([p[1] for p in pts], [p[2] for p in pts], color=colors[s], label=f"SysID {s}", linewidth=0.8, alpha=0.8)
    plt.legend()
    plt.title("All Drone Trajectories")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig("script/traj_all.png")
    plt.close()
    print("[+] Saved script/traj_all.png")

if __name__ == "__main__":
    plot_trajectories()
