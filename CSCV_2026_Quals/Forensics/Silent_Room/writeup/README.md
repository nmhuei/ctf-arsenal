# Writeup: Silent Room

| Property | Value |
| :--- | :--- |
| **Category** | `Forensics` |
| **Points** | `100` |
| **Author** | `-` |
| **Solves** | `217` |

---

## 📝 Challenge Overview

> A 17-year-old girl named A left home for unclear reasons. After being unable to
> contact her for a while, her family reported the case to the authorities. You
> are given an image extracted from A's computer to look for traces that can
> identify A's current location.
>
> Determine the most likely current room, hotel, and province/city. The final flag
> is recovered from the evidence image itself.

- E01 2GiB, NTFS, synthetic laptop evidence SilentRoom-001.

---

## 🔍 Reconnaissance & Vulnerability Analysis

- Target: `challenge/here` (7z, 5.0M) -> `evidence.E01` (9.9M) + logs.
- Mount: `ewfmount evidence.E01 script/mnt`, `mmls` 1 NTFS at 128, `fls -o 128 -r`.
- First anomaly: Downloads has 1 allocated receipt (BAB-403) + 2 deleted PNGs (HSR preview, ticket) with `init_size 0` - classic superseded-booking pattern, not just missing files.
- Second trigger: `thumbnail_cache_hint.txt` explicitly says preview deleted, recover elsewhere, don't trust chat text - points to cache/carving, not chat.
- Chrome History 11 URLs gave timeline: BAB receipt -> NSE ticket -> HSR reservation -> maps M-4412 -> xor research. Order matters: HSR after BAB.
- `app.bundle.js` 541B contained `deriveKey=SHA256(kid|peer|caseId)` - tiny file, huge value; searched because msg_cache bodies looked like `{"v":2,"kid":"chatapp-web-v2","alg":"AES-256-CBC"}`.
- Research trail: no web needed except local `pdftotext`, `exiftool`, `icat/istat`, OpenCV QR (failed, pivoted). GCHQ Chef hint in cache metadata confirmed repeating-XOR UTF-8.

## 💻 Exploitation Strategy & PoC

1. Extracted History (61), Local State (73), msg_cache (74), bundle (70) via `icat -o 128`.
2. Derived ChatApp key `SHA256(chatapp-web-v2|fi-operator-73|FI-217)=5cc72b55...` and decrypted 15 msgs. Messages 6-9/11/13-15 gave recipe and warning: PNR secret, delete files, old screenshot stale, XOR key order `PNR|status|room|hotel-nospace|province-nospace`.
3. Resolved current booking via cache JSON + leveldb, not HTML receipt:
   - `STAYHUB_STATE`: 2=confirmed, 7=cancelled.
   - BAB-403DN: state 7, `supersededBy HSR-260820-0401`.
   - HSR: state 2, room 401, lodgingRef R8QK-72M-19, DAD, 16.071:108.229, M-4412.
4. Recovered ticket PNR from cache PNG (f_000033 -> NorthStar Express, PNR NSE1842, DN-1842, B12, Ha Noi->Da Nang Central) and hotel/province from preview PNG (f_000054 -> Hana River Side, Da Nang, HSR-260820-0401, R8QK-72M-19). Used `read` image render, not strings.
5. Built `NSE1842|confirmed|401|HanaRiverSide|DaNang`, XOR-decrypted f_000089 (c60.bin, 57289B) -> valid PNG 1280x720 `LOCATION CONFIRMATION STILL / 401 Hana River Side Da Nang / CSCV2026{...} / fm0923812`.
6. Verified via header `89 50 4E 47...` + tail `IEND`, rejected `CONFIRMED`/`Danang` variants (header spaces / `IENd`).

Exploit script: [`../solver/solve.py`](../solver/solve.py).

```bash
python3 solver/solve.py --out script/out/proof.decrypted.png
```

## Dead-ends & Pivots

- `icat 82/84` zeros -> abandoned MFT-direct, pivoted to Chrome `Cache_Data` PNGs (same content, allocated).
- `CONFIRMED` uppercase and `Danang` lowercase both give near-PNG headers but fail IEND - used tail check to pick `confirmed`/`DaNang`.
- QR decode via `zbarimg`/OpenCV failed (unsupported/synthetic) - skipped, text layer sufficient.
- 13 Camera Roll JPGs + PDF notice + todo/scholarship: background/lure only, confirmed via exif/content, not location.

---

## 🚩 Flag

- Status: `- [x] Solved`
- Flag: `CSCV2026{F04nd_h3r_4t_401_HanaRiverSide_DaNang_fm0923812}` (submitted ✔ server `solved_by_me=True`; see `../script/analysis.md`, `../flag.txt`)
