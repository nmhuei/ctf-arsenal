#!/usr/bin/env python3
"""End-to-End Solver for Residuegate (CSCV 2026 Quals)

Author: Automated Agent Architecture
"""

import argparse
import io
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
import numpy as np
from PIL import Image
import safetensors.torch
import torch
import transformers

DEFAULT_REMOTE_URL = 'http://113.20.103.55:5000'
SESSION_ROUTE = '/feature_fa8688cbfa3fc935ae60de224a972126'
SLOT_ROUTE = '/feature_c426f4d0ed166214ae89992cbd592932'
SUBMIT_ROUTE = '/feature_c26f994e7f7d755a4602972a35430050'
DOMAIN = 'residuegate-six-way-logit-commitment-v1'


def generate_variant(base_arr, variant, epsilon=8):
  out = base_arr.copy().astype(np.int16)
  quadrants = [
      (slice(0, 16), slice(0, 16)),
      (slice(0, 16), slice(16, 32)),
      (slice(16, 32), slice(0, 16)),
      (slice(16, 32), slice(16, 32)),
  ]
  col = 1
  for r_slice, c_slice in quadrants:
    for ch in range(3):
      sign = 1 if (bin(variant & col).count('1') % 2 == 0) else -1
      out[r_slice, c_slice, ch] += epsilon * sign
      col += 1
  return out.astype(np.uint8)


