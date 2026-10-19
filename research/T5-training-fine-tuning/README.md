# T5: Training & Fine-Tuning

Issue: #29 · Contract: 1.0.0 · Kinds: `training_framework`, `training_compute`, `training_dataset`, `fine_tuned_model`
Status: summary of the merged component records · Last researched: 2026-10-16

This is the workstream summary for T5. It consolidates the four component decision records and does not replace them. The records are reviewed research; handoff acceptance is limited to the actual receiving decisions linked below.

**Record reconciliation, 2026-10-18:** the framework summary follows the accepted #375/#380 scope corrections and `training-framework-decision/0.2.0`; the compute summary follows `training-compute-decision/0.2.0`, including its scoped accounting, K-series envelope and amended cost intake. Cost and artifact statements retain the component notes' stated conditions. This is a consistency update against the cited repository records, not a new vendor-source retrieval, training/export experiment or blanket acceptance of the workstream. Original source dates, versions and evidence grades remain in the component records.

The four component records are merged into `main` (#68, #76, #77, #84). Merging this summary does not complete the T5 workstream or its component issues, confirm any handoff, or close any issue. Acceptance stays with the issue owners.

The [actual #30 reconciliation](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/30#issuecomment-6253889603) records its research completion at 19:02:53 UTC on 2026-10-18, after the scoped #380 correction. The [#31 completion receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/31#issuecomment-6255596160) and [#33 ten-criterion completion receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/33#issuecomment-6258532242) record their separately reviewed deliveries and actual post-main checks. The [#32 final coordinating determination](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/32#issuecomment-6260236369) completes its separately reviewed ten-criterion Dataset acceptance. These links retain their original source, deciding engineer and reviewer attribution; they do not imply a new personal approval by an absent assignee.

**Artifact summary reconciliation, 2026-10-19:** the artifact section below now follows the exact [#449 delivered record](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/201aa8ea927fa35c4794f939f99f18e39dfdafb4/research/T5-training-fine-tuning/fine-tuned-model.md), including the #418/#424 source qualifications and `fine-tuned-artifact-rule-interpretation/0.3.0`. This is a summary of those reviewed decisions, not a new provider, engine, legal-source or measured-quality campaign. Their original access dates, release pins, evidence grades, research-only representations and actual receiving limits remain in the component record.

**Dataset summary reconciliation, 2026-10-19:** [#456's delivered Dataset record](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/7d6a3b81abc4fcebafecd34e54c49c0e78432277/research/T5-training-fine-tuning/training-dataset.md) supplies the eight-field evidence map and the twenty remaining D concerns in shared format, alongside the delivered D-01/D-14 interpretation 0.2. It withdraws the unavailable private shortlist/recheck findings and unqualified later-appellate identity/status from operative evidence. Their original statements remain in immutable source history; no replacement audit, primary-source check, access date, evidence grade or rights conclusion is introduced by this summary. Component and parent completion remain the actual issue decisions, separate from the merged representation.

**Parent handoff reconciliation, 2026-10-19 04:50 UTC:** the actual [delegated aggregate decision6259851201](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/29#issuecomment-6259851201) accepts the two boundaries listed in #29 against the current source and six original directional decisions. T1 supplies the scoped model and managed-service facts; T5 owns training and artifact definition; T2 owns selected hardware/engine serving; T6 owns selected evaluation thresholds and actual evidence. Each original reviewer, source, direction and limit stays attached to its own receipt. The parent's second criterion is now checked; its summary criterion was already accepted through [#454](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/454). Fresh native readback retains #30/#31/#33 closed/completed and #32 open/reopened, so the first criterion and #29 remain open. The checked parent handoff criterion covers those two literal #29 boundaries; it does not accept every broader request in the outgoing table, whose individual scopes and outstanding decisions remain as recorded. The pending Dataset child-completion assessment is separate from this summary correction.

**Current child-completion reconciliation, 2026-10-19 05:25 UTC:** fresh native readback confirms all four children #30/#31/#32/#33 closed/completed, so the first research-completion criterion below is now met. The preceding 04:50 paragraph retains its historical cutoff. The [parent closeout](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/29#issuecomment-6260338332) separately reconciles all three original criteria against the actual component, handoff and summary decisions. This status update supplies no new source-use permission, training or evaluation result, executable rule adoption, or implementation acceptance.

| Component | Issue | Decision record | PR | Structured proposals |
| --- | --- | --- | --- | --- |
| Training Framework | #30 | [training-framework.md](training-framework.md) | #68 (merged) | 4 `training_framework` proposals ([`catalog/proposals/training_framework-*.json`](../../catalog/proposals/)), all provenance `unverified` |
| Training Compute | #31 | [training-compute.md](training-compute.md) | #77 (merged) | none (see blockers) |
| Training Dataset | #32 | [training-dataset.md](training-dataset.md) | #76, #451, #456 (merged) | none; future source-specific intake remains separate |
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

- **Rights and privacy checklist (C1–C15):** its dated legal, regulatory and provider inputs accompany the exact source, included subset, actor, use, jurisdiction and period. The actual scoped assessment supplies the answer; licence names, uploader metadata, governance Booleans and record availability do not establish permission, privacy approval or anonymity. Training and retrieval keep separate purpose-specific dispositions with #13.
- **Preparation procedure:**
  1. Freeze the eval set (with #36).
  2. Validate the format.
  3. Scan for PII.
  4. Deduplicate.
  5. Check leakage in layers: exact, 13-gram, MinHash, then embedding plus LLM judge.
  6. Split by source.
  7. Record lineage (Croissant 1.1 / RAI).
- **Eight comparison fields:** source, rights basis, format, split, PII handling, lineage record, dedup method and leakage check have explicit types, units and evidence requirements in the [delivered field map](training-dataset.md#eight-field-evidence-map-and-d-series-companion-03). Bind the actual selected dataset and every included upstream source/revision, preparation edge, participant, intended operation and period. The companion supplies research evidence beside the frozen fields; it does not add JSON members or turn an ID-only reference into complete lineage.
- **Leakage and trainer interfaces:** #36 owns the evaluation freeze, hashes and canary; T5 owns the ordered check and its methods, counts and set hashes. D-20 concerns availability of that eligible exact record, which can contain an adverse finding while E-R44 independently fails with fixed error severity. D-22 uses the actual trainer/loader/version, objective, tokenizer/template and mask/packing contract; a missing row in the finite comparison is unresolved support evidence. Neither a held-out Boolean nor a method list proves clean data, measured quality or permission.
- **Historical shortlist:** the unavailable S1/S2 audit and reported recheck counts, distributions and candidate-specific licence/access conclusions are [withdrawn from operative findings](training-dataset.md#historical-shortlist-excluded-from-operative-evidence). The original report remains in immutable c2b/23b history. A future actual source proposal needs its own primary evidence, exact source/version/use and responsible assessment; this summary supplies no replacement audit.

### Fine-tuned model (#33)

- **Artifact identity and serving mode:** identify the actual adapter, full/merged or converted weights, or provider-held result; keep exact artifact/base revisions, training method, tokenizer/template, saved tensors and transformation lineage. API / managed / self-hosted mode follows the actual operator and capacity arrangement, not the training channel, billing or downloadable packaging. An adapter inherits its served base's mode ([artifact definitions and fields](fine-tuned-model.md#comparison-fields)).
- **Selected release and route evidence:**
  - The exact inspected Ollama sources retain adapter conversion at v0.34.0 and reject adapter requests/GGUF adapter inputs at v0.34.1 and v0.40.5. This records those releases and the removal boundary, without asserting every intervening or future release (artifact V7-R).
  - TGI's v3.3.7 source documents maintenance mode and startup LoRA loading; the repository API was observed archived on the recorded 2026-10-18 check. This is maintenance and source evidence, not a new serving result (V4-R).
  - Together and Fireworks requirements apply to the actual job output, base, adapter and selected deployment. Export form, access, merge eligibility, capacity and destination support remain separate; documentation does not establish a particular account's entitlement or a successful relocation (V12–V13 and the dated provider clarification).
  - Apache-2.0 notice duties are conditional, not blanket: §4(a) licence copy, §4(b) change notices on modified files, and §4(d) NOTICE attributions only if the base distribution includes a NOTICE file (A-18a to A-18c).
- **Recommendation:**
  - Keep the adapter and, where the exact method and quantization support it, a merged checkpoint, pinned to the base's full commit SHA. Merging loses PEFT-specific adapter management and does not qualify the resulting architecture, tokenizer, precision or serving/import tuple (artifact V11; framework R2).
  - Merging into the 16-bit base before target quantization is the note's conditional project inference, not a universal PEFT recommendation. A supported merge, any subsequent conversion and serving compatibility require separate checks (artifact A-06/V11).
  - Record actual token/vocabulary changes, saved modules and tensor layout, then apply the selected converter or loader's evidenced operands. The vLLM saved-module, SGLang effective-vocabulary, llama.cpp converter-tensor and Fireworks target/live-merge conditions are different. A generic `added_tokens` flag is not a cross-engine verdict; any alternate merge/export and resulting serving tuple need their own qualification (V1-R/V3-R/V6-R/V13-R; A-03).
- **Quality evidence and evaluation gate for #36:**
  - Keep compatibility findings in the frozen EvaluationReport distinct from measured QualityEvaluationRun evidence. The proposed measured-quality locator needs the actual artifact/served-configuration association, evaluator/suite/dataset revisions, observations, selected thresholds and applicable same-suite base comparison; a URI or status alone supplies none of those facts ([evidence roles](fine-tuned-model.md#compatibility-and-measured-quality-evidence)).
  - The historical Q1 example used GPT-3.5-Turbo-0613, five epochs on ten Anthropic red-team demonstrations, and 330 policy-oriented prompts across eleven categories. Its GPT-4 score-5 rate changed from 1.8% to 88.8%, with the base/tuned comparison using the same system prompt. This motivates the proposed regression gate; it neither measures the selected artifact nor predicts current-service behavior ([artifact Q1 and rationale](fine-tuned-model.md#recommendation-and-rationale)).
  - Preserve separate pre-training data and post-training model assessments, capability retention, target-task gain and exact artifact/provenance conditions. #36 retains G1/G2/G4/G5/G9, suite/threshold selection and change-triggered reevaluation. Provider screens and a compatibility pass do not establish those measured gates or deployment readiness.

## Rules contributed to #40

**Evidence labels.** The component registers retain their original source dates and the historical convention in the [#75 owner review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75#pullrequestreview-5550616927); interpret their labels under the [accepted #41 policy](../T0-configuration/catalog-data-sources.md#mapping-evidence-labels-to-frozen-v1). Reading primary documentation supports only its stated scope; a passing research assertion or repository test does not reproduce a selected training, export or serving result. The current framework proposal additionally defines exact participants, evidence admission, fixed severity and `on_unknown: review` in its [shared evaluation envelope](training-framework.md#shared-participant-and-evaluation-envelope). Those proposal semantics do not adopt a new frozen rule or grant deployment permission.

The table counts research identities and points to their current evidence boundaries. The original summary's aggregate of 67 source-checked rules is superseded by the revised F-series assertions; it must not be used as a current evidence total.

| Series | Component | Identities | Current record and evidence boundary |
| --- | --- | --- | --- |
| F-01 – F-24 | #30 | 24 | `training-framework-decision/0.2.0` replaces the original assertions. Each row distinguishes scoped source checks, historical leads, project policy and unresolved selected-use facts; no aggregate source-checked count is assigned here |
| K-01 – K-09 | #31 | 9 | `training-compute-decision/0.2.0` supplies the shared participant/configuration/evidence envelope, fixed severity and four outcomes. K-02's headroom remains a project proposal; qualified bounds, missing facts, explicit contradictions, joint support and requested calibration retain distinct outcomes. No aggregate source-checked or measured-result count is assigned here |
| D-01 – D-22 | #32 | 22 | Delivered D-01/D-14 interpretation 0.2 and the [0.3 field/profile companion](training-dataset.md#eight-field-evidence-map-and-d-series-companion-03) cover all twenty remaining concerns: six advisories, six evidence-status concerns and eight constraints. Each retains exact participant/evidence scope, fixed severity, explicit unknown handling and synthetic examples. Evidence availability can retain an adverse result; D-20 does not clear E-R44 or the separate frozen governance error/unknown-block predicate. No aggregate source-checked or permission count is assigned here |
| A-01 – A-20 (A-18 split into A-18a, A-18b, A-18c) | #33 | 22 | The historical register and its labels remain intact. The five corrected 0.2.0 interpretations plus [0.3.0's remaining seventeen concerns](fine-tuned-model.md#complete-a-series-proposal-mapping--research-interpretation-030) provide the full shared proposal format: eleven additional constraints and six advisories, with exact participant/evidence boundaries and fixed severity. Synthetic examples and project inferences remain labeled; this is no executable adoption or new measured result |

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

#33 adds: `base_model_revision`, adapter rank / target modules / PEFT variant / `modules_to_save`, `base_quantization`, `added_tokens`, actual training `method`, `evaluation_report_ref` for compatibility findings, a separate exact artifact/configuration association for measured QualityEvaluationRun evidence, `signature` and `base_notice_file_present` (needed by A-18c), plus revision-pinned catalog references. These remain note-only/versioned proposals where frozen v1 has no field; no richer association or measured result is invented.

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
| Selected fine-tune/base-snapshot shutdown and the Foundry classic-FAQ idle-deployment condition, with the model retained | #33 | #37 | @PUSHINGSQUARES |
| User attestations (EU market, revenue, MAU, residency, lawful basis) | #30, #32 | #2, #3 | @tynamite |
| Rule format and contract changes; "competing model" policy | all | #40 | @tynamite |
| Evidence grading (checked vs verified), price freshness | all | #41 | @tynamite |

**#31 → #39: accepted with constraints.** The [actual receiving decision 6251932295](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/39#issuecomment-6251932295), at 15:52:51 UTC on 2026-10-18, accepts quantity, unit and uncertainty inputs at its exact recorded source. It preserves provider/model/method scope, distinct per-1K/per-1M divisors, provider-specific evaluation billing, a minimum charged once, instance-hour versus GPU-hour units, disjoint allocation lifetimes, separate one-off/recurring periods and unpriced unknowns. It does not adopt a meter, validate every historical quote, accept #33's separate serving handoff or supply #42 snapshot acceptance. See the [compute record's bounded dispositions](training-compute.md#bounded-receiving-dispositions--2026-10-18) for the reviewed revisions and checks. The decision is the actual in-session review under delegated project authority, not a statement by an absent named co-assignee.

The [amended #31 → #39 receiving decision 6255117285](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/39#issuecomment-6255117285) separately accepts the revised compute note's quantity, unit, capacity and uncertainty boundaries against the unchanged `cost-estimate.md` blob `6405fd07b1465178c82bcfeab18d13990ad2836e`. It preserves the earlier receipt and its original source identity. It supplies neither a current quote, observed performance, new meter, rights or entitlement, nor completion of #39.

**Dataset received interfaces:** the [six-row dated reconciliation](training-dataset.md#received-interface-reconciliation--2026-10-19) records #32 → #36, #32 → #33, #30 → #32, #36 → #32, #40 → #32 and #13 → #32 with their actual reviewers, source revisions and dates. The directions remain distinct: #30 supplies the trainer contract, #36 supplies the frozen-set requirements, #40 supplies representation and #32's responsible assessor supplies the scoped answer, while #13 shares source identity without inherited training permission. The [current corrected-source Artifact intake5566913920](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/456#pullrequestreview-5566913920) accepts the unchanged field/profile interface at de61/74d; it does not enlarge the six historical receipts or certify an actual dataset, source right, evaluation result or executable successor.

**#33 → #10/#11/#36/#37: actual scoped receipts.** The [GPU/Compute intake6255801883](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10#issuecomment-6255801883) receives exact tensor/storage/configuration inputs; the [Engine intake6255802511](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/11#issuecomment-6255802511) retains its three-candidate joint-support scope. [PUSHINGSQUARES's historical A-20 → G5 decision6232138142](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/121#issuecomment-6232138142) is separate from the [reciprocal #36 → #33 requirements6255762046](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/33#issuecomment-6255762046). The [two expressly distinguished Deployment directions6255762785](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/37#issuecomment-6255762785) preserve exact loaded identity, applicable evaluation and rehearsed rollback. The classic FAQ's more-than-15-day/no-named-calls condition deletes the deployment while retaining the model; it is not a universal Foundry policy or an observed deletion. Each receipt keeps its original reviewer, source, direction and constraints; the later #449 completion review does not retroactively repin it. These inputs supply no fit result, executed quality gate, account/rights grant, broader engine inventory or new serving-cost decision.

Incoming T2 boundaries have separate receiving-owner receipts: [#9 → #31](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/9#issuecomment-6230482274), [historical #10 → #31](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10#issuecomment-6230482484), and [#11 → #33](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/11#issuecomment-6230482684). The later [actual #10 → #31 decision 6250287107](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10#issuecomment-6250287107) receives the current L40S/RTX 4090/A100 and G6e/P4de subset while retaining H100 SXM/MI300X as note-only. These decisions retain their individual revisions and constraints, including tokenizer/template ownership; they do not accept reverse-direction requests or supply missing catalog records. The two later decisions were read back on 2026-10-18; the earlier receipts retain the prior recorded readback.

Owners are the live GitHub assignees as of 2026-10-16 and are not duplicated elsewhere.

## Blockers on structured artifacts

T2 proposals merged in #75 originally supplied three accelerator records. The [2026-10-18 precision correction](../T2-infrastructure/gpu-compute.md#incomplete-precision-intake-correction-2026-10-18) now keeps H100 SXM and MI300X note-only because their researched precision subsets cannot safely encode the frozen selected-precision semantics. Their hardware facts and historical receipts remain available, but they are no longer current catalog-reference targets. L40S, RTX 4090 and the later A100 80GB proposal remain in intake, alongside the `aws-ec2-g6e-xlarge-us-east-1` and `aws-ec2-p4de-24xlarge-us-east-1` compute profiles, hosting/storage records and `gpu_hour` meter. The [A100/P4de follow-up](../T2-infrastructure/gpu-compute.md#a100-and-p4de-precision-and-profile-follow-up--2026-10-18) retains its separate native-precision evidence and joint-compatibility limits. They are proposals under their own review, not approved catalog data. The two existing profiles are valid `compute_profile_ref` targets; historical rates and training fit still need their own binding and evidence. The meter enum's `gpu_hour` can represent per-GPU-hour billing, such as the Fireworks Dedicated Training API row, once matching catalog references exist; the other managed training rows need separate meter review, and those limits do not exclude all managed training prices from v1. The S3 Standard storage identity was added in #158; its historical P13 rate has not been rebound to that catalog version. The remaining gaps are the records and fields that actually do not exist, listed in [Upstream T2 records](training-compute.md#upstream-t2-records).

| Artifact | Blocked by |
| --- | --- |
| `training_compute` items, training Pricebooks, ResourceEstimates | #31 proposes no `training_compute` item and no Pricebook or ResourceEstimate. Missing current records: `compute_profile` for every priced SKU except `aws-ec2-g6e-xlarge-us-east-1` and `aws-ec2-p4de-24xlarge-us-east-1` (#10), and `accelerator` for H100 SXM and MI300X pending precision scope (#10/#40); RTX 4090 identity is supplied by `nvidia-geforce-rtx-4090` version `2026-10-18` without a profile/rate binding, `hosting_platform` for Google Cloud, Azure, Lambda and CoreWeave (#9). Unresolved fields and meters: peak dense TFLOP/s per accelerator, training-token, job-minimum, training-hour and model-storage meters, optional `compute_profile_ref` for managed services, a training-memory ResourceEstimate metric (#40), and whether a multi-GPU instance-hour price maps to `gpu_hour` per GPU or per instance (#39) |
| Future source-specific `data_source` proposals | The earlier shortlist/recheck is archival, not an admitted candidate pool. Each future proposal needs its own primary evidence and exact source/version/use assessment. The shared #13 identity and #40 representation/assessor boundaries are already received; richer licence, terms and opt-out evidence still has no frozen `spec_data_source` fields and needs its own versioned adoption |
| Managed `training_framework` items | `backends` required but not user-visible for managed services (#40) |
| `fine_tuned_model` items | User-specific; references require `model` and `training_dataset` items, and A-18c needs the proposed `base_notice_file_present` fact (#40, #6) |

None of these is a native GitHub blocker; they are information dependencies under `docs/DEPENDENCIES.md`.

## Open questions

| Question | Owner |
| --- | --- |
| What counts as a "competing model" under provider output terms (F-17, D-12–D-14) | #40 · @tynamite |
| Establish any later appellate case identity and disposition following the appeal allowed by the dated R7 judgment before relying on it; qualify the Bartz appeal-notice scope from primary evidence | #32 · @appletechie |
| Mistral Forge licensing and weight export (not public) | #30 · @appletechie |
| ONNX export for any training framework | #30 · @appletechie |
| Calibrate the documented GRPO/distillation phase and allocation models for a concrete workload; calibrate the Qwen3-8B example with a dry run | #31 · @appletechie |
| vLLM/SGLang LoRA on GGUF bases; SGLang on quantised bases; TGI and llama.cpp LoRA limits; Vertex PEFT_ADAPTER output form; Bedrock import of adapters; Fireworks retention; tuned-Gemini lifecycle | #33 · @appletechie |
| Priority: P2 remains appropriate for all T5 issues; no product decision makes fine-tuning part of the first release | #29 · @appletechie |

## Secondary inputs

The historical private training-source compilation and reported Hub recheck are preserved in the Dataset record's immutable source links. Their underlying audit and claim-level records are unavailable here, so the counts, discrepancies, distribution and source-specific conclusions are withdrawn from operative evidence. No current primary-source check, grade or eligible candidate is inferred from those archived statements.

The separate local training-methods guide remains a historical lead in #31. Its disagreements, including the guide's 8-bit Adam memory figure, retain the compute note's actual source and accounting qualification. This Dataset correction neither supplies that private document nor broadens its original check.

## Workstream done when

- [x] #30–#33 closed with merged decision records meeting their acceptance criteria (the four records are merged; research completion and remaining handoffs are recorded separately in each component issue)
- [x] Handoffs above confirmed by the consuming owners
- [x] This summary merged, with rules contributed to #40 and open questions current
