#!/usr/bin/env python3
import json, random, socket, sys
from hashlib import sha256

# Parameters copied from hamiltonicity.py
P = 0x19dad539e2d348cc3ab07d51f2bb6491d1552aa8cf1db928920fd3d86946aed8805d2e279fa8632dd5fbab8aaf7df1069906b057cc785b7f191ef1b9b5da38cff2e7c64da17bb56a058707d9fd69e546a95e502e556a314c587c7ae36c3d1122e6954f5d81dd9239e02f61b045360187b4caeed271cec1919a0d8a39e855040cf
q = 0xced6a9cf169a4661d583ea8f95db248e8aa9554678edc944907e9ec34a3576c402e9713cfd43196eafdd5c557bef8834c83582be63c2dbf8c8f78dcdaed1c67f973e326d0bddab502c383ecfeb4f2a354af28172ab518a62c3e3d71b61e8891734aa7aec0eec91cf017b0d8229b00c3da65776938e760c8cd06c51cf42a82067
h1 = 250335104192448110684442096964171969189371208477846978499544515755228857598805930673171509152681305793789903169450438090936970626429806187630240086681623358732517929314870247393468568111513100989768455673769015138136779312483203922847547169463972757664497001482465636402329003817055202840451714256443734563502
h2 = 50837518481371967588098771977165879422445597094015682347125264774697010574110399136037637691883034517374621248070926110725252171239208140392324019115211573768989274797050961703999139947885402838647962534519882622024973824201026885393782961783980351898031905383197219266093119145616328556294476943229578292306
comm_params = (P, q, h1, h2)

N = 5
numrounds = 128
G = [
    [0,0,1,0,0],
    [1,0,0,0,0],
    [0,1,0,0,0],
    [0,0,0,0,1],
    [0,0,0,1,0],
]

# This is a Hamiltonian cycle in the *fake* committed graph used when challenge bit = 1.
cycle = [(0,1), (1,3), (3,2), (2,4), (4,0)]
cycle_pos = {u * N + v: (u, v) for u, v in cycle}
sorted_cycle_positions = sorted(cycle_pos)


def pedersen_commit_with_r(message, r):
    return (pow(h1, message, P) * pow(h2, r, P)) % P


def pedersen_commit(message):
    r = random.randrange(q)
    return pedersen_commit_with_r(message, r), r


def pedersen_open(commitment, message, r):
    return (commitment * pow(h1, -message, P) * pow(h2, -r, P)) % P == 1


def hash_committed_graph(A, state):
    fs_state = sha256(str(comm_params).encode())
    fs_state.update(state)
    first_message = "".join(str(x) for row in A for x in row)
    fs_state.update(first_message.encode())
    return fs_state.digest()


def flat_to_mat(xs):
    return [xs[i*N:(i+1)*N] for i in range(N)]


def suffix_representative(residue_mod_p, suffix_int):
    """Return X == residue_mod_p mod P and decimal str(X) ends in str(suffix_int)."""
    suffix = str(suffix_int)
    mod10 = 10 ** len(suffix)
    t = ((suffix_int - residue_mod_p) * pow(P, -1, mod10)) % mod10
    x = residue_mod_p + P * t
    assert x % P == residue_mod_p
    assert str(x).endswith(suffix)
    return x


