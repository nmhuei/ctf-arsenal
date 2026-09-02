We say a set of vectors

v

1

,


v

2

,

…

,


v

k

∈

V

v\_{1}, v\_{2}, \ldots, v\_{k} \in V






v










1

​


,




v










2

​


,



…



,




v










k

​




∈





V
are linearly independent if the only solution to the equation:
  
  









a

1

⋅


v

1

+


a

2

⋅


v

2

+

…

+


a

k

⋅


v

k

=

0

a\_{1} \cdot v\_{1} + a\_{2} \cdot v\_{2} + \ldots + a\_{k} \cdot v\_{k} = 0






a










1

​




⋅






v










1

​




+






a










2

​




⋅






v










2

​




+





…



+






a










k

​




⋅






v










k

​




=





0
  
  
is for

a

1

=


a

2

=

…

=


a

k

=

0

a\_{1} = a\_{2} = \ldots = a\_{k} = 0






a










1

​




=






a










2

​




=





…



=






a










k

​




=





0
.
  
  


To visualise this, think of a vector directed out of a point. Given a set of linearly independent vectors, the only way to return back to the original point is by moving along the original vector. No combination of any of the other vectors will get you there.
  
  
A basis is a set of linearly independent vectors

v

1

,


v

2

,

…

,


v

n

∈

V

v\_{1}, v\_{2}, \ldots, v\_{n} \in V






v










1

​


,




v










2

​


,



…



,




v










n

​




∈





V
such that any vector

w

∈

V

w \in V





w



∈





V
can be written as:
  
  








w

=


a

1

⋅


v

1

+


a

2

⋅


v

2

+

…

+


a

k

⋅


v

n

w = a\_{1} \cdot v\_{1} + a\_{2} \cdot v\_{2} + \ldots + a\_{k} \cdot v\_{n}





w



=






a










1

​




⋅






v










1

​




+






a










2

​




⋅






v










2

​




+





…



+






a










k

​




⋅






v










n

​

  
  
The number of elements in the basis is also the dimension of the vector space.
  
  
We define the size of a vector, denoted

∣

∣

v

∣

∣

||v||





∣∣

v

∣∣
, using the inner product of the vector with itself:

∣

∣

v

∣


∣

2

=

v

⋅

v

||v||^{2} = v \cdot v





∣∣

v

∣


∣










2



=





v



⋅





v
.
  
  
A basis is orthogonal if for a vector basis

v

1

,


v

2

,

…

,


v

n

∈

V

v\_{1}, v\_{2}, \ldots, v\_{n} \in V






v










1

​


,




v










2

​


,



…



,




v










n

​




∈





V
, the inner product between any two different vectors is zero:

v

i

⋅


v

j

=

0

,

i

≠

j

v\_{i} \cdot v\_{j} = 0, i \neq j






v










i

​




⋅






v










j

​




=





0

,



i















=





j
.
  
  
A basis is orthonormal if it is orthogonal and

∣

∣


v

i

∣

∣

=

1

||v\_{i}|| = 1





∣∣


v










i

​


∣∣



=





1
, for all

i

i





i
.
  
  
That's a lot of stuff, but we'll be needing it. Time for the flag. Given the vector

v

=

(

4

,

6

,

2

,

5

)

v = (4, 6, 2, 5)





v



=





(

4

,



6

,



2

,



5

)
, calculate its size.
