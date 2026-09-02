The last challenge showed that this protocol satisfies (perfect) completeness! That is, if a prover and verifier follow the protocol on valid inputs, and the prover knows the real witness, the verifier will always accept.
  
  
The second property a protocol must have to be a

Σ

\Sigma





Σ
-Protocol is Special Soundness. We will call the messages sent between P and V,

(

a

,

e

,

z

)

(a,e,z)





(

a

,



e

,



z

)
, a "transcript".
  
  
Special soundness is defined (roughly) as follows: Given any two accepting transcripts

(

a

,

e

,

z

)

(a,e,z)





(

a

,



e

,



z

)
and

(

a

,


e

′

,


z

′

)

(a,e',z')





(

a

,




e










′

,




z










′

)
proving the same relation, where

e

≠


e

′

e \neq e'





e















=






e










′
, you can efficiently compute a witness for this relation.
  
  
For our current protocol, this means that for a given

P

,

q

,

g

,

y

P,q,g,y





P

,



q

,



g

,



y
and accepting transcripts

(

a

,

e

,

z

)

(a,e,z)





(

a

,



e

,



z

)
and

(

a

,


e

′

,


z

′

)

(a,e',z')





(

a

,




e










′

,




z










′

)
where

e

≠


e

′

e \neq e'





e















=






e










′
, we can efficiently compute a witness

w

w





w
such that

g

w

=

y






m

o

d

P

g^w = y \mod P






g









w



=





y







mod





P
.
  
  


This doesn't require that the

w

w





w
computed is the same one that the Prover was using. While in our current case

w

w





w
is unique, so it must be the same, there exist other classes of relations where there are many valid witnesses. And computing any valid witness is enough for special soundness.
  
  
This property is very powerful, and is the essence of what we mean when we talk about "proving knowledge" of something.
  
  
Imagine a Prover has sent an

a

a





a
to the Verifier, and receives a random challenge

e

e





e
back, the Prover now has to produce a

z

z





z
such that the verifier accepts the transcript.
  
  
If the prover can do this, then either the Prover was only able to complete the transcript for one specific

e

e





e
, (in which case he got

1

/


2

t

1/2^t





1/


2









t
lucky, and his probability of convincing the verifier is negligible in the security parameter.) Or the Prover was able to complete the transcript for more than one

e

e





e
challenge.
  
  
However, being able to complete a transcript for more than one

e

e





e
challenge is equivalent to being able to produce at least two accepting transcripts locally, which is equivalent to computing the witness.
  
  
So any Prover who can convince the verifier he knows

w

w





w
with non negligible probability knows

w

w





w
, (or is able to efficiently compute it, which we treat as equivalent.)
  
  


You can see special soundness as saying "if the prover can produce a

z

z





z
which the verifier accepts for at least two challenges after committing to an

a

a





a
, then

w

w





w
, or information to compute

w

w





w
, is somewhere in his head."
  
  
For this challenge, you are the verifier, and the prover will accidentally reuse the same

a

a





a
over two runs. Show that this lets you extract

w

w





w
from her!
  
  


Look at the relation between

z

,

e

,


z

′

,


e

′

z, e, z', e'





z

,



e

,




z










′

,




e










′
and

r

r





r
  
  
Connect at
`socket.cryptohack.org 13426`
  
  
**Challenge files:**
  
-
[13426.py](/static/challenges/13426_2434b3b3f4044a63115e18e476f420db.py)
  
  
  
Challenge contributed by
[killerdog](/user/killerdog)
