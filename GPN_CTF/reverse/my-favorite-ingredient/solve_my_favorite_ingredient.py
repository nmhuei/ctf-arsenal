#!/usr/bin/env python3
import ctypes
import os
import subprocess
import sys
import tempfile
from pathlib import Path

MOD = 256
C_LOADER = r'''
#define _GNU_SOURCE
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <elf.h>

static uint8_t *base = NULL;
typedef void (*matvec_fn_t)(uint8_t *matrix, const uint8_t *in, uint8_t *out);
static matvec_fn_t matvec = NULL;
static uint8_t *matrix = NULL;
static uint8_t *target = NULL;

int mfi_init(const char *path) {
    int fd = open(path, O_RDONLY);
    if (fd < 0) { perror("open"); return -1; }
    struct stat st;
    if (fstat(fd, &st) != 0) { perror("fstat"); close(fd); return -1; }
    uint8_t *file = mmap(NULL, st.st_size, PROT_READ, MAP_PRIVATE, fd, 0);
    if (file == MAP_FAILED) { perror("mmap file"); close(fd); return -1; }
    Elf64_Ehdr *eh = (Elf64_Ehdr*)file;
    if (memcmp(eh->e_ident, ELFMAG, SELFMAG) != 0) { fprintf(stderr,"not ELF\n"); return -1; }
    Elf64_Phdr *ph = (Elf64_Phdr*)(file + eh->e_phoff);
    uint64_t maxend = 0;
    for (int i=0; i<eh->e_phnum; i++) if (ph[i].p_type == PT_LOAD) {
        uint64_t end = ph[i].p_vaddr + ph[i].p_memsz;
        if (end > maxend) maxend = end;
    }
    size_t mapsz = (maxend + 0xfff) & ~0xfffull;
    base = mmap(NULL, mapsz, PROT_READ|PROT_WRITE|PROT_EXEC, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0);
    if (base == MAP_FAILED) { perror("mmap anon"); return -1; }
    memset(base, 0, mapsz);
    for (int i=0; i<eh->e_phnum; i++) if (ph[i].p_type == PT_LOAD)
        memcpy(base + ph[i].p_vaddr, file + ph[i].p_offset, ph[i].p_filesz);
    munmap(file, st.st_size);
    close(fd);
    matvec = (matvec_fn_t)(base + 0x15b0);   // matvec_mul_vectorized
    matrix = base + 0x31170;                 // 64x64 byte matrix in .rodata
    target = base + 0x32170;                 // 64-byte target in .rodata
    return 0;
}

void mfi_eval_original(const uint8_t in[64], uint8_t out[64]) {
    uint8_t pre[64];
    // verify_flag first maps x -> 197*x + 101; matvec immediately applies the inverse.
    for (int i=0; i<64; i++) pre[i] = (uint8_t)(197u * in[i] + 101u);
    matvec(matrix, pre, out);
}

void mfi_get_target(uint8_t out[64]) {
    for (int i=0; i<64; i++) out[i] = (uint8_t)~target[i];
}

int mfi_verify(const uint8_t in[64]) {
    uint8_t out[64], tgt[64];
    mfi_eval_original(in, out);
    mfi_get_target(tgt);
    return memcmp(out, tgt, 64) == 0;
}
'''

def compile_loader() -> Path:
    td = Path(tempfile.mkdtemp(prefix='mfi_solver_'))
    c_path = td / 'mfi_loader.c'
    so_path = td / 'mfi_loader.so'
    c_path.write_text(C_LOADER)
    subprocess.check_call(['gcc', '-shared', '-fPIC', '-O2', '-o', str(so_path), str(c_path)])
    return so_path

def deaffine(bs: bytes) -> bytes:
    # inverse of y = 197*x + 101 mod 256; because 13*197 == 1 and 13*101 + 0xdf == 0 mod 256
    return bytes(((13 * b + 0xdf) & 0xff) for b in bs)

def inv_odd(a: int) -> int:
    return pow(a, -1, MOD)

def solve_mod256(A, b):
    n = len(b)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    r = 0
    for c in range(n):
        piv = next((i for i in range(r, n) if M[i][c] & 1), None)
        if piv is None:
            continue
        M[r], M[piv] = M[piv], M[r]
        inv = inv_odd(M[r][c])
        for j in range(c, n + 1):
            M[r][j] = (M[r][j] * inv) & 0xff
        for i in range(n):
            if i != r and M[i][c]:
                f = M[i][c]
                for j in range(c, n + 1):
                    M[i][j] = (M[i][j] - f * M[r][j]) & 0xff
        r += 1
        if r == n:
            break
    if r != n:
        raise RuntimeError(f'matrix rank with invertible pivots is only {r}/{n}')
    return bytes(M[i][n] & 0xff for i in range(n))

def main():
    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} ./my-favorite-ingredient', file=sys.stderr)
        sys.exit(1)
    bin_path = Path(sys.argv[1]).resolve()
    so_path = compile_loader()
    lib = ctypes.CDLL(str(so_path))
    lib.mfi_init.argtypes = [ctypes.c_char_p]
    lib.mfi_init.restype = ctypes.c_int
    if lib.mfi_init(str(bin_path).encode()) != 0:
        raise SystemExit('mfi_init failed')

    def run(inp: bytes) -> bytes:
        assert len(inp) == 64
        In = (ctypes.c_ubyte * 64).from_buffer_copy(inp)
        Out = (ctypes.c_ubyte * 64)()
        lib.mfi_eval_original(In, Out)
        return bytes(Out)

    def matvec(inp: bytes) -> bytes:
        return deaffine(run(inp))

    cols = []
    for j in range(64):
        e = bytearray(64)
        e[j] = 1
        cols.append(matvec(bytes(e)))
    A = [[cols[c][r] for c in range(64)] for r in range(64)]

    tgt = (ctypes.c_ubyte * 64)()
    lib.mfi_get_target(tgt)
    rhs = deaffine(bytes(tgt))
    flag = solve_mod256(A, list(rhs))

    print(flag.decode('ascii'))
    ok = lib.mfi_verify((ctypes.c_ubyte * 64).from_buffer_copy(flag))
    print('[+] local verify via mapped binary code:', bool(ok))
    try:
        p = subprocess.run([str(bin_path), flag.decode('ascii')], text=True, capture_output=True, timeout=5)
        print('[+] local verify via original binary:', (p.stdout + p.stderr).strip())
    except Exception as e:
        print('[!] could not execute original binary:', e)

if __name__ == '__main__':
    main()
