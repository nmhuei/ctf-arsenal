# Analysis: sinkhole (CSCV 2026 Quals - Pwn)

## 1. Challenge Overview
- **Category**: Pwn (V8 JIT / Browser Exploitation)
- **Target**: Patched Chromium 153.0.8010.0 (V8 13.x branch) running headless without sandbox (`--no-sandbox`, `--no-memory-protection-keys`, `--expose-cage-base`).
- **Bot**: `bot.py` takes an HTTP/HTTPS URL, navigates using headless Chrome for 45s. Flag is at `/flag` (mode 600, owned by ctf).

## 2. Root Cause Analysis
Two custom compiler passes were added to Maglev:
1. `MaglevStoreSink` (`src/maglev/maglev-store-sink.cc`): Sinks element stores and transitions into loop headers.
2. `MaglevSmiCheckElimination` (`src/maglev/maglev-smi-check-elimination.cc`):
```cpp
void MaglevSmiCheckElimination::CollectGuardedIndices() {
  for (BasicBlock* block : graph_->blocks()) {
    for (Node* node : block->nodes()) {
      if (node == nullptr) continue;
      auto* check = node->TryCast<CheckInt32Condition>();
      if (check == nullptr) continue;
      if (check->deoptimize_reason() != DeoptimizeReason::kOutOfBounds) continue;
      if (check->condition() != AssertCondition::kUnsignedLessThan) continue;
      guarded_.insert(check->input(0).node()->UnwrapIdentities());
    }
  }
}
void MaglevSmiCheckElimination::NarrowGuardedUntags() {
  for (ValueNode* index : guarded_) {
    if (!index->Is<CheckedObjectToIndex>() && !index->Is<CheckedSmiUntag>()) continue;
    index->OverwriteWith<UnsafeSmiUntag>();
  }
}
```

Both passes gate execution on:
```cpp
if (graph_->num_blocks() <= kSmallFunctionMaxBlocks) return; // 1024
```
Padding a JS function with ~1200 simple branches bypasses this check, allowing the buggy passes to run.

### The Flaw in `MaglevSmiCheckElimination`
The pass operates purely syntactically across the entire graph. If an index is bounds-checked anywhere (even in an unreachable or conditional branch), the pass assumes the conversion from JavaScript value to integer index does not require verification and overwrites `CheckedSmiUntag` / `CheckedObjectToIndex` with `UnsafeSmiUntag`.

This has two critical side effects on type propagation:
1. **Addrof Primitive**:
   In `let t = x + 1`, when `x` is a HeapObject, V8 generates an arithmetic shift on the compressed pointer rather than type-checking and deoptimizing. This directly yields the object's compressed address.
2. **Missing Write Barrier (UAF)**:
   In `MaglevReducer::CanElideWriteBarrier()`, if the node type is believed to be `kSmi`, the generational write barrier is dropped. An assignment `dst[0] = obj` into an old-space array emits `StoreFixedArrayElementNoWriteBarrier`. Subsequent young-generation garbage collections (scavenges) evacuate `obj` without updating `dst[0]`, leaving a dangling pointer (Use-After-Free).

## 3. Exploit Chain
1. **Warmup & Compilation**:
   Function is invoked ~25k times to tier up into Maglev (padded to avoid Turbofan tier-up).
2. **UAF Trigger**:
   Old-space array holds a reference to a young-space victim object without a write barrier. Triggering scavenge leaves a dangling pointer.
3. **Array Spraying**:
   Double arrays are sprayed over the freed address to forge a fake `JSArray` with controlled `elements` pointer.
4. **Cage & Process Read/Write**:
   With the fake array, corrupting the length of an adjacent array provides out-of-bounds read/write within the V8 heap cage. Overwriting an ArrayBuffer's external pointer provides full process memory read/write.
5. **Code Execution**:
   Because `--no-memory-protection-keys` and `--no-sandbox` are active, writing shellcode to the Wasm jump table and invoking the Wasm function achieves native code execution to read `/flag`.
