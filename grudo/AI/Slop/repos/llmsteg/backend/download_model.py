from huggingface_hub import hf_hub_download
from transformers import logging

logging.set_verbosity_info()


def download_gpt2_model():
    print("Downloading GPT-2 model and tokenizer manually...", flush=True)

    model_file = hf_hub_download(repo_id="gpt2", filename="pytorch_model.bin")
    print(f"Model downloaded to: {model_file}", flush=True)

    config_file = hf_hub_download(repo_id="gpt2", filename="config.json")
    print(f"Config downloaded to: {config_file}", flush=True)

    vocab_file = hf_hub_download(repo_id="gpt2", filename="vocab.json")
    print(f"Vocab file downloaded to: {vocab_file}", flush=True)

    merges_file = hf_hub_download(repo_id="gpt2", filename="merges.txt")
    print(f"Merges file downloaded to: {merges_file}", flush=True)

    print("All files downloaded successfully.", flush=True)


if __name__ == "__main__":
    download_gpt2_model()
