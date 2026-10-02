# Writeup: sinkhole (CSCV 2026 Quals - Pwn)

| Property | Value |
| :--- | :--- |
| **Category** | `Pwn` |
| **Points** | `275` (500 initial) |
| **Target** | Chromium 153.0.8010.0 (Patched Maglev JIT) |
| **Service** | `nc 113.20.103.216 31337` |

---

## 1. Challenge Summary
The challenge provides a custom build of Chromium with modified V8 source files located in `src/maglev/`. The bot (`bot.py`) receives an HTTP/HTTPS URL and launches headless Chromium with `--no-sandbox`, `--no-memory-protection-keys`, and `--expose-cage-base`. The objective is to achieve renderer code execution and read `/flag`.

---

## 2. Vulnerability Discovery & Root Cause Analysis

### Discovery Triggers
Examining `src/maglev/` reveals two custom passes added to `maglev-compiler.cc`:
- `MaglevStoreSink`
- `MaglevSmiCheckElimination`

Both passes contain a threshold check:
```cpp
if (graph_->num_blocks() <= kSmallFunctionMaxBlocks) return; // 1024
```
Standard test suites with small functions never hit these passes. Adding ~1200 branches (`if (p === i) ...`) expands the control flow graph to exceed 1024 basic blocks.

### Flaw in `MaglevSmiCheckElimination`
In `src/maglev/maglev-smi-check-elimination.cc`:
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

The pass assumes that if an index value is checked by a bounds check anywhere in the function graph, it is safe to replace its tagged-to-integer conversion (`CheckedSmiUntag`) with `UnsafeSmiUntag`. However:
1. The bounds check consumes the output of the untag operation, not validating the input type.
2. The check only needs to exist somewhere in the graph (e.g. inside an unexecuted conditional `if (flag) { sink = a[x]; }`), yet affects uses along all execution paths.
3. Overwriting `CheckedSmiUntag` causes Maglev's type inference (`KnownNodeAspects`) to mark the input as `NodeType::kSmi`.

---

## 3. Exploitation Chain

### Primitive 1: Addrof via Untag Confusion
With `x` considered a Smi, evaluating `let t = x + 1` generates an arithmetic right shift directly on the compressed pointer of a `HeapObject`. Subtracting 1 and multiplying by 2 recovers the exact 32-bit compressed address without triggering deoptimization.

### Primitive 2: Generational Write Barrier Elimination & UAF
In `MaglevReducer::CanElideWriteBarrier()`, stores where the value is statically known to be Smi skip the write barrier. Executing `dst[0] = x` into an old-space array emits `StoreFixedArrayElementNoWriteBarrier`. When a minor GC (scavenge) occurs:
- The young-space object `x` is relocated or reclaimed.
- Because no write barrier recorded the old-to-young edge, `dst[0]` retains the old address, creating a dangling pointer (Use-After-Free).

### Primitive 3: Fake Object & Heap Sandbox Corruption
1. Spraying arrays of double elements (`[41 doubles]`) reallocates the freed backing store.
2. The dangling pointer now points inside the sprayed double array, giving control over the object's Map, properties, and elements pointers.
3. Forging a fake `JSObject` allows arbitrary reads and writes across the V8 cage.
4. Overwriting the backing store pointer of a `Float64Array` provides arbitrary full 64-bit process memory read/write.

### Primitive 4: Code Execution & Exfiltration
1. Locate the WebAssembly jump table from `WasmInstanceObject` -> `WasmTrustedInstanceData`.
2. Because `--no-memory-protection-keys` is enabled and no sandbox restricts execution, the jump table page remains writable.
3. Write shellcode into the Wasm jump table and call the exported Wasm function.
4. Shellcode opens `/flag`, reads its contents into memory, and exfiltrates it via an HTTP callback to the hosting server.
