# python3 -m pip install torch safetensors
import torch
from safetensors.torch import load_file

from model import NUM_LAYERS, HiddenEmbeddingNet

state_dict = load_file("model.safetensors")
dims = [state_dict["layers.0.weight"].shape[1]]
dims += [state_dict[f"layers.{i}.weight"].shape[0] for i in range(NUM_LAYERS)]

model = HiddenEmbeddingNet(dims=dims)
model.load_state_dict(state_dict)
model.eval()

# Set input vector = [1, 0, 0, 0, ...]
x = torch.zeros(dims[0])
x[0] = 1.0

with torch.no_grad():
    output = model(x)

print(f"[*] input dim={dims[0]}, num_layers={NUM_LAYERS}")
print(f"[*] output: {output.tolist()}")

try:
    text = "".join(chr(int(round(v))) for v in output.tolist())
    print(f"[*] decoded: {text!r}")
except ValueError as e:
    print(f"[-] decode failed: {e}")
