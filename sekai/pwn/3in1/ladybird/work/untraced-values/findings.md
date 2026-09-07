# Findings: Untraced Values, Conservative Containers, and reinterpret_cast Patterns

## Overview

This document covers three investigations in the Ladybird LibJS codebase:
- **Task 5**: Untraced Values in the Bytecode Interpreter
- **Task 6**: ConservativeVector/ConservativeHashMap analysis
- **Task 7**: reinterpret_cast<Value> and bit_cast<Value> patterns

---

## Task 5: Untraced Values in the Bytecode Interpreter

### How GC Tracing Works for Bytecode Execution

#### Execution Context Tracing (SAFE)

The bytecode interpreter stores all registers, locals, constants, and arguments as a flexible array member at the tail of `ExecutionContext`:

**File**: `Libraries/LibJS/Runtime/ExecutionContext.h`, lines 85-88, 127-130
```cpp
Value const* registers_and_constants_and_locals_and_arguments() const
{
    return reinterpret_cast<Value*>(reinterpret_cast<uintptr_t>(this) + sizeof(ExecutionContext));
}
```

This array is properly traced via `ExecutionContext::visit_edges`:

**File**: `Libraries/LibJS/Runtime/ExecutionContext.cpp`, lines 129-140
```cpp
void ExecutionContext::visit_edges(Cell::Visitor& visitor)
{
    visitor.visit(function);
    visitor.visit(realm);
    visitor.visit(variable_environment);
    visitor.visit(lexical_environment);
    visitor.visit(private_environment);
    visitor.visit(this_value);
    visitor.visit(executable);
    visitor.visit(registers_and_constants_and_locals_and_arguments_span()); // Traces all Values in flexible array
    visitor.visit(script_or_module);
}
```

#### Root Collection for All Execution Contexts (SAFE)

The VM collects roots from ALL execution contexts at GC time:

**File**: `Libraries/LibJS/Runtime/VM.cpp`, lines 325-336
```cpp
auto gather_roots_from_execution_context_stack = [...] {
    for_each_execution_context_top_to_bottom(stack, previous_running_contexts, running_execution_context, [&](ExecutionContext& execution_context) {
        ExecutionContextRootsCollector visitor;
        execution_context.visit_edges(visitor);
        for (auto cell : visitor.roots)
            roots.set(cell, GC::HeapRoot { .type = GC::HeapRoot::Type::VM });
        return true;
    });
};
gather_roots_from_execution_context_stack(m_execution_context_stack, m_execution_context_stack_previous_running_contexts, m_running_execution_context);
```

**File**: `Libraries/LibJS/Runtime/VM.h`, lines 465-500
The `for_each_execution_context_top_to_bottom` function traverses the execution context stack AND follows `caller_frame` pointers for inline JS-to-JS frames. All contexts are reached.

#### Conservative Native Stack Scanning (STRONG SAFETY NET)

The GC scans the entire native C++ stack at mark time:

**File**: `Libraries/LibGC/Heap.cpp`, lines 890-912, 1005-1012
```cpp
auto stack_reference = bit_cast<FlatPtr>(&dummy);
auto stack_top = m_stack_info.top();
...
for (FlatPtr stack_address = stack_reference; stack_address < stack_top; stack_address += sizeof(FlatPtr)) {
    auto data = *reinterpret_cast<FlatPtr*>(stack_address);
    add_possible_value(possible_pointers, data, HeapRoot { ... }, ...);
}
```

Critically, `add_possible_value` (lines 379-401) handles NaN-boxed Values:
```cpp
if ((data & SHIFTED_IS_CELL_PATTERN) == SHIFTED_IS_CELL_PATTERN)
    possible_pointer = NanBoxedValue::extract_pointer_bits(data);
```

This means any `JS::Value` holding a Cell pointer that exists on the native C++ stack will be correctly identified as a possible GC root, even if the Value is not traced through `visit_edges`.

Additionally, `setjmp` (line 896) captures callee-saved registers into a `jmp_buf`, which is also scanned (lines 906-909). This covers the asm interpreter's pinned registers (pc, pb, values, exec_ctx, dispatch).

#### InterpreterStack: The Non-Scanned Region

