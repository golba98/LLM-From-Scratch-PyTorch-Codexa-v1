# Codexa Session Decision Log

## 2026-08-21 — Native conversational quality probe failed

- Decision: Do not approve `checkpoints/codexa-900m-sft-v2/latest.pt` as a usable
  conversational model yet. Treat this as a behavioral-quality failure, not an
  inference-speed issue.
- Evidence: The native bridge loaded the checkpoint successfully on CPU, but
  CUDA was unavailable in the current PyTorch runtime (`torch.cuda.is_available()`
  returned `False`). A multi-turn probe against this 900M checkpoint produced a
  generic greeting that hit the 24-token length limit, then repeated the
  weather-app answer for an arithmetic prompt. Fresh isolated 900M probes also
  failed: `17 + 25` produced `1. Two numbers and a short calculation` and a
  three-bullet tea request produced unrelated exercise instructions; both hit
  the 16-token length limit instead of emitting `<|end|>`. A separate reset
  probe against the retained 100M SFT pilot showed the same class of failures:
  incorrect arithmetic/explanation, generic continuations, and unreliable
  stopping. The bridge also reports the hard-coded 900M model name for that
  older pilot, which should be corrected before using bridge metadata as proof.
- Affected paths: `checkpoints/codexa-900m-sft-v2/latest.pt`,
  `checkpoints/tokenizer-base-v1/tokenizer.json`, `scripts/native_chat_bridge.py`,
  and `src/native_chat.py`.
- Next action: Audit role-token serialization, assistant-only labels, checkpoint
  lineage, and EOS/`<|end|>` supervision with a deterministic 100–500-example
  overfit diagnostic. Require readable greeting, arithmetic, explanation,
  correction, multi-turn memory, and reliable stop behavior before any further
  checkpoint promotion or export.

## 2026-08-21 — Chat protocol overfit gate passed

- Decision: Accept the chat serialization and native stopping path as
  mechanically functional; move the investigation to the 900M SFT data,
  checkpoint lineage, and optimization recipe.
- Evidence: Added `scripts/run_chat_overfit.py` and its viewer launcher. The
  300-step CUDA diagnostic used the real 16,384-token tokenizer, four fixed
  user/assistant examples, assistant-only next-token labels, greedy decoding,
  and `<|end|>` stopping. Loss fell from `9.625757` to `0.0001216`; all four
  expected answers were reproduced exactly and all four generations terminated
  with `stop_token`. Focused regression coverage is `14 passed`.
- Affected paths: `scripts/run_chat_overfit.py`,
  `scripts/run_chat_overfit.sh`, `tests/test_sft_serialization.py`, and
  `scripts/native_chat_bridge.py`; diagnostic evidence is under
  `logs/chat-overfit-diagnostic-v1/`.
- Next action: inspect the 900M SFT records and training composition, then run
  a larger bounded SFT sanity experiment from the verified base checkpoint.
  Do not delete or replace the existing 900M checkpoints yet.

## 2026-08-21 — 900M SFT sanity recipe rejected

- Decision: Reject `codexa-900m-sft-sanity-v1` as a candidate model. Preserve
  its checkpoint for comparison and do not export or promote it.
- Evidence: The run loaded the checksum-verified
  `checkpoints/codexa-900m-base-v1/latest.pt`, completed 205 CUDA optimizer
  steps over approximately 5.06M tokens with finite loss, and wrote a valid
  checkpoint whose SHA-256 sidecar passes. After reload, multi-turn and
  reset-isolated probes collapsed into repeated agricultural-field text,
  failed arithmetic and explanation, failed the three-bullet tea instruction,
  and frequently stopped by the 48-token length limit. The final training loss
  was `1.376913`; numerical completion did not produce behavioral quality.
- Affected paths: `scripts/run_900m_sft_sanity.sh`,
  `checkpoints/codexa-900m-sft-sanity-v1/latest.pt`,
  `logs/codexa-900m-sft-sanity-v1/`, and the preserved base checkpoint.
- Next action: do not repeat the first-500-record recipe. Build a seeded,
  source-balanced and length-balanced diagnostic subset, reduce the SFT update
  aggressiveness or increase replay protection, and compare against the base
  checkpoint with fixed behavioral probes before another longer run.

This file records the decisions made during each Codexa development session.
Entries are append-only and include the reason, affected artifacts, and next
action.

## 2026-08-11 — Native SFT-v2 quality evaluation and retention gate

- Decision: Treat `checkpoints/codexa-900m-sft-v2/latest.pt` as loadable but not
  quality-approved for reasoning or conversational use. Do not delete any
  checkpoint, dataset, tokenizer, export, or log until the retention set is
  explicitly confirmed.
- Evidence: The checkpoint passed checksum/load through
  `src.native_chat.NativeChatEngine` on CPU. A bounded native probe produced a
  relevant photosynthesis explanation but truncated at the length limit, and
  answered `17 * 24` incorrectly with repeated text (`The multiplication by
  24 is 16`) before stopping. The generic evaluator also rejected this legacy
  checkpoint payload because it lacks `format_version`; the native loader's
  legacy fallback was used for the probe. The active Python installation is
  CPU-only despite an available RTX 4080, so full prompt-suite evaluation was
  not completed in this session.
- Affected paths: `checkpoints/codexa-900m-sft-v2/latest.pt`,
  `checkpoints/tokenizer-base-v1/tokenizer.json`,
  `scripts/evaluate_checkpoint.py`, `src/native_chat.py`, and
  `logs/codexa-900m-sft-v2/train_metrics.jsonl`.
- Next action: Preserve the model plus its tokenizer and architecture metadata;
  obtain confirmation of the exact disposable directories, then use reversible
  cleanup only after confirming no active process references them. Re-run the
  complete behavior suite with a CUDA-enabled PyTorch environment before any
  production-quality claim.

## 2026-08-03 — LM Studio compatibility and next training phase

### Decisions

1. The existing `codexa-100m-base-v1` checkpoint remains a native PyTorch
   training artifact and is not accepted as the LM Studio release model.
2. The GPT-2/Llama GGUF adapters are compatibility experiments only. They are
   not quality-approved because their runtime architecture does not exactly
   match the trained Codexa architecture.
3. The next 100M model will use an LM Studio-compatible architecture from the
   beginning: RMSNorm, SwiGLU, rotary position embeddings, and exact tokenizer
   mapping.
4. The next base phase will use the existing FineWeb-Edu/Wikipedia mixed corpus
   and its untouched validation splits.
5. Conversational SFT will use the prepared UltraChat and OASST1 datasets with
   assistant-only labels and a small percentage of base-language replay.
6. Every evaluation checkpoint will record complete fixed-prompt outputs and
   metrics in `documentation/training/100M_PROGRESS_LOG.md`.
7. This decision log will receive a dated entry after every future session.

### Evidence

- Native checkpoint completed 10,000 optimizer steps and processed
  655,360,000 tokens.
- Native validation loss was 3.61696 and perplexity was 37.22.
- LM Studio accepted the generated GGUF files, but generation was malformed
  and highly repetitive, confirming that loading alone is not a quality gate.
- The trained Codexa model uses learned absolute position embeddings while the
  Llama adapter uses rotary position embeddings.

### Next action

Implement and validate the native LM Studio-compatible model architecture
before starting the replacement 100M training run.

## 2026-08-03 — Native rotary architecture gate

### Decisions

1. Preserve the legacy learned-position mode for existing checkpoints and
   configs; add rotary mode as a separate selectable architecture.
2. Use `configs/100m-native.yaml` for the replacement training run.
3. Export native checkpoints through the Llama-compatible GGUF path rather than
   adapting an already-trained learned-position checkpoint.
4. Treat a clean llama.cpp/LM Studio model load and tokenizer metadata check as
   a pre-training gate.

### Evidence

- Rotary forward/backward smoke passed with 125,848,320 parameters.
- Legacy learned-position configs still load and run unchanged.
- A native rotary checkpoint exported to GGUF successfully with 111 tensors.
- Bundled llama.cpp loaded the GGUF and returned `{"status":"ok"}` without
  the previous special-token metadata warnings.

### Next action

Run the replacement 100M base training job from `configs/100m-native.yaml`,
then evaluate native and LM Studio generations before beginning conversational
SFT.

## 2026-08-03 — Native 100M training started

### Decisions

1. Start a separate run named `codexa-100m-native-v1`; do not overwrite the
   completed learned-position checkpoint.
2. Keep the same 10,000-step base-training schedule and mixed token corpus so
   the architecture comparison remains interpretable.
3. Expose the run through a dedicated 100x22 Kitty progress viewer with steps,
   speed, loss, tokens, elapsed time, and ETA.

### Evidence

- The native run reached optimizer step 13 successfully.
- Current speed is approximately 52,170 tokens/second on CUDA BF16.
- Current training loss is 9.7109 during early warmup.
- GPU utilization is active and no training error has occurred.

### Next action

Let the native run complete, then run the fixed evaluation suite and export the
accepted checkpoint to GGUF for an LM Studio generation comparison.

## 2026-08-03 — Viewer command corrected

### Decision

The documented viewer command now targets `codexa-100m-native-v1` through the
`CODEXA_TRAINING_RUN` environment variable. It attaches to the active native
run and cannot accidentally restart the legacy base run.

### Evidence

- `scripts/open_100m_training_viewer.sh` passes shell syntax validation.
- `commands/TRAINING_VIEWER.md` now opens the native run by default.

## 2026-08-03 — Native run completed and evaluated

### Decision

Accept `codexa-100m-native-v1` as the new compatible base checkpoint for the
next training stage, but do not call it conversationally ready yet.

### Evidence

- Completed 10,000 optimizer steps and 655,360,000 tokens.
- Validation perplexity improved from 37.22 to 30.89.
- Native GGUF loaded in LM Studio and generated without the prior protocol
  failure.
- Generation still shows severe repetition, so the quality gate remains open.

### Next action

Run the fixed output logger against this checkpoint, then continue base replay
or controlled training before assistant-only conversational SFT.

## 2026-08-03 — Stale LM Studio model removed from active session

### Decision

The old `codexa-100m-base-v1-lmstudio-llama` adapter is not to be used for
quality testing. LM Studio was unloaded from that model and the active model
was changed to `codexa-100m-native-v1-lmstudio`.

### Evidence

- The reported malformed output identified the old adapter model by name.
- LM Studio now reports `codexa-100m-native-v1-lmstudio` as the loaded Llama
  model.
- The old adapter remains on disk only as a historical artifact; it is not an
  accepted checkpoint.

## 2026-08-03 — Full LM Studio behavior test

### Decision

Use the native LM Studio model for future evaluation and treat the current
checkpoint as runtime-compatible but not behaviorally ready.

### Evidence

- Six LM Studio prompts completed without a runtime/protocol error.
- Prose continuation showed topic drift and repetition.
- Factual explanation, instruction following, arithmetic, and conversation
  failed.
- The complete transcript is recorded in
  `logs/codexa-100m-native-v1/lmstudio_test_2026-08-03.md`.

### Next action

Prioritize repetition/degeneration reduction through continued base training
and fixed evaluation before conversational SFT; preserve this transcript as the
first behavioral baseline.

## 2026-08-03 — Natural multi-turn chat test

### Decision

Do not expose the current native base checkpoint as a chat model. Require
conversational SFT and repeat the same multi-turn memory test after each SFT
checkpoint.

