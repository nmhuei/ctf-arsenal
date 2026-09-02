In the background section, we covered the basics of how we can view point addition over an elliptic curve as being an abelian group operation. In this geometric picture we allowed the coordinates on the curve to be any real number.
  
  
To apply elliptic curves in a cryptographic setting, we study elliptic curves which have coordinates in a finite field

F

p

\Fp






F










p

​

.
  
  
We will still be considering elliptic curves of the form

E

:


Y

2

=


X

3

+

a

X

+

b

E: Y^{2} = X^{3} + a X + b





E



:






Y










2



=






X










3



+





a

X



+





b
, which satisfy the following conditions:

a

,

b

∈


F

p

a,b \in \Fp





a

,



b



∈






F










p

​

and

4


a

3

+

27


b

2

≠

0

4a^{3} + 27 b^{2} \neq 0





4


a










3



+





27


b










2















=





0
. However, we no longer think of the elliptic curve as a geometric object, but rather a set of points defined by
  
  








E

(


F

p

)

=

{

(

x

,

y

)

:

x

,

y

∈


F

p

satisfying


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

}

∪

O

E(\Fp) = \{(x,y) : x,y \in \Fp \textrm{ satisfying } y^{2} = x^{3} + a x + b \} \cup O





E

(


F










p

​


)



=





{(

x

,



y

)



:





x

,



y



∈






F










p

​



satisfying


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

}



∪





O
  
  


Note: Everything we covered in the background still holds. The identity of the group is the point at infinity:

O

O





O
, and the addition law is unchanged. Given two points in

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
, the addition law will generate another point in

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
  
  
For all the challenges in the starter set, we will be working with the elliptic curve
  
  








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
  
  
Using the above curve, and the point

P

(

8045

,

6936

)

P(8045,6936)





P

(

8045

,



6936

)
, find the point

Q

(

x

,

y

)

Q(x,y)





Q

(

x

,



y

)
such that

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
  
  


Remember, we're working in a finite field now, so you'll need to correctly handle negative numbers.
  
  
**Resources:**
  
-
[The Animated Elliptic Curve: Visualizing Elliptic Curve Cryptography](https://curves.xargs.org/)
