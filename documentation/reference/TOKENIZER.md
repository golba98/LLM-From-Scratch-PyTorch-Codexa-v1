# Base Tokenizer

Codexa uses Hugging Face `tokenizers` with byte-level BPE, a ByteLevel
pre-tokenizer, and a ByteLevel decoder. The current production candidate has
8,192 entries; an 8,192-versus-16,384 bake-off must run before it is frozen.

| Token | ID |
| --- | ---: |
| `<pad>` | 0 |
| `<bos>` | 1 |
| `<eos>` | 2 |
| `<unk>` | 3 |
| `<|system|>` | 4 |
| `<|user|>` | 5 |
| `<|assistant|>` | 6 |
| `<|end|>` | 7 |

No BOS or EOS token is silently added to prompts. Dataset tokenization appends
exactly one EOS token after every document.

The retained legacy FineWeb-Edu tokenizer has SHA-256:

```text
6b26d3c98d8782298119875c368a69fdccbff03cca6fbfa1fc0851b0f3f8ef0c
```

It predates the four reserved chat tokens and therefore cannot be frozen for
the rebuild. The new candidates must prove round-trip correctness and include
all eight stable special-token IDs in their checksummed manifests. The
tokenizer remains English-focused and is not specialized for multilingual text
or code. Token binaries and checkpoints from different tokenizer checksums may
never be mixed.