### Evidence

- Four-turn chat ignored the greeting and user-provided facts.
- The model failed to recall the name Maya and Cape Town.
- It ignored astronomy and emitted unrelated repeated health text.
- The complete conversation is recorded in
  `logs/codexa-100m-native-v1/multi_turn_chat_2026-08-03.md`.

### Next action

Implement the assistant-only SFT dataloader and train a first conversational
checkpoint from the prepared UltraChat/OASST1 data with base replay.

## 2026-08-03 — Conversational SFT pilot started

### Decision

Start a bounded 2,000-step conversational SFT pilot from the native 100M
checkpoint. Use 60,000 UltraChat conversations, 1,000 validation conversations,
and 10% mixed-base replay to reduce catastrophic forgetting.

### Runtime

- Viewer: `scripts/run_100m_sft_pilot.sh` in a 100×22 Kitty terminal
- Base checkpoint: `checkpoints/codexa-100m-native-v1/latest.pt`
- Metrics: `logs/codexa-100m-sft-pilot/train_metrics.jsonl`
- Pilot checkpoint: `checkpoints/codexa-100m-sft-pilot/latest.pt`

### Initial evidence

- Startup/import issue fixed before launch by making the repository importable
  from the script path.
- Optimizer steps are running; early loss is approximately 2.1–2.8 while the
  learning rate warms up.
- The viewer reports steps, tokens/second, loss, validation loss, elapsed time,
  and ETA.

## 2026-08-03 — Checkpoint retention and session logging policy

### Decision

Record every consequential update in this file and keep progress details in
`100M_PROGRESS_LOG.md`. After a successful training run, remove only that
run's disposable `.pt` checkpoints after export and native/exported smoke-test
validation. Preserve model exports, tokenizer files, datasets, logs, and any
active or recoverable run.

### Storage evidence

- Legacy base checkpoints: 62G.
- Native base checkpoints: 61G.
- Tiny overfit checkpoints: 1.7G.
- Active SFT checkpoint: 481M.
- Exported model files and tokenizer remain outside the cleanup target.

No deletion was performed in this update because the SFT pilot is still
running and the native checkpoint remains its recovery source.

## 2026-08-03 — Automatic training progress viewer

### Decision

Every future model-training launch must automatically open or attach the
100×22 Kitty progress viewer. Its progress-bar line must always include an
`ETA HH:MM:SS`; the viewer also reports steps, tokens/second, losses, total
tokens, and checkpoint path without requiring a follow-up request.

### Implementation

The SFT viewer is `scripts/view_100m_sft_progress.sh`, and the launch wrapper
is `scripts/run_100m_sft_pilot.sh`.

## 2026-08-03 — Complete two-source base corpus preparation after session restart

### Decision

Resume verification of the deterministic FineWeb-Edu plus Wikipedia preparation
stage after the interactive session restarted. The completed output is retained
and is not regenerated or overwritten.

### Evidence

- `data/processed/base-v1/base_preparation_manifest.json` exists and records
  `elapsed_seconds: 6590.489408666996` (1h 49m 50s).
- Wikipedia: 6,406,791 accepted documents from 6,407,814 rows; 1,023 exact
  within-source duplicates rejected; 31,957 validation documents.
- FineWeb-Edu: 7,043,681 accepted documents from 7,293,000 rows; 249,319 exact
  within-source duplicates rejected; 35,232 validation documents.
- The manifest records SHA-256 checksums for all 51 input Parquet files and all
  four output JSONL splits. Near-duplicate clustering remains explicitly
  deferred.
- Output size is approximately 54 GB under `data/processed/base-v1`.

### Affected paths

- `scripts/prepare_base_corpus.py`
- `data/processed/base-v1/`
- `documentation/planning/PHASE_PLAN.md`
- `documentation/planning/TRAINING_DATA_PLAN.md`

### Next action

Verify output checksums and split isolation, then run the tokenizer bake-off and
post-tokenization accounting. Do not launch base training until the tokenizer,
mixture, token budget, and production-shape benchmark gates pass.

## 2026-08-03 — Keep a completed preparation viewer visible

### Decision

The live preparation viewer ended with the process, which left no visible
100%-complete progress screen after the session restarted. Reopen a 100×22
Kitty terminal containing the final progress bar and output counts after a
completed preparation run.

### Evidence

- The preparation process and live dashboard are no longer running.
- The completed viewer reports 100%, 13,700,814 raw rows, 13,450,472 accepted
  documents, 01:49:50 elapsed, and the final manifest path.

### Affected paths

- `/tmp/codexa-base-prep-complete.sh`
- `data/processed/base-v1/base_preparation_manifest.json`

### Next action

Use the same persistent visible-viewer convention for tokenizer bake-off,
tokenization, benchmarking, and every future training launch.

## 2026-08-03 — Replace training viewer with compact completion dashboard

### Decision

Use one shared 100×22 Kitty dashboard for native base and conversational SFT
launches. It keeps the straight progress bar, percentage, `ETA HH:MM:SS`,
steps, token speed, losses, total tokens, and checkpoint path visible while
running and after completion.

### Evidence

- The native base log ends at 10,000/10,000 steps and has a completed latest
  checkpoint; no training process is running.
- The new viewer was syntax-checked and rendered the completed native run with
  `COMPLETE`, 100%, validation loss, token total, and checkpoint path.

### Affected paths

- `scripts/training_viewer.sh`
- `scripts/open_100m_training_viewer.sh`
- `scripts/run_100m_native_training.sh`
- `scripts/view_100m_sft_progress.sh`
- `scripts/run_100m_sft_pilot.sh`

### Next action

Use the completed native checkpoint only after the existing export and native
smoke-test acceptance checks are verified; do not launch another training run
from this viewer change.

## 2026-08-03 — Resume SFT pilot to its planned endpoint

### Decision

Resume `codexa-100m-sft-pilot` from its last saved checkpoint at optimizer step
1,500 and continue to the planned 2,000 steps. The immutable native base
checkpoint remains the source model and is not modified.

### Evidence

- `checkpoints/codexa-100m-sft-pilot/latest.pt` reports optimizer step 1,500.
- The prior metrics log reached step 1,617 before interruption.
- The resumed process is active and has appended new metrics; the shared Kitty
  dashboard is attached to it.

### Affected paths

- `scripts/train_conversational_sft.py`
- `scripts/run_100m_sft_pilot.sh`
- `checkpoints/codexa-100m-sft-pilot/latest.pt`
- `logs/codexa-100m-sft-pilot/`

### Next action

Wait for step 2,000, then verify the final checkpoint and run the SFT smoke and
evaluation gates before exposing any conversational checkpoint.

## 2026-08-03 — Restore the mandatory visible progress viewer

### Decision

Treat the Kitty dashboard as part of the training run, not an optional aid.
When the viewer disappeared while the SFT process remained active, reattach a
100×22 dashboard to the live PID immediately.

### Evidence

- SFT process PID 14205 remains active at optimizer step 1,587.
- The dashboard was restored with `scripts/training_viewer.sh` and points at
  the live metrics and checkpoint paths.

### Affected paths

- `scripts/training_viewer.sh`
- `logs/codexa-100m-sft-pilot/train_metrics.jsonl`

### Next action

Keep the viewer attached through step 2,000 and report its location with every
live training status update.

## 2026-08-03 — Restore the minimal training-monitor aesthetic

### Decision

Replace the dense box-drawing dashboard with the earlier minimal terminal
layout: strong title hierarchy, ASCII progress bar, compact metric rows, and
clear checkpoint/log sections. This avoids broken Unicode glyphs and preserves
the required 100×22 Kitty presentation.

### Evidence

- The updated viewer renders cleanly in a 100-column terminal and reports the
  live SFT run at step 1,721/2,000.
- Training process PID 14205 remains active; no model or dataset artifacts were
  changed.

### Affected paths

- `scripts/training_viewer.sh`

### Next action

Keep this shared viewer as the default for all future Codexa training launches.

## 2026-08-03 — Stack training telemetry in one aligned column

### Decision

Present steps, speed, training loss, validation loss, tokens, and elapsed time
as a straight vertical list below the progress bar. This matches the operator
workflow and avoids split-column scanning in the 100×22 terminal.

### Evidence

- The viewer syntax-checks successfully and renders all telemetry as aligned
  rows against the live SFT metrics.
- The dashboard was relaunched and remains attached to the active training PID.

### Affected paths

- `scripts/training_viewer.sh`

### Next action

Keep the vertical telemetry layout for completed and future training runs.

## 2026-08-03 — Save the approved viewer appearance

### Decision

Keep a checked-in visual reference for the current minimal dashboard so future
viewer changes preserve its hierarchy, spacing, and vertical metric ordering.

### Evidence

- The reference mirrors the dashboard currently attached to the live SFT run.
- It documents the ASCII bar, metric order, checkpoint/log placement, and
  100×22 terminal constraint.

### Affected paths

- `documentation/training/TRAINING_VIEWER_STYLE.md`
- `scripts/training_viewer.sh`

### Next action

Use the reference when modifying the viewer or adding another training
launcher.

## 2026-08-03 — Complete conversational SFT pilot

### Decision

Mark `codexa-100m-sft-pilot` complete at its planned 2,000 optimizer steps.
Retain the checkpoint as a recoverable artifact until export and native/exported
smoke tests pass.

### Evidence

- Final metrics report 2,000/2,000 steps and 15,784,215 processed tokens.
- Final training loss is 2.198 and validation loss is 2.003.
- No SFT training process remains active.
- `checkpoints/codexa-100m-sft-pilot/latest.pt` exists at 481 MB.

### Affected paths

- `logs/codexa-100m-sft-pilot/train_metrics.jsonl`
- `checkpoints/codexa-100m-sft-pilot/latest.pt`

### Next action

Run checkpoint integrity, conversational evaluation, and export smoke gates;
do not delete the checkpoint before those checks succeed.

## 2026-08-03 — Remove obsolete LM Studio entries and open native model

### Decision

Remove the obsolete GPT-2 and pre-native Llama model entries from the LM
Studio library, remove the unused `golba98/codexa-openai-adapter` plugin, and
leave the accepted native Llama export available. Keep repository checkpoints,
exports, and tokenizer artifacts until their required evaluation/export gates
are complete.

### Evidence

- Moved these exact obsolete library directories to the user Trash:
  `codexa-100m-base-v1-lmstudio-f16` and
  `codexa-100m-base-v1-lmstudio-llama-f16` (approximately 505 MB total).
- Moved the exact 17 MB adapter plugin directory to Trash.
- LM Studio now reports 17 models and no Codexa adapter; only
  `codexa-100m-native-v1-lmstudio` remains.
- Loaded `codexa-100m-native-v1-lmstudio` successfully through `lms`; it is
  available in the LM Studio UI/API.

### Affected paths

- `/home/k9-vortex/LMStudioLocalTest/lmstudio-community/k9-vortex/`
- `/home/k9-vortex/.cache/lm-studio/extensions/plugins/golba98/`
- `exports/codexa-100m-native-v1-lmstudio-f16.gguf` (preserved)

### Next action

Evaluate the conversational SFT checkpoint and export it separately before
replacing the native LM Studio model; do not delete recoverable checkpoints.

## 2026-08-03 — Remove disposable training artifacts after storage audit

### Decision

