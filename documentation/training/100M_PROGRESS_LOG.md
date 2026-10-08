# Codexa 100M — Three-Month Progress Log

## 2026-08-21 — Native chat behavioral probe

The current native 900M conversational checkpoint was loaded through
`scripts/native_chat_bridge.py` and exercised with multi-turn and reset-isolated
prompts. The runtime had no CUDA device available, so this was a CPU behavioral
probe rather than a performance benchmark. The 900M model generated generic or
semantically incorrect answers, repeated a previous weather-app response across
later turns, stopped by the token limit instead of `<|end|>`, and failed basic
arithmetic and format-following prompts. The checkpoint is therefore retained
for diagnosis but is not accepted as conversationally ready. A retained 100M
pilot produced the same failure pattern in separate reset-isolated probes.

Next milestone: run a bounded chat-format overfit diagnostic covering role
serialization, assistant-only masks, EOS/stop supervision, and deterministic
behavioral probes before selecting the next SFT recipe.

## 2026-08-21 — Chat protocol overfit gate passed

The bounded diagnostic used the real tokenizer and chat-v1 serializer on a tiny
CUDA model for 300 steps. Loss decreased from `9.625757` to `0.0001216`. The
model reproduced fixed arithmetic, identity, explanation, and correction
answers exactly, and every response stopped on `<|end|>`. This proves the
role-token format, shifted assistant-only labels, and native stop handling are
mechanically capable of learning.

The 900M SFT failure should therefore be investigated in the training corpus,
checkpoint lineage, replay mixture, optimization schedule, and scale-specific
training behavior. No 900M checkpoint was deleted or promoted during this
diagnostic.

## 2026-08-21 — 900M SFT sanity recipe rejected

A 205-step CUDA sanity run from the verified 900M base completed successfully
at the numerical level, but its reloaded checkpoint was behaviorally worse than
the existing SFT-v2 checkpoint. It repeated an agricultural-field template,
failed arithmetic, explanation, correction, and requested list formatting, and
often exhausted the generation limit. This first-500-record-per-source recipe
is rejected as a narrow-subset overfit or catastrophic-forgetting experiment;
the checkpoint remains preserved for comparison.

## 2026-08-21 — Balanced 900M SFT v1 launched

The replacement run `codexa-900m-sft-balanced-v1` is using deterministic
corpus-wide samples of 30,000 UltraChat and 30,000 OASST1 records, 50% base
replay, a quarter-rate SFT learning-rate scale, and 1,000 warmup steps over a
6,000-step target. The run has its own checkpoint lineage and attached 100×22
Kitty viewer; previous checkpoints remain preserved until behavioral acceptance.

## 2026-08-22 — Balanced 900M SFT v1 failed behavioral acceptance

The balanced 6,000-step run completed numerically with validation loss
`2.028321`, but the reloaded model still failed basic arithmetic, explanation,
correction, and exact list-format probes. It is preserved but not accepted as
chat-ready. Further long SFT runs are gated on auditing sample alignment and
adding explicit short-answer and instruction-following coverage.

This document records the model's measurable progress across the next 100M
training phase and the later conversational SFT phase.

## Objective

Produce a versatile 100M-class model that can:

- continue ordinary text coherently;
- answer simple questions after conversational SFT;
- maintain a short multi-turn conversation;
- load and generate correctly in LM Studio;
- improve measurably over a fixed three-month evaluation schedule.

## Baseline — 2026-08-03

The first base checkpoint completed 10,000 optimizer steps and processed
655,360,000 tokens. Its native validation loss was 3.61696 (perplexity 37.22).

The current LM Studio GGUF is only a compatibility adapter. Its output is
recorded as a conversion failure, not as the model's true quality baseline:

> The model produced repetitive and malformed text in LM Studio. The adapter
> changes the trained architecture's positional and feed-forward behavior.

Baseline artifacts:

- Native checkpoint: `checkpoints/codexa-100m-base-v1/latest.pt`
- Native evaluation: `logs/codexa-100m-base-v1/evaluation.json`
- LM Studio adapter: `exports/codexa-100m-base-v1-lmstudio-llama-f16.gguf`

## Native checkpoint — 2026-08-03

- Run: `codexa-100m-native-v1`
- Architecture: native rotary/RMSNorm/SwiGLU
- Optimizer steps / tokens seen: 10,000 / 655,360,000
- Parameters: 125,848,320
- Training loss: 3.16557
- Validation loss / perplexity: 3.43051 / 30.89
- Speed: 52,850.6 tokens/second
- LM Studio load: pass
- LM Studio generation: pass at runtime level; quality gate pending
- Native generation: coherent fragments, but repetition remains high
- Full fixed-prompt outputs: `logs/codexa-100m-native-v1/evaluation.json`
- GGUF artifact: `exports/codexa-100m-native-v1-lmstudio-f16.gguf`
- LM Studio test transcript: `logs/codexa-100m-native-v1/lmstudio_test_2026-08-03.md`
- Multi-turn chat transcript: `logs/codexa-100m-native-v1/multi_turn_chat_2026-08-03.md`

This checkpoint is a meaningful improvement over the previous validation
perplexity (37.22 to 30.89), but it is not yet accepted as a conversational
model. Repetition must be addressed through additional base training and then
assistant-only conversational SFT.

The natural four-turn chat test failed memory and grounding: the model ignored
the greeting, did not recall the name Maya or Cape Town, ignored astronomy, and
repeated unrelated health text. This is the baseline that conversational SFT
must improve.

The LM Studio transcript confirms that the remaining problem is model quality:
runtime compatibility passes, but factual answers, arithmetic, instruction
following, and conversation all fail through repetition or topic drift.

## Next model contract

The replacement 100M model will use an LM Studio-compatible architecture from
the start: RMSNorm, SwiGLU, rotary position embeddings, and exact tokenizer
mapping. No post-training architecture adapter will be accepted.

## Fixed evaluation suite

Every checkpoint evaluation must record the same prompts and settings:

1. ordinary prose continuation;
2. factual explanation;
3. short instruction response;
4. multi-turn conversation;
5. repetition stress test;
6. LM Studio GGUF load and generation smoke test.

For each prompt, record the complete generated output, checkpoint step, token
count, tokens/second, temperature, top-k/top-p, and finish reason.

## Three-month schedule

| Period | Required record |
|---|---|
| Week 0 | Architecture/export compatibility gate and baseline outputs |
| Weeks 1–4 | Base pretraining checkpoints and weekly evaluation |
| Weeks 5–8 | Continued base training, regression checks, tokenizer/runtime checks |
| Weeks 9–10 | Conversational SFT checkpoints and multi-turn tests |
| Weeks 11–12 | Final SFT selection, LM Studio validation, comparison report |

## Checkpoint entry template

### YYYY-MM-DD — checkpoint name

- Training stage:
- Optimizer step / tokens seen:
- Validation loss / perplexity:
- LM Studio load: pass/fail
- Generation speed:
- Repetition score:
- Notes:

#### Fixed-prompt outputs

```text
Prompt:
Output:
```

## Acceptance gates

- GGUF tokenization matches native token IDs.
- LM Studio loads without an architecture warning.
- Native and LM Studio generations are materially equivalent.
- Repetition decreases across checkpoints.
- Conversational SFT must improve multi-turn behavior without unacceptable
  regression on the base-language prompts.

## 2026-08-03 — SFT pilot in progress

The first conversational fine-tuning run is active as `codexa-100m-sft-pilot`.
It is configured for 2,000 optimizer steps over 60,000 UltraChat training
conversations with 1,000 validation conversations and 10% base-corpus replay.
The visible viewer is `scripts/run_100m_sft_pilot.sh`; live metrics are written
to `logs/codexa-100m-sft-pilot/train_metrics.jsonl`.

