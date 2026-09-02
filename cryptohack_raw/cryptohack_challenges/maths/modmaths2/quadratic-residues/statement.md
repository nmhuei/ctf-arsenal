We've looked at multiplication and division in modular arithmetic, but what does it mean to take the square root modulo an integer?
  
  
For the following discussion, let's work modulo

p

=

29

p = 29





p



=





29
. We can take the integer

a

=

11

a = 11





a



=





11
and calculate

a

2

=

5






m

o

d

29

a^{2} = 5 \mod 29






a










2



=





5







mod





29
.
  
  
As

a

=

11

,


a

2

=

5

a = 11, a^{2} = 5





a



=





11

,




a










2



=





5
, we say the square root of

5

5





5
is

11

11





11
.
  
  
This feels good, but now let's think about the square root of

18

18





18
. From the above, we know we need to find some integer

a

a





a
such that

a

2

=

18

a^{2} = 18






a










2



=





18
  
  
Your first idea might be to start with

a

=

1

a = 1





a



=





1
and loop to

a

=

p

−

1

a = p-1





a



=





p



−





1
. In this discussion

p

p





p
isn't too large and we can quickly check all options.
  
  
Have a go, try coding this and see what you find. If you've coded it right, you'll find that for all

a

∈


F

p

∗

a \in \Fp^{\*}





a



∈






F










p






∗

​

you never find an

a

a





a
such that

a

2

=

18

a^{2} = 18






a










2



=





18
.
  
  
What we are seeing, is that for the elements of

F

p

∗

\Fp^{\*}






F










p






∗

​

, not every element has a square root. In fact, what we find is that for roughly one half of the elements of

F

p

∗

\Fp^{\*}






F










p






∗

​

, there is no square root.
  
  


We say that an integer

x

x





x
is a
*Quadratic Residue*
if there exists an

a

a





a
such that

a

2

≡

x






m

o

d

p

a^{2} \equiv x \mod p






a










2



≡





x







mod





p
. If there is no such solution, then the integer is a
*Quadratic Non-Residue*
.
  
  
In other words,

x

x





x
is a quadratic residue when it is possible to take the square root of

x

x





x
modulo an integer

p

p





p
.
  
  
In the below list there are two non-quadratic residues and one quadratic residue.
  
  
Find the quadratic residue and then calculate its square root. Of the two possible roots, submit the smaller one as the flag.
  
  


If

a

2

=

x

a^{2} = x






a










2



=





x
then

(

−

a


)

2

=

x

(-a)^{2} = x





(

−

a


)










2



=





x
. So if

x

x





x
is a quadratic residue in some finite field, then there are always two solutions for

a

a





a
.
  
  








p

=

29



i

n

t

s

=

[

14

,

6

,

11

]

p = 29 \quad ints = [14, 6, 11]





p



=





29



in

t

s



=





[

14

,



6

,



11

]