Preserve the cleaned/raw/tokenized corpora, the active native checkpoint, the
completed SFT checkpoint, tokenizer, and exports. Move only verified disposable
artifacts to the user Trash: the completed old base checkpoint, tiny-overfit
checkpoint, and three failed production-shape benchmark runs.

### Evidence

- Native checkpoint is actively loaded by LM Studio and remains untouched.
- Old base exports exist under `exports/`, and no process references the old
  checkpoint directory.
- Removed exact artifact sizes: 62 GB old base checkpoint, 1.7 GB tiny
  overfit checkpoint, and approximately 48 GB failed benchmark logs/checkpoint
  directories.
- Remaining live storage in this repository is approximately 146 GB data,
  61 GB native checkpoint, 481 MB SFT checkpoint, 403 MB logs, and 2.1 GB
  exports.

### Affected paths

- `checkpoints/codexa-100m-base-v1/` (moved to Trash)
- `checkpoints/tiny-overfit-base-v1/` (moved to Trash)
- `logs/production-shape-v1/` (moved to Trash)
- `logs/production-shape-v1-failed-20260802-evaluation/` (moved to Trash)
- `logs/production-shape-v1-failed-20260802-rerun/` (moved to Trash)

### Next action

Empty the user Trash when ready to reclaim the physical disk space; do not
remove the preserved corpora or active/recoverable model checkpoints.

## 2026-08-03 — Pass 900M-class production-shape gate

### Decision

Proceed with the 900M-class base run using the existing 16K-token data and
current 934,356,480-parameter configuration. The proven memory shape is BF16,
activation checkpointing, 8-bit AdamW, microbatch 1, and gradient accumulation
32. The production budget is 10,000 optimizer steps (655,360,000 tokens).

### Evidence

- The 12-step production gate passed at 7,700.7 tokens/second.
- Peak reserved VRAM was 12.92 GB with 3.83 GB headroom on the RTX 4080.
- Validation and fixed-prompt generation completed successfully.

### Affected paths

- `configs/1b.yaml`
- `logs/production-shape-900m-v1/production_shape_benchmark.json`
- `data/tokenized/base-v1/mixed/train.bin`

### Next action

Launch the 10,000-step run from random weights and monitor it through the
mandatory Kitty dashboard; preserve every resumable checkpoint.

## 2026-08-03 — Pause 900M-class base training

### Decision

Pause the live `codexa-900m-base-v1` process with `SIGSTOP` so it can resume
in-place without losing its current GPU state. Do not terminate the process.

### Evidence

- Process PID 33993 is stopped (`TNsl`) at optimizer step 418 and 27,394,048
  processed tokens.
- A durable atomic checkpoint exists at step 250 in
  `checkpoints/codexa-900m-base-v1/latest.pt` with checksum and completion
  metadata.
- The Kitty viewer remains attached to the stopped process.

### Affected paths

- `checkpoints/codexa-900m-base-v1/latest.pt`
- `logs/codexa-900m-base-v1/train_metrics.jsonl`

### Next action

Resume in place with `kill -CONT 33993`; if the process must be restarted,
resume from `checkpoints/codexa-900m-base-v1/latest.pt` at step 250.

## 2026-08-03 — Pause after next 900M checkpoint for interactive use

### Decision

Resume the stopped base process only through the next checkpoint, then pause
it again so GPU resources are available for the user. The process is now
paused after checkpoint step 500.

### Evidence

- Process PID 33993 is stopped (`TNsl`).
- Durable checkpoint `checkpoints/codexa-900m-base-v1/latest.pt` reports
  optimizer step 500 and has completion/checksum sidecars.
- Training remains recoverable without deleting any model artifacts.

### Affected paths

- `checkpoints/codexa-900m-base-v1/latest.pt`
- `logs/codexa-900m-base-v1/train_metrics.jsonl`

### Next action

The user can play games now. Resume with `kill -CONT 33993` when ready.

## 2026-08-04 — Resume 900M-class base training after logout

### Decision

The stopped process did not survive logout, so resume the base run from its
verified step-500 checkpoint. Start a fresh detached process with the standard
vertical Kitty dashboard attached.

### Evidence

- `checkpoints/codexa-900m-base-v1/latest.pt` reports optimizer step 500.
- The resumed process is active as PID 8719 with the expected config,
  optimizer, BF16 precision, and activation checkpointing.
- The viewer is attached as PID 8720.

### Affected paths

- `checkpoints/codexa-900m-base-v1/latest.pt`
- `logs/codexa-900m-base-v1/`

### Next action

Continue monitoring from step 500 toward the 10,000-step budget; preserve each
250-step checkpoint.

## 2026-08-04 — Complete and verify 900M-class base training

### Decision

Mark `codexa-900m-base-v1` training complete at 10,000 optimizer steps. Keep
the final checkpoint and all milestone checkpoints for evaluation and export.

### Evidence

- Final metrics: 10,000 steps, 655,360,000 tokens, training loss 3.1042,
  validation loss 3.3491.
- `latest.pt` reports optimizer step 10,000, format version 1, complete=true,
  and SHA-256 `808afec9923e3f00d91bcbef47643265ae5dbe6c5aeb4bd112c4e97be3d0a3a7`.
- No training process remains active.
- The interrupted temporary checksum artifact was moved to Trash; no temporary
  checkpoint files remain.

### Affected paths

- `checkpoints/codexa-900m-base-v1/latest.pt`
- `checkpoints/codexa-900m-base-v1/latest.pt.complete.json`
- `logs/codexa-900m-base-v1/train_metrics.jsonl`

### Next action

Run the fixed base-model evaluation suite, then export and smoke-test the
selected checkpoint before beginning conversational SFT.

## 2026-08-04 — Remove obsolete 900M benchmark checkpoints

### Decision

Keep the final 900M model, all resumable 900M milestones, native lineage,
training corpus, tokenizer, and SFT checkpoint. Remove only the disposable
production-shape benchmark checkpoint artifacts after the gate report was
recorded.

### Evidence

- The benchmark report, config, and evaluation JSON remain in
  `logs/production-shape-900m-v1/`.
- The exact nested benchmark checkpoint directory was 16 GB and is no longer
  needed for recovery or evaluation.
- The final 900M checkpoint and native model were not touched.

### Affected paths

- `logs/production-shape-900m-v1/checkpoints/` (moved to Trash)
- `logs/production-shape-900m-v1/production_shape_benchmark.json` (preserved)
- `checkpoints/codexa-900m-base-v1/` (preserved)

### Next action

Export and smoke-test the final 900M model. Only then evaluate deleting
redundant 900M milestone/optimizer checkpoints; retain at least one verified
recoverable checkpoint until the successor is accepted.

## 2026-08-03 — Conversational quality evaluation failed

### Decision

Do not expose either the native LM Studio export or the 100M SFT pilot as an
accepted chat model. The native export remains the loaded diagnostic model;
the SFT checkpoint remains preserved for further experiments.

### Evidence

- Native LM Studio probes repeated prompts, drifted into unrelated text, and
  failed simple factual, list, story, and memory prompts.
- Direct generation from the completed SFT checkpoint produced recognizable
  answers for photosynthesis and the Amina memory prompt, but repeated each
  answer many times and failed the requested conversational stopping behavior.
- The SFT checkpoint is a 100M pilot, not the approved 1B production model.

### Affected paths

- `logs/codexa-100m-sft-pilot/train_metrics.jsonl`
- `checkpoints/codexa-100m-sft-pilot/latest.pt`
- `logs/codexa-100m-native-v1/lmstudio_test_2026-08-03.md`

### Next action

Audit SFT serialization, assistant-only masks, EOS supervision, and stopping;
run a longer controlled SFT/replay comparison, then repeat deterministic chat
and base-regression gates before exporting any conversational model.

## 2026-08-04 — 900M base exported and redundant training artifacts retired

### Decision

Select the verified step-10,000 900M-class checkpoint as the immutable base
model handoff. Keep the final checkpoint and one recovery copy; remove only
intermediate milestone and staging artifacts after export and smoke validation.

### Evidence

- Native checkpoint generation completed with a deterministic factual
  continuation from `latest.pt`.
- GGUF export completed successfully and was parsed as 293 tensors with a
  GPT-2 architecture, 2,048 context length, and 16,384-token vocabulary.
- Export SHA256: `506bbd45becc4b711cd512f204260d3496b3d5c76aa966d276f476f7dd8e789d`.
- 84 redundant files/directories (approximately 215G) were moved to Trash,
  not permanently deleted; physical reclamation requires emptying Trash.

### Affected paths

- Preserved: `checkpoints/codexa-900m-base-v1/latest.pt`,
  `checkpoints/codexa-900m-base-v1/previous.pt` and integrity sidecars.
- Preserved: `exports/codexa-900m-base-v1-lmstudio-f16.gguf`.
- Moved to Trash: all 900M milestone files, `best.pt` and sidecar, and the
  intermediate HF export directories.
- Changed exporter metadata naming in `scripts/export_codexa_lmstudio.py` and
  `scripts/export_codexa_llama_lmstudio.py` to use the actual artifact name.

### Next action

Run the fixed base evaluation suite, then prepare tree-safe UltraChat/OASST1
SFT data. The exported base is not yet an accepted conversational model.

## 2026-08-04 — LM Studio catalog import verified; runtime load deferred

### Decision

Import the 900M GGUF into LM Studio for visibility, but do not replace the
working 100M native model or claim LM Studio inference acceptance yet.

### Evidence

- LM Studio indexed `codexa-900m-base-v1-lmstudio` as a 900M F16 GGUF with
  2,048-token context and the expected GPT-2 architecture.
- The llama-server runtime exited before becoming healthy when loading it.
- Native CUDA generation from the original checkpoint remains successful.

### Affected paths

- LM Studio catalog entry: `codexa-900m-base-v1-lmstudio`.
- Preserved export: `exports/codexa-900m-base-v1-lmstudio-f16.gguf`.

### Next action

Investigate a runtime-compatible exporter for Codexa's learned-position
architecture before exposing this checkpoint through LM Studio. Do not change
the architecture or silently substitute rotary embeddings.

## 2026-08-04 — 900M LM Studio load repaired

### Decision

Keep the trained architecture unchanged and correct the GGUF tokenizer metadata
only: llama.cpp expects `gpt-2`, not `gpt2`, for this ByteLevel BPE tokenizer.

### Evidence

- Direct llama-server diagnostics identified the original failure as
  `unknown pre-tokenizer type: 'gpt2'`.
- The regenerated GGUF reports `tokenizer.ggml.pre = gpt-2`.
- LM Studio successfully loaded `codexa-900m-base-v1-lmstudio` to 100% in
  1.26 seconds; it is idle at 1.47 GB with 2,048 context.
- The CLI chat wrapper rejects the base model's prompt as non-chat-native;
  this is expected before conversational SFT. Text-completion evaluation is
  the correct current interface.

### Affected paths

- `exports/codexa-900m-base-v1-lmstudio-f16.gguf`
- LM Studio catalog entry `codexa-900m-base-v1-lmstudio`

### Next action

Evaluate the loaded base model with completion prompts, then build and train
the approved conversational SFT datasets. Do not expose it as a chat model yet.

## 2026-08-04 — Base behavior and LM Studio fidelity check failed

### Decision

Do not treat the current LM Studio GGUF as an accepted model export. Preserve
the native checkpoint as the source of truth and defer public use of the GGUF.

