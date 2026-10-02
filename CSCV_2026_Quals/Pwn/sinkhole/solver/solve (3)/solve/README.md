# sinkhole — solution

Renderer RCE in the patched Chromium 153.0.8010.0 via the injected Maglev pass
`MaglevSmiCheckElimination`.

## The bug

`v8-src/src/maglev/maglev-smi-check-elimination.cc`:

```cpp
void MaglevSmiCheckElimination::CollectGuardedIndices() {
  ... if (check->deoptimize_reason() != DeoptimizeReason::kOutOfBounds) continue;
      if (check->condition() != AssertCondition::kUnsignedLessThan) continue;
      guarded_.insert(check->input(0).node()->UnwrapIdentities());
}
void MaglevSmiCheckElimination::NarrowGuardedUntags() {
  for (ValueNode* index : guarded_) {
    if (!index->Is<CheckedObjectToIndex>() && !index->Is<CheckedSmiUntag>()) continue;
    index->OverwriteWith<UnsafeSmiUntag>();      // <-- unsound
  }
}
```

The "tidy story" is *"the value is bounds-checked, so the checked conversion is
redundant"*. It is backwards: the bounds check consumes the **result** of the
untag and proves nothing about the **input**. Worse, the pass is purely
syntactic — the check only has to exist *somewhere in the graph*, not on the
path that executes.

Dropping `CheckedSmiUntag` does not just remove a deopt; it invalidates the
`NodeType::kSmi` that `KnownNodeAspects` recorded for the *input* while the
graph was built. Two things were derived from that lie:

1. `x + 1` on a HeapObject becomes `sar` on a compressed pointer
   → **addrof** for free, no deopt.
2. `MaglevReducer::CanElideWriteBarrier()` returns true for
   `CheckType(value, NodeType::kSmi)`, so `arr[0] = x` is emitted as
   `StoreFixedArrayElementNoWriteBarrier`
   → an old→new pointer that the scavenger never records → **UAF**.

Both added passes bail out on `graph_->num_blocks() <= 1024`, which is why the
9000-case test suite never built a graph that reaches them. The victim function
is padded with 1200 `if` statements to get past that gate.

## Chain

| Step | Primitive |
|---|---|
| 1 | `x + 1` on an object → `(compressed_addr >> 1)` — **addrof** |
| 2 | `objArr[0] = obj` without a write barrier, objArr in old space |
| 3 | 2 scavenges → `objArr[0]` dangles at the victim's old young-gen address |
| 4 | spray `[41 doubles]` arrays over that address → **fake object with a controlled header** |
| 5 | fake `JSObject` (map of `{}`) + hijacked `elements` → cage R/W |
| 6 | corrupt a sprayed array's `FixedDoubleArray.length` → OOB double R/W |
| 7 | overwrite `Float64Array.external_pointer` (+48) → **arbitrary process R/W** (the V8 sandbox is off in this build, `backing_store` is a raw inline pointer) |
| 8 | `WasmInstanceObject+12` → `WasmTrustedInstanceData+40` = `jump_table_start`; follow the `jmp rel32` to the code body |
| 9 | write shellcode there (`--no-memory-protection-keys` keeps the page writable), call the exported wasm function |
| 10 | shellcode `open("/flag")` + `read()` into the ArrayBuffer backing store; JS reads it back and exfiltrates |

No `--allow-natives-syntax` and no `--expose-gc`: minor GCs are forced by
allocating until an `addrof` canary moves, and the function reaches Maglev
naturally after ~19k calls (it is far too large for Turbofan, so it never tiers
past Maglev and the bug stays live).

Only three constants are baked in, all snapshot-derived and identical in every
run of this build: the map of `{}` (`0x1029d4d`), the map of `new Map()`
(`0x1038f2d`, used only to verify the fake-object slot) and the object layout
offsets. The `PACKED_DOUBLE` JSArray map is recovered at runtime.

## Usage

```bash
# serve it somewhere the bot can reach, then
nc 113.20.103.216 31337
# URL to visit (http/https only): https://<your-host>/exploit.html
```

The flag is sent back to the page's own origin as
`GET /flag_is?f=<flag>` (also as a `sendBeacon` POST and an `<img>` request), so
just watch the access log of whatever serves `exploit.html`.

Local check against the shipped binary:

```bash
python3 -m http.server 8777 &
chrome/chrome --headless=new --no-sandbox --disable-gpu \
  --js-flags="--no-memory-protection-keys --expose-cage-base" \
  --enable-logging=stderr --log-level=0 \
  http://127.0.0.1:8777/solve/exploit.html 2>&1 | grep CONSOLE
```
