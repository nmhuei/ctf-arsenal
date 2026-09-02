from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import random, re, time
random.seed(0)

ct = bytes.fromhex('6ccb80c46c19243a37633d316a66871ca70ec8a44f48a80134f31d8d27f920c6bd5d810831833221d0f282130d2c222de38c2080ef995b2ad10dc5af8518')
known = {i:b for i,b in enumerate(b'Congratulations! hkcert21{')}
known[len(ct)-1]=ord('}')
positions = sorted(known)
m = len(positions)*8
print('known bytes', len(positions), 'bits', m, 'n', 256)

def stream_for_keybyte(k, n):
    cipher = Cipher(algorithms.AES(bytes([k])+b'\0'*15), modes.CTR(b'\0'*16))
    enc = cipher.encryptor()
    return enc.update(b'\0'*n) + enc.finalize()

streams = [stream_for_keybyte(k, len(ct)) for k in range(256)]

def pack_known(bs):
    x=0; bit=0
    for pos in positions:
        val = bs[pos]
        for b in range(8):
            if (val>>b)&1:
                x |= 1<<bit
            bit += 1
    return x

cols = [pack_known(s) for s in streams]
target_bytes = bytearray(len(ct))
for pos,b in known.items():
    target_bytes[pos] = ct[pos] ^ b
target = pack_known(target_bytes)

def solve_basis(sel):
    # Solve M*y = target where M's columns are cols[sel[j]] over GF(2).
    # rows are augmented coefficient rows (m coeff bits + rhs at bit m)
    rows = []
    for i in range(m):
        row=0
        mask=1<<i
        for j,idx in enumerate(sel):
            if cols[idx] & mask:
                row |= 1<<j
        if target & mask:
            row |= 1<<m
        rows.append(row)
    rank = 0
    pivots = []
    for col in range(m):
        pivot = None
        bit = 1<<col
        for r in range(rank, m):
            if rows[r] & bit:
                pivot = r; break
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        # eliminate all other rows for direct solution
        for r in range(m):
            if r != rank and (rows[r] & bit):
                rows[r] ^= rows[rank]
        pivots.append(col)
        rank += 1
        if rank == m: break
    if rank < m:
        return None, rank
    sol=0
    for i,col in enumerate(pivots):
        if (rows[i] >> m) & 1:
            sol |= 1<<col
    return sol, rank

start=time.time()
allidx=list(range(256))
for it in range(1,10000):
    sel = random.sample(allidx, m)
    sol, rank = solve_basis(sel)
    if sol is None:
        continue
    wt=sol.bit_count()
    if wt <= 16 and wt % 2 == 0:
        subset = [sel[j] for j in range(m) if (sol>>j)&1]
        print('found iter', it, 'weight', wt, 'subset', subset, 'time', time.time()-start)
        # decrypt using subset xor
        ks = bytearray(len(ct))
        for k in subset:
            st=streams[k]
            for i,b in enumerate(st): ks[i]^=b
        pt = bytes(c^k for c,k in zip(ct, ks))
        print(pt)
        print('valid?', re.fullmatch(rb'Congratulations! hkcert21\{\w{35}\}', pt) is not None)
        break
    if it%50==0:
        print('iter', it, 'rank', rank, 'wt', wt, 'elapsed', time.time()-start)
else:
    print('not found')