### Evidence

- Native CUDA generation is executable but repeats the prompt heavily, which is
  a quality limitation of the unsupervised base checkpoint before SFT.
- LM Studio loads the GGUF, but direct completion produces corrupted output.
- The compatibility exporter maps Codexa RMSNorm and gated feed-forward blocks
  into GPT-2 LayerNorm and non-gated FFN tensors; this is not behaviorally
  equivalent even though the file is structurally loadable.

### Next action

Implement a faithful runtime exporter or use the native Codexa inference path.
Do not claim LM Studio output quality until an equivalence test against native
logits and fixed prompts passes.

## 2026-08-04 — 900M conversational SFT launched with memory-safe optimizer

### Decision

Begin the approved conversational SFT pilot from the immutable 900M base
checkpoint using the prepared UltraChat/OASST1-compatible serialization and a
controlled 10% base-language replay. Keep the base checkpoint unchanged.

### Evidence

- The first full-AdamW attempt reached optimizer step 1 with loss 2.5141 but
  exceeded the 16 GB GPU during step 2.
- The retry uses bitsandbytes AdamW8bit plus the existing activation
  checkpointing implementation; it is running successfully through step 9.
- Current measured peak allocated VRAM is approximately 11.98 GB, with no OOM.
- Current throughput is approximately 3,900–4,500 tokens/second and the live
  100x22 viewer is attached.

### Affected paths

- `scripts/train_conversational_sft.py`
- `scripts/run_900m_sft.sh`
- `logs/codexa-900m-sft-v1/`
- `checkpoints/codexa-900m-sft-v1/` (active run)
- Source checkpoint preserved at `checkpoints/codexa-900m-base-v1/latest.pt`.

### Next action

Let the 2,000-step pilot complete, validate its checkpoint and chat/base
regression metrics, then compare against a pure-SFT variant before selecting a
conversational successor.

## 2026-08-04 — 900M SFT paused safely for host switch

### Decision

Stop the active SFT process after a durable checkpoint so the host can switch
to Windows without losing recoverable training state.

### Evidence

- The active run reached optimizer step 285; the latest durable checkpoint is
  verified at optimizer step 250.
- `checkpoints/codexa-900m-sft-v1/latest.pt` is present at approximately 3.7 GB.
- The process was terminated after checkpoint verification; no training process
  remains active.
- Base checkpoint `checkpoints/codexa-900m-base-v1/latest.pt` is untouched.

### Affected paths

- `checkpoints/codexa-900m-sft-v1/latest.pt`
- `logs/codexa-900m-sft-v1/train_metrics.jsonl`

### Next action

Resume from `checkpoints/codexa-900m-sft-v1/latest.pt` after returning to
Linux. Do not resume from the immutable base checkpoint or delete this SFT
checkpoint.

## 2026-08-04 — 900M SFT resumed from step 250

### Decision

Resume the conversational SFT pilot from its verified step-250 checkpoint
after the host switch.

### Evidence

- Resume loaded `checkpoints/codexa-900m-sft-v1/latest.pt` at step 250.
- Training is active at step 257 with loss 2.5475 and approximately 3,300–4,100
  tokens/second.
- Activation checkpointing and AdamW8bit remain enabled; peak allocated VRAM
  remains approximately 11.98 GB.
- The live 100x22 training viewer is restored.

### Affected paths

- `scripts/run_900m_sft.sh`
- `checkpoints/codexa-900m-sft-v1/latest.pt`
- `logs/codexa-900m-sft-v1/`

### Next action

Continue to the 2,000-step pilot checkpoint, then run conversational and base
regression evaluation before selecting a successor.

## 2026-08-05 — 900M SFT pilot complete but conversational gate failed

### Decision

Preserve the completed 900M SFT checkpoint for analysis, but do not expose it
as the conversational model yet.

### Evidence

- The pilot completed at optimizer step 2,000 with training loss 2.0080 and
  validation loss 1.9259 (perplexity 6.86).
- Native greedy probe for a name question produced a relevant refusal-like
  opening but repeated `iphone` six times.
- Native greedy photosynthesis probe repeated the instruction instead of
  answering it and hit the generation limit.
- The checkpoint is checksum-protected at
  `checkpoints/codexa-900m-sft-v1/latest.pt`.

### Affected paths

- `checkpoints/codexa-900m-sft-v1/latest.pt`
- `checkpoints/codexa-900m-sft-v1/latest.pt.sha256`
- `logs/codexa-900m-sft-v1/train_metrics.jsonl`
- `scripts/generate.py` (supports inference from the pilot checkpoint format)

### Next action

Audit serialized prompt/label alignment, EOS supervision, truncation and
decoding before another SFT run. Compare pure SFT against controlled replay;
do not overwrite the immutable base or publish this pilot as chat-ready.

## 2026-08-05 — Chat stop-contract repair and SFT v2 preparation

### Decision

Treat `<|end|>` (the chat turn delimiter) as a required generation stop
sequence, and start the next conversational run from the immutable 900M base
with both approved conversational sources. Keep the failed v1 checkpoint for
comparison and do not overwrite it.

### Evidence

- The completed v1 checkpoint answered the correctly serialized Amina prompt
  cleanly when native generation stopped at token `<|end|>`.
- The existing CLI stopped only on `<eos>`, continued into subsequent turns,
  and produced the repeated output seen in LM Studio.
- The v1 LM Studio GGUF was structurally loadable but not behaviorally faithful:
  its compatibility exporter changes learned positions, RMSNorm, and the gated
  feed-forward path. The exporter now records the chat template for future
  exports, but LM Studio quality remains gated on an equivalence test.

### Affected paths

- `src/sft.py`
- `scripts/generate.py`
- `scripts/train_conversational_sft.py`
- `scripts/run_900m_sft.sh`
- `scripts/export_codexa_lmstudio.py`
- `tests/test_sft_serialization.py`

### Next action

Run `codexa-900m-sft-v2` for 6,000 steps with 30,000 examples per source,
validate multi-turn stopping natively, then export only if the chat and base
regression gates pass. Disable LM Studio web-search/tool mode during model
smoke tests because the model is not trained to emit tool-call protocol.

## 2026-08-05 — 900M SFT v2 paused safely for Windows switch

### Decision

Pause the active UltraChat-plus-OASST1 SFT v2 run after its latest durable
checkpoint so the host can switch operating systems safely.

### Evidence

- The v2 process was at optimizer step 521; its durable checkpoint is verified
  at step 500.
- `checkpoints/codexa-900m-sft-v2/latest.pt` is preserved and checksum-protected.
- The training process and its 100x22 viewer have been stopped.
- The immutable base and completed v1 SFT checkpoint remain unchanged.

### Affected paths

- `checkpoints/codexa-900m-sft-v2/latest.pt`
- `checkpoints/codexa-900m-sft-v2/latest.pt.sha256`
- `logs/codexa-900m-sft-v2/train_metrics.jsonl`

### Next action

Resume v2 from step 500 after returning to Linux. Do not delete this active
recovery checkpoint.
## 2026-08-05 — Resume conversational SFT v2 after host lag

- Decision: Resume `codexa-900m-sft-v2` from its highest durable checkpoint, `checkpoints/codexa-900m-sft-v2/latest.pt`, at optimizer step 1,750; do not resume from later log-only steps.
- Evidence: No training process is active; the checkpoint deserializes with a valid model state and `optimizer_step: 1750`; `sha256sum` produced `2364eaddc4668d077727ecf53b9dbb058e52852ef6151bad78537dcd6532e483`, while the prior sidecar was stale. The prior metrics reached step 1,836 and reported peak reserved VRAM of 12,920,553,472 bytes, consistent with the reported host lag.
- Affected paths: `checkpoints/codexa-900m-sft-v2/latest.pt`, `checkpoints/codexa-900m-sft-v2/latest.pt.sha256`, `logs/codexa-900m-sft-v2/train_metrics.jsonl`, `scripts/run_900m_sft.sh`.
- Next action: Relaunch the existing 6,000-step SFT command from the validated step-1,750 checkpoint and attach the visible 100×22 Kitty viewer; preserve all checkpoints and logs.
## 2026-08-05 — Resume confirmed at optimizer step 1,751

- Decision: Keep `codexa-900m-sft-v2` running from the validated step-1,750 checkpoint.
- Evidence: The resumed process is active as PID 6682; `train_metrics.jsonl` was truncated to 1,750 records and now contains a fresh optimizer-step 1,751 record with run ID `846dda94-8542-4eda-8b4b-8a92b5e08cb5`, training loss 2.5412, and peak reserved VRAM 11,070,865,408 bytes as reported by the metric. A separate Kitty viewer was launched with PID 6683 using the required 100×22 geometry.
- Affected paths: `logs/codexa-900m-sft-v2/train_metrics.jsonl`, `logs/codexa-900m-sft-v2/run_metadata.json`, `checkpoints/codexa-900m-sft-v2/latest.pt`, `scripts/train_conversational_sft.py`.
- Next action: Let the run continue toward step 6,000; validate the final checkpoint, export, and native/exported smoke test before any checkpoint cleanup.

## 2026-08-06 — Pause conversational SFT v2 for power outage

- Decision: Suspend the active `codexa-900m-sft-v2` process with `SIGSTOP` so the run can be resumed safely when power and connectivity return.
- Evidence: PID `6682` is stopped (`TNsl`); the required 100x22 Kitty viewer remains present and the latest durable checkpoint is `checkpoints/codexa-900m-sft-v2/latest.pt`, timestamped 2026-08-06 04:17:52. The latest observed metric reached optimizer step 5,117; no checkpoint or log files were deleted.
- Affected paths: `checkpoints/codexa-900m-sft-v2/latest.pt`, `checkpoints/codexa-900m-sft-v2/latest.pt.sha256`, `logs/codexa-900m-sft-v2/train_metrics.jsonl`.
- Next action: After power returns, resume PID `6682` with `kill -CONT 6682` only if its process and checkpoint are still present; otherwise relaunch from the validated `latest.pt` checkpoint and restore the 100x22 viewer.

## 2026-08-06 — Resume conversational SFT v2 after power restoration

- Decision: Continue `codexa-900m-sft-v2` from the paused process and preserved checkpoint.
- Evidence: `kill -CONT 6682` succeeded; PID `6682` is no longer stopped, and `train_metrics.jsonl` advanced to optimizer step `5118` at 2026-08-06 06:49:34 UTC. The 100x22 Kitty viewer remains attached as PID `8746`.
- Affected paths: `logs/codexa-900m-sft-v2/train_metrics.jsonl`, `checkpoints/codexa-900m-sft-v2/latest.pt`, `documentation/training/SESSION_DECISIONS.md`.
- Next action: Let the run continue toward step 6,000, then validate the final checkpoint, export, and native/exported smoke test before cleanup.

## 2026-08-06 — Conversational SFT v2 completed and staged in LM Studio

### Decision

Mark the 6,000-step conversational SFT v2 training phase complete and stage
its exported GGUF in LM Studio under the separate key
`codexa-900m-sft-v2-lmstudio`. Preserve the native checkpoint and all source
data while LM Studio behavioral compatibility remains unresolved.

### Evidence

- `logs/codexa-900m-sft-v2/train_metrics.jsonl` ends at optimizer step 6,000,
  103,459,920 total tokens, training loss 1.5768, and validation loss 2.0316.
