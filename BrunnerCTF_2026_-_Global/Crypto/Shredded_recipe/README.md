# Shredded recipe

| Property | Value |
| :--- | :--- |
| **Category** | `Crypto` |
| **Points** | `100` |
| **Solves** | 250 |

## 📝 Description

**Difficulty:** Hard  
**Author:** Vincent  

Brunnerne Inc. just released their new revolutionary and innovating cake: The *citronkvartmåne* - a new, never before seen cost-saving take on the classic *citronhalvmåne*.

However, they shredded and burned the recipe.
We think they may be hiding something with that cake.

I even heard that they might be cutting the citronhalvmåne in half and selling it at a markup.
Can you get to the bottom of this and retrieve the recipe?


## 📦 Files & Resources

| File / Resource | Source | Status | Local Path / URL |
| :--- | :--- | :--- | :--- |
| `crypto_shredded-recipe.zip` | `platform_attachment` | ✅ Downloaded | [crypto_shredded-recipe.zip](crypto_shredded-recipe.zip) |

## 🚩 Flag & Solution

- [x] Solved

```
brunner{i_really_love_solving_equations_with_lattices}
```

### Writeup / Notes

Solved using SageMath LLL with Kannan embedding on the 5x5 lattice matrix:
`M = Matrix(ZZ, [[S*p, 0, 0, 0, 0], [S*a, 1, 0, 0, 0], [S*b, 0, 1, 0, 0], [S*c, 0, 0, 1, 0], [S*(-d), 0, 0, 0, X]])` where `S = 2^368`, `X = 2^144`.
