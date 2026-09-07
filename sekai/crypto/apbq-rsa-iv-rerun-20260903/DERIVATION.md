Symbolic Number-Theory Derivation Plan
Scope

This step uses only the information present in INVENTORY.md and the original local apbq-rsa-iv.py.

The goal of this step is only to derive the mathematical structure needed for a later local recovery procedure. No factorization, plaintext recovery, flag recovery, executable solver, or final numerical answer is performed here.

1. Known values and constants

From the source, the public instance supplies:

RSA modulus:

n=pq

RSA ciphertext:

c≡m
e
(modn)

public exponent:

e=0x10001=65537

three integer hints:

h
0
	

, h
1
	

, h
2
	


The hidden prime factors satisfy:

p,q are 1024-bit primes

Each hint has the source-level form

h
i
	

=a
i
	

p+b
i
	

q,i∈{0,1,2},

where

0≤a
i
	

,b
i
	

≤B,B=4
312
=2
624
.

The plaintext integer is

m=bytes_to_long(FLAG),

and the source computes

c≡m
65537
(modn).

Known quantities for the symbolic attack are therefore

n, c, e, h
0
	

, h
1
	

, h
2
	

, B.

Unknown quantities are

p, q, m,

and the six hint coefficients

a
0
	

,b
0
	

,a
1
	

,b
1
	

,a
2
	

,b
2
	

.
2. Determinants of the hidden coefficient pairs

For each pair of hint rows define the signed determinant

d
ij
	

=a
i
	

b
j
	

-a
j
	

b
i
	

.

Because every coefficient lies in [0,B],

∣d
ij
	

∣≤B
2
=2
1248
.

Define the determinant vector

d=(d
12
	

,-d
02
	

,d
01
	

).

Also define

a=(a
0
	

,a
1
	

,a
2
	

),b=(b
0
	

,b
1
	

,b
2
	

),h=(h
0
	

,h
1
	

,h
2
	

).

Then

d=a×b.

Since

h=pa+qb,

the cross product is orthogonal to both a and b, hence

d⋅h=0
	

.

Written explicitly,

d
12
	

h
0
	

-d
02
	

h
1
	

+d
01
	

h
2
	

=0
	

.

This is an exact integer equality, not a congruence.

3. Integer relation lattice of the public hints

Define the rank-two integer lattice

L={x=(x
0
	

,x
1
	

,x
2
	

)∈Z
3
:x
0
	

h
0
	

+x
1
	

h
1
	

+x
2
	

h
2
	

=0}.

The determinant vector d lies in this lattice.

Let

g=gcd(h
0
	

,h
1
	

,h
2
	

).

A full integer basis

r,s

of L may be obtained locally from the known hints and then reduced in dimension two.

For a primitive full basis, orientation can be chosen so that

r×s=±
g
h
	

.

The hidden determinant vector therefore has unique integer coordinates

d=λr+μs
	


for some unknown integers λ,μ.

This converts three roughly 1248-bit determinant components into two much smaller lattice coordinates.

4. Exact coordinate bounds for λ,μ

Write

r=(r
0
	

,r
1
	

,r
2
	

),s=(s
0
	

,s
1
	

,s
2
	

).

Choose any two coordinate positions j,k for which

δ
jk
	

=r
j
	

s
k
	

-r
k
	

s
j
	


=0.

From

d
j
	

=λr
j
	

+μs
j
	

,d
k
	

=λr
k
	

+μs
k
	

,

Cramer's rule gives the exact formulas

λ=
δ
jk
	

d
j
	

s
k
	

-d
k
	

s
j
	

	

,
μ=
δ
jk
	

r
j
	

d
k
	

-r
k
	

d
j
	

	

.

Using

∣d
j
	

∣,∣d
k
	

∣≤B
2
,

one obtains the rigorous bounds

∣λ∣≤B
2
∣δ
jk
	

∣
∣s
j
	

