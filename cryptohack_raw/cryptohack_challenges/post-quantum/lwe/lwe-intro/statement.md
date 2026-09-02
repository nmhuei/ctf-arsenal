Learning With Errors (LWE) refers to the computational problem of learning a linear function

f

(

A

)

f(A)





f

(

A

)
which takes values over a ring, given many noisy samples of the function. These samples look like the pair

(

A

,

⟨

A

,

S

⟩

+

e

)

(A, \langle A, S \rangle + e)





(

A

,



⟨

A

,



S

⟩



+





e

)
, where

S

S





S
is the secret element which defines the linear function,

e

e





e
is some small error term from a known distribution, and

A

A





A
is a known element of the ring. Note that

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
denotes the matrix multiplication of a matrix

A

A





A
with vector

S

S





S
.
  
  
Cryptosystems based on LWE are quite varied, but they usually have several common features:
  
  

* They use modular arithmetic under two different moduli: the plaintext modulus and the ciphertext modulus.
* The secret key is an element of a vector space modulo n.
* Messages are encrypted by adding an encoded noisy message to a large dot-product.

  
  
The noisy message is a properly-encoded sum of the message and a small error or noise term.
  
  
The dot-product is between the secret key and a random element of the vector space, where this random element is provided as part of the ciphertext.
  
  
This looks like

(

A

,

⟨

A

,

S

⟩

+

encoded

(

m

,

e

)

)

(A, \langle A,S \rangle + \text{encoded}(m, e))





(

A

,



⟨

A

,



S

⟩



+






encoded

(

m

,



e

))
, where

A

A





A
is an element of the vector space.
  
  
If the secret key is known, then the dot-product can be subtracted out, leaving only the encoded message and noise. Thanks to the special way in which the message and noise are encoded, the noise can be removed from the encoding, leaving only the message behind.
  
  
There are two common approaches to storing the message and noise in LWE systems: you can either store the message in the high-bits of the LWE sample and the noise in the low-bits, or vice-versa.
  
  

* Some examples of LWE schemes where the message is stored in the high-bits are
  [Regev09](https://cims.nyu.edu/~regev/papers/qcrypto.pdf)
  and BFV.
* An example of an LWE scheme where the message is stored in the low-bits is BGV.

  
  
What algorithm could be used to recover the message from the linear equations in polynomial time, if there was no added error?
  
  
**Resources:**
  
-
[The Learning with Errors Problem](https://cims.nyu.edu/~regev/papers/lwesurvey.pdf)
  
-
[Kyber - How does it work?](https://web.archive.org/web/20231008081450/https://cryptopedia.dev/posts/kyber/)
  
  
  
Challenge contributed by
[ireland](/user/ireland)
