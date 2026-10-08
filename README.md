# Build an LLM From Scratch

This integration repository coordinates seven independently packaged components in the sibling workspace. It retains the original Git history, overall documentation, current configuration files, evaluation workflows and the complete original regression suite. Generic `src` imports and old `scripts/*.py` entry points are temporary adapters here; reusable implementations live in their owning repositories.

| Repository | Import namespace | Responsibility |
| --- | --- | --- |
| LLM-Architecture | llm_architecture | Decoder, positions, attention, normalization, KV cache, native checkpoint readers |
| LLM-Tokenizer | llm_tokenizer | Byte-level BPE and shared conversation/SFT protocol |
| LLM-Data | llm_data | Corpus preparation, provenance, packing and memmap data |
| LLM-Training | llm_training | Optimizers, training loops, configuration and checkpoint restoration |
| LLM-Inference | llm_inference | Completion, native chat, context composition and native exports |
| LLM-Memory | llm_memory | Scoped SQLite persistence and cosine retrieval |
| LLM-Specialist | llm_specialist | Separate frozen encoder/worker and programming classifier |

## Run without installing dependencies

From this directory:

```bash
python run.py generate --help
python run.py chat_native --help
python run.py train --help
python run.py --profile specialist specialist --help
python run.py --repo LLM-Architecture test -q
```

The launcher reuses the original generative or specialist interpreter if available, or accepts `--python /path/to/python`. It sets source paths only for the launched process; it does not modify either environment. Independent package installation uses their pyproject.toml metadata; packages are not published to PyPI. Wheel builds are verified but were not installed.

## Existing native chat

```bash
python run.py chat_native \
  --checkpoint '/home/k9-vortex/Development/3-Python/31-LLM (PyTorch)/checkpoints/codexa-900m-sft-repair-v1/latest.pt' \
  --tokenizer '/home/k9-vortex/Development/3-Python/31-LLM (PyTorch)/checkpoints/tokenizer-base-v1/tokenizer.json' \
  --device cuda
```

Alternatively, resolve these paths through the catalog:

```bash
python run.py module workflows.chat --help
python run.py module workflows.chat --device cuda
```

The chat helper resolves the repair comparison baseline and tokenizer from the catalog. Memory is off by default; `--memory ephemeral` explicitly enables the configured specialist worker. Existing persistent databases are never selected automatically. The repair model remains experimental; the Stage 2 pilot is not promoted.

## Artifact preservation

Original checkpoints, exports, tokenizers, datasets and logs remain under the original `31-LLM (PyTorch)` directory. No large assets or artifact symlinks were copied into the repositories. Catalog metadata is in artifact-catalog/catalog.json; history, source snapshot, working-tree patch, hashes and environment inventories are in ../preservation/. That local directory is not an independent disk backup and must not be published.

New training outputs default to this checkout, not the original directory. Native/full/legacy SFT and specialist formats remain distinct. Legacy SFT resume is not exact optimizer/RNG restoration. Operator base/SFT/Stage 2 launches retain the required visible 100x22 Kitty viewer. Do not rerun historical recipes without checking their inputs and acceptance gates; no model training pipeline was launched during extraction.

## Validation and review

See VALIDATION.md for tested scope and limitations, MIGRATION.md for the mapping and rollback, compatibility.json for the pinned component set, and project/ for local GitHub Project issue drafts. Remote repositories, commits, pushes and PRs have not been created. The Project token still lacks read:project.

Historical planning/reference documents remain available under documentation/. The current 16K learned-position configuration has 934,356,480 parameters; stale 8K descriptions are corrected in the architecture reference and model card. Original documents are preserved in the source snapshot.

# LLM-From-Scratch-PyTorch-Codexa-v1