∣+∣s
k
	

∣
	

,
∣μ∣≤B
2
∣δ
jk
	

∣
∣r
j
	

∣+∣r
k
	

∣
	

.

A reduced rank-two basis is expected to have entries around the square root of the hint scale. Since the hints are approximately 1024+624≈1648 bits, reduced basis components are expected around 824 bits, while a nonzero minor is on the scale of a hint component.

Consequently the expected coordinate scale is approximately

∣λ∣,∣μ∣≈2
1248+824-1648
=2
424
.

The exact numerical bound is to be computed later from the actual reduced basis, rather than assumed.

5. Quadratic lifting variables

Define

u=λ
2
,v=λμ,w=μ
2
.

Then

u≥0,w≥0

and the exact rank-one relation is

uw=v
2
	

.

If

∣λ∣,∣μ∣≤M,

then

0≤u,w≤M
2
,∣v∣≤M
2
.

With the expected M near 2
424
, these variables are expected to be approximately at most

2
848

up to a small safety margin determined from the concrete basis.

This is substantially smaller than the approximately 1648-bit hint moduli.

6. Expressing every hidden determinant as a linear form in λ,μ

From

d=λr+μs,

the three signed determinants are

d
12
	

=λr
0
	

+μs
0
	

,
d
02
	

=-(λr
1
	

+μs
1
	

),
d
01
	

=λr
2
	

+μs
2
	

.

For every pair i

=j, the square of the relevant determinant has the form

d
ij
2
	

=α
ij
	

u+β
ij
	

v+γ
ij
	

w,

where the coefficients

α
ij
	

,β
ij
	

,γ
ij
	


are completely known after the public relation basis is fixed.

If

d
ij
	

=R
ij
	

λ+S
ij
	

μ,

then explicitly

d
ij
2
	

=R
ij
2
	

u+2R
ij
	

S
ij
	

v+S
ij
2
	

w.

Thus all determinant squares become known linear forms in the three lifted unknowns u,v,w.

7. Pairwise determinant identity

For every ordered pair i

=j,

a
i
	

h
j
	

-a
j
	

h
i
	

=d
ij
	

q,

because

a
i
	

(a
j
	

p+b
j
	

q)-a
j
	

(a
i
	

p+b
i
	

q)=(a
i
	

b
j
	

-a
j
	

b
i
	

)q.

Likewise,

b
j
	

h
i
	

-b
i
	

h
j
	

=d
ij
	

p.

Multiplying the two exact equalities gives

(a
i
	

h
j
	

-a
j
	

h
i
	

)(b
j
	

h
i
	

-b
i
	

h
j
	

)=nd
ij
2
	

.

Reducing this equality modulo h
i
	

 leaves

(a
i
	

h
j
	

)(-b
i
	

h
j
	

)≡nd
ij
2
	

(modh
i
	

).

Therefore

nd
ij
2
	

+a
i
	

b
i
	

h
j
2
	

≡0(modh
i
	

)
	

.

Define

A
i
	

=a
i
	

b
i
	

.

Since

0≤A
i
	

≤B
2
=2
1248
,

the congruence becomes

nd
ij
2
	

+A
i
	

h
j
2
	

≡0(modh
i
	

)
	

.

This identity is central because A
i
	

 is much smaller than h
i
	

.

8. Six modular small-residue equations

If

gcd(h
i
	

,h
j
	

)=1,

then h
j
2
	

 is invertible modulo h
i
	

, so

A
i
	

≡-nd
ij
2
	

(h
j
2
	

)
-1
(modh
i
	

)
	

.

Substituting the lifted determinant square gives

A
i
	

≡L
ij
	

(u,v,w)(modh
i
	

),

where

L
ij
	

(u,v,w)=-n(h
j
2
	

)
-1
(α
ij
	

u+β
ij
	

v+γ
ij
	

w)(modh
i
	

).

There are six ordered pairs

