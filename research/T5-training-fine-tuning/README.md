# T5: Training & Fine-Tuning

Issue: #29 · Contract: 1.0.0 · Kinds: `training_framework`, `training_compute`, `training_dataset`, `fine_tuned_model`
Status: summary of the merged component records · Last researched: 2026-10-16

This is the workstream summary for T5. It consolidates the four component decision records and does not replace them. The records are reviewed research; handoff acceptance is limited to the actual receiving decisions linked below.

**Record reconciliation, 2026-10-18:** the framework summary follows the accepted #375/#380 scope corrections and `training-framework-decision/0.2.0`; the compute summary follows `training-compute-decision/0.2.0`, including its scoped accounting, K-series envelope and amended cost intake. Cost and artifact statements retain the component notes' stated conditions. This is a consistency update against the cited repository records, not a new vendor-source retrieval, training/export experiment or blanket acceptance of the workstream. Original source dates, versions and evidence grades remain in the component records.

The four component records are merged into `main` (#68, #76, #77, #84). Merging this summary does not complete the T5 workstream or its component issues, confirm any handoff, or close any issue. Acceptance stays with the issue owners.

The [actual #30 reconciliation](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/30#issuecomment-6253889603) records its research completion at 19:02:53 UTC on 2026-10-18, after the scoped #380 correction. For #31–#33 and the parent workstream, use the live issue records and cited receiving decisions to determine research completion and remaining work; this summary supplies no additional issue acceptance.

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

- **Customisation availability:** assess the exact service, account, model, method, region and date using the [framework record](training-framework.md), including its F-18–F-21 boundaries.
  - The recorded OpenAI new-job cutoff is 2027-01-06, with earlier account-eligibility gates. Existing fine-tuned-model inference follows its exact base's separate shutdown schedule; unknown customer history does not establish eligibility.
  - The recorded Mistral/Cohere deprecations are lifecycle warnings, not invented shutdown dates or proof of current account access.
  - The recorded Gemini API/AI Studio tuning path is unsupported. A Vertex offering needs its own model, method, region, account and export checks.
  - The historical checked Bedrock tuple is Claude 3 Haiku in `us-west-2`, with recorded end of life on 2026-09-10. It does not establish availability through the Anthropic API or any other Claude/Bedrock route; unestablished routes remain unknown.
- **Licence and access checks:** assess the selected checkpoint, operation, intended use and framework components. A licence label alone does not establish every requested permission, notice obligation, weight-access grant, data right or technical capability (framework F-01–F-17, F-23–F-24).
- **User-operated reference stack:** compare a selected TRL trainer with PEFT when an adapter is needed, and consider Axolotl or Unsloth for a qualified configuration. These are project proposals, not measured performance winners; PEFT alone is not a standalone SFT/DPO trainer. The pinned Unsloth source has separately scoped Apache core and AGPL Studio **and MoE kernel** components. The exact `2026.10.6` wheel and selected use were not inspected; neither whole-wheel licensing nor compliance follows from the root licence (framework R1–R3, R7).
- **Maintenance:** the framework record retains torchtune's published unmaintained status and the NVIDIA tooling migration. These are maintenance inputs, not evidence that every old runtime fails.
- **Export and managed portability:** require the needed artifact kind and an eligible conversion/import path. Axolotl's audited GGUF guide delegates to a llama.cpp checkout, requires merged LoRA/QLoRA input and rejects prequantized source checkpoints; the separate adapter converter has architecture and tensor-mapping limits. Together's download kinds depend on the job; Fireworks' adapter, exact base, merge and serving are separate steps. A format label or platform-side merge proves neither full-checkpoint delivery nor serving compatibility. Show provider-only and unknown-export outcomes during selection (framework R2, R4–R6; artifact V11).

### Training compute (#31)

- **Memory:** account for the exact model, objective, parameter updates, quantizer, trainer/backend, optimiser, dtypes, sequence/batch shape and execution phase, including sharding, offload, loss and workspace. The 16N/18N state examples apply only to their stated resident tensors; device memories cannot be pooled into an unconditional fit claim. The compute note collects 12 published comparison rows; B12 is a capability claim without measurements. These rows do not establish calibration of the Qwen3-8B worked example or a general fit guarantee.
  - Logits are often the largest swing: for Qwen3-8B at 4,096 tokens, 2.5–7.5 GB per sequence without fused cross-entropy.
- **Time:** use qualified measured throughput only within its exact workload and runtime scope. With N parameters, D dataset tokens and E epochs, the rough 6·N·D·E (full) and ≈4·N·D·E (LoRA, a project estimate) model-FLOPs conventions exclude checkpoint rematerialization when paired with MFU. Executed work including recomputation needs a matching HFU denominator or throughput measurement; published comparison rows do not independently calibrate the selected job. The compute record retains separate objective/phase accounting and uncertainty.
- **Cost:** the [historical priced scenarios](training-compute.md#priced-scenarios) use 10M dataset tokens × 3 epochs. Their displayed 8B rows are about $1–4 for rented-GPU compute and $10–45 for managed training, with different methods and published benchmark conditions; they are compute-only lower bounds, not matched measurements, current quotes or complete job prices. Setup, data loading, evaluation, idle time, minimum billing increments and egress are excluded there. Preserve provider-specific billing units and minimums when constructing an actual estimate.
- **Recurring serving:** the separate historical Azure `gpt-4.1-mini` example is $1.70/hour × 730 hours = $1,241, against $150 for the stated 30M-token training job. The roughly 8× relationship belongs to that example, not all fine-tunes. Keep one-off training and recurring hosting/storage/inference separate; the cost note's 720-hour example uses a different period. Missing rates, capacity, entitlement or overhead remain unknown and unpriced, never zero or a budget pass ([bounded #31 → #39 intake](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/39#issuecomment-6251932295)).

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
  - Keep the adapter and, where the exact method and quantization support it, a merged checkpoint, pinned to the base's full commit SHA. Merging loses PEFT-specific adapter management and does not qualify the resulting architecture, tokenizer, precision or serving/import tuple (artifact V11; framework R2).
  - Merging into the 16-bit base before target quantization is the note's conditional project inference, not a universal PEFT recommendation. A supported merge, any subsequent conversion and serving compatibility require separate checks (artifact A-06/V11).
  - Avoid adding tokens.
- **Evaluation gate for #36:**
  - Safety regression vs the base: 10 adversarial examples took GPT-3.5 Turbo from 1.8% to 88.8% harmfulness.
  - A training-data harm screen.
  - Capability retention.
  - Task gain.

## Rules contributed to #40

**Evidence labels.** The component registers retain their original source dates and the interim #41 policy recorded in the [#75 owner review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75#pullrequestreview-5550616927). Reading primary documentation supports only its stated scope; a passing research assertion or repository test does not reproduce a selected training, export or serving result. The current framework proposal additionally defines exact participants, evidence admission, fixed severity and `on_unknown: review` in its [shared evaluation envelope](training-framework.md#shared-participant-and-evaluation-envelope). Those proposal semantics do not adopt a new frozen rule or grant deployment permission.

The table counts research identities and points to their current evidence boundaries. The original summary's aggregate of 67 source-checked rules is superseded by the revised F-series assertions; it must not be used as a current evidence total.

| Series | Component | Identities | Current record and evidence boundary |
| --- | --- | --- | --- |
| F-01 – F-24 | #30 | 24 | `training-framework-decision/0.2.0` replaces the original assertions. Each row distinguishes scoped source checks, historical leads, project policy and unresolved selected-use facts; no aggregate source-checked count is assigned here |
| K-01 – K-09 | #31 | 9 | `training-compute-decision/0.2.0` supplies the shared participant/configuration/evidence envelope, fixed severity and four outcomes. K-02's headroom remains a project proposal; qualified bounds, missing facts, explicit contradictions, joint support and requested calibration retain distinct outcomes. No aggregate source-checked or measured-result count is assigned here |
| D-01 – D-22 | #32 | 22 | The component register labels 21 source checked; D-20 is leakage policy with #36. Checked source conditions do not establish an actual dataset's rights, privacy or absence of leakage |
| A-01 – A-20 (A-18 split into A-18a, A-18b, A-18c) | #33 | 22 | The component register labels 20 source checked, retaining A-06's inference; A-13 has classic-FAQ scope and A-20 is a proposed evaluation gate with #36 |

There are 77 research rule identities. This count establishes neither executable rule adoption nor independent reproduction; #40 owns adoption and versioned migration. Historical saved results retain their original rule/version/evidence identities.

A-06 is counted as source checked but carries a stated inference: no PEFT document states "merge into the 16-bit base" positively. K-01–K-09 retain the compute record's exact participant, configuration and evidence scopes; K-04 requires joint support for the selected optimizer/dtype/offload configuration, without inferring combinations from separate support lists. The sources behind D-14 (an archived snapshot, because the live pages were not readable) and D-19 (a 2023 Hub snapshot) are limited as well.

A-18a, A-18b and A-18c replace the single A-18, which failed every distributed Apache-2.0 artifact that lacked a NOTICE or change notice. They encode the §4(a) licence copy, §4(b) change notices on modified files and §4(d) NOTICE attributions. §4(d) applies only if the base distribution includes a NOTICE file, and §4(c) is not encoded as a rule. Each rule can return `unknown` when applicability is unresolved, and none infers applicability from `adapter_only` or artifact format.

Contract-change proposals are consolidated in the #40 comment of 2026-10-16:
- `training_framework` method enum values and fields;
- optional `backends` for managed services;
- optional `compute_profile_ref` for managed training;
- Pricebook training meters;
- a training-memory ResourceEstimate metric;
- `training_dataset` and `data_source` provenance fields replacing the governance booleans.

#33 adds: `base_model_revision`, adapter rank / target modules / PEFT variant / `modules_to_save`, `base_quantization`, `added_tokens`, `method`, `evaluation_report_ref`, `signature` and `base_notice_file_present` (needed by A-18c), plus revision-pinned catalog references.

## Outgoing handoffs and recorded dispositions

The table retains the requested boundaries. The bounded #31 → #39 quantity/unit/uncertainty intake has the actual receiving decision below; other portions require their own decisions. An incoming receipt does not accept a reverse-direction request.

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

**#31 → #39: accepted with constraints.** The [actual receiving decision 6251932295](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/39#issuecomment-6251932295), at 15:52:51 UTC on 2026-10-18, accepts quantity, unit and uncertainty inputs at its exact recorded source. It preserves provider/model/method scope, distinct per-1K/per-1M divisors, provider-specific evaluation billing, a minimum charged once, instance-hour versus GPU-hour units, disjoint allocation lifetimes, separate one-off/recurring periods and unpriced unknowns. It does not adopt a meter, validate every historical quote, accept #33's separate serving handoff or supply #42 snapshot acceptance. See the [compute record's bounded dispositions](training-compute.md#bounded-receiving-dispositions--2026-10-18) for the reviewed revisions and checks. The decision is the actual in-session review under delegated project authority, not a statement by an absent named co-assignee.

The [amended #31 → #39 receiving decision 6255117285](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/39#issuecomment-6255117285) separately accepts the revised compute note's quantity, unit, capacity and uncertainty boundaries against the unchanged `cost-estimate.md` blob `6405fd07b1465178c82bcfeab18d13990ad2836e`. It preserves the earlier receipt and its original source identity. It supplies neither a current quote, observed performance, new meter, rights or entitlement, nor completion of #39.

Incoming T2 boundaries have separate receiving-owner receipts: [#9 → #31](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/9#issuecomment-6230482274), [historical #10 → #31](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10#issuecomment-6230482484), and [#11 → #33](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/11#issuecomment-6230482684). The later [actual #10 → #31 decision 6250287107](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10#issuecomment-6250287107) receives the current L40S/RTX 4090/A100 and G6e/P4de subset while retaining H100 SXM/MI300X as note-only. These decisions retain their individual revisions and constraints, including tokenizer/template ownership; they do not accept reverse-direction requests or supply missing catalog records. The two later decisions were read back on 2026-10-18; the earlier receipts retain the prior recorded readback.

Owners are the live GitHub assignees as of 2026-10-16 and are not duplicated elsewhere.

## Blockers on structured artifacts

T2 proposals merged in #75 originally supplied three accelerator records. The [2026-10-18 precision correction](../T2-infrastructure/gpu-compute.md#incomplete-precision-intake-correction-2026-10-18) now keeps H100 SXM and MI300X note-only because their researched precision subsets cannot safely encode the frozen selected-precision semantics. Their hardware facts and historical receipts remain available, but they are no longer current catalog-reference targets. L40S, RTX 4090 and the later A100 80GB proposal remain in intake, alongside the `aws-ec2-g6e-xlarge-us-east-1` and `aws-ec2-p4de-24xlarge-us-east-1` compute profiles, hosting/storage records and `gpu_hour` meter. The [A100/P4de follow-up](../T2-infrastructure/gpu-compute.md#a100-and-p4de-precision-and-profile-follow-up--2026-10-18) retains its separate native-precision evidence and joint-compatibility limits. They are proposals under their own review, not approved catalog data. The two existing profiles are valid `compute_profile_ref` targets; historical rates and training fit still need their own binding and evidence. The meter enum's `gpu_hour` can represent per-GPU-hour billing, such as the Fireworks Dedicated Training API row, once matching catalog references exist; the other managed training rows need separate meter review, and those limits do not exclude all managed training prices from v1. The S3 Standard storage identity was added in #158; its historical P13 rate has not been rebound to that catalog version. The remaining gaps are the records and fields that actually do not exist, listed in [Upstream T2 records](training-compute.md#upstream-t2-records).

| Artifact | Blocked by |
| --- | --- |
| `training_compute` items, training Pricebooks, ResourceEstimates | #31 proposes no `training_compute` item and no Pricebook or ResourceEstimate. Missing current records: `compute_profile` for every priced SKU except `aws-ec2-g6e-xlarge-us-east-1` and `aws-ec2-p4de-24xlarge-us-east-1` (#10), and `accelerator` for H100 SXM and MI300X pending precision scope (#10/#40); RTX 4090 identity is supplied by `nvidia-geforce-rtx-4090` version `2026-10-18` without a profile/rate binding, `hosting_platform` for Google Cloud, Azure, Lambda and CoreWeave (#9). Unresolved fields and meters: peak dense TFLOP/s per accelerator, training-token, job-minimum, training-hour and model-storage meters, optional `compute_profile_ref` for managed services, a training-memory ResourceEstimate metric (#40), and whether a multi-GPU instance-hour price maps to `gpu_hour` per GPU or per instance (#39) |
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
| Calibrate the documented GRPO/distillation phase and allocation models for a concrete workload; calibrate the Qwen3-8B example with a dry run | #31 · @appletechie |
| vLLM/SGLang LoRA on GGUF bases; SGLang on quantised bases; TGI and llama.cpp LoRA limits; Vertex PEFT_ADAPTER output form; Bedrock import of adapters; Fireworks retention; tuned-Gemini lifecycle | #33 · @appletechie |
| Priority: P2 remains appropriate for all T5 issues; no product decision makes fine-tuning part of the first release | #29 · @appletechie |

## Secondary inputs

The workstream owner supplied two internal documents, used as leads and re-checked against primary sources; neither is committed:
- a 165-row free training-source audit;
- a local training-methods guide.

Where they disagreed with primary sources, the notes say so. For example, the guide's 8-bit Adam memory figure is refuted (#31).

## Workstream done when

- [ ] #30–#33 closed with merged decision records meeting their acceptance criteria (the four records are merged; research completion and remaining handoffs are recorded separately in each component issue)
- [ ] Handoffs above confirmed by the consuming owners
- [ ] This summary merged, with rules contributed to #40 and open questions current