def solve(target_url):
  print(f'[*] Target server: {target_url}')

  # 1. Start fresh session
  url_session = f'{target_url}{SESSION_ROUTE}'
  req = urllib.request.Request(
      url_session, data=b'{}', headers={'Content-Type': 'application/json'}
  )
  with urllib.request.urlopen(req) as resp:
    sess = json.loads(resp.read().decode())

  session_id = sess['session_id']
  seed = sess['combination']['seed']
  commitment = sess['combination']['commitment']
  print(f'[*] Session ID: {session_id}')
  print(f'[*] Seed:       {seed}')
  print(f'[*] Commitment: {commitment}')

  # 2. Download slot base images
  slot_images = []
  os.makedirs('script/remote_slots', exist_ok=True)
  for slot in range(6):
    url_slot = f'{target_url}{SLOT_ROUTE}?session_id={session_id}&slot={slot}'
    slot_path = f'script/remote_slots/slot_{slot}.png'
    urllib.request.urlretrieve(url_slot, slot_path)
    img = Image.open(slot_path).convert('RGB')
    slot_images.append(np.array(img))
    print(f'[*] Downloaded slot {slot} base image ({img.size})')

  # 3. Load Vision Model & Preprocessor
  weights_path = 'model/visual_model.safetensors'
  if not os.path.exists(weights_path):
    print(
        f'[!] Error: Visual weights file {weights_path} not found. Please wait'
        ' for download.'
    )
    sys.exit(1)

  print('[*] Loading Qwen3-VL visual model and projection weights...')
  cfg = json.load(open('script/config.json'))
  vision_cfg = transformers.Qwen3VLVisionConfig(**cfg['vision_config'])
  model = transformers.Qwen3VLVisionModel(vision_cfg)

  state_dict = safetensors.torch.load_file(weights_path)
  clean_dict = {}
  for k, v in state_dict.items():
    if k.startswith('model.visual.'):
      clean_dict[k[len('model.visual.') :]] = v
    elif k.startswith('visual.'):
      clean_dict[k[len('visual.') :]] = v
    else:
      clean_dict[k] = v

  model.load_state_dict(clean_dict, strict=True)
  model.eval()
  processor = transformers.AutoProcessor.from_pretrained(
      'script', trust_remote_code=True
  )

  # Vision config parameters
  obj = json.load(open('script/remote_objective.json'))
  v_cfg = json.loads(obj['vision_config_json'])
  proj_seed = v_cfg['projection_seed']
  proj_center = np.array(v_cfg['projection_center'], dtype=np.float32)
  proj_scale = np.array(v_cfg['projection_scale'], dtype=np.float32)
  gain = v_cfg['quantization_gain']

  rng = np.random.Generator(np.random.PCG64(proj_seed))
  proj_bits = rng.integers(0, 2, size=(12, 2048), dtype=np.int8)
  proj_matrix = (2.0 * proj_bits.astype(np.float32) - 1.0) / np.sqrt(2048.0)

  cache_meta = json.load(
      open('challenge/give_to_player/local-data/qwen_cache.json')
  )
  head_weight = np.array(cache_meta['head_weight'], dtype=np.int64)
  head_bias = np.array(cache_meta['head_bias'], dtype=np.int64)

  # 4. Compute 6x16x4 Logits
  print('[*] Computing embeddings and logits for all 6 slots x 16 variants...')
  logits_table = np.zeros((6, 16, 4), dtype=np.int64)
  cache_by_img = {}

  for slot in range(6):
    base_arr = slot_images[slot]
    img_key = base_arr.tobytes()
    if img_key in cache_by_img:
      print(
          f'[*] Slot {slot} base image matches previous slot -> reusing'
          ' computed logits (instant).'
      )
      logits_table[slot] = cache_by_img[img_key]
      continue

    print(f'[*] Running Qwen3-VL inference for slot {slot} variants...')
    variants = [
        Image.fromarray(generate_variant(base_arr, v)).resize(
            (448, 448), Image.Resampling.BICUBIC
        )
        for v in range(16)
    ]
    inputs = processor.image_processor(images=variants, return_tensors='pt')
    pixel_values = inputs['pixel_values'].to(model.dtype).to(model.device)
    grid_thw = inputs['image_grid_thw'].to(model.device)

    with torch.no_grad():
      outputs = model(pixel_values, grid_thw=grid_thw)
      hidden = outputs.pooler_output
      split_sizes = (
          (grid_thw.prod(-1) // (model.spatial_merge_size**2)).cpu().tolist()
      )
      tokens_per_img = hidden.split(split_sizes)

      for v, chunk in enumerate(tokens_per_img):
        pooled = chunk.mean(dim=0, dtype=torch.float32).cpu().numpy()
        projected = pooled @ proj_matrix.T
        quantized = np.clip(
            np.rint((projected - proj_center) / proj_scale * gain), -16, 16
        ).astype(np.int64)
        logits = head_weight @ quantized + head_bias
        logits_table[slot, v] = logits

    cache_by_img[img_key] = logits_table[slot].copy()

  # Save to logits text file
  logits_txt_path = 'script/remote_logits.txt'
  with open(logits_txt_path, 'w') as f:
    for s in range(6):
      for v in range(16):
        f.write(' '.join(map(str, logits_table[s, v])) + '\n')
  print(f'[*] Wrote {logits_txt_path}')

  # 5. Run Bruteforce Commitment
  print('[*] Brute-forcing 16^6 = 16,777,216 candidate tuples...')
  cmd = [
      './script/bruteforce_commitment_v2',
      seed,
      commitment,
      DOMAIN,
      logits_txt_path,
  ]
  out = subprocess.check_output(cmd, text=True)
  print(f'[*] Output: {out.strip()}')

  m = re.search(r'match:\s*\[([0-9,]+)\]', out)
  if not m:
    print('[!] Bruteforce failed to find matching tuple!')
    sys.exit(1)

  matched_variants = [int(x) for x in m.group(1).split(',')]
  print(f'[+] SUCCESS! Matched variant tuple: {matched_variants}')

  # 6. Submit Multipart Request
  print('[*] Submitting variant images to server...')
  boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
  body = io.BytesIO()

  # session_id
  body.write(f'--{boundary}\r\n'.encode())
  body.write(
      b'Content-Disposition: form-data; name="session_id"\r\n\r\n'
  )
  body.write(f'{session_id}\r\n'.encode())

  # image_0 .. image_5
  for slot, v in enumerate(matched_variants):
    var_arr = generate_variant(slot_images[slot], v)
    var_img = Image.fromarray(var_arr)
    img_bytes = io.BytesIO()
    var_img.save(img_bytes, format='PNG')
    data = img_bytes.getvalue()

    body.write(f'--{boundary}\r\n'.encode())
    body.write(
        f'Content-Disposition: form-data; name="image_{slot}";'
        f' filename="image_{slot}.png"\r\n'.encode()
    )
    body.write(b'Content-Type: image/png\r\n\r\n')
    body.write(data)
    body.write(b'\r\n')

  body.write(f'--{boundary}--\r\n'.encode())
  payload = body.getvalue()

  url_submit = f'{target_url}{SUBMIT_ROUTE}'
  req = urllib.request.Request(
      url_submit,
      data=payload,
      headers={'Content-Type': f'multipart/form-data; boundary={boundary}'},
      method='POST',
  )

  try:
    with urllib.request.urlopen(req) as resp:
      resp_body = resp.read().decode()
      print(f'[*] Server Response: {resp_body}')
      data = json.loads(resp_body)
      if 'flag' in data:
        flag = data['flag']
        print(f'\n[+] FLAG ACQUIRED: {flag}\n')
        with open('flag.txt', 'w') as f:
          f.write(flag + '\n')
        return flag
  except urllib.error.HTTPError as e:
    print(f'[!] HTTP Error {e.code}: {e.read().decode()}')
    sys.exit(1)


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--url', default=DEFAULT_REMOTE_URL)
  args = parser.parse_args()
  solve(args.url)


if __name__ == '__main__':
  main()
