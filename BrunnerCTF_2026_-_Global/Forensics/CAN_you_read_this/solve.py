#!/usr/bin/env python3
"""Solution for: CAN you read this (Forensics, BrunnerCTF 2026)

The secret is Morse code flashed with the car's high-beam stalk.
Signal: ID 0x249 (SCCM_leftStalk), SCCM_highBeamStalkStatus
(start bit 12, len 2, little-endian) — Tesla Model 3 vehicle bus DBC.

ON pulses: dots ~0.13-0.18 s, dashes ~0.41-0.96 s -> threshold 0.30 s.
Letter/word spacing is human-keyed and sloppy -> threshold grid + dictionary.
"""
import os

M = {'.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E', '..-.': 'F',
     '--.': 'G', '....': 'H', '..': 'I', '.---': 'J', '-.-': 'K', '.-..': 'L',
     '--': 'M', '-.': 'N', '---': 'O', '.--.': 'P', '--.-': 'Q', '.-.': 'R',
     '...': 'S', '-': 'T', '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X',
     '-.--': 'Y', '--..': 'Z'}
WORDS = {"HIDDEN", "IN", "PLAIN", "LIGHT", "THE", "AND", "A", "I", "IS", "IT",
         "TO", "OF", "FOR", "WITH", "ON", "AT", "BY", "FROM", "CAN", "CAR",
         "SECRET", "NOT", "ARE", "YOU", "THIS", "THAT", "HAVE", "WAS", "WERE"}


def parse(path):
    frames = []
    with open(path) as f:
        for line in f:
            p = line.split()
            if len(p) < 6 or p[3] not in ("Rx", "Tx"):
                continue
            try:
                ts, cid, dlc = float(p[0]), p[2], int(p[5])
            except ValueError:
                continue
            frames.append((ts, cid, [int(x, 16) for x in p[6:6 + dlc]]))
    return frames


def ext(b, start, length):
    """Little-endian bit extraction of a signal from payload bytes."""
    v = 0
    for i in range(length):
        bit = start + i
        if bit // 8 < len(b):
            v |= ((b[bit // 8] >> (bit % 8)) & 1) << i
    return v


def extract_runs(frames):
    """(val, duration) runs of the high-beam stalk signal (ID 0x249)."""
    sig = sorted((ts, 1 if ext(b, 12, 2) else 0) for ts, cid, b in frames if cid == "249")
    runs, val, st = [], sig[0][1], sig[0][0]
    for ts, v in sig[1:]:
        if v != val:
            runs.append((val, st, ts)); val, st = v, ts
    runs.append((val, st, sig[-1][0]))
    return [(v, e - s) for v, s, e in runs][1:-1]


def decode_with(runs, dd, cg, wg):
    out, cur = [], ""
    for v, d in runs:
        if v == 1:
            cur += '-' if d >= dd else '.'
        elif d >= wg:
            if cur:
                out.append(cur); cur = ""
            out.append(" ")
        elif d >= cg:
            if cur:
                out.append(cur); cur = ""
    if cur:
        out.append(cur)
    return "".join(" " if t == " " else M.get(t, "?") for t in out)


def word_group(s):
    words = []
    i = 0
    while i < len(s):
        if s[i] == ' ':
            i += 1
            continue
        matched = False
        for L in range(min(8, len(s) - i), 0, -1):
            if s[i:i + L] in WORDS:
                words.append(s[i:i + L])
                i += L
                matched = True
                break
        if not matched:
            words.append(s[i]); i += 1
    return " ".join(words)


def score_phrase(phrase):
    return sum(len(w) * len(w) if w in WORDS else 1 for w in phrase.split())


def main():
    base = os.path.dirname(os.path.abspath(__file__))
    log = os.path.join(base, "forensics_can-you-read-this", "can-recording-model-3.asc")
    frames = parse(log)
    runs = extract_runs(frames)

    best = None
    for dd in (0.28, 0.30, 0.32, 0.35):
        for cg in (x / 100 for x in range(60, 95)):
            for wg in (x / 100 for x in range(95, 151)):
                if cg >= wg:
                    continue
                msg = " ".join(decode_with(runs, dd, cg, wg).split())
                phrase = word_group(msg)
                sc = score_phrase(phrase)
                if best is None or sc > best[0]:
                    best = (sc, dd, cg, wg, phrase)

    _, dd, cg, wg, phrase = best
    print("Raw Morse:", "".join('-' if d >= 0.30 else '.' for v, d in runs if v == 1))
    print(f"Thresholds: dot/dash={dd} char_gap={cg} word_gap={wg}")
    print("Decoded:", phrase)
    print("Flag:", "brunner{" + phrase.lower().replace(" ", "_") + "}")


if __name__ == "__main__":
    main()
