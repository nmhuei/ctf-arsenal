import numpy as np

data = np.memmap('challenge/Sideband_Surgery/challenge.raw', dtype=np.complex64, mode='r')
seg_len = 9338400

m0 = data[0*seg_len : 1*seg_len].real - 0.5
m2 = data[2*seg_len : 3*seg_len].real
m3 = data[3*seg_len : 4*seg_len].real

step = 200000
for i in range(0, seg_len - step, step):
    c02 = np.corrcoef(m0[i:i+step], m2[i:i+step])[0, 1]
    c03 = np.corrcoef(m0[i:i+step], m3[i:i+step])[0, 1]
    c23 = np.corrcoef(m2[i:i+step], m3[i:i+step])[0, 1]
    var0 = np.var(m0[i:i+step])
    var2 = np.var(m2[i:i+step])
    var3 = np.var(m3[i:i+step])
    print(f"[{i:7d}..{i+step:7d}] var=(v0:{var0:.4f}, v2:{var2:.4f}, v3:{var3:.4f})  corr(0,2)={c02:+.3f}  corr(0,3)={c03:+.3f}  corr(2,3)={c23:+.3f}")
