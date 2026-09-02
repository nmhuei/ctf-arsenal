Imagine you lean over and look at a cryptographer's notebook. You see some notes in the margin:
  
  

4 + 9 = 1
  
5 - 7 = 10
  
2 + 3 = 5
  
  
At first you might think they've gone mad. Maybe this is why there are so many data leaks nowadays you'd think, but this is nothing more than modular arithmetic modulo 12 (albeit with some sloppy notation).
  
  
You may not have been calling it modular arithmetic, but you've been doing these kinds of calculations since you learnt to tell the time (look again at those equations and think about adding hours).
  
  
Formally, "calculating time" is described by the theory of congruences. We say that two integers are congruent modulo m if

a

≡

b






m

o

d

m

a \equiv b \mod m





a



≡





b







mod





m
.
  
  
Another way of saying this, is that when we divide the integer

a

a





a
by

m

m





m
, the remainder is

b

b





b
. This tells you that if

m

m





m
divides

a

a





a
(this can be written as

m

∣

a

m | a





m

∣

a
) then

a

≡

0






m

o

d

m

a\equiv 0 \mod m





a



≡





0







mod





m
.
  
  
Calculate the following integers:
  
  








11

≡

x






m

o

d

6

11 \equiv x \mod 6





11



≡





x







mod





6
  







8146798528947

≡

y






m

o

d

17

8146798528947 \equiv y \mod 17





8146798528947



≡





y







mod





17
  
  
The solution is the smaller of the two integers,

(

x

,

y

)

(x, y)





(

x

,



y

)
, you obtained after reducing by the modulus.
