In the CSIDH key exchange, a private key is a list of integers as long as the number of odd primes dividing

(

p

+

1

)

(p+1)





(

p



+





1

)
. This data represents an exponent vector

[


e

0

,


e

1

,


e

2

,

.

.

.

,


e

k

]

[e\_0, e\_1, e\_2, ..., e\_k]





[


e









0

​


,




e









1

​


,




e









2

​


,



...

,




e









k

​


]
which dictates the path of Alice and Bob's secret isogenies.
  
  
Before implementing CSIDH let us begin by computing an isogeny with the secret vector

[

2

,

3

,

4

]

[2,3,4]





[

2

,



3

,



4

]
from the starting curve
  
  









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
  
  
The flag for this challenge is the Montgomery coefficient A of the codomain.
  
  


Essentially what this challenge is asking you to do is compute an isogeny of degree

n

=


3

2

⋅


5

3

⋅


7

4

n = 3^{2} \cdot 5^{3} \cdot 7^{4}





n



=






3










2



⋅






5










3



⋅






7










4
. You will need this code again throughout this section, think about how to write this efficiently so you can generalise it to other vectors and other characteristics!
