# Versioned workspace documentation

OVERVIEW.md, WORKSPACE_GUIDELINES.md and SHARED_INFRASTRUCTURE.md are the canonical saved versions of the workspace-level README, AGENTS instructions and infrastructure README. Local workspace files link to these documents, so there is one maintained copy and their contents are included in the integration PR.

To expose the documents in a fresh sibling workspace, run from the parent of LLM-From-Scratch (only where destinations are absent):

```sh
ln -s LLM-From-Scratch/documentation/workspace/OVERVIEW.md README.md
ln -s LLM-From-Scratch/documentation/workspace/WORKSPACE_GUIDELINES.md AGENTS.md
mkdir -p workspace-infrastructure
ln -s ../LLM-From-Scratch/documentation/workspace/SHARED_INFRASTRUCTURE.md workspace-infrastructure/README.md
```

Source and docs live in the eight repositories and are published on their review branches. Private configuration, virtual environments, checkpoints, datasets, recovery bundles, full audit inventories and generated build/test evidence remain saved locally or in the existing external asset store. They are deliberately excluded from public Git. Local preservation is verified; an independent off-disk backup is still required before retiring original projects.