- `checkpoints/codexa-900m-sft-v2/latest.pt` passes its SHA-256 sidecar check.
- `exports/codexa-900m-sft-v2-lmstudio-f16.gguf` was generated with 293
  tensors, verified structurally, and has SHA-256
  `5b5a2f7a17282946e6573c80027886ed4d0f41f705305b73fc678411f34d5698`.
- LM Studio imported the GGUF and loaded it to 100% in 1.95 seconds, but both
  chat and raw completion API smoke tests failed with the engine's
  `expected peg-native format` / `expected Content-only format` errors.

### Affected paths

- `checkpoints/codexa-900m-sft-v2/latest.pt`
- `checkpoints/codexa-900m-sft-v2/latest.pt.sha256`
- `logs/codexa-900m-sft-v2/train_metrics.jsonl`
- `exports/codexa-900m-sft-v2-hf-gpt2/`
- `exports/codexa-900m-sft-v2-lmstudio-f16.gguf`
- LM Studio model key `codexa-900m-sft-v2-lmstudio`

### Storage audit and next action

No checkpoint cleanup was performed because the exported model failed the
behavioral smoke gate. The largest candidates are the 61G native 100M
checkpoint lineage, 11G 900M base lineage, and 3.5G completed SFT v1 copy;
the native lineage is still protected by the repository retention policy, the
900M base is the SFT parent, and SFT v1 has no verified replacement export.
The 146G dataset tree and 417M logs are also retained. Fix or replace the
LM Studio-compatible exporter, then rerun native/exported equivalence and
quality gates before deleting any checkpoint artifacts.

## 2026-08-06 — Add native interactive SFT chat path

### Decision

Use native PyTorch inference as the immediate conversational test path and add
`scripts/chat_native.py` so the completed SFT checkpoint can be queried without
the incompatible LM Studio GGUF adapter.

### Evidence

- A direct native probe against `checkpoints/codexa-900m-sft-v2/latest.pt`
  generated a coherent response on CUDA.
- The new interactive command loads the checkpoint once, preserves prior turns,
  supports `/clear` and `/exit`, and stops generation at `<|end|>`.
- The native response identified itself as Open Assistant, so native execution
  works but conversational identity/data quality still needs evaluation.

### Affected paths

- `scripts/chat_native.py`
- `checkpoints/codexa-900m-sft-v2/latest.pt`
- `checkpoints/tokenizer-base-v1/tokenizer.json`

### Next action

Run the fixed native multi-turn, factual, arithmetic, and stopping probes before
any further training or exporter work.

## 2026-08-06 — Expose native SFT chat through local Codexa CLI

### Decision

Make the completed native checkpoint directly accessible through the existing
local-development Codexa CLI as `codexa-dev native`, while leaving the
published `codexa` command unchanged.

### Evidence

- The local launcher now resolves the Python environment, interactive chat
  script, SFT v2 checkpoint, tokenizer, and CUDA device explicitly.
- The stale `codexa-dev` and `cxd` shims were reinstalled to point at the
  current `13-Codexa CLI` checkout.
- An end-to-end `codexa-dev native` smoke conversation loaded the checkpoint on
  CUDA and returned assistant text without LM Studio or GGUF.

### Affected paths

- `/home/k9-vortex/Development/1-JavaScript(Type)/13-Codexa CLI/scripts/run-local-dev.mjs`
- `/home/k9-vortex/Development/1-JavaScript(Type)/13-Codexa CLI/scripts/run-local-dev.test.ts`
- `/home/k9-vortex/Development/1-JavaScript(Type)/13-Codexa CLI/scripts/README.md`
- `/home/k9-vortex/.local/share/npm/bin/codexa-dev`
- `/home/k9-vortex/.local/share/npm/bin/cxd`

### Next action

Use `codexa-dev native` for manual conversational evaluation and record native
quality separately from the rejected LM Studio adapter.

## 2026-08-06 — Repair interactive native CLI terminal ownership

- Decision: Keep `codexa-dev native` attached to the invoking terminal's stdin
  and open one verified visible Kitty native-chat session for immediate use.
- Evidence: The prior Zsh wrapper routed every `codexa-dev` invocation through
  an external-terminal handoff, making native chat appear to exit. The repaired
  function bypasses that handoff for `native`; Zsh syntax validation passes,
  and the visible native process is loaded on CUDA as PID 804619.
- Affected paths: `/home/k9-vortex/.zshrc`, backup
  `/home/k9-vortex/.zshrc.codexa-native-20260806-1125.bak`, and the running
  `codexa-dev native` Kitty session.
- Next action: Type directly at the visible `You:` prompt; use `/exit` to close.
## 2026-08-06 — Route Codexa CLI through a dedicated native provider

Decision: add `Codexa Native` as a first-class Codexa CLI provider backed by a
persistent PyTorch JSONL bridge. This provider bypasses LM Studio, llama.cpp,
and the GGUF compatibility export while preserving conversation history inside
one loaded `NativeChatEngine` process.

Evidence: `scripts/native_chat_bridge.py` loaded
`checkpoints/codexa-900m-sft-v2/latest.pt` on CUDA and completed two sequential
requests in one process. The bridge protocol and routing work, but the returned
answers were low quality and failed the requested exact-phrase instruction;
this is now isolated as checkpoint/SFT quality rather than LM Studio transport.
The Codexa CLI TypeScript typecheck and full Bun test suite passed. The model
repository suite reported 56 passes and three pre-existing stale fixture
failures involving parameter-count/config expectations.

Affected paths: `src/native_chat.py`, `scripts/chat_native.py`,
`scripts/native_chat_bridge.py`, and the Codexa CLI provider runtime/registry/UI
under `/home/k9-vortex/Development/1-JavaScript(Type)/13-Codexa CLI/src/`.

Next action: test through the visible `Codexa Native` route, then evaluate or
repair SFT data/checkpoint behavior independently of provider integration.

## 2026-08-11 — Reuse the prepared full base-training stream

- Decision: Use the existing mixed base-training stream for the next base phase;
  do not rebuild the corpus or delete raw, processed, tokenized, checkpoint, or
  export artifacts.
- Evidence: `data/tokenized/base-v1/mixed/token_data_manifest.json` records
  12,819,847,234 training tokens, 13,383,283 documents, the frozen
  FineWeb-Edu/Wikipedia mixture, and zero repeated documents. The train stream,
  index, and manifest match their recorded SHA-256 checksums. The full Python
  validator was not runnable because `.venv` lacks the `tokenizers` package.
- Affected paths: `data/tokenized/base-v1/mixed/`,
  `data/tokenized/base-v1/production/token_data_manifest.json`,
  `configs/1b.yaml`, and the existing training launch scripts. No generated
  data or model artifact was changed in this session.
- Next action: Restore repository dependencies, run the complete token-data
  validator, then choose the optimizer-step budget before launching. At 65,536
  tokens per optimizer step, the full stream requires approximately 195,616
  steps; the current 10,000-step config covers only about 5.1 percent.

## 2026-08-14 — Measure preparation speed and recheck production readiness

- Decision: Treat the existing prepared corpus as intact but not yet fully
  accepted for launch; repair the validator/test contract before starting a
  training run.
- Evidence: The completed preparation manifest records 13,700,814 input rows
  processed in 6,590.5 seconds, approximately 2,078 rows/second, and the four
  processed JSONL output SHA-256 values match the manifest. A bounded memmap
  probe read 409,600 tokens at approximately 14.9M tokens/second, so host token
  loading is not the observed bottleneck. The prior verified 900M production
  benchmark measured 7,700.7 tokens/second and 8.51 seconds per optimizer step.
  `inspect_token_data.py` currently rejects the mixed manifest with missing
  `eos_token_id`. The test suite reports 56 passed and 3 failures caused by
  stale 921,773,568-parameter/config fixtures versus the active
  934,356,480-parameter model and required rotary fields.
- Affected paths: `data/processed/base-v1/`,
  `data/tokenized/base-v1/mixed/token_data_manifest.json`,
  `scripts/inspect_token_data.py`, `src/token_data.py`, `tests/`,
  `configs/1b.yaml`, and `documentation/training/100M_PROGRESS_LOG.md`.
- Next action: align the validator and fixtures with the active manifest/model,
  rerun the full test suite and token-data validator, then run a fresh visible
  12-step CUDA BF16 production-shape benchmark before selecting the training
  budget. No training or cleanup was launched in this update.

## 2026-08-14 — Diagnose native inference speed

- Decision: Optimize native inference before spending additional training time;
  the measured bottleneck is missing attention KV caching, not insufficient
  base-training steps.
- Evidence: On the RTX 4080 using
  `checkpoints/codexa-900m-sft-v2/latest.pt`, native CUDA generation measured
  approximately 117 tokens/second with a 32-token prompt, 61 tokens/second
  with a 128-token prompt, and 21 tokens/second with a 512-token prompt. A
  128-token prompt with 64 generated tokens measured 59 tokens/second. The
  current `src/generate.py` calls the full model on the entire growing
  sequence for every generated token, and `src/model.py` exposes no KV-cache
  state in attention or transformer blocks. No local llama.cpp/LM Studio CLI
  was available for an immediate GGUF comparison.
- Affected paths: `src/generate.py`, `src/model.py`, `src/native_chat.py`,
  `scripts/generate.py`, `scripts/native_chat_bridge.py`, and the current 900M
  SFT checkpoint.
- Next action: implement an opt-in KV-cache path with equivalence tests for
  logits, EOS/`<|end|>` stopping, and multi-turn history; then rerun the same
  prompt-length benchmark before comparing quantized exports. No checkpoint
  or dataset was changed.

## 2026-08-14 — Start 900M base 10,000-step run

- Decision: Start a fresh 10,000-optimizer-step base-training run from random
  weights using the existing mixed FineWeb-Edu/Wikipedia token stream.
- Evidence: No active training process was found. The production model is
  934,356,480 parameters and the RTX 4080 supports CUDA BF16. The existing
  250-step checkpoint interval was unsafe with 116GB free because it could
  create approximately 40 full checkpoints. A dedicated run configuration
  uses a 1,000-step interval, retaining recoverable latest/previous state and
  ten milestone checkpoints while avoiding that storage overrun.
- Affected paths: `configs/900m-base-10k.yaml`,
  `data/tokenized/base-v1/mixed/train.bin`,
  `data/tokenized/base-v1/fineweb_edu/validation.bin`,
  `data/tokenized/base-v1/production/token_data_manifest.json`,
  `checkpoints/codexa-900m-base-10k-20260814/`, and
  `logs/codexa-900m-base-10k-20260814/`.
- Next action: Monitor the first metrics and checkpoint, confirm sustained
  CUDA BF16 throughput and finite losses, then retain the visible 100x22
  viewer through completion or resume it after interruption.

## 2026-08-14 — Stop mistaken base-training launch

- Decision: Stop the newly launched base-training run because the active user
  objective is inference speed, not additional pretraining.
- Evidence: The run was terminated cleanly at optimizer step 17 after seeing
  1,114,112 tokens. The final recorded training loss was 9.6977 and measured
  throughput was 7,859 tokens/second. No checkpoint was written because the
  configured safe milestone interval was 1,000 steps. The run log and metrics
  remain preserved; no dataset, existing checkpoint, or export was deleted.
