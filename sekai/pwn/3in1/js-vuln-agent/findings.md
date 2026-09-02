STATUS: IN_PROGRESS
CONFIDENCE: medium
SUMMARY:
Ladybird LibJS binary (js.real) sử dụng bytecode compiler (Rust-based) + interpreter.
Phát hiện: Rust JIT compiler symbols (`rust_compile_function`, `rust_materialize_compiled_function`)
nhưng đây là bytecode compiler, KHÔNG phải machine-code JIT (không RWX pages).
Attack surface chính: GC engine (LibGC) + Typed Arrays + interpreter bugs.

EVIDENCE:

=== Binary Analysis ===
File: /home/light/Workspace/CTF/sekai/pwn_3in1/work/guest-runtime-agent/initramfs_root/usr/bin/js.real
- ELF 64-bit LSB PIE x86-64, stripped, dynamically linked
- ~113K binary, links to liblagom-js.so.0 (main JS engine)
- Interpreter: /lib64/ld-linux-x86-64-linux.so.2

=== Key Symbols in js.real (dynamic syms) ===
- asm_interpreter_entry — assembly interpreter entry point
- rust_compile_builtin_file — Rust bytecode compiler
- rust_compile_function
- rust_compile_eval
- rust_materialize_compiled_function
- rust_validate_bytecode
- rust_dump_bytecode
Tất cả Rust symbols đều là bytecode compiler, KHÔNG phải machine-code JIT.

=== GC Symbols (from liblagom-gc.so.0) ===
- GC::Heap::collect_garbage(CollectionType, bool) — gọi bởi gc()
- GC::CellAllocator::allocate_cell(Heap&)
- GC::HeapBlock — quản lý block-based heap
- GC::BlockAllocator — cấp phát/free block
- GC::WeakContainer — weak reference tracking
- GC::RootImpl — root handling

=== Removed Functions (from ladybird_1.patch) ===
- exit, help, save, loadINI, loadJSON, print — all removed
- Chỉ còn: gc()

=== Patch Details (ladybird_1.patch) ===
- Build LibJS standalone shell via Meta/JSOnly/CMakeLists.txt
- Vcpkg dependencies: fast-float, fmt, icu, libtommath, mimalloc, openssl, simdjson, simdutf
- Rust toolchain: channel 1.96.0

=== Known CVEs ===
- Chưa xác nhận được CVE cụ thể cho Ladybird commit 53a956c68c03
- LibGC và LibJS đều là in-house của Ladybird, không phải fork từ project khác
- Rust bytecode compiler có thể có bugs nhưng ít khả năng RCE trực tiếp

=== Attack Surface Assessment ===
1. GC::Heap::collect_garbage() — potential UAF nếu Typed Array không tracking GC root
   properly (cần verify mã nguồn LibGC/LibJS)
2. Typed Arrays (Uint8Array, etc.) — potential OOB access
3. Bytecode compiler (Rust) — potential validation bugs
4. Interpreter (asm_interpreter_entry) — potential stack/heap corruption

=== Key Difference: NOT a traditional JIT ===
Ladybird's JS engine dùng bytecode interpreter, không có machine-code JIT.
Điều này loại trừ JIT spraying technique.
Cần tìm bug trong interpreter/GC/Typed Array implementation.

NEXT_STEP:
1. Clone Ladybird source tại commit 53a956c68c03
2. Áp ladybird_1.patch và build để có debug binary
3. Audit source code của GC::Heap (collect_garbage) và Typed Array implementation
4. Tìm bug UAF hoặc heap corruption có thể trigger từ JS
5. Nếu không tìm thấy bug: thử fuzz JS engine

NEEDS_FROM_OTHER_AGENT:
- build-debug-agent: có thể build Ladybird debug binary
- exploit-primitive-agent: cần cụ thể primitive để chuyển JS exploit → native exec
