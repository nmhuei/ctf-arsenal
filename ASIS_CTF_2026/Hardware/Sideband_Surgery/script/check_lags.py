import numpy as np
import scipy.signal

data = np.memmap('challenge/Sideband_Surgery/challenge.raw', dtype=np.complex64, mode='r')
seg_len = 9338400

m0 = data[0*seg_len : 1*seg_len].real - 0.5
m2 = data[2*seg_len : 3*seg_len].real
m3 = data[3*seg_len : 4*seg_len].real

# Let's test at several points: 1M, 3.5M, 4M, 5M, 6M, 7M, 8M
for test_idx in [1000000, 3500000, 3700000, 4000000, 5000000, 6000000, 7000000, 8000000]:
    N = 20000
    chunk0 = m0[test_idx : test_idx + N]
    chunk2 = m2[test_idx - 5000 : test_idx + N + 5000]
    chunk3 = m3[test_idx - 5000 : test_idx + N + 5000]
    
    corr02 = scipy.signal.correlate(chunk2, chunk0, mode='valid')
    lags02 = np.arange(-5000, 5001)
    best_lag02 = lags02[np.argmax(corr02)]
    max_c02 = np.max(corr02) / (np.linalg.norm(chunk0) * np.linalg.norm(chunk2[best_lag02+5000 : best_lag02+5000+N]))
    
    corr03 = scipy.signal.correlate(chunk3, chunk0, mode='valid')
    best_lag03 = lags02[np.argmax(corr03)]
    max_c03 = np.max(corr03) / (np.linalg.norm(chunk0) * np.linalg.norm(chunk3[best_lag03+5000 : best_lag03+5000+N]))
    
    print(f"Index {test_idx:7d}:")
    print(f"  m0 vs m2: best lag = {best_lag02:+5d}, max corr = {max_c02:.4f}")
    print(f"  m0 vs m3: best lag = {best_lag03:+5d}, max corr = {max_c03:.4f}")
