# T5: Training & Fine-Tuning

Issue: #29 · Contract: 1.0.0 · Kinds: `training_framework`, `training_compute`, `training_dataset`, `fine_tuned_model`
Status: summary of the merged component records · Last researched: 2026-10-16

This is the workstream summary for T5. It consolidates the four component decision records and does not replace them. The records are reviewed research; consuming-owner acceptance of their proposed handoffs remains pending.

The four component records are merged into `main` (#68, #76, #77, #84). Merging this summary does not complete the T5 workstream or its component issues, confirm any handoff, or close any issue. Acceptance stays with the issue owners.

| Component | Issue | Decision record | PR | Structured proposals |
| --- | --- | --- | --- | --- |
| Training Framework | #30 | [training-framework.md](training-framework.md) | #68 (merged) | 4 `training_framework` proposals ([`catalog/proposals/training_framework-*.json`](../../catalog/proposals/)), all provenance `unverified` |
| Training Compute | #31 | [training-compute.md](training-compute.md) | #77 (merged) | none (see blockers) |
| Training Dataset | #32 | [training-dataset.md](training-dataset.md) | #76 (merged) | none (see blockers) |
| Fine-Tuned Model | #33 | [fine-tuned-model.md](fine-tuned-model.md) | #84 (merged) | none (user-specific artifact) |

## Scope and optionality

T5 answers whether the selected model can and should be customised, and what the resulting artifact requires downstream. It is optional and must disappear cleanly when unused.

This was checked with the v1 reference evaluator (`contracts/v1/reference/evaluate.py`), the baseline ruleset and the synthetic fixture build, run with all T5 selections present, removed, and present with `enabled: false`:

- **Six baseline rules are triggered by a T5 selection:** `rule.training.model.capable`, `.dataset.governance`, `.base.lineage`, `.method.support`, `.backend.support` and `.artifact.engine`. They pass with T5 present and are `skipped` when T5 is removed or disabled.
- **Two shared rules list T5 kinds among affected kinds** (`rule.engine.model.format`, `rule.budget.monthly.cap`). Their outcomes do not change.
- **No other rule's outcome changes.**
- **Dependency graph:** 7 of the 10 baseline edges touching T5 kinds activate only under `fine_tuning_enabled`; the other 3 are `if_selected`.

These results were reproduced in an independent rerun of the same fixture.

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

- **Memory:** a component formula with gradient dtype, optimiser and fused-loss choice as explicit inputs. The compute note collects 12 published comparison rows; B12 is a capability claim without measurements. These rows do not establish calibration of the Qwen3-8B worked example or a general fit guarantee.
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
  - Apache-2.0 notice duties are conditional, not blanket: §4(a) licence copy, §4(b) change notices on modified files, and §4(d) NOTICE attributions only if the base distribution includes a NOTICE file (A-18a to A-18c).
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

**Evidence labels.** Under the interim #41 policy adopted in the [#75 owner review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75#pullrequestreview-5550616927), *checked* means provenance was confirmed against the cited primary source on its access date. *Verified* means independently reproduced (a second source or a reproducible test). None of these rules has been independently reproduced, so the table reports rules as **source checked** and none as verified. A rule may pass on checked evidence while its result stays "unverified".

Counts below were reconciled against the merged component notes.

| Series | Component | Rules | Source checked | Hypothesis / policy / partial |
| --- | --- | --- | --- | --- |
| F-01 – F-24 | #30 | 24 | 21 | F-13 (policy), F-17 ("competing model" undefined), F-24 (AGPL scope) |
| K-01 – K-09 | #31 | 9 | 5 | K-02 (fit threshold), K-06 (needs #10 dtype facts), K-08 (contract gap), K-09 (policy) |
| D-01 – D-22 | #32 | 22 | 21 | D-20 (leakage policy, with #36) |
| A-01 – A-20 (A-18 split into A-18a, A-18b, A-18c) | #33 | 22 | 20 | A-13 (partial: classic-FAQ wording), A-20 (evaluation gate policy, with #36) |

77 rules in total, 67 source checked.

A-06 is counted as source checked but carries a stated inference: no PEFT document states "merge into the 16-bit base" positively. K-01 and K-04 are counted with limits their notes state (an estimated overhead factor; Axolotl only). The sources behind D-14 (an archived snapshot, because the live pages were not readable) and D-19 (a 2023 Hub snapshot) are limited as well.

A-18a, A-18b and A-18c replace the single A-18, which failed every distributed Apache-2.0 artifact that lacked a NOTICE or change notice. They encode the §4(a) licence copy, §4(b) change notices on modified files and §4(d) NOTICE attributions. §4(d) applies only if the base distribution includes a NOTICE file, and §4(c) is not encoded as a rule. Each rule can return `unknown` when applicability is unresolved, and none infers applicability from `adapter_only` or artifact format.

Contract-change proposals are consolidated in the #40 comment of 2026-10-16:
- `training_framework` method enum values and fields;
- optional `backends` for managed services;
- optional `compute_profile_ref` for managed training;
- Pricebook training meters;
- a training-memory ResourceEstimate metric;
- `training_dataset` and `data_source` provenance fields replacing the governance booleans.

#33 adds: `base_model_revision`, adapter rank / target modules / PEFT variant / `modules_to_save`, `base_quantization`, `added_tokens`, `method`, `evaluation_report_ref`, `signature` and `base_notice_file_present` (needed by A-18c), plus revision-pinned catalog references.

## Outgoing handoffs (none confirmed)

| Handoff | From | To | Owner |
| --- | --- | --- | --- |
| Per-checkpoint licence, weight access, revision, whether the base distribution at that revision includes a NOTICE file, provider fine-tuning lifecycle | #30, #33 | #6, #5 | @zwright8 |
| Missing accelerator and compute-profile records for the priced SKUs; a peak dense TFLOP/s field; missing hosting and storage records; adapter and merged VRAM | #31, #33 | #10, #9 | @Mattycodes69 |
| Adapter and format support facts for `inference_engine` items | #33 | #11 | @Mattycodes69 |
| Training vs retrieval rights boundary; `data_source` for training sources | #32 | #13 | @zabyxc01 |
| Leakage method and eval-set freeze; pre-deployment evaluation gate | #32, #33 | #36 | @PUSHINGSQUARES |
| Training price normalisation; post-training hosting next to training cost | #31, #33 | #39 | @PUSHINGSQUARES |
| Fine-tune lifecycle at deployment (OpenAI shutdown with base; Foundry 15-day deletion) | #33 | #37 | @PUSHINGSQUARES |
| User attestations (EU market, revenue, MAU, residency, lawful basis) | #30, #32 | #2, #3 | @tynamite |
| Rule format and contract changes; "competing model" policy | all | #40 | @tynamite |
| Evidence grading (checked vs verified), price freshness | all | #41 | @tynamite |

Incoming T2 boundaries have separate receiving-owner receipts: [#9 → #31](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/9#issuecomment-6230482274), [#10 → #31](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10#issuecomment-6230482484), and [#11 → #33](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/11#issuecomment-6230482684). These accept reuse of existing records and narrow tokenizer/template ownership; they do not accept the reverse-direction requests in this table or supply missing catalog records. The receipts were read back on 2026-10-18.

Owners are the live GitHub assignees as of 2026-10-16 and are not duplicated elsewhere.

## Blockers on structured artifacts

T2 proposals merged to `main` in #75 already supply part of what T5 references: three `accelerator` records (`nvidia-h100-sxm`, `nvidia-l40s`, `amd-mi300x`) with VRAM and precision inputs, one `compute_profile` (`aws-ec2-g6e-xlarge-us-east-1`), `hosting_platform` and `storage` records, and a `gpu_hour` meter. They are proposals under their own review, not approved catalog data. The one existing profile is a valid `compute_profile_ref` target, and having only one profile is not a schema blocker. The meter enum's `gpu_hour` can represent per-GPU-hour billing, such as the Fireworks Dedicated Training API row, once matching catalog references exist; the other managed training rows need separate meter review, and those limits do not exclude all managed training prices from v1. The S3 Standard storage identity was added in #158; its historical P13 rate has not been rebound to that catalog version. The remaining gaps are the records and fields that actually do not exist, listed in [Upstream T2 records](training-compute.md#upstream-t2-records).

| Artifact | Blocked by |
| --- | --- |
| `training_compute` items, training Pricebooks, ResourceEstimates | #31 proposes no `training_compute` item and no Pricebook or ResourceEstimate. Missing records: `compute_profile` for every priced SKU except `aws-ec2-g6e-xlarge-us-east-1` (#10), `accelerator` for A100 80 GB (#10); RTX 4090 identity is now supplied by `nvidia-geforce-rtx-4090` version `2026-10-18` without a profile/rate binding, `hosting_platform` for Google Cloud, Azure, Lambda and CoreWeave (#9). Unresolved fields and meters: peak dense TFLOP/s per accelerator, training-token, job-minimum, training-hour and model-storage meters, optional `compute_profile_ref` for managed services, a training-memory ResourceEstimate metric (#40), and whether a multi-GPU instance-hour price maps to `gpu_hour` per GPU or per instance (#39) |
| `data_source` items from the source audit | `spec_data_source` has no licence, terms or opt-out fields; agreement needed with #13 and #40 |
| Managed `training_framework` items | `backends` required but not user-visible for managed services (#40) |
| `fine_tuned_model` items | User-specific; references require `model` and `training_dataset` items, and A-18c needs the proposed `base_notice_file_present` fact (#40, #6) |

None of these is a native GitHub blocker; they are information dependencies under `docs/DEPENDENCIES.md`.

## Open questions

| Question | Owner |
| --- | --- |
| What counts as a "competing model" under provider output terms (F-17, D-12–D-14) | #40 · @tynamite |
| BGH appeal I ZR 281/25 on natural-language TDM reservations (pending) | #32 · @appletechie |
| Mistral Forge licensing and weight export (not public) | #30 · @appletechie |
| ONNX export for any training framework | #30 · @appletechie |
| GRPO and distillation time and cost models; calibrate the Qwen3-8B example with a dry run | #31 · @appletechie |
| vLLM/SGLang LoRA on GGUF bases; SGLang on quantised bases; TGI and llama.cpp LoRA limits; Vertex PEFT_ADAPTER output form; Bedrock import of adapters; Fireworks retention; tuned-Gemini lifecycle | #33 · @appletechie |
| Priority: P2 remains appropriate for all T5 issues; no product decision makes fine-tuning part of the first release | #29 · @appletechie |

## Secondary inputs

The workstream owner supplied two internal documents, used as leads and re-checked against primary sources; neither is committed:
- a 165-row free training-source audit;
- a local training-methods guide.

Where they disagreed with primary sources, the notes say so. For example, the guide's 8-bit Adam memory figure is refuted (#31).

## Workstream done when

- [ ] #30–#33 closed with merged decision records meeting their acceptance criteria (the four records are merged; component acceptance and handoffs remain pending)
- [ ] Handoffs above confirmed by the consuming owners
- [ ] This summary merged, with rules contributed to #40 and open questions current
