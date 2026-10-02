# Collector code constants audit

## Prior-work audit

The existing `script/offline_audit/zipcrypto_constant_hits.json` already contains 11 exact little-endian occurrences of the ZIPCrypto multiplier `0x08088405`, with instruction contexts. Therefore earlier work did search implementation constants, in addition to runtime keys and PLT signatures. Those offsets were reused and validated against memory; the multiplier search was not repeated.

No saved whole-memory scan was located for the CRC polynomial, initial-key constants, or compact hash constants. `scan_constants.py` closes that bounded gap using exact little-endian bytes and ripgrep JSON offsets. It reads the validated `script/evidence/mem.clean` without modifying evidence. It does not execute captured code.

## Scan scope and results

| Constant | Hits |
|---|---:|
| CRC polynomial `edb88320` |145|
| ZIP initial key0 `12345678` |429|
| ZIP initial key1 `23456789` |715|
| ZIP initial key2 `34567890` |11|
| FNV32 basis `811c9dc5` |74|
| FNV32 prime `01000193` |996|
| FNV64 basis `cbf29ce484222325` |72|
| Legacy shortened FNV64 basis `14650fb0739d0383` |0|
| FNV64 prime `00000100000001b3` |124|
| djb2 basis 5381 |1,939|
| sdbm multiplier 65599 |859|
| ZIP multiplier (reused prior results) |11|

Total: 5,375 constant occurrences. These are signatures, not identified functions. Many are data and duplicate memory copies.

For each hit the script examines a 2,048-byte neighborhood for raw absolute values in `0x403000..0x403190`, and direct-CALL byte patterns that can be translated into two expected PLT slots while placing the constant in collector text `0x401000..0x4022f5`.

The relative-call test is deliberately permissive: it produced 733 hit neighborhoods with an arithmetic mapping. Such mappings are **not validated instruction boundaries, executable bases, or collector identifications**. Nearby relative calls occur throughout unrelated libraries. These raw results are retained for transparency in `constant_neighborhoods.json`.

## ZIPCrypto instruction findings

`initial_key2_context.asm` contains disassembly around all 11 occurrences of the most distinctive initial-key constant. Three neighborhoods contain recognizable ZIPCrypto routines:

- `0xcc51d0c0`: initializes key2 and packs key0/key1 in a 64-bit immediate. Nearby calls include `0xcc51d089 -> 0xcc49b27e` and `0xcc51d0f9 -> 0xcc4e090e`. These separations are far larger than the collector's text segment.
- `0x10b90ee71`: initializes all three keys in a large object at offsets `0x10158/0x10160/0x10168`; the same routine calls from `0x10b90ee65` to `0x111381f5e`, incompatible with the collector's small ET_EXEC layout.
- `0x19af16bfe`: recognizable password-key initialization, followed in the same nearby code region by a call from `0x19af16c9e` to `0x191513b7e`. Additional nearby code uses large RIP-relative displacements and large object offsets. This does not establish collector provenance.

The existing multiplier hits include these larger-component routines and two identical high-entropy/data contexts. No multiplier or key2 neighborhood contains a raw absolute reference into the collector's known small rodata range. Exact containing-library attribution was not established and is not claimed.

## Raw low-address matches

Six hash-constant neighborhoods contain raw values in the requested low rodata range. They are structured data, not recovered collector instructions:

- `0x35229777`, `0x40b747b7`, `0xed1ed835`, `0x1aadbb8b3` share the same data layout. The supposed sdbm constant crosses the byte representation of a floating-point-looking value and an adjacent integer; `0x403100` values occur in repeated fields.
- `0x11347c6a6` is a sparse table/record with `0x1505` and nearby `0x403000`.
- `0x1e3a5bff6` is a pointer-rich heap record with `0x1003f` and nearby `0x403100`.

Their exact contexts and offsets are preserved in `constant_neighborhoods.json`.

## Conclusion and limitations

No attributable collector code page or password-formation routine was recovered. This audit provides no new password candidate and does not support selecting FNV, djb2, sdbm, or CRC-based password generation. The absence of a supported match does not prove that all collector code is absent: optimized constants, split pages, data transformations, unknown carve alignment, and code without these signatures remain outside the demonstrated result. No additional speculative scan was launched after this bounded review.
