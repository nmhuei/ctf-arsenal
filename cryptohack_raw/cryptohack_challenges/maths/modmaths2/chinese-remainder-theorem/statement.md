The Chinese Remainder Theorem gives a unique solution to a set of linear congruences if their moduli are coprime.
  
  
This means, that given a set of arbitrary integers

a

i

a^{i}






a










i
, and pairwise coprime integers

n

i

n^{i}






n










i
, such that the following linear congruences hold:
  
  


Note "pairwise coprime integers" means that if we have a set of integers

{


n

1

,


n

2

,

.

.

.

,


n

i

}

\{n^{1}, n^{2}, ..., n^{i}\}





{


n










1

,




n










2

,



...

,




n










i

}
, all pairs of integers selected from the set are coprime:

gcd

⁡

(


n

i

,


n

j

)

=

1

\gcd(n^{i}, n^{j}) = 1






g
cd

(


n










i

,




n










j

)



=





1
.
  
  








x

≡


a

1






m

o

d


n

1

x \equiv a^{1} \mod n^{1}





x



≡






a










1







mod






n










1
  







x

≡


a

2






m

o

d


n

2

x \equiv a^{2} \mod n^{2}





x



≡






a










2







mod






n










2
  







…

\ldots





…
  







x

≡


a

n






m

o

d


n

n

x \equiv a^{n} \mod n^{n}





x



≡






a










n







mod






n










n
  
  
There is a unique solution

x

≡

a






m

o

d

N

x \equiv a \mod N





x



≡





a







mod





N
where

N

=


n

1

⋅


n

2

⋅

.

.

.

⋅


n

n

N = n^{1} \cdot n^{2} \cdot ... \cdot n^{n}





N



=






n










1



⋅






n










2



⋅





...



⋅






n










n
.
  
  
In cryptography, we commonly use the Chinese Remainder Theorem to help us reduce a problem of very large integers into a set of several, easier problems.
  
  
Given the following set of linear congruences:
  
  








x

≡

2






m

o

d

5

x \equiv 2 \mod 5





x



≡





2







mod





5
  







x

≡

3






m

o

d

11

x \equiv 3 \mod 11





x



≡





3







mod





11
  







x

≡

5






m

o

d

17

x \equiv 5 \mod 17





x



≡





5







mod





17
  
  
Find the integer

a

a





a
such that

x

≡

a






m

o

d

935

x \equiv a \mod 935





x



≡





a







mod





935
  
  


Starting with the congruence with the largest modulus, use that for

x

≡

a






m

o

d

p

x \equiv a \mod p





x



≡





a







mod





p
we can write

x

=

a

+

k

⋅

p

x = a + k \cdot p





x



=





a



+





k



⋅





p
for arbitrary integer

k

k





k
.
