The Elliptic Curve Discrete Logarithm Problem (ECDLP) is the problem of finding an integer

n

n





n
such that

Q

=

[

n

]

P

Q = [n]P





Q



=





[

n

]

P
.
  
  
Like we encountered with the discrete logarithm problem, scalar multiplication of a point in

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
seems to be be a hard problem to undo, with the most efficient algorithm running at

q


1

/

2

q^{1/2}






q










1/2
time when

P

P





P
generates a subgroup of size

q

q





q
.
  
  
This makes it a great candidate for a trapdoor function.
  
  
Alice and Bob are talking and they want to create a shared secret so they can start encrypting their messages with some symmetric cryptographic protocol Alice and Bob don't trust their connection, so they need a way to create a secret others can't replicate.
  
  
To start thing off, Alice and Bob agree on a curve

E

E





E
, a prime

p

p





p
and a generator point

G

G





G
which generates a subgroup

H

=

⟨

G

⟩

H = \langle G \rangle





H



=





⟨

G

⟩
of prime order

q

q





q
  
  


In elliptic curve cryptography, it is important that the order of

G

G





G
is prime. Constructing secure curves is complicated and it is recommended to use a preconstructed curve where a client is given the curve, the prime and the generator to use.
  
  
The Elliptic Curve Diffie-Hellman Key Exchange goes as follows:
  
  

* Alice generates a secret random integer

  n

  A

  n\_A






  n









  A

  ​

  and calculates

  Q

  A

  =

  [


  n

  A

  ]

  G

  Q\_A = [n\_A]G






  Q









  A

  ​




  =





  [


  n









  A

  ​


  ]

  G
* Bob generates a secret random integer

  n

  B

  n\_B






  n









  B

  ​

  and calculates

  Q

  B

  =

  [


  n

  B

  ]

  G

  Q\_B = [n\_B]G






  Q









  B

  ​




  =





  [


  n









  B

  ​


  ]

  G
* Alice sends Bob

  Q

  A

  Q\_A






  Q









  A

  ​

  , and Bob sends Alice

  Q

  B

  Q\_B






  Q









  B

  ​

  . Due to the hardness of ECDLP, an onlooker Eve is unable to calculate

  n


  A

  /

  B

  n\_{A/B}






  n










  A

  /

  B

  ​

  in reasonable time.
* Alice then calculates

  [


  n

  A

  ]


  Q

  B

  [n\_A]Q\_B





  [


  n









  A

  ​


  ]


  Q









  B

  ​

  , and Bob calculates

  [


  n

  B

  ]


  Q

  A

  [n\_B]Q\_A





  [


  n









  B

  ​


  ]


  Q









  A

  ​

  .
* Due to the associativity of scalar multiplication,

  S

  =

  [


  n

  A

  ]


  Q

  B

  =

  [


  n

  B

  ]


  Q

  A

  S = [n\_A]Q\_B = [n\_B]Q\_A





  S



  =





  [


  n









  A

  ​


  ]


  Q









  B

  ​




  =





  [


  n









  B

  ​


  ]


  Q









  A

  ​

  .
* Alice and Bob can use

  S

  S





  S
  as their shared secret.
  
  
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

Q

A

=

(

815

,

3190

)

Q\_A = (815, 3190)






Q









A

​




=





(

815

,



3190

)
, with your secret integer

n

B

=

1829

n\_B = 1829






n









B

​




=





1829
.
  
  
Generate a key by calculating the SHA1 hash of the

x

x





x
coordinate (take the integer representation of the coordinate and cast it to a string). The flag is the hexdigest you find.
  
  


This curve is not cryptographically secure!! We've picked a small prime for these starter challenges to keep everything fast while you learn. Cryptographically secure curves have primes of bit size ≈ 256
