While working with elliptic curve cryptography, we will need to add points together. In the background challenges, we did this geometrically by finding a line that passed through two points, finding the third intersection and then reflecting along the

y

y





y
-axis.
  
  
It turns out that there is an efficient algorithm for calculating the point addition law for an elliptic curve.
  
  
Taken from "An Introduction to Mathematical Cryptography",
*Jeffrey Hoffstein, Jill Pipher, Joseph H. Silverman*
, the following algorithm will calculate the addition of two points on an elliptic curve
  
  

**Algorithm for the addition of two points:

P

+

Q

P + Q





P



+





Q**
  
  
(a) If

P

=

O

P = O





P



=





O
, then

P

+

Q

=

Q

P + Q = Q





P



+





Q



=





Q
.
  
(b) Otherwise, if

Q

=

O

Q = O





Q



=





O
, then

P

+

Q

=

P

P + Q = P





P



+





Q



=





P
.
  
(c) Otherwise, write

P

=

(


x

1

,


y

1

)

P = (x\_{1}, y\_{1})





P



=





(


x










1

​


,




y










1

​


)
and

Q

=

(


x

2

,


y

2

)

Q = (x\_{2}, y\_{2})





Q



=





(


x










2

​


,




y










2

​


)
.
  
(d) If

x

1

=


x

2

x\_{1} = x\_{2}






x










1

​




=






x










2

​

and

y

1

=

−


y

2

y\_{1} = −y\_{2}






y










1

​




=





−


y










2

​

, then

P

+

Q

=

O

P + Q = O





P



+





Q



=





O
.
  
(e) Otherwise:
  
(e1) if

P

≠

Q

P \neq Q





P















=





Q
:

λ

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

\lambda = (y\_{2} - y\_{1}) / (x\_{2} - x\_{1})





λ



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
  
(e2) if

P

=

Q

P = Q





P



=





Q
:

λ

=

(

3


x

1

2

+

a

)

/

2


y

1

\lambda = (3x\_{1}^2 + a) / 2y\_{1}





λ



=





(

3


x










1





2

​




+





a

)

/2


y










1

​

  
(f)

x

3

=


λ

2

−


x

1

−


x

2

x\_{3} = λ^2 − x\_{1} − x\_{2}






x










3

​




=






λ









2



−






x










1

​




−






x










2

​

  
(h)

y

3

=

λ

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

y\_{3} = λ(x\_{1} −x\_{3}) − y\_{1}






y










3

​




=





λ

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

  
(i)

P

+

Q

=

(


x

3

,


y

3

)

P + Q = (x\_{3}, y\_{3})





P



+





Q



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
  
  
  


We are working with a finite field, so the above calculations should be done modulo

p

p





p
, and we do not "divide" by an integer, we instead multiply by the modular inverse of a number. e.g.

5


−

1

≡

9






m

o

d

11

5^{-1} \equiv 9 \mod 11






5










−

1



≡





9







mod





11
.
  
  
We will work with the following elliptic curve, and prime:
  
  








E

:


Y

2

=


X

3

+

497

X

+

1768






m

o

d

9739

E: Y^{2} = X^{3} + 497 X + 1768 \mod 9739





E



:






Y










2



=






X










3



+





497

X



+





1768







mod





9739
  
  


You can test your algorithm by asserting:

X

+

Y

=

(

1024

,

4440

)

X + Y = (1024, 4440)





X



+





Y



=





(

1024

,



4440

)
and

X

+

X

=

(

7284

,

2107

)

X + X = (7284, 2107)





X



+





X



=





(

7284

,



2107

)
for

X

=

(

5274

,

2841

)

X = (5274, 2841)





X



=





(

5274

,



2841

)
and

Y

=

(

8669

,

740

)

Y = (8669, 740)





Y



=





(

8669

,



740

)
.
  
  
Using the above curve, and the points

P

=

(

493

,

5564

)

,

Q

=

(

1539

,

4742

)

,

R

=

(

4403

,

5202

)

P = (493, 5564), Q = (1539, 4742), R = (4403,5202)





P



=





(

493

,



5564

)

,



Q



=





(

1539

,



4742

)

,



R



=





(

4403

,



5202

)
, find the point

S

(

x

,

y

)

=

P

+

P

+

Q

+

R

S(x,y) = P + P + Q + R





S

(

x

,



y

)



=





P



+





P



+





Q



+





R
by implementing the above algorithm.
  
  


After calculating

S

S





S
, substitute the coordinates into the curve. Assert that the point

S

S





S
is in

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
