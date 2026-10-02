# Silent Room - analysis
Target: CSCV_2026_Quals / Forensics / Silent_Room (id 18)
Evidence: E01 2.0GiB, MD5 abb90c7772c153b2d37633065e71f670, 1 NTFS partition (offset 128)

## Triage
- `ewfmount evidence.E01 script/mnt`, `mmls` -> 1 NTFS, `fls -o 128 -r` full tree.
- Users/A/{Documents/Downloads/Pictures}, AppData/{Local/Google/Chrome, Local/Programs/ChatApp, Roaming/ChatApp}, Recent, Prefetch.
- Key files:
  - Downloads/booking_BAB_403_receipt.html (ALLOCATED): Babarian Hotel, Room 403, Da Nang, CONFIRMED, BAB-403DN, 2026-08-20. DECOY (old).
  - Downloads/booking_HSR_260820_preview.png + ticket_DN1842.png (DELETED, init_size 0) -> carve via Chrome Cache instead.
  - Chrome History (inode 61): 11 urls - stayhub BAB-403DN, stayhub HSR-260820-0401, northstar NSE1842, maps dir Da Nang Central Bus Terminal -> M-4412, gov notice 217, scholarship, searches (video-call police?, money laundering, cyberchef xor, Noi Bai->Da Nang, hotel check-in tre).
  - Chrome Cache_Data: f_000020 (STAYHUB_STATE 1:draft 2:confirmed 4:checked_in 7:cancelled 9:expired), f_000021 BAB-403DN supersededBy HSR-260820-0401, f_000033 (c56.png) ticket PNG, f_000054 (c58.png) preview PNG, f_000089 (c60.bin, 57289B) XOR proof, metadata op=XOR key=UTF-8.
  - leveldb: stayhub:last_viewed BAB-403DN state=7 replace_with=HSR-260820-0401; activeReservation HSR-260820-0401 lodgingRef R8QK-72M-19 roomNumber 401 state=2 mapPinKey M-4412.
  - Roaming/ChatApp/msg_cache.db: 15 AES-256-CBC msgs (kid chatapp-web-v2). Local State peer fi-operator-73 case FI-217. app.bundle.js deriveKey=SHA256(kid|peer|caseId).
  - Decrypted chat (VI): coercion as FI-217 investigators, PNR is part of comparison key, delete ticket+booking after viewing, old screenshot outdated vs system, final image XOR-locked, key order: PNR|status words|room|lodging nospace|province nospace.
  - notice_217.pdf: fake FI-217 urgent verification notice (VPF-73), lure to video-call + bank/wallet sync. Decoy, not location.
  - Pictures/Camera Roll 13 JPGs: personal decoys.
  - thumbnail_cache_hint.txt: warns preview deleted, recover from deleted/RecycleBin, don't trust chat text.
  - Prefetch CHROME.EXE synthetic.

## Why HSR-401-current (not BAB-403)
- BAB-403DN state 7 = cancelled, supersededBy HSR, last_viewed replaced 2026-08-20T06:58:09+07.
- HSR state 2 = confirmed, activeReservation room 401, checkin 19:00-22:00 2026-08-20, cityCode DAD, geo 16.071:108.229 (Da Nang), mapPin M-4412 matches Maps history.
- Chat msgs 9,11,13 explicitly say old screenshot outdated, follow active system code.
- Ticket: NorthStar Express Ha Noi (My Dinh) -> Da Nang Central, 07:25-18:45 2026-08-20, Seat B12, Coach DN-1842, PNR NSE1842. Consistent with bus-terminal origin.

## Key build
- PNR NSE1842 (ticket PNG c56, scan NSE1842-DAD-B12)
- status "confirmed" (state 2 lowercase mapping; CONFIRMED STAY header uppercase but key needs lowercase - verified by PNG header/IEND)
- room 401 (activeReservation, proof still shows 401 Hana River Side Da Nang)
- hotel nospace HanaRiverSide (preview PNG "Hana River Side")
- province nospace DaNang ("Da Nang", DAD)
- XOR_KEY = NSE1842|confirmed|401|HanaRiverSide|DaNang -> decrypts c60.bin to valid PNG 1280x720 (IHDR + IEND ok).

## Proof
- `python3 solver/solve.py` -> script/out/proof.decrypted.png, visual flag CSCV2026{F04nd_h3r_4t_401_HanaRiverSide_DaNang_fm0923812}, case media id fm0923812.
- Extraction: inode 60 (f_000089) via icat from ewf1; header 89504E47..., tail IEND.

## Dead ends
- icat 82/84 directly gives zeros (deleted init_size 0) -> pivoted to Chrome cache PNGs.
- Single-byte XOR brute unnecessary once recipe known; status case (CONFIRMED vs confirmed) and province case (Danang vs DaNang) tested via header+IEND.
- QR in ticket/preview/proof not decodable via opencv/zbar (QR sym unsupported) - not needed, text readable.
- Pictures EXIF empty, PDF only lure, todo/scholarship only background (old CCCD, FI-217 linkage).

## Candidate
- CANDIDATE -> VERIFIED (local PNG decrypt + visual read): CSCV2026{F04nd_h3r_4t_401_HanaRiverSide_DaNang_fm0923812}
