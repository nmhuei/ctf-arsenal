import unicorn
from unicorn.arm64_const import *
from elftools.elf.elffile import ELFFile
from collections import deque
import struct
import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes

inner_path = '/home/light/Workspace/CTF/ASIS_CTF_2026/Reverse/NEON/script/last-cartridge.inner'
f = open(inner_path, 'rb')
elf = ELFFile(f)
BASE_ADDR = 0x400000

mu = unicorn.Uc(unicorn.UC_ARCH_ARM64, unicorn.UC_MODE_ARM)
mu.mem_map(BASE_ADDR, 0x100000)
mu.mem_map(0x8000000, 0x1000000)
mu.mem_map(0x9000000, 0x1000000)
mu.mem_map(0xa000000, 0x100000)

for seg in elf.iter_segments():
    if seg['p_type'] == 'PT_LOAD':
        vaddr = BASE_ADDR + seg['p_vaddr']
        data = seg.data()
        mu.mem_write(vaddr, data)

rela_dyn = elf.get_section_by_name('.rela.dyn')
for rel in rela_dyn.iter_relocations():
    if rel['r_info_type'] == 1027:
        offset = BASE_ADDR + rel['r_offset']
        val = BASE_ADDR + rel['r_addend']
        mu.mem_write(offset, struct.pack('<Q', val))

heap_ptr = [0x9000000]
def hook_malloc(size, align=64):
    addr = (heap_ptr[0] + align - 1) & ~(align - 1)
    heap_ptr[0] = addr + size
    return addr

canary_addr = hook_malloc(8)
mu.mem_write(canary_addr, b'DEADBEEF')
mu.mem_write(BASE_ADDR + 0x3fff0, struct.pack('<Q', canary_addr))

evp_state = {}
aes_state = {}
dynsym = elf.get_section_by_name('.dynsym')
rela_plt = elf.get_section_by_name('.rela.plt')
plt_sec = elf.get_section_by_name('.plt')
plt_addr = plt_sec['sh_addr']
plt_hooks = {}
TRAP_BASE = 0xa000000

for i, rel in enumerate(rela_plt.iter_relocations()):
    sym_name = dynsym.get_symbol(rel['r_info_sym']).name
    got_addr = BASE_ADDR + rel['r_offset']
    trap_addr = TRAP_BASE + i * 4
    stub_addr = BASE_ADDR + plt_addr + 0x20 + i * 0x10
    
    mu.mem_write(trap_addr, b'\xc0\x03\x5f\xd6')
    mu.mem_write(stub_addr, b'\xc0\x03\x5f\xd6')
    mu.mem_write(got_addr, struct.pack('<Q', trap_addr))
    
    plt_hooks[trap_addr] = sym_name
    plt_hooks[stub_addr] = sym_name

