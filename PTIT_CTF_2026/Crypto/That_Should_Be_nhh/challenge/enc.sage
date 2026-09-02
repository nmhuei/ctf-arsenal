from Crypto.Cipher import AES
from hashlib import sha256
from os import urandom

flag = open("flag.txt", "rb").read()
NBIT, PBIT, SBIT, DBIT, FBIT = 1024, 512, 80, 96, 32

def smooth(bits):
    x = ZZ(1)
    while x.nbits() < bits - FBIT:
        x *= random_prime(2^FBIT - 1, lbound=2^(FBIT - 1))
    return x * 2^(bits - x.nbits())

def small(bits, odd=False):
    return 2 * ZZ.random_element(-2^(bits - 1), 2^(bits - 1)) + odd

def prime_near_smooth():
    while True:
        A = smooth(PBIT)
        for _ in range(20000):
            s, p = small(SBIT, True), 0
            p = A + s
            if p.nbits() == PBIT and is_prime(p):
                return Integer(p), Integer(A), Integer(s)

while True:
    p, A, s = prime_near_smooth()
    q = random_prime(2^PBIT - 1, lbound=2^(PBIT - 1))
    r = small(SBIT)
    if p == q or q <= abs(r):
        continue

    N, K = p * q, A * (q - r)
    u = random_prime(2^DBIT - 1, lbound=2^(DBIT - 1))
    v = random_prime(2^(DBIT - 8) - 1, lbound=2^(DBIT - 9))
    e = (K * v + u // 2) // u
    w = e * u - K * v

    if 1 < e < N and abs(w) < 2^DBIT and gcd(e, (p - 1) * (q - 1)) == 1:
        break

iv = urandom(16)
pad = 16 - len(flag) % 16
ct = AES.new(sha256(str(p).encode()).digest(), AES.MODE_CBC, iv).encrypt(flag + bytes([pad]) * pad)
m = Integer((iv + ct).hex(), 16)
assert m < N and e*u - (p - s)*(q - r)*v == w

print("n =", N)
print("e =", e)
print("c =", power_mod(m, e, N))


# n = 142217133950331383280849240147704444479347756839197748359496621059788089766910006904838605206502343346784621083909830941944628842677247904138991949650529500950063288595336962598606848151740001164215358829068316743899886573916423795874723508083910684350048423004067616316245233835164152303866893899098404075307
# e = 735562091150242199086137919579103601129940065511032380153512599537270426450426263582268920053003161544983227567832252495021917091489748774366094722437238758924451476396513769768400726278723557098141590858309774096405563453563592561074531837480565567125040985794075273534996592428835861192841524496633102653
# c = 137457406660129767400819964307866522985441842464715884517889980293434382803283064686956906367455039759668586682637407035813231325408151214355647002146143963348554367638105785351285114550546508429635975747755892192290014158317026703192846835308010477939727103064715916819117898597698267398988054857699040341517