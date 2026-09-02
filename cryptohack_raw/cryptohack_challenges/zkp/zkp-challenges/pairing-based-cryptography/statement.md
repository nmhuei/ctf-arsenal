Pairing-based cryptography refers to a branch of cryptography that focuses on constructions utilizing bilinear pairings or couplings. A pairing is a non-degenerate bilinear map (explained in Definition).
  
  
Employing these tools allows for the development of cryptographic schemes that are not feasible with just a single group satisfying cryptographic properties, such as the Decisional Diffie-Hellman (DDH) assumption.
  
  
**Recap:**
  
  
The DDH assumption relates to the following problem: Let values

p

p





p
,

q

q





q
,

r

r





r
from

Z

\mathbb{Z}





Z
Let values

G

G





G
,

P

P





P
,

Q

Q





Q
,

R

R





R
from an (additive) abelian group, where

P

=

[

p

]

G

P = [p]G





P



=





[

p

]

G
,

Q

=

[

q

]

G

Q = [q]G





Q



=





[

q

]

G
,

R

=

[

r

]

G

R = [r]G





R



=





[

r

]

G
, the pairing function allows us to verify

p

⋅

q

=

r

p \cdot q = r





p



⋅





q



=





r
by checking if

pairing

(

P

,

Q

)

=

R

\text{pairing}(P, Q) = R






pairing

(

P

,



Q

)



=





R
.
  
  


Sometimes this definition is given with some multiplication group, and so

P

=


G

p

P = G^p





P



=






G









p
would be written instead. However, for all practical pairing based protocols the underlying groups are elliptic curves and so in this section we use additive notation for the groups of which we pair elements.
  
  
**Definition**
  
  
A pairing is a function

e

:


G

1

×


G

2

→


G

T

e: G\_1 \times G\_2 \to G\_T





e



:






G









1

​




×






G









2

​




→






G









T

​

, which is bilinear, meaning it satisfies:
  
  

* For any integers

  (

  a

  ,

  b

  )

  (a, b)





  (

  a

  ,



  b

  )
  and any group elements

  (

  g

  ,

  h

  )

  (g, h)





  (

  g

  ,



  h

  )
  the equation

  e

  (

  [

  a

  ]

  g

  ,

  [

  b

  ]

  h

  )

  =

  e

  (

  g

  ,

  h


  )


  a

  b

  e([a]g, [b]h) = e(g, h)^{ab}





  e

  ([

  a

  ]

  g

  ,



  [

  b

  ]

  h

  )



  =





  e

  (

  g

  ,



  h


  )










  ab
  .
* The pairing must not be degenerate, meaning

  e

  (

  g

  ,

  h

  )

  =

  0

  e(g, h) = 0





  e

  (

  g

  ,



  h

  )



  =





  0
  if and only if

  g

  =

  0

  g = 0





  g



  =





  0
  or

  h

  =

  0

  h = 0





  h



  =





  0
  . Note:

  0

  0





  0
  here means the identity element.
* For cryptographic usage, it's crucial that the pairing function

  e

  e





  e
  can be computed in polynomial time.

  
  
**Categories of Pairings**
  
  
Pairings are mainly categorized into two families: symmetric, when the two source groups are the same (

G

1

=


G

2

G\_1 = G\_2






G









1

​




=






G









2

​

), and asymmetric when they differ.
  
  
Cryptographers further distinguish between strong and weak asymmetric pairings. Strong asymmetric pairings are those where establishing a homomorphism between

G

1

G\_1






G









1

​

and

G

2

G\_2






G









2

​

is difficult, and weak if otherwise. This classification is summarized into three types:
  
  

* **Type 1**
  : Symmetric pairings, where

  G

  1

  =


  G

  2

  G\_1 = G\_2






  G









  1

  ​




  =






  G









  2

  ​

  .
* **Type 2**
  : Weak asymmetric pairings, when there exists a computable polynomial-time homomorphism

  ϕ

  :


  G

  2

  →


  G

  1

  \phi: G\_2 \to G\_1





  ϕ



  :






  G









  2

  ​




  →






  G









  1

  ​

  .
* **Type 3**
  : Strong asymmetric pairings, where no such homomorphism between

  G

  1

  G\_1






  G









  1

  ​

  and

  G

  2

  G\_2






  G









  2

  ​

  is known.

  
  
**Example of Applications in ZKP**
  
  
The Boneh–Lynn–Shacham (BLS) digital signature is a cryptographic protocol enabling the verification of a signer's authenticity. This scheme employs bilinear pairing for the verification process, with signatures represented as elements of an elliptic curve group.
  
  
**Key Generation**
  
  
The process starts by choosing a random integer

x

x





x
within the range

0

<

x

<

r

0 < x < r





0



<





x



<





r
(

r

r





r
the order of the generator point). This integer

x

x





x
serves as the private key. The corresponding public key is published as

[

x

]

g

[x]g





[

x

]

g
, derived by multiplying a generator

g

g





g
of the elliptic curve by

x

x





x
.
  
  
**Signing**
  
  
To sign a message

m

m





m
, the signer hashes the message bitstring

m

m





m
to a hash

h

=

H

(

m

)

h = H(m)





h



=





H

(

m

)
. The signature

S

S





S
is then generated as

S

=

[

x

]

h

S = [x]h





S



=





[

x

]

h
, effectively signing the hash with the private key

x

x





x
.
  
  
**Verification**
  
  
To verify a signature

S

S





S
against a public key

[

x

]

g

[x]g





[

x

]

g
, one checks if the bilinear pairing of the signature and the generator

g

g





g
,

e

(

S

,

g

)

e(S, g)





e

(

S

,



g

)
, matches the pairing of the message hash and the public key,

e

(

H

(

m

)

,

[

x

]

g

)

e(H(m), [x]g)





e

(

H

(

m

)

,



[

x

]

g

)
. Successful verification indicates that the signature is authentic and was created using the corresponding private key.
  
  
This warmup challenge uses the Python module
`py_ecc`
, which utilizes an implementation of an optimized pairing algorithm.
  
  







x

x





x
,

y

y





y
are random, and the goal is to verify that

z

=

x

⋅

y

z = x \cdot y





z



=





x



⋅





y
.
  
  
Snippet for generating

[

x

]

G

[x]G





[

x

]

G
,

[

y

]

G

[y]G





[

y

]

G
,

[

z

]

G

[z]G





[

z

]

G
:
  
  

from py\_ecc.optimized\_bn128 import G\_1, G\_2, multiply, pairing
  
  
...
  
xG = multiply(G\_1, x)
  
yG = multiply(G\_2, y)
  
zG = pairing(yG, xG)
  
...
  
  
  
Each line in
`output.txt`
will represent a bit of the flag depending on whether the proof is correctly verified or not (1 if the proof is validated, 0 otherwise).
  
  
**Challenge files:**
  
-
[generate.py](/static/challenges/generate_c8c4cc90fd7a3febddb72b6ce176fdac.py)
  
-
[output.txt](/static/challenges/output_2d8920fd1c945fde7ff1ad5fc0810aa7.txt)
  
  
  
Challenge contributed by
[Ectario](/user/Ectario)
