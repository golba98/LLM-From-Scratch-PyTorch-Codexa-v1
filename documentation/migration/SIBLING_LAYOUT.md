# Current sibling architecture — 2026-10-09

The workspace directory is no longer a Git root. LLM-From-Scratch contains the original integration worktree and Git history. Seven components retain their original histories, branches, HEADs and indexes in independent .git directories. compatibility.json records sibling paths and exact Git pins. The old .gitmodules is preserved as submodules-before-2026-10-09.gitmodules. Historical tracked gitlinks and .gitmodules appear as unstaged deletions; review these when authorizing a commit. The initial migration was uncommitted; subsequent publication is recorded in PUBLICATION_2026-10-09.md. Historical commits still describe the previous layout.

Integration owns src/codexa_workspace, evaluation/research orchestration, compatibility src/script adapters, recipes/configs/schemas/workflows, central tests/docs, requirements and runtime outputs. Components own reusable named packages and their independent tests. Repeated test cases and standalone config examples are validation/recipe copies, not duplicate implementation. Historical files under preservation are read-only recovery evidence. The exhaustive pre-change file map and actual move journal are in ../../../workspace-infrastructure/audit-2026-10-09 (from this file's directory).

Shared build, preservation and validation directories live in workspace-infrastructure and are linked from integration. Local environments remain integration-owned; launch prefixes were repaired. Historical assets remain external and unchanged. 31 and 32 remain untouched. An independent off-disk backup is still required before retirement.

## Checkout and install

For future sibling checkouts, clone the integration repository into LLM-From-Scratch, then clone each compatibility.json component into its sibling name using the URL in submodules-before-2026-10-09.gitmodules, and check out the recorded commit. The open integration review branch uses this layout; default branches retain the historical layout until reviewed and merged. Do not reset existing worktrees to recreate this layout.

From integration, use `.venv/bin/python run.py test -q`, `run.py --repo LLM-Data test -q`, or the specialist profile. Source bootstrap uses explicit manifest sibling paths. Installed components depend only on declared distributions; install the local component wheels in dependency order or together with pip, and install integration last. Integration's package metadata now declares its generative dependencies; Specialist is optional in its separate environment. A standalone integration wheel requires an explicit checkout/configured root for operator scripts/recipes (those are source workflows).

## Dependency graph

Architecture and Tokenizer are leaves. Data depends on Tokenizer. Training depends on Architecture, Tokenizer and Data. Inference depends on Architecture and Tokenizer, with Memory optional. Memory uses a separately configured JSON-lines Specialist worker; no Python import dependency. Specialist is independent. Integration depends on generative components and optionally Specialist. No reverse component-to-integration imports are permitted.

The migration is reversible via the saved metadata and reverse move journal. Stop writers first; preserve new outputs and changes before restoring. Never overwrite original projects or historical assets.

## Ownership correction found by independent checks

LLM-Data/tests/test_general_chat.py depended on integration test helpers and exercised Training. Its AST matches central tests/test_general_chat.py exactly after package-name normalization. The misplaced copy moved to LLM-Data/documentation/migration/retained-tests/test_general_chat.py.txt, byte for byte, for tracked provenance; central integration retains all three tests. No test coverage was discarded. The Data sampling console entry point now exports main(), sharing the existing implementation.
