load('test_all_quad_kernel.sage')

# Root:
a_val = -20166902895871906608985532196863568493294924112419716727766293785798470105605753776298615145306195994555971
b_val = 62808042341278115552926401834523733164409046005808515554251469158592792749495624069149796560440638811133949

x_sol = a_val * r0 + b_val * r1
sign = 1 if x_sol[0] > 0 else -1
x1, x2, x3, x4, x5 = [sign * x for x in x_sol]

w1 = ZZ(isqrt(x1))
w2 = ZZ(isqrt(x2))

print("x1 == w1^2:", x1 == w1^2)
print("x2 == w2^2:", x2 == w2^2)

# w0:
w0_from_x3 = x3 / w1
w0_from_x4 = x4 / (x5 / w1)

print("w0_from_x3 == w0_from_x4:", w0_from_x3 == w0_from_x4)
print("w0 from x3:", w0_from_x3)
