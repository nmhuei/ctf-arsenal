import json
import math
import os
import struct
import numpy as np
from PIL import Image
import safetensors.torch
import torch
import transformers

print('[*] Loading configs...')
obj = json.load(open('script/remote_objective.json'))
v_cfg = json.loads(obj['vision_config_json'])
proj_seed = v_cfg['projection_seed']
proj_center = np.array(v_cfg['projection_center'], dtype=np.float32)
proj_scale = np.array(v_cfg['projection_scale'], dtype=np.float32)
gain = v_cfg['quantization_gain']

print(f'[*] Building projection matrix (PCG64 seed {proj_seed})...')
rng = np.random.Generator(np.random.PCG64(proj_seed))
proj_bits = rng.integers(0, 2, size=(12, 2048), dtype=np.int8)
proj_matrix = (2.0 * proj_bits.astype(np.float32) - 1.0) / np.sqrt(2048.0)


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


def load_ground_truth_cache(bin_path):
  with open(bin_path, 'rb') as f:
    f.seek(8)
    badge_hash = f.read(32)
    records = []
    for _ in range(16):
      opaque = f.read(32)
      emb = [
          int.from_bytes(f.read(1), 'little', signed=True) for _ in range(12)
      ]
      records.append((opaque, emb))
    return badge_hash, records


def run_pipeline(model, processor, base_img_path):
  base_img = Image.open(base_img_path).convert('RGB')
  base_arr = np.array(base_img)

  variants = []
  for v in range(16):
    var_arr = generate_variant(base_arr, v)
    variants.append(Image.fromarray(var_arr))

  # Preprocessing
  inputs = processor.image_processor(images=variants, return_tensors='pt')
  pixel_values = inputs['pixel_values'].to(model.dtype).to(model.device)
  grid_thw = inputs['image_grid_thw'].to(model.device)

  with torch.no_grad():
    outputs = model(pixel_values, grid_thw=grid_thw)
    # merged image tokens (shape: total_tokens, 2048)
    hidden = outputs.pooler_output
    split_sizes = (grid_thw.prod(-1) // (model.spatial_merge_size**2)).cpu().tolist()
    tokens_per_img = hidden.split(split_sizes)

    embeddings = []
    for chunk in tokens_per_img:
      # float32 mean over tokens
      pooled = chunk.mean(dim=0, dtype=torch.float32).cpu().numpy()
      # Projection
      projected = pooled @ proj_matrix.T
      # Quantization
      quantized = np.clip(
          np.rint((projected - proj_center) / proj_scale * gain), -16, 16
      ).astype(np.int8)
      embeddings.append(quantized.tolist())

  return embeddings


def main():
  weights_path = 'model/visual_model.safetensors'
  if not os.path.exists(weights_path):
    print(f'[!] Weights not ready yet: {weights_path}')
    return

  print('[*] Loading model and processor...')
  cfg = json.load(open('script/config.json'))
  vision_cfg = transformers.Qwen3VLVisionConfig(**cfg['vision_config'])
  model = transformers.Qwen3VLVisionModel(vision_cfg)

  # Load state dict
  state_dict = safetensors.torch.load_file(weights_path)
  # Filter model.visual prefix if needed
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
  print('[*] Model weights loaded with 100% strict match!')

  processor = transformers.AutoProcessor.from_pretrained(
      'script', trust_remote_code=True
  )

  print('[*] Testing pipeline on benchmark base_badge.png...')
  pred_embs = run_pipeline(
      model, processor, 'challenge/give_to_player/local-data/base_badge.png'
  )

  _, gt_records = load_ground_truth_cache(
      'challenge/give_to_player/local-data/qwen_cache.bin'
  )
  gt_embs = [r[1] for r in gt_records]

  matches = 0
  for v in range(16):
    is_match = pred_embs[v] == gt_embs[v]
    if is_match:
      matches += 1
    print(
        f'Variant {v:2d}: match={is_match} | pred={pred_embs[v]} |'
        f' gt={gt_embs[v]}'
    )

  print(f'\n[*] Benchmark verification result: {matches}/16 matches!')


if __name__ == '__main__':
  main()
