# MASTER FINDINGS — pwn_3in1

## Round 2 — 2026-06-28 ~06:20 GMT+7

### Overall Status

| Agent | Status | Confidence |
|-------|--------|------------|
| recon-agent | ✅ SOLVED | high |
| guest-runtime-agent | ✅ SOLVED (JS exec) | high |
| orchestration-infra-agent | ⚠️ BLOCKED (nsjail mknod) | medium |
| build-debug-agent | ✅ COMPLETE | high |
| js-vuln-agent | ✅ IN_PROGRESS | medium |
| js-source-agent | ⏳ RUNNING | - |
| exploit-primitive-agent | ⏳ NOT STARTED | - |

### Key Discoveries This Round

#### 1. Full guest chain confirmed working
- Cần pad payload lên 512-byte boundary (raw block device)
- **QEMU debug binary đã chạy được PoC JS** thành công
- Output:
  ```
  "Hello from pwn_3in1 guest!"
  "typeof gc:" "function"
  "typeof console:" "object"
  "typeof JSON:" "object"
  "typeof ArrayBuffer:" "function"
  "typeof Uint8Array:" "function"
  "gc() works!"
  "ArrayBuffer works!"
  ```
- QEMU exit 0, JS hoạt động đầy đủ

#### 2. QEMU debug binary sẵn sàng
- Path: `work/shared/qemu-debug/qemu-system-x86_64`
- File: ELF 64-bit, not stripped, debug_info, 73MB
- Version: QEMU 11.0.50
- Both patches applied, device virtio-sound-pci present

#### 3. Docker bị block bởi nsjail mknod
- `docker compose up` fail vì rootless Docker không support mknod device node
- Workaround: QEMU local trực tiếp (đã kiểm chứng)

#### 4. JS Engine attack surface
- **Ladybird LibJS** (commit 53a956c68c03)
- **Chỉ còn**: `gc()`, `console.log`, `JSON`, Typed Arrays, standard ECMA-262
- **Không**: require/import/fetch/XMLHttpRequest/process/fs
- **Rust bytecode compiler** (không phải machine-code JIT) — loại trừ JIT spraying
- **Rust symbols**: `rust_compile_function`, `rust_materialize_compiled_function`, `rust_validate_bytecode`
- **GC**: LibGC (block-based allocator, mark-sweep collect_garbage)
- **GC Symbols**: `GC::Heap::collect_garbage`, `GC::CellAllocator::allocate_cell`, `GC::HeapBlock`
- `asm_interpreter_entry` — assembly interpreter entry
- **Cần audit**: TypedArray implementation + GC interaction (potential UAF/OOB)

### Next Round (Round 3) Plan
1. Chờ deep-research kết quả: CVE/bug Ladybird LibJS
2. Chờ js-source-agent: source code TypedArray/GC audit
3. exploit-primitive-agent: Khi đã có bug path → heap layout GDB analysis
4. orchestration-infra-agent: Cần QEMU local test script thay vì Docker

## Round: exploit-primitive-agent — Heap Overflow Analysis

### New Findings

1. **Vulnerability confirmed**: Missing `MIN(to_read, max_size - buffer->size)` in
   `virtio_snd_pcm_in_cb` (qemu_1.patch). `audio_be_read()` writes silence data
   beyond allocated PCM buffer's flexible array.

2. **Trigger mechanism**: `-audiodev none` with `in.mixing-engine=off` causes
   `audio_run_in()` to call callback with `available = INT_MAX`. Guest can set
   `period_bytes` up to UINT32_MAX with no bounds check. Rate control via
   `audio_rate_get_bytes()` limits per-call overflow to ~256KB (65536-frame cap).

3. **Overflow content**: Depends on audio format (guest-chosen via SET_PARAMS).
   Signed formats (S8/S16/S32/FLOAT) -> zeros. Unsigned formats (U8/U16/U32) ->
   non-zero patterns (0x80 per byte for U8, 0x7FFF per sample for U16).

4. **Critical size class aliasing**: `VirtIOSoundPCMBuffer` (48B),
   `virtio_snd_ctrl_command` (48B), and `QEMUTimer` (48B) all allocate same
   glibc chunk size (0x40 = 64 bytes) -> same tcache bin. Enables heap aliasing:
   free ctrl_command, then allocate PCM buffer on same location.

5. **Key struct details**:
   - PCMBuffer data[] starts at offset 48 from buffer
   - SWVoiceIn has `callback.fn` function pointer at offset 136
   - QEMUTimer has `cb` function pointer at offset 16
   - PCMStream has QSIMPLEQ_HEAD { *sqh_first, **sqh_last } at offset 184

6. **glibc 2.42**: Has safe-linking (PROTECT_PTR, since 2.32), tcache keys (since
   2.29), TCACHE_MAX_BINS=33. Tcache poisoning requires knowing heap addr >> 12.

### Still Needed
- Heap grooming strategy evaluation (which objects can be adjacent)
- QEMU 11.0.50 QOM type verification
- Concrete test harness to verify overflow
- Exploitation path selection
