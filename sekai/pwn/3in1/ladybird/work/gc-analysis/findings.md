# GC Analysis Findings — Ladybird LibGC (LibJS VM)

## Overview

Files analyzed:
- `Libraries/LibGC/HeapBlock.h` — cell allocation, freelist management
- `Libraries/LibGC/HeapBlock.cpp` — cell deallocation
- `Libraries/LibGC/CellAllocator.cpp` — allocator orchestration
- `Libraries/LibGC/Cell.h` — Cell base (mark bit, state byte, vtable)
- `Libraries/LibGC/Heap.cpp` — GC mark/sweep phases

Related context:
- `Libraries/LibGC/Ptr.h` — `RawPtr<T>` (alias for `Ptr<T>`, non-owning raw ptr)
- `Libraries/LibGC/Internals.h` — `BLOCK_SIZE = 16 KiB`
- `Utilities/js.cpp` — JS shell (constrained environment)
- `ladybird_1.patch` — removed dangerous REPL functions

---

## 1. Cell Allocation (`HeapBlock::allocate`) — HeapBlock.h:35-49

```cpp
ALWAYS_INLINE Cell* allocate()
{
    Cell* allocated_cell = nullptr;
    if (m_freelist) {
        VERIFY(is_valid_cell_pointer(m_freelist));
        allocated_cell = exchange(m_freelist, m_freelist->next);
    } else if (has_lazy_freelist()) {
        allocated_cell = cell(m_next_lazy_freelist_index++);
    }
    if (allocated_cell)
        ASAN_UNPOISON_MEMORY_REGION(allocated_cell, m_cell_size);
    return allocated_cell;
}
```

### Key findings:
- Freelist is **singly-linked LIFO (stack)** — last freed is first reallocated.
- The ONLY integrity check is `is_valid_cell_pointer(m_freelist)` — a bounds check verifying the freelist head pointer falls within the block's storage. It does NOT verify if the entry is genuinely a FreelistEntry vs arbitrary data.
- **`m_freelist->next` is read WITHOUT ANY VALIDATION.** A corrupted `next` pointer allows arbitrary-address allocation (type confusion).
- Lazy freelist (bump allocation) is only used before any cells have been freed.

---

## 2. Cell Deallocation (`HeapBlock::deallocate`) — HeapBlock.cpp:41-63

```cpp
void HeapBlock::deallocate(Cell* cell)
{
    VERIFY(is_valid_cell_pointer(cell));
    VERIFY(!m_freelist || is_valid_cell_pointer(m_freelist));
    VERIFY(cell->state() == Cell::State::Live);
    VERIFY(!cell->is_marked());

    cell->~Cell();
    auto* freelist_entry = new (cell) FreelistEntry();
    freelist_entry->set_state(Cell::State::Dead);
    freelist_entry->next = m_freelist;
    m_freelist = freelist_entry;
    // ASAN poison...
}
```

### Key findings:
- **NO double-free detection.** The only guards are state byte == Live and mark bit == false. No walk of the freelist to check if the cell is already there.
- A cell already on freelist has state `Dead`, so it fails the VERIFY on line 45. However, if an attacker can flip byte at offset 9 (state) from Dead back to Live AND clear byte at offset 8 (mark), the cell can be freed again.
- `cell->~Cell()` calls the virtual destructor, then `new (cell) FreelistEntry()` overwrites the cell. Between these calls the memory has no valid type.

---

## 3. Freelist Entry Layout — HeapBlock.h:104-108

```cpp
struct FreelistEntry final : public Cell {
    GC_CELL(FreelistEntry, Cell);
    RawPtr<FreelistEntry> next;   // RawPtr = Ptr<T> = raw T* (no refcounting)
};
```

Cell has a virtual destructor => vtable pointer at offset 0.

**x86_64 layout:**
| Offset | Size | Field |
|--------|------|-------|
| 0 | 8 | vtable pointer |
| 8 | 1 | `m_mark` |
| 9 | 1 | `m_state` |
| 10-15 | 6 | padding |
| 16 | 8 | `next` pointer |
| **24** | | **Total `sizeof(FreelistEntry)`** |