## 2026-08-03 — Base corpus preparation milestone

The separate 1B base-corpus preparation completed before the interactive
session restarted. The run processed all 13,700,814 raw rows in 6,590 seconds
(1h 49m 50s) and produced approximately 54 GB of cleaned JSONL.

- Wikipedia accepted: 6,406,791; validation: 31,957.
- FineWeb-Edu accepted: 7,043,681; validation: 35,232.
- Exact within-source duplicates rejected: 1,023 Wikipedia and 249,319
  FineWeb-Edu.
- Manifest: `data/processed/base-v1/base_preparation_manifest.json`.
- Near-duplicate clustering: deferred and remains a production gate.

## 2026-08-03 — SFT pilot resumed

The interrupted conversational pilot resumed from its last saved milestone at
step 1,500 and is continuing toward the configured step 2,000 endpoint. The
native base checkpoint remains unchanged. Progress is visible in Kitty through
the shared dashboard and is recorded in
`logs/codexa-100m-sft-pilot/train_metrics.jsonl`.

## 2026-08-03 — SFT pilot complete

The conversational SFT pilot completed its planned 2,000 optimizer steps in
the restored Kitty viewer. Final metrics were 2.198 training loss, 2.003
validation loss, and 15,784,215 processed tokens. The checkpoint remains at
`checkpoints/codexa-100m-sft-pilot/latest.pt` pending evaluation and export
smoke gates.

## 2026-08-03 — 900M-class base training launched

The 934,356,480-parameter 900M-class base model is now training from random
weights as `codexa-900m-base-v1`. The run uses the passed production shape:
BF16, gradient checkpointing, 8-bit AdamW, context 2,048, microbatch 1, and
gradient accumulation 32. The configured budget is 10,000 optimizer steps
(655,360,000 tokens). The Kitty dashboard is attached and the first metrics are
finite at approximately 7,697 tokens/second.

## 2026-08-03 — 900M-class base run paused

The live base process is paused in place at optimizer step 418 (27,394,048
tokens) with `SIGSTOP`. A durable checkpoint was completed at step 250 and is
available for recovery if the process cannot be continued. Resume in place
with `kill -CONT 33993`.

## 2026-08-03 — Conversational quality gate failed

Deterministic probes of the native LM Studio export and completed SFT pilot
showed severe repetition. The SFT pilot can begin a relevant answer, but it
loops the same sentence and does not stop reliably; the native export also
drifts and fails factual and memory prompts. Neither checkpoint is accepted as
a chat model. Further work is required on SFT serialization/EOS supervision,
training duration, and controlled base replay before export.

## 2026-08-03 — Paused at checkpoint 500

Training resumed until the next durable checkpoint and is now paused at step
500, with `latest.pt` and its checksum/completion metadata verified. The user
can use the GPU; resume in place with `kill -CONT 33993`.

## 2026-08-04 — 900M-class base training complete

The 934,356,480-parameter base run completed at 10,000 optimizer steps and
655,360,000 processed tokens. Final training loss was 3.1042 and validation
loss was 3.3491. The final step-10,000 checkpoint is verified and preserved;
evaluation and export gates are next.

## 2026-08-04 — 900M base handoff exported

The verified step-10,000 checkpoint was exported to
`exports/codexa-900m-base-v1-lmstudio-f16.gguf` (SHA256
`506bbd45becc4b711cd512f204260d3496b3d5c76aa966d276f476f7dd8e789d`). Native
generation and GGUF structural validation passed. Redundant 900M milestones,
the duplicate best copy, and intermediate HF staging directories were moved
to Trash after validation; `latest.pt`, `previous.pt`, the tokenizer, datasets,
and the GGUF export remain preserved.
## 2026-08-05 — Conversational SFT v2 resumed