(i,j)∈{(0,1),(0,2),(1,0),(1,2),(2,0),(2,1)}.

Hence there are six known modular linear forms in u,v,w.

Their residues are not arbitrary: they are exactly

A
0
	

,A
0
	

,A
1
	

,A
1
	

,A
2
	

,A
2
	

,

respectively, and each satisfies

0≤A
i
	

≤B
2
.

Thus every one of the six approximately 1648-bit modular equations has a residue bounded by only about 1248 bits.

Equivalently, for suitable integers k
ij
	

,

L
ij
int
	

(u,v,w)-k
ij
	

h
i
	

=A
i
	

,

where L
ij
int
	

 denotes any fixed integer representative of the known linear form.

The difference between the two equations belonging to the same i also yields the exact zero-residue congruence

L
ij
	

(u,v,w)-L
ik
	

(u,v,w)≡0(modh
i
	

)
	

.

Those three equal-residue congruences are useful consistency constraints, but by themselves they are homogeneous and do not fix the overall scale. The small-residue bounds on the individual L
ij
	

 values provide the required scale information.

If a pairwise hint gcd is not one, inversion is not performed; the non-inverted identity

nd
ij
2
	

+A
i
	

h
j
2
	

≡0(modh
i
	

)

remains exact and can be handled after first checking whether the gcd itself already exposes a simpler degeneracy.

9. Low-dimensional lattice formulation for u,v,w

The six equations define a simultaneous modular small-residue problem with only three principal unknowns.

For each of the six ordered pairs, write

F
ℓ
	

(u,v,w)=f
ℓ,1
	

u+f
ℓ,2
	

v+f
ℓ,3
	

w(modH
ℓ
	

),

where

H
ℓ
	


is the corresponding hint modulus h
i
	

.

The true solution satisfies

F
ℓ
	

(u,v,w)=R
ℓ
	

(modH
ℓ
	

),

with

∣u∣,∣v∣,∣w∣≤U

for a concrete bound U=M
2
, and

0≤R
ℓ
	

≤R,R=B
2
.

A standard fixed-dimensional modular lattice can encode vectors of the shape

(u,v,w,R
1
	

,…,R
6
	

)

together with arbitrary multiples of the six moduli.

Conceptually, the lattice is generated by:

three directions corresponding to changing u,v,w, with the six modular linear forms appended;

six directions corresponding to independently adding one full modulus H
ℓ
	

 to a residue coordinate.

This gives a fixed rank/dimension near nine before any optional embedding coordinate.

The coordinates should be weighted so that the expected bounds

U≈2
848

and

R=2
1248

have comparable geometric influence.

Any rational scaling can be converted into an equivalent integral scaling by multiplying through by common factors.

A reduction/enumeration stage can then seek nonzero short vectors consistent with the bounds.

Every candidate must subsequently satisfy the exact nonlinear filter

uw=v
2
	

.

This rank-one relation is strong and should discard generic short lattice vectors.

The expected computational difficulty is modest because:

the public integer-relation lattice has rank only two;

the lifted modular problem has only three principal unknowns;

the simultaneous modular embedding remains fixed and low-dimensional;

the true u,v,w are expected around 800--850 bits while the moduli are around 1648 bits;

there are six modular constraints plus the exact equation uw=v
2
.

Therefore the intended local work is expected to be dominated by big-integer arithmetic, rank-two lattice reduction, and low-dimensional LLL/BKZ plus short-vector enumeration rather than an exponential search over the original six 624-bit coefficients.

No claim of a worst-case polynomial-time factorization algorithm is being made; the feasibility relies on the special bounded-hint structure and the concrete low dimension.

10. Reversing the lifting

Once a candidate u,v,w is found, first require

uw=v
2
.

Because

u=λ
2
,w=μ
2
,

valid candidates should permit integer square roots

∣λ∣=
u
	

,∣μ∣=
w
	

.

The sign combination is determined by

v=λμ,

