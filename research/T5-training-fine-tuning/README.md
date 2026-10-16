# T5: Training & Fine-Tuning

Issue: #29 · Contract: 1.0.0 · Kinds: `training_framework`, `training_compute`, `training_dataset`, `fine_tuned_model`
Status: **draft reconciliation, not ready to merge** · Last researched: 2026-10-16

This is the workstream summary for T5. It consolidates the four component decision records and does not replace them. Every finding below is **draft research awaiting review**, and no handoff has been confirmed by a consuming owner yet.

**The four component records are not on `main`.** They exist only as open proposal PRs, each under change requests. The links below are pinned to the PR head commits that this draft was reconciled against, not to files in this branch. They will move as the PRs are corrected. Counts and labels in this summary describe those pinned heads and are provisional until the components merge and this summary is re-reconciled.

Merging this summary would not accept the T5 workstream, any component record or any handoff. Acceptance stays with the issue owners.

| Component | Issue | Decision record (pinned proposal head) | PR | Structured proposals |
| --- | --- | --- | --- | --- |
| Training Framework | #30 | [training-framework.md @ 4063552](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/40635525c66bbcfbc9a5a549c826c4cfa89ab2cd/research/T5-training-fine-tuning/training-framework.md) | #68 (open, changes requested) | 4 `training_framework` proposals on the PR branch (`catalog/proposals/training_framework-*.json`); none on `main` |
| Training Compute | #31 | [training-compute.md @ 6396aec](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/6396aec760a5d6ac80577b107b7af1c47c575e84/research/T5-training-fine-tuning/training-compute.md) | #77 (open, changes requested) | none (see blockers) |
| Training Dataset | #32 | [training-dataset.md @ daa9666](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/daa9666c3c241e00ed7ec59cd7151a0e603d6558/research/T5-training-fine-tuning/training-dataset.md) | #76 (open, changes requested) | none (see blockers) |
| Fine-Tuned Model | #33 | [fine-tuned-model.md @ 3f8ad44](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/3f8ad4473de359e727a2ff1bd01225161b67fa90/research/T5-training-fine-tuning/fine-tuned-model.md) | #84 (open, changes requested) | none (user-specific artifact) |

Corrections pending in the component PRs, per their live reviews:

- #68: its `Verified` label and the four `CatalogItem` provenance entries (`verification_status: verified`) conflict with the adopted checked-versus-verified evidence policy (see "Evidence labels" under Rules contributed to #40). #40/#2/#3 routing needs refreshing.
- #76: `Verified` is defined as "cited text was read directly", which redefines verification. #40 routing needs refreshing. The `license_verified` field name is canonical and stays.
- #77: it reports no T2 compute profiles, accelerators or hosting platforms, but #75 has merged T2 proposals into `main`. #40 routing needs refreshing.
- #84: rule A-18 fails every distributed Apache-2.0 artifact lacking a NOTICE or change notice, without the applicability conditions of Apache-2.0 §4(b) and §4(d). It also needs the checked-versus-verified distinction.

## Scope and optionality

T5 answers whether the selected model can and should be customised, and what the resulting artifact requires downstream. It is optional and must disappear cleanly when unused.

This was checked with the v1 reference evaluator (`contracts/v1/reference/evaluate.py`), the baseline ruleset and the synthetic fixture build, run with all T5 selections present, removed, and present with `enabled: false`:

- **Six baseline rules are triggered by a T5 selection:** `rule.training.model.capable`, `.dataset.governance`, `.base.lineage`, `.method.support`, `.backend.support` and `.artifact.engine`. They pass with T5 present and are `skipped` when T5 is removed or disabled.
- **Two shared rules list T5 kinds among affected kinds** (`rule.engine.model.format`, `rule.budget.monthly.cap`). Their outcomes do not change.
- **No other rule's outcome changes.**
- **Dependency graph:** 7 of the 10 baseline edges touching T5 kinds activate only under `fine_tuning_enabled`; the other 3 are `if_selected`.

The T5 rule proposals (F-, K-, D- and A-series) are written to apply only when a T5 selection exists. They are not yet in a versioned ruleset, so they have not been run through the evaluator.

## Decisions by component

### Training framework (#30)

- **Customisation availability.** Most first-party APIs no longer offer self-serve fine-tuning:
  - OpenAI closes job creation to all customers on 2027-01-06.
  - Mistral and Cohere have deprecated theirs.
  - The Gemini API has none (Vertex AI does).
  - No Claude model remains fine-tunable: Claude 3 Haiku reached end of life on Bedrock on 2026-09-10.