`codexa-900m-sft-v2` was interrupted after log-only progress reached optimizer step 1,836. The latest durable checkpoint was validated and contains optimizer step 1,750; its refreshed SHA-256 sidecar is `2364eaddc4668d077727ecf53b9dbb058e52852ef6151bad78537dcd6532e483`. Resume is being launched toward the existing 6,000-step target with BF16, activation checkpointing, microbatch 1, and gradient accumulation 32. Peak reserved VRAM observed before interruption was approximately 12.9 GiB; the run remains unvalidated until completion and smoke/quality gates pass.
The resume is confirmed at optimizer step 1,751 under a fresh run ID. The process is active as PID 6682 and the required Kitty viewer is attached separately as PID 6683. The resumed metric reports training loss 2.5412 and peak reserved VRAM 11,070,865,408 bytes; the run is not yet complete or acceptance-validated.

## 2026-08-06 — Conversational SFT v2 paused

The active `codexa-900m-sft-v2` process was suspended with `SIGSTOP` for a
power outage. PID `6682` is stopped, the 100x22 Kitty viewer remains attached,
and `latest.pt` is preserved at 04:17:52. The latest log-only metric reached
optimizer step 5,117; resume only after power returns, using the durable
checkpoint rather than assuming log-only progress is recoverable.

## 2026-08-06 — Conversational SFT v2 resumed

Power was restored and the paused process was continued with `SIGCONT`. PID
`6682` is active again, the required 100x22 viewer remains attached, and the
first post-resume metric reached optimizer step 5,118. The run remains
incomplete and acceptance validation is still pending.

## 2026-08-06 — 900M conversational SFT v2 completed and staged

The `codexa-900m-sft-v2` run completed at optimizer step 6,000 with
103,459,920 total tokens, training loss 1.5768, and validation loss 2.0316.
The final checkpoint passed its checksum check and was exported to
`exports/codexa-900m-sft-v2-lmstudio-f16.gguf` (SHA256
`5b5a2f7a17282946e6573c80027886ed4d0f41f705305b73fc678411f34d5698`). LM
Studio imported and loaded the 900M GGUF successfully, but its chat and raw
completion API smoke tests failed with the expected-format engine errors.
The checkpoint, datasets, logs, and prior lineages remain preserved while the
exporter/runtime compatibility gate is unresolved.

## 2026-08-06 — Native interactive chat path verified

Added `scripts/chat_native.py` for direct CUDA inference from the completed
900M SFT checkpoint. A native probe generated a coherent answer without LM
Studio, confirming that the checkpoint can be tested independently of the
failed GGUF adapter. The response still used “Open Assistant” identity text,
so native runtime success is not a conversational quality acceptance result.

## 2026-08-06 — Native model added to local Codexa CLI

The local-development Codexa launcher now supports `codexa-dev native`, which
loads the verified SFT v2 checkpoint and tokenizer directly on CUDA. The exact
CLI command completed an end-to-end smoke conversation without LM Studio. This
is a runtime-access success only; conversational quality remains under review.

The shell launcher was subsequently repaired so `codexa-dev native` keeps the
current terminal's stdin instead of disappearing into the generic external
terminal handoff. A visible Kitty session is running with the native checkpoint
loaded on CUDA and ready at the `You:` prompt.
## 2026-08-06 — Dedicated Codexa Native provider accepted structurally

The local Codexa CLI now exposes `Codexa Native` as a separate provider and
loads the 900M SFT v2 PyTorch checkpoint through a persistent JSONL bridge. A
two-turn CUDA smoke test passed bridge loading, request handling, and retained
history transport without LM Studio. Response quality remains below acceptance:
both smoke answers ignored the requested exact phrase and terminated at the
token limit. Provider transport is working; checkpoint behavior remains the
next quality gate.

## 2026-08-11 — Next base-training data prepared

The next base-training input is already present and was not rebuilt. The mixed
FineWeb-Edu/Wikipedia stream contains 12,819,847,234 training tokens across
13,383,283 documents, packed at context length 2,048 with zero repeated
documents. Recorded SHA-256 checksums for the mixed train file, index, and
manifest match the files on disk. No training process was launched.

