# Analysis: Weirdo (Misc 500)

## 1. Challenge Overview
- **File**: `challenge/here` (PCAP capture file, ~52 MB, 556,262 packets)
- **Time range**: 2026-09-10 01:45:05 to 2026-09-10 02:51:11 (~66 minutes)
- **Transport**: 100% UDP traffic on port 14550 (Standard MAVLink port)
- **Endpoints**:
  - `10.13.37.50:14550` -> `10.13.37.10:14550` (SysID 1)
  - `10.13.37.51:14550` -> `10.13.37.10:14550` (SysID 2)
  - `10.13.37.52:14550` -> `10.13.37.10:14550` (SysID 3, duration ~1980s, anomalous "Weirdo")
  - `10.13.37.53:14550` -> `10.13.37.10:14550` (SysID 4)
- **GCS**: `10.13.37.10`
- **Protocol**: MAVLink v2 (magic byte `0xFD`).

---

## 2. Trajectory Analysis: The "Weirdo" Drone (SysID 3)
1. **The Anomaly**:
   - Drones 1, 2, and 4 fly normal survey grids for ~3950s.
   - Drone 3 (IP `10.13.37.52`) flies for only ~1980s.
   - Plotting Drone 3's GPS path (`GLOBAL_POSITION_INT`, msg 33) and rotating by ~31° aligns the flight trajectory horizontally.
2. **Decoded Skywriting Text**:
   - Line 1: `reisen_1943 said:`
   - Line 2: `b1rd5_4r3nt_r34l_th3y_ch4rg3_0n_p0w3rl1n3s`
3. **Submission Result**:
   - Attempt 1 (`pow3rl1n3s`): Incorrect.
   - Attempt 2 (`p0w3rl1n3s` with leetspeak `0`): **Correct! (Platform accepted: `{"status": "correct", "message": "Correct"}`)**

---

## 3. The Decoy Layer: STATUSTEXT Telemetry
The author deliberately created an elaborate rabbit hole inside `STATUSTEXT` (msg 253):
- Drone 1 sent interleaved fragments with 1-bit noise alongside an MD5 hash:
  `use this md5 to verify the flag`
  `FLAG_MD5: 1e375de6074f25cd86ddab22948b5064`
- The MD5 matched `th3_sky_1s_n0t_r34l_5acb9c6b`, but this was a decoy to mislead anyone relying solely on packet text parsing instead of plotting the actual 2D GPS trajectories of the drones.

---

## 4. Final Flag
```
CSCV2026{b1rd5_4r3nt_r34l_th3y_ch4rg3_0n_p0w3rl1n3s}
```
