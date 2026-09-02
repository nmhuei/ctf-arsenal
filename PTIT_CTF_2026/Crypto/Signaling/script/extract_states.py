import cv2
import numpy as np
import os

cap = cv2.VideoCapture('challenge/Signaling/Signaling.mp4')
frames = []
while True:
    ret, frame = cap.read()
    if not ret:
        break
    frames.append(frame)
cap.release()

os.makedirs('script/states', exist_ok=True)

# Let's inspect steady frames:
# Frame 20 is the initial state (or frame 0..36)
# Then starting from frame 43, steps of 10 frames: 43, 53, 63, ...
steady_indices = [20]
idx = 43
while idx < len(frames):
    steady_indices.append(idx)
    idx += 10

print(f"Number of states: {len(steady_indices)}")
print(f"Indices: {steady_indices}")

for i, s_idx in enumerate(steady_indices):
    cv2.imwrite(f'script/states/state_{i:02d}_frame_{s_idx:03d}.png', frames[s_idx])

