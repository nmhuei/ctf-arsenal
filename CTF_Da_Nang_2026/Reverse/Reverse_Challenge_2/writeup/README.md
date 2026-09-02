# ONNX Model Secrets

Our AI research team deployed an emotion classification model for internal use.
The model is served via HTTP from your challenge instance.

Download the model file and analyze it. Something sensitive was embedded during
the model's calibration process.

## Interface

HTTP service. Download the model from the instance URL.

## Hints

- The ONNX format is based on Protocol Buffers
- Models can carry more than just weights and graph structure
- Tools: `onnx` Python library, Netron (https://netron.app)
