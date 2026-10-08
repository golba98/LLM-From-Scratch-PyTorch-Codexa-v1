# Canonical PyTorch workspace guidelines

This root Git repository pins seven independent component repositories as submodules. Keep reusable implementations in their owners and integration/evaluation orchestration in `src/codexa_workspace`. Generic `src` and script adapters are temporary compatibility interfaces. Do not import the integration package from a component or introduce reverse/circular package dependencies.

Use `.venv` for generative checks and `.venv-specialist` for the frozen encoder/heads. Assets resolve through CODEXA_ASSET_ROOT or ignored artifacts.local.json; never fall back to retired project directories. Never commit weights, datasets, private logs, environments, source snapshots, credentials or recovery bundles. New experiments require distinct output paths beneath this workspace or an explicitly configured output root; historical assets are read-only inputs.

Preserve state-dictionary keys, NPZ/native checkpoint dialects, tokenizer IDs and hashes, model lineage, RNG/optimizer restoration and memory scopes. Base/SFT operator launches require the automatically attached visible 100x22 Kitty viewer. Use bounded synthetic tests; no expensive training runs during refactors.

Append dated decisions/evidence to documentation/training/SESSION_DECISIONS.md and milestones to 100M_PROGRESS_LOG.md. Run the relevant regression suites, wheel and CLI checks before PRs. Stage source changes and intentional submodule pins only. Do not force-push, merge PRs, alter repository permissions/protection or remove pending-retirement directories without satisfying the documented gates.