def make_ambiguous_pair():
    """
    Build two matrices with identical vulnerable hash serialization:
      A0: all integers, opens to the real non-Hamiltonian G => valid if challenge=0
      A1: cycle entries are integers opening to 1; other entries are strings => valid if challenge=1
    """
    A0_flat = [None] * (N*N)
    openings0_flat = [None] * (N*N)

    # Fake cycle commitments for the challenge-1 opening.
    fake = {}
    for edge in cycle:
        c, r = pedersen_commit(1)
        fake[edge] = (c, r)

    # For five chosen A0 entries, choose a different representative modulo P whose
    # decimal expansion ends with the corresponding fake challenge-1 commitment.
    # This creates a second valid parsing of the same concatenated decimal string.
    # Use early positions so fake strings occur in the correct row-major order.
    embed_positions = list(range(len(sorted_cycle_positions)))
    for embed_i, fake_pos in zip(embed_positions, sorted_cycle_positions):
        edge = cycle_pos[fake_pos]
        suffix_c, _ = fake[edge]
        m = G[embed_i // N][embed_i % N]
        r0 = random.randrange(q)
        residue0 = pedersen_commit_with_r(m, r0)
        A0_flat[embed_i] = suffix_representative(residue0, suffix_c)
        openings0_flat[embed_i] = [m, r0]
        assert pedersen_open(A0_flat[embed_i], m, r0)

    # Other challenge-0 entries are normal representatives.
    for idx in range(N*N):
        if A0_flat[idx] is not None:
            continue
        m = G[idx // N][idx % N]
        c, r = pedersen_commit(m)
        A0_flat[idx] = c
        openings0_flat[idx] = [m, r]

    S = "".join(str(x) for x in A0_flat)

    # Split the same string into A1 fields. Cycle positions are the fake commitments;
    # gaps are arbitrary strings because bit=1 verification never opens them.
    A1_flat = [""] * (N*N)
    cursor = 0
    for fake_pos in sorted_cycle_positions:
        edge = cycle_pos[fake_pos]
        t = str(fake[edge][0])
        at = S.find(t, cursor)
        assert at >= cursor, "embedded fake commitment not found in order"
        gap = S[cursor:at]
        # Put the gap into the field immediately before the cycle position; all other
        # unused fields stay as empty strings and contribute nothing to the hash string.
        assert fake_pos > 0 and A1_flat[fake_pos - 1] == ""
        A1_flat[fake_pos - 1] = gap
        A1_flat[fake_pos] = int(t)
        cursor = at + len(t)
    A1_flat[-1] += S[cursor:]

    A0 = flat_to_mat(A0_flat)
    A1 = flat_to_mat(A1_flat)
    openings0 = flat_to_mat(openings0_flat)

    assert "".join(str(x) for row in A0 for x in row) == "".join(str(x) for row in A1 for x in row)

    z0 = [list(range(N)), openings0]
    # Openings must be in the same order as `cycle`, not row-major order.
    z1 = [[list(e) for e in cycle], [fake[e][1] for e in cycle]]
    return (A0, z0), (A1, z1)


def make_proofs():
    pairs = [make_ambiguous_pair() for _ in range(numrounds)]

    state = b""
    for (A0, _), _ in pairs:
        state = hash_committed_graph(A0, state)
    bits = bin(int.from_bytes(state, "big"))[-numrounds:]
    # In the astronomically unlikely event of leading-zero truncation, pad like the
    # server effectively should have done. This almost never changes anything.
    bits = bits.rjust(numrounds, "0")

    proofs = []
    for bit, pair in zip(bits, pairs):
        (A0, z0), (A1, z1) = pair
        if bit == "0":
            proofs.append({"A": A0, "z": z0})
        else:
            proofs.append({"A": A1, "z": z1})
    return bits, proofs


def local_verify(proofs):
    # Equivalent to chal.py verification, but self-contained.
    state = b""
    for pr in proofs:
        state = hash_committed_graph(pr["A"], state)
    bits = bin(int.from_bytes(state, "big"))[-numrounds:].rjust(numrounds, "0")
    for i, (bit, pr) in enumerate(zip(bits, proofs)):
        A, z = pr["A"], pr["z"]
        if bit == "0":
            perm, openings = z
            # Identity permutation only in this exploit.
            for r in range(N):
                for c in range(N):
                    m, rr = openings[r][c]
                    assert pedersen_open(A[r][c], m, rr), (i, r, c)
                    assert m == G[r][c], (i, r, c, m, G[r][c])
        else:
            cyc, rs = z
            froms = [e[0] for e in cyc]
            tos = [e[1] for e in cyc]
            for v in range(N):
                assert v in froms and v in tos, (i, v)
                assert cyc[v][1] == cyc[(v+1) % N][0], (i, cyc)
            for (src, dst), rr in zip(cyc, rs):
                assert pedersen_open(A[src][dst], 1, rr), (i, src, dst)
    return bits


def recv_until(sock, marker):
    data = b""
    while marker not in data:
        chunk = sock.recv(4096)
        if not chunk:
            break
        data += chunk
    return data


def solve_remote(host, port):
    bits, proofs = make_proofs()
    print("challenge bits:", bits)
    s = socket.create_connection((host, int(port)))
    print(recv_until(s, b"send fiat shamir proof: ").decode(errors="replace"), end="")
    for i, pr in enumerate(proofs):
        s.sendall(json.dumps(pr, separators=(",", ":")).encode() + b"\n")
        if i != len(proofs) - 1:
            recv_until(s, b"send fiat shamir proof: ")
    # Print the verifier output and flag.
    out = b""
    while True:
        chunk = s.recv(4096)
        if not chunk:
            break
        out += chunk
    print(out.decode(errors="replace"))


if __name__ == "__main__":
    bits, proofs = make_proofs()
    print("local verifying...")
    print("bits:", local_verify(proofs))
    print("local ok")
    if len(sys.argv) == 3:
        solve_remote(sys.argv[1], sys.argv[2])