- **Licence checks per checkpoint, not per family.** Qwen 3.8, Mistral, Meta, Gemma and Cohere ship mixed licences across sizes.
- **Recommended self-hosted stack:** TRL + PEFT, with Axolotl and Unsloth as alternatives. All are Apache-2.0 at the core and actively released, and they are proposed as catalog items.
- **Not recommended:**
  - torchtune is unmaintained.
  - NVIDIA's LLM fine-tuning moved from `NVIDIA/NeMo` to Megatron-Bridge, AutoModel and NeMo-RL.
  - Only Axolotl and Unsloth export GGUF natively; PEFT adapters convert with llama.cpp.
- **Managed services:** prefer the ones that return portable artifacts (Vertex open models, Together, Fireworks). The builder must show provider lock-in before selection.

### Training compute (#31)

- **Memory:** a component formula with gradient dtype, optimiser and fused-loss choice as explicit inputs, calibrated against 12 published measurements.
  - Logits are often the largest swing: for Qwen3-8B at 4,096 tokens, 2.5–7.5 GB per sequence without fused cross-entropy.
- **Time:** measured tokens/s where a calibration row exists. Otherwise 6·N·D (full) or ≈4·N·D (LoRA, a project estimate) FLOPs with an MFU range.
- **Cost:** a 30M-token LoRA run on an 8B model costs about $1–4 in rented-GPU compute, or $10–45 on a managed service. Post-training hosting dominates instead: about $1,241/month for a fine-tuned Azure deployment, roughly 8× its training cost.

### Training dataset (#32)