- Affected paths: `logs/codexa-900m-base-10k-20260814/`,
  `/tmp/codexa-900m-base-10k-20260814.log`, and the stopped process/viewer.
- Next action: Do not resume this run. Continue with the already measured
  native inference diagnosis and implement/test KV caching in
  `src/model.py` and `src/generate.py`.

## 2026-08-14 — Add and benchmark native inference KV caching

- Decision: Keep the KV-cache path enabled by default for `LanguageModel`
  generation while preserving an explicit uncached reference path for tests and
  regression comparison.
- Evidence: The focused model/generation suite passes 12 tests, including
  cached versus uncached logit equivalence and identical greedy token output.
  On the RTX 4080 with the 900M SFT v2 checkpoint, cached generation measured
  137 versus 117 tokens/second for a 32-token prompt, 124 versus 61 for a
  128-token prompt, 96 versus 21 for a 512-token prompt, and 125 versus 59 for
  a 128-token prompt generating 64 tokens. The cache therefore improves long
  context generation by approximately 4.5x in this bounded test.
- Affected paths: `src/model.py`, `src/generate.py`, `tests/test_generation.py`,
  and the native inference path used by `src/native_chat.py`.
- Next action: run the full repository regression suite, then add explicit
  first-token/steady-state latency telemetry and benchmark multi-turn native
  chat before considering quantization or further model changes.

## 2026-08-14 — Torch compile environment gate

- Decision: Keep `torch.compile` opt-in and do not make it the default yet.
- Evidence: The compile wiring is present for one-shot generation and native
  chat, but the first real 900M CUDA attempt failed in PyTorch Inductor/Triton
  before producing a benchmark. The environment is missing `Python.h` for
  Python 3.14, so Triton cannot build its CUDA helper. The existing KV-cache
  path remains validated and unaffected.
- Affected paths: `src/generate.py`, `src/native_chat.py`,
  `scripts/generate.py`, and `scripts/chat_native.py`.
- Next action: provide a compatible Python development-header/toolchain
  environment, rerun the compile smoke test, then benchmark compiled versus
  cached generation. Do not enable compile by default until that benchmark and
  output/stopping checks pass.

## 2026-08-14 — Reject torch.compile as default speed path

- Decision: Keep `torch.compile` available only as an experimental opt-in; do
  not enable it for Codexa native inference.
- Evidence: After installing `python3.14-devel`, a temporary no-space toolchain
  alias bypassed the linker path issue caused by the repository name. The real
  900M CUDA benchmark completed with a 45.39-second compile warm-up and about
  126.6 tokens/second steady state versus about 125.5 tokens/second for the
  normal KV-cache path. Outputs matched, but the steady-state gain was only
  approximately 1% and does not justify the compile warm-up/runtime fragility.
- Affected paths: `src/generate.py`, `src/native_chat.py`,
  `scripts/generate.py`, and `scripts/chat_native.py`.
- Next action: leave compile opt-in and benchmark weight-only quantization or a
  compatible optimized inference runtime as the next speed candidate. The
  validated KV-cache path remains the default.

## 2026-08-16 — Remove obsolete base-training data

- Decision: Remove the old raw and derived base-training datasets to reclaim
  storage while preserving the data required for the next 900M conversational
  improvement.
- Evidence: `data/` occupied approximately 146 GB. No active training process
  referenced the dataset paths. The current 900M SFT launcher still references
  `data/tokenized/base-v1/mixed/train.bin`, so that 27 GB replay dataset was
  retained. Chat/SFT data was also retained.
- Affected paths removed: `data/processed/base-v1/`,
  `data/raw/fineweb-edu-10bt/`, `data/raw/wikipedia/`,
  `data/tokenized/base-v1/fineweb_edu/`,
  `data/tokenized/base-v1/wikipedia/`, and
  `data/tokenized/fineweb-edu-1b-v1/`. These exact directories were moved to
  the desktop Trash using `/usr/bin/gio trash`; the removal is recoverable
  until the Trash is emptied.
- Evidence after cleanup: `data/processed/` is approximately 4.7 GB,
  `data/raw/` approximately 820 MB, and `data/tokenized/` approximately 27 GB.
- Next action: rebuild only the dataset needed for the next approved training
  phase; do not empty the Trash until the retained SFT/replay path has been
  validated.

## 2026-08-16 — Remove obsolete 100M native checkpoints

- Decision: Remove the completed `codexa-100m-native-v1` checkpoint lineage
  because the active improvement path is the 900M model and the 100M native
  export is already present.
- Evidence: The checkpoint directory occupied approximately 61 GB, no matching
  100M training process was active, and
  `exports/codexa-100m-native-v1-lmstudio-f16.gguf` plus the HF export existed.
- Affected paths: `checkpoints/codexa-100m-native-v1/` was moved to the desktop
  Trash using `/usr/bin/gio trash`; the 100M exports, tokenizer, 900M
  checkpoints, and 100M SFT pilot checkpoint were preserved.
- Next action: use the retained 900M SFT-v2 checkpoint for model improvements;
  empty the Trash only after confirming the 100M export is no longer needed.

## 2026-08-16 — Permanently remove 100M native checkpoints from Trash

- Decision: Permanently delete the previously trashed
  `codexa-100m-native-v1` checkpoint directory after the user confirmed it was
  no longer needed.
- Evidence: The exact Trash item and matching `.trashinfo` metadata were found;
  the 100M HF and GGUF exports remain under `exports/`.
- Affected paths: `/home/k9-vortex/.local/share/Trash/files/codexa-100m-native-v1`
  and its matching Trash metadata were permanently removed. Approximately
  61 GB of checkpoint artifacts were reclaimed; unrelated Trash contents were
  left untouched.
- Next action: continue model improvements from the retained 900M lineage.

## 2026-08-21 — Launch balanced 900M SFT v1

- Decision: Start `codexa-900m-sft-balanced-v1` from the checksum-verified
  900M base checkpoint using a corpus-wide deterministic sample rather than
  the first-record subset that caused collapse.
- Evidence: New samples contain 30,000 UltraChat and 30,000 OASST1 records,
  selected by stable hash with seed `20260821`. The run uses 50% base replay,
  `learning_rate_scale=0.25`, 1,000 warmup steps, 6,000 optimizer steps,
  AdamW8bit, and the required Kitty viewer. Existing SFT-v1, SFT-v2, and sanity
  checkpoints are preserved.
- Affected paths: `scripts/sample_conversation_jsonl.py`,
  `scripts/train_conversational_sft.py`, `scripts/run_900m_sft_balanced.sh`,
  `data/processed/chat-sft-balanced-v1/`, and the new run paths under
  `logs/codexa-900m-sft-balanced-v1/` and
  `checkpoints/codexa-900m-sft-balanced-v1/`.
- Next action: monitor the attached viewer; after completion, verify checksum,
  reload the checkpoint, and run the fixed native behavioral probes before any
  export or promotion.

## 2026-08-22 — Balanced 900M SFT v1 behavioral gate failed

- Decision: Do not promote or export `codexa-900m-sft-balanced-v1` as a usable
  conversational model. Preserve its checkpoint and logs for comparison.
- Evidence: The run completed 6,000 CUDA optimizer steps and approximately
  210.18M tokens; the final validation loss was `2.028321` and the checkpoint
  sidecar passed. Reloaded native probes showed grammatical output and some
  `<|end|>` stops, but arithmetic was wrong (`17+16=42`), explanations drifted
  into invented Codexa plant facts, correction produced unrelated content, and
  the tea request failed the exact three-item requirement and often hit the
  length limit. Multi-turn responses also repeated the arithmetic template.
- Affected paths: `checkpoints/codexa-900m-sft-balanced-v1/latest.pt`,
  `logs/codexa-900m-sft-balanced-v1/`, and the balanced SFT launcher/config.
- Next action: stop treating validation loss as conversational proof. Audit
  training-example quality and prompt/answer alignment at the sampled-record
  level, compare logits and labels on fixed probes, and design a supervised
  chat dataset with explicit short-answer, correction, and instruction-following
  coverage before another long run.

## 2026-08-22 — Pre-training diagnostic complete; no new run authorized

- Decision: Do not start another training run yet. Keep all existing model
  checkpoints, exports, datasets, and logs intact while the next SFT recipe is
  reviewed.
- Evidence: The tiny four-example CUDA overfit reached exact target text and
  stopped on `<|end|>`, and the shifted-label audit reports zero END alignment
  failures. The balanced sampled corpus contains 26,082 accepted UltraChat
  records and 29,186 accepted OASST1 records at context length 2,048; 3,918
  and 814 records respectively are rejected only because complete conversations
  exceed context. Accepted UltraChat has 77.1% supervised tokens and accepted
  OASST1 has 84.7%. Native comparison shows base incoherence, while balanced
  SFT is grammatical but gives wrong arithmetic, prompt drift, and incomplete
  list answers even when each probe is reset.
- Affected paths: `scripts/audit_chat_training.py`, `src/native_chat.py`,
  `scripts/chat_native.py`, `scripts/native_chat_bridge.py`,
  `scripts/train_conversational_sft.py`, `tests/test_sft_serialization.py`,
  and the diagnostic output under `logs/diagnostics/`.
- Next action: review and approve a replacement data/recipe gate with explicit
  short-answer, arithmetic, correction, list, and multi-turn examples; only
  after that approval may a new training launch be started.

## 2026-09-10 — Plan bounded 900M conversational repair pilot

- Decision: The next run will be a bounded repair pilot from the retained
  `codexa-900m-base-v1` checkpoint, using a new filtered short-response corpus.
  Do not repeat the 6,000-step, 50%-base-replay balanced recipe before a
  behavioral gate passes.
- Recipe proposal: build `chat-sft-repair-v1` with explicit user-first
  conversations, a 512-token maximum serialized context for the pilot, exact
  deduplication, prompt-echo rejection, complete assistant turns only, and
  guaranteed coverage for arithmetic, factual short answers, explanations,
  corrections, lists, and multi-turn memory. Use a deterministic 80/20 train /
  validation split, AdamW8bit, batch size 1, gradient accumulation 32, peak
  learning rate `1e-5`, 500 warmup steps, 2,000 optimizer steps, and no base
  replay in the first repair pilot. Retain the base replay path for a later
  stability run only if this pilot passes.
- Preflight gate: run the serializer audit, the four-example CUDA overfit, and
  a 100-record dry-run accounting report before launching. Reject the launch
  if any shifted-label or END alignment check fails.
- Acceptance gate: checksum and reload the checkpoint, then run isolated native
  probes with a reset before every prompt. Require correct arithmetic, factual
  recall, correction, three-item list structure, bounded explanation, valid
  stop-token termination, and no prompt echo or cross-prompt contamination.
  Validation loss is secondary evidence and cannot promote a checkpoint by
  itself.
- Affected paths: planned `data/processed/chat-sft-repair-v1/`,
  `logs/codexa-900m-sft-repair-v1/`,
  `checkpoints/codexa-900m-sft-repair-v1/`, and a new launcher based on the
  required Kitty 100x22 viewer. Existing checkpoints, exports, data, and logs
  remain untouched.
- Next action: implement and inspect the repair dataset and dry-run report;
  wait for explicit approval before starting the 2,000-step pilot.

## 2026-09-10 — Repair corpus and preflight gates passed

- Decision: The repair pilot is technically ready but remains unlaunched until
  the user explicitly requests the training start.
