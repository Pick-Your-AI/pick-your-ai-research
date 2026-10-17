# MR-09: Validate benchmark comparability and harness effects

Issue: [#62](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/62). Live assignees (2026-10-16): @appletechie and @PUSHINGSQUARES. Status: desk validation drafted; no benchmark run; owner review pending. Readiness: Ready. Last researched: 2026-10-16. Live Project fields are authoritative; this note does not change them.

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
| arXiv full HTML, v2 | Revision 2026-10-15; recorded by #79 on 2026-10-16 | 300 = 274 general + 26 multimodal | 20,454 model/harness/task combinations; one run per configuration (§4.1) | Not re-read for this note | HTML shows CC BY 4.0 for the paper | B1 |
| Website | Unversioned "Diagnostic Benchmark 2026"; accessed 2026-10-16 | 300 = 274 + 26 | 20,454 = 274 × 7 × 10 + 26 × 7 × 7 | Hidden oracles on final artifacts; "No LLM judge in scoring" | "All rights reserved" | B2 |
| Repository | Commit `b8d89634c6f445fcc68ceb6744a59bef6cdf4863`, dated 2026-10-09, "Update Harness-Bench 3.0 benchmark"; inspected 2026-10-16 | 274 packages in `tasks/` + 26 in `multimodal-tasks/`; general content lock `standard274.release-v1.lock.json` | No results in Git; public result bundles are exported separately | Deterministic oracles, plus a bounded LLM fallback on 79 general tasks (see below) | No LICENSE file; CITATION.cff only | B3 |

For re-identification if links change, the general lock records `task_ids_sha256` `sha256:8cb63ccd4df67b2c9c829b6e598296635013f1a31c5c9ff05e768508b9fed4e7` and `task_set_manifest_sha256` `sha256:3a667df15143fa223659f05c137eff6df0d2e1cbbbf571390d6425eaece2b956`. Public history starts on 2026-10-09 although the v1 paper is from May 2026, so earlier history was probably replaced (inference). A later force-push could break the commit links; these hashes would still identify the task set.

The v2 landing-page and full-text figures are taken from #79's record; this pass could not reopen arXiv because the request was rate-limited. The public `main` branch holds a single commit, dated 2026-10-09; other branches and tags were not checked. The task contents behind the May 2026 v1 paper therefore cannot be retrieved or hashed from `main`.

The 26 multimodal tasks ran on only 7 of the 10 backends (26 × 7 × 7). The website does not name the three excluded backends or say whether its pooled and per-model figures mix the two suites. Until that is known, pooled and model-to-model comparisons fail G2.

**Grader conflict.** At the pinned commit, 79 of the 274 general tasks declare `semantic_judge` with `score_role: bounded_case_fallback`, `default_model: agent` and a `max_fallback_weight` between 0.06 and 0.25 (median 0.10). The judge code caps that weight at 0.25 and says the deterministic oracle stays authoritative for structure, numbers and safety. With `default_model: agent`, the judge is the evaluated model unless a task overrides it. This contradicts the website's "No LLM judge in scoring". Whether the published results used this code is unknown.

Two consequences follow. For a harness comparison at one model, the judge is the same on both sides, so G2 can still pass. For a model comparison, the grader changes with the model, so G2 fails unless the judge is fixed or judged cases are excluded.

### Comparability checklist

The fields are the 15 minimum-evidence items in PR #74's [`prompts/T6.md`](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/5910bcca98e4064c16ee77b77a338c8ac4c99bc3/prompts/T6.md), an unmerged proposal at commit `5910bcc` used here as a checklist, not as evidence. The #36 owner may replace the list. "Present" means the surface states the field; it does not mean the field is verified. Repository cells describe its tooling defaults, not the settings of the published runs.

| Field | arXiv v2 body (via #79) | Website | Repository `b8d8963` |
| --- | --- | --- | --- |
| Evaluation identifier | Present (paper ID and version) | Missing (no version) | Present (commit; lock file) |
| Task/dataset and version | Present (300) | Present (300), unversioned | Present (274 + 26, content locks) |
| Model and version | Not checked | Missing (marketing names, no snapshot or date) | Missing (user-supplied) |
| Provider or runtime | Not checked | Missing; Gemma-4-31B and Qwen3.8-27B noted as locally hosted with no API cost (quantization and hardware not stated) | Missing (user-supplied endpoint) |
| Inference settings | Not checked | Missing | Present as runner defaults (temperature 1.0, `--thinking high`, `--max-tokens 32768`) |
| Hardware or hosting | Not checked | Missing | Missing |
| Prompt and harness version | Not checked | Missing | Present (pinned harness images: Claude Code 2.1.220, Codex 0.145.0, Nanobot 0.3.0, OpenCode 1.18.8, Goose 1.44.0, OpenClaw `2026.5.26-slim`, Hermes `v2026.7.20`) |
| Sampling | Present (one run per configuration) | Derivable (one run per configuration) | Present (temperature default 1.0; see Inference settings) |
| Concurrency and load | Not checked | Missing | Present (`--workers` default 4; one runbook example uses 2) |
| Metric definitions | Not checked | Partial (R0.8 and R1 defined; mean undefined) | Present (case weights, 0.80 threshold, terminal outcomes kept) |
| Measurement method | Present (budgets stated, per #79) | Partial (200K-token context threshold, 150-turn limit) | Present (per-task `timeout_sec`: 185 tasks at 7,200 s, 44 at 3,600, 17 at 2,400, 28 at 1,800, replaced for all tasks when `--timeout` is set; `--context-window` default 200,000; `--max-agent-turns` default 150) |
| Uncertainty | Not checked | Missing | Missing |
| Date of measurement | Not checked | Missing | Missing |
| Source | Present | Present (cites paper tables 4, 7, 8 and 11) | Present |
| Known limitations | Not checked | Missing | Partial (rerun policy records deferred reasoning-metadata cases) |

Backends named on the website pages read: GPT-5.6 Sol, two GLM-5.3 variants, Qwen3.8-27B and Gemma-4-31B. The per-model matrix did not render, so the other five are not transcribed. No snapshot, provider or date is given for any of them.

The decisive gap is the link between published results and pinned inputs. The repository pins harness images, task content and runner defaults, but no surface states which model snapshot, harness pin, settings and grader code produced the published numbers. Every published claim below therefore fails G1.

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

All figures are from the website (B2), accessed 2026-10-16, unversioned. The website cites paper Tables 4, 7, 8 and 11 for these results as a group and does not say which table backs each claim; no row has been checked against B1. Evidence grade: Vendor claim, except the derived row. Capability scope: agentic workflow tasks in Harness Bench's six task categories only. The website does not say which suite each figure covers. Confidence: Low for every harness-effect conclusion.

| Claim as published | Metric and gap | G1 | G2 | G3 outcome and conditional sensitivity | G4 | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| GPT-5.6 Sol: mean score SD 1.93 across harnesses, full-credit range 9.12 | Divergence claim | Fail | Pass | Unknown: 9.12 is below the illustrative 11.5-point range threshold only under the independent-means scenario; paired/clustered uncertainty is unavailable | Divergence is the claim | Not established; observed spread has no valid uncertainty estimate |
| Per-model harness choice adds 2.53 to 2.73 points of held-out full credit; mean moves within ±0.14 | Selection gain averaged over models | Fail | Pass | Unknown: split size and SE are not published, so the single-pair floor does not apply | Divergence is the claim | Not established |
| Harness gaps of 5.0 to 9.5 points within nine models | Metric not stated; likely best-to-worst | Fail | Pass | Unknown: metric, suite and dependence are missing; 9.5 exceeds 8.4 only in the conditional n = 274 pairwise scenario | Unknown | Not established |
| Qwen3.8-27B harness gap of 39.2 points | Metric not stated | Fail (locally hosted; snapshot and quantization unknown) | Pass | Unknown: metric, suite and paired/clustered errors are missing; 39.2 exceeds 8.4 and 12.6 only if the corresponding independent-task/means scenario applies | Unknown | Not established at G1 or G3; largest transcribed gap, metric/suite unidentified |
| Both GLM-5.3 variants: 13.5-point full-credit gap | Full credit, 13.5, two comparisons | Fail | Pass if the pair is two harnesses | Unknown: suite and paired/clustered errors are missing; 13.5 exceeds 12.6 only in the conditional n = 274 seven-harness scenario | Unknown | Not established at G1 or G3 |
| GPT-5.6 Sol: Nanobot costs 2.97 × OpenClaw at 24.82% vs 31.02% full credit | Full credit, 6.2; illustrative z ≈ 1.6 only at n = 274, p = 0.30 with independent tasks/means | Fail | Pass | Unknown: paired covariance, run variation and shared-source dependence are unavailable | Unknown (means not given) | Full-credit gap not established; the cost ratio is a separate vendor claim |
| Pooled harness profile: OpenCode first on mean (66.3), OpenClaw first on full credit (27.1%), Codex 65.3 / 23.8% vs Goose 62.0 / 26.1% | Ranking by metric | Fail | Fail (pooled over models, possibly across both suites) | Unknown: gaps are 0.1 to 3.3 points and pooled attempts share tasks across models | Divergence is the claim | Hypothesis, not established: the orders differ, but the reversals are small and untested |
| Derived (Estimate): 20,454 = 274 × 7 × 10 + 26 × 7 × 7, so k = 1 | Runs per configuration | Not applicable | Not applicable | Not applicable | Not applicable | One run per configuration, matching the v2 body per #79 |

### Contamination and task overlap

- **Answers are publicly readable.** Each of the 274 general task packages at the pinned commit ships `tests/` with `cases.yaml`, `ground_truth/`, `reference/` and `test_outcome.py`; multimodal packages were not inspected. This was observed on 2026-10-16. A commit date does not show when a repository became public, so the exposure start date is unknown. A model trained on data collected after the files became public may have seen them.
- **The authors' intent is unclear (hypothesis).** `docs/PUBLIC_RELEASE_POLICY.md` describes the full repository as the collaborators' copy of a private benchmark and keeps tests and ground truth out of public result bundles. Public access to these files may not have been intended.
- **Model exposure is unknown.** No surface gives training cutoffs for the evaluated backends, so exposure is "unknown" for every model.
- **Task sources.** `catalog/task_catalog.csv` classes the 274 general tasks as 212 public workflow adaptations, 42 handcrafted synthetic and 20 adapted synthetic. Source cards say fixtures are synthetic and cite public documentation for the workflows. Multimodal task sources are not in that file and remain unchecked.
- **The authors' own checks.** The repository lists a public-leakage validator among its release checks. This is a process claim, not an exposure measurement.
- **Overlap between the 106 and 300 sets is unknown.** Task IDs are stable while content may be redesigned under the same ID, so an ID match does not prove a content match. Lock files hash the current 274 tasks and earlier 237- and 254-task sets. The v1 task list and its content hashes are not on `main`.

### Mean score versus complete delivery

Each task's cases sum to 1.00 with a pass threshold of 0.80. Core outcomes carry 0.80 and every core case must pass. Timeouts and other terminal outcomes stay in the denominator. Full credit means every scored module passes. Partial credit therefore raises the mean without any task being delivered. The pooled profile is consistent with this, because mean and full-credit orders differ, but it does not establish it.

### Replication limits and confidence

- One run per configuration, so run-to-run variance cannot be separated from task sampling. The published-run temperature and thinking level are not stated; the repository defaults are 1.0 and "high".
- Per-task results are not public, so paired or clustered errors cannot be recomputed.
- A replication needs paid model endpoints or local GPUs, Docker images, and judge calls on 79 tasks. All are outside the initial pass.
- There is no license for the tasks or code, and the website reserves all rights. Reuse of tasks or results needs #41 and #60 review.
- Confidence is High for the repository facts at the pinned commit, Medium for website figures as transcriptions of vendor claims, Medium for B1 as taken from #79, and Low for any conclusion about harness effects.

## Protocol and acceptance
- [ ] Pin models harnesses budgets and task versions (desk, partial: task set, content lock, harness images and runner defaults pinned at the repository commit; model snapshots and result-to-pin links missing)
- [ ] Check contamination and task overlap (desk, partial: exposure, multimodal sources and the 106/300 overlap remain unknown)
- [x] Separate mean score from complete delivery (desk only, from published aggregates and the scoring rules)
- [x] Record replication limits and confidence (desk only)
- [ ] Record exact source/version, conditions, failures and confidence. (desk, partial: versions pinned for B3 to B6; B2 is unversioned and B1 was taken from #79 and not re-read; model snapshots, provider, hardware, run dates and uncertainty are missing on every surface)
- [ ] Link every significant conclusion to evidence or an explicit hypothesis (desk: conclusions cite H1, F1, G1 to G4 and B1 to B6; pending reviewer confirmation)
- [ ] Obtain affected-owner review and accepted handoff. (#62 → #25, #36, #40 and #41 rows pending; #39 conditional)
- [ ] Repository checks pass; reviewer accepts the evidence before Done (checks below pass; reviewer acceptance pending)

### Replication protocol (prepared, not authorized)

This is the smallest run that could test F1. It needs the owner's approval, a #36 placement decision and #39 pricing before anyone runs it.

1. Pin repository commit `b8d8963`, verify the content lock with `tools/task_maintenance/verify_task_set_lock.py`, and build the pinned harness images. Use each task's own `timeout_sec` with no `--timeout` override, and record `--context-window`, `--max-agent-turns`, `--max-tokens`, `--thinking` and `--temperature`.
2. Choose one model and two harnesses. The default is GPT-5.6 Sol with OpenClaw versus Nanobot, because the website gives both rates and the cost ratio. Record the provider's model snapshot and date.
3. Fix the judge explicitly, or report a deterministic-only score that excludes judged cases, so the grader is identical on both sides.
4. Run k ≥ 3 at a fixed temperature on all 274 general tasks, or on a pre-registered stratified subset with that limit stated. Subsets can flip about 12% of rankings, per the abstract of B6.
5. Retain result-level task/run/harness outcomes and report paired differences for mean score, full-credit rate and pass^k, plus cost per full-credit task. Predeclare the inference target, shared-source cluster structure, treatment of repeated runs and any harness-selection adjustment with #36; task-only clustering is insufficient if tasks share dependent sources. Apply F1 with the owner's δ and δm and a justified dependence-aware method. No result or confidence interval is supplied by this prepared protocol.

Power caveat: repeating each task three times does not triple the number of independent tasks or clusters. The conditional MDE table is a planning sensitivity only; actual power depends on paired covariance, run variation and shared-source dependence. #36 must review the design before any run is authorized.

The v1 `QualityEvaluationRun` schema is bound to a build, so no website figure fits it. Any real run needs a placement agreed with #36 first.

### Conventions offered to consumers (proposals, not rules)

- **C1 for #41 and #36:** show a benchmark figure only with its full tuple of task lock, model snapshot, harness version, budget, inference settings, grader and run count; otherwise show the outcome as unknown.
- **C2 for #25:** agent-framework evidence names the paired model, budget and task version. Harnesses are candidates, not a ranking.
- **C3 for #36:** evaluation-suite notes record grader identity and the budget tuple before any result attaches. Candidate `metric_names`: `mean_score`, `full_credit_rate`, `threshold_rate_0.8`, `pass_pow_k`, `cost_per_full_credit`. For delivery-style workloads, show full-credit rate with cost before mean score.
- **Finding for #40:** v1's `spec_model` has no benchmark or quality field, and `spec_evaluation_suite` has only `metric_names`, `mode`, `gate_on_deployment` and `dataset_refs`. Any display rule therefore needs a field proposal through #40, not a new rule-template entry.

### Evidence-policy boundary

The adopted [#41 interim policy, PR #75 review 5550616927 §3](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75#pullrequestreview-5550616927), distinguishes checked primary documentation from independently reproduced evidence; [PR #88 review 5554964868](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/88#pullrequestreview-5554964868) confirms that distinction. Eligible documentation may support a constraint pass labelled unverified; that does not supply missing statistical evidence for G3. Version-pinned facts retain their original scope/access dates; website figures remain as-of 2026-10-16 vendor claims. No new source access or independent reproduction is claimed. Only short paraphrases and links are retained; task/result reuse remains subject to #41/#60 review. C1–C3 and the gates are proposals for receiving-owner review; final rules or contract changes require central versioned #40 review.

## Next action
For @PUSHINGSQUARES (#36): accept, narrow or reject this desk pass, the gates, and conventions C1 and C3; set δ and δm if a replication is wanted. Ask the Harness Bench authors for the full list of the 10 backends with snapshot, provider or runtime and run date for each (quantization and hardware for the locally hosted ones), result-level task/run/harness scores with metric/suite labels and shared-source cluster metadata, the code, settings and grader behind the published tables, the three backends excluded from the multimodal suite, and the v1 task list with content hashes. Once arXiv is readable, check each ledger figure against B1 Tables 4, 7, 8 and 11. Decide whether a replication is wanted, and if so, its placement with #36 and its pricing with #39.

For @CompleteDotTech (#25): accept, narrow or reject C2.

For @tynamite (#40, #41): review the field finding, C1, and reuse rights for Harness Bench tasks and results.

## Result
No benchmark was run. No paid API output, benchmark artifact, raw dataset or customer content was collected; the repository was inspected read-only. None of the published harness-effect claims passes G1, so none survives yet. Every published performance claim is also unknown on G3. The 39.2-point Qwen3.8-27B and 13.5-point GLM-5.3 deltas remain unverified vendor claims with the source conditions and unknowns above. They exceed illustrative thresholds only under stated independent-task/means assumptions; no statistical significance or confidence interval is established. The published aggregates are consistent with, but do not establish, mean score and full-credit rate ranking harnesses differently. Consumers: #25, #36.

Repository checks on 2026-10-16, Python 3.12.3: both unittest suites (21 and 24 tests), `scripts/validate_research.py`, `scripts/validate_market_research.py` and `git diff --check` pass. They check structure and integrity, not the truth of sources, figures or rights.

## Evidence

| ID | Publisher and URL | Access date | Version / region | Evidence grade | Capability scope | Confidence | Limitations / reuse terms | sources.json |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B1 | Harness-Bench authors / arXiv, [v2 landing](https://arxiv.org/abs/2605.27922v2) and [v2 HTML](https://arxiv.org/html/2605.27922v2) | 2026-10-16 (via #79, F14) | Revision 2026-10-15; region not applicable | Primary documentation (release metadata); Vendor claim (experiment results, not independently reproduced) | Harness Bench agentic tasks | Medium | Landing metadata and body disagree. Not re-read here because of rate limiting. Paper HTML shows CC BY 4.0; tasks and results need separate rights review. | `src-harness-bench` (supporting URL, unversioned) |
| B2 | Harness Bench Team, [website](https://www.harness-bench.ai/) and [leaderboard](https://www.harness-bench.ai/leaderboard.html) | 2026-10-16 | Unversioned; region not applicable | Vendor claim | Harness Bench agentic tasks | Medium (as transcription) | No run dates, model snapshots, software versions or variance. Per-model matrix did not render. "All rights reserved". | `src-harness-bench` |
| B3 | Qihoo360, [Harness-Bench repository](https://github.com/Qihoo360/harness-bench/tree/b8d89634c6f445fcc68ceb6744a59bef6cdf4863): [CURRENT.json](https://github.com/Qihoo360/harness-bench/blob/b8d89634c6f445fcc68ceb6744a59bef6cdf4863/catalog/CURRENT.json), [scoring](https://github.com/Qihoo360/harness-bench/blob/b8d89634c6f445fcc68ceb6744a59bef6cdf4863/docs/EVALUATION_AND_SCORING.md), [semantic judge](https://github.com/Qihoo360/harness-bench/blob/b8d89634c6f445fcc68ceb6744a59bef6cdf4863/src/harnessbench/grading/semantic_judge.py), [task catalog](https://github.com/Qihoo360/harness-bench/blob/b8d89634c6f445fcc68ceb6744a59bef6cdf4863/catalog/task_catalog.csv) | 2026-10-16 | Commit `b8d8963`, dated 2026-10-09 | Primary documentation | Harness Bench tooling and task packages | High | Counts made from a read-only, non-shallow clone of `main`; nothing was run. No LICENSE file; visibility is not a reuse grant. | `src-harness-bench-repo-b8d8963` |
| B4 | Miller (Anthropic), [Adding error bars to evals](https://arxiv.org/abs/2411.00640v1) | 2026-10-16 | v1 | Independent measurement | Evaluation statistics method | High | Method paper; clustering factor measured on other benchmarks. | `src-miller-2024` |
| B5 | Bjarnason et al., [repeated SWE-bench Verified trials](https://arxiv.org/abs/2602.07150v1) | 2026-10-16 | v1 | Independent measurement | Run-to-run variance on SWE-bench Verified | Medium | Not measured on Harness Bench. | `src-bjarnason-2026` |
| B6 | Madaan et al., [benchmark subsampling](https://arxiv.org/abs/2406.10229) | 2026-10-16 | Abstract page only; revision not recorded | Independent measurement | Subsampling ranking stability | Medium | Abstract only, full text not read; measured on other benchmarks. | `src-madaan-2024` |

## Open questions and handoffs

- **#36 (PUSHINGSQUARES):** accept or replace the gates, C1 and C3; set δ and δm; decide whether a replication is wanted and where its results live; confirm whether published R1 and R0.8 include judged cases.
- **#25 (CompleteDotTech):** accept or narrow C2. No framework ranking is offered.
- **#40 (tynamite):** the quality-field finding.
- **#41 (tynamite), with #60:** C1, and rights for Harness Bench tasks and results.
- **#39 (PUSHINGSQUARES):** price the replication protocol, only if #36 wants a replication.
- **Harness Bench authors:** the backend list and snapshots, result-level task/run/harness scores with metric/suite labels and shared-source cluster metadata, the code, settings and grader behind the published tables, the excluded multimodal backends, the v1 task list with content hashes, and a license.

Handoff rows #62 → #25, #36, #40, #41 and #39 are in [handoffs.md](handoffs.md) and [handoffs.json](handoffs.json). All are pending; nothing here pre-marks acceptance. #62 and #36 share an assignee, so the #36 acceptance must be recorded explicitly.
