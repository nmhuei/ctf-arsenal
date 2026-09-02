Here's an isogeny challenge which many of you may have already solved before. An isomorphism between elliptic curves is an isogeny of degree one, and a common isomorphism one might compute is mapping from one curve model to another.
  
  
In this challenge, you are given a curve in short Weierstrass form:

E

:


y

2

=


x

3

+

a

x

+

b

E : y^2 = x^3 + ax + b





E



:






y









2



=






x









3



+





a

x



+





b
and the goal is to find the Montgomery model of the curve:

E

M

:


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

E\_M : y^2 = x^3 + Ax^2 + x






E









M

​




:






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
. The flag is the Montgomery coefficient A.
  
  








E

:


y

2

=


x

3

+

312589632

x

+

654443578






m

o

d

1912812599

E : y^2 = x^3 + 312589632 x + 654443578 \mod 1912812599





E



:






y









2



=






x









3



+





312589632

x



+





654443578







mod





1912812599
  
  


Hint: a point of order two on a Montgomery curve is

(

0

:

0

:

1

)

(0 : 0 : 1)





(

0



:





0



:





1

)
, to find an isomorphism from a curve to Montgomery form, look at the transformation you need to send a point of order two to this so-called "Montgomery point".
