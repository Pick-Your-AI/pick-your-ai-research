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

**Receiving interpretation clarified on 2026-10-18:** the historical G2 pass labels below describe a nominal one-factor comparison design. They do not verify that the actual published runs held immutable model, task, budget and grader bindings fixed; missing G1 evidence still prevents that conclusion. G3's 1.96 convention is a proposed desk screen under its stated assumptions, not an automatically adopted runtime or statistical acceptance rule. A future experiment must predeclare the comparison's direction, practical margins and an applicable paired/dependence/selection-aware inference procedure under #36's accepted R1–R15 method. The current unknown G3 cells and conditional sensitivity examples supply none of that missing result evidence.

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
- [x] Link every significant conclusion to evidence or an explicit hypothesis (bounded desk/method review of prepared `1a1324d` recorded below; no fresh audit of every publisher row)
- [x] Obtain affected-owner review and accepted handoff. (five actual scoped receipts are indexed below; missing publisher pins remain open)
- [ ] Repository checks pass; reviewer accepts the evidence before Done (historical checks retain their exact inputs; final amendment checks and canonical delivery remain required)

### Possible future replication protocol (not selected under #62)

This is a possible future #36 experiment to test F1, outside #62's desk-comparability scope. It requires a permitted task corpus, exact model/grader identity, preregistered margins and statistical design, actual resource availability, agreed result placement and #39 costing. The actual 2026-10-18 receiving decision below selects no replication under #62 and retains the missing-evidence finding without starting or pricing a run.

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
- **Finding for #40:** v1's `spec_model` has no benchmark or quality field, and `spec_evaluation_suite` has only `metric_names`, `mode`, `gate_on_deployment` and `dataset_refs`. The existing frozen [`QualityEvaluationRun`](../../contracts/v1/schemas/quality-evaluation-run.schema.json) separately supports real build-bound evaluation observations. Its required build/revision, selected evaluation suite, evaluator/dataset identity, timestamps, sample size and per-measurement threshold/comparator cannot be manufactured from these publisher aggregates. A future external-result/catalog provenance or display-field extension goes through #40 with versioned schema, fixtures and migration; this finding neither removes the existing run artifact nor requires a new schema merely to display a genuinely conforming run. No rule-template prose creates missing contract fields.

### Evidence-policy boundary

