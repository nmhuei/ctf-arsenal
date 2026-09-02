The SIDH protocol is a great way to learn some of the machinery of isogeny-based cryptography, but in 2022 it was shown to be broken in polynomial time by a series of papers (the paper by Castryck and Decru appeared online first, only a week before the following two papers which further broke more general protocols).
  
  
Given only the public data of an SIDH protocol can you recover the shared secret and decrypt the flag?
  
  


You may notice the prime used here:

p

=

45

⋅


2

117

⋅


3

73

−

1

p = 45 \cdot 2^{117} \cdot 3^{73} - 1





p



=





45



⋅






2










117



⋅






3










73



−





1
is different to the previous challenges. This has been done on purpose to simplify the attack! Read the resources and you should see why.
  
  


Setting the score for this challenge is very hard. The whole attack implemented without help is very challenging and was first done in SageMath as a team effort in our discord chat (see the resources below). On the other hand, there's now a few different implementations of the attack on GitHub which do a lot of the work for you. Our advice here is to spend as much time as you want on this project and if you rely on tools for the flag, maybe come back another day and try implementing certain steps yourself. It's a beautiful topic and the main reason I (Jack) am so interested in the topic today. It's also the cornerstone of many new advanced isogeny primitives such as SQIsign2D, FESTA and SCALLOP-HD.
  
  
**Challenge files:**
  
-
[source.sage](/static/challenges/source_0e46e87ca6110ad062f6ce1819ded232.sage)
  
  
**Resources:**
  
-
[An efficient key recovery attack on SIDH, Wouter Castryck, Thomas Decru](https://eprint.iacr.org/2022/975)
  
-
[A Direct Key Recovery Attack on SIDH, Luciano Maino, Chloe Martindale, Lorenz Panny, Giacomo Pope, Benjamin Wesolowski](https://eprint.iacr.org/2023/640)
  
-
[Breaking SIDH in polynomial time, Damien Robert](https://eprint.iacr.org/2022/1038)
  
-
[A Note on Reimplementing the Castryck-Decru Attack and Lessons Learned for SageMath, Rémy Oudompheng, Giacomo Pope](https://eprint.iacr.org/2022/1283)
  
-
[You could have broken SIDH, Lorenz Panny](https://yx7.cc/blah/2022-08-22.html)