The current 10,000-step configuration processes 655,360,000 tokens, or about
5.1% of this stream. A full single pass would require approximately 195,616
optimizer steps. Using observed 900M SFT throughput of roughly 2,800–3,100
tokens/second, that is approximately 48–53 days of continuous GPU time before
checkpoint, validation, and downtime overhead. The Python validator remains
pending because the local `.venv` is missing the `tokenizers` dependency.
## 2026-08-11 — 900M SFT-v2 behavior checkpoint

The native `codexa-900m-sft-v2` checkpoint at optimizer step 6,000 loads with
the repository's legacy checkpoint fallback, but the bounded CPU behavior probe
does not pass reasoning quality. It generated a relevant photosynthesis
sentence, then answered `17 * 24` incorrectly and repeated the same answer.
The probe was stopped before the full suite because the host PyTorch build has
no CUDA support and CPU generation is very slow. This is a quality failure,
not evidence that the checkpoint is corrupted. Keep the checkpoint, tokenizer,
and model configuration until the next training/evaluation decision is made.

## 2026-08-14 — Preparation speed and acceptance recheck

The existing full preparation output was verified without rebuilding it. The
manifest records 13,700,814 input rows and 6,590.5 seconds elapsed, or about
2,078 rows/second, producing approximately 54 GB of processed JSONL. All four
processed output checksums match the manifest. A 200-batch host memmap probe
read 409,600 tokens at approximately 14.9M tokens/second.

The repository test run completed with 56 passing tests and 3 failures. The
failures are stale model/config expectations: tests still assert 921,773,568
parameters and older model keys, while `configs/1b.yaml` currently resolves to
934,356,480 parameters. The production mixed token-data validator also fails
before scanning because the older validator requires `eos_token_id`, which is
absent from that mixed manifest. The previous verified 900M CUDA BF16 benchmark
remains 7,700.7 tokens/second, or 8.51 seconds per 65,536-token optimizer
step.

Next gate: align the validator and stale fixtures, rerun all validation, then
perform a fresh visible 12-step production-shape benchmark before launching
any extended base-training budget.

## 2026-08-14 — Native inference speed diagnosis

The current native CUDA path was benchmarked on the RTX 4080 with the 900M SFT
v2 checkpoint. Generation measured approximately 117 tokens/second for a
32-token prompt, 61 tokens/second for a 128-token prompt, and 21 tokens/second
for a 512-token prompt. A 128-token prompt with 64 generated tokens measured
59 tokens/second. Inspection confirms that `generate_sequences` reruns the
full growing sequence for each new token; attention has no reusable KV-cache
state. The speed degradation with prompt length is therefore an implementation
bottleneck, not a training-data problem.

Next step: add an opt-in KV-cache implementation, preserve uncached behavior as
a reference path, test cached/uncached logit and stopping equivalence, and
repeat the same CUDA benchmark. Quantized GGUF comparison follows after a
local runtime is available or explicitly selected.

## 2026-08-14 — KV-cache milestone

The native inference path now supports cached attention keys and values while
retaining the uncached reference path. Twelve focused model/generation tests
pass, including cached/uncached logit equivalence and identical greedy output.

On the RTX 4080 with the 900M SFT v2 checkpoint, cached versus uncached speed
was 137 versus 117 tokens/second for a 32-token prompt, 124 versus 61 for a
128-token prompt, 96 versus 21 for a 512-token prompt, and 125 versus 59 for a
128-token prompt generating 64 tokens. The largest measured improvement is
approximately 4.5x for long context.

Next gate: run the full regression suite and measure first-token latency and
steady-state multi-turn chat speed before adding another optimization.

## 2026-08-14 — Torch compile gate blocked by environment

