# Discrete Algebraic Inversion & Operator Identification Problem

We consider an unknown composite discrete transformation $T_i: \mathbb{Z}_{256} \to \mathbb{Z}_{256}$ parametrized by index $i \in \{0, \dots, 23\}$.

We have two known vectors of 24 integers in $\mathbb{Z}_{256}$:
- Vector $X = [x_0, x_1, \dots, x_{23}]$
- Vector $Y = [y_0, y_1, \dots, y_{23}]$

The transformation applied at each step $i$ is a sequence of 4 elementary operations:
$$v^{(0)} = x_i$$
$$v^{(1)} = \phi_1(v^{(0)}, i)$$
$$v^{(2)} = \phi_2(v^{(1)}, 255)$$
$$v^{(3)} = \phi_3(v^{(2)}, 67)$$
$$v^{(4)} = \phi_4(v^{(3)}, 4)$$
$$y_i = v^{(4)}$$

Where each $\phi_k(v, c)$ is chosen from standard discrete byte-level operations:
1. Addition / Subtraction modulo 256: $(v + c) \bmod 256$, $(v - c) \bmod 256$, $(c - v) \bmod 256$
2. Bitwise XOR: $v \oplus c$
3. Bitwise Rotations: $\text{ROL}(v, c)$, $\text{ROR}(v, c)$
4. Multiplicative inversions modulo 256: $(v \cdot c) \bmod 256$ (when $\gcd(c, 256) = 1$)
5. Bitwise NOT: $\sim v \bmod 256$ (equivalent to $v \oplus 255$)
6. Nibble swapping / modular shifts.

## Goal
Identify the exact operator tuple $(\phi_1, \phi_2, \phi_3, \phi_4)$ that satisfies $y_i = T_i(x_i)$ for all $i \in \{0, \dots, 23\}$, or determine if an alternative mapping exists.
Produce a Python script `solve_system.py` in the workspace to output the confirmed operator mapping.
