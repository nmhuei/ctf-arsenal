# Bad Apple 3 – local writeup notes

## 1. Recon

The uploaded file is a 1920×1080, 60 FPS, ~325 s MP4. Individual frames look like random black/white maze noise, so normal screenshots are not useful.

```bash
ffprobe -v error -show_entries format=duration,size,bit_rate \
  -show_streams -of json 'tao_den(10).mp4'
```

Useful crop: the actual content is centered; black side bars can be removed with `crop=1440:1080:240:0`.

## 2. Reveal the Bad Apple layer

Average or variance over short chunks cancels much of the per-frame maze/noise and reveals the hidden Bad Apple animation.

```bash
mkdir frames
ffmpeg -i 'tao_den(10).mp4' \
  -vf "crop=1440:1080:240:0,scale=720:540,fps=30" \
  frames/f_%05d.png
```

Then compute chunk mean/std/diff over windows of about 1–5 seconds. The mean/std maps show the animation silhouette.

Python skeleton:

```python
import cv2, numpy as np
from PIL import Image

video = 'tao_den(10).mp4'
cap = cv2.VideoCapture(video)
fps = cap.get(cv2.CAP_PROP_FPS)
chunk = int(fps * 5)
frames = []
idx = 0

while True:
    ok, frame = cap.read()
    if not ok:
        break
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)[:, 240:1680]
    gray = cv2.resize(gray, (720, 540))
    frames.append(gray.astype(np.float32))
    if len(frames) == chunk:
        arr = np.stack(frames)
        mean = arr.mean(axis=0)
        std = arr.std(axis=0)
        for name, img in [('mean', mean), ('std', std)]:
            lo, hi = np.percentile(img, [1, 99])
            out = np.clip((img - lo) / (hi - lo + 1e-9) * 255, 0, 255).astype(np.uint8)
            Image.fromarray(out).save(f'{name}_{idx:03d}.png')
        frames.clear()
        idx += 1
```

## 3. Reproduce the YouTube seek-bar clue locally

Use a custom scrubber with frame stepping. The included HTML file lets you load the MP4 locally, drag the timeline, step frame-by-frame with `,` and `.`, and optionally enable persistence/alpha blending to make moving hidden text easier to see.

Open `bad_apple3_scrubber.html`, choose `tao_den(10).mp4`, then scrub slowly. Use persistence mode when the text is visible only through motion.

## 4. Extra analysis route

If the message is only visible as motion, build kymographs/time-slices. For example, take a vertical stripe from each frame and stack it over time:

```python
# arr shape: frame_count × height × width, grayscale
x = 360
stripe = arr[:, :, x-3:x+4].mean(axis=2)  # frame_count × height
kymo = stripe.T                              # height × time
Image.fromarray(kymo.astype('uint8')).save('kymograph.png')
```

Repeat for multiple `x` positions, and also try horizontal stripes if the text moves vertically.

## Current status

I could verify the hidden Bad Apple layer from local processing. I cannot verify or quote an online writeup from here because web search is disabled in this session.
