This category is filled with insecure implementations of elliptic curve cryptography. Picking bad curves leads to broken protocols and fun puzzles, but private keys can be extracted from devices even when the curves picked are safe!
  
  
One technique to learn private information is through side channel analysis. At a high level, a system performing operations with a secret can leak information about the secret through data such as the time taken, or work done by the circuit.
  
  
Timing attacks against ECDSA signing can leak information about the nonce, which together with sophisticated attacks like
[LadderLeak](https://eprint.iacr.org/2020/615.pdf)
can be lethal for the protocol. To protect against this, a lot of work has been done to make scalar multiplication of points on an elliptic curve to run in constant time.
  
  
A key component of constant time algorithms for scalar multiplication for points on elliptic curves are based on Montgomery's Ladder. In this challenge, the aim is to implement the most basic version of this: Montgomery’s binary algorithm in the group

E

(


F

p

)

E(\Fp)





E

(


F










p

​


)
.
  
  

**Montgomery’s binary algorithm in the group**







E

(


F

p

)

E(\Fp)





E

(


F










p

​


)
  
  
Input:

P

∈

E

(


F

p

)

P \in E(\Fp)





P



∈





E

(


F










p

​


)
and an n-bit integer

k

=

∑


2

i


k

i

k = \sum 2^i k\_i





k



=





∑




2









i


k









i

​

where

k


n

−

1

=

1

k\_{n-1} = 1






k










n

−

1

​




=





1
  
Output:

[

k

]

P

∈

E

(


F

p

)

[k]P \in E(\Fp)





[

k

]

P



∈





E

(


F










p

​


)
  
  
1. Set

(


R

0

,


R

1

)

(R\_0, R\_1)





(


R









0

​


,




R









1

​


)
to

(

P

,

[

2

]

P

)

(P, [2]P)





(

P

,



[

2

]

P

)
  
2. for i = n - 2 down to 0 do
  
3.   If

k

i

=

0

k\_i = 0






k









i

​




=





0
then
  
4.      Set

(


R

0

,


R

1

)

(R\_0, R\_1)





(


R









0

​


,




R









1

​


)
to

(

[

2

]


R

0

,


R

0

+


R

1

)

([2]R\_0, R\_0 + R\_1)





([

2

]


R









0

​


,




R









0

​




+






R









1

​


)
  
5.   Else:
  
6.      Set

(


R

0

,


R

1

)

(R\_0, R\_1)





(


R









0

​


,




R









1

​


)
to

(


R

0

+


R

1

,

[

2

]


R

1

)

(R\_0 + R\_1, [2]R\_1)





(


R









0

​




+






R









1

​


,



[

2

]


R









1

​


)
  
7. Return

R

0

R\_0






R









0

​

  
  
  


At a high level, notice that regardless of the bit of k, we perform both a doubling and an addition operation for each step. Compare this to the double and add algorithm we gave in the starter challenges. There are a couple obvious problems within here still: the number of steps taken leaks the bit length of k and there's an if statement, which could leak data on the bit structure of k due to branching. For the interested learner, we recommend improving your algorithm to match Alg. 8 in this resource:
[Montgomery curves and their arithmetic](https://eprint.iacr.org/2017/212.pdf)
.
  
  
We will work with the following elliptic curve:
  
  








E

:


Y

2

=


X

3

+

486662


X

2

+

X






m

o

d


2

255

−

19

E: Y^{2} = X^{3} + 486662 X^{2} + X \mod 2^{255} - 19





E



:






Y










2



=






X










3



+





486662


X










2



+





X







mod






2










255



−





19
  
  
Using the above curve, and the generator point with
`G.x = 9`
, find the

x

x





x
-coordinate (decimal representation) of point
`Q = [0x1337c0decafe] G`
by implementing the above algorithm.
  
  
This curve is in Montgomery form, rather than Weierstrass like many of the curves in these challenges. Although this curve can be mapped to Weierstrass form and old doubling and addition formula can be reused, we recommend working directly with the formula for Montgomery curves:

E

:

B


y

2

=


x

3

+

A


x

2

+

x

E : By^{2} = x^{3} + Ax^{2} + x





E



:





B


y










2



=






x










3



+





A


x










2



+





x
. To encourage this, we give the addition and doubling formulas for the curve in affine coordinates. Please see
[Montgomery curves and the Montgomery ladder](https://eprint.iacr.org/2017/293.pdf)
for a beautiful and fast set of formula in projective coordinates.
  
  

**Addition formula for Montgomery Curve (Affine)**
  
  
Input:

P

,

Q

∈

E

(


F

p

)

P, Q \in E(\Fp)





P

,



Q



∈





E

(


F










p

​


)
with

P

≠

Q

P \neq Q





P















=





Q
  
Output:

R

=

(

P

+

Q

)

∈

E

(


F

p

)

R = (P + Q) \in E(\Fp)





R



=





(

P



+





Q

)



∈





E

(


F










p

​


)
  
  







(


x

1

,


y

1

)

,

(


x

2

,


y

2

)

=

P

,

Q

(x\_1, y\_1), (x\_2, y\_2) = P, Q





(


x









1

​


,




y









1

​


)

,



(


x









2

​


,




y









2

​


)



=





P

,



Q
  







α

=

(


y

2

−


y

1

)

/

(


x

2

−


x

1

)

\alpha = (y\_{2} - y\_{1}) / (x\_{2} - x\_{1} )





α



=





(


y










2

​




−






y










1

​


)

/

(


x










2

​




−






x










1

​


)
  








x

3

=

B


α

2

−

A

−


x

1

−


x

2

x\_{3} = B \alpha^{2} - A - x\_{1} - x\_{2}






x










3

​




=





B


α










2



−





A



−






x










1

​




−






x










2

​

  








y

3

=

α

(


x

1

−


x

3

)

−


y

1

y\_{3} = \alpha (x\_{1} - x\_{3}) - y\_{1}






y










3

​




=





α

(


x










1

​




−






x










3

​


)



−






y










1

​








R

=

(


x

3

,


y

3

)

R = (x\_{3}, y\_{3})





R



=





(


x










3

​


,




y










3

​


)
  
  

**Doubling formula for Montgomery Curve (Affine)**
  
  
Input:

P

∈

E

(


F

p

)

P \in E(\Fp)





P



∈





E

(


F










p

​


)
  
Output:

R

=

[

2

]

P

∈

E

(


F

p

)

R = [2]P \in E(\Fp)





R



=





[

2

]

P



∈





E

(


F










p

​


)
  
  







(


x

1

,


y

1

)

=

P

(x\_1, y\_1) = P





(


x









1

​


,




y









1

​


)



=





P
  







α

=

(

3


x

1

2

+

2

A


x

1

+

1

)

/

(

2

B


y

1

)

\alpha = (3x^{2}\_{1} + 2Ax\_{1} + 1) / (2By\_{1})





α



=





(

3


x










1






2

​




+





2

A


x










1

​




+





1

)

/

(

2

B


y










1

​


)
  








x

3

=

B


α

2

−

A

−

2


x

1

x\_{3} = B\alpha^{2} - A - 2x\_{1}






x










3

​




=





B


α










2



−





A



−





2


x










1

​

  








y

3

=

α

(


x

1

−


x

3

)

−


y

1

y\_{3} = \alpha(x\_{1} - x\_{3}) - y\_{1}






y










3

​




=





α

(


x










1

​




−






x










3

​


)



−






y










1

​








R

=

(


x

3

,


y

3

)

R = (x\_{3}, y\_{3})





R



=





(


x










3

​


,




y










3

​


)
  
  
Note that all operations are performed modulo

p

p





p
.
  
  


For a general overview of Montgomery's ladder, we recommend:
[Montgomery curves and the Montgomery ladder](https://eprint.iacr.org/2017/293.pdf)
. For a clean algorithm to implement, we recommend Alg. 4
`LADDER`
in
[Montgomery curves and their arithmetic](https://eprint.iacr.org/2017/212.pdf)
together with Alg. 1
`xADD`
and Alg. 2
`xDBL`
.
