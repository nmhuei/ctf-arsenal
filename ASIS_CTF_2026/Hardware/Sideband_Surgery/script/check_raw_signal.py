import numpy as np

data = np.memmap('challenge/Sideband_Surgery/challenge.raw', dtype=np.complex64, mode='r')
seg_len = 9338400

m0 = data[:seg_len].real - 0.5
m1 = data[1*seg_len:2*seg_len] # FM
m2 = data[2*seg_len:3*seg_len].real # LSB
m3 = data[3*seg_len:4*seg_len].real # USB

# Let's check: in decoded_seg0, the left side is at x in [50, 100]
# That corresponds to the beginning of the Y scan:
# Line 90 to 140
# In decode_robot36, for line 100 (which had the finder in seg3):
# Let's check what filt_freq was in m0 vs m3 during that line!
