# Codexa v1 — PyTorch workspace

This is the canonical PyTorch development repository. Its seven component repositories are pinned Git submodules beneath this root; the former nested integration repository has been lifted here with its Git history intact.

| Submodule | Responsibility |
| --- | --- |
| LLM-Architecture | Native Transformer, RMSNorm, SwiGLU, learned/RoPE positions, KV cache and checkpoint readers |
| LLM-Tokenizer | Byte-level BPE and shared conversation/SFT serialization |
| LLM-Data | Corpus provenance, preparation, packing and token data |
| LLM-Training | Base/SFT training, optimizer state, restoration and monitoring |
| LLM-Inference | Native completion, chat and experimental exports |
| LLM-Memory | Scoped SQLite persistence, retrieval and worker client |
| LLM-Specialist | Independently frozen EmbeddingGemma 2 and classifier heads |

Reusable integration tools live in `src/codexa_workspace/`. Legacy `src` imports, script paths and `--repo LLM-From-Scratch` remain compatibility adapters. NumPy is a separate implementation and repository.

## Checkout and environments

```bash
git clone --recurse-submodules https://github.com/golba98/LLM-From-Scratch-PyTorch-Codexa-v1.git
# Existing checkout:
git submodule update --init --recursive
python run.py test -q
python run.py --repo LLM-Architecture test -q
python run.py --profile specialist --repo LLM-Specialist test -q
```

The local `.venv` and `.venv-specialist` were relocated from the original checkout on the same machine, their generated launch paths repaired, and local package wheels installed. They no longer require the old directory. Keep the generative and specialist environments separate. Exact external package inventories are recorded in requirements lock files; package and Git pins are in `compatibility.json`. See documentation/migration/ENVIRONMENTS.md for rebuilding and limitations.

## Protected assets and new outputs

Copy `artifacts.local.example.json` to ignored `artifacts.local.json` and set `asset_root`, or export `CODEXA_ASSET_ROOT`. The root contains the historical `checkpoints/`, `data/`, `exports/` and `logs/` trees. Local inputs currently live in protected temporary storage outside project directories. Model weights, datasets, private logs, source snapshots and recovery bundles are never committed.

```bash
python run.py module workflows.chat --describe
python run.py module workflows.chat --device cuda
python run.py generate --help
python run.py train --help
```

The chat catalog retains the repair comparison baseline and exact 16K tokenizer. The stage-2 pilot remains experimental. Learned-position/RMSNorm/SwiGLU native checkpoints are authoritative; historical GPT-2/Llama conversion paths remain experimental. New launcher outputs default beneath `outputs/`; direct component commands must receive explicit output paths. Operator training attaches the required visible 100x22 Kitty viewer before training.

See [MIGRATION.md](MIGRATION.md), [VALIDATION.md](VALIDATION.md) and the detailed migration report under documentation/migration/. The source directories remain pending retirement, PRs are not auto-merged, and a single asset store is not an independent disk backup.
