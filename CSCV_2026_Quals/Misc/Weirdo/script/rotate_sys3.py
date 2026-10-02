#!/usr/bin/env python3
import struct
import math
from collections import defaultdict
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

PCAP_PATH = "challenge/here"

def get_sys3_coords():
    pts = []
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
                if sysid == 3 and msgid == 33: # GLOBAL_POSITION_INT
                    lat, lon = struct.unpack("<ii", p[14:22])
                    pts.append((lon / 1e7, lat / 1e7))
    return pts

def rotate_and_plot():
    pts = np.array(get_sys3_coords())
    print(f"[+] Loaded {len(pts)} points for SysID 3")
    
    # Calculate angle of principal axis or try angles around 30-35 degrees
    # Center points
    mean = np.mean(pts, axis=0)
    centered = pts - mean
    
    # PCA to find angle
    cov = np.cov(centered, rowvar=False)
    evals, evecs = np.linalg.eigh(cov)
    main_dir = evecs[:, np.argmax(evals)]
    angle_rad = np.arctan2(main_dir[1], main_dir[0])
    angle_deg = np.degrees(angle_rad)
    print(f"[+] Detected principal angle: {angle_deg:.2f} degrees")
    
    # We want text to be horizontal. Try angle_rad and test a few variations
    for test_angle_deg in [angle_deg, angle_deg + 180, -31.0, 31.0, -32.5, 32.5]:
        theta = np.radians(test_angle_deg)
        # Rotation matrix: rotate by -theta to align with X axis
        # [ cos(-theta) -sin(-theta) ]
        # [ sin(-theta)  cos(-theta) ]
        R = np.array([
            [np.cos(-theta), -np.sin(-theta)],
            [np.sin(-theta),  np.cos(-theta)]
        ])
        rotated = centered @ R.T
        
        # Plot
        plt.figure(figsize=(24, 8), dpi=300)
        plt.plot(rotated[:, 0], rotated[:, 1], color='#0033aa', linewidth=1.2, alpha=0.9)
        plt.title(f"SysID 3 rotated by {-test_angle_deg:.1f} deg")
        plt.axis('equal')
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.tight_layout()
        plt.savefig(f"script/sys3_rot_{test_angle_deg:.1f}.png")
        plt.close()
        print(f"[+] Saved script/sys3_rot_{test_angle_deg:.1f}.png")

if __name__ == "__main__":
    rotate_and_plot()
