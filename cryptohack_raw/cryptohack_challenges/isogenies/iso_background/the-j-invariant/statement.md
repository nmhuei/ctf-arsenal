Much like in modular arithmetic, where many computations are only equal up to an equivalence modulo N, in isogeny based-cryptography, many computations are only equal up to isomorphism. For two participants in a protocol, it's not enough to compare curve equations but instead they check whether two curves are isomorphic.
  
  
One way of determining whether two curves are isomorphic is by comparing an invariant of the curve. For elliptic curves we use the "j-invariant", denoted

j

(

E

)

j(E)





j

(

E

)
, which is what we will be computing for this challenge.
  
  


There is a subtle point here. If two curves are isomorphic, they have the same j-invariant, but if two curves have the same j-invariant they may not be isomorphic over the base field, but instead over some extension. An example of this is two curves related by a quadratic twist. The curves will have the same j-invariant but are only isomorphic over a quadratic extension.
  
  
To grab the flag for this challenge, compute

j

(

E

)

j(E)





j

(

E

)
of the supersingular curve:
  
  








E

:


y

2

=


x

3

+

145

x

+

49






m

o

d

163

E : y^2 = x^3 + 145 x + 49 \mod 163





E



:






y









2



=






x









3



+





145

x



+





49







mod





163
  
  
**Resources:**
  
-
[Ordinary and supersingular elliptic curves, Section 13.2, Andrew Sutherland](https://ocw.mit.edu/courses/18-783-elliptic-curves-spring-2021/6b139f926bbbe94db322ea23300b0246_MIT18_783S21_notes13.pdf)
