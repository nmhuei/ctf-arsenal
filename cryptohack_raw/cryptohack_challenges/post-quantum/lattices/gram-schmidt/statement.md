In the last challenge we saw that there is a special kind of basis called an orthogonal basis. Given a basis

v

1

,


v

2

,

…

,


v

n

∈

V

v\_{1}, v\_{2}, \ldots, v\_{n} \in V






v










1

​


,




v










2

​


,



…



,




v










n

​




∈





V
for a vector space, the Gram-Schmidt algorithm calculates an orthogonal basis

u

1

,


u

2

,

…

,


u

n

∈

V

u\_{1}, u\_{2}, \ldots, u\_{n} \in V






u










1

​


,




u










2

​


,



…



,




u










n

​




∈





V
.
  
  
In "An Introduction to Mathematical Cryptography",
*Jeffrey Hoffstein, Jill Pipher, Joseph H. Silverman*
, the Gram-Schmidt algorithm is given as:
  
  

**Algorithm for Gram-Schmidt**
  
  








u

1

=


v

1

u\_{1} = v\_{1}






u










1

​




=






v










1

​

  
Loop

i

=

2

,

3

…

,

n

i = 2,3\ldots,n





i



=





2

,



3



…



,



n
  
Compute

μ


i

j

=


v

i

⋅


u

j

/

∣

∣


u

j

∣


∣

2

,

1

≤

j

<

i

\mu\_{ij} = v\_{i} \cdot u\_{j} / ||u\_{j}||^2, 1 \leq j < i






μ










ij

​




=






v










i

​




⋅






u










j

​


/∣∣


u










j

​


∣


∣









2

,



1



≤





j



<





i
.
  
Set

u

i

=


v

i

−


μ


i

j

⋅


u

j

u\_{i} = v\_{i} - \mu\_{ij} \cdot u\_{j}






u










i

​




=






v










i

​




−






μ










ij

​




⋅






u










j

​

(Sum over

j

j





j
for

1

≤

j

<

i

1 \leq j < i





1



≤





j



<





i
)
  
End Loop
  
  
  
To test your code, let's grab the flag. Given the following basis vectors:
  
  









v

1

=

(

4

,

1

,

3

,

−

1

)

,


v

2

=

(

2

,

1

,

−

3

,

4

)

,


v

3

=

(

1

,

0

,

−

2

,

7

)

,


v

4

=

(

6

,

2

,

9

,

−

5

)

v\_{1} = (4,1,3,-1), \;\; v\_{2} = (2,1,-3,4), \;\; v\_{3} = (1,0,-2,7), \;\; v\_{4} = (6, 2, 9, -5)






v










1

​




=





(

4

,



1

,



3

,



−

1

)

,








v










2

​




=





(

2

,



1

,



−

3

,



4

)

,








v










3

​




=





(

1

,



0

,



−

2

,



7

)

,








v










4

​




=





(

6

,



2

,



9

,



−

5

)
.
  
  
use the Gram-Schmidt algorithm to calculate an orthogonal basis. The flag is the float value of the second component of

u

4

u\_{4}






u










4

​

to 5 significant figures.
  
  


Note that this algorithm doesn't create an ortho
*normal*
basis! It's a small change to implement this. Think about what you would have to change. If you're using someone else's algorithm and the flag is incorrect, this might be the issue. If everything seems good and you're still not having your answer accepted, check your rounding when you take 5.s.f. for the solution.
