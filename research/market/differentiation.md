# Differentiation hypotheses and falsification

Issue: [#57](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/57) (MR-10). Status: **Draft — cannot be accepted before #66.** This is not an accepted positioning decision or marketing copy. Live assignee on 2026-10-16: `appletechie`; the issue body names CompleteDotTech as coordinator. That discrepancy is for the owner to resolve and is not settled here.

Base revision: `research/market-intelligence` at `6511dea`. Inputs: [profiles](competitors/README.md), [catalog](competitors.json), [matrix](features.json), [substitute log](substitute-validation.md) (#66, one scenario), and tynamite's PR #67 review (2026-10-16). Pending and unaccepted inputs: PR #87 (matrix re-grade, head `870d6d8`), PR #94 (#58 risk ranking, head `ec1c5fe`) and PR #81 (T0 notes, head `6b6e975`, D36–D41). Access date for everything below: 2026-10-16.

Evidence classes: **PD** primary documentation, **VC** vendor claim, **OB** observed behavior (scoped to recorded steps), **IM** independent measurement, **ES** estimate, **HY** hypothesis. No claim in this note is IM.

## Prior conclusions retained

- The broad claim that users lack model recommendation or hardware-fit tools is falsified (PD/OB: Flocci, ModelFit, llmfit, Local AI Planner, Artificial Analysis).
- Simple guided stack advice is not distinctive. A Flocci Stack Builder run returned ordered RAG components, constraints and uncertainty (OB, [substitute log](substitute-validation.md)).
- Nobody has shown that a complete T0–T6 builder is unique, or that it isn't. No exhaustive market search or full end-to-end competitor test was performed.

## Falsifiable hypotheses

Historical thresholds were left as named coordinator decisions (D-57-n). The prospective protocol below supplies engineering choices for a new follow-up only. Existing #66 results were already read, so these choices cannot retroactively preregister or score that work. Once a follow-up result is known, its threshold cannot be changed to save a hypothesis.

| ID | User decision (bounded) | Observable outcome | Falsification test | Fails if | Class |
| --- | --- | --- | --- | --- | --- |
| H1 Traceable compatibility advice | Which component set to adopt for one constrained local/hybrid workload | The user reaches a configuration that meets the stated constraints, with each fit/compatibility claim traced to a source or marked unknown | #66 common and contradictory-constraint scenarios: the best substitute versus a traced record, scored on constraint satisfaction, contradiction detection and per-claim traceability | The substitute meets or exceeds D-57-1 (parity margin) on all three, or it flags the contradiction and cites its sources | HY |
| H2 Workload-first cross-provider comparison | Whether to run each component locally, through an API or hosted | A local/API/hosted split with stated trade-offs that satisfies the constraints | Same #66 scenarios, run against Flocci Stack Builder and one second substitute (Artificial Analysis recommender or OpenRouter plus docs) | A substitute's output satisfies the constraints and explains the trade-offs at or above D-57-2 | HY |
| H3 Versioned shared configuration record | Whether a reviewer or teammate can approve or reproduce a configuration without the author | The recipient reconstructs the exact component versions, assumptions and unknowns | Round-trip test: the recipient rebuilds from (a) the proposed record, (b) Dify DSL / n8n JSON / SkyPilot YAML, (c) a README plus deployment manifest. #63 then asks which one participants prefer | (b) or (c) reaches D-57-3 reconstruction parity, **or** #63 preference/willingness-to-pay falls below D-57-4 | HY |
| H4 Neutral cost advice | Which option is cheapest for a stated workload | A cost comparison the user trusts and that stays within its freshness window | Measure the maintenance effort for the scenario's price set over D-57-5 days (#64/#39), plus #63 trust responses against OpenRouter/Artificial Analysis pricing pages | Keeping prices fresh costs more than D-57-6, or trust is not higher than the substitutes | HY |
| H5 Defensible configuration-outcome history | Whether to trust a recommendation because it has comparable recorded outcomes | Version-pinned, reviewed outcome records for the scenario's hardware/model/engine combination | Coverage check of LocalScore, MetriLLM, Rapid-MLX, LocalMaxxing, llama.cpp threads and OpenBenchmarking for the #66 scenario's combination | Existing projects publish comparable version-pinned outcomes for at least D-57-7 of the scenario's combinations | HY |
| H5b (declared now, before results) | Same decision, **multi-component stacks** (RAG/agent), not single-model inference speed | Outcome records cover stack-level behavior (retrieval, tool use), not only tok/s | Same coverage check, restricted to stack-level outcomes | Any reviewed project publishes stack-level reproducible outcomes for the scenario | HY |

H5 is the current note's "reviewed, reproducible history of configuration outcomes" claim. tynamite's PR #67 review (provenance item 5) says community fit-report projects are direct counterexamples to it. The evidence below supports that for single-model inference throughput. H5b is the narrowed alternative, declared before #66 reports. It is not a result.

## Counterexamples

Two labels are kept apart: **NPE** (no public evidence found; this is not absence) and **EXU** (explicitly unsupported or excluded by the source).

| Hyp. | Strongest competing workflow | Evidence (class) | NPE vs EXU | Substitute is sufficient when |
| --- | --- | --- | --- | --- |
| H1 | Flocci Stack Builder; ModelFit; llmfit | Flocci returned an ordered RAG stack with uncertainty (OB). llmfit documents fit scoring and `recommend --json` (PD). ModelFit speed is "bandwidth-derived, explicitly not measured" (PD) | NPE: per-claim source tracing in Flocci output; no contradiction test yet. EXU: ModelFit says it does not measure speed | The user only needs a plausible starting stack, not per-claim provenance |
| H2 | Flocci Stack Builder; Artificial Analysis recommender; OpenRouter models plus routing | AA recommender priorities across intelligence/speed/cost (VC). OpenRouter Models API (PD) | NPE: whether any of them mixes local and API per component under constraints | The decision is API-only, or local-only on one device |
| H3 | Dify YAML DSL; n8n workflow JSON; SkyPilot task YAML; README plus Compose/Helm manifest | Dify DSL exports model parameters (PD); n8n JSON export/import (PD); SkyPilot YAML (PD), all per PR #87 cells | EXU: Dify DSL excludes knowledge data and tool API keys; n8n exports may retain credential names/IDs (PD, PR #87). NPE: assumption or unknown fields in any of them | The team already runs on one platform, and the manifest is the source of truth |
| H4 | OpenRouter pricing; Artificial Analysis price/speed data; GPU price sites | Listed rates (PD). The profile notes that a list price is not a complete bill | NPE: complete TCO with operational cost (matrix `tco` Unknown for all products) | The user compares API token prices only |
| H5 | **LocalScore** (Mozilla Builders) | an open-source benchmark plus a public results database; users "optionally submit". The site says it "cannot cover all possible scenarios (speculative decoding, etc)" ([about](https://www.localscore.ai/about), PD) | Hardware-purchase or "can my machine run model X" decisions |
| H5 | **MetriLLM** | "Every submitted result is displayed. We don't curate or filter"; "Each run includes a hash for verification"; tests Ollama models as-is ([methodology](https://metrillm.dev/methodology), VC) | The user accepts unreviewed but hashed community runs |
| H5 | **Rapid-MLX** | "Every submission is one locked run". Runs under older versions are "badged with their version and never mixed into current medians". "Submissions: CC0" ([leaderboard](https://rapidmlx.com/leaderboard), PD) | Mac users comparing version-pinned inference throughput. This is the closest match to the "versioned outcome history" claim |
| H5 | **LocalMaxxing** | "Every number on this site comes from a community-submitted run". Leaderboard filters by model, hardware, engine and quantization ([home](https://www.localmaxxing.com/en), VC). The plausibility filter is reported by #81 D38 and was not re-verified | Speed comparison across engines and quantizations |
| H5 | **llama.cpp performance threads** | [#4167](https://github.com/ggml-org/llama.cpp/discussions/4167) (Apple, updated 2026-10-01) and [#15013](https://github.com/ggml-org/llama.cpp/discussions/15013) (CUDA, updated 2026-10-16): tables pinned to a commit hash for a fixed model/quant (PD) | A llama.cpp user picking a GPU or backend |
| H5 | **OpenBenchmarking `pts/llama-cpp`** | via the Phoronix Test Suite. The PTS docs describe uploading to OpenBenchmarking.org and a batch mode that does not upload ([docs](https://github.com/phoronix-test-suite/phoronix-test-suite/blob/master/documentation/phoronix-test-suite.md), PD) | Reproducible hardware/software-labelled throughput |

H5 conclusion (HY, Medium confidence): for single-model local inference throughput, these projects already provide public, partly version-pinned outcome histories. H5 is therefore **falsified as stated** for that scope. In the reviewed sources (NPE), none of them shows stack-level (RAG/agent) outcomes or a review process tied to a component contract. That gap leaves H5b open, and it remains untested.

## Source provenance and explainability (profiled products)

Each cell ID is `product_id:feature`. "PR #67" is the current branch grade (`Verified Partial`/`Verified Full`). "PR #87" is the pending re-grade (`Documented`/`Exercised`) that answers tynamite's review item 1. Grades shown use PR #87 names. Cells marked ⁸⁷ are Unknown on PR #67 and graded only in PR #87. Every other non-Unknown cell is `Verified Partial` on PR #67. PR #87 is unmerged, so its grades are proposals. No cell anywhere is graded IM.

| Product | Explanation | Version identity | Saved / share / export | Provenance assessment |
| --- | --- | --- | --- | --- |
| flocci | `flocci:explanation` Verified Full (#67) → Unknown in #87 (historical run not replayed) | Unknown | `flocci:saved` Documented (bookmarks, FAQ; #67 basis was generic); share/export Unknown | Explanations observed once (OB); no per-claim sources seen; recommendation correctness unverified |
| modelfit | `modelfit:explanation` Documented | `modelfit:model_versions`⁸⁷ Documented (variants; immutable revisions unverified) | `modelfit:export`⁸⁷ Documented (JSON dataset, not a build) | The publisher labels its speed estimates as not measured. Explaining its own uncertainty is an existing counter to H1 |
| llmfit | `llmfit:explanation` Documented (info output exposes assumptions) | Unknown | `llmfit:saved`/`share`⁸⁷, `llmfit:export` Documented (local benchmark runs, contribution, `--json`) | The closest open-source analogue to traced fit plus shareable runs; seed-site operator unconfirmed |
| local-ai-planner | `local-ai-planner:explanation` Documented ("why these models", heuristic limits) | Unknown | Unknown | EXU: the page says context metadata is unavailable for the current model set |
| artificial-analysis | `artificial-analysis:explanation` Documented (recommender priorities, not exercised) | `artificial-analysis:model_versions`⁸⁷ Documented | `artificial-analysis:export`⁸⁷ Documented (API) | The methodology page documents evaluation provenance; data terms restrict reuse (PR #82, pending) |
| benchlm | `benchlm:explanation` Documented (evidence-confidence labels) | `benchlm:model_versions`⁸⁷ Documented | `benchlm:share`⁸⁷ (URL state), `benchlm:export`⁸⁷ (CSV) Documented | Strong source-level provenance for benchmarks; commercial display needs an agreement |
| harness-bench | Unknown | Unknown | Unknown | `harness-bench:benchmarks` Documented; the paper (106 tasks) and the site (300 tasks) conflict; no repository license |
| hugging-face | Unknown | `hugging-face:model_versions` Documented (commit history) | `hugging-face:export`⁸⁷ Documented (repo clone, not a build) | Strongest revision provenance for artifacts; cards are publisher-authored |
| models-dev | Unknown | `models-dev:model_versions` Documented | `models-dev:export`⁸⁷ Documented (JSON, offline snapshot) | Metadata provenance only; no decision explanation |
| openrouter | Unknown | `openrouter:model_versions`⁸⁷ Documented (IDs; alias-to-revision unknown) | `openrouter:export`⁸⁷ Documented (catalog, not a build) | Coupled to execution; no recommendation rationale found (NPE) |
| dify | Unknown | Unknown | `dify:saved`/`share`/`export`⁸⁷ Documented (DSL) | EXU: the export excludes knowledge data and keys. It is reproducible as an app, but it doesn't record why choices were made |
| n8n | Unknown | Unknown | `n8n:saved`/`share`/`export`⁸⁷ Documented (JSON) | Executable artifact; no recommendation or assumption record found (NPE) |
| skypilot | Unknown | Unknown | `skypilot:saved`/`share`⁸⁷, `skypilot:export` Documented (task YAML) | Declarative resource provenance; no workload-fit rationale found (NPE) |

Reading (HY): explanation and versioning already exist, but in separate products. Explanation sits in recommenders (Flocci, ModelFit, llmfit, AA). Version identity sits in metadata hubs (HF, models.dev). Reproducible artifacts sit in workflow tools (Dify, n8n, SkyPilot). No reviewed product combines rationale, per-claim source, version pin and declared unknowns in one exportable record (NPE, not absence). This is H1/H3's remaining claim, and #66 plus the H3 round-trip test must establish it.

## Kill and pivot criteria (conditions, not results)

| Condition | Action |
| --- | --- |
| #66: a substitute passes H1 **and** H2 in both the common and the contradictory scenario | Kill H1/H2 as differentiators. #58 drops guided selection as the wedge |
| #66: a substitute passes the common scenario but fails contradiction detection or traceability | Pivot to a narrowed H1: contradiction detection plus traced unknowns only |
| H3 round-trip: a Dify/n8n/SkyPilot manifest or README reaches D-57-3 parity | Pivot H3 from a standalone record to export **into** those formats (n8n profile's complementary option) |
| #63 (only with approved, accepted primary evidence): preference or willingness-to-pay for a versioned record falls below D-57-4 | Kill H3 as a paid proposition; keep it as an internal artifact. Without #63 evidence, H3 value stays **unknown**, not assumed |
| H4 maintenance cost exceeds D-57-6, or trust is not above the substitutes | Kill cost neutrality as a differentiator; link to provider pricing |
| H5: community projects already cover D-57-7 | H5 stays killed; carry H5b forward |
| H5b: a stack-level reproducible outcome source exists for the scenario | Kill H5b; the remaining option is integration or contribution with those projects (#81 Q7, #41 rights) |
| All of H1–H5b fail | Recommend that #58 rejects a differentiated MVP for this scope |

## Proposed source-register additions

These are for the #48 owner to apply in `sources.json`. They are not applied here.

| Proposed ID | URL | Publisher | Status 2026-10-16 | Grade per claim |
| --- | --- | --- | --- | --- |
| src-localscore | https://www.localscore.ai/about | Mozilla Builders / LocalScore | retrieved | PD (scope, submission, collected fields) |
| src-metrillm | https://metrillm.dev/methodology | MetriLLM | retrieved | VC (reproducibility, no-curation) |
| src-rapid-mlx | https://rapidmlx.com/leaderboard | Rapid-MLX | retrieved | PD (protocol, CC0 statement) |
| src-localmaxxing | https://www.localmaxxing.com/en | LocalMaxxing | home retrieved; leaderboards excluded by robots.txt | VC |
| src-llamacpp-perf | https://github.com/ggml-org/llama.cpp/discussions/4167, /15013 | ggml-org community | retrieved via GitHub API | PD (thread protocol) |
| src-openbenchmarking-llama-cpp | https://openbenchmarking.org/test/pts/llama-cpp | Phoronix Media | HTTP 403 challenge; PTS docs retrieved instead | PD (PTS docs) |

Data reuse rights for these sources are not established (#60/#41). Rapid-MLX's CC0 statement is a claim for #41 to review, not a grant accepted here.

## Acceptance map

| Criterion | Section | State |
| --- | --- | --- |
| State falsifiable hypotheses | Falsifiable hypotheses | Drafted; thresholds D-57-1…7 await a coordinator decision |
| List counterexamples | Counterexamples | Drafted; #66 second substitute and contradictory scenario pending |
| Provenance and explainability | Provenance table | Drafted against the PR #67 cells; PR #87 pending |
| Kill and pivot criteria | Kill and pivot | Drafted as conditions |
| Every conclusion linked | Throughout | Self-checked only; reviewer pending |
| Technical owners review handoffs | handoffs.md rows #57 → #2/#40/#42 | tynamite accepted with a coverage gap, now addressed for review |
| Checks pass; reviewer accepts | — | Blocked by #66; no acceptance claimed |

## CanIRun.ai intake (2026-10-16)

The [CanIRun.ai profile](competitors/canirun-ai.md) adds a device-first counterexample candidate for #66. It strengthens the reason to test narrow model-selection substitutes; it does not establish full-stack substitution. Keep existing hypothesis thresholds and acceptance gates unchanged pending scenario evidence.


## Prospective follow-up protocol (2026-10-18)

These are engineering design choices under the user's delegated project authority, not measured product thresholds, an accepted positioning decision, or another owner's acknowledgement. Existing Flocci, ModelFit and CanIRun observations informed the design and remain exploratory. Preserve the historical H5 disposition. Before collecting new results, record this protocol's commit, the exact scenario inputs, product/runtime versions, a fixed required-field list and the evaluator. Any amendment creates a separately labelled follow-up; do not pool earlier results or silently exclude failures. An inaccessible tool is unobserved, not a failed capability.

| Decision | Fixed rule for the new follow-up | Rationale and limit |
| --- | --- | --- |
| D-57-1 | Zero parity margin: a substitute must meet every hard constraint, explicitly identify every deliberately contradictory pair, and attach an eligible source or an explicit unknown to every material compatibility assertion. A claimed resolution based on an unknown hard constraint does not pass. | Hard constraints are conjunctive; average scores must not hide a violation. No historical result is rescored. |
| D-57-2 | Require all D-57-1 conditions plus an explicit operator/capacity classification for each serving component and at least one stated trade-off between the local and hosted alternatives. | A provider name alone does not explain the local/API decision. |
| D-57-3 | Reconstruction parity requires 100% agreement on the predeclared required fields: component identities and revisions, operator/capacity, runtime, tokenizer/template, context/output reservations, precision, concurrency, cost assumptions, and evidence/unknowns. A field outside the scenario is marked not applicable before the test. The recipient must reconstruct without author clarification. | This tests a record, not deployment success; execution requires separate authorization. Record all omissions and requests for clarification. |
| D-57-4 | In a future authorized sample of 12 qualified participants spanning at least three distinct buyer roles, require at least 7 to prefer the versioned record over their current alternative and at least 4 to identify a payer and a positive unprompted budget for it. Otherwise narrow or stop the paid-record hypothesis. Incomplete recruitment is inconclusive. | Exploratory stopping rule, not a population estimate, revenue forecast or price anchor. This does not approve #63 recruitment, consent, quotas, interview wording or collection. |
| D-57-5 | Observe one fixed scenario's price set over 28 consecutive days; log source checks, changes and missing observations. | A bounded maintenance study; one period does not establish long-term freshness. No scheduled job is created here. |
| D-57-6 | More than 2 researcher-hours of active maintenance over that 28-day period triggers narrowing the cost-advice scope. Track time prospectively; missing time logs make the outcome inconclusive. | An explicit analyst effort budget, not measured economics or authorization for purchases. Trust remains a separate #63 observation; maintenance alone cannot pass H4. |
| D-57-7 | For a newly fixed scenario matrix, comparable outcomes from existing projects for 100% of its required combinations falsify the exclusive outcome-coverage claim. Each match needs artifact/runtime/hardware pins and the same measured quantity. | An existence/coverage check, not permission to reuse data. It cannot revive the already rejected historical H5 claim. |

For #58, a substitute satisfies this follow-up's **full decision-record scenario** only if D-57-1, D-57-2 and D-57-3 all pass. Failure narrows the research question; it does not establish demand or authorize implementation. Preserve #66's native prerequisite and its owners' evidence review. Hardware error tolerance and cost uncertainty remain workload-specific #10/#39 decisions: without matched measurements or complete meters, offer assumption-explicit screening or partial costs, not a certified fit or savings claim. No go decision follows until applicable empirical gates and receiving scopes are accepted.
