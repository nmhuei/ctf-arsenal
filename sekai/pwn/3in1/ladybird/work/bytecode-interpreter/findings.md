STATUS: IN_PROGRESS
CONFIDENCE: high
SUMMARY: Analysis of LibJS Bytecode Interpreter GC Rooting for UAF Vulnerabilities
EVIDENCE:

## 1. Register File / Value Array Architecture

### ExecutionContext Layout (ExecutionContext.h:38-49)
The bytecode interpreter stores register values as a tail-allocated Value array immediately following the ExecutionContext struct in memory. The layout is:
[registers | locals | constants | arguments]

- File: /home/light/Workspace/CTF/sekai/pwn_3in1/pwn_3in1/ladybird/Libraries/LibJS/Runtime/ExecutionContext.h
- Line 38: Constructor copies constants into the value array during construction
- Line 127-129: `registers_and_constants_and_locals_and_arguments()` returns pointer to the tail-allocated Value array
- Line 85-87: const version (the value array starts at `this + sizeof(ExecutionContext)`)

### InterpreterStack (InterpreterStack.h, InterpreterStack.cpp)
The InterpreterStack is an 8 MiB mmap'd region with bump-pointer allocation:
- Line 22: `static constexpr size_t stack_size = 8 * MiB;`
- Line 14 (InterpreterStack.cpp): `m_base = mmap(...)` — raw mmap, no GC integration
- Line 29-44: `allocate()`: placement-new into current `m_top`, then bump forward
- Line 46-49: `deallocate(void* mark)`: just resets `m_top = mark` (trivially destructible, no cleanup)

### Register Access (VM.h:96-113)
- Line 96-99: `Value& reg(Register const& r)` returns reference directly into the value array
- Line 106-108: `Value get(Operand op)` reads using `op.raw()` as index
- Line 110-112: `void set(Operand op, Value value)` writes directly into the value array

## 2. GC Rooting — NORMAL EXECUTION

### Root Collection (VM.cpp:269-340)
- Line 269-289: `ExecutionContextRootsCollector::visit_impl(Span<NanBoxedValue>)` iterates values, adds cells to roots
- Line 325-336: `gather_roots_from_execution_context_stack` visits all execution contexts

### ExecutionContext GC Visiting (ExecutionContext.cpp:129-140)
- Line 138: `visitor.visit(registers_and_constants_and_locals_and_arguments_span())` — ALL registers visited
- The entire Value array is passed as ReadonlySpan<NanBoxedValue> to the GC visitor

### Inline Frame Traversal (VM.h:465-500)
- `for_each_execution_context_top_to_bottom()` traverses both:
  - `m_execution_context_stack` (normal contexts via push_execution_context)
  - `caller_frame` linked list (inline JS-to-JS frames set via push_inline_frame)
- Line 478-482: When no stack, walks `caller_frame` chain from `m_running_execution_context`
- Line 486-497: Combined traversal when both exist

### Mark Phase (Heap.cpp:1098-1115)
- Marking visitor has `visit_impl(Span<NanBoxedValue>)` that marks all referenced cells

### VERDICT: NO UAF — registers properly rooted through visit_edges

## 3. GC Rooting — GENERATOR/ASYNC CONTEXTS

### GeneratorObject (GeneratorObject.cpp:63-68)
- Line 67: `m_execution_context->visit_edges(visitor)` — saved ExecutionContext visited during GC

### AsyncFunctionDriverWrapper (AsyncFunctionDriverWrapper.cpp:220-230)
- Line 227-228: `m_suspended_execution_context->visit_edges(visitor)` — properly visited

### SavedExecutionContextStack (VM.cpp:335-336)
- Line 335: saved stacks also iterated in gather_roots

### VERDICT: NO UAF — generator/async contexts properly rooted

## 4. Edge Cases

### 4a. Non-moving GC (mark-sweep, no compaction)
- Raw pointers (TypedArrayBase::m_data, PropertyLookupCache raw ptrs) remain valid while object is alive

### 4b. PropertyLookupCache uses untraced GC::RawPtr (Executable.h:74-78)
- `GC::RawPtr<Shape> from_shape, shape, prototype, prototype_chain_validity;`
- NOT traced during mark phase (Executable::visit_edges skips property_lookup_caches)
- Cleared during sweep via `remove_dead_cells` (Executable.cpp:560-573) and `clear_cache_entry_if_dead`
- By-design: these are speculative caches, not ownership references
- **Risk**: If `clear_cache_entry_if_dead` had a bug, stale RawPtr could survive → type confusion on next cache hit
- **Confidence**: Low — looks by-design safe

### 4c. TypedArray Cached Data Pointer (TypedArray.h:101-111)
- `u8* m_data` cached raw pointer into ArrayBuffer backing store
- Only enabled for fixed-length ArrayBuffers with OwnedBackingStore (cannot reallocate)
- Resizable buffers: cache disabled (fallback to slow path)
- **Confidence**: Medium — safe for normal operation; if a buffer is resized through unexpected path, stale pointer

### 4d. Constants double-visited
- Constants copied into ExecutionContext value array (ExecutionContext.h:47-48)
- Both Executable::constants AND the value array copy are independently GC-visited
- Even if constant overwritten in value array (via set()), original constant in Executable still rooted

### 4e. No concurrent execution during GC
- Single-threaded, stop-the-world GC
- No allocation/mutation during marking/sweep

## 5. Remaining Investigation Areas (lower confidence)

1. **PropertyLookupCache bypass**: If `remove_dead_cells` misses a stale entry (e.g., race between incremental sweep and cache update), a RawPtr could dangle to reused memory. Requires bug in sweep/WeakContainer interaction.

2. **Constants overwrite**: `set(Operand, Value)` can overwrite constant slots in the value array. On generator copy (ExecutionContext::copy()), the modified constant is preserved. If code expects constant objects to be immutable, this could cause type confusion.

3. **InterpreterStack deallocate during exception unwinding**: `handle_exception` (Interpreter.cpp:147-174) calls `interpreter_stack().deallocate(callee_frame)` before updating `m_running_execution_context`. If GC could trigger in that window (it can't — no allocation), the old frame would be visited. Currently safe.

4. **asm_interpreter_entry**(Interpreter.cpp:301): The assembly interpreter receives a raw `Value* values` pointer. If the bytecode is malformed, index operations via `Operand::raw()` could access out-of-bounds in the value array. This is an OOB access, not UAF.

NEXT_STEP:
1. Investigate `structuredClone` path for ArrayBuffer detachment triggering stale TypedArray cached_data_ptr
2. Check assembly interpreter for memory safety issues
3. Check if host-provided `DataBlock::UnownedExternalBuffer` can detach/realloc behind TypedArray's back
