#!/usr/bin/env python3
from pathlib import Path
import json
import re
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent
MP3 = ROOT / "osint_unknown-artist" / "Brunnerne Inc.mp3"
ZIP = ROOT / "osint_unknown-artist.zip"
FLAG_TXT = ROOT / "flag.txt"
PROGRESS = Path("/home/light/GitHub/gpt/scratch/ctf-runs/unknown-artist/progress.json")

def synchsafe(b: bytes) -> int:
    return (b[0] << 21) | (b[1] << 14) | (b[2] << 7) | b[3]

def parse_id3v24(data: bytes):
    tags = {}
    if data[:3] != b"ID3":
        return tags, 0
    tag_end = 10 + synchsafe(data[6:10])
    pos = 10
    while pos + 10 <= tag_end:
        fid = data[pos:pos+4].decode("latin1", "replace")
        size = int.from_bytes(data[pos+4:pos+8], "big")
        if not fid.strip("\x00") or size <= 0 or pos + 10 + size > len(data):
            break
        body = data[pos+10:pos+10+size]
        tags.setdefault(fid, []).append(body)
        pos += 10 + size
    return tags, tag_end

def decode_text_frame(body: bytes) -> str:
    if not body:
        return ""
    enc = body[0]
    raw = body[1:]
    if enc == 0:
        return raw.decode("latin1", "replace").rstrip("\x00")
    if enc == 1:
        return raw.decode("utf-16", "replace").rstrip("\x00")
    if enc == 2:
        return raw.decode("utf-16-be", "replace").rstrip("\x00")
    if enc == 3:
        return raw.decode("utf-8", "replace").rstrip("\x00")
    return raw.decode("utf-8", "replace").rstrip("\x00")

def decode_uslt(body: bytes) -> str:
    if not body:
        return ""
    enc = body[0]
    rest = body[4:] if len(body) >= 4 else b""
    # USLT body = encoding byte + language(3) + content descriptor + text.
    if enc == 1:
        parts = rest.split(b"\x00\x00", 1)
        text = parts[1] if len(parts) == 2 else rest
        return text.decode("utf-16", "replace").lstrip("\ufeff\x00").rstrip("\x00")
    if enc == 0:
        parts = rest.split(b"\x00", 1)
        text = parts[1] if len(parts) == 2 else rest
        return text.decode("latin1", "replace").rstrip("\x00")
    if enc == 3:
        parts = rest.split(b"\x00", 1)
        text = parts[1] if len(parts) == 2 else rest
        return text.decode("utf-8", "replace").rstrip("\x00")
    return rest.decode("utf-8", "replace").rstrip("\x00")

def main():
    if not MP3.exists():
        raise SystemExit(f"missing extracted MP3: {MP3}; unzip {ZIP.name} first")

    data = MP3.read_bytes()
    tags, tag_end = parse_id3v24(data)
    urls = re.findall(rb"https?://[^\x00\s\"']+", data)
    uuids = re.findall(rb"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", data, re.I)
    flags = re.findall(rb"(?:brunner|flag)\{[^}]+\}", data, re.I)

    title = decode_text_frame(tags.get("TIT2", [b""])[0])
    source_url = tags.get("WOAS", [b""])[0].decode("latin1", "replace").rstrip("\x00")
    lyrics = decode_uslt(tags.get("USLT", [b""])[0])
    lyric_lines = [ln.strip() for ln in lyrics.splitlines() if ln.strip() and not ln.startswith("[")]

    result = {
        "challenge": "Unknown Artist",
        "status": "local_analysis_complete_pending_online_profile_lookup",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "workspace": str(ROOT),
        "mp3": str(MP3),
        "id3_tag_end": tag_end,
        "title": title,
        "source_url": source_url,
        "song_uuid": uuids[0].decode() if uuids else None,
        "local_flags_found": [f.decode("utf-8", "replace") for f in flags],
        "local_findings": [
            "Archive contains a single MP3.",
            "MP3 has ID3v2.4 metadata with title, source URL, lyrics, and cover art.",
            "Source URL points to a Suno song UUID.",
            "Lyrics explicitly say: search the profile, match the ID; two tracks are published on a hidden page and one is a decoy.",
            "No brunner{...} or flag{...} string was found in local bytes.",
            "Cover art metadata/strings and basic stego checks did not reveal a local flag.",
            "Per the no-remote rule, online Suno profile lookup was not performed."
        ],
        "lyrics_first_letters": "".join(ln[0] for ln in lyric_lines if ln),
        "next_step_requires_user_permission": "Open/fetch the Suno song/profile page for the UUID and inspect the artist profile/other track."
    }

    PROGRESS.parent.mkdir(parents=True, exist_ok=True)
    PROGRESS.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    FLAG_TXT.write_text("PENDING_ONLINE_LOOKUP\n")
    print("[*] Local analysis complete.")
    print(f"TITLE: {title}")
    print(f"SOURCE_URL: {source_url}")
    print(f"SONG_UUID: {result['song_uuid']}")
    print("FLAG: PENDING_ONLINE_LOOKUP")
    print("DONE")

if __name__ == "__main__":
    main()