def hook_code(uc, address, size, user_data):
    if address in plt_hooks:
        name = plt_hooks[address]
        lr = uc.reg_read(UC_ARM64_REG_X30)
        if name in ['_Znwm', 'malloc']:
            size = uc.reg_read(UC_ARM64_REG_X0)
            res = hook_malloc(size)
            uc.reg_write(UC_ARM64_REG_X0, res)
        elif name == 'mmap':
            size = uc.reg_read(UC_ARM64_REG_X1)
            res = hook_malloc(size, align=0x1000)
            uc.reg_write(UC_ARM64_REG_X0, res)
        elif name == 'munmap': uc.reg_write(UC_ARM64_REG_X0, 0)
        elif name == 'mprotect': uc.reg_write(UC_ARM64_REG_X0, 0)
        elif name in ['_ZdlPvm', 'free']: pass
        elif name in ['memcpy', 'memmove']:
            dst = uc.reg_read(UC_ARM64_REG_X0)
            src = uc.reg_read(UC_ARM64_REG_X1)
            n = uc.reg_read(UC_ARM64_REG_X2)
            if n > 0: uc.mem_write(dst, bytes(uc.mem_read(src, n)))
        elif name == 'memset':
            dst = uc.reg_read(UC_ARM64_REG_X0)
            val = uc.reg_read(UC_ARM64_REG_X1) & 0xff
            n = uc.reg_read(UC_ARM64_REG_X2)
            if n > 0: uc.mem_write(dst, bytes([val] * n))
        elif name == 'strlen':
            s = uc.reg_read(UC_ARM64_REG_X0)
            l = 0
            while uc.mem_read(s + l, 1)[0] != 0: l += 1
            uc.reg_write(UC_ARM64_REG_X0, l)
        elif name == 'OPENSSL_cleanse':
            dst = uc.reg_read(UC_ARM64_REG_X0)
            n = uc.reg_read(UC_ARM64_REG_X1)
            if n > 0:
                try: uc.mem_write(dst, bytes(n))
                except: pass
        elif name in ['CRYPTO_memcmp', 'bcmp', 'memcmp']:
            p1 = uc.reg_read(UC_ARM64_REG_X0)
            p2 = uc.reg_read(UC_ARM64_REG_X1)
            n = uc.reg_read(UC_ARM64_REG_X2)
            d1 = bytes(uc.mem_read(p1, n))
            d2 = bytes(uc.mem_read(p2, n))
            print(f'memcmp len={n}: d1={d1.hex()} vs d2={d2.hex()}')
            uc.reg_write(UC_ARM64_REG_X0, 0)
        elif name == 'EVP_sha256': uc.reg_write(UC_ARM64_REG_X0, 0x20)
        elif name == 'EVP_Digest':
            data_ptr = uc.reg_read(UC_ARM64_REG_X0)
            data_len = uc.reg_read(UC_ARM64_REG_X1)
            md_ptr = uc.reg_read(UC_ARM64_REG_X2)
            size_ptr = uc.reg_read(UC_ARM64_REG_X3)
            data = bytes(uc.mem_read(data_ptr, data_len))
            digest = hashlib.sha256(data).digest()
            uc.mem_write(md_ptr, digest)
            if size_ptr != 0: uc.mem_write(size_ptr, struct.pack('<I', 32))
            uc.reg_write(UC_ARM64_REG_X0, 1)
        elif name == 'EVP_PKEY_CTX_new_id':
            ctx = hook_malloc(0x100)
            evp_state[ctx] = {'info': b''}
            uc.reg_write(UC_ARM64_REG_X0, ctx)
        elif name == 'EVP_PKEY_CTX_free': pass
        elif name == 'EVP_PKEY_derive_init': uc.reg_write(UC_ARM64_REG_X0, 1)
        elif name == 'EVP_PKEY_CTX_set_hkdf_mode':
            ctx = uc.reg_read(UC_ARM64_REG_X0)
            mode = uc.reg_read(UC_ARM64_REG_X1)
            if ctx in evp_state: evp_state[ctx]['mode'] = mode
            uc.reg_write(UC_ARM64_REG_X0, 1)
        elif name == 'EVP_PKEY_CTX_set_hkdf_md': uc.reg_write(UC_ARM64_REG_X0, 1)
        elif name == 'EVP_PKEY_CTX_set1_hkdf_salt':
            ctx = uc.reg_read(UC_ARM64_REG_X0)
            salt_ptr = uc.reg_read(UC_ARM64_REG_X1)
            salt_len = uc.reg_read(UC_ARM64_REG_X2)
            if ctx in evp_state: evp_state[ctx]['salt'] = bytes(uc.mem_read(salt_ptr, salt_len))
            uc.reg_write(UC_ARM64_REG_X0, 1)
        elif name == 'EVP_PKEY_CTX_set1_hkdf_key':
            ctx = uc.reg_read(UC_ARM64_REG_X0)
            key_ptr = uc.reg_read(UC_ARM64_REG_X1)
            key_len = uc.reg_read(UC_ARM64_REG_X2)
            key = bytes(uc.mem_read(key_ptr, key_len))
            if key_len == 208:
                print('IKM 208 bytes:')
                print(key.hex())
                for i in range(0, 208, 16):
                    print(f'  {i:3d}..{i+16:3d}: {key[i:i+16].hex()}')
            if ctx in evp_state: evp_state[ctx]['key'] = key
            uc.reg_write(UC_ARM64_REG_X0, 1)
        elif name == 'EVP_PKEY_CTX_add1_hkdf_info':
            ctx = uc.reg_read(UC_ARM64_REG_X0)
            info_ptr = uc.reg_read(UC_ARM64_REG_X1)
            info_len = uc.reg_read(UC_ARM64_REG_X2)
            if ctx in evp_state: evp_state[ctx]['info'] += bytes(uc.mem_read(info_ptr, info_len))
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
            aes_state[ctx] = {'ct': b'', 'aad': b'', 'out_blocks': []}
            uc.reg_write(UC_ARM64_REG_X0, ctx)
        elif name == 'EVP_CIPHER_CTX_free': pass
        elif name == 'EVP_aes_256_gcm': uc.reg_write(UC_ARM64_REG_X0, 0x1)
        elif name == 'EVP_CIPHER_CTX_ctrl':
            ctx = uc.reg_read(UC_ARM64_REG_X0)
            cmd = uc.reg_read(UC_ARM64_REG_X1)
            arg = uc.reg_read(UC_ARM64_REG_X2)
            ptr = uc.reg_read(UC_ARM64_REG_X3)
            if cmd == 0x11 or cmd == 0x10:
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
                if ctx in aes_state:
                    aes_state[ctx]['aad'] += in_data
            else:
                if ctx in aes_state:
                    aes_state[ctx]['ct'] += in_data
                    aes_state[ctx]['out_blocks'].append((out_ptr, inl))
                if outl_ptr != 0:
                    uc.mem_write(outl_ptr, struct.pack('<I', inl))
            uc.reg_write(UC_ARM64_REG_X0, 1)
        elif name == 'EVP_DecryptFinal_ex':
            ctx = uc.reg_read(UC_ARM64_REG_X0)
            st = aes_state.get(ctx, {})
            ct_len = len(st.get('ct', b''))
            if ct_len == 9936:
                stage2_code = open('decrypted_stage2.bin', 'rb').read()
                for optr, olen in st.get('out_blocks', []):
                    uc.mem_write(optr, stage2_code[:olen])
                uc.reg_write(UC_ARM64_REG_X0, 1)
            elif ct_len == 48:
                try:
                    aesgcm = AESGCM(st['key'])
                    pt = aesgcm.decrypt(st['iv'], st['ct'] + st['tag'], st.get('aad', b'') if st.get('aad') else None)
                    print('========================================================')
                    print('[+] SUCCESS DECRYPTED MASTER FLAG:')
                    print(pt.decode('utf-8', errors='replace'))
                    print('========================================================')
                except Exception as e:
                    print('AESGCM DECRYPT FAIL (len=48):', e)
                uc.reg_write(UC_ARM64_REG_X0, 1)
            else:
                uc.reg_write(UC_ARM64_REG_X0, 1)
        elif name.startswith('vk') or name.startswith('SDL'):
            uc.reg_write(UC_ARM64_REG_X0, 0)
    elif address == BASE_ADDR + 0x1a958:
        print('HIT 0x1a958 (calling Stage 2 VM)!')
        x9 = uc.reg_read(UC_ARM64_REG_X9)
        def hook_s2_insn(uc, addr, size, udata):
            print('HIT Stage 2 hook at 0x%x!' % addr)
            w8 = uc.reg_read(UC_ARM64_REG_W8)
            uc.reg_write(UC_ARM64_REG_W9, w8)
            uc.hook_del(udata['handle'])
        ctx_data = {}
        h = uc.hook_add(unicorn.UC_HOOK_CODE, hook_s2_insn, user_data=ctx_data, begin=x9 + 0x34c, end=x9 + 0x350)
        ctx_data['handle'] = h

