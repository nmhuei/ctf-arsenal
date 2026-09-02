Before beginning this section you should have attempted many of the challenges in the "Elliptic Curves" section and completed the starter challenges.
  
  
Welcome to the isogeny section of cryptohack!
  
  


Disclaimer: throughout the following challenges there will be (at times) slightly relaxed notation / statements. Sometimes this will be an accident and the challenges may be modified and improved over time. Other times it will be done on purpose with the hope of losing some mathematical rigour in the description with the hope to build intuition. We're aware that not everyone likes learning this way, but a more formal education of isogenies are available from textbooks and lecture notes which we link throughout.
  
  
Isogenies between elliptic curves, at their heart, are two things. Firstly, they are rational maps between elliptic curves (a surjective morphism). They don't just map between curves though, they also preserve the group structure from the domain to the codomain of the map. This means they are also group homomorphisms (they are a non-constant rational map which fixes the point at infinity). We denote an isogeny

ϕ

\phi





ϕ
with domain

E

E





E
and codomain

E

′

E'






E










′
as

ϕ

:

E

→


E

′

\phi : E \to E'





ϕ



:





E



→






E










′
.
  
  
For most of what follows, we will be concerned with separable isogenies, for which the degree of the map is exactly equal to the size of the kernel (the kernel is the set of points on the domain mapped to the point at infinity on the codomain). The mathematics of isogenies extends far beyond cryptographic applications (and certainly beyond these sets of challenges), but generally we will want to do two things. The first is given a subgroup

H

H





H
of points, we will want to be able to compute an isogeny with kernel

H

H





H
(and so of degree

#

H

\#H





#

H
). The second thing we will want to do is to take any point on the domain and evaluate the isogeny at this point to find a corresponding point on the codomain. If you can do these two things, you can implement most of what you need for isogeny-based cryptography (narrator: this is dramatically over-simplified).
  
  
Understanding
why
we do certain combinations of these calculations and why we consider them useful for asymmetric cryptography is much more complicated. We hope a small amount of intuition comes from solving these challenges but let us also discuss a little bit about what we think is a hard problem in isogeny based cryptography and what problems we have efficient solutions for.
  
  
The cryptographic side of isogenies comes from considering long paths of isogenies between many different elliptic curves. If we fix some prime

ℓ

\ell





ℓ
, then the

ℓ

\ell





ℓ
-isogeny graph is a graph whose vertices are (isomorphism classes) of elliptic curves and the edges are isogenies of degree

ℓ

\ell





ℓ
(the polynomials appearing in the rational map have maximum degree

ℓ

\ell





ℓ
). Generally, when we consider the isogeny graphs of supersingular elliptic curves, we end up with a horrible mess of a graph, where you can take relatively short walks through the graph and get totally lost (this is true for SIDH, but for CSIDH we restrict to a special set of isogenies and the graphs have more structure and look more beautiful).
  
  
When

ℓ

\ell





ℓ
is small, we can compute an

ℓ

\ell





ℓ
-isogeny efficiently. We can walk through the graph by computing many

ℓ

\ell





ℓ
-isogenies and end up on some vertex. The idea of isogeny-based cryptography is to use this path of isogenies as a secret key and the start and end nodes as a public key. Protocols are built by taking secret walks between curves, exchanging these curves (and sometimes additional data) and then repeating this walk to end up on a shared secret vertex on the graph for which no one else knows. This vertex can then be used to create symmetric keys just like secret points on elliptic curves can be used in the ECDH key exchange.
  
  
In this series of challenges you will first learn a few background tricks before setting out to implement two key exchange protocols: SIDH and CSIDH. The last challenges in the section are more CTF-like and should give you some fun isogeny-based puzzles to get additional experience and intuition for working with these maps. There are many other isogeny-based cryptographic primatives (such as SQIsign, the CGL hash function and more exotic things like verifiable delay functions). Introductions to these topics may appear at a later date.
  
  
There are two ways we think you can approach solving the following challenges. For those who want to get a surface level understanding, a great way to start is to try and solve the challenges using all the various functions available in SageMath. This will avoid needing to worry about the gritty details of isogenies and algebraic geometry and should get you some practical experience useful for solving CTF challenges.
  
  
Alternatively, we have tried to include as many resources as we can through the starter challenges. For a focused student, these should set you on the right path to really appreciate the subject and give practical experience with the engineering required to compute isogenies efficiently. Of course another option is to do both! Work with SageMath to verify your understanding and then start coding things yourself.
  
  


If you use Discord, then the channel #isogeny-school (
[Discord Invite](https://discord.gg/h9E7cna5pV)
) is a great place to ask for more details about isogeny based cryptography. We hope to see you there!
  
  
Below are a few general resources which we found useful ourselves while learning about this subject. Specific resources are also attached to challenges so don't feel like you need to read all of the below before starting — dive in!
  
  
For the flag of this wall of text, what would the size of a kernel be for a separable isogeny of degree 65537?
  
  
**Resources:**
  
-
[Mathematics of Isogeny Based Crypto, Luca De Feo, Marc Houben](https://github.com/defeo/MathematicsOfIBC/blob/popayan-temp/poly.pdf)
  
-
[Elliptic Curves, Lecture Notes, Andrew Sutherland](https://ocw.mit.edu/courses/18-783-elliptic-curves-spring-2021/pages/lecture-notes-and-worksheets/)
  
-
[Cryptography on Isogeny Graphs, Lorenz Panny](https://yx7.cc/docs/phd/thesis.pdf)
  
-
[Supersingular isogeny key exchange for beginners, Craig Costello](https://eprint.iacr.org/2019/1321)