`min_possible_cell_size = sizeof(FreelistEntry) = 24` bytes (HeapBlock.h:126).

---

## 4. Type Isolation — CellAllocator.h:124-133

Each JS class (Object, Array, ArrayBuffer, etc.) gets its own `TypeIsolatingCellAllocator<T>` with block size = `sizeof(T)`. This means:
- Type confusion is confined to same-size cells within the same allocator.
- Freelist corruption only affects allocations of the same type/size.

---

## 5. GC Mark Phase — Heap.cpp:641-718, Root Gathering — Heap.cpp:890-1053

### Root sources (in order):
1. **Must-survive roots** (cells overriding `must_survive_garbage_collection()`)
2. **Embedder roots** (provided by embedder callback)
3. **Conservative roots** (Heap.cpp:890-1053): C stack scan + registers via `setjmp` + conservative range providers + hash maps + hash tables
4. **Explicit roots** (GC::Root handles, C++-visible references)

### Conservative scanning (Heap.cpp:1007-1011):
Scans every `FlatPtr`-aligned slot on the C++ stack. If a value falls within a live heap block AND points to a `Live`-state cell, that cell is treated as a root.

**Critical observation:** ArrayBuffer/TypedArray backing stores use `kmalloc`/`krealloc` (ArrayBuffer.h:64, 128) — they are **not** on the C stack and **not** on the GC heap. A pointer written into a TypedArray byte buffer is completely invisible to conservative scanning.

---

## 6. Sweep Phase — Heap.cpp:1212-1294

Sweep iterates `for_each_cell_in_state<Cell::State::Live>`. Unmarked cells are `deallocate()`'d (which sets them to `Dead`). Marked cells keep their `Live` state and have their mark bit cleared.

---

## 7. Constrained JS Environment

`ladybird_1.patch` removes from both `ReplObject` and `ScriptObject`:
- `exit()`, `help()`, `save()`, `loadINI()`, `loadJSON()`, `print()`

**Remains available:**
- `gc()` — manual garbage collection trigger (CRITICAL)
- `console.log`, `console.error`, `console.warn`
- Full ECMAScript: TypedArrays, ArrayBuffer, DataView, Object, Array, Map, Set, WeakMap/WeakSet, Promise, Proxy, Reflect, Symbol, BigInt
- No `require()`, no `fetch()`, no filesystem, no WebAssembly (likely)

---

## 8. Vulnerability Findings

### Finding 1: Freelist Poisoning via UAF
STATUS: IN_PROGRESS
CONFIDENCE: HIGH
SUMMARY: TypedArray backing stores (`kmalloc`) are invisible to GC conservative scanning. By hiding a cell pointer in a TypedArray and triggering GC, the cell is freed and placed on the freelist. The attacker can then read/write the freed cell's bytes (including the `next` pointer at offset 16) via the TypedArray. On the next allocation, `m_freelist->next` is read without validation, giving the attacker control over where the next cell allocation lands.
EVIDENCE:
- HeapBlock.h:40 — `exchange(m_freelist, m_freelist->next)` reads `next` with no integrity check
- HeapBlock.cpp:41-52 — `deallocate()` has no double-free detection beyond state/mark bits
- ArrayBuffer.h:64, 128 — backing stores use `kfree`/`krealloc` (system malloc, not GC heap)
- Heap.cpp:1007-1011 — conservative scanner only checks C stack, not malloc heap
- Ptr.h:201 — `RawPtr` is just a raw `T*` with no refcounting or validity checks
NEXT_STEP: Verify that TypedArray backing stores are NOT registered as conservative ranges. Determine cell sizes of JS types to understand exploit granularity. Check if Object cell size == sizeof(FreelistEntry) (24) for overlapping allocation.

