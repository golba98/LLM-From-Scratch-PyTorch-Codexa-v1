# Review publication and preservation — 2026-10-09

The user authorized commits, pushes and PR updates for LLM-Data and LLM-From-Scratch after the local audit. Existing Data PR #3 and integration PR #2 carry these changes. No PR is merged and no repository is deleted. The eight sibling repositories are saved under project 37; shared local infrastructure is workspace-infrastructure. Original 31 and 32 remain untouched and pending independent backup verification.

## What Git labels as removed

Integration removes seven mode-160000 submodule pointers and relocates .gitmodules to documentation/migration/submodules-before-2026-10-09.gitmodules. The pointers contain commit IDs, not component source; the seven real component working trees, histories and objects remain. Exact sibling paths and commits are recorded in compatibility.json. Data relocates its original integration-dependent test into documentation/migration/retained-tests/test_general_chat.py.txt with identical bytes. Its three tests remain active centrally. No substantive source file, checkpoint, dataset or repository is discarded.

The audit was not exclusively directory changes. Manifest/import resolution, dependency metadata, build/CLI tools and docs were updated, and the Data sampling CLI gained a main() that delegates to its existing implementation. Environment launch prefixes were repaired locally. Generated wheels/build logs were refreshed. Everything is accounted for by the local original inventory, move journal and edited-file hashes.

## Saved versus published

All migration files remain on disk beneath project 37 or the pre-existing configured external historical asset store. Public source/docs changes in these two repositories are committed and pushed to existing review branches. The user subsequently authorized publishing all remaining changes. All six remaining components' documentation edits are committed to their review branches; runtime code is unchanged. Workspace README/AGENTS and shared-infrastructure README have canonical tracked owners in documentation/workspace with local links. Shared private audit/recovery/build evidence remains local. Private settings, environments, checkpoint weights, datasets and recovery bundles are intentionally excluded from public Git, as required by repository guidelines. These are not deleted or relocated into PRs.

## Verification

The full initial audit found zero missing files across 66,474 inventory entries. Original 31/32 files, symlinks and Git state are unchanged. All ten original Git HEADs were preserved by directory restructuring; subsequent authorized publication commits advance the relevant repositories while retaining all earlier history. All ten histories pass Git integrity verification. All 517 historical assets (138,521,323,134 bytes) passed streaming SHA-256 plus metadata verification. Ten recovery bundles verified. Independent off-disk backup is still unavailable.

Prior complete validation: integration 121 passed / 5 skipped; Specialist package 39 passed; Specialist integration selection 58 passed; independent Architecture/Tokenizer/Data/Training/Inference/Memory 5/6/12/10/1/5 passed. Eight wheels built; 33 packaged module help commands passed; 52 applicable independent, dependency and installed-wheel probes passed. Exact references and deterministic sampling were verified. Existing optional-dependency skips and return-value warnings remain; clean-host dependency installation and production training are not claimed. Publication revalidation and fresh sibling-clone results are appended below before pushing.

Publication revalidation: integration 121 passed / 5 optional sklearn skips / 8 inherited return-value warnings; Data 12 passed; all eight wheels rebuilt; all 33 module CLI helps passed. All 517 asset size/mtime records and ten recovery bundles reverified. Fresh committed sibling-clone verification follows before push.

Fresh committed sibling checkouts passed: integration 119 passed / 7 expected private-fixture or optional-dependency skips / 8 inherited warnings; Data 12 passed. Final preservation scan again found zero missing inventoried files and no original 31/32 file changes. Git recognizes the Data archive and .gitmodules as 100% identical renames. Only seven obsolete mode-160000 submodule pointers are removed; component histories remain accessible as ancestors. Both target worktrees are clean after saving the publication evidence. Raw results remain local in validation/publication-preservation-and-clones.json.

## Complete source/documentation publication

All remaining component README/AGENTS changes are saved and published through their PRs. The central manifest pins their exact saved commits. Workspace-level documents are tracked in documentation/workspace and exposed through local symlinks, with no duplicate maintained copies. All eight repositories are checked for clean status, exact remote-branch synchronization and PR coverage. Latest independent component tests: Architecture 5, Tokenizer 6, Training 10, Inference 1, Memory 5, Specialist 39 passed. Integration/package/CLI and final preservation checks are repeated before the final push. No private artifacts are published or deleted; no original projects or repositories are removed.

Final all-repository publication revalidation passed: integration 121 passed / 5 optional sklearn skips; Architecture/Tokenizer/Training/Inference/Memory/Specialist 5/6/10/1/5/39 passed. Eight wheels rebuilt and 33 module CLI helps passed. All 517 asset metadata records and ten recovery bundles reverified. All review links and tracked workspace-document owners are listed in documentation/workspace/REVIEW_STATUS.md. Source/documentation is saved on review branches, not merged into default branches.
