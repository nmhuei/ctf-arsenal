In the last challenge we showed how
*not*
to do the Fiat-Shamir transform for a multi-round

Σ

\Sigma





Σ
-Protocol. This time we've been a little bit more careful and implemented iterated Fiat-Shamir hashing properly.
  
  
Can you break it again?
  
  


As this protocol is somewhat complicated, we have included the script
`example.py`
, which uses the
`pwntools process()`
function to locally run the challenge.
  
  
This script will run the Prover side protocol honestly, to give you a starting point. And it will successfully solve the challenge when

G

G





G
is set to a graph which has a Hamiltonian cycle, which the prover knows!
  
  
Such a graph has been included in the challenge file, but will only be used by the verifier if the "LocalTest" boolean is set to True, so to locally test out the protocol you can set this to True, and run

e

x

a

m

p

l

e

.

p

y

example.py





e

x

am

pl

e

.

p

y
to get the local flag!
  
  
**This challenge is hosted on the CTF archive. Find the corresponding challenge in that category, solve it, then enter the flag here.**
  
  
Challenge contributed by
[killerdog](/user/killerdog)
and
[Lance Roy](#)