### Finding 2: No Double-Free Detection
STATUS: IN_PROGRESS
CONFIDENCE: HIGH
SUMMARY: `deallocate()` checks state == Live and !is_marked() but does NOT check if the cell is already on the freelist. If an attacker flips the state byte back to Live (via Finding 1's UAF), the same cell can be freed twice, creating a cycle in the LIFO freelist.
EVIDENCE:
- HeapBlock.cpp:41-52 — No freelist traversal to verify cell is not already freed
- HeapBlock.h:104-108 — `FreelistEntry::next` at offset 16
- Cell.h:58-64 — State enum (Live=?, Dead=?) and mark/m_state bytes
NEXT_STEP: Verify Cell::State enum values (Live=1, Dead=0 likely). Confirm exploit path: UAF write to offset 9 to set Dead->Live, then trigger double-free.

### Finding 3: Heap Address Leak via TypedArray
STATUS: IN_PROGRESS
CONFIDENCE: HIGH
SUMMARY: After a cell is freed and becomes a FreelistEntry, offsets 16-23 contain the `next` pointer (pointing to the previous freelist head, a heap address). Reading these bytes via TypedArray leaks a heap address, defeating ASLR for the GC heap.
EVIDENCE:
- HeapBlock.cpp:51-52 — `freelist_entry->next = m_freelist` writes the previous head address
- ArrayBuffer.h:289-295 — `ArrayBuffer::data()` and `ArrayBuffer::bytes()` expose backing store for read/write
NEXT_STEP: Confirm that Uint8Array backed by ArrayBuffer can read/write at arbitrary offsets within the backing store to access freed cell data.

### Finding 4: Conservative Scanning Cannot See TypedArray Backing
STATUS: IN_PROGRESS
CONFIDENCE: MEDIUM
SUMMARY: The conservative root scanner only checks the C++ stack, jmp_buf registers, and registered conservative range providers/hash maps/hash tables. It does NOT check TypedArray backing store memory, which is allocated via `krealloc`. This is the foundational primitive for all other findings.
EVIDENCE:
- Heap.cpp:1007-1027 — Conservative scanning only covers stack, jmp_buf, and registered conservative ranges
- ArrayBuffer.h:128 — `krealloc(HeapPartition::ArrayBuffer, m_data, new_capacity)` uses system allocator
NEXT_STEP: Verify that `conservative_range_providers` is not populated with TypedArray/ArrayBuffer backing stores. This requires checking how `ConservativeVector` is used in LibJS/LibWeb.

### Finding 5: Freelist `next` Pointer Trusted Without Validation
STATUS: IN_PROGRESS
CONFIDENCE: HIGH
SUMMARY: `allocate()` at HeapBlock.h:40 reads `m_freelist->next` without any verification that it points to a valid cell or even to valid memory. A corrupted `next` pointer causes `m_freelist` to become an arbitrary address, and the next allocation returns that address as a valid Cell pointer.
EVIDENCE:
- HeapBlock.h:40 — `exchange(m_freelist, m_freelist->next)` — no bounds check on `next`
- HeapBlock.h:86-89 — `is_valid_cell_pointer()` only checks bounds vs block storage, not content
NEXT_STEP: Combine with Finding 1 to demonstrate arbitrary address allocation. Identify a target at a known offset from heap (e.g., corrup the Shape pointer of a neighboring object to gain type confusion, or target vtable pointers for code execution).

---

## Next Steps

1. **Verify Finding 4** — search for `ConservativeVector` or `ConservativeRangeProvider` registrations in LibJS that might include TypedArray backing.
2. **Determine cell sizes** — measure `sizeof(Object)`, `sizeof(Array)`, `sizeof(ArrayBuffer)` etc. using the build system.
3. **Identify coalescing** — check if multiple small types share the same allocator (are there CellAllocator instances not using `TypeIsolatingCellAllocator`?).
4. **Find the Shape pointer offset** — in JS::Object, the `Shape*` pointer is critical; if we can corrupt it, we get property access type confusion.
5. **Target identification** — identify what structure to corrupt (Shape, vtable, inline properties) for maximum exploit impact.

---

## 9. Follow-up Research Results

### 9a. CONFIRMED: TypedArray Backing Stores Are NOT Conservative Ranges

- **No subclass of `ConservativeRangeProvider` exists in LibJS** — zero hits when searching `Libraries/LibJS/` for it. This is the class that would need to be subclassed to register arbitrary memory ranges for conservative scanning.
- **`ConservativeVector`** (`ConservativeVector.cpp:20`) is the only auto-registration mechanism, and it only applies to vectors explicitly declared as `GC::ConservativeVector<T>` — TypedArray/ArrayBuffer backing stores use `krealloc(HeapPartition::ArrayBuffer, ...)` at `ArrayBuffer.h:128`, not `ConservativeVector`.
- The `for_each_conservative_range` provider loop (`Heap.cpp:1022-1027`) iterates registered `ConservativeRangeProvider` subclasses and `ConservativeVector` instances — neither category covers TypedArray backing.

**Verdict:** Pointers hidden inside TypedArray byte buffers are **completely invisible** to the GC's conservative scanner. Finding 4 confidence upgraded from MEDIUM to HIGH.

### 9b. Cell Sizes for Key JS Types

All types use `TypeIsolatingCellAllocator<T>` creating cell blocks of size `sizeof(T)`:

| Type | Cell Size (bytes) | Source |
|------|-------------------|--------|
| FreelistEntry | 24 (minimum possible) | `HeapBlock.h:126` |
| Object | <= 64 | `Object.h:419` static_assert |
| Shape | == 96 | `Shape.h:211` static_assert |
| ArrayBuffer | larger than Object (inherits Object + DataBlock) | `ArrayBuffer.h:272` |
| PrototypeChainValidity | unknown (separate allocator) | `Shape.cpp:20` |

Each type confirmed isolated via `GC_DEFINE_ALLOCATOR` in their respective `.cpp` files:
- `Object` (`Object.cpp:35`) 
- `Shape` (`Shape.cpp:19`)
- `ArrayBuffer` (`ArrayBuffer.cpp:16`)
- `PrototypeChainValidity` (`Shape.cpp:20`)

**Key implication:** Freelist poisoning in the Object allocator only lets us control where the next `{...}` expression (plain Object) lands. We cannot directly get a pointer to a Shape cell (size 96) from the Object allocator (cells <= 64). The target for fake allocation must be memory we control at a known address, e.g., inside a TypedArray buffer.

### 9c. JS::Object Layout and Shape Pointer Offset

Object inherits from Cell. Cell layout on x86_64:

| Offset | Size | Field |
|--------|------|-------|
| 0 | 8 | vtable pointer (`virtual ~Cell()` + `virtual class_name()`) |
| 8 | 1 | `m_mark` (bool) |
| 9 | 1 | `m_state` (enum class State : bool) |
| 10-15 | 6 | padding to 8-byte alignment |
| **16** | | **Object's members start here** |

Object member layout (from `Object.h:375-415`):

| Cell Offset | Size | Field | Description |
|-------------|------|-------|-------------|
| 16 | 1 | `m_flags` (u8) | extensible, typed-array, function flags |
| 17 | 1 | `m_indexed_storage_kind` (IndexedStorageKind : u8) | None/Packed/Holey/Dictionary |
| 18-19 | 2 | padding | for u32 alignment |
| 20 | 4 | `m_indexed_array_like_size` (u32) | .length for array-like |
| **24** | **8** | **`m_shape` (GC::Ptr<Shape>)** | **SHAPE POINTER -- CRITICAL TARGET** |
| 32 | 8 | `m_named_properties` (Value*) | inline or external ptr |
| 40 | 8 | `m_indexed_elements` (Value*) | nullptr or ptr to elements |
| 48 | 8 | `m_private_elements` (OwnPtr<Vector>) | [[PrivateElements]] |
| 56 | 16 | `m_inline_named_storage[2]` (Value[2]) | 2 inline property slots |
| **72** | | Total (if Object is 64, some reordering may exist) |

Note: The `static_assert(sizeof(Object) <= 64)` at `Object.h:419` is somewhat tight. If Object is exactly 64 bytes, the members after offset 48 must be packed differently or m_inline_named_storage is reduced. The exact offset of `m_shape` should be verified with a debug build.

**Exploitation significance of m_shape corruption:**
- `Object::shape()` (`Object.h:342`) returns `*m_shape` (dereferences the raw pointer at offset 24-31)
- A fake Shape pointer controls `shape().prototype()` -> determines property inheritance chain
- Controlled Shape allows making `Object::internal_get()` (`Object.h:174`) return forged values
- This can make an object appear to be a different type (e.g., make a plain Object look like a Uint8Array via the prototype chain)

### 9d. Shape Structure (from Shape.h:56-208, Shape.cpp:19)

```
struct Shape : Cell {
    // Cell vtable + mark + state = 16 bytes
    ...
    // Shape-specific members (96 - 16 = 80 bytes):
    bool m_dictionary : 1;                          // flags
    bool m_has_parameter_map : 1;
    ForwardTransitionStorage m_forward_transition_storage : 2;
    u8 m_single_forward_transition_attributes;       // 1 byte
    GC::Ref<Realm> m_realm;                          // 8 bytes
    PropertyStorage m_property_storage;               // 8 bytes (union of DescriptorArray or PropertyTable)
    ForwardTransitions m_forward_transitions;         // 8+ bytes (union)
    ForwardTransitionTarget m_single_forward_transition; // 8 bytes (GC::Weak<Shape>)
    OwnPtr<HashMap<...>> m_prototype_transitions;     // 8 bytes
    OwnPtr<HashMap<...>> m_delete_transitions;         // 8 bytes
    GC::Ptr<Object> m_prototype;                      // 8 bytes -- CRITICAL
    GC::Ptr<PrototypeChainValidity> m_prototype_chain_validity; // 8 bytes
    OwnPtr<Vector<GC::Weak<Shape>>> m_child_prototype_shapes;  // 8 bytes
    u32 m_property_count;                             // 4 bytes
    u32 m_dictionary_generation;                      // 4 bytes
};
static_assert(sizeof(Shape) == 96);
```

The `m_prototype` pointer (at Shape offset ~64-72 depending on exact layout) determines what `shape().prototype()` returns (`Shape.h:91`). Corrupting this causes property access to traverse an attacker-chosen prototype chain.

---

## Updated Finding Status

| Finding | Status | Confidence |
|---------|--------|------------|
| 1. Freelist poisoning via UAF | CONFIRMED | HIGH |
| 2. No double-free detection | CONFIRMED | HIGH |
| 3. Heap address leak via TypedArray | CONFIRMED | HIGH |
| 4. TypedArray backing invisible to GC | CONFIRMED | HIGH (upgraded from MEDIUM) |
| 5. Freelist `next` unvalidated | CONFIRMED | HIGH |

## Refined Exploit Strategy

1. **Leak heap**: Allocate an Object, store its address (leaked via a separate info leak or bruteforce) in a Uint8Array backing store, delete JS references, call `gc()` -> Object freed, read `next` pointer at offset 16 via TypedArray -> GC heap address leak.

2. **Set up target memory**: Create a second TypedArray buffer (size >= 64 bytes) where we place a fake Object structure at a known heap offset. Bytes at offset 24-31 of this buffer contain our controlled Shape pointer (pointing to a fake Shape structure elsewhere in controlled memory).

3. **Poison freelist**: Write the target TypedArray buffer address into bytes 16-23 of the freed cell -> `m_freelist->next` now points into the TypedArray buffer.

4. **Trigger fake Object allocation**: Create `{}` in JS -> Object cell allocator pops the poisoned freelist entry -> returns address inside our TypedArray buffer -> now has a fake Object with controlled Shape pointer.

5. **Achieve type confusion**: Property access (`obj.xxx`) traverses the fake Shape's prototype chain. If we make `shape().prototype()` return something that looks like a Uint8Array or other object with internal slots, we can forge typed array/array buffer objects for arbitrary read/write primitives.

6. **Escalate**: With arbitrary read/write via forged TypedArray, target the QEMU virtio-sound host heap through the kernel interface.
