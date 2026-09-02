#!/usr/bin/env python3
"""Solve 'Write The Кодэ' (grodnoCTF).
Reproduces the modified-TCC 'audit' provenance hash over RELA relocations of
/proc/self/exe, XOR-decodes the embedded VM blob, then solves the per-char
state machine for the flag.
"""
import struct

M64 = 0xFFFFFFFFFFFFFFFF
M32 = 0xFFFFFFFF


def rotl64(x, n):
    x &= M64
    return ((x << n) | (x >> (64 - n))) & M64


def provenance_hash(path):
    """Mirror of sub_401F92: hash over SHT_RELA entries of the ELF."""
    data = open(path, "rb").read()
    e_shoff = struct.unpack_from("<Q", data, 0x28)[0]
    e_shentsize = struct.unpack_from("<H", data, 0x3A)[0]
    e_shnum = struct.unpack_from("<H", data, 0x3C)[0]
    state = 0x6A09E667F3BCC909
    for i in range(e_shnum):
        off = e_shoff + i * e_shentsize
        shdr = data[off:off + 0x40]
        sh_type, sh_offset, sh_size = struct.unpack_from("<IQ Q".replace(" ", ""), shdr, 4) if False else (struct.unpack_from("<I", shdr, 4)[0], struct.unpack_from("<Q", shdr, 0x18)[0], struct.unpack_from("<Q", shdr, 0x20)[0])
        if sh_type != 4:  # SHT_RELA
            continue
        count = sh_size // 24
        for j in range(count):
            r_info, r_addend = struct.unpack_from("<Qq", data, sh_offset + j * 24 + 8)
            state ^= (r_info + 0x9E3779B97F4A7C15 + (i << 32) + j) & M64
            state = rotl64(state, 17)
            state = (state * 0xBF58476D1CE4E5B9) & M64
            state ^= r_addend & M64
    return state & M64


def mix(ptr):  # sub_40220C, state mutated in place
    x = ptr[0]
    ptr[0] = (ptr[0] ^ (ptr[0] >> 12)) & M64
    ptr[0] = (ptr[0] ^ ((ptr[0] << 25) & M64)) & M64
    ptr[0] = (ptr[0] ^ (ptr[0] >> 27)) & M64
    return (ptr[0] * 0x2545F4914F6CDD1D) & M64


def decode_blob(path):
    """Read the 0x200-byte blob at vaddr 0x405B34, XOR with mix(hash) stream."""
    elf = open(path, "rb").read()
    # find section containing 0x405B34
    e_shoff = struct.unpack_from("<Q", elf, 0x28)[0]
    e_shentsize = struct.unpack_from("<H", elf, 0x3A)[0]
    e_shnum = struct.unpack_from("<H", elf, 0x3C)[0]
    for i in range(e_shnum):
        off = e_shoff + i * e_shentsize
        sh_addr, sh_offset, sh_size = struct.unpack_from("<QQQ", elf, off + 0x10)
        if sh_addr <= 0x405B34 < sh_addr + sh_size:
            file_off = sh_offset + (0x405B34 - sh_addr)
            enc = elf[file_off:file_off + 0x200]
            break
    else:
        raise RuntimeError("blob section not found")
    h = provenance_hash(path)
    st = [h]
    blob = bytearray()
    for b in enc:
        blob.append(b ^ (mix(st) >> 56))
    return bytes(blob)


def rotl32(x, n):
    x &= M32
    if n == 0:
        return x
    return ((x << n) | (x >> (32 - n))) & M32


def rotr32(x, n):
    return rotl32(x, (32 - n) & 31) if n else x


def solve_vm(blob):
    assert blob[2] == 0x51, hex(blob[2])
    n = struct.unpack_from("<H", blob, 0)[0]
    assert 8 <= n <= 0x1F4
    p = 3
    state = 0xC0DEC0DE
    flag = []
    for i in range(n):
        assert blob[p] == 0xA7, (i, p, hex(blob[p]))
        add_ = blob[p + 1]
        rot = blob[p + 2] & 0x1F
        exp = struct.unpack_from("<I", blob, p + 3)[0]
        p += 7
        mixadd = ((i * 0x45D9F3B) & M32) ^ 0x9E3779B9
        t3 = (exp - mixadd) & M32
        t1 = rotr32(t3, rot)
        c = ((t1 ^ state) - add_) & 0xFF
        # answer char must be nonzero, printable; try ascii decode
        if not (0x20 <= c <= 0x7E):
            print(f"WARN: char {i} out of printable range: {hex(c)}")
        flag.append(chr(c))
        state = t3  # state after this element == expected == t3
    return "".join(flag)


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "/tmp/re/kode/dist/checker"
    blob = decode_blob(path)
    print("blob[:16]", blob[:16].hex())
    print("len, map[2]:", struct.unpack_from("<H", blob, 0)[0], hex(blob[2]))
    flag = solve_vm(blob)
    print("FLAG:", flag)
    print("len:", len(flag))
