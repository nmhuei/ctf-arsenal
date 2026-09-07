# llm-steganography

**Goal:** hide a short secret message inside normal-looking plaintext using LLM output. The text itself is not encrypted. Instead, the message is encoded in the token choices the model makes while generating. For the full mechanism, see [`docs/theoretical.md`](docs/theoretical.md). The payload is UTF-8 bytes with a 32-bit byte-length header, followed by 8 bits per byte. On non-dominant steps, one bit is encoded per token by choosing between the two most likely non-EOG candidates. Anyone with the same model and prompt can replay generation, recover the bits, and read the message.

<img width="547" height="744" alt="low quality aah image" src="https://github.com/user-attachments/assets/89dc7520-62ac-4d36-b54b-bf7bbfefad0f" />

**Why it matters:** the output still reads like a normal response, while the hidden data is carried by small token-level choices. This is experimental. Capacity is low, recovery depends on the exact same model, tokenizer, and prompt, and `decrypt` must receive the exact `completionText` returned by `encrypt` so tokenization stays aligned.

**Stack:** [Bun](https://bun.sh), [node-llama-cpp](https://github.com/withcatai/node-llama-cpp), and a local GGUF (e.g. `models/llama3.gguf`) model. Prompts are wrapped with Llama 3’s chat format so behavior matches instruction-tuned models.

## Prerequisites

- [Bun](https://bun.sh)
- [node-llama-cpp](https://github.com/withcatai/node-llama-cpp)
- a local GGUF (e.g. `models/llama3.gguf`) model (see [docs/ollama-to-gguf.md](docs/ollama-to-gguf.md))

## Usage

### CLI ([commander](https://github.com/tj/commander.js))

```bash
# embed a payload (writes completion text to stdout)
bun src/cli.ts encrypt -u "A poem about dogs." -p "hello world" -m llama3

# save completion to a file
bun src/cli.ts encrypt -u "A poem about dogs." -P ./secret.txt -o completion.txt -m llama3

# recover payload (completion must match encrypt output exactly)
bun src/cli.ts decrypt -u "A poem about dogs." -f completion.txt -m llama3
```

With `bun install` (or `npm link`), the `llm-steganography` binary is on `PATH` (`package.json` `"bin"`).

Place your model at `models/<name>.gguf` and pass `-m` without the extension (e.g. `llama3`). If you use Ollama, copy the exported GGUF from `~/.ollama/models/blobs/` (see `docs/ollama-to-gguf.md`).
