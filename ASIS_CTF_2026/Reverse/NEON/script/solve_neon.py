#!/usr/bin/env python3
import sys
import struct
import unicorn
from unicorn.arm64_const import *
from elftools.elf.elffile import ELFFile
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes

inner_path = 'ASIS_CTF_2026/Reverse/NEON/script/last-cartridge.inner'
f = open(inner_path, 'rb')
elf = ELFFile(f)

BASE_ADDR = 0x400000
mu = unicorn.Uc(unicorn.UC_ARCH_ARM64, unicorn.UC_MODE_ARM)

# Map pages
mu.mem_map(BASE_ADDR, 0x100000)
mu.mem_map(0x8000000, 0x200000) # Stack
mu.mem_map(0x9000000, 0x500000) # Heap
mu.mem_map(0xa000000, 0x100000) # PLT Trap area

for seg in elf.iter_segments():
    if seg['p_type'] == 'PT_LOAD':
        vaddr = BASE_ADDR + seg['p_vaddr']
        memsz = (seg['p_memsz'] + 0xfff) & ~0xfff
        data = seg.data()
        mu.mem_write(vaddr, data)

# Apply RELATIVE relocations
rela_dyn = elf.get_section_by_name('.rela.dyn')
for rel in rela_dyn.iter_relocations():
    if rel['r_info_type'] == 1027: # R_AARCH64_RELATIVE
        offset = BASE_ADDR + rel['r_offset']
        val = BASE_ADDR + rel['r_addend']
        mu.mem_write(offset, struct.pack('<Q', val))

# Heap manager
heap_ptr = 0x9000000
allocated = {}

def hook_malloc(size):
    global heap_ptr
    addr = heap_ptr
    heap_ptr = (heap_ptr + size + 31) & ~31
    allocated[addr] = size
    return addr

# Crypto state tracker
evp_state = {}
aes_state = {}

# Set up PLT stubs
dynsym = elf.get_section_by_name('.dynsym')
rela_plt = elf.get_section_by_name('.rela.plt')
plt_hooks = {}

TRAP_BASE = 0xa000000
for i, rel in enumerate(rela_plt.iter_relocations()):
    sym_name = dynsym.get_symbol(rel['r_info_sym']).name
    got_addr = BASE_ADDR + rel['r_offset']
    trap_addr = TRAP_BASE + i * 4
    mu.mem_write(trap_addr, b'\xc0\x03\x5f\xd6') # ret
    mu.mem_write(got_addr, struct.pack('<Q', trap_addr))
    plt_hooks[trap_addr] = sym_name

