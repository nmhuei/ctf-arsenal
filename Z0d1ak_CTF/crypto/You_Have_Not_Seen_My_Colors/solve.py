#!/usr/bin/env python3
"""Solution for: You Have Not Seen My Colors (z0d1akCTF 2026 Qualifiers, crypto).

Method:
1. The 100x100 RGB PNG is visual noise (9,996 unique colors / 10,000 px).
2. Channel analysis: Red and Green use every byte value 1..255 but NO zero;
   Blue has exactly 166 pixels equal to 0.  Those blue==0 pixels are a
   reserved sentinel hiding the message.
3. Masking B==0 pixels reveals four lines written in Elian script:
       ZEK
       MASTER
       OF
       CTF
   ("ZEK" is the author's signature, not part of the answer.)
4. The private endpoint answer (lowercase, underscores) is master_of_ctf.
5. Endpoint returns the flag.
"""
from PIL import Image


def extract(image_path: str) -> tuple[list, tuple, str]:
    im = Image.open(image_path)
    px = im.load()
    w, h = im.size
    marked = [(x, y) for y in range(h) for x in range(w) if px[x, y][2] == 0]
    xs = [p[0] for p in marked]
    ys = [p[1] for p in marked]
    bbox = (min(xs), min(ys), max(xs), max(ys))
    # Render enlarged mask for visual confirmation of the Elian glyphs.
    out = Image.new("RGB", (w, h), (0, 0, 0))
    for (x, y) in marked:
        out.putpixel((x, y), (255, 255, 255))
    mask = out.crop((bbox[0] - 1, bbox[1] - 1, bbox[2] + 2, bbox[3] + 2))
    mask = mask.resize((mask.width * 10, mask.height * 10), Image.NEAREST)
    mask.save("decoded-mask.png")
    return marked, bbox, "master_of_ctf"


if __name__ == "__main__":
    marked, bbox, answer = extract("image.png")
    print(f"[+] blue-zero pixels: {len(marked)}")
    print(f"[+] carrier bounding box: {bbox}")
    print("[+] Elian transcription: ZEK / MASTER / OF / CTF")
    print("[+] decoded answer: %s" % answer)
    print("[+] flag: zdk{m4S7er_OF_C0l0rs_4nD_C7f}")
