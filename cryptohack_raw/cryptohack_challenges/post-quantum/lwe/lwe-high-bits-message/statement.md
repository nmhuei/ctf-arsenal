Now we're going to jump in and decrypt a message that's hidden in the high bits of a toy LWE system.
  
  
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
* scaling factor

  Δ

  =

  round

  (

  q

  /

  p

  )

  \Delta = \text{round}(q / p)





  Δ



  =






  round

  (

  q

  /

  p

  )

  
  
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

   Δ

   /

   2

   ,

   Δ

   /

   2

   ]

   [-\Delta / 2, \Delta / 2]





   [

   −

   Δ/2

   ,



   Δ/2

   ]
   . (Note: often the error is sampled from a discrete Gaussian distribution, but uniform sampling is fine)
3. Compute

   b

   =

   ⟨

   A

   ,

   S

   ⟩

   +

   Δ

   ⋅

   m

   +

   e

   b = \langle A,S \rangle + \Delta \cdot m + e





   b



   =





   ⟨

   A

   ,



   S

   ⟩



   +





   Δ



   ⋅





   m



   +





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






   m

   o

   d

   q

   x = b - \langle A,S \rangle \mod q





   x



   =





   b



   −





   ⟨

   A

   ,



   S

   ⟩







   mod





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
   )
2. Compute

   m

   =

   round

   (

   x

   /

   Δ

   )

   m = \text{round}(x / \Delta)





   m



   =






   round

   (

   x

   /Δ

   )
   , where the division and rounding happens over the integers
3. return m

  
  
In this system, decryption works because after the mask

⟨

A

,

S

⟩

\langle A,S \rangle





⟨

A

,



S

⟩
has been removed, the remaining equation for the noisy message

Δ

⋅

m

+

e

\Delta \cdot m + e





Δ



⋅





m



+





e
holds over the integers, so there is no modular wraparound due to

q

q





q
. As such, removing the error term

e

e





e
can be done by rounding integer-division. This requires the parameters to be chosen so that

Δ

⋅

m

+

e

<

q

/

2

\Delta \cdot m + e < q/2





Δ



⋅





m



+





e



<





q

/2
holds.
  
  
**Challenge files:**
  
-
[lwe-high-bits.sage](/static/challenges/lwe-high-bits_a83f7bfc0f6e3bfd1b962842feb5d91d.sage)
  
-
[output.txt](/static/challenges/output_575f13474e5a8cc76e938508bce813c2.txt)
  
  
  
Challenge contributed by
[ireland](/user/ireland)
