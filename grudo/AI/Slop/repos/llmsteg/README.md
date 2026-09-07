# llmsteg: Text-Based Steganography Using Language Models

## An update

After talking to one if the professers at JKU, I will probably research this topic further in form of the **Seminar in AI** course. Maybe I will even write my bachelor thesis on it, lets see. 

Seminar presentation can be found here:
[Watermarks_for_Language_Models-Toller.pdf](https://github.com/user-attachments/files/20224960/Watermarks_for_Language_Models-Toller.pdf)

## Introduction

Steganography, the art of concealing messages, has long intrigued me as a niche but fascinating complement to cryptography. Unlike cryptography, which focuses on securing data through encryption, steganography seeks to hide the very existence of a message. This project explores an approach to text-based steganography by leveraging language models to encode hidden messages within naturally generated text. It's an approach I personally haven't seen so far.

## Other resources

Looks like there are some other papers on this: https://youtu.be/55LXhbPjyeM?si=-kn1_VQe_fdln1xZ

While still a simple and experimental proof of concept, this method demonstrates the potential to obscure data in plain sight using probabilistic token selection.

## Demo

https://github.com/user-attachments/assets/ab60e0e0-06d0-4a9c-8d42-53a134fa3723

## Project Overview

The core idea is to encode a secret message within the sequence of tokens chosen by a language model during text generation. By mapping bits of the hidden message to token indices, the generated text remains coherent and natural-looking while embedding concealed data.

The project comprises two main components:

- **Backend**: Implements the encoding and decoding algorithms, utilizing a pre-trained language model (e.g., GPT-2).
- **Frontend**: A simple Svelte application for testing the encoding and decoding processes.

## Installation

### Starting the Backend

1. Install the required dependencies.
2. Run the backend server using `python server.py`.

### Starting the Frontend

1. Install the required dependencies.
2. Start the frontend using `npm run dev`.

## Advantages Over Traditional Steganography Methods

- **Natural Language Medium**: Concealing data in text is less conspicuous compared to traditional methods involving images or audio files.
- **Adaptive Content**: Generated text can align contextually with a given scenario, making it versatile for applications like storytelling or automated responses.
- **Resistance to Detection**: Existing steganalysis tools primarily focus on media files, making text-based methods harder to detect.

## How It Works

### Encoding Process

1. **Message Compression**: The secret message is compressed using zlib to minimize size.
2. **Bit Conversion**: The compressed message is transformed into a bit string.
3. **Error Correction**: Hamming encoding adds redundancy to correct errors during decoding.
4. **Bit Grouping**: The bit string is divided into groups of a fixed size (`bits_per_choice`).
5. **Token Selection**:
   - Each group of bits is converted into an integer `n`.
   - The language model predicts the probabilities for the next tokens in the sequence.
   - The top `2^bits_per_choice` tokens are considered, and the token corresponding to index `n` is selected.
6. **Text Generation**: Tokens are appended to the input prompt to produce encoded text containing the hidden message.

### Decoding Process

1. **Tokenization**: The encoded text is tokenized into a sequence of tokens.
2. **Context Initialization**: Decoding begins with the same initial prompt used during encoding.
3. **Bit Extraction**:
   - For each token, the model computes probabilities for possible continuations.
   - The top `2^bits_per_choice` tokens are identified, and the actual token's index is extracted and converted back to bits.
4. **Error Correction and Decompression**:
   - Bits are concatenated to reconstruct the encoded string.
   - Hamming decoding corrects errors.
   - The bit string is decompressed to recover the original message.

## Current Limitations and Challenges

1. **Efficiency**: Encoding data in text is far less efficient than in images or audio files. The generated text may be significantly longer than the hidden message.
2. **Performance**:
   - The current implementation is slow and lacks optimization.
   - Text generation depends on local LLM performance, requiring suitable hardware and technical expertise.
3. **Coherence**: Poorly generated or excessively verbose text may arouse suspicion.
4. **Setup Discrepancies**: Differences in LLM versions, settings, or hardware may lead to decoding errors.
5. **Reliability**: Tiny inconsistencies can significantly impact the decoding process.
6. **Practicality**: While interesting, this method is not yet practical for real-world steganography.

## Future Exploration

This project is an experimental take on text-based steganography and opens the door for further exploration:

- Experimenting with various language models and token selection strategies.
- Optimizing encoding methods for better efficiency and coherence.
- Exploring smaller, faster, and more energy-efficient language models for practical use cases.

As language models continue to evolve, this approach could become a viable means of embedding messages in everyday communications, such as text messaging or content generation.

---

This project remains a proof of concept and serves as a starting point for those interested in combining steganography with advances in language models. If you know of similar work or have suggestions for improvement, let me know!