The [accepted #41 evidence policy](../T0-configuration/catalog-data-sources.md#evidence-grades-and-labels), retaining the [historical #75 owner decision §3](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75#pullrequestreview-5550616927), distinguishes checked primary documentation from independently reproduced evidence; [PR #88 review 5554964868](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/88#pullrequestreview-5554964868) confirms that distinction. Eligible documentation may support a constraint pass labelled unverified; that does not supply missing statistical evidence for G3. Version-pinned facts retain their original scope/access dates; website figures remain as-of 2026-10-16 vendor claims. B1 v2 and B6 v1 were re-read on 2026-10-17; no independent experiment was run. Only short paraphrases and links are retained; task/result reuse remains subject to #41/#60 review. The actual receipts below accept the precisely bounded documentary C1–C3 and contract inputs; they do not adopt these desk gates as runtime rules or supply new source rights. Final rule or contract extensions require central versioned #40 review.

## Next action
Complete the final amendment checks and canonical delivery, preserving the actual scoped receiving decisions below. The source corrections delivered through #83/#189, missing model/grader/result provenance and G3 limitations, and the prior explicitly withheld #36/#39 receipt retain their original scope. Obtaining missing publisher pins remains a real #62 criterion; a paid experiment is not required to accept this negative desk-comparability finding.

## Evidence

| ID | Publisher and URL | Access date | Version / region | Evidence grade | Capability scope | Confidence | Limitations / reuse terms | sources.json |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B1 | Harness-Bench authors / arXiv, [v2 landing](https://arxiv.org/abs/2605.27922v2) and [v2 HTML](https://arxiv.org/html/2605.27922v2) | 2026-10-17 (v2 body directly; historical landing via #79) | Revision 2026-10-15; region not applicable | Primary documentation (release metadata); Vendor claim (experiment results, not independently reproduced) | Harness Bench agentic tasks | Medium | Landing metadata and body disagree. Versioned body directly source-checked; landing observation remains historical. Paper HTML shows CC BY 4.0; its paper material and separate repository task/result artifacts have different rights scopes under #60. | `src-harness-bench` (supporting URL, unversioned) |
| B2 | Harness Bench Team, [website](https://www.harness-bench.ai/) and [leaderboard](https://www.harness-bench.ai/leaderboard.html) | 2026-10-16 | Unversioned; region not applicable | Vendor claim | Harness Bench agentic tasks | Medium (as transcription) | No run dates, model snapshots, software versions or variance. Per-model matrix did not render. "All rights reserved". | `src-harness-bench` |
| B3 | Qihoo360, [Harness-Bench repository](https://github.com/Qihoo360/harness-bench/tree/b8d89634c6f445fcc68ceb6744a59bef6cdf4863): [CURRENT.json](https://github.com/Qihoo360/harness-bench/blob/b8d89634c6f445fcc68ceb6744a59bef6cdf4863/catalog/CURRENT.json), [scoring](https://github.com/Qihoo360/harness-bench/blob/b8d89634c6f445fcc68ceb6744a59bef6cdf4863/docs/EVALUATION_AND_SCORING.md), [semantic judge](https://github.com/Qihoo360/harness-bench/blob/b8d89634c6f445fcc68ceb6744a59bef6cdf4863/src/harnessbench/grading/semantic_judge.py), [task catalog](https://github.com/Qihoo360/harness-bench/blob/b8d89634c6f445fcc68ceb6744a59bef6cdf4863/catalog/task_catalog.csv) | 2026-10-16 | Commit `b8d8963`, dated 2026-10-09 | Primary documentation | Harness Bench tooling and task packages | High | Counts made from a read-only, non-shallow clone of `main`; nothing was run. No LICENSE file; visibility is not a reuse grant. | `src-harness-bench-repo-b8d8963` |
| B4 | Miller (Anthropic), [Adding error bars to evals](https://arxiv.org/abs/2411.00640v1) | 2026-10-16 | v1 | Independent measurement | Evaluation statistics method | High | Method paper; clustering factor measured on other benchmarks. | `src-miller-2024` |
| B5 | Bjarnason et al., [repeated SWE-bench Verified trials](https://arxiv.org/abs/2602.07150v1) | 2026-10-16 | v1 | Independent measurement | Run-to-run variance on SWE-bench Verified | Medium | Not measured on Harness Bench. | `src-bjarnason-2026` |
| B6 | Madaan et al., [benchmark variance and IRT](https://arxiv.org/html/2406.10229v1) | 2026-10-17 | v1, §5/Table 7 | Independent measurement | Subsampling ranking stability | Medium | IRT/IRT++ ranking reversals on other benchmarks, not a generic stratified-subset rate. | `src-madaan-2024` |

## Remaining questions and receiving dispositions

- **#36 (appletechie, PUSHINGSQUARES):** bounded desk/C1/C3 intake is accepted below, with no replication selected under #62. Any later experiment needs its own margins, procedure, result placement and resources; published R1/R0.8 judged-case composition remains unresolved.
- **#25 (CompleteDotTech, Mattycodes69):** C2 was actually accepted at its earlier pinned input. No framework ranking is offered.
- **#40 (zwright8, tynamite):** the external-result/catalog binding gap is received; no extension or frozen field change is adopted.
- **#41 (tynamite, PUSHINGSQUARES), with #60:** the claim/evidence distinction is received under the accepted material/use boundary; no new task/code/result permission is supplied.
- **#39 (appletechie, PUSHINGSQUARES):** replication costing is not applicable because no experiment is selected, not a zero-cost estimate. A later selected experiment needs separate complete costing.
- **Harness Bench authors:** immutable model snapshots, result-level task/run/harness scores with metric/suite labels and shared-source cluster metadata, the code, settings and grader behind the published tables, the v1 task list with content hashes, and a license.

The five handoffs are indexed in [handoffs.md](handoffs.md) and [handoffs.json](handoffs.json) with the actual reviews below. These are truthful dated engineering dispositions under the user's delegation, not replies attributed to absent coassignees or general PR approval substituted for a receiving decision.

## Prepared receiving proposal at `1a1324d` — 2026-10-18

The table preserves the concrete proposal reviewed at prepared `1a1324d`; the separately dated receipts below state exactly what was accepted. [Review 5556580902](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/83#pullrequestreview-5556580902) explicitly withheld #36/#39 handoff acceptance and remains historical. Later actual decisions do not rewrite its reviewer, date or scope. A reviewed merge still leaves #62 open while its literal publisher-pinning criterion remains unmet.

**Proposed decision:** accept the desk result that the audited publisher figures do not establish a qualifying harness-effect comparison. Reject their use as a normalized ranking or product quality guarantee. G1 failures and G3 unknowns are the result of the audit; they are not repaired by invented model snapshots, assumed independence, an unrelated benchmark's correction factor or the source's permission to publish its paper. H1 remains untested, not falsified.

| Consumer | Offered research disposition | Retained work / constraint |
| --- | --- | --- |
| #25 Agent Framework | Accept C2: preserve paired model/task/budget identities in framework evidence; use these harnesses as candidates, with no ranking derived from this audit | Any future framework recommendation needs applicable workload evidence; C2 creates no v1 field or universal compatibility rule |
| #36 Evaluation | Accept G1–G4 as bounded desk-screening proposals with the explicit nominal-G2/conditional-G3 limits above, C1's historical-claim distinction and C3's grader/budget/metric requirements; accept the current comparisons as unestablished | Select no replication under #62. If #36 later selects one, it must set margins, rights, pins, dependence design, resource and result-placement decisions before execution; no QualityEvaluationRun or runtime gate is created here |
| #40 Shared Contract | Accept the narrow external-result/catalog provenance and binding gap as a versioned contract input, preserving existing QualityEvaluationRun support for real conforming observations | Existing v1 files and evaluator remain unchanged; a future extension needs approved fields, fixtures and migration rather than an added claim in a template. Missing aggregate-to-build/run identities are not guessed |
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
| Relevant technical owners review handoffs; unresolved decisions named | Five actual scoped receiving dispositions below, preserving original and later inputs separately | Completed for the offered documentary inputs; no absent coassignee reply, runtime gate, new source-use grant or missing publisher fact is inferred |
| Checks pass; reviewer accepts evidence before Done | Source-correction review and checks are historical; this follow-up needs current PR checks and an exact-head acceptance review | No new local test result, benchmark run, owner receipt or issue completion is pre-asserted |

The criterion review distinguishes obtaining missing publisher facts from deciding that a public claim cannot support a comparison. The negative pin audit was accepted as a bounded finding in review 5561325177, and the later actual receiving decisions are recorded next. The literal pinning criterion remains open because the missing model/grader facts were not obtained. Structural checks and publication do not supply those facts.

## Actual technical receiving decisions — 2026-10-18

The original [#62 → #25 receipt 6251565503](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/25#issuecomment-6251565503), created **15:16:43Z**, accepts C2 at main `be60732a1353f9d4efab9d1a4c5fbf7627d49abf`, benchmark blob `1ab917cda860cabfce5d2280475613fd1ae11f61` and framework blob `37a1a29b27a8c619a22048399f4a6dd9488486d3`. It is indexed once. That actual assignee review does not retrospectively cover the later gate/contract clarification.

The coordinating in-session engineer's [actual four-scope receipt 6253421648](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/62#issuecomment-6253421648), created **18:17:20Z**, reviewed prepared local `1a1324d064139efecb4830fe5e2b793efec81d3b`, tree `139a0db010896b67f121208a2a68a41cc5489d59`, benchmark blob `5f6d1aedcfd3cef90877b5f321ad181638cbb34d`, on accepted parent `745e58704262aa7b0c755794f820ec1372b24395`. The reviewer read the complete correction, relevant adopted methods and actual frozen schemas under delegated project authority, without a fresh publisher/source-rights audit or experiment. Normal publication and checks were still ahead at the time of that receipt.

| Consumer | Actual received scope | Limit |
| --- | --- | --- |
| #25 | C2 configured evidence identity and harness candidates, under the original 15:16:43Z receipt | No ranking, new benchmark execution or other-assignee reply |
| #36 | Negative desk comparability finding and C1/C3 under R1–R15; nominal G2 and conditional G3 stay explicit | No measured quality, causal effect, runtime/deployment gate or fabricated evaluation run; a later experiment needs a valid predeclared procedure |
| #39 | Replication costing is not applicable to the desk result | No experiment is selected; not applicable is not zero cost, and 2.97× remains a publisher claim, not a bill or rate |
| #40 | External-result/catalog provenance and binding gap, preserving conforming build-bound QualityEvaluationRun support | No invented required fields or frozen change; a future extension needs versioned schema, fixtures and migration |
| #41 | Dated claim, comparable evidence and reproduced evidence remain distinct under accepted #60 material/use policy | Paper permission is not task/code/result permission or proof of statistical quality; no fresh licence or integration grant |

**Adopted engineering decision: no replication under #62.** A future #36 experiment is separate work with its actual protocol, rights, resources and result placement. H1 remains untested, not falsified. Missing immutable publisher model snapshots and result-to-grader bindings keep #62 open. These receipts accept the offered technical inputs; they do not supply final-amendment validation, Project-field QA or canonical delivery.

## Contamination and task-overlap continuation — 2026-10-18

This is a new source inspection under [coordination receipt 6256574606](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/62#issuecomment-6256574606), after the earlier receiving decisions. It resolves the earlier *uninspected multimodal metadata* limitation at the same publisher revision. The preceding 47,499 bytes, including the original checklists, source dates and five receiving scopes, are retained unchanged; none of those historical reviews is relabelled as a review of this continuation. The first live criterion still lacks evaluated-model and published-run bindings.

### Inputs and method

The publisher's main ref was directly read at `b8d89634c6f445fcc68ceb6744a59bef6cdf4863`. Its [complete recursive tree](https://api.github.com/repos/Qihoo360/harness-bench/git/trees/b8d89634c6f445fcc68ceb6744a59bef6cdf4863?recursive=1) contained **10,834 entries**, with `truncated: false`. The read-only input set comprised all **26 `task.yaml` files and 26 `design.md` files** under [the pinned multimodal directory](https://github.com/Qihoo360/harness-bench/tree/b8d89634c6f445fcc68ceb6744a59bef6cdf4863/multimodal-tasks), the four locks below, the general CSV, both multimodal READMEs, the suite's `multimodal26.yaml` and `release.yaml` manifests, the release-policy note and the lock-verifier source: **63 exact files**. Four initial reads preceded a 59-file bulk read at **23:38:09–23:38:17Z**; those times identify that bulk read, not every input. The two empty archive manifests were read separately later on the same date, bringing the inspected metadata total to **65 files**.

For every retrieved file, its UTF-8 byte length and Git blob SHA-1 were independently recomputed against the pinned tree entry. The initial 63-file local capture is 2,334,935 bytes with SHA-256 `6621dd972ad96e9188ffae0b1ec5ca6378bb7bf2f3196df1b02811ad0b9b0ac5`; the two archive records are separate. These checks identify the bytes inspected. The raw capture, task descriptions, answers and reference implementations are not added to this repository.

The lock comparison reads unique JSON object keys, checks the declared task count against the distinct task-ID keys, checks both digest fields' syntax, then compares sets and the two declared digests at each shared ID. It does **not** recompute task-content locks from complete task packages. The [current verifier source](https://github.com/Qihoo360/harness-bench/blob/b8d89634c6f445fcc68ceb6744a59bef6cdf4863/tools/task_maintenance/verify_task_set_lock.py) was read, not executed. No publisher Python, Docker image, model, grader, browser scenario or benchmark was run.

### Available release locks: identity overlap and declared hash agreement

All four records declare schema version 1 and the same hash-policy names: `runner_v1_excludes_reference_cache_and_llm_rubric` for definitions and `snapshot_v1_includes_hidden_files_excludes_cache_and_llm_rubric` for complete packages. Equal policy labels do not prove which implementation produced an older lock or that the old package bytes were retained.

| Inspected lock at the pinned publisher commit | Declared tasks | Exact Git blob |
| --- | ---: | --- |
| [standard237.lock.json](https://github.com/Qihoo360/harness-bench/blob/b8d89634c6f445fcc68ceb6744a59bef6cdf4863/catalog/standard237.lock.json) | 237 | `74776584da46b7141d9c192282eda659d14d1fb2` |
| [standard254.lock.json](https://github.com/Qihoo360/harness-bench/blob/b8d89634c6f445fcc68ceb6744a59bef6cdf4863/catalog/standard254.lock.json) | 254 | `2df5aa5e5551f9f2e5c9f3c9441e3df803fb02c6` |
| [standard274.release-v1.lock.json](https://github.com/Qihoo360/harness-bench/blob/b8d89634c6f445fcc68ceb6744a59bef6cdf4863/catalog/standard274.release-v1.lock.json) | 274 | `83a81164f60617d9ffe5c1df2155b45254fbc98d` |
| [multimodal26.lock.json](https://github.com/Qihoo360/harness-bench/blob/b8d89634c6f445fcc68ceb6744a59bef6cdf4863/suites/multimodal26/catalog/multimodal26.lock.json) | 26 | `b22201fee9deaa62c77c386ce3f1387fdefb56dd` |

The multimodal lock declares task-ID SHA-256 `5764149e9f2a01d882aa53bab2f441249334a1a1eeaa45ce6d69e0b3a5074fb4` and manifest SHA-256 `d0a37bb3e4dc6550a6599b013d7677e53630d44fa5cd39bd93dbb60641018342`. The inspected [multimodal26.yaml](https://github.com/Qihoo360/harness-bench/blob/b8d89634c6f445fcc68ceb6744a59bef6cdf4863/suites/multimodal26/catalog/multimodal26.yaml) has the latter exact byte hash. These identify this available release, not the inputs of a published model run.

| Left / right lock | Shared full task IDs | Left only | Right only | Shared IDs with equal declared definition hash | Shared IDs with equal declared complete-package hash |
| --- | ---: | ---: | ---: | ---: | ---: |
| 237 / 254 general | 237 | 0 | 17 | 237 | 237 |
| 254 / 274 general | 254 | 0 | 20 | 0 | 0 |
| 237 / 274 general | 237 | 0 | 37 | 0 | 0 |
| 274 general / 26 multimodal | 0 | 274 | 26 | 0 | 0 |

Thus the 254/274 records disagree on **both declared digests for all 254 shared IDs**. A comparison cannot assume that those records differ only by adding 20 tasks. This is a demonstrated difference in the lock declarations; the audit has not established the particular task edits, reproduced the old hashing process, or matched either lock to a published result. The 237 matching declarations in the 237/254 pair are likewise not a repeated-run observation. No equal declared definition or package digest was found between the general 274 and multimodal 26 locks, including when IDs were ignored; that still does not prove semantic independence.

The current [general archive manifest](https://github.com/Qihoo360/harness-bench/blob/b8d89634c6f445fcc68ceb6744a59bef6cdf4863/catalog/archive0.yaml) and [multimodal archive manifest](https://github.com/Qihoo360/harness-bench/blob/b8d89634c6f445fcc68ceb6744a59bef6cdf4863/suites/multimodal26/catalog/archive0.yaml) both declare zero tasks and empty ID lists. The general manifest says older packages remain in Git history; that statement does not supply the original 106-task membership/content lock. This pass did not inspect a historical 106-task package collection. Its exact overlap with either later suite remains **unknown**. The numeric prefix of a single task name, or the locally reused 001–026 prefixes, is not a task-set identity.

### Multimodal source and selection metadata

Every inspected multimodal YAML declares `provenance.origin: handcrafted_synthetic`, `real_user_log_derived: false`, a single source label FE-201 through FE-226, and `difficulty: hard`. Its full task ID matches exactly one of the 26 lock entries. These are publisher declarations, not independently verified origin, training-rights or leakage attestations. None of the FE labels occurs in the general CSV's source-label set; label disjointness does not establish semantic or statistical independence.

The following map covers every inspected YAML/design pair. Paths are `multimodal-tasks/<task ID>/task.yaml` and `design.md` at the immutable commit above. “Pending” records an explicit pending human-validation statement in that design note; absence of that statement in another note is not proof of completed review.

| Full task ID | Declared source label | Design-note scope inspected |
| --- | --- | --- |
| 001-creator-revenue-dashboard | FE-201 | Synthetic source/design card; human validation pending |
| 002-studio-task-board | FE-202 | Synthetic source/design card; human validation pending |
| 003-pet-care-game | FE-203 | Synthetic source/design card; human validation pending |
| 004-incident-command-console | FE-204 | Synthetic source/design card; human validation pending |
| 005-research-lab-site | FE-205 | Synthetic source/design card; human validation pending |
| 006-appointment-finder-ui | FE-206 | Synthetic source/design card; human validation pending |
| 007-budget-planning-workspace | FE-207 | Synthetic source/design card; human validation pending |
| 008-media-timeline-editor | FE-208 | Replacement-prototype interaction design |
| 009-course-builder-app | FE-209 | Replacement-prototype interaction design |
| 010-support-ticket-router | FE-210 | Synthetic source/design card; human validation pending |
| 011-local-data-explorer | FE-211 | Synthetic source/design card; human validation pending |
| 012-policy-diff-viewer | FE-212 | Synthetic source/design card; human validation pending |
| 013-kanban-build-repair | FE-213 | Replacement-prototype interaction design |
| 014-accessibility-retrofit | FE-214 | Replacement-prototype interaction design |
| 015-responsive-redesign | FE-215 | Replacement-prototype interaction design |
| 016-feature-flag-admin | FE-216 | Synthetic source/design card; human validation pending |
| 017-travel-itinerary-planner | FE-217 | Replacement-prototype interaction design |
| 018-scientific-simulation-controls | FE-218 | Synthetic source/design card; human validation pending |
| 019-portfolio-reference-rebuild | FE-219 | Synthetic source/design card; human validation pending |
| 020-form-builder-validation | FE-220 | Replacement-prototype interaction design |
| 021-choropleth-map-selection | FE-221 | Synthetic image task; answer-bearing visual facts in design text |
| 022-waveform-audio-cue-editor | FE-222 | Synthetic image task; answer-bearing visual facts in design text |
| 023-spreadsheet-grid-formula | FE-223 | Synthetic image task; answer-bearing visual facts in design text |
| 024-image-pair-diff-annotation | FE-224 | Synthetic image task; answer-bearing visual facts in design text |
| 025-network-graph-explorer | FE-225 | Synthetic image task; answer-bearing visual facts in design text |
| 026-wysiwyg-print-preview | FE-226 | Synthetic image task; answer-bearing visual facts in design text |

The counts are **13 explicit pending design cards, seven replacement-prototype notes and six image-task notes**. They describe the notes inspected, not validated benchmark strata. In particular, the same-commit [multimodal README's difficulty table](https://github.com/Qihoo360/harness-bench/blob/b8d89634c6f445fcc68ceb6744a59bef6cdf4863/multimodal-tasks/README.md#difficulty-distribution) says **four easy, nine medium and 13 hard**, while all 26 YAMLs say hard. This discrepancy remains unresolved; neither representation is adopted here as an empirically validated difficulty classification. A later sampling design must specify its actual selection fields and resolve or disclose the conflict.

### Shared sources and public answer-bearing material

The independently read [general task CSV](https://github.com/Qihoo360/harness-bench/blob/b8d89634c6f445fcc68ceb6744a59bef6cdf4863/catalog/task_catalog.csv), Git blob `ce7e067da4fb820953b8ccfd5be1a8703ad13d27`, contains 274 unique IDs matching the current general lock. Its origin counts remain **212 public-workflow adaptations, 42 handcrafted synthetic and 20 adapted synthetic**. Splitting `source_ids` on the literal `|` separator, discarding empty tokens and counting each label at most once per task yields **320 distinct labels, 67 labels used by multiple tasks, and a maximum of 31 tasks for SQLITE-TRANSACTIONS**. Reused documentation/workflow labels are concrete leads for a dependence audit. They are not measured covariance, validated clusters, independent sample counts or proof of contamination; distinct labels can still describe related tasks.

The public tree includes `tests/cases.yaml`, `tests/test_outcome.py`, both `tests/ground_truth/frontend_contract.json` and `ground_truth.json`, and `tests/reference/web/src/App.tsx` under **all 26 multimodal packages**. This is an exact path-presence observation; those oracle/reference file bodies were not separately fetched or exercised in this pass. More directly, the six inspected design notes for 021–026 expose answer-bearing visual facts in plain text. This note records that exposure surface without copying the answers. The [README's vision-gated description](https://github.com/Qihoo360/harness-bench/blob/b8d89634c6f445fcc68ceb6744a59bef6cdf4863/multimodal-tasks/README.md#vision-gated-tasks-021-026) concerns which facts are available in the evaluated workspace's PNG versus hidden data. The separate [release policy](https://github.com/Qihoo360/harness-bench/blob/b8d89634c6f445fcc68ceb6744a59bef6cdf4863/docs/PUBLIC_RELEASE_POLICY.md) distinguishes the complete collaborator repository from allowlisted result bundles and evaluated-agent inputs. Neither process description establishes that a particular evaluated backend never encountered the public design material.

**Exposure remains unknown for every evaluated model.** This read establishes public availability of the inspected material on this date, not its first public date, ingestion into a training corpus, a provider's training cutoff, a model's access during a published run, or a measured leakage effect. No clean-contamination verdict, compromised-result verdict or corrected benchmark score follows. Public source availability and runtime workspace isolation answer different questions.

### Current research disposition and remaining work

This continuation supplies the previously missing multimodal source-card inspection and concrete comparisons among the four available locks. Under [the #62 prompt's contamination/overlap scope](../../prompts/market/issue-062.md), the offered result is a bounded desk assessment of available overlap/exposure evidence and explicit unverifiable limits. The original 106-task content, actual model exposure and result-level dependence remain unknown; unknown is a documented audit result, not an absence claim. The new source/arithmetic findings require their own independent review and normal current-source validation/delivery before the live contamination/overlap criterion is reconciled.

The first live criterion remains **unmet**: no immutable evaluated provider/model or local weight/quantization identity, published-run-to-task/harness/settings binding, or published-result-to-grader revision was obtained. The separately required paired task/run outcomes and dependence information for G3 also remain unavailable. Current task/source metadata cannot supply these facts. The adopted **no replication under #62** decision, the original five technical receiving scopes and #41/#60's distinct paper versus repository material/use boundaries remain unchanged. This continuation creates no quality record, ranking, runtime gate, source-use permission, paid experiment or whole-issue completion.