- **Rights and privacy checklist (C1–C15):** EU AI Act Art. 53 and the GPAI modifier threshold, DSM Art. 4(3) machine-readable opt-outs, GDPR (EDPB, CNIL, ICO), US fair-use rulings, Creative Commons and ODC licence scope, and provider output terms.
  - Each item states where training rights differ from retrieval rights (#13).
- **Preparation procedure:**
  1. Freeze the eval set (with #36).
  2. Validate the format.
  3. Scan for PII.
  4. Deduplicate.
  5. Check leakage in layers: exact, 13-gram, MinHash, then embedding plus LLM judge.
  6. Split by source.
  7. Record lineage (Croissant 1.1 / RAI).
- **Source audit:** the owner's 165-source shortlist was re-checked against the Hugging Face API. 118 of 137 licences match, and 7 substantive discrepancies are recorded.

### Fine-tuned model (#33)

- **Artifact type:** adapter, merged weights, GGUF or provider-hosted. Serving compatibility depends on format, adapter vs merged, base id and revision, rank and target modules, PEFT variant, base quantisation and added tokens.
- **Changes since common guidance:**
  - Ollama no longer accepts LoRA adapters (v0.34.1+).
  - TGI is archived.
  - Together and Fireworks serve adapters only on dedicated or on-demand deployments.
- **Recommendation:**
  - Keep both an adapter and a merged checkpoint, pinned to the base's full commit SHA.
  - Merge into the 16-bit base, then quantise.
  - Avoid adding tokens.
- **Evaluation gate for #36:**
  - Safety regression vs the base: 10 adversarial examples took GPT-3.5 Turbo from 1.8% to 88.8% harmfulness.
  - A training-data harm screen.
  - Capability retention.
  - Task gain.

## Rules contributed to #40

**Evidence labels.** Under the interim #41 policy adopted in the [#75 owner review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75#pullrequestreview-5550616927), *checked* means provenance was confirmed against the cited primary source on its access date. *Verified* means independently reproduced (a second source or a reproducible test). None of these rules has been independently reproduced, so the table calls the components' `verified` labels **source-checked** and does not report any rule as verified. A rule may pass on checked evidence while its result stays "unverified".

Counts below are taken from the pinned component heads and are **provisional**. They will change when #68, #76, #77 and #84 land their corrections (including the A-18 rewrite in #84) and this summary is re-reconciled.

| Series | Component | Count | Source-checked (labelled `verified` in the component) | Hypothesis / policy / partial |
| --- | --- | --- | --- | --- |
| F-01 – F-24 | #30 | 24 | 21 | F-13 (policy), F-17 ("competing model" undefined), F-24 (AGPL scope) |
| K-01 – K-09 | #31 | 9 | 5 | K-02 (fit threshold), K-06 (needs #10 dtype facts), K-08 (contract gap), K-09 (policy) |
| D-01 – D-22 | #32 | 22 | 21 | D-20 (leakage policy, with #36) |
| A-01 – A-20 | #33 | 20 | 18 | A-13 (classic-FAQ wording), A-20 (evaluation gate policy, with #36) |

A-06 is counted as source-checked but carries a stated inference. A-18 is counted but is under correction in #84.

Contract-change proposals are consolidated in the #40 comment of 2026-10-16:
- `training_framework` method enum values and fields;
- optional `backends` for managed services;
- optional `compute_profile_ref` for managed training;
- Pricebook training meters;
- a training-memory ResourceEstimate metric;
- `training_dataset` and `data_source` provenance fields replacing the governance booleans.

#33 adds: `base_model_revision`, adapter rank / target modules / PEFT variant / `modules_to_save`, `base_quantization`, `added_tokens`, `method`, `evaluation_report_ref` and `signature`.

## Handoffs (none confirmed)

| Handoff | From | To | Owner |
| --- | --- | --- | --- |
| Per-checkpoint licence, weight access, revision, provider fine-tuning lifecycle | #30, #33 | #6, #5 | @zwright8 |
| Accelerator facts (VRAM, dtype, peak FLOP/s), compute profiles, hosting regions; adapter and merged VRAM | #31, #33 | #10, #9 | @Mattycodes69 |
| Adapter and format support facts for `inference_engine` items | #33 | #11 | @Mattycodes69 |
| Training vs retrieval rights boundary; `data_source` for training sources | #32 | #13 | @zabyxc01 |
| Leakage method and eval-set freeze; pre-deployment evaluation gate | #32, #33 | #36 | @PUSHINGSQUARES |
| Training price normalisation; post-training hosting next to training cost | #31, #33 | #39 | @PUSHINGSQUARES |
| Fine-tune lifecycle at deployment (OpenAI shutdown with base; Foundry 15-day deletion) | #33 | #37 | @PUSHINGSQUARES |
| User attestations (EU market, revenue, MAU, residency, lawful basis) | #30, #32 | #2, #3 | @tynamite |
| Rule format and contract changes; "competing model" policy | all | #40 | @tynamite |
| Evidence grading (checked vs verified), price freshness | all | #41 | @tynamite |

Owners are the live GitHub assignees as of 2026-10-16 and are not duplicated elsewhere.

## Blockers on structured artifacts

Upstream T2 records **do exist** on `main` since #75: `accelerator` (3), `compute_profile` (1, `aws-ec2-g6e-xlarge-us-east-1`), `hosting_platform` (5), `storage` (4) and `inference_engine` (3) proposals, plus a `gpu_hour` meter in `pricing/proposals/t2-hosting-2026-10-16.json`. They are proposals, not a published catalog. Whether they cover the SKUs, dtype facts (K-06) and regions that #31 prices has not been reconciled; that belongs to the #77 correction. Until it lands, this table lists only the training-specific gaps that #31 and #40 describe, not a missing upstream catalog.

| Artifact | Blocked by (provisional, pending #77, #68, #76 and #84 corrections) |
| --- | --- |
| `training_compute` items, training Pricebooks, ResourceEstimates | Training-specific gaps only: the Pricebook has no training-token or job-minimum meters; there is no training-memory metric (#40). Whether the existing T2 `compute_profile` / `accelerator` proposals suffice for #31's priced SKUs is unreconciled (#77) |
| `data_source` items from the source audit | `spec_data_source` has no licence, terms or opt-out fields; agreement needed with #13 and #40 |
| Managed `training_framework` items | `backends` required but not user-visible for managed services (#40) |
| `fine_tuned_model` items | User-specific; references require `model` and `training_dataset` items |

None of these is a native GitHub blocker; they are information dependencies under `docs/DEPENDENCIES.md`.

## Open questions

| Question | Owner |
| --- | --- |
| What counts as a "competing model" under provider output terms (F-17, D-12–D-14) | #40 · @tynamite |
| BGH appeal I ZR 281/25 on natural-language TDM reservations (pending) | #32 · @appletechie |
| Mistral Forge licensing and weight export (not public) | #30 · @appletechie |
| ONNX export for any training framework | #30 · @appletechie |
| GRPO and distillation time and cost models; calibrate the Qwen3-8B example with a dry run | #31 · @appletechie |
| vLLM/SGLang LoRA on GGUF bases; SGLang on quantised bases; TGI and llama.cpp LoRA limits; Vertex PEFT_ADAPTER output form; Bedrock import of adapters; tuned-Gemini lifecycle | #33 · @appletechie |
| Priority: P2 remains appropriate for all T5 issues; no product decision makes fine-tuning part of the first release | #29 · @appletechie |

## Secondary inputs

The workstream owner supplied two internal documents, used as leads and re-checked against primary sources; neither is committed:
- a 165-row free training-source audit;
- a local training-methods guide.

Where they disagreed with primary sources, the notes say so. For example, the guide's 8-bit Adam memory figure is refuted (#31).

## Workstream done when

- [ ] #30–#33 closed with merged decision records meeting their acceptance criteria
- [ ] Handoffs above confirmed by the consuming owners
- [ ] This summary merged, with rules contributed to #40 and open questions current
