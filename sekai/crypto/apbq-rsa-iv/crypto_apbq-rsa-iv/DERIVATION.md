apbq-rsa-iv - Number-Theory Derivation (Step 2/4)
1. Variables, constants, and known/unknown quantities

Let

B=4
312
=2
624
.

The generator samples two independent 1024-bit primes

2
1023
≤p,q<2
1024
,

and defines the RSA modulus

n=pq.

The public exponent is

e=0x10001=65537.

The flag bytes are converted to the nonnegative integer

m=bytes_to_long(FLAG),

and the public ciphertext is

c≡m
e
(modn),0≤c<n.

Thus the public RSA quantities are n,e,c. The secret RSA quantities are p,q,m. Once p,q are known, ordinary RSA recovery is possible whenever

gcd(e,(p-1)(q-1))=1,

by computing

d≡e
-1
(mod(p-1)(q-1))

(or modulo lcm(p-1,q-1)) and then

m≡c
d
(modn).

The generator does not explicitly test this gcd condition, so it should be verified rather than assumed after a factor is recovered.

For each i∈{0,1,2}, the generator independently samples

0≤a
i
	

,b
i
	

≤B

and publishes

h
i
	

=a
i
	

p+b
i
	

q.

Known from the embedded challenge instance:

n,c,h
0
	

,h
1
	

,h
2
	

,e.

Unknown:

p,q,m,a
0
	

,a
1
	

,a
2
	

,b
0
	

,b
1
	

,b
2
	

.

Because B=2
624
,

0≤a
i
	

b
i
	

≤B
2
=2
1248
.

Also

h
i
	

≤B(p+q)<2
1649
.

No modular reduction is applied when a hint is generated: every h
i
	

 is an exact integer linear combination of p and q.

2. Pairwise determinant variables

For every pair i,j, define

Δ
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

Then

Δ
ji
	

=-Δ
ij
	

,

and, since both products lie in [0,B
2
],

∣Δ
ij
	

∣≤B
2
=2
1248
.

These determinants eliminate one RSA prime at a time.

Starting from

h
i
	

=a
i
	

p+b
i
	

q,h
j
	

=a
j
	

p+b
j
	

q,

multiply by b
j
	

,b
i
	

 and subtract:

b
j
	

h
i
	

-b
i
	

h
j
	

=(a
i
	

b
j
	

-a
j
	

b
i
	

)p=Δ
ij
	

p.

Similarly,

a
i
	

h
j
	

-a
j
	

h
i
	

=(a
i
	

b
j
	

-a
j
	

b
i
	

)q=Δ
ij
	

q.

Therefore the exact identities are

b
j
	

h
i
	

-b
i
	

h
j
	

=Δ
ij
	

p
	


and

a
i
	

h
j
	

-a
j
	

h
i
	

=Δ
ij
	

q
	

.

Multiplying them gives

(b
j
	

h
i
	

-b
i
	

h
j
	

)(a
i
	

h
j
	

-a
j
	

h
i
	

)=Δ
ij
2
	

n
	

.

This identity involves only one determinant Δ
ij
	

, the public modulus n, the two public hints, and the four corresponding hidden coefficients.

3. Exact linear relation among the three determinants

The three coefficient vectors

(a
0
	

,b
0
	

),(a
1
	

,b
1
	

),(a
2
	

,b
2
	

)

lie in a two-dimensional space, so their 2×2 minors give an exact dependency.

With the sign convention above,

Δ
12
	

h
0
	

-Δ
02
	

h
1
	

+Δ
01
	

h
2
	

=0
	

.

Direct expansion verifies it:

	

(a
1
	

b
2
	

-a
2
	

b
1
	

)(a
0
	

p+b
0
	

q)
-(a
0
	

b
2
	

-a
2
	

b
0
	

)(a
1
	

p+b
1
	

q)
+(a
0
	

b
1
	

-a
1
	

b
0
	

)(a
2
	

p+b
2
	

q)=0,
	


because both the coefficient of p and the coefficient of q cancel identically.

Equivalently,

h
1
	

Δ
02
	

-h
2
	

Δ
01
	

=h
0
	

Δ
12
	

,

so

h
1
	

Δ
02
	

≡h
2
	

Δ
01
	

