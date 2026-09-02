So far we've only been looking at

Σ

\Sigma





Σ
-Protocols with one round, where there is a large enough challenge space that the probability of randomly sampling a specific

e

e





e
is negligible in the security parameter. While this works well for

Σ

\Sigma





Σ
-Protocols like Schnorrs, there are other classes of relations we wish to prove witnesses of where this pattern isn't so convenient.
  
  
In this challenge we are going to look at an example of a

Σ

\Sigma





Σ
-Protocol which uses a one bit challenge, giving the Prover a 50% chance of "guessing" the challenge correctly. While this gives a Soundness error of

1

/

2

1/2





1/2
, we can then repeat the protocol

t

t





t
number of times, to bootstrap this soundness error to

2


−

t

2^{-t}






2










−

t
until it is negligible in the security parameter.
  
  
These types of protocols are generally based around making the prover commit to some information, then being asked to do one of two actions based on what he committed to, where a prover who can answer both challenges must know the witness. While the previous

Σ

\Sigma





Σ
-Protocols we looked at were only easily realisable for problems with certain types of structure, this new technique lets us start doing zero knowledge for a huge range of types of relations.
  
  
The

Σ

\Sigma





Σ
-Protocol we are going to look at now is a

Σ

\Sigma





Σ
-Protocol for proving that a given graph includes a Hamiltonian cycle. A Hamiltonian cycle is a path through a graph which visits each node exactly once, ending at the same node which it started at.
  
  


The reason this specific protocol is interesting is because the problem of finding if a graph has a Hamiltonian cycle is part of a class of decision problems called NP-Complete. To handwave some complexity theory, this implies that any problem in NP can be embedded into an instance of the Hamiltonian cycle problem.
  
This is a very important result, because it means that if we have a

Σ

\Sigma





Σ
-Protocol for proving knowledge of a Hamiltonian cycle in a graph, we by extension have a

Σ

\Sigma





Σ
-Protocol for ANY relation in NP!
  
  
  
The protocol runs as follows, for Prover P and Verifier V, with public input graph

G

G





G
with

N

N





N
nodes, and private input

w

w





w
being a Hamiltonian cycle in

G

G





G
.
  
  

1. P encodes

   G

   G





   G
   as a

   N

   ×

   N

   N \times N





   N



   ×





   N
   matrix, where

   1

   1





   1
   at index

   (

   i

   ,

   j

   )

   (i,j)





   (

   i

   ,



   j

   )
   signifies that

   G

   G





   G
   has an edge going from node

   i

   i





   i
   to node

   j

   j





   j
   , while

   0

   0





   0
   signifies no such edge.
2. P commits to each entry in

   G

   G





   G
   using an information theoretically hiding commitment, we call this

   G

   ′

   G'






   G










   ′
3. P samples a random permutation

   perm

   \texttt{perm}






   perm
   and applies this permutation to each row and column of the

   G

   ′

   G'






   G










   ′
4. P sends

   a

   =


   G

   ′

   a = G'





   a



   =






   G










   ′
   to V
5. V samples a challenge random bit

   e

   ′

   e'






   e










   ′
   , and sends it to P
6. If

   e

   =

   1

   e = 1





   e



   =





   1
   :

* P computes the cycle in

  G

  ′

  G'






  G










  ′
  , denoted

  cycle

  ′

  \texttt{cycle}'







  cycle










  ′
  by applying

  perm

  \texttt{perm}






  perm
  to the cycle

  w

  w





  w
* P sets

  openings

  \texttt{openings}






  openings
  to the randomness needed to open only the commitments on this cycle
