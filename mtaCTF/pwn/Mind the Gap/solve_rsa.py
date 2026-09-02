import gmpy2
from Crypto.Util.number import long_to_bytes
from sympy import Symbol, expand, Poly

n = 12673253690434816535258555577578255117165368364890899668719870237759065934336300522248725336616279512507728372053937708483888713312010147733089600475550227843638848732302942611742875377642480746336467471144993526093694994911237045247079209745847819619536059442919083802452845650273011355314124070961551294721817433726140797328330990352638701425794124206601808399272847857983966532916617389441899516161279137475435163550016065385292226784918264018318042118885809789293357468368478770310884459630699838625860039142077429058776459183266200446323703309079460630733248986054158790820678807005406841696541302203583106685841
ct = 6001179588356074976458039473570288595953787029686543260841538443558433217468093201149147858909856398761346977979599245085768427398884369229320470578462927260632744243995883680986604991454952430552188527436874128607223850084010060034642728037497950114005012347763459127940638827470147144359618065326097613169668749591229425664053560520536527723251215691831977976395246584419356251893715412567611160347733573353875065182775867669478939166265452610842238589932436865494901889491251727764675035215816537236678767407974182868301182750126166271556588936698966107977505862740534386457494569633293660040189905756105650350005
leak = 33924829295369435346374850680783339765280262286856571264970865051963968704066339019412362804103800653164941108968374217279018462961216973813743173538356631790095
e = 65537

q0 = leak << 490
X = 1 << 490

from decimal import Decimal, getcontext
getcontext().prec = 200

def dot(v1, v2):
    return sum(x * y for x, y in zip(v1, v2))

def lll(B, delta=0.75):
    n = len(B)
    d = len(B[0])
    B = [[Decimal(x) for x in row] for row in B]
    B_star = [[Decimal(0)] * d for _ in range(n)]
    mu = [[Decimal(0)] * n for _ in range(n)]
    
    def gram_schmidt():
        for i in range(n):
            B_star[i] = list(B[i])
            for j in range(i):
                mu[i][j] = dot(B[i], B_star[j]) / dot(B_star[j], B_star[j])
                B_star[i] = [b_ik - mu[i][j] * b_jk for b_ik, b_jk in zip(B_star[i], B_star[j])]
                
    gram_schmidt()
    k = 1
    while k < n:
        for j in range(k - 1, -1, -1):
            if abs(mu[k][j]) > Decimal('0.5'):
                q = Decimal(int(round(mu[k][j])))
                B[k] = [b_k - q * b_j for b_k, b_j in zip(B[k], B[j])]
                gram_schmidt()
        
        c1 = dot(B_star[k], B_star[k])
        c2 = (Decimal(delta) - mu[k][k-1]**2) * dot(B_star[k-1], B_star[k-1])
        if c1 >= c2:
            k += 1
        else:
            B[k], B[k-1] = B[k-1], B[k]
            gram_schmidt()
            k = max(k - 1, 1)
            
    return [[int(round(x)) for x in row] for row in B]

m = 3
polys = []
x = Symbol('x')
for u in range(m + 1):
    poly = expand(((x + q0) ** u) * (n ** (m - u)))
    coeffs = [int(poly.coeff(x, i)) for i in range(m + 1)]
    polys.append(coeffs)

dim = m + 1
matrix = []
for i in range(dim):
    row = [polys[i][j] * (X ** j) for j in range(dim)]
    matrix.append(row)

print("Running LLL...")
red_matrix = lll(matrix)
print("LLL finished!")

reduced_poly = 0
for j in range(dim):
    coeff = red_matrix[0][j] // (X ** j)
    reduced_poly += coeff * (x ** j)

p_poly = Poly(reduced_poly, x)
print("Poly degree:", p_poly.degree())

# Newton-Raphson or bisection for root in [0, X]
# f(x) and f'(x)
f = p_poly
f_prime = p_poly.diff(x)

def eval_f(val):
    return int(f.eval(val))

def eval_df(val):
    return int(f_prime.eval(val))

# Bisection search in [0, X]
low = 0
high = X
f_low = eval_f(low)
f_high = eval_f(high)

print(f"f(0) sign: {f_low > 0}, f(X) sign: {f_high > 0}")

if f_low * f_high <= 0:
    while high - low > 1:
        mid = (low + high) // 2
        f_mid = eval_f(mid)
        if f_mid == 0:
            low = mid
            break
        if (f_low > 0 and f_mid > 0) or (f_low < 0 and f_mid < 0):
            low = mid
            f_low = f_mid
        else:
            high = mid
            f_high = f_mid
    roots = [low, high]
else:
    # Use Newton-Raphson with multiple starting points
    roots = []
    for guess in [0, X // 4, X // 2, 3 * X // 4, X]:
        curr = guess
        for _ in range(100):
            df_val = eval_df(curr)
            if df_val == 0:
                break
            f_val = eval_f(curr)
            curr = curr - f_val // df_val
        roots.append(curr)

print("Candidate roots:", roots)

for r_val in roots:
    for offset in range(-10, 11):
        cand_r = r_val + offset
        q_cand = q0 + cand_r
        if q_cand > 0 and n % q_cand == 0:
            q = int(q_cand)
            p = n // q
            print(f"\n[+] Found factors!\np = {p}\nq = {q}")
            phi = (p - 1) * (q - 1)
            d = int(gmpy2.invert(e, phi))
            m_val = pow(ct, d, n)
            flag = long_to_bytes(m_val)
            print("\n" + "="*50)
            print("         RSA FLAG RESULT: ", flag.decode(errors='ignore'))
            print("="*50)
            exit(0)