(modh
0
	

)
	

.

This reduces the three unknown determinants to a two-dimensional integer-lattice problem.

Define

x=Δ
01
	

,y=Δ
02
	

.

Then the true pair (x,y) satisfies

∣x∣,∣y∣≤2
1248

and

h
1
	

y-h
2
	

x≡0(modh
0
	

)
	

.

If gcd(h
1
	

,h
0
	

)=1, define

C≡h
2
	

h
1
-1
	

(modh
0
	

).

The condition is then

y≡Cx(modh
0
	

)
	

.

Thus (x,y) lies in the known rank-two lattice

Λ={(x,y)∈Z
2
:h
1
	

y-h
2
	

x≡0(modh
0
	

)}.

When gcd(h
1
	

,h
0
	

)=1, this lattice has determinant h
0
	

. A simple basis is obtainable from the congruence; a reduced basis should have vector lengths on the scale of

h
0
	

	

,

which for a roughly 1648-bit h
0
	

 is about 2
824
.

The true determinant coordinates are bounded near 2
1248
, so after reducing this two-dimensional lattice one expects a representation

(x,y)=uv
1
	

+vv
2
	


with v
1
	

,v
2
	

 reduced lattice basis vectors and coefficient magnitudes on the rough scale

2
1248-824
=2
424
.

This 2
424
-scale estimate is heuristic until the actual reduced basis is computed. It must be checked using the concrete instance rather than treated as an unconditional theorem.

4. Small-residue identity modulo a public hint

The most useful additional relation comes from reducing the product identity modulo one hint.

Use i=0,j=1:

(b
1
	

h
0
	

-b
0
	

h
1
	

)(a
0
	

h
1
	

-a
1
	

h
0
	

)=Δ
01
2
	

n.

Modulo h
0
	

,

b
1
	

h
0
	

-b
0
	

h
1
	

≡-b
0
	

h
1
	

(modh
0
	

),

and

a
0
	

h
1
	

-a
1
	

h
0
	

≡a
0
	

h
1
	

(modh
0
	

).

Therefore

Δ
01
2
	

n≡-a
0
	

b
0
	

h
1
2
	

(modh
0
	

).

If

gcd(h
1
	

,h
0
	

)=1,

then h
1
2
	

 is invertible modulo h
0
	

. Define the fully known constant

K
1
	

≡-n(h
1
2
	

)
-1
(modh
0
	

)
	

.

Then

K
1
	

Δ
01
2
	

≡a
0
	

b
0
	

(modh
0
	

)
	

.

Set

t
0
	

=a
0
	

b
0
	

.

Its exact bound is

0≤t
0
	

≤B
2
=2
1248
	

.

If the concrete public value satisfies

h
0
	

>B
2
,

then t
0
	

<h
0
	

, so the least nonnegative residue is not merely congruent to t
0
	

; it equals it:

(K
1
	

Δ
01
2
	

modh
0
	

)=t
0
	

	


and hence

0≤(K
1
	

Δ
01
2
	

modh
0
	

)≤2
1248
	

.

Since h
0
	

 is roughly 1648 bits while t
0
	

 is at most 1249 bits including the endpoint convention, the correct determinant produces a modular result with about 400 leading zero bits relative to the modulus size.

The same derivation with j=2 gives

K
2
	

≡-n(h
2
2
	

)
-1
(modh
0
	

)

and

(K
2
	

Δ
02
2
	

modh
0
	

)=a
0
	

b
0
	

	


under the same invertibility and size conditions.

Thus the correct pair satisfies

K
1
	

Δ
01
2
	

≡K
2
	

Δ
02
2
	

(modh
0
	

).

This equality is algebraically consistent with the earlier linear congruence. In fact, if

Δ
02
	

≡CΔ
01
	

(modh
0
	

),C≡h
2
	

h
1
-1
	

(modh
0
	

),

then

K
2
	

C
2
≡(-nh
2
-2
	

)(h
2
2
	

h
1
-2
	

)≡-nh
1
-2
	

≡K
1
	

(modh
0
	

).

Therefore the second quadratic congruence is not independent after the linear determinant congruence has been imposed. The genuinely useful extra information is that the common residue is unusually small:

a
0
	

b
0
	