**File**: `Libraries/LibJS/Runtime/InterpreterStack.h`, lines 12-17
```cpp
InterpreterStack::InterpreterStack()
{
    m_base = mmap(nullptr, stack_size, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    ...
}
```

The interpreter stack is an 8 MiB `mmap`-allocated region. This is NOT on the native C++ stack and is NOT conservatively scanned by the GC. It relies entirely on the `ExecutionContext::visit_edges` mechanism for tracing.

**Risk Assessment**: ExecutionContexts on the interpreter stack are always traced because they are reachable through `m_running_execution_context`, its `caller_frame` chain, and `m_execution_context_stack` -- all of which are visited during GC root collection.

---

### Finding 5.1: Interpreter Stack Window During Inline Frame Setup

**File**: `Libraries/LibJS/Bytecode/AsmInterpreter/asmint.asm`, lines 2434-2556

**Issue**: During the `Call` handler inline frame setup, a new `ExecutionContext` is allocated on the interpreter stack (line 2436) and populated (lines 2440-2547). The new context is only set as `m_running_execution_context` at line 2552.

**Time window**: Between lines 2436 and 2552, the callee's `ExecutionContext` is on the interpreter stack but NOT yet `m_running_execution_context`.

**Mitigation**: During this window, the Values being written to the callee's frame come from:
1. The caller's Value array (which IS traced via the caller's `ExecutionContext::visit_edges`)
2. Constants from the `Executable` (which IS traced via `Executable::visit_edges`)
3. `undefined` (static sentinel, not a cell)

No Values exist ONLY in the callee's untraced frame during this window.

**STATUS**: SAFE by construction
**CONFIDENCE**: Low (no exploitable UAF)

---

### Finding 5.2: Asm Interpreter Temp Register Values During C++ Calls

**File**: `Libraries/LibJS/Bytecode/AsmInterpreter/asmint.asm`

**Issue**: Many handlers load Values into temp registers (caller-saved) before calling `call_helper` / `call_interp`. Temp registers are NOT preserved across C++ calls.

**Mitigation**:
1. `setjmp` captures callee-saved regs into `jmp_buf` (scanned). Caller-saved regs may not be captured, but C++ function prologues typically save them to the stack (which IS scanned).
2. `call_slow_path` is always TERMINAL (never returns to the handler), so stale register Values are never reused.
3. `call_helper` returns simple values (booleans), not cell pointers.
4. After `call_interp`, the handler reads from the traced `values` array or checks a simple return code.

**STATUS**: SAFE
**CONFIDENCE**: Low

---

### Finding 5.3: Return Value from RawNativeFunction

**File**: `Libraries/LibJS/Bytecode/AsmInterpreter/asmint.asm`, lines 2716-2735

The return value from `call_raw_native` is held in a register. Between the native return and the store to the caller's register (lines 2726-2735), no allocation occurs that could trigger GC. The return value is promptly stored.

**STATUS**: SAFE - no allocation between native return and register store
**CONFIDENCE**: Low

---

## Task 6: ConservativeVector/ConservativeHashMap Analysis

### How They Work

**ConservativeVector** (`Libraries/LibGC/ConservativeVector.h`, lines 15-82):
- Derives from `ConservativeVectorBase` and `Vector<T, inline_capacity>`
- Registers with the GC heap via `ConservativeVectorBase` (intrusive list `m_conservative_vectors`)
- `possible_values()` returns raw vector data as `ReadonlySpan<FlatPtr>`

**ConservativeHashMap** (`Libraries/LibGC/ConservativeHashMap.h`, lines 16-88):
- `for_each_possible_value()` scans each key and value byte-by-byte for potential FlatPtr pointers

**ConservativeHashTable** (`Libraries/LibGC/ConservativeHashTable.h`, lines 17-84):
- Same approach as ConservativeHashMap

### GC Scanning (Heap.cpp, lines 1014-1040)
All three container types are scanned during every GC mark phase via intrusive lists:
- `m_conservative_vectors` (Heap.h line 215)
- `m_conservative_hash_maps` (Heap.h line 213)
- `m_conservative_hash_tables` (Heap.h line 214)

---

### Finding 6.1: ConservativeVector<Value> Correctness