up to the simultaneous global sign flip

(λ,μ)↦(-λ,-μ).

That global sign changes

d↦-d

but leaves every determinant square unchanged, so it does not affect the later recovery of A
i
	

.

Reconstruct

d=λr+μs

and verify

d⋅h=0

exactly together with

∣d
01
	

∣,∣d
02
	

∣,∣d
12
	

∣≤B
2
.
11. Exact recovery of A
i
	

=a
i
	

b
i
	


For each i, choose either j

=i and compute the residue

A
i
	

=(-nd
ij
2
	

(h
j
2
	

)
-1
)modh
i
	

.

Because the true value obeys

0≤A
i
	

≤B
2

and normally

B
2
<h
i
	

,

the correct modular residue is the exact ordinary integer A
i
	

, not merely a congruence class.

The second available j for the same i must produce the identical integer.

Thus each candidate has a strong check:

A
i
(j)
	

=A
i
(k)
	


with

0≤A
i
	

≤B
2
.

No factoring of A
i
	

 is required.

12. Exact reversible relationship from A
i
	

 to the RSA factors

This is the key reversible identity.

Starting from

h
i
	

=a
i
	

p+b
i
	

q

and

A
i
	

=a
i
	

b
i
	

,n=pq,

compute

h
i
2
	

-4A
i
	

n.

Expanding gives

(a
i
	

p+b
i
	

q)
2
-4a
i
	

b
i
	

pq
=a
i
2
	

p
2
-2a
i
	

b
i
	

pq+b
i
2
	

q
2
=(a
i
	

p-b
i
	

q)
2
.

Therefore

Δ
i
	

=h
i
2
	

-4A
i
	

n=(a
i
	

p-b
i
	

q)
2
	

.

For a correct candidate, Δ
i
	

 must be a nonnegative perfect square.

Let

S
i
	

=
Δ
i
	

	

=∣a
i
	

p-b
i
	

q∣.

Then the two combinations

h
i
	

+S
i
	

,h
i
	

-S
i
	


are, in some order,

2a
i
	

p

and

2b
i
	

q.

Hence a nontrivial RSA factor is recoverable by gcd:

gcd(n,h
i
	

+S
i
	

)
	


or

gcd(n,h
i
	

-S
i
	

)
	

.

The other factor is then exactly

n/p

or

n/q.

This is an exact algebraic reversal. It does not require factoring the potentially large composite integer A
i
	

=a
i
	

b
i
	

.

13. Degenerate cases

The source permits zero coefficients, so local checks must account for them.

13.1 A
i
	

=0

If

A
i
	

=a
i
	

b
i
	

=0,

then at least one coefficient is zero and

h
i
	


is a pure multiple of one RSA prime.

In a nonzero hint this normally makes

gcd(n,h
i
	

)

immediately nontrivial.

Therefore gcd checks should occur before any lattice work.

13.2 Zero hint

If

a
i
	

=b
i
	

=0,

then

h
i
	

=0.

Such an instance should be treated separately rather than using modular inverses.

13.3 Pairwise hint gcds

If

gcd(h
i
	

,h
j
	

)

=1,

do not blindly invert h
j
2
	

modh
i
	

.

First inspect whether the gcd provides a direct factor or other simplification. Otherwise retain the non-inverted determinant congruence.

13.4 Nonprimitive public hint vector

If

g=gcd(h
0
	

,h
1
	

,h
2
	

)>1,

construct the exact relation lattice relative to the primitive vector

h/g.

The identity

d⋅h=0

is unchanged.

14. Local consistency checks before factor recovery

The later implementation should perform the following checks strictly locally.

Public-instance checks

Verify:

n>0,h
i
	

≥0.

Record bit lengths of

n,c,h
0
	

,h
1
	

,h
2
	

.

Check

gcd(n,h
i
	

)

for each hint before doing harder work.

Check pairwise

gcd(h
i
	

,h
j
	

).
Relation-lattice checks

