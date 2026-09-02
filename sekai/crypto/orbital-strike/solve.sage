#!/usr/bin/env sage
from sage.all import *
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

orbit = [
    46157012221654917396851254347154820393060391878580715960476654689260395468184,
    36926194633341127588542680684095293820802193681748458943524916140809713523560,
    16005201943847263206512436577001283414470030273089746675203830598137794555134,
    28937919714389596084610407023450127584695575606301484773390370819366639643218,
    11459012353705334109041842799942754581703065868230253271729711591416155557180,
    31030059279554219046464541926833857543445131889728181065565033726460506326840,
    20987315604501021667042879662101693092441980938033961081037347214532349371248,
    76741461130245451493723909055453557280102065396647043801270629949855565452326,
    84258885183671683674472390974667571532577240974449641001706593550302243268268,
    59535034089467707172052245359810812420431903279354584714432674122159502991956,
    7115679899033391144975170596669540596311296590450661546000723388170577963715,
    35572951991838484594163260879328705523576344587262461128887804475450813563036,
    85569022704397114858282741078883377190544624744955636482627379979792474136036,
    5047270986830280372910174287287823507537624765267582560460157826800286170460,
]
star = bytes.fromhex(
    "1664ff83cbca2643b357bcdc8c3d6e1548615a18cec73e734a82e163b32a9b0c367c61bab01140a04ac8eda8b007d1d6"
)

def max_bits(row):
    return max(abs(ZZ(x)).nbits() for x in row)

def recover_short_syzygies(D):
    H = Matrix(ZZ, [D[:11], D[1:12], D[2:13]])
    rels = [list(r) for r in H.right_kernel_matrix().LLL().rows()]
    short = [r for r in rels if max_bits(r) <= 96]
    if len(short) < 2:
        raise RuntimeError("not enough short syzygies")
    return rels, short

def recover_inner_modulus_and_multiplier(short):
    R = PolynomialRing(ZZ, "T")
    T = R.gen()
    polys = [R(sum(ZZ(c) * T**i for i, c in enumerate(rel))) for rel in short]

    g = ZZ(0)
    for i in range(len(polys)):
        for j in range(i + 1, len(polys)):
            res = abs(ZZ(polys[i].resultant(polys[j])))
            if res:
                g = res if g == 0 else gcd(g, res)

    large_primes = [ZZ(q) for q, _ in factor(g) if ZZ(q).nbits() > 300 and is_prime(q)]
    if not large_primes:
        raise RuntimeError("resultant gcd did not expose the 311-bit prime")
    p = max(large_primes, key=lambda q: q.nbits())

    Rp = PolynomialRing(GF(p), "T")
    gp = Rp(polys[0])
    for poly in polys[1:]:
        gp = gcd(gp, Rp(poly))
    gp = gp.monic()
    if gp.degree() != 1:
        raise RuntimeError(f"expected a linear gcd over GF(p), got degree {gp.degree()}")
    a = ZZ(-gp[0])
    return p, a

def recover_inner_differences(D, short, p, a):
    rows = []
    for rel in short:
        row = [ZZ(0)] * 25
        for k, c in enumerate(rel):
            row[k + 1] = ZZ(c)
        rows.append(row)

        row = [ZZ(0)] * 25
        for k, c in enumerate(rel):
            row[k + 2] = ZZ(c)
        rows.append(row)

    for i in range(12):
        row = [ZZ(0)] * 25
        row[i + 1] = 1
        row[i] = -a
        row[13 + i] = -p
        rows.append(row)

    reduced = Matrix(ZZ, rows).right_kernel_matrix().LLL()
    for basis_row in reduced.rows():
        base = [ZZ(x) for x in basis_row[:13]]
        for sign in (1, -1):
            E = [sign * x for x in base]
            if not any(E) or not all(-p < x < p for x in E):
                continue
            if not all((E[i + 1] - a * E[i]) % p == 0 for i in range(12)):
                continue

            g = ZZ(0)
            for i in range(1, 13):
                for j in range(i + 1, 13):
                    val = (D[i] - E[i]) * D[j - 1] - (D[j] - E[j]) * D[i - 1]
                    if val:
                        g = abs(val) if g == 0 else gcd(g, abs(val))

            if g.nbits() == 256 and is_prime(g) and max(orbit) < g < 2**256:
                return E, g

    raise RuntimeError("could not identify the inner difference vector and outer modulus")

def recover_outer_multiplier(D, E, P):
    vals = []
    for i in range(1, 13):
        vals.append(((D[i] - E[i]) * inverse_mod(D[i - 1], P)) % P)
    if len(set(vals)) != 1:
        raise RuntimeError("outer multiplier candidates disagree")
    return ZZ(vals[0])

def decrypt_flag(p, a, P, A, E):
    x1, x2 = ZZ(orbit[0]), ZZ(orbit[1])
    y2_mod_p = (x2 - A * x1) % P
    e1_residue = (inverse_mod(a, p) * E[1]) % p

    for E1 in (ZZ(e1_residue), ZZ(e1_residue) - p):
        y1_mod_p = (y2_mod_p - E1) % P
        X = ((x1 - y1_mod_p) * inverse_mod(A, P)) % P
        try:
            flag = unpad(AES.new(int(X).to_bytes(32, "big"), AES.MODE_ECB).decrypt(star), 16)
        except ValueError:
            continue
        if (A * X + y1_mod_p) % P == x1:
            return X, flag

    raise RuntimeError("AES decryption failed for both E1 lifts")

def main():
    print("[*] Computing differences D...")
    D = [ZZ(orbit[i + 1]) - ZZ(orbit[i]) for i in range(len(orbit) - 1)]
    rels, short = recover_short_syzygies(D)
    print("[+] Using short syzygies:", [max_bits(r) for r in short])

    p, a = recover_inner_modulus_and_multiplier(short)
    print(f"[+] Recovered inner modulus p = {p}")
    print(f"[+] Recovered inner multiplier a = {a}")

    E, P = recover_inner_differences(D, short, p, a)
    A = recover_outer_multiplier(D, E, P)
    print(f"[+] Recovered outer modulus P = {P}")
    print(f"[+] Recovered outer multiplier A = {A}")

    X, flag = decrypt_flag(p, a, P, A, E)
    print(f"[+] Recovered AES key X = {X}")
    flag_str = flag.decode()
    print(f"\n[+] FLAG: {flag_str}\n")
    with open("flag.txt", "w") as f:
        f.write(flag_str)

if __name__ == "__main__":
    main()
