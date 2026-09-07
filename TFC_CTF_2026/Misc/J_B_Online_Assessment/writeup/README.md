# Writeup: J*B Online Assessment

| Property | Value |
| :--- | :--- |
| **Category** | `Misc` |
| **Points** | `109` |
| **Author** | `cr0` |
| **Solves** | `129` |

---

## 📝 Challenge Overview

The challenge presents a Cisco Packet Tracer activity file (`job-oa.pka`) that requires 100% completion (122 signed configuration markers) to get the flag from a web verification endpoint (`POST /api/submit`).

---

## 🔍 Reconnaissance & Vulnerability Analysis

1. **Packet Tracer Encryption Mechanism (`.pka` / `.pkt`):**
   - Cisco Packet Tracer activity files are encrypted using Twofish in EAX mode with hardcoded static keys:
     - Key: `bytes([137]) * 16` (`0x89` repeated 16 times)
     - IV / Nonce: `bytes([16]) * 16` (`0x10` repeated 16 times)
   - The ciphertext undergoes a two-stage XOR byte shuffling/obfuscation layer, followed by Qt's `qCompress` (4-byte big-endian uncompressed size prefix + zlib compression).
   - Once decrypted, the payload is an XML document representing the entire activity.

2. **Activity XML Structure:**
   - The root element `<PACKETTRACER5_ACTIVITY>` contains three `<PACKETTRACER5>` network configuration blocks:
     - **Block 1 (lines 4 - 121,370):** Initial student topology state (unconfigured/partial).
     - **Block 2 (lines 121,371 - 242,763):** Intermediate reference state.
     - **Block 3 (lines 242,764 - 392,057):** The author's fully completed answer network state (configured routers, switch ports, routes, IPs, etc.).

3. **Backend Assessment Verification:**
   - The backend runs a verification engine that checks for 122 configuration markers.
   - When the uncompleted activity is submitted, it returns:
     `{"ok":false,"message":"Relay incomplete: 18/122 signed configuration markers recovered."}`
   - Because the completed target state is stored directly inside Block 3 of the activity file, replacing Block 1 with Block 3 gives the student file a 100% completed state.

---

## 💻 Exploitation Strategy & PoC

1. Decrypt `job-oa.pka` to extract the XML string.
2. Locate the three `<PACKETTRACER5>` blocks using regex.
3. Replace Block 1 (initial network state) with the exact content of Block 3 (the answer network state).
4. Compress and re-encrypt the XML back into a valid `.pka` container using Twofish-EAX and Qt byte shuffling.
5. Submit the re-encrypted `.pka` payload to `POST /api/submit`.

The complete automated exploit script is available at [`../solver/solve.py`](../solver/solve.py).

```bash
python3 ../solver/solve.py https://j-b-online-assessment-40c7f9a9b1261b04.challs.ctf.thefewchosen.com
```

### Output:
```json
{"ok":true,"message":"J*B Online Assessment complete. You're hired.","matched":122,"required":122,"flag":"TFCCTF{cheating_is_the_only_way_to_get_a_job_in_2026}"}
```

---

## 🚩 Flag

- Status: `[x] Solved`
- Flag: `TFCCTF{cheating_is_the_only_way_to_get_a_job_in_2026}`