- Evidence: `chat-sft-repair-v1` contains 12,096 total records: 12,000
  deterministic natural records and 96 behavioral anchors, split into 9,627
  train and 2,469 validation records. Both splits have 100% serializer
  acceptance, zero prompt echoes, zero END alignment failures, and a maximum
  serialized length of 512 tokens. The 300-step CUDA overfit finished at loss
  `0.0001215646` and reproduced all four exact targets with `stop_token`.
- Affected paths: `scripts/prepare_repair_sft.py`,
  `scripts/run_900m_sft_repair.sh`, `data/processed/chat-sft-repair-v1/`,
  `logs/diagnostics/chat-repair-audit-20260910.json`, and
  `logs/chat-overfit-repair-preflight-v1/`.
- Next action: on explicit start approval, launch the prepared 2,000-step
  repair run with the required Kitty 100x22 viewer; otherwise leave all model
  artifacts unchanged.

## 2026-09-10 — Launch approved repair SFT run

- Decision: Start `codexa-900m-sft-repair-v1` from the verified retained 900M
  base checkpoint after explicit user approval.
- Evidence: The base checkpoint sidecar passed, the repair train and validation
  files are present, the base replay token file is present, and no training
  process was active. The preflight serializer, END alignment, and CUDA
  overfit gates had already passed.
- Affected paths: `scripts/run_900m_sft_repair.sh`,
  `checkpoints/codexa-900m-sft-repair-v1/`,
  `logs/codexa-900m-sft-repair-v1/`, and the visible Kitty 100x22 viewer.
- Next action: monitor the run to completion; verify checkpoint checksum,
  reload it, and execute the isolated behavioral acceptance probes before any
  export or promotion.

## 2026-09-10 — Repair SFT completed; behavioral promotion gate failed

- Decision: Do not export or promote `codexa-900m-sft-repair-v1` as the usable
  conversational checkpoint. Preserve its checkpoint and logs for comparison.
- Evidence: The run completed all 2,000 optimizer steps, reached validation
  loss `2.4453267`, and passed the checkpoint checksum. Native CUDA probes with
  resets showed correct `17 + 25 = 42`, true two-turn color memory, and a
  correction response. However, explanation prompts produced repeated
  `photosynthetic` text and hit the length limit; the exact-three-item tea list
  returned only two items. The checkpoint therefore fails the explanation and
  exact-list quality gates despite targeted improvements.
- Affected paths: `checkpoints/codexa-900m-sft-repair-v1/latest.pt`,
  `logs/codexa-900m-sft-repair-v1/`, and the repair launcher. No checkpoint,
  export, tokenizer, dataset, or log was deleted.
- Next action: diagnose the repetition/list failure and revise the repair data
  or decoding/training recipe before any export or follow-up run.

## 2026-09-10 — Deeper repair checkpoint postmortem

- Decision: Treat the repair checkpoint as a narrow template-repair result,
  not a general conversational improvement.
- Evidence: Exact familiar prompts pass, but generalization probes fail: `18 +
  24` became `19 + 24 = 42`, an unseen correction claimed `4 is 8`, and both
  tea and fruit requests returned the same Apple/Banana/Orange answer. Simple
  anchor-matching explanations pass, while a photosynthesis request with a
  different wording loops on `photosynthetic` until the length limit. The
  training loss continued down to about `2.0` while validation loss flattened
  near `2.43-2.45`, indicating memorization/fit without robust behavioral
  generalization.
- Root cause assessment: The repair corpus contains 9,556 natural records but
  only 71 anchor records in train, with each anchor category generated from
  four repeated templates. Anchor answers also repeat across the split. This
  teaches fixed answer forms and does not provide enough varied arithmetic,
  correction, list, or explanation transformations. The low-learning-rate
  pilot improved exact templates but did not repair the underlying base-model
  generalization.
- Affected paths: `data/processed/chat-sft-repair-v1/`,
  `checkpoints/codexa-900m-sft-repair-v1/latest.pt`, and the native probe
  path. No artifacts were removed or exported.
- Next action: replace repeated anchors with a larger deduplicated, generated
  behavioral suite using many distinct operands, list subjects, corrections,
  and explanation prompts; hold out templates by task family so validation
  measures generalization before another training decision.

## 2026-09-11 — Launch five-hour 900M base continuation

- Decision: Start `codexa-900m-base-continuation-5h-v1` as a fresh optimizer
  continuation initialized from the verified `codexa-900m-base-v1` weights.
- Evidence: The source model completed 10,000 steps / 655.36M tokens but remains
  undertrained. The new run reserves the final 39,298,352 tokens from the
  retained 12.82B-token stream for validation and excludes that range from new
  training. The source checkpoint loads successfully, the baseline loss on 16
  held-out batches is `3.2042928`, and focused range/checkpoint tests pass
  (`9 passed`). The validation tail may have been sampled during the historic
  base run, but it is disjoint from this continuation and is suitable for a
  within-run comparison.
- Affected paths: `src/token_data.py`, `scripts/train.py`,
  `scripts/evaluate_checkpoint.py`, `tests/test_token_data.py`,
  `configs/900m-base-continuation-5h.yaml`,
  `data/tokenized/base-v1/continuation-5h/token_data_manifest.json`,
  `scripts/run_900m_base_continuation_5h.sh`, and the new run paths under
  `logs/` and `checkpoints/`.
- Next action: keep the Kitty 100x22 viewer attached through 2,000 optimizer
  steps, then verify checksum and compare final held-out loss and fixed outputs
  against the recorded baseline before any SFT or export decision.

## 2026-09-11 — Pause five-hour base continuation

- Decision: Pause `codexa-900m-base-continuation-5h-v1` immediately at the
  user's request using `SIGSTOP`; do not terminate or restart it.
- Evidence: PID `236816` is in stopped state `T`. The last completed optimizer
  step is 7 with 458,752 tokens processed and training loss `3.0028406`.
- Affected paths: the live training process, its existing logs, and the visible
  Kitty viewer. No checkpoint, log, dataset, or model was removed.
- Next action: wait for an explicit resume instruction before sending
  `SIGCONT` or performing further run actions.

## 2026-09-11 — End paused base continuation

- Decision: End `codexa-900m-base-continuation-5h-v1` at the user's request and
  close its viewer. Do not delete or alter the original 900M base checkpoint.
- Evidence: The detached process did not honor the first graceful interrupt
  after being continued from `SIGSTOP`; it was terminated explicitly after
  reaching optimizer step 13 and 851,968 tokens. The GPU process and Kitty
  viewer are gone. The run ended before its first scheduled checkpoint at step
  500, so it produced no recoverable continuation checkpoint.
- Affected paths: `logs/codexa-900m-base-continuation-5h-v1/` and
  `/tmp/codexa-900m-base-continuation-5h-v1.log`. Original checkpoints,
  datasets, exports, and tokenizer files remain intact.
- Next action: treat this run as interrupted and start any future continuation
  again from `checkpoints/codexa-900m-base-v1/latest.pt` after explicit approval.

## 2026-10-08 — Stage 1 specialist implementation authorized

- Decision: Implement a separate frozen EmbeddingGemma 2 classifier with an isolated dependency environment. Preserve the generative pipeline and record its three baseline failures separately. Use dominant-intent labels, hold uncertain cases for review, and return uncalibrated five-class scores only from trained heads.
- Evidence: The baseline suite reports 58 passed / 3 failed. Existing Transformers 4.57.6 lacks the encoder; Sentence Transformers is absent. Transformers 5.19.0 contains the model and dependency resolution with Sentence Transformers 6.1.0 succeeds. Inspected local data lacks the required intent labels; the user confirmed infrastructure-first delivery without a labeled dataset.
- Affected paths: `src/specialist/`, `scripts/specialist.py`, `configs/specialist.yaml`, specialist requirements/tests/documentation, `.venv-specialist/`, and the added environment ignore rule. Existing checkpoints, exports, datasets, logs, and unrelated working-tree changes are protected.
- Next action: Implement offline coverage and perform real text-only encoder initialization and embedding smoke verification. Do not launch generative training or fabricate classifier accuracy.

## 2026-10-08 — Specialist offline pipeline and baseline regression check

- Decision: Keep the initial specialist as infrastructure without a task-trained head. Enforce visible viewer attachment before public training launches, protected specialist output namespaces, immutable prepared bundles, and checksummed head checkpoints. Cache reuse now avoids loading the encoder when the execution/input identity matches.
- Evidence: The initial original-environment specialist pass has 33 passed and 5 dependency-related skips; the complete suite has 91 passed, 5 skipped, and the same 3 pre-existing failures. Tests exercise schema validation, frozen encoder contracts, gradient updates, losses, deterministic head/text inference, checkpoint corruption, and viewer configuration. The five scikit-learn-dependent tests await the isolated environment installation. Review corrected a possible prior-head CUDA allocation reference in checkpoint payloads.
- Affected paths: `src/specialist/`, `scripts/specialist.py`, `tests/test_specialist.py`, the specialist configuration and dependency lock, and `documentation/reference/SPECIALIST.md`. No existing checkpoint, dataset, export, or generative source file was changed.
- Next action: Complete the isolated dependency install, run every specialist test, and verify the real pinned text-only model. Report encoder measurements separately from task accuracy.

## 2026-10-08 — Specialist dependency setup and mechanical acceptance

- Decision: Add Pillow 12.3.0 and TorchVision 0.28.0 for the upstream processor loader, while keeping vision/audio neural towers disabled. Seed the new isolated environment with copies of exact-version existing PyTorch/CUDA distributions, then install the remaining lock; do not share package paths or modify the original environment.
- Evidence: Transformers' EmbeddingGemma2Processor requires vision utility backends even on text inputs; TorchVision 0.28.0 requires the selected PyTorch 2.13.0. The original native distributions match the lock versions. A slow redundant binary download was interrupted without deleting its cache. All 39 offline tests pass with compatible downloaded test dependencies. An earlier cache-only verification attempt selected a free-threaded wheel for a non-free-threaded Python; this setup-only mismatch was corrected and is not a pipeline acceptance failure. A real 100x22 Kitty viewer attached successfully and only that test window was closed.
- Affected paths: `.venv-specialist/`, specialist requirements/lock/documentation, `tests/test_specialist.py`, and the new viewer-smoke log under `logs/specialist/`. Original environment, model lineages, training checkpoints, datasets, and exports remain unchanged.
- Next action: Verify locked imports and all tests inside the completed isolated environment, then run the real pinned encoder smoke and record measured results separately from task metrics.

## 2026-10-08 — Stage 1 specialist accepted as verified infrastructure