The opt-in `torch.compile` path was wired into one-shot generation and native
chat. The first real 900M CUDA attempt did not reach benchmarking: PyTorch
Inductor/Triton failed while compiling its CUDA helper because the Python 3.14
environment lacks `Python.h`. The compile path remains disabled by default.
The already validated KV-cache path is unaffected.

Next gate: use a Python environment with compatible development headers and a
working Triton compiler, then compare compiled and cached generation for output
equivalence, stopping behavior, and steady-state tokens/second.

## 2026-08-14 — Torch compile benchmark complete

The missing Python headers were installed and a temporary no-space compiler
alias allowed Inductor to build around the repository path issue. The compiled
900M CUDA path produced identical output to the KV-cache path, but required
approximately 45 seconds to warm up and reached about 126.6 tokens/second,
compared with 125.5 tokens/second uncached by compile. The approximately 1%
steady-state gain is not sufficient to make compilation the default.

Next step: evaluate weight-only quantization or another optimized inference
runtime. Keep the stable KV-cache path as the production default.

## 2026-08-16 — Base corpus storage cleanup

The obsolete raw and derived base-training datasets were moved to the desktop
Trash to reclaim working-tree storage while retaining the current
conversational improvement path. The preserved base replay data is
`data/tokenized/base-v1/mixed/` at approximately 27 GB, alongside the chat/SFT
datasets. The old base raw/processed copies and unused tokenized variants are
recoverable from Trash until it is emptied.

Next step: prepare only the data required by the next training phase after the
model-improvement plan is selected.

## 2026-08-16 — 100M checkpoint storage cleanup

The completed 61 GB `checkpoints/codexa-100m-native-v1/` lineage was moved to
the desktop Trash. Its HF and LM Studio exports remain available for comparison
or inference, while the 900M base and SFT checkpoints remain the active
improvement path.

The user subsequently confirmed permanent deletion of the trashed 100M native
checkpoint directory. Approximately 61 GB of checkpoint artifacts were
reclaimed; the 100M exports remain available.

## 2026-08-22 — Diagnostic gate complete; training paused

No new training was launched. The chat serializer and shifted assistant-only
targets passed 12 focused tests, including exact END-token alignment; the tiny
CUDA overfit reproduced all four exact responses. A streaming audit found
26,082 accepted UltraChat records and 29,186 accepted OASST1 records in the
balanced sample, with complete over-context conversations rejected rather than
truncated. The balanced 900M checkpoint was re-probed with a reset before every
prompt: it stopped on some responses but failed arithmetic, explanation,
correction, and list-quality gates. The next run remains blocked pending a
reviewed short-answer/correction/instruction-following dataset and recipe.

## 2026-09-10 — Next run planned: bounded conversational repair pilot

The next proposed run is `codexa-900m-sft-repair-v1`, starting from the
retained 900M base checkpoint. It will use a deterministic filtered
short-response dataset, 512-token pilot context, no base replay, a `1e-5` peak
learning rate, 500 warmup steps, and 2,000 optimizer steps. The launch remains
paused until the dataset audit, 100-record dry run, and CUDA overfit gate pass;
the final checkpoint must also pass isolated arithmetic, recall, correction,
list, explanation, stopping, and contamination probes before export or
promotion.

## 2026-09-10 — Repair SFT completed; conversational gate failed

The 2,000-step repair run completed and its checkpoint checksum passed. Native
probes improved arithmetic, genuine two-turn memory, and correction behavior,
but explanation prompts repeated `photosynthetic` text until the length limit
and an exact three-item tea request returned only two items. The checkpoint is
retained but not exported or promoted.

## 2026-09-10 — Repair failure diagnosed as template memorization

Additional probes showed exact anchor prompts succeeding while unseen variants
failed: `18 + 24` was rewritten as `19 + 24 = 42`, an unseen correction was
wrong, and unrelated list requests collapsed to the same fruit list. The repair
corpus contained only 71 train anchors built from four repeated templates per
category, while validation loss flattened as training loss continued down. The
checkpoint therefore improved memorized forms without learning robust task
generalization.

