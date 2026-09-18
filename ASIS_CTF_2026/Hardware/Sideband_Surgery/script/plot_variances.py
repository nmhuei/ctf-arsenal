import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

data = np.memmap('challenge/Sideband_Surgery/challenge.raw', dtype=np.complex64, mode='r')
seg_len = 9338400

# Demodulate all 4 segments:
# m0: real - 0.5
m0 = data[0*seg_len : 1*seg_len].real - 0.5

# m1: FM freq dev
seg1 = data[1*seg_len : 2*seg_len]
m1 = np.diff(np.unwrap(np.angle(seg1))) / (2 * np.pi)
m1 = np.append(m1, m1[-1])

# m2: LSB (take real)
m2 = data[2*seg_len : 3*seg_len].real

# m3: USB (take real)
m3 = data[3*seg_len : 4*seg_len].real

# Let's check the power/envelope of m0, m1, m2, m3 in chunks of 50000 samples
chunk_size = 50000
n_chunks = seg_len // chunk_size

t_axis = np.arange(n_chunks) * (chunk_size / 240000)

p0 = [np.var(m0[i*chunk_size : (i+1)*chunk_size]) for i in range(n_chunks)]
p1 = [np.var(m1[i*chunk_size : (i+1)*chunk_size]) for i in range(n_chunks)]
p2 = [np.var(m2[i*chunk_size : (i+1)*chunk_size]) for i in range(n_chunks)]
p3 = [np.var(m3[i*chunk_size : (i+1)*chunk_size]) for i in range(n_chunks)]

plt.figure(figsize=(14, 8))
plt.subplot(4, 1, 1)
plt.plot(t_axis, p0, label='m0 (AM)')
plt.ylabel('Var')
plt.title('Variance over time for m0, m1, m2, m3')
plt.grid(True)

plt.subplot(4, 1, 2)
plt.plot(t_axis, p1, label='m1 (FM)', color='orange')
plt.ylabel('Var')
plt.grid(True)

plt.subplot(4, 1, 3)
plt.plot(t_axis, p2, label='m2 (LSB)', color='green')
plt.ylabel('Var')
plt.grid(True)

plt.subplot(4, 1, 4)
plt.plot(t_axis, p3, label='m3 (USB)', color='red')
plt.ylabel('Var')
plt.xlabel('Time (s)')
plt.grid(True)

plt.tight_layout()
plt.savefig('script/variances.png', dpi=150)
plt.close()
print("Saved script/variances.png")
