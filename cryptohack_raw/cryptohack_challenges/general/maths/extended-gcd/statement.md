Let

a

a





a
and

b

b





b
be positive integers.
  
  
The extended Euclidean algorithm is an efficient way to find integers

u

,

v

u,v





u

,



v
such that
  
  








a

⋅

u

+

b

⋅

v

=

gcd

⁡

(

a

,

b

)

a \cdot u + b \cdot v = \gcd(a,b)





a



⋅





u



+





b



⋅





v



=






g
cd

(

a

,



b

)
  
  


Later, when we learn to decrypt RSA ciphertexts, we will need this algorithm to calculate the modular inverse of the public exponent.
  
  
Using the two primes

p

=

26513

,

q

=

32321

p = 26513, q = 32321





p



=





26513

,



q



=





32321
, find the integers

u

,

v

u,v





u

,



v
such that
  
  








p

⋅

u

+

q

⋅

v

=

gcd

⁡

(

p

,

q

)

p \cdot u + q \cdot v = \gcd(p,q)





p



⋅





u



+





q



⋅





v



=






g
cd

(

p

,



q

)
  
  
Enter whichever of

u

u





u
and

v

v





v
is the lower number as the flag.
  
  


Knowing that

p

,

q

p,q





p

,



q
are prime, what would you expect

gcd

⁡

(

p

,

q

)

\gcd(p,q)






g
cd

(

p

,



q

)
to be? For more details on the extended Euclidean algorithm, check out
[this page](https://web.archive.org/web/20230511143526/http://www-math.ucdenver.edu/~wcherowi/courses/m5410/exeucalg.html)
.