num_plt = len(list(rela_plt.iter_relocations()))
mu.hook_add(unicorn.UC_HOOK_CODE, hook_code, begin=TRAP_BASE, end=TRAP_BASE + 0x1000)
mu.hook_add(unicorn.UC_HOOK_CODE, hook_code, begin=BASE_ADDR + plt_addr, end=BASE_ADDR + plt_addr + num_plt * 0x10 + 0x20)
mu.hook_add(unicorn.UC_HOOK_CODE, hook_code, begin=BASE_ADDR + 0x1a958, end=BASE_ADDR + 0x1a95c)

def hook_branches(uc, addr, size, udata):
    if addr == BASE_ADDR + 0x11044:
        w9 = uc.reg_read(UC_ARM64_REG_W9)
        print(f'At 0x11044: tbz w9, #0 -> w9=0x{w9:x}')
    elif addr == BASE_ADDR + 0x11420:
        nzcv = uc.reg_read(UC_ARM64_REG_NZCV)
        print(f'At 0x11420: b.ne -> nzcv=0x{nzcv:x}')
    elif addr == BASE_ADDR + 0x11454:
        nzcv = uc.reg_read(UC_ARM64_REG_NZCV)
        print(f'At 0x11454: b.ne -> nzcv=0x{nzcv:x}')
    elif addr == BASE_ADDR + 0x11494:
        w8 = uc.reg_read(UC_ARM64_REG_W8)
        print(f'At 0x11494: cbz w8 -> w8=0x{w8:x}')