≤2
1248
.
5. Reduced two-variable formulation

Let a reduced basis of Λ be

v
1
	

=(r
1
	

,s
1
	

),v
2
	

=(r
2
	

,s
2
	

).

Then every admissible determinant pair can be written exactly as

(
Δ
01
	

Δ
02
	

	

)=u(
r
1
	

s
1
	

	

)+v(
r
2
	

s
2
	

	

)

for integers u,v.

In particular,

Δ
01
	

=r
1
	

u+r
2
	

v.

Substituting this into the small-residue identity yields the concrete two-variable problem

0≤(K
1
	

(r
1
	

u+r
2
	

v)
2
modh
0
	

)≤2
1248
	

.

Equivalently, there exists an integer quotient z and a small nonnegative integer t
0
	

 such that

K
1
	

(r
1
	

u+r
2
	

v)
2
-zh
0
	

=t
0
	

	


with

0≤t
0
	

≤2
1248
.

After the actual lattice is reduced, the expected search bounds for u,v should be derived from the concrete basis geometry. The rough scale predicted from the bit sizes is approximately

∣u∣,∣v∣≲2
424
-2
425
,

but the next step must measure rather than assume this bound.

This formulation is substantially smaller than trying to recover all six coefficients

a
0
	

,a
1
	

,a
2
	

,b
0
	

,b
1
	

,b
2
	


simultaneously.

6. Why this is the smallest feasible computation to attempt next

The public instance can first be compressed to the two unknown determinant coordinates

(Δ
01
	

,Δ
02
	

)

using the exact relation

h
1
	

Δ
02
	

-h
2
	

Δ
01
	

≡0(modh
0
	

).

A two-dimensional lattice reduction is extremely small compared with a multivariate lattice over all original coefficients.

After reduction, only two small combination coefficients u,v remain, and the hidden RSA structure supplies an additional approximately 400-bit modular-smallness condition

(K
1
	

(r
1
	

u+r
2
	

v)
2
modh
0
	

)≤2
1248
.

Therefore the smallest reasonable next-stage computation is:

verify the required gcd and size assumptions on the concrete public instance;

construct and reduce the rank-two determinant lattice Λ;

express its reduced basis explicitly;

measure the resulting coefficient bounds for u,v;

attack only the resulting two-variable modular quadratic small-residue problem.

Direct brute force over u,v is not feasible if both are around 425 bits. The next step therefore needs a lattice/small-root or equivalent number-theoretic treatment of this reduced quadratic condition, not enumeration.

7. Recovery path after a valid determinant candidate

Step 2 stops before performing recovery, but a candidate must have an exact verification route.

Suppose a later step produces candidate values

Δ
01
	

,Δ
02
	

.

First recover

Δ
12
	

=
h
0
	

h
1
	

Δ
02
	

-h
2
	

Δ
01
	

	

.

This must be an integer and must satisfy

∣Δ
12
	

∣≤B
2
.

The determinant triple is

(Δ
12
	

,-Δ
02
	

,Δ
01
	

).

The original coefficient rows

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
	

)

both lie in the integer plane orthogonal to this determinant vector:

a⋅(Δ
12
	

,-Δ
02
	

,Δ
01
	

)=0,
b⋅(Δ
12
	

,-Δ
02
	

,Δ
01
	

)=0.

A correct later reconstruction must additionally satisfy

0≤a
i
	

,b
i
	

≤B

and

h
i
	

=a
i
	

p+b
i
	

q

for the same two primes p,q.

Even before reconstructing all coefficients, the candidate determinant must satisfy the exact small-residue value

t
0
	

=(K
1
	

Δ
01
2
	

modh
0
	

),0≤t
0
	

≤B
2
.

The identity

t
0
	

=a
0
	

b
0
	


then gives an additional consistency condition for coefficient reconstruction.

8. Concrete verification tests for Step 3

The next step should perform the following checks in order.

Test A - Parse and basic public-value sanity

Extract the embedded public values and verify:

n>0,0≤c<n,

there are exactly three hints, and each hint is positive.

Record the exact bit lengths of

n,c,h
0
	

,h
1
	

,h
2
	

.

Verify the expected scale:

n is 2047 or 2048 bits;

each h
i
	

 is at most 1649 bits.

