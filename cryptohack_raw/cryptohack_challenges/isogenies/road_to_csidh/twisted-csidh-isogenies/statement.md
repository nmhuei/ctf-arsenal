In the challenge "CSIDH prime power isogenies" we explored the

ℓ

\ell





ℓ
-isogeny graphs for the curves we use in CSIDH and saw that they were cyclic. We were able to compute how many vertices there were in the graph and effectively walk all the way around until we reached the starting node again.
  
  
We also know that given some point of order

ℓ

\ell





ℓ
on the curve, there seems to be only one way to walk from each node and that this graph is directed. This challenge is about how we can effectively (and efficiently) take one step "backwards" on the graph. This means if the

ℓ

\ell





ℓ
-isogeny graph has k nodes, instead of computing k-1

ℓ

\ell





ℓ
-isogenies to go backwards we can compute just a single isogeny in the other direction.
  
  
To do this, we will need to be able to compute the quadratic twist

E

t

E^{t}






E










t
of a curve. Look at this curve in Montgomery form. Notice that it is not isomorphic to

E

E





E
. Compute their j-invariants. Compute their order, are they isogenous?
  
  
To walk backwards on the graph we temporarily work on the quadratic twist. Practically, to walk one step backwards we map

E

→


E

t

E \to E^t





E



→






E









t
. From this twisted curve, we compute as normal an isogeny of degree

ℓ

\ell





ℓ
using a point of order

ℓ

\ell





ℓ
on the twisted curve. Then, we untwist the codomain (by computing a second quadratic twist) to finish the computation.
  
  
To test your code, use the solution of "CSIDH prime power isogenies" and compare the result of taking

k

−

1

k-1





k



−





1
"forward" 7-isogenies and a single "backwards" isogeny.
  
  


Note: if you are computing x-only isogenies you do not need to explicitly compute the twist, but instead compute random

x

x





x
-coordinates in

F

p

\Fp






F










p

​

. A point is on

E

E





E
when

x

3

+

A


x

2

+

x

x^{3} + Ax^{2} + x






x










3



+





A


x










2



+





x
is a square and

E

t

E^t






E









t
when it is not. From this, we see that checking the squareness of

y

2

y^{2}






y










2
is enough to determine if you will take a step forwards or backwards when this

x

x





x
-only point is used to compute an isogeny.
  
  
To compute the flag, walk one step "backwards" on the three-isogeny graph from the below curve. The flag is the Montgomery coefficient of this curve.
  
  









E

0

:


y

2

=


x

3

+

x






m

o

d

419

E\_0 : y^{2} = x^{3} + x \mod 419






E









0

​




:






y










2



=






x










3



+





x







mod





419
  
  


In the CSIDH exponent vector, when an integer is positive we take

e

e





e
steps from the curve on the

ℓ

\ell





ℓ
-isogeny graph. When the integer is negative, we take

e

e





e
steps from the
quadratic twist
of the curve on the

ℓ

\ell





ℓ
-isogeny graph.
  
  
**Resources:**
  
-
[The quadratic twist of an elliptic curve, Section 7.6, Andrew Sutherland](https://ocw.mit.edu/courses/18-783-elliptic-curves-spring-2021/5e4e3bd15c9a81db2ac186628da095bf_MIT18_783S21_notes7.pdf)
  
-
[Isogenies: The basics, some applications, and nothing much in between, Lorenz Panny](https://yx7.cc/docs/isog/isog_icetalk_slides.pdf)
