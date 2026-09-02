The private key

d

d





d
is used to decrypt ciphertexts created with the corresponding public key (it's also used to "sign" a message but we'll get to that later).
  
  
The private key is the secret piece of information, or "trapdoor", which allows us to quickly invert the encryption function. If RSA is implemented well, if you do not have the private key the fastest way to decrypt the ciphertext is to factorise the modulus which is very hard to do for large integers.
  
  
In RSA, the private key is the
[modular multiplicative inverse](https://en.wikipedia.org/wiki/Modular_multiplicative_inverse)
of the exponent

e

e





e
modulo

ϕ

(

N

)

\phi(N)





ϕ

(

N

)
, Euler's totient of

N

N





N
.
  
  
Given the two primes:
  
  

p = 857504083339712752489993810777
  
q = 1029224947942998075080348647219
  
  
and the exponent

e

=

65537

e = 65537





e



=





65537
, what is the private key

d

≡


e


−

1






m

o

d

ϕ

(

N

)

d \equiv e^{-1} \mod \phi(N)





d



≡






e










−

1







mod





ϕ

(

N

)
?
