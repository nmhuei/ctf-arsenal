We'll pick up from the last challenge and imagine we've picked a modulus

p

p





p
, and we will restrict ourselves to the case when

p

p





p
is prime.
  
  
The integers modulo

p

p





p
define a field, denoted

F

p

\Fp






F










p

​

.
  
  


If the modulus is not prime, the set of integers modulo

n

n





n
define a ring.
  
  
A finite field

F

p

\Fp






F










p

​

is the set of integers

0

,

1

,

.

.

.

,

p

−

1

{0,1,...,p-1}






0

,



1

,



...

,



p



−



1
, and under both addition and multiplication there are inverse elements

b

+

b\_{+}






b










+

​

and

b

∗

b\_{\*}






b










∗

​

for every element

a

a





a
in the set, such that

a

+


b

+

=

0

a + b\_{+} = 0





a



+






b










+

​




=





0
and

a

⋅


b

∗

=

1

a \cdot b\_{\*} = 1





a



⋅






b










∗

​




=





1
.
  
  


Note that the identity element for addition and multiplication is different! This is because the identity when acted with the operator should do nothing:

a

+

0

=

a

a + 0 = a





a



+





0



=





a
and

a

⋅

1

=

a

a \cdot 1 = a





a



⋅





1



=





a
.
  
  
Lets say we pick

p

=

17

p = 17





p



=





17
. Calculate

3

17






m

o

d

17

3^{17} \mod 17






3










17







mod





17
. Now do the same but with

5

17






m

o

d

17

5^{17} \mod 17






5










17







mod





17
.
  
  
What would you expect to get for

7

16






m

o

d

17

7^{16} \mod 17






7










16







mod





17
? Try calculating that.
  
  
This interesting fact is known as Fermat's little theorem. We'll be needing this (and its generalisations) when we look at RSA cryptography.
  
  
Now take the prime

p

=

65537

p = 65537





p



=





65537
. Calculate

27324678765


4

65536






m

o

d

65537

273246787654^{65536} \mod 65537





27324678765


4










65536







mod





65537
.
  
  
Did you need a calculator?