- Decision: Accept Stage 1 infrastructure and real encoder verification. Do not claim a trained intent classifier, task accuracy, macro-F1, or baseline-versus-MLP task superiority until human-reviewed data is supplied. Retain all existing artifacts and baseline failures independently.
- Evidence: All 39 specialist tests pass in the isolated environment; all 65 locked packages pass compatibility checks with no lock mismatches. Representative copied PyTorch and cuBLAS binary hashes match the original and have separate inodes. Original package versions are unchanged. The original-environment full suite reports 92 passed, 5 dependency-related specialist skips, and the same 3 baseline failures. Actual pinned encoder tests pass on CUDA BF16 and CPU FP32: 271,002,624 text-only parameters, zero trainable encoder weights, normalized deterministic [2, 768] outputs. Final warmed batch-size-one encoder latency is 15.208 ms on the RTX 4080 and 46.008 ms on CPU; CUDA peaks are 580,295,680 allocated bytes and 599,785,472 reserved bytes. The actual Kitty viewer attachment check passed. No labeled task training or generative model training was launched.
- Affected paths: `src/specialist/` (9 modules), `scripts/specialist.py`, `configs/specialist.yaml`, specialist requirements/lock, `tests/test_specialist.py`, `documentation/reference/SPECIALIST.md`, the isolated environment ignore rule, and these append-only records. GPU evidence: `logs/specialist/encoder-smoke-1791451727274305893/report.json`. CPU evidence: `logs/specialist/encoder-smoke-1791451782146202907/report.json`. Review removed the deprecated embedding-dimension API call and corrected the active run metadata state; the specialist suite still passes after those changes.
- Next action: Obtain representative human-reviewed dominant-intent labels with independent group coverage, then run documented prepare/train/evaluate commands using fresh specialist artifact namespaces. Prioritize independent ambiguity/OOD probes and confidence calibration in Stage 2. No checkpoint, dataset, export, tokenizer, or existing log was deleted; nothing was committed or pushed.


## 2026-10-08 — Stage 2 implementation begins

Decision: implement opt-in semantic memory, preserve Stage 1 classification and all existing artifacts; conditional SFT limited to 200 steps and 60 minutes including preflight/evaluation. Evidence: 39 specialist and 26 focused generative tests pass; full baseline 92 passed / 5 skipped / 3 existing failures; verified base and repair checkpoint checksums and base tokenizer fingerprint. Affected paths: src/memory, native chat, SFT infrastructure, tests and documentation. Next action: implement isolated retrieval worker, scoped storage, transactional context construction, then measure retrieval before training. No cleanup, commit or push.


## 2026-10-08 — Stage 2 retrieval and SFT data acceptance

Decision: use opt-in, user/conversation-scoped SQLite exact cosine memory with CPU FP32 encoder worker; threshold 0.68 selected only on development fixtures. Use 480-byte exact-text chunks to bound byte-fallback token counts without crossing environment tokenizers; preserve full raw turns separately. Evidence: held-out synthetic retrieval Recall@3 0.90, MRR 1.00, false-positive rate 0/5; 30 held-out queries. Original repair chat output comparison retrieves names but fails correction queries and remains repetitive/inaccurate; this is not general intelligence improvement. Affected paths: src/memory, scripts/evaluate_memory.py, logs/memory/retrieval-stage2-cpu-v1, logs/memory/chat-original-v1. Next action: remeasure optimized single-load native inference and both GPU models.

Decision: prepare general-chat-sft-v2 using only canonical existing UltraChat/OpenAssistant derivatives, not repeated repair anchors. Evidence: 182,892 training / 10,135 validation / 9,874 test conversations; source/root and normalized-message duplicate groups do not cross new splits. 26,497 overlength/role rejects, 42 normalized duplicates, 56 severe repetitions, 5 control-marker records rejected. Historic SFT exposure remains recorded; semantic near-duplicate/factual audits remain limitations. Affected paths: src/data/general_chat.py, src/conversational_training.py, data/processed/general-chat-sft-v2. Next action: conditional 200-step BF16/8-bit AdamW pilot from checksum/fingerprint-verified base; exact initialization restored after preflight; strict 14 GiB reserved VRAM gate, visible 100x22 Kitty viewer, 60-minute inclusive budget. No old artifact overwritten/deleted.


## 2026-10-08 — Stage 2 pilot preflight and first validation

Decision: proceed with bounded full-parameter SFT; the automatically launched 100x22 Kitty viewer attached before backward. Evidence: preflight assistant loss 2.262700, finite gradient norm 2.834639, verified parameter update, peak reserved 10,118,758,400 bytes. Restored original base weights and restarted optimizer before training. Baseline validation loss 2.652032; step-50 validation 2.460254. Training is in progress and this loss change does not establish conversational improvement. Runtime peak reserved 13,103,005,696 bytes remains under the 14 GiB gate. Affected paths: logs/codexa-900m-chat-stage2-pilot-v1 and separately named checkpoints/codexa-900m-chat-stage2-pilot-v1. Next action: complete up to 200 steps within the deadline, verify checkpoint, evaluate real outputs, and export only to a fresh experimental directory.

Hardware evidence: optimized native chat plus CUDA BF16 encoder reached 7,647 MiB total GPU usage, including desktop/driver allocations; CPU encoder mode reached 6,526 MiB. Native CPU-encoder median full reply latency: 0.427s memory off, 0.496s on; CUDA-encoder 0.429s off, 0.443s on in the 24 synthetic scenarios. These medians mix response lengths and are not a pure encoder speed comparison. Affected paths: logs/memory/chat-original-cpu-v2 and logs/memory/chat-combined-cuda-v1. Next action: retain CPU default to isolate generation/training and keep CUDA optional.


## 2026-10-08 — Stage 2 final acceptance

Decision: deliver opt-in semantic-memory native chat; retain the original repair checkpoint as the default and do not promote the experimental pilot. Evidence: 200 bounded SFT steps / 4,029,761 assistant tokens; validation 2.652032 to 2.379369, test 2.270733; actual conversation quality did not improve, expected whole values 0/8 pilot versus 2/8 original-with-memory with incorrect self attribution. END rates 10/24 pilot versus 14/24 original-with-memory. Frozen retrieval Recall@3 0.90 / MRR 1.00 on 30 synthetic held-out queries. Source/export smoke token IDs identical; original base/repair hashes unchanged. Full tests 114 pass / 5 dependency skips / 0 fail; isolated tests 58 pass including all original 39. Dataset root/group violations zero; 21 exact common diagnostic-prompt occurrences disclosed. Affected paths: documentation/training/STAGE2_RESULTS.md, documentation/reference/CONVERSATIONAL_MEMORY.md, ENCODER_CONDITIONING.md, logs/memory, the separately named pilot checkpoint and experimental exports/codexa-900m-chat-stage2-pilot-v1. Next action: broader human-held-out conversation evaluation and provenance-preserving memory-format supervision, not automatic longer training. Inclusive acceptance 58.25 minutes from launch; no cleanup, commit or push.

Implementation hardening: stable source labels prevent random IDs from changing prompts; raw turns and chronological references are preserved; clearing/deleting active memory also resets live history. Scoped embedding cache returns copies and clears on deletion/shutdown. Foreign database files are rejected unchanged. Future bounded launches check competing CUDA processes and use two-update steady-state preflight. The completed pilot ran one-update preflight and all 200 steps verified steady-state VRAM below 14 GiB.


## 2026-10-08 — Independent repository extraction

Decision: implement the approved sibling workspace architecture, preserving the original project and assets. Eight local working trees now hold seven packaged components plus integration; no commits, remote repositories, pushes or PRs were made. Evidence: source_manifest/history.bundle, compatibility.json, package-build metadata and offline validation records. Affected paths: all sibling repositories under 37-LLM-From-Scratch-Workspace; the original 31 directory is unchanged. Neutral native checkpoint loading is Architecture-owned, SFT protocol Tokenizer-owned, context composition Inference-owned, and encoder subprocess configuration replaces hardcoded environment/script paths. Original model equations/state keys and tokenizer fingerprint are preserved. No model promotion or production training was performed. Independent asset backup and real-model/GPU/encoder validation remain release gates. Next action: review VALIDATION.md and authorize publication separately.


## 2026-10-08 — Authorized GitHub README PR

Published existing committed history (66eec75) as main to golba98/LLM-From-Scratch-PyTorch-Codexa-v1 under explicit user authorization. Created README-only commit 300a8eb (first commit) on docs/codexa-v1-readme and PR https://github.com/golba98/LLM-From-Scratch-PyTorch-Codexa-v1/pull/1. Existing local README edits plus the requested heading are included; all other working-tree changes remain unpublished. README references unpublished integration files and sibling packages, disclosed in the PR. GitHub reported a bypassed main rule for an existing historical merge commit. No training launched.


## 2026-10-08 — Authorized training repository publication

Under explicit user authorization, published README-only first commit 8643336 to main of golba98/LLM-Training-PyTorch-Codexa-v1 and saved all remaining 29 project files in commit 33effac on feat/save-training-project. Opened PR https://github.com/golba98/LLM-Training-PyTorch-Codexa-v1/pull/1. Offline existing-environment validation: 10 passed, two existing return-value warnings. Weights, datasets, encoder caches, generated logs and environments remain excluded. No production training, downloads, architecture changes or checkpoint/token format changes. Sibling packages remain local version 0.1.0 dependencies.


## 2026-10-08 — Authorized data repository publication

Under explicit user authorization, saved all 42 remaining LLM-Data project files in commit 479f248 on feat/save-data-project and published PR https://github.com/golba98/LLM-Data-PyTorch-Codexa-v1/pull/2, including the existing README heading commit. Anchored the dataset ignore rule to /data/ so nine Python source modules under src/llm_data/data are tracked. Offline existing-environment validation: 14 passed; staged whitespace check passed. Validation uses sibling sources and an existing integration test helper; standalone installation remains unverified, disclosed in the PR. Weights, datasets, encoder caches, generated logs and build output remain excluded. No production training, downloads, checkpoint key, token ID or format changes.


## 2026-10-08 — Canonical workspace consolidation

Lifted integration history to the renamed workspace root and registered seven existing repositories as pinned submodules. Preserved source/Git recovery records and relocated historical assets to a single protected temporary store with before/after SHA-256 verification. Canonical environments and asset resolution no longer depend on project 31. NumPy remains independently implemented and packaged. Actual-checkpoint parity and bounded CPU/CUDA validations are recorded in documentation/migration/. Originals remain pending review and independent backup; no model lineage was promoted.


## 2026-10-09 — Restore eight sibling repository boundaries

Moved integration and its Git history into LLM-From-Scratch; made existing component Git metadata independent without changing HEADs or indexes. Shared recovery/build/validation evidence moved once to workspace-infrastructure. Full pre-change plan, ownership inventory and journal are retained there. Source imports use pinned sibling paths; environments retain separate profiles. Original 31 and 32 are untouched; independent backup remains unavailable. No commits, pushes, PRs, training runs or repository deletion authorized. Validation results are recorded in the migration audit report.


## 2026-10-09 — Publish sibling-layout review changes

User explicitly authorized saving and publishing LLM-Data and LLM-From-Scratch changes to PRs. Existing Data PR #3 and integration PR #2 are updated without merging. Original Data integration test is preserved byte for byte in its tracked documentation archive; central active coverage remains. No original project, component repository, checkpoint or dataset is deleted. Other component documentation changes remain locally saved and unpublished. Private assets, environments and local recovery evidence remain outside Git. See documentation/migration/PUBLICATION_2026-10-09.md for validation and preservation details.


## 2026-10-09 — Save every remaining workspace source/documentation change

User authorized PRs for all remaining unsaved files. Six remaining component README/AGENTS changes are saved on their existing review branches. Integration compatibility pins advance to their saved commits. Workspace-level README, instructions and shared-infrastructure README now have single canonical tracked owners in documentation/workspace with local links. Every public source/documentation change is reviewed and published; private assets/configuration/environments/recovery records remain preserved and excluded from public Git. No merge, repository deletion, original-project mutation or production training is authorized.