* P sets

  z

  =

  (


  cycle

  ′

  ,

  openings

  )

  z = (\texttt{cycle}', \texttt{openings})





  z



  =





  (



  cycle










  ′

  ,




  openings

  )

7. If

   e

   =

   0

   e = 0





   e



   =





   0
   :

* P sets

  openings

  \texttt{openings}






  openings
  to the randomness needed to open every entry in

  G

  ′

  G'






  G










  ′
* P sets

  z

  =

  (

  perm

  ,

  openings

  )

  z = (\texttt{perm}, \texttt{openings})





  z



  =





  (


  perm

  ,




  openings

  )

8. P sends

   z

   z





   z
   to V
9. If

   e

   =

   1

   e = 1





   e



   =





   1
   :

* V checks that

  cycle

  ′

  \texttt{cycle}'







  cycle










  ′
  is a Hamiltonian path in

  G

  ′

  G'






  G










  ′
* V uses

  openings

  \texttt{openings}






  openings
  to verify that all edges in the cycle are commitments to

  1

  1





  1
* If both satisfy, V returns \top, otherwise \bot

10. If

    e

    =

    0

    e = 0





    e



    =





    0
    :

* V applies

  perm

  \texttt{perm}






  perm
  to

  G

  G





  G
  to get

  G


  ′

  ′

  G''






  G










  ′′
* V uses

  openings

  \texttt{openings}






  openings
  to open every entry in

  G

  ′

  G'






  G










  ′
* If

  G

  ′

  =


  G


  ′

  ′

  G' = G''






  G










  ′



  =






  G










  ′′
  , V returns \top, otherwise \bot

  
  
Here is an (informal) argument for why this is a

Σ

\Sigma





Σ
-Protocol. For a more formal treatment, see
[Lecture notes by Damgård](https://cs.au.dk/%7Eivan/CPT1.pdf)
.
  
  

1. 3 move form: The protocol has the

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
   form, where

   e

   e





   e
   is a random (1) bit string
2. Correctness: By inspection of the protocol, if P knows

   w

   w





   w
   and follows the protocol, an honest V should always accept
3. Special Soundness: Given accepting transcripts

   (

   a

   ,

   0

   ,

   z

   )

   ,

   (

   a

   ,

   1

   ,


   z

   ′

   )

   (a,0,z),(a,1,z')





   (

   a

   ,



   0

   ,



   z

   )

   ,



   (

   a

   ,



   1

   ,




   z










   ′

   )
   : Note

   z

   ′

   z'






   z










   ′
   gives us

   w

   w





   w
   which is a Hamiltonian cycle in

   G

   ′

   G'






   G










   ′
   , and

   z

   z





   z
   gives us the permutation

   G

   −

   >


   G

   ′

   G -> G'





   G

   −



   >






   G










   ′
   . We can simply invert the permutation to get a

   w

   ′

   w'






   w










   ′
   which is a Hamiltonian cycle in

   G

   G





   G
4. SHVZK: Basic simulator idea is: given

   (

   G

   ,

   [


   e

   0

   ,


   e

   1

   .

   .

   .

   .


   e

   t

   ]

   )

   (G,[e\_{0}, e\_{1}....e\_{t}])





   (

   G

   ,



   [


   e










   0

   ​


   ,




   e










   1

   ​


   ....


   e










   t

   ​


   ])
5. for

   i

   i





   i
   in range(

   t

   t





   t
   )

1. Sample random bit

   e

   ′

   e'






   e










   ′
2. if

   e

   ′

   =

   0

   e' = 0






   e










   ′



   =





   0
   : commit to a random permutation of G and set this as

   a

   a





   a
3. if

   e

   ′

   =

   1

   e' = 1






   e










   ′



   =





   1
   : commit to a random graph

   G

   2

   G\_2






   G









   2

   ​

   which you know a Hamiltonian cycle in as

   a

   a





   a
4. if

   e

   =


   e

   ′

   e = e'





   e



   =






   e










   ′
   , generate a satisfying

   z

   z





   z
   (either open to

   G

   G





   G
   , or open only the cycle you know in

   G

   2

   G\_2






   G









   2

   ​

   ),

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
   is a satisfying transcript
5. Otherwise if

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
   , rewind to step 1

  
  
This challenge is about a Fiat-Shamir'd implementation of this protocol. To get the flag you need to convince the server that you know a Hamiltonian cycle in graph

G

G





G
, despite

G

G





G

NOT
having such a cycle. (Thereby breaking special soundness, and therefore soundness.)
  
  


Hint: Look at how the fiat shamir is implemented, something seems fishy...
  
  


As this protocol is somewhat complicated, we have included the script
`example.py`
, which uses the
`pwntools process()`
function to locally run the challenge.
  
  
This script will run the Prover side protocol honestly, to give you a starting point. And it will successfully solve the challenge when

G

G





G
is set to a graph which has a Hamiltonian, which the prover knows!
  
  
Such a graph has been included in the challenge file, but will only be used by the verifier if the "LocalTest" boolean is set to True, so to locally test out the protocol you can set this to True, and run example.py to get the local flag!
  
  
**This challenge is hosted on the CTF archive. Find the corresponding challenge in that category, solve it, then enter the flag here.**
  
  
Challenge contributed by
[killerdog](/user/killerdog)