ConservativeVector<Value> correctly traces cell references because `possible_values()` returns raw bytes, and `add_possible_value` handles NaN-boxing. Non-pointer data that accidentally matches `SHIFTED_IS_CELL_PATTERN` and points into a heap block will keep cells alive unnecessarily (extra liveness, not UAF).

**STATUS**: SAFE (false-positive retention only)
**CONFIDENCE**: Medium

---

### Finding 6.2: ConservativeHashMap<PropertyKey, ...> with Non-Trivial Key Types

**Files**:
- `Libraries/LibJS/Bytecode/AsmInterpreter/AsmSlowPaths.cpp`, lines 393-394, 507-511, 1248
- `Libraries/LibJS/Runtime/Object.cpp`, line 1515
- `Libraries/LibJS/Runtime/ProxyObject.cpp`, line 684
- `Libraries/LibJS/Runtime/ClassConstruction.cpp`, lines 110-113
- `Libraries/LibJS/Console.cpp`, lines 154, 261, 279
- `Libraries/LibJS/Runtime/IndexedProperties.cpp`, line 85

PropertyKey contains a Variant that may hold a pointer to a GC-managed Symbol or interned string. The conservative scan covers these. If PropertyKey embeds a small-string optimization, inline string bytes could false-positive as cell pointers -- this only causes extra retention, not UAF.

**STATUS**: SAFE (false-positive retention only)
**CONFIDENCE**: Medium

---

### Finding 6.3: Conservative Containers in Module Initialization

**File**: `Libraries/LibJS/SourceTextModule.cpp`, lines 127, 271
```cpp
GC::ConservativeVector<FunctionToInitialize> functions_to_initialize;
```
`FunctionToInitialize` contains `GC::Ref<SharedFunctionInstanceData>` and `Utf16FlyString`. The GC::Ref is correctly found by the conservative scan.

**File**: `Libraries/LibJS/CyclicModule.cpp`, line 886
```cpp
GC::ConservativeVector<LoadedModuleRequest> records;
```
Same analysis.

**STATUS**: SAFE
**CONFIDENCE**: Medium

---

## Task 7: reinterpret_cast and bit_cast with Value Types

### Finding 7.1: ExecutionContext Flexible Array Member

**File**: `Libraries/LibJS/Runtime/ExecutionContext.h`, lines 85-88, 127-130

Standard C-style flexible array member. `reinterpret_cast<Value*>(reinterpret_cast<uintptr_t>(this) + sizeof(ExecutionContext))` accesses the trailing Value array, which is traced via `ExecutionContext::visit_edges`.

**STATUS**: SAFE - standard pattern with proper GC tracing
**CONFIDENCE**: High

---

### Finding 7.2: Object Named/Indexed Property Storage

**File**: `Libraries/LibJS/Runtime/Object.cpp`, lines 56, 97, 1808, 1878

`kmalloc`-allocated storage for Object properties, accessed via `reinterpret_cast<Value*>`. Properly traced by `Object::visit_edges` (lines 1684-1713) which visits named properties as `Span<Value>` and indexed elements in a loop.

**STATUS**: SAFE - properly traced by Object::visit_edges
**CONFIDENCE**: High

---

### Finding 7.3: bit_cast<Value> in RustIntegration.cpp (Bytecode Dump)

**File**: `Libraries/LibJS/RustIntegration.cpp`, lines 171, 178, 185

Debug-only callbacks for bytecode dumping. Values come from the Executable's constants table (traced). No exploitation risk.

**STATUS**: SAFE - debug-only callbacks
**CONFIDENCE**: High

---

### Finding 7.4: bit_cast<Value> in AsmSlowPaths.cpp (Math FFI)

**File**: `Libraries/LibJS/Bytecode/AsmInterpreter/AsmSlowPaths.cpp`, lines 3016-3054

Used in fast-path math operations. Values are immediately used as operands; the only references are on the native C++ stack (conservatively scanned).

**STATUS**: SAFE - native stack is conservatively scanned
**CONFIDENCE**: Medium

---

### Finding 7.5: reinterpret_cast in LibWasm ConservativeRangeProvider

**File**: `Libraries/LibWasm/AbstractMachine/AbstractMachine.cpp`, line 137

Registers Value array ranges with the GC for conservative scanning. Proper usage of the ConservativeRangeProvider API.

**STATUS**: SAFE
**CONFIDENCE**: High

