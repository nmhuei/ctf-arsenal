Now we're going to jump in and decrypt a message that's hidden in the low bits of a toy LWE system. The noise is stored in the high bits.
  
  
**Parameters:**
  
  

* vector space dimension

  n

  n





  n
* ciphertext modulus

  q

  q





  q
* plaintext modulus

  p

  p





  p
  (can only encrypt messages

  m

  <

  p

  m < p





  m



  <





  p
  )
* must have

  q

  q





  q
  ,

  p

  p





  p
  be coprime

  
  
**Key-gen:**
  
  

* The secret key

  S

  S





  S
  is a random element of the vector space

  Z

  q

  n

  \mathbb{Z}\_q^n






  Z









  q





  n

  ​

  .

  
  
**Ciphertext format:**
  
  

* Ciphertexts consist of a pair

  A

  ,

  b

  A, b





  A

  ,



  b
  , where

  A

  A





  A
  is an element of the vector space

  Z

  q

  n

  \mathbb{Z}\_q^n






  Z









  q





  n

  ​

  , and

  b

  b





  b
  is an element of

  Z

  q

  \mathbb{Z}\_q






  Z









  q

  ​

  .

  
  
**Encryption given message

m

m





m
:**
  
  

1. Sample

   A

   A





   A
   , a random element of the vector space

   Z

   q

   n

   \mathbb{Z}\_q^n






   Z









   q





   n

   ​
2. Sample the error-term

   e

   e





   e
   , an integer in the range

   [

   −

   (

   q

   /

   p

   )

   /

   2

   ,

   (

   q

   /

   p

   )

   /

   2

   ]

   [-(q/p)/2, (q/p)/2]





   [

   −

   (

   q

   /

   p

   )

   /2

   ,



   (

   q

   /

   p

   )

   /2

   ]
   . Note: often the error is sampled from a discrete Gaussian distribution, but uniform sampling is fine
3. Compute

   b

   =

   ⟨

   A

   ,

   S

   ⟩

   +

   m

   +

   p

   ⋅

   e

   b = \langle A, S \rangle + m + p \cdot e





   b



   =





   ⟨

   A

   ,



   S

   ⟩



   +





   m



   +





   p



   ⋅





   e
4. Return the pair

   (

   A

   ,

   b

   )

   (A, b)





   (

   A

   ,



   b

   )

  
  
**Decryption given ciphertext

(

A

,

b

)

(A, b)





(

A

,



b

)
:**
  
  

1. Compute

   x

   =

   b

   −

   ⟨

   A

   ,

   S

   ⟩

   x = b - \langle A, S \rangle





   x



   =





   b



   −





   ⟨

   A

   ,



   S

   ⟩
   centered modulo

   q

   q





   q
   and then interpret

   x

   x





   x
   as an integer (
   *not*
   modulo

   q

   q





   q
   ). Note: this centered modular reduction must produce a result between

   (

   −

   q

   /

   2

   ,

   q

   /

   2

   ]

   (-q/2, q/2]





   (

   −

   q

   /2

   ,



   q

   /2

   ]
   as opposed to usual modular reduction producing a result between

   [

   0

   ,

   q

   −

   1

   ]

   [0, q-1]





   [

   0

   ,



   q



   −





   1

   ]
2. Compute

   m

   =

   x






   m

   o

   d

   p

   m = x \mod p





   m



   =





   x







   mod





   p
   , where the division and rounding happens over the integers
3. return m

  
  
In this system, decryption works because after the mask

⟨

A

,

S

⟩

\langle A, S \rangle





⟨

A

,



S

⟩
has been removed, the remaining equation for the noisy message

m

+

p

⋅

e

m + p \cdot e





m



+





p



⋅





e
holds over the integers, so there is no modular wraparound due to

q

q





q
. As such, removing the error term

e

e





e
can be done by reducing modulo

p

p





p
. This requires the parameters to be chosen so that

m

+

p

⋅

e

<

q

/

2

m + p \cdot e < q/2





m



+





p



⋅





e



<





q

/2
holds.
  
  
**Challenge files:**
  
-
[lwe-low-bits.sage](/static/challenges/lwe-low-bits_a2c45284086e181a601486fe22f873ff.sage)
  
-
[output.txt](/static/challenges/output_9eb8e78124c8c48ec9eb687bf1d10a4e.txt)
  
  
  
Challenge contributed by
[ireland](/user/ireland)
