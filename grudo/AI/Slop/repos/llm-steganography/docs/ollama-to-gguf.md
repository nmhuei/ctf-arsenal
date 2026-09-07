# Ollama → standalone `.gguf`

Ollama does not ship an `ollama export` command. Weights are already stored as **content-addressed blobs**; the big one is usually a **GGUF** you can copy out.

## 1. Pull the model

```bash
ollama pull llama3
```

## 2. Copy the weights blob (no “conversion”)

Ollama already stores the model as a **GGUF** blob. You only need to **copy** it into this repo as `models/llama3.gguf` (or whatever name matches your `modelName`).

**Using the manifest (exact digest):**

```bash
MODEL=llama3
TAG=latest
MANIFEST="$HOME/.ollama/models/manifests/registry.ollama.ai/library/${MODEL}/${TAG}"
DIGEST=$(jq -r '.layers[] | select(.mediaType=="application/vnd.ollama.image.model") | .digest' "$MANIFEST")
# digest looks like sha256:abcd...  →  blob file is sha256-abcd...
BLOB="$HOME/.ollama/models/blobs/${DIGEST/:/-}"
mkdir -p models
cp "$BLOB" models/llama3.gguf
```

**Sanity check:** the file should start with the ASCII magic `GGUF`:

```bash
xxd -l 4 models/llama3.gguf
# 00000000: 4747 5546                              GGUF
```

To save disk space you can use a **symlink** instead of `cp`, but then the project breaks if Ollama prunes that blob.

## 3. Manual path (no `jq`)

Default model root:

| OS      | Path |
|--------|------|
| macOS / Linux | `~/.ollama/models` |
| Windows | `%USERPROFILE%\.ollama\models` |

Override with `OLLAMA_MODELS` if you use a custom directory.

- **`blobs/`** — files named `sha256-<64 hex chars>` (no extension). The **largest** file is usually the model GGUF.
- **`manifests/`** — open `manifests/registry.ollama.ai/library/<model>/<tag>` and find the `application/vnd.ollama.image.model` layer digest (`sha256:`…); the blob on disk is the same digest with the colon replaced by a hyphen (`blobs/sha256-…`).

```bash
cp ~/.ollama/models/blobs/sha256-<digest> ./models/llama3.gguf
```

```bash
file ./models/llama3.gguf   # may say "data"; use `xxd -l 4` above to confirm GGUF magic
```

**Caveat:** Some setups use multiple blobs (layers). If `file` does not say GGUF, check the manifest for which digest is the base weights, or use a helper such as [Ollama-Model-Dumper](https://github.com/AaronFeng753/Ollama-Model-Dumper) to dump by model name.

**Going the other way** (GGUF → Ollama): see [Importing a GGUF-based model](https://docs.ollama.com/import#importing-a-gguf-based-model-or-adapter).
