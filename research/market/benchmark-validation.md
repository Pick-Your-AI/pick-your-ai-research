# MR-09: Validate benchmark comparability and harness effects

Issue: [#62](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/62). Live assignees (2026-10-18): @appletechie and @PUSHINGSQUARES. Status: negative comparability finding and scoped receiving decisions prepared for review; no benchmark run. Readiness: Ready. Last researched: 2026-10-18 (bounded B1 table-scope recheck below). Live Project fields are authoritative; this note does not change them.

This desk pass was prepared by a contributor who is not the assignee, for the owner's review. The owner keeps every decision in it. It does not complete #62.

## Question
Which benchmark differences survive controlled model-harness comparisons?

**Working hypothesis H1.** At a fixed model snapshot, task set, budget and grader, harness choice changes delivery outcomes on agentic workloads by at least δ full-credit points, or δm mean-score points. The owner sets δ and δm before any run.

**Falsifier F1.** H1 is falsified for a pair of harnesses at one model when a pinned, paired replication meets two conditions. It uses at least three runs per task and a paired error analysis accounting for repeated runs and shared-source task clusters. Its 90% confidence interval for the gap (two one-sided tests at 5%) lies entirely within ±δ on full-credit rate and within ±δm on mean score. H1 is supported for that pair only when all four gates pass and the estimated gap meets the applicable owner-set margin. A non-significant gap whose interval reaches beyond the margin is inconclusive, not a falsification.

**Gates.** Each published claim gets pass, fail or unknown on four gates. A claim survives only if it passes all four.

| Gate | Test |
| --- | --- |
| G1 Pinned | Both sides name the task set and content lock, model snapshot and provider, harness version, budget, inference settings and grader that produced the result. |
| G2 One factor | Exactly one of those factors differs between the two sides. |
| G3 Above noise | For an identified metric and suite, the gap divided by a valid standard error of the paired difference is at least 1.96, with task/run dependence, shared-source clusters and harness selection accounted for. Missing result-level evidence yields unknown. |
| G4 Same direction | The direction holds on both mean score and full-credit rate, or the claim is explicitly about their divergence. |

The initial market pass forbids paid runs, so this note **can** identify unpinned or conflicting comparisons and conditional power limitations. It **cannot** say whether any harness effect is real.

## Starting evidence
[technical-feasibility.md](technical-feasibility.md), in particular "Benchmark release correction and child boundaries" and evidence rows F14 and F15. The #62 row of the [parent-completion gate](mr09-acceptance.md) and the #56 → #36 and #56 → #25 rows of the [handoff ledger](handoffs.md) list what this child must deliver. This note is not a new canonical component catalog or a completed measurement.

### Release identities

Harness Bench is the only benchmark here with a public model-by-harness design. Its surfaces disagree, so they stay separate rows and are never merged into one dataset.

| Surface | Version / access | Tasks | Runs | Grading as stated | Rights | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| arXiv landing metadata, v2 | Revision 2026-10-15; recorded by #79 on 2026-10-16 | 106 | 5,194 trajectories | Not stated on the landing page | Not stated on the landing page | B1 |
| arXiv full HTML, v2 | Revision 2026-10-15; directly re-read 2026-10-17 | 300 = 274 general + 26 multimodal | 20,454 model/harness/task combinations; one run per configuration (§4.1) | Claims model-judge-free verification; conflicts with B3 | HTML shows CC BY 4.0 for the paper | B1 |
| Website | Unversioned "Diagnostic Benchmark 2026"; accessed 2026-10-16 | 300 = 274 + 26 | 20,454 = 274 × 7 × 10 + 26 × 7 × 7 | Hidden oracles on final artifacts; "No LLM judge in scoring" | "All rights reserved" | B2 |
| Repository | Commit `b8d89634c6f445fcc68ceb6744a59bef6cdf4863`, dated 2026-10-09, "Update Harness-Bench 3.0 benchmark"; inspected 2026-10-16 | 274 packages in `tasks/` + 26 in `multimodal-tasks/`; general content lock `standard274.release-v1.lock.json` | No results in Git; public result bundles are exported separately | Deterministic oracles, plus a bounded LLM fallback on 79 general tasks (see below) | No LICENSE file; CITATION.cff only | B3 |

For re-identification if links change, the general lock records `task_ids_sha256` `sha256:8cb63ccd4df67b2c9c829b6e598296635013f1a31c5c9ff05e768508b9fed4e7` and `task_set_manifest_sha256` `sha256:3a667df15143fa223659f05c137eff6df0d2e1cbbbf571390d6425eaece2b956`. Public history starts on 2026-10-09 although the v1 paper is from May 2026, so earlier history was probably replaced (inference). A later force-push could break the commit links; these hashes would still identify the task set.

The landing-page observation above remains the historical #79 snapshot. B1's versioned full text was directly read on 2026-10-17. Its §4.1 names the multimodal set: GPT-5.6 Sol/Terra/Luna, GLM-5.3-Flash, Kimi-K3, Gemma-4-31B and Qwen3.8-27B. General and multimodal results are separate; GLM-5.3 and DeepSeek-V4 Pro/Flash are excluded from the latter. Cross-suite comparisons still require matching coverage.

**Grader conflict.** At the pinned commit, 79 of the 274 general tasks declare `semantic_judge` with `score_role: bounded_case_fallback`, `default_model: agent` and a `max_fallback_weight` between 0.06 and 0.25 (median 0.10). The judge code caps that weight at 0.25 and says the deterministic oracle stays authoritative for structure, numbers and safety. With `default_model: agent`, the judge is the evaluated model unless a task overrides it. This contradicts the paper introduction and the website's "No LLM judge in scoring". Whether the published results used this code is unknown.

Two consequences follow. For a harness comparison at one model, the judge is the same on both sides, so G2 can still pass. For a model comparison, the grader changes with the model, so G2 fails unless the judge is fixed or judged cases are excluded.

### Comparability checklist

The fields are the 15 minimum-evidence items in PR #74's [`prompts/T6.md`](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/5910bcca98e4064c16ee77b77a338c8ac4c99bc3/prompts/T6.md), a historical proposal at commit `5910bcc` used here as a checklist (#74 has since merged), not as evidence. The #36 owner may replace the list. "Present" means the surface states the field; it does not mean the field is verified. Repository cells describe its tooling defaults, not the settings of the published runs.

| Field | arXiv v2 body (direct recheck 2026-10-17) | Website | Repository `b8d8963` |
| --- | --- | --- | --- |
| Evaluation identifier | Present (paper ID and version) | Missing (no version) | Present (commit; lock file) |
| Task/dataset and version | Present (300) | Present (300), unversioned | Present (274 + 26, content locks) |
| Model and version | Model names in §4.1; immutable snapshots missing | Missing (marketing names, no snapshot or date) | Missing (user-supplied) |
| Provider or runtime | Partial: local versus API routes, no immutable deployment identity | Missing; Gemma-4-31B and Qwen3.8-27B noted as locally hosted with no API cost (quantization and hardware not stated) | Missing (user-supplied endpoint) |
| Inference settings | B.1: temperature 1.0; model-specific maximum output; 200K context; 150 turns | Missing | Present as runner defaults (temperature 1.0, `--thinking high`, `--max-tokens 32768`) |
| Hardware or hosting | Incomplete for local models | Missing | Missing |
| Prompt and harness version | Harness versions in Table 5; exact prompt/result provenance incomplete | Missing | Present (pinned harness images: Claude Code 2.1.220, Codex 0.145.0, Nanobot 0.3.0, OpenCode 1.18.8, Goose 1.44.0, OpenClaw `2026.5.26-slim`, Hermes `v2026.7.20`) |
| Sampling | Present (one run per configuration) | Derivable (one run per configuration) | Present (temperature default 1.0; see Inference settings) |
| Concurrency and load | Not specified for published runs | Missing | Present (`--workers` default 4; one runbook example uses 2) |
| Metric definitions | §4.1 defines mean score, R0.8 and full credit | Partial (R0.8 and R1 defined; mean undefined) | Present (case weights, 0.80 threshold, terminal outcomes kept) |
| Measurement method | §4.1 and B.1 describe settings; no immutable result-to-grader link | Partial (200K-token context threshold, 150-turn limit) | Present (per-task `timeout_sec`: 185 tasks at 7,200 s, 44 at 3,600, 17 at 2,400, 28 at 1,800, replaced for all tasks when `--timeout` is set; `--context-window` default 200,000; `--max-agent-turns` default 150) |
| Uncertainty | Appendix C describes paired task bootstrap; dependence audit remains open | Missing | Missing |
| Date of measurement | No exact run dates identified | Missing | Missing |
| Source | Present | Present (cites paper tables 4, 7, 8 and 11) | Present |
| Known limitations | Appendix A: one run per configuration; bounded model/task coverage | Missing | Partial (rerun policy records deferred reasoning-metadata cases) |

B1 Table 5 identifies harness versions; Appendix B.1 sets temperature 1.0, each model's maximum output, 200K context and 150 turns. These are published-run settings, not the repository's 32768-token default. Immutable model snapshots and the result-to-grader revision remain missing, so G1 still fails. Appendix C reports task-bootstrap intervals and grouped splits; that does not resolve shared-source dependence or independently establish G3.

### Conditional noise sensitivity (Estimate; not G3 evidence)

These calculations illustrate an independent-task scenario, not an uncertainty estimate for any published result. Assume independent Bernoulli task outcomes within each harness, independent harness means, a common full-credit probability p, a known task count n, and a normal approximation. Then SE = sqrt(p(1 − p)/n), and the SE of a two-harness difference is SE × √2. The illustrative base case is p = 0.30, motivated by the website's GPT-5.6 Sol and pooled rates; it is not an observed probability for Qwen or GLM. All table values are percentage points. The nominal 1.96 × SE threshold and approximate MDE = 2.8 × SE (80% power, two-sided 5%) apply only under these assumptions. They are neither measured confidence intervals nor gate verdicts.

| Tasks per cell (n) | SE | SE of difference | z ≥ 1.96 floor | MDE |
| --- | --- | --- | --- | --- |
| 274 (general suite, one run) | 2.77 | 3.92 | 7.7 points | 11.0 points |
| 106 (v1 suite) | 4.45 | 6.29 | 12.3 points | 17.6 points |
| 26 (multimodal suite) | 8.99 | 12.7 | 24.9 points | 35.6 points |

Conditional sensitivity at n = 274: the nominal pairwise threshold is 8.4 points at p = 0.5 (maximum Bernoulli variance within this scenario), 6.7 at p = 0.2 and 5.0 at p = 0.1. If the metric is a mean of independent task scores bounded from 0 to 100, its per-task SD is at most 50 and the same 8.4-point pairwise threshold follows under independent harness means. Neither bound applies under arbitrary task clustering or to an unidentified metric/suite.

For a best-to-worst range across seven independent, equal-variance, approximately normal harness means, the illustrative 95% critical range uses q ≈ 4.17: 4.17 × 2.77 ≈ 11.5 points (12.6 at p = 0.5). The expected null range is about 2.70 × 2.77 ≈ 7.5 points. This is a conditional normal-range calculation, not a bound for paired or clustered results. Harness selection and unequal variances require their own treatment.

With one run per task, task heterogeneity and run-to-run variation cannot be separated. Aggregate rates do not identify paired covariance or shared-source cluster dependence. Pairing can change the difference SE in either direction; clustering can invalidate the independent-task thresholds entirely. B5's 2.2-to-6.0-point shifts and B4's up-to-3.05 clustering factor concern other benchmarks; neither supplies a correction factor or bound for Harness Bench. No finite threshold derived here establishes G3 for any published gap. Per-task results, metric/suite identities and a justified dependence/selection analysis are required. **Every published performance claim below is unknown on G3**, independently of its G1 failure.

### Claims ledger

Figures were originally transcribed from B2 on 2026-10-16. Direct B1 recheck on 2026-10-17 maps general-task gaps to Table 2, sensitivity to Table 9 and selection gains to Table 10. Evidence grade: Vendor claim, except the derived row. Capability scope: agentic workflow tasks in Harness Bench's six task categories only. Use B1's explicit general-task scope for those mapped rows; do not pool multimodal results. Confidence: Low for every harness-effect conclusion.

| Claim as published | Metric and gap | G1 | G2 | G3 outcome and conditional sensitivity | G4 | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| GPT-5.6 Sol: mean score SD 1.93 across harnesses, full-credit range 9.12 | Divergence claim | Fail | Pass | Unknown: 9.12 is below the illustrative 11.5-point range threshold only under the independent-means scenario; paired/clustered uncertainty is unavailable | Divergence is the claim | Not established; observed spread has no valid uncertainty estimate |
| Per-model harness choice adds 2.53 to 2.73 points of held-out full credit; mean moves within ±0.14 | Selection gain averaged over models | Fail | Pass | Unknown: B1 Table 10 reports grouped five-fold selection repeated 20 times; this audit lacks result-level evidence for its dependence/selection check, so the single-pair floor does not apply | Divergence is the claim | Not established |
| Harness gaps of 5.0 to 9.5 points within nine models | General-task mean-score range (B1 Table 2) | Fail | Pass | Unknown: dependence-adjusted uncertainty is missing; 9.5 exceeds 8.4 only in the conditional n = 274 pairwise scenario | Unknown | Not established |
| Qwen3.8-27B harness gap of 39.2 points | General-task mean-score range (B1 Table 2) | Fail (locally hosted; snapshot and quantization unknown) | Pass | Unknown: paired/clustered errors remain unavailable for this audit; 39.2 exceeds 8.4 and 12.6 only if the corresponding independent-task/means scenario applies | Unknown | Not established at G1 or G3; largest transcribed gap, general-task mean-score scope identified |
| Both GLM-5.3 variants: 13.5-point full-credit gap | General-task full-credit ranges, 13.50 for each variant (B1 Table 9) | Fail | Pass if the pair is two harnesses | Unknown: paired/clustered errors remain unavailable for this audit; 13.5 exceeds 12.6 only in the conditional n = 274 seven-harness scenario | Unknown | Not established at G1 or G3 |
| GPT-5.6 Sol: Nanobot costs 2.97 × OpenClaw at 24.82% vs 31.02% full credit | General-task full credit, 6.2; illustrative z ≈ 1.6 only at n = 274, p = 0.30 with independent tasks/means | Fail | Pass | Unknown: paired covariance, run variation and shared-source dependence are unavailable | Pass on the published aggregates: B1 Table 7 also gives mean scores 66.49 vs 73.08 in the same direction | Full-credit gap not established; the cost ratio is a separate vendor claim |
| Pooled harness profile: OpenCode first on mean (66.3), OpenClaw first on full credit (27.1%), Codex 65.3 / 23.8% vs Goose 62.0 / 26.1% | Ranking by metric, pooled general and multimodal configuration–task evaluations (B1 Table 4) | Fail | Fail (pooled over models and suites, not a fixed-model one-factor comparison) | Unknown: gaps are 0.1 to 3.3 points and pooled attempts share tasks across models | Divergence is the claim | Hypothesis, not established: the orders differ, but the reversals are small and untested |
| Derived (Estimate): 20,454 = 274 × 7 × 10 + 26 × 7 × 7, so k = 1 | Runs per configuration | Not applicable | Not applicable | Not applicable | Not applicable | One run per configuration, matching the v2 body per #79 |

**B1 scope recheck, 2026-10-18.** The [v2 paper's Table 4](https://arxiv.org/html/2605.27922v2) caption explicitly pools general and multimodal evaluations. Its general-only per-model rows come from Table 7, which supplies both GPT-5.6 Sol mean scores above. These corrections settle the suite label and descriptive G4 direction only; model/grader pins and G3 evidence remain missing. Prior source dates continue to identify the earlier observations.

### Public release and result-manifest recheck (2026-10-18)

This follow-up searched the publisher's current public release surfaces for the missing evaluated model snapshots and result-to-grader bindings. It preserves the earlier B1–B3 access dates and adds this separately dated observation. The [independent review of #204](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/204#pullrequestreview-5561325177) accepted the bounded negative comparability finding and explicitly retained the literal pinning criterion. The search below did not obtain those missing identities.

| Publisher surface | Exact inspected scope | Observation | What it establishes | Remaining limitation |
| --- | --- | --- | --- | --- |
| [arXiv current landing](https://arxiv.org/abs/2605.27922) and [v2 body](https://arxiv.org/html/2605.27922v2) | Submission history and the versioned paper's release links, §4.1 and Appendix B.1 | The latest listed revision is still v2, dated 2026-10-15. The paper links its GitHub repository and project website for code/data | No newer paper revision was found at this read; the recorded harness versions and published generation settings remain identifiable | Model marketing names and a versioned paper do not identify evaluated provider snapshots, local weight/quantization revisions or the grader that produced a table |
| [Repository refs](https://github.com/Qihoo360/harness-bench/branches), [releases](https://github.com/Qihoo360/harness-bench/releases) and [pinned tree](https://github.com/Qihoo360/harness-bench/tree/b8d89634c6f445fcc68ceb6744a59bef6cdf4863) | Git head/tag refs, public releases API and the complete recursive tree | The sole advertised branch is `main` at `b8d89634c6f445fcc68ceb6744a59bef6cdf4863`; tag enumeration and public releases are empty. The tree response contains 10,834 entries and is not truncated | The inspected publisher repository has not advanced beyond the already pinned source | This is a bounded public read, not evidence that private runs or separately shared artifacts do not exist |
| [Current catalog](https://github.com/Qihoo360/harness-bench/blob/b8d89634c6f445fcc68ceb6744a59bef6cdf4863/catalog/CURRENT.json), [release policy](https://github.com/Qihoo360/harness-bench/blob/b8d89634c6f445fcc68ceb6744a59bef6cdf4863/docs/PUBLIC_RELEASE_POLICY.md), [runbook](https://github.com/Qihoo360/harness-bench/blob/b8d89634c6f445fcc68ceb6744a59bef6cdf4863/docs/CPU_DOCKER_GPU_VLLM_RUNBOOK.md) and [summary exporter](https://github.com/Qihoo360/harness-bench/blob/b8d89634c6f445fcc68ceb6744a59bef6cdf4863/tools/export_public_summary.py) | Catalog/release metadata, model-service freezing instructions and public-summary field allowlists; no benchmark tooling was executed | The catalog still points to `standard274.release-v1.lock.json`. The runbook describes freezing model-service identities. The exporter allows fields including `run_id`, `model`, `harness` and `grading`; the policy describes separate public result bundles | The source contains mechanisms for recording and exporting run information | A mechanism or template is not a released instance or an immutable binding between the paper tables and the inspected task/grader code. No such published-run binding was located in these records |
| [Public leaderboard](https://www.harness-bench.ai/leaderboard.html) | HTML and its inline `DATA` initializer, parsed as JSON without executing JavaScript | The initializer contains 70 general and 49 multimodal configuration aggregates. Each configuration has exactly `model`, `harness`, `score`, `r08`, `r1`, `traj_k`, `tokens_k`, `requests`, `cost_usd` and `local_model` | The per-configuration aggregates can be read directly even when the rendered matrix stays at Loading. This resolves a retrieval limitation in the historical B2 observation | Neither the configuration rows nor the remaining initializer contain immutable model/grader identities, run IDs or result-level task/run rows. Readable aggregates do not supply the paired evidence required by G3 |
| [Public data request #2](https://github.com/Qihoo360/harness-bench/issues/2) and [trajectory request #5](https://github.com/Qihoo360/harness-bench/issues/5) | Current issue bodies and all returned comments | The former contains a 2026-06-14 collaborator reply expressing an intention to update, without a linked result bundle; the latter has no reply at this read | These discussions do not supply an additional result-manifest locator | A statement of intended publication is not proof of delivery; this observation does not characterize uninspected or private channels |

Evidence class: primary documentation/source inspection; High confidence for the retrieved refs, field identities and counts at this read, and a bounded negative search for the missing artifact. Existing aggregate values retain their vendor-claim grade. No result was reproduced, no customer/task corpus or private trajectory was collected, and no additional source-use permission is inferred. The paper, website and repository keep the separate #60 rights conditions.

For byte identification of this mutable web observation, the retrieved leaderboard HTML is 59,435 bytes with SHA-256 `7e47c32819319ff105982e50aa57828d597647da11d695d61b0f3ff5b0fe22e0`. The exact JSON object following `const DATA =`, from its opening brace through the end returned by a JSON decoder, has UTF-8 SHA-256 `ea2d80f8ce490992ac63da6fc87fa23df279b467cdda49300b9e8e338239c8ee`. The raw page and aggregate dataset are not committed. These hashes identify inspected bytes; they are neither run attestations nor a redistribution grant.

**Disposition:** keep the first acceptance criterion unchecked. Completion still needs the evaluated provider model snapshots or local model/quantization revisions, and an immutable binding from the cited published runs to their task-content lock, harness/settings tuple and grader revision. Result-level paired task/run records and dependence information remain a separate G3 gap. A later publisher release can answer these questions; the current negative audit cannot substitute for the missing facts or the actual receiving-owner decisions.

### Contamination and task overlap

- **Answers are publicly readable.** Each of the 274 general task packages at the pinned commit ships `tests/` with `cases.yaml`, `ground_truth/`, `reference/` and `test_outcome.py`; multimodal packages were not inspected. This was observed on 2026-10-16. A commit date does not show when a repository became public, so the exposure start date is unknown. A model trained on data collected after the files became public may have seen them.
- **The authors' intent is unclear (hypothesis).** `docs/PUBLIC_RELEASE_POLICY.md` describes the full repository as the collaborators' copy of a private benchmark and keeps tests and ground truth out of public result bundles. Public access to these files may not have been intended.
- **Model exposure is unknown.** No surface gives training cutoffs for the evaluated backends, so exposure is "unknown" for every model.
- **Task sources.** `catalog/task_catalog.csv` classes the 274 general tasks as 212 public workflow adaptations, 42 handcrafted synthetic and 20 adapted synthetic. Source cards say fixtures are synthetic and cite public documentation for the workflows. Multimodal task sources are not in that file and remain unchecked.
- **The authors' own checks.** The repository lists a public-leakage validator among its release checks. This is a process claim, not an exposure measurement.
- **Overlap between the 106 and 300 sets is unknown.** Task IDs are stable while content may be redesigned under the same ID, so an ID match does not prove a content match. Lock files hash the current 274 tasks and earlier 237- and 254-task sets. The v1 task list and its content hashes are not on `main`.

### Mean score versus complete delivery

Each task's cases sum to 1.00 with a pass threshold of 0.80. Core outcomes carry 0.80 and every core case must pass. Timeouts and other terminal outcomes stay in the denominator. Full credit means every scored module passes. Partial credit can raise the mean even when no additional task reaches full credit; it does not imply that none of a task's required work was delivered. The pooled profile is consistent with a distinction between partial and complete delivery, because mean and full-credit orders differ, but it does not establish a causal explanation.

### Replication limits and confidence

- One run per configuration, so run-to-run variance cannot be separated from task sampling. B1 states temperature 1.0 and model-specific maximum output; do not substitute repository defaults for unreported thinking or exact model snapshots.
- No result-level task/run/harness scores were located on the publisher surfaces in the dated public release recheck above, so this audit cannot recompute paired or clustered errors. This does not establish their absence from uninspected or private channels.
- A replication needs paid model endpoints or local GPUs, Docker images, and judge calls on 79 tasks. All are outside the initial pass.
- No repository-wide licence was found for the pinned task/code collection; the website reserves its own rights. The separate v2 paper is CC BY 4.0. [#60's source/material boundary](rights-validation.md) allows attributed paper material under that licence while excluding unlicensed repository tasks, code and trajectories from product reuse.
- Confidence is High for the repository facts at the pinned commit, Medium for website figures as transcriptions of vendor claims, Medium for B1 as directly source-checked, not independently reproduced, and Low for any conclusion about harness effects.

## Protocol and acceptance
- [ ] Pin models harnesses budgets and task versions (desk, partial: task set, content lock, harness images and runner defaults pinned at the repository commit; model snapshots and result-to-pin links missing)
- [ ] Check contamination and task overlap (desk, partial: exposure, multimodal sources and the 106/300 overlap remain unknown)
- [x] Separate mean score from complete delivery (desk only, from published aggregates and the scoring rules)
- [x] Record replication limits and confidence (desk only)
- [ ] Record exact source/version, conditions, failures and confidence. (desk, partial: versions pinned for B3 to B6; B2 is unversioned; B1 v2 was directly re-read on 2026-10-17; model snapshots, provider, hardware, run dates and uncertainty are missing on every surface)
- [ ] Link every significant conclusion to evidence or an explicit hypothesis (desk: conclusions cite H1, F1, G1 to G4 and B1 to B6; pending reviewer confirmation)
- [ ] Obtain affected-owner review and accepted handoff. (#62 → #25, #36, #40 and #41 rows pending; #39 conditional)
- [ ] Repository checks pass; reviewer accepts the evidence before Done (checks below pass; reviewer acceptance pending)

### Replication protocol (prepared, not authorized)

This is a possible future #36 experiment to test F1, outside #62's desk-comparability scope. It requires a permitted task corpus, exact model/grader identity, preregistered margins and statistical design, actual resource availability, agreed result placement and #39 costing. No replication is selected by this desk review; the proposed receiving decision below keeps the missing-evidence finding without starting or pricing a run.

1. Pin repository commit `b8d8963`, verify the content lock with `tools/task_maintenance/verify_task_set_lock.py`, and build the pinned harness images. Use each task's own `timeout_sec` with no `--timeout` override, and record `--context-window`, `--max-agent-turns`, `--max-tokens`, `--thinking` and `--temperature`.
2. Choose one model and two harnesses. The default is GPT-5.6 Sol with OpenClaw versus Nanobot, because the website gives both rates and the cost ratio. Record the provider's model snapshot and date.
3. Fix the judge explicitly, or report a deterministic-only score that excludes judged cases, so the grader is identical on both sides.
4. Run k ≥ 3 at a fixed temperature on all 274 general tasks, or on a pre-registered stratified subset with that limit stated. B6 §5/Table 7 concerns IRT-based estimates, not this stratified-subset protocol; no 12% reversal rate is transferred to this design.
5. Retain result-level task/run/harness outcomes and report paired differences for mean score, full-credit rate and pass^k, plus cost per full-credit task. Predeclare the inference target, shared-source cluster structure, treatment of repeated runs and any harness-selection adjustment with #36; task-only clustering is insufficient if tasks share dependent sources. Apply F1 with the owner's δ and δm and a justified dependence-aware method. No result or confidence interval is supplied by this prepared protocol.

Power caveat: repeating each task three times does not triple the number of independent tasks or clusters. The conditional MDE table is a planning sensitivity only; actual power depends on paired covariance, run variation and shared-source dependence. #36 must review the design before any run is authorized.

The v1 `QualityEvaluationRun` schema is bound to a build, so no website figure fits it. Any real run needs a placement agreed with #36 first.

### Conventions offered to consumers (proposals, not rules)

- **C1 for #41 and #36, offered narrowing:** require the full task lock, model snapshot, harness version, budget, inference settings, grader and run-count tuple before a figure can support a comparable quality claim. A research note may retain an attributed historical publisher figure with its exact metric/suite/date and visible missing-pin limitations; that does not make it verified, comparable or usable for ranking. Statistical support remains a separate G3 requirement.
- **C2 for #25:** agent-framework evidence names the paired model, budget and task version. Harnesses are candidates, not a ranking.
- **C3 for #36:** evaluation-suite notes record grader identity and the budget tuple before any result attaches. Candidate `metric_names`: `mean_score`, `full_credit_rate`, `threshold_rate_0.8`, `pass_pow_k`, `cost_per_full_credit`. For delivery-style workloads, show full-credit rate with cost before mean score.
- **Finding for #40:** v1's `spec_model` has no benchmark or quality field, and `spec_evaluation_suite` has only `metric_names`, `mode`, `gate_on_deployment` and `dataset_refs`. Any display rule therefore needs a field proposal through #40, not a new rule-template entry.

### Evidence-policy boundary

The adopted [#41 interim policy, PR #75 review 5550616927 §3](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75#pullrequestreview-5550616927), distinguishes checked primary documentation from independently reproduced evidence; [PR #88 review 5554964868](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/88#pullrequestreview-5554964868) confirms that distinction. Eligible documentation may support a constraint pass labelled unverified; that does not supply missing statistical evidence for G3. Version-pinned facts retain their original scope/access dates; website figures remain as-of 2026-10-16 vendor claims. B1 v2 and B6 v1 were re-read on 2026-10-17; no independent experiment was run. Only short paraphrases and links are retained; task/result reuse remains subject to #41/#60 review. C1–C3 and the gates are proposals for receiving-owner review; final rules or contract changes require central versioned #40 review.

## Next action
Review the bounded decisions and live criterion map below at this PR's immutable head. Preserve the source corrections already delivered through #83/#189, all missing model/grader/result provenance and G3 limitations, and the prior explicitly withheld #36/#39 receipt. This follow-up requests actual receiving-owner dispositions on the proposals; it does not reinterpret that prior review as acceptance or require a paid experiment to answer the desk-comparability question.

## Evidence

| ID | Publisher and URL | Access date | Version / region | Evidence grade | Capability scope | Confidence | Limitations / reuse terms | sources.json |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B1 | Harness-Bench authors / arXiv, [v2 landing](https://arxiv.org/abs/2605.27922v2) and [v2 HTML](https://arxiv.org/html/2605.27922v2) | 2026-10-17 (v2 body directly; historical landing via #79) | Revision 2026-10-15; region not applicable | Primary documentation (release metadata); Vendor claim (experiment results, not independently reproduced) | Harness Bench agentic tasks | Medium | Landing metadata and body disagree. Versioned body directly source-checked; landing observation remains historical. Paper HTML shows CC BY 4.0; its paper material and separate repository task/result artifacts have different rights scopes under #60. | `src-harness-bench` (supporting URL, unversioned) |
| B2 | Harness Bench Team, [website](https://www.harness-bench.ai/) and [leaderboard](https://www.harness-bench.ai/leaderboard.html) | 2026-10-16 | Unversioned; region not applicable | Vendor claim | Harness Bench agentic tasks | Medium (as transcription) | No run dates, model snapshots, software versions or variance. Per-model matrix did not render. "All rights reserved". | `src-harness-bench` |
| B3 | Qihoo360, [Harness-Bench repository](https://github.com/Qihoo360/harness-bench/tree/b8d89634c6f445fcc68ceb6744a59bef6cdf4863): [CURRENT.json](https://github.com/Qihoo360/harness-bench/blob/b8d89634c6f445fcc68ceb6744a59bef6cdf4863/catalog/CURRENT.json), [scoring](https://github.com/Qihoo360/harness-bench/blob/b8d89634c6f445fcc68ceb6744a59bef6cdf4863/docs/EVALUATION_AND_SCORING.md), [semantic judge](https://github.com/Qihoo360/harness-bench/blob/b8d89634c6f445fcc68ceb6744a59bef6cdf4863/src/harnessbench/grading/semantic_judge.py), [task catalog](https://github.com/Qihoo360/harness-bench/blob/b8d89634c6f445fcc68ceb6744a59bef6cdf4863/catalog/task_catalog.csv) | 2026-10-16 | Commit `b8d8963`, dated 2026-10-09 | Primary documentation | Harness Bench tooling and task packages | High | Counts made from a read-only, non-shallow clone of `main`; nothing was run. No LICENSE file; visibility is not a reuse grant. | `src-harness-bench-repo-b8d8963` |
| B4 | Miller (Anthropic), [Adding error bars to evals](https://arxiv.org/abs/2411.00640v1) | 2026-10-16 | v1 | Independent measurement | Evaluation statistics method | High | Method paper; clustering factor measured on other benchmarks. | `src-miller-2024` |
| B5 | Bjarnason et al., [repeated SWE-bench Verified trials](https://arxiv.org/abs/2602.07150v1) | 2026-10-16 | v1 | Independent measurement | Run-to-run variance on SWE-bench Verified | Medium | Not measured on Harness Bench. | `src-bjarnason-2026` |
| B6 | Madaan et al., [benchmark variance and IRT](https://arxiv.org/html/2406.10229v1) | 2026-10-17 | v1, §5/Table 7 | Independent measurement | Subsampling ranking stability | Medium | IRT/IRT++ ranking reversals on other benchmarks, not a generic stratified-subset rate. | `src-madaan-2024` |

## Open questions and handoffs

- **#36 (appletechie, PUSHINGSQUARES):** accept or replace the gates, C1 and C3; set δ and δm; decide whether a replication is wanted and where its results live; confirm whether published R1 and R0.8 include judged cases.
- **#25 (CompleteDotTech, Mattycodes69):** accept or narrow C2. No framework ranking is offered.
- **#40 (zwright8, tynamite):** the quality-field finding.
- **#41 (tynamite, PUSHINGSQUARES), with #60:** C1, and rights for Harness Bench tasks and results.
- **#39 (appletechie, PUSHINGSQUARES):** price the replication protocol, only if #36 wants a replication.
- **Harness Bench authors:** immutable model snapshots, result-level task/run/harness scores with metric/suite labels and shared-source cluster metadata, the code, settings and grader behind the published tables, the v1 task list with content hashes, and a license.

Handoff rows #62 → #25, #36, #40, #41 and #39 are in [handoffs.md](handoffs.md) and [handoffs.json](handoffs.json). All are pending; nothing here pre-marks acceptance. #62 and #36 share both assignees, so the #36 acceptance must be recorded explicitly.

## Proposed receiving decisions — 2026-10-18

These concrete decisions remain proposals for the listed consuming owners. Independent integration review may evaluate this partial research for publication, but it does not satisfy live #62's separate receiving-owner requirement. [Review 5556580902](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/83#pullrequestreview-5556580902) explicitly withheld #36/#39 handoff acceptance; that historical boundary remains unchanged. Each new receiving-owner review must name its actual reviewer, head, scope and residual questions. A reviewed merge of this partial package leaves #62 open until its criterion-specific decisions and required owner receipts are recorded and its complete deliverable is reviewed and merged.

**Proposed decision:** accept the desk result that the audited publisher figures do not establish a qualifying harness-effect comparison. Reject their use as a normalized ranking or product quality guarantee. G1 failures and G3 unknowns are the result of the audit; they are not repaired by invented model snapshots, assumed independence, an unrelated benchmark's correction factor or the source's permission to publish its paper. H1 remains untested, not falsified.

| Consumer | Offered research disposition | Retained work / constraint |
| --- | --- | --- |
| #25 Agent Framework | Accept C2: preserve paired model/task/budget identities in framework evidence; use these harnesses as candidates, with no ranking derived from this audit | Any future framework recommendation needs applicable workload evidence; C2 creates no v1 field or universal compatibility rule |
| #36 Evaluation | Accept G1–G4 as conservative desk-screening conventions, C1's historical-claim distinction and C3's grader/budget/metric requirements; accept the current comparisons as unestablished | Select no replication under #62. If #36 later selects one, it must set margins, rights, pins, dependence design, resource and result-placement decisions before execution; no QualityEvaluationRun is created here |
| #40 Shared Contract | Accept the documented missing quality-field/result-binding finding as a versioned contract input | Existing v1 fields and evaluator remain unchanged; a future rule needs approved fields, fixtures and migration rather than an added claim in a template |
| #41 Evidence (using #60's rights policy) | Accept C1's separation of an attributed historical source claim from comparable/independently verified evidence; consume the paper-only source-use boundary | Keep original source dates, exact paper/repository identities, licence notices and missing-provenance flags; rights do not prove quality or authorize repository reuse |
| #39 Cost Estimate | Accept that replication costing is not applicable to this desk result because no experiment is selected | If a future #36 experiment is selected, price its complete actual tuple and permitted resources; the published 2.97× ratio is a publisher claim, not this project's bill or estimate |

## Live #62 criterion map

| Live criterion | Evidence / audit outcome | Decision required before closure |
| --- | --- | --- |
| Pin models harnesses budgets and task versions | Release identities and checklist pin the inspected paper, repository, task locks, harness versions and published settings. The 2026-10-18 public release recheck still did not obtain immutable evaluated model snapshots or result-to-grader links; G1 fails | Keep this literal criterion open until the missing published-run identities and bindings are obtained and accepted. The negative audit records the gap and rejects unsupported comparable claims; it does not satisfy the missing pins |
| Check contamination and task overlap | Pinned public release/task observations distinguish availability, training exposure, shared-source dependence and the missing v1 content lock. Unestablished exposure/overlap remains unknown | Accept the bounded contamination/overlap assessment; no absence-of-contamination or exact v1/v2 overlap is asserted |
| Separate mean score from complete delivery | Claims ledger and scoring section separate mean, full credit and partial credit; Table 4 pooled scope and Table 7 metric direction were corrected in #189 | Accept the descriptive distinction without a causal/statistical effect claim |
| Record replication limits and confidence | G3 limits, conditional sensitivity assumptions, release/metric uncertainty and the possible future protocol are explicit | Accept the limits; a future experiment is outside this issue's stated scope |
| Significant conclusions linked to evidence or hypothesis | B1–B6, H1/F1, G1–G4 and the explicitly labelled sensitivity calculations | Independent reviewer confirms the preserved evidence and the negative conclusion |
| Relevant technical owners review handoffs; unresolved decisions named | Five proposed receiving dispositions above and historical receipts in the shared ledger | Record actual scoped receiving-owner acceptance; generic integration review, general PR approval and the former withholding review do not satisfy this criterion |
| Checks pass; reviewer accepts evidence before Done | Source-correction review and checks are historical; this follow-up needs current PR checks and an exact-head acceptance review | No new local test result, benchmark run, owner receipt or issue completion is pre-asserted |

The criterion review must distinguish obtaining missing publisher facts from deciding that a public claim cannot support a comparison. The negative pin audit is accepted as a bounded technical finding in review 5561325177; the literal pinning criterion remains open because the missing model/grader facts were not obtained. Passing structural checks, publication review and that negative finding do not supply those facts or the separate required receiving-owner receipts.
