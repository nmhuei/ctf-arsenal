import cv2
import numpy as np
import os

cap = cv2.VideoCapture('challenge/Signaling/Signaling.mp4')
fps = cap.get(cv2.CAP_PROP_FPS)
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
duration = total_frames / fps

print(f"FPS: {fps}, Total frames: {total_frames}, Size: {width}x{height}, Duration: {duration}s")

os.makedirs('script/all_frames', exist_ok=True)
prev_frame = None
frame_idx = 0
saved_idx = 0

frames_data = []

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    if prev_frame is None:
        cv2.imwrite(f'script/all_frames/frame_{frame_idx:04d}.png', frame)
        saved_idx += 1
        prev_frame = frame
        frames_data.append((frame_idx, frame_idx/fps))
    else:
        diff = cv2.absdiff(frame, prev_frame)
        diff_mean = np.mean(diff)
        if diff_mean > 2.0:
            cv2.imwrite(f'script/all_frames/frame_{frame_idx:04d}.png', frame)
            saved_idx += 1
            prev_frame = frame
            frames_data.append((frame_idx, frame_idx/fps, diff_mean))
    frame_idx += 1

cap.release()
print(f"Saved {saved_idx} distinct frames.")
for f in frames_data[:30]:
    print(f)
if len(frames_data) > 30:
    print(f"... and {len(frames_data) - 30} more")