## 2026-09-11 — Five-hour 900M base continuation launched

The approved continuation initializes a fresh AdamW8bit optimizer from the
verified 900M base weights and runs 2,000 updates, approximately 131.07M new
tokens. A non-overlapping 39.30M-token tail is reserved from the retained base
stream for validation. The pre-run 16-batch baseline loss is `3.2042928`; range
and checkpoint tests pass. The required Kitty 100x22 viewer is attached, and
post-run checksum, loss comparison, and generation checks remain required.

## 2026-09-11 — Base continuation paused at step 7

The user-requested pause was applied with `SIGSTOP` to PID `236816`. The process
is retained in stopped state with 458,752 tokens completed; logs, data, model
weights, and the Kitty viewer remain intact. Resume requires explicit approval.

## 2026-09-11 — Five-hour continuation ended

The user ended the paused run. The process was terminated at optimizer step 13
after 851,968 tokens, before the first scheduled checkpoint at step 500. No new
model checkpoint exists; the original 900M base, datasets, tokenizer, exports,
and all prior model artifacts remain unchanged. The run log is retained and
marked interrupted.

## 2026-09-10 — Repair corpus preflight passed; launch held

The repair corpus was generated with 12,000 deterministic natural records and
96 behavioral anchors, producing 9,627 train and 2,469 validation records at a
512-token serialized limit. Both splits passed serialization and END alignment
audits with no prompt echoes. The CUDA 300-step chat overfit reproduced all four
diagnostic responses exactly and stopped on the native END token. The prepared
2,000-step repair launcher exists, but the actual training run was not started.

## 2026-09-10 — 900M repair SFT launched

The approved `codexa-900m-sft-repair-v1` run was launched from the checksum-
verified 900M base checkpoint with the prepared repair corpus, no base replay,
`1e-5` peak learning rate, 500 warmup steps, and 2,000 optimizer steps. The
required Kitty 100x22 viewer was opened. Behavioral acceptance and export are
pending completion.

## 2026-10-08 — Independent specialist Stage 1 infrastructure

A frozen EmbeddingGemma 2 programming-request classifier is being added outside
all native/base/SFT model lineages. The baseline remains three existing failures
(934M versus stale 921M assertions and missing position-embedding fixture fields).
The first full check after adding the specialist reports 91 passed, 5 skipped,
and those same three failures. The skips concern scikit-learn-dependent new tests;
the separate dependency environment is still installing. No generative run was
started and no artifact was removed. No human-reviewed intent dataset exists,
so classifier training and accuracy are intentionally unavailable.

## 2026-10-08 — Specialist Stage 1 infrastructure and real encoder verification complete

The separate frozen-embedding classifier infrastructure passes all 39 specialist
tests in its own environment. The existing generative suite still has the same
three baseline failures (92 passed, 5 specialist dependency skips). Actual
EmbeddingGemma 2 text-only loading passed on CUDA BF16 and CPU FP32 with
271,002,624 frozen parameters and normalized deterministic 768-dimensional
vectors. The final five-call warmed encoder median was 15.208 ms on the RTX 4080
and 46.008 ms on CPU; encoder CUDA peak allocation was 553.4 MiB. These are
encoder-only measurements. No intent dataset, task-trained head, task accuracy,
or baseline-versus-MLP task comparison is available. No generative run was
started and no existing model/data/log/checkpoint artifact was removed.


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


## 2026-10-08 — Canonical workspace consolidation

Lifted integration history to the renamed workspace root and registered seven existing repositories as pinned submodules. Preserved source/Git recovery records and relocated historical assets to a single protected temporary store with before/after SHA-256 verification. Canonical environments and asset resolution no longer depend on project 31. NumPy remains independently implemented and packaged. Actual-checkpoint parity and bounded CPU/CUDA validations are recorded in documentation/migration/. Originals remain pending review and independent backup; no model lineage was promoted.
