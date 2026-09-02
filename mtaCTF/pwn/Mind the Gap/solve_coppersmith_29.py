import gmpy2
from Crypto.Util.number import long_to_bytes
from sympy import Symbol, expand, Poly
from fpylll import IntegerMatrix, LLL
import time

n = 12673253690434816535258555577578255117165368364890899668719870237759065934336300522248725336616279512507728372053937708483888713312010147733089600475550227843638848732302942611742875377642480746336467471144993526093694994911237045247079209745847819619536059442919083802452845650273011355314124070961551294721817433726140797328330990352638701425794124206601808399272847857983966532916617389441899516161279137475435163550016065385292226784918264018318042118885809789293357468368478770310884459630699838625860039142077429058776459183266200446323703309079460630733248986054158790820678807005406841696541302203583106685841
ct = 6001179588356074976458039473570288595953787029686543260841538443558433217468093201149147858909856398761346977979599245085768427398884369229320470578462927260632744243995883680986604991454952430552188527436874128607223850084010060034642728037497950114005012347763459127940638827470147144359618065326097613169668749591229425664053560520536527723251215691831977976395246584419356251893715412567611160347733573353875065182775867669478939166265452610842238589932436865494901889491251727764675035215816537236678767407974182868301182750126166271556588936698966107977505862740534386457494569633293660040189905756105650350005
leak = 33924829295369435346374850680783339765280262286856571264970865051963968704066339019412362804103800653164941108968374217279018462961216973813743173538356631790095
e = 65537

q0 = leak << 490
X = 1 << 490

# Let m = 14, t = 14 -> dim = 29
m = 14
t = 14
dim = m + 1 + t

print(f"Building lattice of dimension {dim}...")
start_t = time.time()
x = Symbol('x')
polys = []
for u in range(m + 1):
    poly = expand(((x + q0) ** u) * (n ** (m - u)))
    polys.append(poly)

for v in range(1, t + 1):
    poly = expand((x ** v) * ((x + q0) ** m))
    polys.append(poly)

M = IntegerMatrix(dim, dim)
for i in range(dim):
    p = polys[i]
    for j in range(dim):
        coeff = int(p.coeff(x, j)) if hasattr(p, 'coeff') else 0
        M[i, j] = coeff * (X ** j)

print(f"Matrix built in {time.time() - start_t:.2f}s. Running LLL reduction...")
start_lll = time.time()
L = LLL.reduction(M)
print(f"LLL completed in {time.time() - start_lll:.2f}s!")

for row_idx in range(dim):
    p_expr = sum((L[row_idx, j] // (X ** j)) * (x ** j) for j in range(dim))
    p_poly = Poly(p_expr, x)
    if p_poly.is_zero or p_poly.degree() == 0:
        continue
    # Let's find roots
    try:
        roots = p_poly.nroots(n=80)
    except:
        continue
    for r in roots:
        try:
            r_val = int(round(float(r.as_real_imag()[0])))
            for offset in range(-5, 6):
                cand_r = r_val + offset
                q_cand = q0 + cand_r
                if q_cand > 0 and n % q_cand == 0:
                    q = int(q_cand)
                    p = n // q
                    phi = (p - 1) * (q - 1)
                    d = int(gmpy2.invert(e, phi))
                    m_val = pow(ct, d, n)
                    flag = long_to_bytes(m_val)
                    print("\n" + "="*50)
                    print("[+] SUCCESS! FACTORED RSA MODULUS!")
                    print(f"p = {p}")
                    print(f"q = {q}")
                    print(f"FLAG = {flag.decode(errors='ignore')}")
                    print("="*50 + "\n")
                    exit(0)
        except Exception as ex:
            pass

print("No root found in checked rows.")