mu.hook_add(unicorn.UC_HOOK_CODE, hook_branches, begin=BASE_ADDR + 0x11044, end=BASE_ADDR + 0x11048)
mu.hook_add(unicorn.UC_HOOK_CODE, hook_branches, begin=BASE_ADDR + 0x11420, end=BASE_ADDR + 0x11424)
mu.hook_add(unicorn.UC_HOOK_CODE, hook_branches, begin=BASE_ADDR + 0x11454, end=BASE_ADDR + 0x11458)
mu.hook_add(unicorn.UC_HOOK_CODE, hook_branches, begin=BASE_ADDR + 0x11494, end=BASE_ADDR + 0x11498)

def hook_f160(uc, addr, size, udata):
    if addr == BASE_ADDR + 0xf160:
        sp_val = uc.reg_read(UC_ARM64_REG_SP)
        x25 = uc.reg_read(UC_ARM64_REG_X25)
        x26 = uc.reg_read(UC_ARM64_REG_X26)
        x27 = uc.reg_read(UC_ARM64_REG_X27)
        x19 = uc.reg_read(UC_ARM64_REG_X19)
        x21 = uc.reg_read(UC_ARM64_REG_X21)
        x23 = uc.reg_read(UC_ARM64_REG_X23)
        print(f'At 0xf160: sp=0x{sp_val:x}, x25=0x{x25:x}, x26=0x{x26:x}, x27=0x{x27:x}, x19=0x{x19:x}, x21=0x{x21:x}, x23=0x{x23:x}')
    elif addr == BASE_ADDR + 0xf290:
        x8 = uc.reg_read(UC_ARM64_REG_X8)
        print(f'At 0xf290: rolling hash x8 = 0x{x8:016x}')

mu.hook_add(unicorn.UC_HOOK_CODE, hook_f160, begin=BASE_ADDR + 0xf160, end=BASE_ADDR + 0xf164)
mu.hook_add(unicorn.UC_HOOK_CODE, hook_f160, begin=BASE_ADDR + 0xf290, end=BASE_ADDR + 0xf294)

def hook_f1e4(uc, addr, size, udata):
    if addr == BASE_ADDR + 0xf1e4:
        sp_val = uc.reg_read(UC_ARM64_REG_SP)
        x10 = struct.unpack('<Q', bytes(uc.mem_read(sp_val + 0x148, 8)))[0]
        x11 = struct.unpack('<Q', bytes(uc.mem_read(sp_val + 0x150, 8)))[0]
        print(f'At 0xf1e4: sp=0x{sp_val:x}, [sp+0x148]=0x{x10:x}, [sp+0x150]=0x{x11:x}')
        q0 = bytes(uc.mem_read(x11, 16)).hex()
        q1 = bytes(uc.mem_read(x11 + 16, 16)).hex()
        q2 = bytes(uc.mem_read(x10, 16)).hex()
        q3 = bytes(uc.mem_read(x10 + 16, 16)).hex()
        print(f'  from x11: q0={q0}, q1={q1}')
        print(f'  from x10: q0={q2}, q2={q3}')

