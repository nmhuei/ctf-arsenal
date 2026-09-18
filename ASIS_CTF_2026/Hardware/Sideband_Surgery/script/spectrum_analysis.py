import numpy as np

data = np.memmap('challenge/Sideband_Surgery/challenge.raw', dtype=np.complex64, mode='r')

seg_len = 9338400

for seg_idx in range(4):
    seg = data[seg_idx*seg_len : (seg_idx+1)*seg_len]
    # Take 2^20 samples from middle
    N = 1048576
    start = seg_len // 2
    chunk = seg[start : start + N]
    
    # Compute FFT
    spectrum = np.fft.fftshift(np.fft.fft(chunk))
    psd = 10 * np.log10(np.abs(spectrum)**2 + 1e-12)
    freqs = np.fft.fftshift(np.fft.fftfreq(N))
    
    # Top 5 peaks
    top_indices = np.argsort(psd)[-10:][::-1]
    print(f"=== Segment {seg_idx} top PSD peaks ===")
    for idx in top_indices:
        print(f"  f/fs = {freqs[idx]:.6f}, PSD = {psd[idx]:.2f} dB")
    
    # Overall frequency band: where is 99% of energy?
    total_energy = np.sum(np.abs(spectrum)**2)
    cum_energy = np.cumsum(np.abs(spectrum)**2) / total_energy
    f_low = freqs[np.searchsorted(cum_energy, 0.005)]
    f_high = freqs[np.searchsorted(cum_energy, 0.995)]
    print(f"  99% energy band: [{f_low:.6f}, {f_high:.6f}]")
