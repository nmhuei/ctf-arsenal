Before defining a lattice or talking about how lattices appear in cryptography, let's review some of the basics of linear algebra. The following challenges should be considered as revision, if this is totally new to you, you might need to do a bit of background reading. As usual, we recommend "An Introduction to Mathematical Cryptography" by Hoffstein, Pipher, Silverman, as well as this
[introduction to lattices](https://web.archive.org/web/20220508113525/https://www.cryptool.org/download/ctb/CTB-Chapter_Lattice-Introduction_en.pdf)
and their applications.
  
  
A vector space

V

V





V
over a field

F

F





F
is a set defined with two binary operators. For a vector

v

∈

V

v \in V





v



∈





V
, and a scalar

a

∈

F

a \in F





a



∈





F
,
*vector addition*
takes two vectors and produces another vector:

v

+

w

=

z

,

v + w = z,





v



+





w



=





z

,
for

v

,

w

,

z

∈

V

v, w, z \in V





v

,



w

,



z



∈





V
and
*scalar multiplication*
takes a vector and a scalar and produces a vector:

a

⋅

v

=

w

,

a \cdot v = w,





a



⋅





v



=





w

,
for

v

,

w

∈

V

,

a

∈

F

v, w \in V, a \in F





v

,



w



∈





V

,



a



∈





F
.
  
  


You will probably have first seen vectors in the context of a two dimensional vector space defined over the reals. We'll use this here too as an example!
  
  
Let's consider a two dimensional vector space over the reals. A vector

v

∈

V

v \in V





v



∈





V
can be considered as a pair of numbers:

v

=

(

a

,

b

)

v = (a,b)





v



=





(

a

,



b

)
for

a

,

b

∈

R

a,b \in R





a

,



b



∈





R
. Vector addition works as

v

+

w

=

(

a

,

b

)

+

(

c

,

d

)

=

(

a

+

c

,

b

+

d

)

v + w = (a,b) + (c,d) = (a+c, b+d)





v



+





w



=





(

a

,



b

)



+





(

c

,



d

)



=





(

a



+





c

,



b



+





d

)
, and scalar multiplication by

c

⋅

v

=

c

⋅

(

a

,

b

)

=

(

c

⋅

a

,

c

⋅

b

)

c \cdot v = c \cdot (a,b) = (c \cdot a, c \cdot b)





c



⋅





v



=





c



⋅





(

a

,



b

)



=





(

c



⋅





a

,



c



⋅





b

)
.
  
  
One can also define the
*inner product*
(also called the
*dot product*
), which takes two vectors and returns a scalar. Formally we think of this as

v

⋅

w

=

a

v \cdot w = a





v



⋅





w



=





a
for

v

,

w

∈

V

,

a

∈

F

v,w \in V, a \in F





v

,



w



∈





V

,



a



∈





F
. In our two-dimensional example, the inner product works as

v

⋅

w

=

(

a

,

b

)

⋅

(

c

,

d

)

=

a

⋅

c

+

b

⋅

d

v \cdot w = (a,b) \cdot (c,d) = a \cdot c + b \cdot d





v



⋅





w



=





(

a

,



b

)



⋅





(

c

,



d

)



=





a



⋅





c



+





b



⋅





d
.
  
  
Time for the flag! Given a three dimensional vector space defined over the reals, where

v

=

(

2

,

6

,

3

)

v = (2,6,3)





v



=





(

2

,



6

,



3

)
,

w

=

(

1

,

0

,

0

)

w = (1,0,0)





w



=





(

1

,



0

,



0

)
and

u

=

(

7

,

7

,

2

)

u = (7,7,2)





u



=





(

7

,



7

,



2

)
, calculate

3

⋅

(

2

⋅

v

−

w

)

⋅

2

⋅

u

3 \cdot (2 \cdot v - w) \cdot 2 \cdot u





3



⋅





(

2



⋅





v



−





w

)



⋅





2



⋅





u
.
