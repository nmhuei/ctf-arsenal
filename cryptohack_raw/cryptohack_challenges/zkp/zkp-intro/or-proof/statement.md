We have already seen how proving a protocol to be a

Σ

\Sigma





Σ
-Protocol essentially gives us a NIZK transformation for free. But it also opens up a wide range of results, constructions and tools from literature which allow us to easily compose simpler

Σ

\Sigma





Σ
-Protocols, using them as the building blocks for much more complicated functionalities.
  
  
One of these basic constructions is the OR-proof. That is, given two

Σ

\Sigma





Σ
-Protocols

Σ

1

\Sigma\_{1}






Σ










1

​

and

Σ

2

\Sigma\_{2}






Σ










2

​

, there is a generic transform which will give us a new

Σ

\Sigma





Σ
-Protocol

Σ

3

\Sigma\_{3}






Σ










3

​

which is the OR of

Σ

1

\Sigma\_{1}






Σ










1

​

and

Σ

2

\Sigma\_{2}






Σ










2

​

.
  
  


Let prover P be given inputs

x

0

,


x

1

,

w

x\_{0},x\_{1},w






x










0

​


,




x










1

​


,



w
, where

w

w





w
is a witness such that either

(


x

0

,

w

)

∈

R

(x\_{0},w) \in R





(


x










0

​


,



w

)



∈





R
or

(


x

1

,

w

)

∈

R

(x\_{1},w) \in R





(


x










1

​


,



w

)



∈





R
. The

Σ


O

R

\Sigma\_{OR}






Σ










OR

​

protocol will allow P to prove he knows a witness to one of these cases, without revealing which he knows the witness to.
  
  
This is a very useful primitive for building more advanced protocols, allowing you to compose the OR of knowledge of a witness for arbitrary many relations together into one protocol.
  
  
  
The protocol is as follows, for public inputs

(


x

0

,


x

1

)

(x\_{0}, x\_{1})





(


x










0

​


,




x










1

​


)
where P has a witness for

x

b

x\_{b}






x










b

​

:
  
  

1. For protocol

   (

   1

   −

   b

   )

   (1-b)





   (

   1



   −





   b

   )
   , P samples a random

   e


   1

   −

   b

   e\_{1-b}






   e










   1

   −

   b

   ​

   , then runs the simulator from

   Σ


   1

   −

   b

   \Sigma\_{1-b}






   Σ










   1

   −

   b

   ​

   to get accepting transcript

   (


   a


   1

   −

   b

   ,


   e


   1

   −

   b

   ,


   z


   1

   −

   b

   )

   (a\_{1-b},e\_{1-b},z\_{1-b})





   (


   a










   1

   −

   b

   ​


   ,




   e










   1

   −

   b

   ​


   ,




   z










   1

   −

   b

   ​


   )
2. For Protocol

   b

   b





   b
   , P computes

   a

   b

   a\_{b}






   a










   b

   ​

   honestly
3. P sends

   (


   a

   0

   ,


   a

   1

   )

   (a\_{0}, a\_{1})





   (


   a










   0

   ​


   ,




   a










   1

   ​


   )
   to V
4. V sends random challenge

   s

   s





   s
   to P
5. P sets

   e

   b

   =

   s

   ⊕


   e


   1

   −

   b

   e\_{b} = s \oplus e\_{1-b}






   e










   b

   ​




   =





   s



   ⊕






   e










   1

   −

   b

   ​
6. P uses

   (


   a

   b

   ,


   e

   b

   ,


   w

   b

   )

   (a\_{b},e\_{b},w\_{b})





   (


   a










   b

   ​


   ,




   e










   b

   ​


   ,




   w










   b

   ​


   )
   to honestly compute

   z

   b

   z\_{b}






   z










   b

   ​

   , getting accepting transcript

   a

   b

   ,


   e

   b

   ,


   z

   b

   a\_{b},e\_{b},z\_{b}






   a










   b

   ​


   ,




   e










   b

   ​


   ,




   z










   b

   ​
7. P sends

   t

   0

   =

   (


   a

   0

   ,


   e

   0

   ,


   z

   0

   )

   ,


   t

   1

   =

   (


   a

   1

   ,


   e

   1

   ,


   z

   1

   )

   t\_{0}=(a\_{0},e\_{0},z\_{0}),t\_{1}=(a\_{1},e\_{1},z\_{1})






   t










   0

   ​




   =





   (


   a










   0

   ​


   ,




   e










   0

   ​


   ,




   z










   0

   ​


   )

   ,




   t










   1

   ​




   =





   (


   a










   1

   ​


   ,




   e










   1

   ​


   ,




   z










   1

   ​


   )
   to V
8. V accepts if

   e

   0

   ⊕


   e

   1

   =

   s

   e\_{0} \oplus e\_{1} = s






   e










   0

   ​




   ⊕






   e










   1

   ​




   =





   s
   , and both transcripts

   t

   0

   t\_{0}






   t










   0

   ​

   and

   t

   1

   t\_{1}






   t










   1

   ​

   are accepting w.r.t the relevant public parameters.

  
  


The intuition behind this protocol is as follows. We know from SHVZK that if we get to choose

e

e





e
before

a

a





a
, then we can forge a transcript which is indistinguishable from a real accepting transcript. In the OR protocol, the prover is essentially providing a valid transcript for both

Σ

0

\Sigma\_{0}






Σ










0

​

and

Σ

1

\Sigma\_{1}






Σ










1

​

, where the

e

e





e
values have to

x

o

r

xor





x

or
to the verifiers challenge. This lets the prover select exactly one of the

e

e





e
values itself. For the branch it does not have a witness for it uses its SHVZK simulator with this selected

e

e





e
, creating a full transcript locally and sending the

a

a





a
for that transcript, and then honestly creates the other transcript running the real protocol against the verifier, with the xor of it's simulated

e

e





e
and the verifiers challenge as the honest protocol challenge.
  
  
The basic idea is P simulates the half of the protocol he has no witness for, by picking that challenge. This results in the

s

s





s
received from the verifier uniquely determining the challenge for the other protocol, but he knows the witness for that half so he can complete the remaining half honestly.
  
  
In this challenge you will show that the OR proof is a

Σ

\Sigma





Σ
-Protocol, by going through completeness, extracting a witness to show special-soundness and simulating a transcript to show SHVZK.
  
  
**This challenge is hosted on the CTF archive. Find the corresponding challenge in that category, solve it, then enter the flag here.**
  
  
Challenge contributed by
[killerdog](/user/killerdog)