def hook_code(uc, address, size, user_data):
    if address in plt_hooks:
        name = plt_hooks[address]
        if name in ['_Znwm', 'malloc']:
            size = uc.reg_read(UC_ARM64_REG_X0)
            res = hook_malloc(size)
            uc.reg_write(UC_ARM64_REG_X0, res)
        elif name in ['_ZdlPvm', 'free']:
            pass
        elif name == 'memcpy':
            dst = uc.reg_read(UC_ARM64_REG_X0)
            src = uc.reg_read(UC_ARM64_REG_X1)
            n = uc.reg_read(UC_ARM64_REG_X2)
            if n > 0:
                data = uc.mem_read(src, n)
                uc.mem_write(dst, bytes(data))
        elif name == 'memset':
            dst = uc.reg_read(UC_ARM64_REG_X0)
            val = uc.reg_read(UC_ARM64_REG_X1) & 0xff
            n = uc.reg_read(UC_ARM64_REG_X2)
            if n > 0:
                uc.mem_write(dst, bytes([val] * n))
        elif name == 'memmove':
            dst = uc.reg_read(UC_ARM64_REG_X0)
            src = uc.reg_read(UC_ARM64_REG_X1)
            n = uc.reg_read(UC_ARM64_REG_X2)
            if n > 0:
                data = uc.mem_read(src, n)
                uc.mem_write(dst, bytes(data))
        elif name == 'strlen':
            s = uc.reg_read(UC_ARM64_REG_X0)
            l = 0
            while uc.mem_read(s + l, 1)[0] != 0:
                l += 1
            uc.reg_write(UC_ARM64_REG_X0, l)
        elif name == 'OPENSSL_cleanse':
            dst = uc.reg_read(UC_ARM64_REG_X0)
            n = uc.reg_read(UC_ARM64_REG_X1)
            if n > 0:
                uc.mem_write(dst, bytes(n))
        elif name == 'CRYPTO_memcmp' or name == 'bcmp':
            p1 = uc.reg_read(UC_ARM64_REG_X0)
            p2 = uc.reg_read(UC_ARM64_REG_X1)
            n = uc.reg_read(UC_ARM64_REG_X2)
            d1 = uc.mem_read(p1, n)
            d2 = uc.mem_read(p2, n)
            uc.reg_write(UC_ARM64_REG_X0, 0 if d1 == d2 else 1)
        elif name == 'EVP_PKEY_CTX_new_id':
            ctx = hook_malloc(0x100)
            evp_state[ctx] = {'info': b''}
            uc.reg_write(UC_ARM64_REG_X0, ctx)
        elif name == 'EVP_PKEY_CTX_free':
            pass
        elif name == 'EVP_PKEY_derive_init':
            uc.reg_write(UC_ARM64_REG_X0, 1)
        elif name == 'EVP_PKEY_CTX_set_hkdf_mode':
            ctx = uc.reg_read(UC_ARM64_REG_X0)
            mode = uc.reg_read(UC_ARM64_REG_X1)
            if ctx in evp_state: evp_state[ctx]['mode'] = mode
            uc.reg_write(UC_ARM64_REG_X0, 1)
        elif name == 'EVP_PKEY_CTX_set_hkdf_md':
            uc.reg_write(UC_ARM64_REG_X0, 1)
        elif name == 'EVP_PKEY_CTX_set1_hkdf_salt':
            ctx = uc.reg_read(UC_ARM64_REG_X0)
            salt_ptr = uc.reg_read(UC_ARM64_REG_X1)
            salt_len = uc.reg_read(UC_ARM64_REG_X2)
            if ctx in evp_state:
                evp_state[ctx]['salt'] = bytes(uc.mem_read(salt_ptr, salt_len))
            uc.reg_write(UC_ARM64_REG_X0, 1)
        elif name == 'EVP_PKEY_CTX_set1_hkdf_key':
            ctx = uc.reg_read(UC_ARM64_REG_X0)
            key_ptr = uc.reg_read(UC_ARM64_REG_X1)
            key_len = uc.reg_read(UC_ARM64_REG_X2)
            if ctx in evp_state:
                evp_state[ctx]['key'] = bytes(uc.mem_read(key_ptr, key_len))
            uc.reg_write(UC_ARM64_REG_X0, 1)
        elif name == 'EVP_PKEY_CTX_add1_hkdf_info':
            ctx = uc.reg_read(UC_ARM64_REG_X0)
            info_ptr = uc.reg_read(UC_ARM64_REG_X1)
            info_len = uc.reg_read(UC_ARM64_REG_X2)
            if ctx in evp_state:
                evp_state[ctx]['info'] += bytes(uc.mem_read(info_ptr, info_len))
            uc.reg_write(UC_ARM64_REG_X0, 1)
        elif name == 'EVP_PKEY_derive':
            ctx = uc.reg_read(UC_ARM64_REG_X0)
            out_ptr = uc.reg_read(UC_ARM64_REG_X1)
            outlen_ptr = uc.reg_read(UC_ARM64_REG_X2)
            outlen = struct.unpack('<Q', bytes(uc.mem_read(outlen_ptr, 8)))[0]
            st = evp_state.get(ctx, {})
            hkdf = HKDF(algorithm=hashes.SHA256(), length=outlen, salt=st.get('salt'), info=st.get('info'))
            derived = hkdf.derive(st.get('key', b''))
            uc.mem_write(out_ptr, derived)
            uc.mem_write(outlen_ptr, struct.pack('<Q', len(derived)))
            uc.reg_write(UC_ARM64_REG_X0, 1)
        elif name == 'EVP_CIPHER_CTX_new':
            ctx = hook_malloc(0x100)
            aes_state[ctx] = {}
            uc.reg_write(UC_ARM64_REG_X0, ctx)
        elif name == 'EVP_CIPHER_CTX_free':
            pass
        elif name == 'EVP_aes_256_gcm':
            uc.reg_write(UC_ARM64_REG_X0, 0x1)
        elif name == 'EVP_CIPHER_CTX_ctrl':
            ctx = uc.reg_read(UC_ARM64_REG_X0)
            cmd = uc.reg_read(UC_ARM64_REG_X1)
            arg = uc.reg_read(UC_ARM64_REG_X2)
            ptr = uc.reg_read(UC_ARM64_REG_X3)
            if cmd == 0x11:
                if ctx in aes_state:
                    aes_state[ctx]['tag'] = bytes(uc.mem_read(ptr, arg))
            uc.reg_write(UC_ARM64_REG_X0, 1)
        elif name == 'EVP_DecryptInit_ex':
            ctx = uc.reg_read(UC_ARM64_REG_X0)
            key_ptr = uc.reg_read(UC_ARM64_REG_X3)
            iv_ptr = uc.reg_read(UC_ARM64_REG_X4)
            if key_ptr != 0 and ctx in aes_state:
                aes_state[ctx]['key'] = bytes(uc.mem_read(key_ptr, 32))
            if iv_ptr != 0 and ctx in aes_state:
                aes_state[ctx]['iv'] = bytes(uc.mem_read(iv_ptr, 12))
            uc.reg_write(UC_ARM64_REG_X0, 1)
        elif name == 'EVP_DecryptUpdate':
            ctx = uc.reg_read(UC_ARM64_REG_X0)
            out_ptr = uc.reg_read(UC_ARM64_REG_X1)
            outl_ptr = uc.reg_read(UC_ARM64_REG_X2)
            in_ptr = uc.reg_read(UC_ARM64_REG_X3)
            inl = uc.reg_read(UC_ARM64_REG_X4)
            in_data = bytes(uc.mem_read(in_ptr, inl))
            if out_ptr == 0:
                if ctx in aes_state: aes_state[ctx]['aad'] = in_data
            else:
                if ctx in aes_state: aes_state[ctx]['ct'] = in_data
                aes_state[ctx]['out_ptr'] = out_ptr
                aes_state[ctx]['outl_ptr'] = outl_ptr
            uc.reg_write(UC_ARM64_REG_X0, 1)
        elif name == 'EVP_DecryptFinal_ex':
            ctx = uc.reg_read(UC_ARM64_REG_X0)
            st = aes_state.get(ctx, {})
            try:
                aesgcm = AESGCM(st['key'])
                pt = aesgcm.decrypt(st['iv'], st['ct'] + st['tag'], st.get('aad'))
                print('[+] AES-GCM DECRYPT SUCCESS! Plaintext:', pt)
                if b'ASIS{' in pt:
                    print('[+] FOUND FLAG:', pt.decode('latin1'))
                uc.mem_write(st['out_ptr'], pt)
                uc.mem_write(st['outl_ptr'], struct.pack('<I', len(pt)))
                uc.reg_write(UC_ARM64_REG_X0, 1)
            except Exception as e:
                print('[-] AES-GCM Decrypt failed:', e)
                uc.reg_write(UC_ARM64_REG_X0, 0)
        elif name.startswith('vk') or name.startswith('SDL'):
            uc.reg_write(UC_ARM64_REG_X0, 0)
        else:
            print(f'Unhandled PLT stub: {name}')

mu.hook_add(unicorn.UC_HOOK_CODE, hook_code)

sp = 0x8100000
mu.reg_write(UC_ARM64_REG_SP, sp)
mu.reg_write(UC_ARM64_REG_X30, 0xdeadbeef)

print('Running constructors at 0x403000...')
mu.emu_start(BASE_ADDR + 0x3000, 0xdeadbeef)
print('Constructors executed successfully!')

game_struct = hook_malloc(0x3000)

print('Running Game Init (0xd378)...')
mu.reg_write(UC_ARM64_REG_SP, sp)
mu.reg_write(UC_ARM64_REG_X0, game_struct)
mu.reg_write(UC_ARM64_REG_X30, 0xdeadbeef)
mu.emu_start(BASE_ADDR + 0xd378, 0xdeadbeef)
print('Game Init completed successfully!')