Test B - Required inverses

Compute

gcd(h
0
	

,h
1
	

),gcd(h
0
	

,h
2
	

),gcd(h
1
	

,h
2
	

).

For the formulation above, verify specifically

gcd(h
0
	

,h
1
	

)=1

and preferably

gcd(h
0
	

,h
2
	

)=1.

If either gcd is nontrivial, test it against n immediately because an unexpected common divisor could yield an even simpler factorization route.

Test C - Small-residue bound is genuinely below the modulus

Verify

B
2
=2
1248
<h
0
	

.

This is necessary to convert

K
1
	

Δ
01
2
	

≡a
0
	

b
0
	

(modh
0
	

)

into the exact least-residue statement

(K
1
	

Δ
01
2
	

modh
0
	

)=a
0
	

b
0
	

.
Test D - Compute the known modular constants

Compute

C≡h
2
	

h
1
-1
	

(modh
0
	

),
K
1
	

≡-n(h
1
2
	

)
-1
(modh
0
	

),

and

K
2
	

≡-n(h
2
2
	

)
-1
(modh
0
	

).

Verify algebraically on the concrete integers that

K
2
	

C
2
≡K
1
	

(modh
0
	

).

Failure indicates a sign, inverse, or indexing mistake.

Test E - Construct the determinant lattice

Construct

Λ={(x,y)∈Z
2
:h
1
	

y-h
2
	

x≡0(modh
0
	

)}.

Verify every proposed basis vector (x,y) by checking

h
1
	

y-h
2
	

x≡0(modh
0
	

).

If gcd(h
1
	

,h
0
	

)=1, verify that the absolute determinant of the lattice basis is exactly

h
0
	

.
Test F - Reduce the two-dimensional lattice

Apply exact two-dimensional Gauss reduction or LLL.

For each reduced basis vector, verify again that it belongs to Λ.

Record:

both vector norms;

both coordinate bit lengths;

the exact determinant of the reduced basis.

The determinant must remain ±h
0
	

.

Test G - Derive realistic bounds for u,v

Using

∣Δ
01
	

∣,∣Δ
02
	

∣≤2
1248
,

and the actual reduced basis matrix, derive a rigorous enclosing box or at least a conservative proven bound for the combination coefficients u,v.

Do not simply assume the heuristic 2
425
 bound. Compute a bound using the inverse of the reduced basis matrix and the determinant-coordinate box.

Compare the proven bounds with the expected approximately 424--425-bit scale.

Test H - Verify the reduced quadratic formulation symbolically

Using the concrete reduced basis

v
1
	

=(r
1
	

,s
1
	

),v
2
	

=(r
2
	

,s
2
	

),

confirm that

Δ
01
	

=r
1
	

u+r
2
	

v

and that the target condition is exactly

0≤(K
1
	

(r
1
	

u+r
2
	

v)
2
modh
0
	

)≤2
1248
.

Also retain the equivalent integer equation

K
1
	

(r
1
	

u+r
2
	

v)
2
-zh
0
	

=t
0
	

,

where

0≤t
0
	

≤2
1248
.
Test I - Candidate validation rules for any Step-3 root

For every candidate (u,v), compute the corresponding

Δ
01
	

,Δ
02
	


and require:

∣Δ
01
	

∣,∣Δ
02
	

∣≤2
1248
,
(K
1
	

Δ
01
2
	

modh
0
	

)≤2
1248
,

and

h
0
	

∣h
1
	

Δ
02
	

-h
2
	

Δ
01
	

.

Then compute

Δ
12
	

=
h
0
	

h
1
	

Δ
02
	

-h
2
	

Δ
01
	

	


and require

∣Δ
12
	

∣≤2
1248
.

Only candidates passing all of these exact integer checks should proceed to coefficient or factor reconstruction.

Test J - Final factor consistency, once a factor candidate exists

Any candidate factor p or q must satisfy

1<p<n,p∣n,

with complementary factor

q=n/p

integral and prime.

Any reconstructed coefficients must then verify all three original equations exactly:

h
i
	

=a
i
	

p+b
i
	

q

with

0≤a
i
	

,b
i
	

≤2
624
.

Only after those identities hold should ciphertext decryption be attempted.

DERIVATION_COMPLETE
