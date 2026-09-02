import torch
import torch.nn as nn
import torch.nn.functional as F

NUM_LAYERS = 16


class HiddenEmbeddingNet(nn.Module):
    def __init__(self, dims: list[int]):
        super().__init__()
        assert len(dims) == NUM_LAYERS + 1
        self.dims = dims
        self.layers = nn.ModuleList(
            [nn.Linear(dims[i], dims[i + 1]) for i in range(NUM_LAYERS)]
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Gotta use all layers and in order... right?
        for layer in self.layers:
            x = F.relu(layer(x))
        return x
