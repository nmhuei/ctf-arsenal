import cv2
import numpy as np

cap = cv2.VideoCapture('challenge/Signaling/Signaling.mp4')
fps = cap.get(cv2.CAP_PROP_FPS)
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

diffs = []
prev = None
frames = []

while True:
    ret, frame = cap.read()
    if not ret:
        break
    if prev is not None:
        diff = np.mean(cv2.absdiff(frame, prev))
        diffs.append(diff)
    else:
        diffs.append(0)
    prev = frame
    frames.append(frame)

cap.release()

print(f"Total frames: {len(frames)}")

# Let's find stationary periods (where diff is low, e.g. < 0.5)
stationary_frames = []
for i, d in enumerate(diffs):
    # check if i is a local minimum or diffs[i] < 0.1
    pass

import matplotlib.pyplot as plt

# Let's see diffs per frame
for i in range(0, min(100, len(diffs))):
    print(f"Frame {i:3d}: diff={diffs[i]:.3f}")

