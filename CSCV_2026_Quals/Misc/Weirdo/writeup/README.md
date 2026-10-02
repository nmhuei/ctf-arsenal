# Weirdo — Writeup

## Summary
- **Category**: Misc
- **Points**: 500
- **Flag**: `CSCV2026{b1rd5_4r3nt_r34l_th3y_ch4rg3_0n_p0w3rl1n3s}`

---

## 1. Rationale & Triage

1. **Protocol Identification**:
   - Initial inspection of `challenge/here` revealed a ~52 MB PCAP capture file with 556,262 packets.
   - Using `capinfos` and `tshark -q -z conv,udp`, 100% of the packets were UDP traffic on port `14550`.
   - Port 14550 is the standard port for the **MAVLink** (Micro Air Vehicle Link) drone telemetry protocol.
   - Inspecting packet headers identified the MAVLink v2 framing byte `0xFD`.
   - Four drone systems (System IDs 1, 2, 3, 4) were communicating with a Ground Control Station at `10.13.37.10`.

---

## 2. Discovery Triggers & The "Weirdo" Anomaly

1. **The Duration & Route Anomaly**:
   - Drones 1, 2, and 4 maintained active telemetry for ~3,950 seconds.
   - Drone 3 (IP `10.13.37.52`) stopped transmitting at ~1,980 seconds — roughly half the duration.
   - The challenge name **"Weirdo"** directly hinted at the one drone that behaved differently from the rest of the swarm.

2. **Trajectory Visualization (Skywriting)**:
   - Extracting GPS coordinates from `GLOBAL_POSITION_INT` (message ID 33) and plotting 2D coordinates revealed that Drones 1, 2, and 4 flew standard search/grid survey patterns.
   - Drone 3 flew a highly deliberate path, drawing distinct cursive and block characters across the coordinates.
   - Rotating the coordinate plane by ~31° counter-clockwise aligned the text horizontally:
     - **Top Line**: `reisen_1943 said:`
     - **Bottom Line**: `b1rd5_4r3nt_r34l_th3y_ch4rg3_0n_p0w3rl1n3s`

---

## 3. Dead-ends & Decoy Dissection

1. **The STATUSTEXT Rabbit Hole**:
   - Examining `STATUSTEXT` (message ID 253) revealed a complex multi-drone sequence where Drone 1 broadcasted fragmented strings with single-bit noise (`th3_sk`, `y_1s_n`, `0tWr34`, `l_5acb`, `9c6b`) alongside:
     ```text
     use this md5 to verify the flag
     FLAG_MD5: 1e375de6074f25cd86ddab22948b5064
     ```
   - While `th3_sky_1s_n0t_r34l_5acb9c6b` matched the MD5 verification hash, the platform rejected this submission.
   - The author had designed the `STATUSTEXT` MD5 puzzle as an elaborate rabbit hole for automated or text-only solvers, while the true flag was visually drawn in the physical skywriting of the "Weirdo" drone.

---

## 4. Verification & Submission

1. **Leetspeak Validation**:
   - Testing `CSCV2026{b1rd5_4r3nt_r34l_th3y_ch4rg3_0n_pow3rl1n3s}` returned `incorrect`.
   - Testing with leetspeak `0` in `p0w3rl1n3s`: `CSCV2026{b1rd5_4r3nt_r34l_th3y_ch4rg3_0n_p0w3rl1n3s}` returned:
     ```json
     {"status": "correct", "message": "Correct"}
     ```

## Final Flag
```
CSCV2026{b1rd5_4r3nt_r34l_th3y_ch4rg3_0n_p0w3rl1n3s}
```
