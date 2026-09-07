#!/usr/bin/env python3
# Solution for: Min beste venn (forensics)
# Chatflare covert channel: Cloudflare cache HIT/MISS as bits.
# Sender warms only 1-bits (d/<dir>/<seq>/<byte><bit>.css), receiver probes all bits.
# Capture contains both sides -> each 1-bit URL appears twice, 0-bit appears once.
# So bit=1 iff URI occurs >=2 times. First byte is message length.
import re
import tarfile
import collections
from pathlib import Path

def find_pcap():
    base = Path(__file__).resolve().parent.parent
    candidates = list(base.rglob("capture.pcap")) + list(base.rglob("*.pcap"))
    if candidates:
        return candidates[0]
    # try extracting tar.gz
    for tgz in base.rglob("*.tar.gz"):
        try:
            with tarfile.open(tgz, "r:gz") as tf:
                for m in tf.getmembers():
                    if m.name.endswith(".pcap"):
                        out = Path("/tmp/opencode_minbeste") / Path(m.name).name
                        out.parent.mkdir(parents=True, exist_ok=True)
                        tf.extract(m, path="/tmp/opencode_minbeste", filter="fully_trusted")
                        # find extracted
                        for p in Path("/tmp/opencode_minbeste").rglob("*.pcap"):
                            return p
        except Exception:
            continue
    raise FileNotFoundError("capture.pcap not found")

def bitmap_to_byte(bits):
    acc = 0
    for i, b in enumerate(bits):
        if b:
            acc |= 1 << (7 - i)
    return acc

def solve():
    pcap = find_pcap()
    print(f"[*] Using pcap: {pcap}")
    data = Path(pcap).read_bytes()
    # HEAD /cf<id>/d/<dir>/<seq>/<byte><bit>.css  (also h/s and c/s signalling, ignored)
    raw_uris = re.findall(rb"HEAD (/cf[^ ]+?)\.css", data)
    print(f"[*] Total HEAD requests: {len(raw_uris)}")
    counts = collections.Counter(raw_uris)
    print(f"[*] Unique URIs: {len(counts)}")

    groups = collections.defaultdict(set)  # (dir,seq) -> set of all paths
    ones = collections.defaultdict(set)    # (dir,seq) -> set of paths seen >=2 (bit=1)
    pat = re.compile(rb"/cf[^/]+/d/([^/]+)/([^/]+)/(.+)")
    for uri, c in counts.items():
        m = pat.match(uri)
        if not m:
            continue
        direction, seq, bitpath = m.group(1).decode(), m.group(2).decode(), m.group(3).decode()
        key = (direction, seq)
        groups[key].add(bitpath)
        if c >= 2:
            ones[key].add(bitpath)

    for key in sorted(groups):
        all_paths = groups[key]
        hit_paths = ones[key]
        # parse byte/bit: last char = bit index, rest = byte index
        def parse(p):
            return int(p[:-1]), int(p[-1])
        maxbyte = max(parse(p)[0] for p in all_paths)
        raw = []
        for b in range(maxbyte + 1):
            bits = [f"{b}{i}" in hit_paths for i in range(8)]
            raw.append(bitmap_to_byte(bits))
        size = raw[0]
        payload = bytes(raw[1:])
        # sanity: unique should be 8+size*8
        assert len(all_paths) == 8 + size * 8, f"{key}: unique {len(all_paths)} != 8+{size}*8"
        assert len(payload) == size, f"{key}: payload len {len(payload)} != size {size}"
        try:
            text = payload.decode()
        except Exception:
            text = repr(payload)
        print(f"[+] d/{key[0]}/{key[1]}: size={size} msg={text!r}")
        if b"NNS{" in payload:
            print(f"FLAG: {text}")

if __name__ == "__main__":
    solve()
