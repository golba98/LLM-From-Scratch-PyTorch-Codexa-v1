# Review publication and preservation — 2026-10-09

The user authorized commits, pushes and PR updates for LLM-Data and LLM-From-Scratch after the local audit. Existing Data PR #3 and integration PR #2 carry these changes. No PR is merged and no repository is deleted. The eight sibling repositories are saved under project 37; shared local infrastructure is workspace-infrastructure. Original 31 and 32 remain untouched and pending independent backup verification.

## What Git labels as removed

Integration removes seven mode-160000 submodule pointers and relocates .gitmodules to documentation/migration/submodules-before-2026-10-09.gitmodules. The pointers contain commit IDs, not component source; the seven real component working trees, histories and objects remain. Exact sibling paths and commits are recorded in compatibility.json. Data relocates its original integration-dependent test into documentation/migration/retained-tests/test_general_chat.py.txt with identical bytes. Its three tests remain active centrally. No substantive source file, checkpoint, dataset or repository is discarded.

The audit was not exclusively directory changes. Manifest/import resolution, dependency metadata, build/CLI tools and docs were updated, and the Data sampling CLI gained a main() that delegates to its existing implementation. Environment launch prefixes were repaired locally. Generated wheels/build logs were refreshed. Everything is accounted for by the local original inventory, move journal and edited-file hashes.

## Saved versus published

All migration files remain on disk beneath project 37 or the pre-existing configured external historical asset store. Public source/docs changes in these two repositories are committed and pushed to existing review branches. Other six components' documentation edits remain locally saved and uncommitted; their runtime code is unchanged. Root workspace README/AGENTS and shared audit/recovery/build evidence remain local. Private settings, environments, checkpoint weights, datasets and recovery bundles are intentionally excluded from public Git, as required by repository guidelines. These are not deleted or relocated into PRs.

## Verification

The full initial audit found zero missing files across 66,474 inventory entries. Original 31/32 files, symlinks and Git state are unchanged. All ten original Git HEADs were preserved by directory restructuring; newly authorized commits now advance only Data and integration. All ten histories pass Git integrity verification. All 517 historical assets (138,521,323,134 bytes) passed streaming SHA-256 plus metadata verification. Ten recovery bundles verified. Independent off-disk backup is still unavailable.

Prior complete validation: integration 121 passed / 5 skipped; Specialist package 39 passed; Specialist integration selection 58 passed; independent Architecture/Tokenizer/Data/Training/Inference/Memory 5/6/12/10/1/5 passed. Eight wheels built; 33 packaged module help commands passed; 52 applicable independent, dependency and installed-wheel probes passed. Exact references and deterministic sampling were verified. Existing optional-dependency skips and return-value warnings remain; clean-host dependency installation and production training are not claimed. Publication revalidation and fresh sibling-clone results are appended below before pushing.

Publication revalidation: integration 121 passed / 5 optional sklearn skips / 8 inherited return-value warnings; Data 12 passed; all eight wheels rebuilt; all 33 module CLI helps passed. All 517 asset size/mtime records and ten recovery bundles reverified. Fresh committed sibling-clone verification follows before push.

Fresh committed sibling checkouts passed: integration 119 passed / 7 expected private-fixture or optional-dependency skips / 8 inherited warnings; Data 12 passed. Final preservation scan again found zero missing inventoried files and no original 31/32 file changes. Git recognizes the Data archive and .gitmodules as 100% identical renames. Only seven obsolete mode-160000 submodule pointers are removed; component histories remain accessible as ancestors. Both target worktrees are clean after saving the publication evidence. Raw results remain local in validation/publication-preservation-and-clones.json.
