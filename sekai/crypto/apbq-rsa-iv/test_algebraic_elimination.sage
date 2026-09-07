import sympy as sp

p, q = sp.symbols('p q')
a0, a1, a2 = sp.symbols('a0 a1 a2')
b0, b1, b2 = sp.symbols('b0 b1 b2')
n = p * q

h0 = a0*p + b0*q
h1 = a1*p + b1*q
h2 = a2*p + b2*q

A0 = a0*b0
A1 = a1*b1
A2 = a2*b2

d01 = a0*b1 - a1*b0
d02 = a0*b2 - a2*b0
d12 = a1*b2 - a2*b1

# Master linear relation:
# h1*h2*d12*A0 - h0*h2*d02*A1 + h0*h1*d01*A2 + n*d01*d02*d12 = 0
# And we have:
# T0*T1 = h2^2*A0*A1 + n*A2*d01^2
# where T0 = (h1*h2*A0 + n*d01*d02)/h0, T1 = (h0*h2*A1 - n*d01*d12)/h1

print("Algebraic system initialized!")