mu.hook_add(unicorn.UC_HOOK_CODE, hook_f1e4, begin=BASE_ADDR + 0xf1e4, end=BASE_ADDR + 0xf1e8)

def hook_f14c(uc, addr, size, udata):
    if addr == BASE_ADDR + 0xf14c:
        q0 = bytes(uc.reg_read(UC_ARM64_REG_Q0)).hex()
        q1 = bytes(uc.reg_read(UC_ARM64_REG_Q1)).hex()
        print(f'At 0xf14c: q0={q0}, q1={q1}')
    elif addr == BASE_ADDR + 0xf21c:
        x10 = uc.reg_read(UC_ARM64_REG_X10)
        data = bytes(uc.mem_read(x10, 32)).hex()
        print(f'At 0xf21c: [x10]={data}')

mu.hook_add(unicorn.UC_HOOK_CODE, hook_f14c, begin=BASE_ADDR + 0xf14c, end=BASE_ADDR + 0xf150)
mu.hook_add(unicorn.UC_HOOK_CODE, hook_f14c, begin=BASE_ADDR + 0xf21c, end=BASE_ADDR + 0xf220)

def hook_f148(uc, addr, size, udata):
    if addr == BASE_ADDR + 0xf148:
        sp_val = uc.reg_read(UC_ARM64_REG_SP)
        x8 = struct.unpack('<Q', bytes(uc.mem_read(sp_val + 0x140, 8)))[0]
        print(f'At 0xf148: sp=0x{sp_val:x}, [sp+0x140]=0x{x8:x}')
    elif addr == BASE_ADDR + 0xf204:
        sp_val = uc.reg_read(UC_ARM64_REG_SP)
        x10 = struct.unpack('<Q', bytes(uc.mem_read(sp_val + 0x140, 8)))[0]
        print(f'At 0xf204: sp=0x{sp_val:x}, [sp+0x140]=0x{x10:x}')

mu.hook_add(unicorn.UC_HOOK_CODE, hook_f148, begin=BASE_ADDR + 0xf148, end=BASE_ADDR + 0xf14c)
mu.hook_add(unicorn.UC_HOOK_CODE, hook_f148, begin=BASE_ADDR + 0xf204, end=BASE_ADDR + 0xf208)

def hook_after_s2(uc, addr, size, udata):
    w0 = uc.reg_read(UC_ARM64_REG_W0)
    print('After Stage 2 VM: w0 = 0x%08x' % w0)
mu.hook_add(unicorn.UC_HOOK_CODE, hook_code, begin=BASE_ADDR + 0x1a958, end=BASE_ADDR + 0x1a95c)
mu.hook_add(unicorn.UC_HOOK_CODE, hook_after_s2, begin=BASE_ADDR + 0x1a95c, end=BASE_ADDR + 0x1a960)

sp = 0x8100000
mu.reg_write(UC_ARM64_REG_SP, sp)
mu.reg_write(UC_ARM64_REG_X30, 0xdeadbeef)
mu.emu_start(BASE_ADDR + 0x3000, 0xdeadbeef)

game_struct = hook_malloc(0x3000)
mu.reg_write(UC_ARM64_REG_SP, sp)
mu.reg_write(UC_ARM64_REG_X0, game_struct)
mu.reg_write(UC_ARM64_REG_X30, 0xdeadbeef)
mu.emu_start(BASE_ADDR + 0xd378, 0xdeadbeef)

def do_step(act, arg=0):
    mu.reg_write(UC_ARM64_REG_SP, sp)
    mu.reg_write(UC_ARM64_REG_X0, game_struct)
    mu.reg_write(UC_ARM64_REG_X1, act)
    mu.reg_write(UC_ARM64_REG_X2, arg)
    mu.reg_write(UC_ARM64_REG_X30, 0xdeadbeef)
    # Ensure stack frame pointers are consistently pointing into game_struct
    # [sp - 0x400 + 0x140] = game_struct + 0x14b8
    # [sp - 0x400 + 0x148] = game_struct + 0x1488
    # [sp - 0x400 + 0x28]  = game_struct + 0x149c
    stack_base = sp - 0x500
    mu.mem_write(stack_base + 0x140, struct.pack('<QQ', game_struct + 0x14b8, game_struct + 0x1488))
    mu.mem_write(stack_base + 0x28, struct.pack('<Q', game_struct + 0x149c))
    mu.emu_start(BASE_ADDR + 0xe198, 0xdeadbeef)