For the chosen basis r,s, verify exactly

r⋅h=0,s⋅h=0.

Verify that the basis spans the full integer kernel, for example by checking

r×s=±
g
h
	

.

Use actual nonzero minors to compute a concrete rigorous bound on ∣λ∣ and ∣μ∣.

Lifted-candidate checks

Require

u

=0 or v

=0 or w

=0.

Require

uw=v
2
.

Require u,w to be perfect squares if explicitly reconstructing λ,μ.

Require the recovered signs to satisfy

v=λμ.

Reconstruct d and verify:

d⋅h=0,
∣d
ij
	

∣≤B
2
.
A
i
	

 checks

For every usable i, derive A
i
	

 independently from both other hints and require equality.

Require

0≤A
i
	

≤B
2
.

Then require

Δ
i
	

=h
i
2
	

-4A
i
	

n

to be nonnegative and a perfect square.

Factor checks

Any proposed factors must satisfy

1<p<n,1<q<n,
pq=n.

Their sizes should agree with the source's 1024-bit prime generation.

A local primality check may be used as an additional confirmation.

15. Recovering the original hint coefficients after factoring

Once p,q are known, the original coefficients can be recovered uniquely because

B=2
624
<p,q.

From

h
i
	

=a
i
	

p+b
i
	

q,

reduce modulo q:

h
i
	

≡a
i
	

p(modq).

Therefore

a
i
	

≡h
i
	

p
-1
(modq).

Since

0≤a
i
	

<B<q,

the least nonnegative residue is the exact a
i
	

.

Similarly,

b
i
	

≡h
i
	

q
-1
(modp),

and because

0≤b
i
	

<B<p,

the least nonnegative residue is the exact b
i
	

.

These recovered coefficients provide a final generator-level consistency check:

h
i
	

=a
i
	

p+b
i
	

q

for all three hints, with every coefficient inside the source bound.

They also verify

A
i
	

=a
i
	

b
i
	


and

d
ij
	

=a
i
	

b
j
	

-a
j
	

b
i
	

.
16. RSA decryption only after all identities pass

Only after the factorization has been independently verified should the ciphertext be touched.

Compute

φ(n)=(p-1)(q-1).

Check

gcd(e,φ(n))=1.

Then define the private exponent

d
RSA
	

≡e
-1
(modφ(n)).

Recover the plaintext integer

m≡c
d
RSA
	

(modn).

Convert m back to its big-endian byte representation compatible with bytes_to_long.

The final ciphertext consistency check is

m
e
modn=c.

No plaintext or final answer is computed during this derivation step.

17. Expected end-to-end structure for the next step

The intended local recovery sequence is therefore:

Parse only the embedded local public instance.

Perform gcd and size sanity checks.

Build the exact rank-two integer kernel of (h
0
	

,h
1
	

,h
2
	

).

Reduce that basis.

Express

d=λr+μs.

Derive rigorous concrete bounds on λ,μ.

Lift to

u=λ
2
,v=λμ,w=μ
2
.

Build the six modular small-residue linear constraints in u,v,w.

Use a fixed-dimensional lattice reduction/enumeration strategy to obtain candidate lifted triples.

Filter candidates using

uw=v
2
.

Recover determinant squares and the exact small values

A
i
	

=a
i
	

b
i
	

.

Require

h
i
2
	

-4A
i
	

n

to be a perfect square.

Use the resulting square root and gcd with n to recover p,q.

Reconstruct all six original hint coefficients and verify every hint exactly.

Only then perform ordinary RSA private-key recovery and ciphertext verification.

The decisive reversible relation is

h
i
2
	

-4(a
i
	

b
i
	

)n=(a
i
	

p-b
i
	

q)
2
	

,

while the determinant identities and the rank-two relation lattice provide a route to recover the small product a
i
	

b
i
	

 without searching over the original coefficients.

DERIVATION_COMPLETE
