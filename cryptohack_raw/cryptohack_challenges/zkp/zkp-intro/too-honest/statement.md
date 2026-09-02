Recall that we only proved Schnorr's protocol to be SHVZK, and while this was enough to make maliciously secure NIZK's, this leaves the question of "what could happen if V isn't honest?"
  
  
This challenge is an implementation of Girault's identification protocol for proving knowledge of a witness for a DLOG relation, but modulo some composite

N

N





N
instead of a prime.
  
  
You are the verifier, and the prover will show that they know the flag using an interactive

Σ

\Sigma





Σ
-Protocol. Extract the flag by selecting a malicious

e

e





e
.
  
  


Note that proving something to be a

Σ

\Sigma





Σ
-Protocol only makes it secure against an "honest" verifier. If we want to use a protocol in a setting where the verifier can't be trusted to be honest, you can either make the proof non-interactive, or convert the SHVZK protocol into a maliciously secure ZK protocol, (there exist generic transformations which generally add another round of interaction.)
  
  
Connect at
`socket.cryptohack.org 13429`
  
  
**Challenge files:**
  
-
[13429.py](/static/challenges/13429_2520b4ebce10bd8b830bc5dc3d67da2b.py)
  
  
  
Challenge contributed by
[oberon](/user/oberon)