def bfs_path(grid, start, end, blocked_tiles=None):
    if blocked_tiles is None: blocked_tiles = set()
    queue = deque([[start]])
    visited = {start} | blocked_tiles
    while queue:
        path = queue.popleft()
        cx, cy = path[-1]
        if (cx, cy) == end: return path
        for act, (dx, dy) in [(1, (0, -1)), (2, (0, 1)), (3, (-1, 0)), (4, (1, 0))]:
            nx, ny = cx + dx, cy + dy
            if 0 <= ny < len(grid) and 0 <= nx < len(grid[ny]):
                c = grid[ny][nx]
                if c not in [' ', '#'] and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append(path + [(nx, ny)])
    return None

def path_to_moves(p):
    if not p: return []
    m = []
    for i in range(len(p)-1):
        x1, y1 = p[i]
        x2, y2 = p[i+1]
        if y2 == y1 - 1: m.append(1)
        elif y2 == y1 + 1: m.append(2)
        elif x2 == x1 - 1: m.append(3)
        elif x2 == x1 + 1: m.append(4)
    return m

grid = [
'  ..                ',
'  ...               ',
'  @+.-       .      ',
'  .....    .....    ',
'  ........#....>..  ',
'  ........#.......  ',
'  ........#.......  ',
'  ........#.......  ',
'  ........#.......  ',
'   .......#.......  ',
'   .......##......  ',
'    .......##.....  ',
'     .......##..... ',
'      .......#..... ',
'        .....D......',
'               .....',
]

# Rooms 0..5
for act in path_to_moves(bfs_path(grid, (2, 2), (5, 2), blocked_tiles={(3, 2)})) + path_to_moves(bfs_path(grid, (5, 2), (13, 14))) + path_to_moves(bfs_path(grid, (13, 14), (15, 4))): do_step(act)
for act in path_to_moves(bfs_path(grid, (2, 2), (5, 2))) + path_to_moves(bfs_path(grid, (5, 2), (13, 14))) + path_to_moves(bfs_path(grid, (13, 14), (15, 4))): do_step(act)
for act in path_to_moves(bfs_path(grid, (2, 2), (5, 2))) + path_to_moves(bfs_path(grid, (5, 2), (6, 4))) + path_to_moves(bfs_path(grid, (6, 4), (13, 14))) + path_to_moves(bfs_path(grid, (13, 14), (15, 4))): do_step(act)
for act in path_to_moves(bfs_path(grid, (2, 2), (5, 2))): do_step(act)
do_step(11) # return
for act in path_to_moves(bfs_path(grid, (5, 2), (13, 14))) + path_to_moves(bfs_path(grid, (13, 14), (15, 4))): do_step(act)
for act in path_to_moves(bfs_path(grid, (2, 2), (4, 2))): do_step(act)
do_step(6)
for act in path_to_moves(bfs_path(grid, (4, 2), (13, 14))) + path_to_moves(bfs_path(grid, (13, 14), (15, 4))): do_step(act)
for act in path_to_moves(bfs_path(grid, (2, 2), (5, 2))): do_step(act)
for _ in range(5): do_step(5)
do_step(7)
for act in path_to_moves(bfs_path(grid, (5, 2), (13, 14))) + path_to_moves(bfs_path(grid, (13, 14), (15, 4))): do_step(act)

# In Room 6:
r6_actions = [4, 8, 5, 1, 2, 9, 7, 4, 4, 2, 10, 4, 5, 2, 6, 4] + [5]*15 + [11]
for act in r6_actions:
    do_step(act, arg=(act-7 if act in [8, 9, 10] else 0))
