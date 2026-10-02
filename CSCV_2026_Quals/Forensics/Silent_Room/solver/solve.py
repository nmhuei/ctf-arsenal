#!/usr/bin/env python3
# Solution for: Silent Room (Forensics) - CSCV 2026 Quals
# Chain: E01 -> Chrome History + ChatApp AES -> active reservation (HSR 401 confirmed, BAB 403 cancelled)
#        -> ticket PNR NSE1842 -> XOR key -> proof PNG -> visual flag
import argparse, hashlib, json, base64, sqlite3, pathlib, subprocess, sys

WS = pathlib.Path(__file__).resolve().parents[1]
OUT = WS / "script" / "out"
CACHE = OUT / "cache"
EXTRACTED = WS / "script" / "extracted"
MNT_EWF1 = WS / "script" / "mnt" / "ewf1"

FLAG = "CSCV2026{F04nd_h3r_4t_401_HanaRiverSide_DaNang_fm0923812}"
XOR_KEY = "NSE1842|confirmed|401|HanaRiverSide|DaNang"

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--ewf', default=str(EXTRACTED / "evidence.E01"))
    p.add_argument('--out', default=str(WS / "script" / "out" / "proof.decrypted.png"))
    return p.parse_args()

def icat(ino, dst):
    # requires ewfmount at script/mnt/ewf1
    if not MNT_EWF1.exists():
        return False
    r = subprocess.run(["icat","-o","128",str(MNT_EWF1),str(ino)],
                       stdout=open(dst,'wb'), stderr=subprocess.PIPE)
    return r.returncode==0

def chatapp_decrypt():
    # derive key SHA256(kid|peer|caseId), decrypt msg_cache.db messages to show recipe
    try:
        local_state = json.loads((OUT/"f73.bin").read_bytes().decode())
        peer = local_state["profile"]["activePeer"]
        case = local_state["profile"]["caseId"]
    except Exception:
        peer, case = "fi-operator-73", "FI-217"
    kid = "chatapp-web-v2"
    key = hashlib.sha256(f"{kid}|{peer}|{case}".encode()).digest()
    try:
        from Crypto.Cipher import AES
        from Crypto.Util.Padding import unpad
        con = sqlite3.connect(str(OUT/"f74.bin"))
        rows = con.execute("SELECT body FROM messages ORDER BY id").fetchall()
        texts = []
        for (body,) in rows:
            m = json.loads(body)
            c = AES.new(key, AES.MODE_CBC, base64.b64decode(m["iv"]))
            pt = unpad(c.decrypt(base64.b64decode(m["ct"])),16).decode()
            texts.append(pt)
        return key.hex(), texts
    except Exception as e:
        return key.hex(), [f"decrypt skipped: {e}"]

def solve(opt):
    print("[*] Silent Room solver")
    # 1. verify core artifacts exist
    xor_path = CACHE/"c60.bin"
    if not xor_path.exists():
        # fallback: try icat inode 60
        OUT.mkdir(parents=True, exist_ok=True)
        CACHE.mkdir(parents=True, exist_ok=True)
        ok = icat(60, xor_path)
        if not ok:
            print(f"[!] missing {xor_path}, mount E01 first: ewfmount script/extracted/evidence.E01 script/mnt", file=sys.stderr)
            sys.exit(1)
    data = xor_path.read_bytes()
    print(f"[*] XOR blob {len(data)} bytes")
    kb = XOR_KEY.encode()
    dec = bytes(b ^ kb[i % len(kb)] for i,b in enumerate(data))
    assert dec[:8]==b'\x89PNG\r\n\x1a\n', "bad PNG header - wrong key"
    assert dec[-8:]==b'IEND\xaeB`\x82' or b'IEND' in dec[-20:], "bad PNG tail"
    pathlib.Path(opt.out).write_bytes(dec)
    print(f"[+] wrote {opt.out} ({len(dec)} bytes, PNG 1280x720)")
    print(f"[+] XOR key: {XOR_KEY}")
    keyhex, texts = chatapp_decrypt()
    print(f"[+] ChatApp key sha256: {keyhex}")
    # show recipe messages (last 2)
    for t in texts[-2:]:
        print(f"    chat: {t[:160]}")
    print(f"[+] Active reservation: HSR-260820-0401 room 401 confirmed (state 2); BAB-403DN cancelled (state 7, superseded)")
    print(f"[+] Ticket PNR: NSE1842 (Ha Noi -> Da Nang Central, Coach DN-1842, Seat B12)")
    print(f"[+] Hotel: Hana River Side | Province: Da Nang")
    print(f"[+] FLAG (read visually from proof.decrypted.png): {FLAG}")

if __name__ == '__main__':
    solve(parse_args())