---

## Summary

### Overall Risk for Bytecode Interpreter: LOW

The Ladybird JS GC provides defense-in-depth:

1. **All ExecutionContexts are fully traced** via `visit_edges`, including the flexible array member for registers/locals/constants/arguments (`Libraries/LibJS/Runtime/VM.cpp:325-336`, `Libraries/LibJS/Runtime/VM.h:465-500`)

2. **Native C++ stack is conservatively scanned** -- every FlatPtr is checked as a potential pointer, with NaN-boxing handled via `extract_pointer_bits` (`Libraries/LibGC/Heap.cpp:379-401, 1005-1012`)

3. **setjmp captures callee-saved registers** (including asm interpreter pinned state: pc, pb, values, exec_ctx, dispatch) (`Libraries/LibGC/Heap.cpp:896, 906-909`)

4. **Conservative containers register their memory ranges** for per-byte conservative scanning (`Libraries/LibGC/ConservativeVector.h:72-79`, `Libraries/LibGC/ConservativeHashMap.h:69-82`)

5. **All reinterpret_cast<Value> patterns** are for flexible array members or storage that is properly traced via visit_edges

### No Exploitable Primitives Found

No exploitable untraced Value, misconfigured conservative container, or dangerous reinterpret_cast/bit_cast pattern was found that would allow a UAF or type confusion from constrained JavaScript (TypedArrays only, no require/fetch) in the Ladybird version being analyzed.

If exploitation is needed for the CTF "3in1" chain, the required primitive would need to come from a different layer (virtio-sound kernel bug, QEMU heap overflow, or a TCG/JIT bug).

---

## References

| File | Lines | Finding |
|------|-------|---------|
| `Libraries/LibJS/Runtime/ExecutionContext.h` | 85-88, 127-130 | Flexible array member with reinterpret_cast<Value*> |
| `Libraries/LibJS/Runtime/ExecutionContext.cpp` | 129-140 | visit_edges traces trailing Value array |
| `Libraries/LibJS/Bytecode/AsmInterpreter/asmint.asm` | 2368-2556 | Call handler inline frame setup |
| `Libraries/LibGC/ConservativeVector.h` | 15-82 | ConservativeVector implementation |
| `Libraries/LibGC/ConservativeHashMap.h` | 16-88 | ConservativeHashMap implementation |
| `Libraries/LibGC/ConservativeHashTable.h` | 17-84 | ConservativeHashTable implementation |
| `Libraries/LibGC/Heap.cpp` | 379-401 | add_possible_value with NaN-boxing |
| `Libraries/LibGC/Heap.cpp` | 890-912, 1005-1012 | Conservative stack scanning |
| `Libraries/LibGC/Heap.cpp` | 1014-1040 | Conservative container scanning |
| `Libraries/LibJS/Runtime/VM.cpp` | 325-336 | Execution context root collection |
| `Libraries/LibJS/Runtime/VM.h` | 465-500 | for_each_execution_context_top_to_bottom |
| `Libraries/LibJS/Runtime/InterpreterStack.h` | 12-17 | mmap-based interpreter stack |
| `Libraries/LibJS/Runtime/Object.cpp` | 56, 97, 1808, 1878 | Object property storage reinterpret_cast |
| `Libraries/LibJS/Runtime/Object.cpp` | 1684-1713 | Object::visit_edges tracing |
| `Libraries/LibJS/RustIntegration.cpp` | 171, 178, 185 | bit_cast<Value> for debug dumps |
| `Libraries/LibJS/Bytecode/AsmInterpreter/AsmSlowPaths.cpp` | 393, 507, 1248 | Conservative containers in slow paths |
| `Libraries/LibJS/Runtime/ProxyObject.cpp` | 684 | ConservativeHashTable in ProxyObject |
| `Libraries/LibJS/Runtime/ClassConstruction.cpp` | 110-113 | ConservativeVector in class construction |
| `Libraries/LibJS/SourceTextModule.cpp` | 127, 271 | ConservativeVector in module init |
| `Libraries/LibJS/CyclicModule.cpp` | 886 | ConservativeVector for module records |
| `Libraries/LibWasm/AbstractMachine/AbstractMachine.cpp` | 137 | ConservativeRangeProvider in Wasm |
