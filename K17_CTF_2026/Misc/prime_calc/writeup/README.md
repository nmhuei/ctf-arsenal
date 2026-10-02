# Writeup: prime calc (K17 CTF 2026)

- **Category**: Misc / Web
- **Points**: 189
- **Status**: Solved ✅
- **Flag**: `K17{d1d_y0u_l1k3_mY_fRont3nD_de$iGn?}`

---

## 1. Vulnerability Analysis

### A. Path Traversal File Overwrite (`/api/config`)
In `src/app.py`:
```python
@app.post("/api/config")
def upload_config():
    uploaded = request.files.get("config")
    timestamp = request.form.get("timestamp", "")
...
    if not timestamp[0].isdigit():
        return jsonify(error="timestamp must be numeric"), 400

    name = timestamp if Path(timestamp).suffix else timestamp + ".json"
    destination = (CONFIG_DIR / name).resolve()
    if destination != BASE_DIR.resolve() and BASE_DIR.resolve() not in destination.parents:
        return jsonify(error="invalid config path"), 400
    destination.parent.mkdir(parents=True, exist_ok=True)
    uploaded.save(destination)
```
- By sending `timestamp = "1/../../checkpoint.dmtcp"`:
  - `timestamp[0].isdigit()` is True (`1`).
  - `Path(timestamp).suffix` is `.dmtcp`.
  - `destination` resolves to `/app/data/checkpoint.dmtcp`.
  - `BASE_DIR.resolve() in destination.parents` is True since `/app/data` is the parent of `/app/data/checkpoint.dmtcp`.
  - `uploaded.save(destination)` writes the uploaded bytes directly to `/app/data/checkpoint.dmtcp`.
  - While subsequent `json.loads(destination.read_text())` fails and returns HTTP 400, the file on disk has already been overwritten.

### B. Dynamic DMTCP Checkpoint Injection (`dmtcp_restart`)
- The server uses DMTCP v4.2.0 (Distributed MultiThreaded CheckPointing).
- `/api/snapshot` allows downloading the active `checkpoint.dmtcp`.
- In DMTCP, `checkpoint.dmtcp` is a gzip-compressed binary snapshot of the entire virtual process space.
- The DMTCP checkpoint header contains `postRestartAddr` (offset 248 / `0xF8`), pointing to `ThreadList::postRestart` inside `libdmtcp.so`.
- When `dmtcp_restart` finishes restoring memory regions, `mtcp_restart.c` calls:
  ```c
  fnptr_post_restart_t post_restart_fptr =
    (fnptr_post_restart_t) rinfo->ckptHdr.postRestartAddr;
  post_restart_fptr(readTime, rinfo->restart_pause);
  ```
- **Zero-Hardcoding Dynamic Offset Discovery**:
  - The solver reads `postRestartAddr` from the checkpoint header.
  - It iterates through the Area header records across the checkpoint to find the mapping where `mapping_start <= postRestartAddr < mapping_end` and `mapping_name` matches `libdmtcp.so`.
  - The Area header is patched to `prot = 7` (RWX), `flags = 0x32` (MAP_PRIVATE | MAP_ANONYMOUS), and name cleared.
  - The exact payload offset `area_hdr_offset + 0x1000 + (postRestartAddr - mapping_start)` is overwritten with custom shellcode.
  - Works dynamically across different kernels, distributions, and compiler configurations.

### C. Shellcode Execution
- The shellcode opens `/flag` (readable by group `prime`), reads the flag content, and writes it directly to:
  - `/app/data/output/latest.txt`
  - `/app/data/output/status.txt`
  - Calls `exit(0)`.
- When `POST /api/run` triggers `worker.py once`, `latest.txt` is updated with the flag and returned in the HTTP response or accessible via `/api/status`.

---

## 2. Exploitation Script
See [`solver/solve.py`](../solver/solve.py).
