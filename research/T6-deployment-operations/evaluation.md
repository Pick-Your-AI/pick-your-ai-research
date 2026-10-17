# T6: Evaluation

Issue: #36 · Contract: 1.0.0 · Kinds: `evaluation_suite`
Status: draft · Last researched: 2026-10-17

Evidence labels follow the interim #41 policy adopted in the [#75 owner review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75#pullrequestreview-5550616927) §3. **Source checked** means the cited primary text was read on its access date and supports the claim. **Verified** means independently reproduced; nothing in this note is verified. No evaluation was run for this note, and no score, latency or cost figure below is a measurement by this project.

## User decision

How will the user know whether the build meets its quality, safety, latency and cost targets?

The builder needs three answers per build:
1. **Which evaluations apply**, given the workload (#2) and the selected components (model #6, RAG #16, agent #25, fine-tune #33, guardrails #35).
2. **Which cited benchmark comparisons are comparable enough to display** in the catalog.
3. **Which results must exist, and pass, before deployment** (#37).

Deployment modes covered:
- **API:** the system under test is a provider endpoint. Open-source harnesses reach it through API backends with limits (EVAL-01). Provider-run evaluation services exist (E17, E18).
- **Managed:** a dedicated provider endpoint is evaluated like an API endpoint. Provider evaluation services cover their own hosted and imported models (E17, E18).
- **Self-hosted:** every open-source candidate below runs locally against local weights or a local OpenAI-compatible server.

Out of scope: running evaluations. This note defines methodology, fields, gates and rules only.

## Evaluation taxonomy by workload

The workload axes come from #2's draft in [PR #81](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/81) (head `e2bcc35`, unmerged). The v1 `workload_type` enum is mapped as well, because it is the current contract.

Evaluation types used below:

| Type | Measures | Scoring | Evidence class |
| --- | --- | --- | --- |
| `task_quality` | Task success on a held-out, labelled set drawn from the user's distribution | Deterministic where possible (exact match, F1, execution tests) | Measured run |
| `structured_output` | JSON / JSON-schema validity rate | Deterministic parser / validator | Measured run |
| `retrieval` | Retrieval relevance and recall | Labelled relevance, or LLM-judged context precision / recall (E09) | Measured run |
| `grounding` | Faithfulness of the answer to retrieved context; answer relevance | LLM-judged (E09, E10) | Measured run, judge recorded |
| `agent_task` | End-state task completion, tool-call correctness, reliability over repeated trials (pass^k) | End-state comparison (E14); tool-call accuracy (E09) | Measured run, k recorded |
| `safety` | Harmful-response rate by hazard category; attack success rate under red teaming | Evaluator models (E07, E08) | Measured run, evaluator recorded |
| `capability_retention` | General benchmark scores before and after a change | Harness tasks (E01) | Paired runs |
| `performance` | TTFT, TPOT / ITL, end-to-end latency percentiles, throughput, failure rate | Load generator under a stated arrival process (E16) | `service_level` measurement (W-R7) |
| `cost` | Cost per request or per completed task | Measured usage × dated Pricebook rates | Estimate owned by #39 |

### By task (#81 Axis 1)

| Task | Required types | Baseline | Notes |
| --- | --- | --- | --- |
| `extraction_classification` | `task_quality` (exact match / F1 per field or label), `structured_output` when `output_format` ≠ `free` | Current system, or the unmodified base model | Deterministic scoring; no judge needed |
| `retrieval_ranking` | `retrieval` on labelled queries | Keyword-only retrieval, or the previous index | Embedding-only builds have no generation to judge |
| `code` | `task_quality` by execution (unit tests; SQL execution equivalence, E09) | Previous model or release | Needs a sandbox (Inspect sandboxing, E11) |
| `generation_transformation` | `task_quality` with a rubric; reference metrics (ROUGE, chrF; E09) only as weak signals | Previous model or release | Usually LLM-judged; judge rules apply (EVAL-06) |
| `other` | Owner-defined from `task_description` | — | No default suite |

### By capability need and interaction pattern (#81 Axes 3 and 5)

| Workload input | Adds | Notes |
| --- | --- | --- |
| `knowledge` ≠ `none` (RAG) | `retrieval` + `grounding` (RAG triad: context relevance, groundedness, answer relevance; E10) | Permission compliance (no answer from documents the user cannot read) is a test case owned with #13 / #16; no suite checked here measures it |
| `actions` = `read_only` | `agent_task` (tool selection and arguments) | — |
| `actions` = `write` | `agent_task` with end-state checks and pass^k, plus side-effect and approval tests with #35 | τ-bench reports pass^8 < 25% in its retail domain for its tested agents (E14, vendor-of-benchmark measurement, 2024 models); reliability is not implied by single-trial success |
| `customisation` = `fine_tune` | The fine-tune gate below | Absorbs #33's handoff |
| `interactive` | `performance`: TTFT and TPOT / ITL at a stated percentile and concurrency | Targets from `latency_targets` (#81) |
| `background` | `performance`: end-to-end latency percentile | — |
| `batch` | `performance`: throughput and completion window | — |
| Any user-facing generation | `safety` | Locale coverage limits apply (EVAL-11) |
| Any build with a budget | `cost` per completed task | #39 prices; #36 supplies the usage measurement definition |

### v1 `workload_type` mapping

| v1 value | Default evaluation types |
| --- | --- |
| `chat` | `task_quality`, `safety`, `performance` (interactive) |
| `completion` | `task_quality`, `performance` |
| `rag` | `retrieval`, `grounding`, `task_quality`, `safety` |
| `agentic` | `agent_task`, `safety`, `cost` per completed task |
| `embedding` | `retrieval` |
| `fine_tuning` | Fine-tune gate (`safety` regression, `capability_retention`, `task_quality` gain) |
| `batch` | `task_quality`, `performance` (throughput) |
| `multimodal` | `task_quality` on the modality pair; harness support must be checked per suite (lm-eval multimodal support is labelled a prototype, E02) |

A model leaderboard score never satisfies `task_quality` for a build. It can only inform candidate selection.

## Candidate options

All rows are source checked unless stated. "What it measures" paraphrases the publisher.

| Candidate | Version (date) / licence | What it measures | Modes | Limits | Evidence |
| --- | --- | --- | --- | --- | --- |
| EleutherAI lm-evaluation-harness | 0.4.13 (2026-08-31) / MIT | Over 60 academic benchmarks with hundreds of subtasks; versioned task configs; optional 13-gram decontamination | Self-hosted (HF, vLLM, SGLang, llama.cpp, GGUF); API (completions, chat completions, Anthropic, LiteLLM) | Chat-completion backends support `generate_until` only, with no logprobs, so loglikelihood / multiple-choice tasks cannot run on chat-only APIs (EVAL-01). The README says vLLM output "occasionally differs" from Hugging Face, which it treats as the reference | E01–E04 |
| Stanford CRFM HELM | 0.5.16 (2026-04-30) / Apache-2.0 | Multi-metric scenarios: accuracy, calibration, robustness, fairness, bias, toxicity, efficiency (paper); standardized datasets (e.g. MMLU-Pro, GPQA, IFEval, WildBench) | API (many providers) and local | **Maintenance mode since 2026-06-01**: no new features or leaderboard evaluations; scenarios relying on external APIs "may break" (EVAL-14) | E05, E06 |
| HarmBench (Center for AI Safety) | No releases; repository last pushed 2024-08-16 / MIT | Automated red teaming and robust refusal: 18 attack methods × 33 target LLMs and defenses in the paper; three released classifier models | Self-hosted (SLURM / local); API targets | Classifiers are Llama-2-13B / Mistral-7B fine-tunes; repository inactive since 2024 | E07 |
| MLCommons AILuminate | Safety v1.0 (README); repository description says v1.1 / data CC BY 4.0, repository Apache-2.0 | Safety of general chat systems across 12 hazard categories; Jailbreak benchmark (text and text+image); agentic workstream announced | Public demo set runs anywhere; official practice set and evaluator are for MLCommons members | Demo: 1,200 prompts (10% of the 12,000 public practice prompts). 12,000 benchmark prompts are private. Locales en_US, fr_FR, zh_CN, hi_IN. The official ensemble evaluator is not public, so a self-run score is not an AILuminate grade | E08 |
| Ragas | 0.4.3 (2026-01-13) / Apache-2.0 | RAG: context precision / recall, faithfulness, response relevancy, noise sensitivity; agents: tool-call accuracy / F1, agent goal accuracy; SQL execution; reference metrics | Library; any model via adapters | Most metrics are LLM-judged; the paper's premise is reference-free evaluation, so judge choice affects scores (EVAL-06). Repository moved to `vibrantlabsai/ragas` | E09 |
| TruLens | 2.15.0 (2026-10-05) / MIT | RAG triad (context relevance, groundedness, answer relevance); tracing; runtime evaluation | Offline and online (tracing) | LLM-judged feedback functions; the docs' "verified to be hallucination free" holds only up to judge accuracy and knowledge-base accuracy (vendor claim) | E10 |
| UK AISI Inspect | 0.3.281 (2026-10-15) / MIT | Framework with 200+ pre-built evaluations; agents, MCP and built-in tools; sandboxed execution (Docker, Kubernetes, Modal, others) | API and local models | Framework, not a fixed suite: metrics depend on the task chosen | E11 |
| promptfoo | 0.124.1 (2026-10-08, npm) / MIT | Assertion-based prompt / model comparison, red teaming, CI integration | Local CLI; API and local providers | Publisher description only; red-team plugins not assessed here | E12 |
| DeepEval (Confident AI) | 4.3.1 (2026-10-16) / Apache-2.0 | pytest-style LLM unit tests; G-Eval, task completion, tool correctness and other judge metrics | Local; any judge model | Publisher description only; judge-dependent | E13 |
| OpenAI Evals | PyPI 3.0.1.post1 (2024-05-01) / MIT (LICENSE.md) | Eval registry and templates, including model-graded YAML evals | API | No PyPI release since 2024; README says custom-code evals are not being accepted. Not recommended as a gate dependency | E13 |
| τ-bench (Sierra) | arXiv 2406.12045 | Tool-agent-user conversations; end-state database comparison; pass^k reliability | API | Simulated user is an LLM; domains are retail and airline | E14 |
| Amazon Bedrock evaluations | Docs, unversioned | Programmatic model evaluation (custom or built-in datasets), human evaluation, judge-model evaluation, RAG evaluation of knowledge bases including external sources | API / managed (AWS) | Provider service; billing and judge models not assessed here | E17 |
| Vertex AI Gen AI evaluation; Microsoft Foundry fine-tuning safety evaluation | Docs (via #33 Q7, Q3) | Vertex: model evaluation service. Foundry: fails fine-tune jobs on harmful training data and blocks deployment of unsafe fine-tunes at fixed thresholds | API / managed | Not re-fetched here; see #33 | E18 |
| vLLM `bench serve` | Docs (latest, unversioned) | TTFT, TPOT, ITL mean / median / P99; request and token throughput; Poisson or Gamma arrivals | Self-hosted; any OpenAI-compatible endpoint | Default `--request-rate` is `inf` (all requests at once). Repeating runs on one server can reuse the prefix cache and inflate throughput | E16 |

Not assessed in this pass (no primary source read): MTEB for embeddings, SWE-bench, over-refusal suites, multimodal safety beyond AILuminate's Jailbreak description, and agent-framework-specific evaluators (#25).

## Benchmark reproducibility criteria

A cited benchmark figure may be displayed as **comparable** only when its full tuple is recorded and every element is pinned. This adopts [PR #83](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/83)'s convention C1 (pending owner review) and its 15-field checklist, itself taken from PR #74's unmerged `prompts/T6.md`.

| # | Element | Requirement | Why (evidence) |
| --- | --- | --- | --- |
| R1 | Evaluation identifier | Suite name and version, or commit | — |
| R2 | Task / dataset and version | Task config version (lm-eval `version`), dataset revision or content-lock hash | lm-eval bumps task versions on breaking changes; one fix "led to underestimated performance" before v1.0 (E03) |
| R3 | Model and version | Snapshot or full revision hash; never a marketing name | #83: every Harness Bench website claim failed this |
| R4 | Provider or runtime | Provider route, or engine and engine version | vLLM vs HF output differences (E02) |
| R5 | Inference settings | Precision / quantization, context limit, chat template | — |
| R6 | Hardware or hosting | Device and count for self-hosted; region for API where relevant | — |
| R7 | Prompt and harness version | Harness version and prompt / few-shot format | Harness effects are the open question in #62 (E20) |
| R8 | Sampling | Temperature, seed, k runs per item | One run per configuration prevents separating run variance (E20) |
| R9 | Concurrency and load | Concurrency, arrival process | Throughput rises with concurrency; default `inf` request rate (E16) |
| R10 | Metric definitions | Exact metric, aggregation, percentile | Mean score and full-credit rate can rank differently (E20) |
| R11 | Measurement method | Budgets, timeouts, turn limits, cache state | Prefix-cache reuse inflates throughput (E16) |
| R12 | Uncertainty | Standard error or interval with the dependence model stated | E20 (B4 clustering, B5 run variance) |
| R13 | Date of measurement | Run date, not only publication date | Current-state facts are "as of" (#75 §3) |
| R14 | Source | Primary URL, evidence grade | — |
| R15 | Known limitations | Contamination status, judge identity, excluded items | Below |

Additional conditions:
- **One factor.** Two figures may be compared only if exactly one tuple element differs (#83 G2). Otherwise the comparison is `unknown`, not a ranking.
- **Contamination.** Record a contamination status: checked (method and hit counts, using #32's layered method: exact hash, 13-gram, MinHash, embedding + judge; E04, E23), not checked, or known exposed (for example, benchmark answers publicly readable, as #83 found for Harness Bench). No method proves absence of leakage (E23). Public benchmarks are never the only `task_quality` evidence for a gate.
- **Judge models.** LLM judges show position, verbosity and self-enhancement biases (E15). A judged metric records judge model and version, prompt, and whether the judge equals the system under test. Harness Bench's default judge is the evaluated model (E20). Judged metrics require a human-agreement check on a sample before they gate (owner threshold).
- **Vendor vs independent.** A publisher's own result is a vendor claim even when the method is published. "Independent measurement" needs a third party with stated conditions.
- **Statistical sufficiency.** No universal sample size is adopted. #83's conditional table shows a single-run 274-task comparison cannot resolve gaps below roughly 8 points under independence assumptions (an estimate, not a bound). The owner sets minimum detectable effect per gate.

These criteria are proposed for #41's evidence grades as the definition of a "comparable" benchmark claim.

## Pre-deployment gate (handoff to #37)

Proposal for #37 to adopt or narrow. Thresholds are owner decisions (Open questions); none are proposed as universal standards.

| Gate | Applies when | Passes when | Missing evidence |
| --- | --- | --- | --- |
| P0 Compatibility | Always | EvaluationReport `result` = `valid`, no `error` findings with outcome `fail` | Report missing: `blocked` |
| P1 Run integrity | Any gating suite | QualityEvaluationRun exists for the current `build_id` and `build_revision`, `status` = `passed`, and `evaluator_version` / `dataset_revision` match the frozen protocol (EVAL-03, EVAL-04) | `blocked` |
| P2 Task quality | Workload sets `quality_target` | W-R10 passes under the target's protocol | W-R10 `unknown`: `needs_review` |
| P3 Workload-specific | RAG, agent, structured output (taxonomy above) | Owner thresholds met (EVAL-12, EVAL-13) | `needs_review` |
| P4 Safety | User-facing generation | Safety suite run on the build; no regression beyond the owner margin against the reference (previous release or base model) | `blocked` for fine-tunes (EVAL-07); `needs_review` otherwise |
| P5 Performance | Latency or throughput target set | W-R7 passes on eligible measurements (EVAL-10) | `needs_review` |
| P6 Cost | Budget set | #39 estimate within budget, using measured usage per task | `needs_review` |

Mapping to EvaluationReport `deployment_readiness`: any `fail` with severity `error` gives `blocked`; any `unknown` with severity `error` gives `needs_review` unless the row says `blocked`; otherwise `ready`. This keeps measured evidence (QualityEvaluationRun) separate from compatibility (EvaluationReport), as the v1 schema titles require. v1 has no field linking the two; the interim link is a finding's `evidence[].path` / `source_version` naming the run id (gap sent to #40).

Re-run triggers: any change to the build revision, model snapshot, engine version, fine-tune artifact, prompt / system instructions, retrieval index, guardrail configuration, or the evaluation protocol invalidates prior runs for the affected gates.

## Fine-tune gate (absorbs #33 and #32 handoffs)

Applies when a `fine_tuned_model` is selected. All paired comparisons use the same protocol (R1–R11) on the base and the tuned artifact.

1. **Freeze the eval set before training** (accepting #32 step 3): #36's protocol owner freezes the task and safety sets, hashes every item, and embeds the BIG-bench canary. The frozen set hashes are recorded in the run's `dataset_revision`.
2. **Training-data harm screen** before training. Foundry's provider-run screen is one implementation (#33 Q3). Self-hosted builds need an equivalent screen; no open-source screen was assessed here.
3. **Safety regression vs base.** Run the same safety suite on base and tuned model. Evidence for the need: Qi et al. report fine-tuning on 10 adversarial examples raised GPT-3.5 Turbo's harmfulness rate from 1.8% to 88.8%, and benign Alpaca fine-tuning from 5.5% to 31.8% (#33 Q1; 2023 models; independent measurement, not reproduced). Candidate suites: AILuminate demo / practice set, HarmBench.
4. **Capability retention** on general harness tasks, because LoRA and full fine-tuning both forget (#33 Q2, Llama-2-7B, code and math).
5. **Task gain** over the base on the frozen task set.
6. **Leakage check** of training data against the frozen sets (#32 D-20), with hit counts recorded.

Rule A-20 (#33) becomes EVAL-07; D-20 (#32) is accepted as EVAL-09.

## Comparison fields

The issue's minimum fields mapped to v1. "No v1 field" items need a #40 proposal; until then they stay in notes or namespaced `extensions`.

| Field / JSON pointer | Type and unit | Finding | Evidence requirement | Conditions / unknowns |
| --- | --- | --- | --- | --- |
| `evaluation id` → CatalogItem `/id`, `/version`; run `/id` | id; string | Suite identity | Publisher release or commit | One version per catalog ID in current intake |
| `type` → no v1 field | enum (taxonomy types above) | Needed for gate selection | — | Propose `evaluation_types` to #40; interim `tags` |
| `applies to` → no v1 field in spec | list of kinds and workload axes | COMPONENTS.md lists model, rag_pipeline, agent_framework, fine_tuned_model as compatible kinds | — | Propose `applies_to_kinds` |
| `dataset` → `/spec/dataset_refs`; run `/dataset_revision` | refs; string | `dataset_refs` must reference `training_dataset` items | Dataset card, revision or content hash | Evaluation sets are not training data; propose an eval-dataset reference or kind to #40 |
| `metric` → `/spec/metric_names` (required, ≥1); run `/measurements/*/metric`, `/unit` | string list; unit string | Framework suites have task-dependent metrics | Publisher metric definition | A framework item cannot list a fixed metric set honestly; catalog a specific suite version instead |
| `mode` → `/spec/mode` (required) | `offline` / `online` / `both` | Online = sampled production evaluation (#38) | — | — |
| `baseline` → no v1 field | run reference | Needed for regression gates | Baseline run with the same protocol | Propose `baseline_run_ref` |
| `threshold` → selection `/settings/minimum_score`; run `/measurements/*/threshold`, `/comparator` | number; `gte`/`gt`/`lte`/`lt`/`eq` | One `minimum_score` per selection cannot express per-metric thresholds | Owner or user decision | Use run measurements for per-metric thresholds |
| gate → `/spec/gate_on_deployment`; selection `/settings/gate_required` | boolean | — | — | Spec flag is a suite property; selection flag is the user's choice |
| sample size → run `/sample_size`; selection `/settings/dataset_size` | integer ≥ 1 | — | Actual items scored | Uncertainty not representable in v1 |
| `reproducibility notes` → run `/evaluator_version`, `/notes`, `/artifacts` | string; string list; URI list | R1–R15 do not fit dedicated fields | Full tuple | Propose fields: judge model, sampling / seed / k, harness and task versions, uncertainty, contamination status |
| licence → CatalogItem `/license` | SPDX, booleans | — | Licence file | Data and code licences can differ (AILuminate) |

## Evidence

Access dates are UTC.

| ID | Publisher and URL | Access date | Version / region | Evidence grade | Limitations / reuse terms |
| --- | --- | --- | --- | --- | --- |
| E01 | EleutherAI, https://pypi.org/project/lm-eval/ | 2026-10-17 | 0.4.13, uploaded 2026-08-31; MIT | Primary documentation | — |
| E02 | EleutherAI, https://github.com/EleutherAI/lm-evaluation-harness (README) | 2026-10-17 | `main`, last push 2026-09-14 | Primary documentation | README on `main`, not pinned to 0.4.13 |
| E03 | EleutherAI, https://github.com/EleutherAI/lm-evaluation-harness/blob/main/docs/new_task_guide.md#versioning | 2026-10-17 | `main` | Primary documentation | — |
| E04 | EleutherAI, https://github.com/EleutherAI/lm-evaluation-harness/blob/main/docs/decontamination.md | 2026-10-16 (via #32 T14) | 0.4.13 | Primary documentation | Not re-read here |
| E05 | Stanford CRFM, https://pypi.org/project/crfm-helm/ ; https://github.com/stanford-crfm/helm ; https://crfm-helm.readthedocs.io/en/latest/maintenance_mode/ | 2026-10-17 | 0.5.16, 2026-04-30; Apache-2.0 | Primary documentation | — |
| E06 | Liang et al., HELM, https://arxiv.org/abs/2211.09110 | 2026-10-17 | v2 | Primary documentation | Abstract only |
| E07 | Mazeika et al., https://arxiv.org/abs/2402.04249 ; https://github.com/centerforaisafety/HarmBench | 2026-10-17 | arXiv v2; repo MIT, last push 2024-08-16, no releases | Primary documentation | Abstract and README only |
| E08 | MLCommons, https://mlcommons.org/ailuminate/ ; https://github.com/mlcommons/ailuminate | 2026-10-17 | README "v1.0 DEMO"; repo description "v1.1"; data CC BY 4.0 | Primary documentation; page totals (59,624 prompts, 109 models) are vendor claims | Version label conflict unresolved; full set and evaluator member-only |
| E09 | Ragas, https://pypi.org/project/ragas/ ; https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/ ; Es et al., https://arxiv.org/abs/2309.15217 | 2026-10-17 | 0.4.3, 2026-01-13; Apache-2.0; docs page dated 2025-12-09; arXiv v2 | Primary documentation | — |
| E10 | TruLens, https://pypi.org/project/trulens/ ; https://www.trulens.org/getting_started/core_concepts/rag_triad/ | 2026-10-17 | 2.15.0, 2026-10-05; MIT | Primary documentation | Hallucination-free statement is a vendor claim |
| E11 | UK AI Security Institute, https://pypi.org/project/inspect-ai/ ; https://inspect.aisi.org.uk/ | 2026-10-17 | 0.3.281, 2026-10-15; MIT | Primary documentation | "200+ evaluations" is a publisher count |
| E12 | promptfoo, https://www.npmjs.com/package/promptfoo ; https://github.com/promptfoo/promptfoo | 2026-10-17 | 0.124.1, 2026-10-08; MIT | Primary documentation | Description only |
| E13 | Confident AI, https://pypi.org/project/deepeval/ ; https://github.com/confident-ai/deepeval . OpenAI, https://pypi.org/project/evals/ ; https://github.com/openai/evals | 2026-10-17 | DeepEval 4.3.1, 2026-10-16, Apache-2.0; Evals 3.0.1.post1, 2024-05-01, MIT | Primary documentation | Descriptions only |
| E14 | Yao et al., τ-bench, https://arxiv.org/abs/2406.12045 | 2026-10-17 | Abstract page | Independent measurement (benchmark authors, 2024 agents) | Abstract only |
| E15 | Zheng et al., Judging LLM-as-a-Judge, https://arxiv.org/abs/2306.05685 | 2026-10-17 | v4 | Independent measurement | Abstract only; agreement figure is for GPT-4 in 2023 |
| E16 | vLLM, https://docs.vllm.ai/en/latest/benchmarking/cli/ | 2026-10-17 | `latest`, unversioned | Primary documentation | Re-check against the pinned vLLM version |
| E17 | AWS, https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation.html | 2026-10-17 | Unversioned; region not assessed | Primary documentation | Pricing and judge-model list not read |
| E18 | Google Cloud and Microsoft, via #33 Q7 and Q3 | 2026-10-16 | See #33 | Primary documentation | Not re-fetched |
| E19 | Qi et al. and Biderman et al., via #33 Q1, Q2 | 2026-10-16 | See #33 | Independent measurement | Not reproduced |
| E20 | #62 desk validation, [PR #83](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/83) head `0be51ab` | 2026-10-17 | Unmerged | Project research (pending) | Gates G1–G4 and C1/C3 are proposals awaiting this issue's owner |
| E21 | #2 workload draft, [PR #81](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/81) head `e2bcc35` (W-R7, W-R10, `latency_targets`) | 2026-10-17 | Unmerged | Project research (pending) | — |
| E22 | #41 interim policy, [PR #75 review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75#pullrequestreview-5550616927) §3 | 2026-10-17 | Interim | Owner decision | — |
| E23 | #32 leakage method and D-20, [training-dataset.md](../T5-training-fine-tuning/training-dataset.md) T11–T16 | 2026-10-17 | `main` | Project research | — |

## Compatibility proposals

Proposed for #40 using the [rule proposal template](../../templates/rule-proposal.md) fields in compact form. Outcome and severity are separate. A missing input returns `unknown`, never `pass`. Status: **source checked** (assertion backed by cited text read on its access date), **hypothesis**, or **policy proposal** (a decision, not a fact). None is verified.

| Rule | Participating kinds / pointers | Applies when | Assertion | Outcome / severity | Missing data | Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EVAL-01 | `evaluation_suite` task type; `model` access route | A selected suite task needs loglikelihood scoring and the model is reachable only through a chat-completion API | Task cannot run on that route; use a generative variant, a completions route or self-hosted weights | fail / error (for that task) | Route unknown: unknown / warning | E02 | source checked (lm-eval only) |
| EVAL-02 | Cited benchmark figure; tuple R1–R15 | A benchmark figure is displayed | Display as comparable only with a fully pinned tuple; compare two figures only when one element differs | unknown / warning when incomplete; fail / warning for a comparison differing in >1 element | unknown | E20, E22 | policy proposal (adopts #83 C1, pending) |
| EVAL-03 | `/settings/gate_required`; QualityEvaluationRun `/build_id`, `/build_revision` | Gate required | A run exists for the current build revision | unknown / error → `blocked` | — | Schema fields (source checked) | policy proposal |
| EVAL-04 | Run `/evaluator_version`, `/dataset_revision` vs frozen protocol | Run exists | Both match the frozen protocol | fail / error when different; unknown / error when unrecorded | unknown | Schema fields | policy proposal |
| EVAL-05 | Run `/status`, `/measurements/*/passed` | Gating metric present | `status` = `passed` and every gating measurement `passed` = true | fail / error; `incomplete` → unknown / error | unknown | Schema fields | policy proposal |
| EVAL-06 | Judged metric; judge model id; system-under-test model id | A gating metric is LLM-judged | Judge identity and version recorded; judge ≠ system under test; human-agreement sample meets owner threshold | unknown / warning when unrecorded; fail / warning when judge = system under test | unknown | E15, E20 | source checked (bias exists); policy proposal (thresholds) |
| EVAL-07 | `fine_tuned_model` base ref; paired safety runs | Fine-tune selected | Paired safety runs on base and tuned model under one protocol; regression within owner margin | unknown / error (no paired run) → `blocked`; fail / error (beyond margin) | unknown | E19, E18 | policy proposal (replaces #33 A-20) |
| EVAL-08 | Same, capability and task runs | Fine-tune selected | Capability retention within margin; task gain ≥ owner minimum | fail / warning; unknown / warning | unknown | E19 | policy proposal |
| EVAL-09 | `training_dataset` `/spec/held_out_test_set`; leakage record; frozen set hashes | `held_out_test_set` = true | Leakage check against #36's frozen set recorded with hit counts | unknown / warning | unknown | E23 | policy proposal (accepts #32 D-20) |
| EVAL-10 | Performance measurement conditions; workload `latency_targets` | Latency or throughput target set | Measurement states arrival process, concurrency and cache state; `inf` request rate or warm prefix cache is ineligible for an interactive latency target | unknown / warning (ineligible) | unknown | E16, E21 | source checked (vLLM defaults and caveat); policy proposal (eligibility) |
| EVAL-11 | Safety suite locales; workload language | Safety gate applies | Workload language is covered by the suite's locales | unknown / warning | unknown | E08 | source checked (AILuminate locales); hypothesis (coverage transfers poorly across languages) |
| EVAL-12 | Workload `knowledge`; suite metric types | `knowledge` ≠ `none` | Suite includes `retrieval` and `grounding` metrics | fail / warning | unknown / warning | E09, E10 | policy proposal |
| EVAL-13 | Workload `actions`; suite metric types | `actions` = `write` | Suite includes end-state `agent_task` with k ≥ owner minimum trials | fail / warning | unknown / warning | E14 | policy proposal |
| EVAL-14 | `evaluation_suite` = HELM | Selected | Maintenance mode; scenarios relying on external APIs may break | pass / warning (deprecated-like) | — | E05 | source checked |

Synthetic examples (illustrative, not measurements):
- EVAL-01 pass: MMLU-style multiple-choice task on a self-hosted vLLM model. Fail: the same task against a chat-completions-only API. Skipped: generative-only suite.
- EVAL-04 fail: run recorded `dataset_revision` `v2` while the frozen protocol is `v3`.
- EVAL-07 unknown: tuned model has a safety run but the base model has none under the same protocol.

## Pricing and capacity

Not priced here. Evaluation cost is model / judge API usage plus compute time, priced by #39 from Pricebooks. Judge calls scale with items × judged metrics × trials (k). AILuminate's official evaluator access and Bedrock evaluation pricing were not read. No capacity estimate is made.

## Recommendation and rationale

1. **Evaluate the configured system, not the model.** Gates use the user's frozen task set; public benchmarks inform selection only.
2. **Prefer deterministic scoring** where the task allows (extraction, code, SQL, structured output). Use judged metrics only with recorded judges (EVAL-06).
3. **Candidate defaults, pending owner adoption:** lm-evaluation-harness for capability retention (self-hosted, or completions-capable routes); Inspect for agent and sandboxed tasks; Ragas or TruLens for RAG grounding; AILuminate (demo or member practice set) and HarmBench for safety, with their access and staleness limits stated; vLLM `bench serve` or an equivalent load generator for performance. HELM and OpenAI Evals are not recommended as gate dependencies (maintenance mode; no release since 2024).
4. **Adopt R1–R15 and the one-factor rule** as #41's definition of a comparable benchmark claim.
5. **Make fine-tune safety regression a blocking gate** (EVAL-07), because the evidence shows large regressions from small fine-tunes.

## Structured artifacts

No CatalogItem proposals. Reasons:
- Framework candidates (lm-eval, Inspect, Ragas, TruLens, DeepEval, promptfoo) have task-dependent metrics, so a fixed `metric_names` list would misstate them.
- Fixed suites (AILuminate, HarmBench) could be catalogued, but `gate_on_deployment` is an owner policy decision, `dataset_refs` would have to point to `training_dataset` items, and AILuminate's version label conflicts (v1.0 vs v1.1).
- No QualityEvaluationRun: nothing was run.

Proposed for #40 (no schema change made): eval-dataset reference or kind; `evaluation_types`; `applies_to_kinds`; `baseline_run_ref`; run fields for judge model, sampling / seed / k, harness and task versions, uncertainty and contamination status; a link from EvaluationReport findings to QualityEvaluationRun ids; #33's `evaluation_report_ref` on `fine_tuned_model`.

## Open questions and handoffs

Owner decisions for @PUSHINGSQUARES (#36):

| Question | Owner |
| --- | --- |
| Gate thresholds: safety regression margin, capability-retention margin, minimum task gain, minimum k for agent pass^k, judge human-agreement threshold, minimum detectable effect per gate | #36 · @PUSHINGSQUARES |
| Suite adoption: which candidates become defaults per evaluation type | #36 · @PUSHINGSQUARES |
| Freeze policy: who freezes eval sets, when re-freezing is allowed, retention of hashes | #36 · @PUSHINGSQUARES, with #32 · @appletechie |
| Accept, narrow or reject #83 gates G1–G4 and conventions C1 / C3; set δ and δm if a replication is wanted | #36 / #62 · @PUSHINGSQUARES |
| Whether P2–P6 `unknown` results give `needs_review` or `blocked` | #36 · @PUSHINGSQUARES, with #37 |
| Latency defaults (#81 Q5) and allowed `quality_target` protocols (#81 Q6) | #36 · @PUSHINGSQUARES |

Handoffs (owners are live assignees on 2026-10-17; none confirmed yet):

| To | What | Owner |
| --- | --- | --- |
| #37 | Pre-deployment gate P0–P6 and readiness mapping | @appletechie, @PUSHINGSQUARES |
| #38 | Online evaluation (`mode` `online` / `both`), re-run triggers | @appletechie, @PUSHINGSQUARES |
| #41 | R1–R15 and one-factor rule as evidence-grade criteria for benchmark claims | @tynamite, @PUSHINGSQUARES |
| #40 | EVAL-01 to EVAL-14; field gaps above | @zwright8, @tynamite |
| #32 | Accept D-20 as EVAL-09; eval-set freeze ownership | @appletechie, @PUSHINGSQUARES |
| #33 | A-20 replaced by EVAL-07 / EVAL-08; fine-tune gate | @Mattycodes69, @appletechie |
| #2 | Taxonomy keyed on #81 axes; W-R10 protocol definition | @tynamite, @appletechie |
| #6 / #7 | Quality only against a selected `quality_target`; no usable-context scalar (#7's #36 row) | @zwright8 (#6 with @PUSHINGSQUARES; #7 with @appletechie) |
| #16 | Retrieval and grounding metrics; permission-compliance test cases | @zabyxc01, @appletechie |
| #25 | `agent_task` with pass^k; #83 C2 | @CompleteDotTech, @Mattycodes69 |
| #35 | Safety suites and side-effect tests for `write` actions | @appletechie, @PUSHINGSQUARES |
| #39 | Evaluation cost (judge calls, compute) and cost per completed task | @appletechie, @PUSHINGSQUARES |
| #10 / #11 | Performance measurement conditions (EVAL-10) and engine-version pinning | @Mattycodes69 (#10 with @appletechie; #11 with @zwright8) |

Evidence gaps: over-refusal measurement; permission-compliance evaluation for RAG; an open-source training-data harm screen; MTEB and SWE-bench primary sources; AILuminate version label; Bedrock / Vertex evaluation pricing and judge models.
