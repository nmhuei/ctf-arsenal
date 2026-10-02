import concurrent.futures
import json
import os
import struct
import sys
import time
import urllib.request

HF_URL = "https://huggingface.co/Qwen/Qwen3-VL-2B-Instruct/resolve/main/model.safetensors"
OUT_DIR = "model"
os.makedirs(OUT_DIR, exist_ok=True)

# 1. Fetch header to map tensor offsets
print("[*] Fetching safetensors header...")
req = urllib.request.Request(HF_URL, headers={"Range": "bytes=0-7"})
with urllib.request.urlopen(req) as resp:
  hdr_len = struct.unpack("<Q", resp.read())[0]

req = urllib.request.Request(HF_URL, headers={"Range": f"bytes=8-{7+hdr_len}"})
with urllib.request.urlopen(req) as resp:
  full_hdr = json.loads(resp.read().decode("utf-8"))

visual_keys = [
    k
    for k in full_hdr
    if k.startswith("visual.") or k.startswith("model.visual.")
]
print(f"[*] Found {len(visual_keys)} visual tensors.")

min_offset = min(full_hdr[k]["data_offsets"][0] for k in visual_keys)
max_offset = max(full_hdr[k]["data_offsets"][1] for k in visual_keys)
total_bytes = max_offset - min_offset
print(
    f"[*] Data span: {min_offset} to {max_offset} ({total_bytes / (1024*1024):.2f} MB)"
)

# Global byte range in model.safetensors
global_start = 8 + hdr_len + min_offset
global_end = 8 + hdr_len + max_offset - 1
print(f"[*] Global byte range: {global_start} - {global_end}")

# 2. Download visual weights using multi-threading
CHUNK_SIZE = 16 * 1024 * 1024  # 16 MB chunks
chunks = []
curr = global_start
idx = 0
while curr <= global_end:
  end = min(curr + CHUNK_SIZE - 1, global_end)
  chunks.append((idx, curr, end))
  curr = end + 1
  idx += 1

print(f"[*] Downloading {len(chunks)} chunks using 8 parallel threads...")

out_bin = os.path.join(OUT_DIR, "visual_raw_data.bin")
# Pre-allocate file
with open(out_bin, "wb") as f:
  f.truncate(total_bytes)


def download_chunk(item):
  chunk_idx, byte_start, byte_end = item
  file_offset = byte_start - global_start
  chunk_len = byte_end - byte_start + 1

  for attempt in range(5):
    try:
      req = urllib.request.Request(
          HF_URL, headers={"Range": f"bytes={byte_start}-{byte_end}"}
      )
      with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read()
      if len(data) == chunk_len:
        with open(out_bin, "r+b") as f:
          f.seek(file_offset)
          f.write(data)
        return chunk_idx, chunk_len
    except Exception as e:
      time.sleep(1)
  raise RuntimeError(f"Failed to download chunk {chunk_idx}")


start_time = time.time()
downloaded = 0
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
  futures = {executor.submit(download_chunk, c): c for c in chunks}
  for future in concurrent.futures.as_completed(futures):
    c_idx, c_len = future.result()
    downloaded += c_len
    pct = downloaded / total_bytes * 100
    elapsed = time.time() - start_time
    speed = (downloaded / (1024 * 1024)) / max(elapsed, 0.1)
    sys.stdout.write(
        f"\r[*] Progress: {pct:5.1f}% ({downloaded / (1024*1024):.1f}/{total_bytes / (1024*1024):.1f} MB) - Speed: {speed:.2f} MB/s"
    )
    sys.stdout.flush()

print(f"\n[*] Raw visual data downloaded in {time.time() - start_time:.1f}s!")

# 3. Create clean visual_model.safetensors
print("[*] Creating visual_model.safetensors...")
new_hdr = {}
for k in visual_keys:
  entry = dict(full_hdr[k])
  orig_offsets = entry["data_offsets"]
  entry["data_offsets"] = [
      orig_offsets[0] - min_offset,
      orig_offsets[1] - min_offset,
  ]
  # strip 'model.visual.' prefix if needed or keep both
  new_hdr[k] = entry
  if k.startswith("model.visual."):
    # also add without 'model.' prefix for direct loading
    short_k = k[len("model.") :]
    new_hdr[short_k] = entry

hdr_bytes = json.dumps(new_hdr, separators=(",", ":")).encode("utf-8")
# Align header to 8 bytes
pad = (8 - (len(hdr_bytes) % 8)) % 8
hdr_bytes += b" " * pad
new_hdr_len = len(hdr_bytes)

final_safetensors = os.path.join(OUT_DIR, "visual_model.safetensors")
with open(final_safetensors, "wb") as f_out:
  f_out.write(struct.pack("<Q", new_hdr_len))
  f_out.write(hdr_bytes)
  with open(out_bin, "rb") as f_in:
    while True:
      buf = f_in.read(4 * 1024 * 1024)
      if not buf:
        break
      f_out.write(buf)

os.remove(out_bin)
print(
    f"[*] SUCCESS! Saved {final_safetensors} ("
    f"{os.path.getsize(final_safetensors) / (1024*1024):.2f} MB)"
)
