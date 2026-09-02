Alice and Bob are looking at the Elliptic Curve Discrete Logarithm Problem and thinking about the data they send.
  
  
They want to try and keep their data transfer as efficient as possible and realise that sending both the

x

x





x
and

y

y





y
coordinate of their public key isn't necessary.
  
  
As long as Alice and Bob agree on the curve parameters, there are only ever two possible values of

y

y





y
for a given

x

x





x
.
  
  
In fact, given
*either*
of the values of

y

y





y
permissible from the value

x

x





x
they receive, the

x

x





x
coordinate of their shared secret will be the same.
  
  


For these challenges, we have used a prime

p

≡

3






m

o

d

4

p \equiv 3 \mod 4





p



≡





3







mod





4
, which will help you find

y

y





y
from

y

2

y^{2}






y










2
.
  
  
Using the curve, prime and generator:
  
  








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

,



G

:

(

1804

,

5368

)

E: Y^{2} = X^{3} + 497 X + 1768 \mod 9739, \quad G: (1804,5368)





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

,





G



:





(

1804

,



5368

)
  
  
Calculate the shared secret after Alice sends you

x

(


Q

A

)

=

4726

x(Q\_A) = 4726





x

(


Q









A

​


)



=





4726
, with your secret integer

n

B

=

6534

n\_B = 6534






n









B

​




=





6534
.
  
  
Use the
`decrypt.py`
file to decode the flag
  
  

{'iv': 'cd9da9f1c60925922377ea952afc212c', 'encrypted\_flag': 'febcbe3a3414a730b125931dccf912d2239f3e969c4334d95ed0ec86f6449ad8'}
  
  


You can specify which of the two possible values your public

y

y





y
coordinate has taken by sending only one bit. Try and think about how you could do this. How are the two

y

y





y
values related to each other?
  
  
**Challenge files:**
  
-
[decrypt.py](/static/challenges/decrypt_08c0fede9185868aba4a6ae21aca0148.py)
