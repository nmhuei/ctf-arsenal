Micro-step 3C1

Scope: fixed-dimensional integer constraint construction only, using local INSTANCE.json, lattice_relations.py, and the relevant formulas in DERIVATION.md.

Created:

lifted_constraints.py

Implemented pure functions for:

u = lambda^2

v = lambda*mu

w = mu^2

exact rank-one check u*w == v*v

concrete lifted-coordinate bound checks

small-residue checks 0 <= residue <= B^2

determinant linear forms d_ij = R_ij*lambda + S_ij*mu

lifted determinant squares
d_ij^2 = R_ij^2*u + 2*R_ij*S_ij*v + S_ij^2*w

all six ordered-pair modular residue expressions
L_ij(u,v,w) = -n*(h_j^2)^(-1)*d_ij^2 (mod h_i)

construction and evaluation of the six fixed-dimensional modular rows.

Synthetic tests:

used small primes and three small coefficient pairs with pairwise-coprime hints

reconstructed the determinant vector in the public integer-relation basis

verified the lifting identity u*w == v*v

verified all six modular residues equal the exact synthetic A_i = a_i*b_i

verified small-residue bounds

verified ordered-pair determinant sign reversal and square consistency.

Supplied public-value tests:

loaded only n and hints from INSTANCE.json

constructed the reduced public relation basis through lattice_relations.py

constructed exactly six modular rows in ordered-pair order

checked canonical residue coefficients lie in their corresponding moduli

computed concrete public bounds:

lambda bound bit length: 425

mu bound bit length: 424

u bound bit length: 849

|v| bound bit length: 849

w bound bit length: 848

small-residue bound B^2 bit length: 1249

exercised rank-one and small-residue check functions on public-value structures.

Verification command:

python3 lifted_constraints.py

Observed result:

PASS synthetic: lift/rank-one identity
PASS synthetic: six modular residues equal exact A_i values
PASS synthetic: small-residue bounds
PASS synthetic: ordered-pair determinant sign/square consistency
PASS public: six fixed-dimensional modular rows constructed
PASS public: canonical residue coefficients and moduli
PASS public: concrete lifted bounds {'lambda_bits': 425, 'mu_bits': 424, 'u_bits': 849, 'abs_v_bits': 849, 'w_bits': 848, 'residue_bound_bits': 1249}
PASS public: rank-one/small-residue check functions exercised
ALL_TESTS_PASS

No plaintext, RSA factors, final answer, lattice enumeration, network access, or external lookup was used.

STEP3C1_COMPLETE
