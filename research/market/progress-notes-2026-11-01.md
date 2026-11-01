# Progress notes: #52, #56, #62 (and #63 blocker)

Refs [#52](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/52), [#56](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/56), [#62](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/62), [#63](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/63). Status: **proposed status notes for owner review; not accepted evidence.** Compiled 2026-11-01 from `main` at `fef30de` and read-only `gh` readbacks. Live issue text, assignees and Project fields are authoritative; this note changes none of them and records no new research. Program context: [program-status-2026-11-01.md](program-status-2026-11-01.md).

## #52 MR-05 Customer Research & Personas (open)

Assignees (live, read 2026-11-01): appletechie, PUSHINGSQUARES.

**Current state.** All seven original criteria are checked. The desk deliverable (ten segments, evidence-qualified JTBD, neutral interview protocol, persona-versus-customer distinction) was completed 2026-10-18 with independent reviews and five bounded technical receiving decisions ([comment 6250471522](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/52#issuecomment-6250471522)). Personas remain desk hypotheses from a self-selected developer sample (Stack Overflow 2026); they supply no demand, rate or willingness-to-pay figure.

**Done.** [customers.md](customers.md); [#67](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/67) initial; parent-completion-gate clarification [#433](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/433); instrument status reconciliation [#494](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/494); interviewer-conflict design and channel-rule limits [#501](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/501) (latest merged change to the customer notes, 2026-10-20).

**Left.** The issue's "Next action" is to maintain the dated desk record as sources change. The parent stays open because its child #63 retains distinct operational work; whether #52 can close independently of #63 is a coordinator decision recorded at [comment 6255561527](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/52#issuecomment-6255561527) (not re-read in full for this note).

## #56 MR-09 Technical Feasibility (open)

Assignees (live, read 2026-11-01): Mattycodes69, appletechie.

**Current state.** All seven #56 criteria are checked at their recorded scope. #56 stays open for two unfinished native children: #61 (three empirical criteria) and #62 (one pinning criterion). #65 (RAG interoperability) is closed.

**Done (merged).**

| Item | PR / path |
| --- | --- |
| Benchmark desk slices | [#83](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/83), [#213](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/213) |
| 15 historical dense CUDA runs (D1-D5 x 3) | [measurements/mr09-D*-r*.json](measurements/), [mr09-results-summary.json](measurements/mr09-results-summary.json) |
| 3 short Granite3.1 GM1 runs | [#251](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/251), [measurements/granite31-2026-10-18](measurements/granite31-2026-10-18) |
| 12 two-byte KV payload component pairs | [#252](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/252) |
| Duplicate-JSON-key parser integrity | [#254](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/254) |
| Prepared total-buffer proposal (execution disabled) | [#259](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/259) |
| Hardware-requirements accounting and cohort guard | [#200](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/200) |
| Receipt-preservation delivery | [#381](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/381) |
| 3 H1 initialization-buffer observations (RTX 5070 Ti, spare capacity) | [#474](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/474), [#476](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/476), [measurements/local-comparison-2026-10-19](measurements/local-comparison-2026-10-19) |
| OLMoE artifact/copy preparation (no weights downloaded) | [#499](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/499), [#502](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/502), [#503](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/503) (M4 cache observations prepared, unexecuted) |
| Native validation receipt type fix | [#514](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/514) (2026-10-29, latest merged commit on `main`) |

**Left.** Whole-runtime peak-allocated estimator pairs remain **zero**. Varied MoE (OLMoE M1-M4), long-context and multi-GPU cells are unexecuted and need authorised hardware. Receiving-owner decisions for #7/#10/#11 are recorded at their bounded scope. Execution plan draft: [execution-plan-61-draft.md](execution-plan-61-draft.md). Open PR [#508](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/508) (OLMoE plan-reader fix) is outside this note and untouched.

## #62 MR-09 Benchmark comparability (open)

Assignees (live, read 2026-11-01): appletechie, PUSHINGSQUARES, itisSomeone.

**Current state.** Four of seven criteria are checked; the unchecked one is "Pin models harnesses budgets and task versions". Gate state per [synthesis.md](synthesis.md): G1 pinning fails, G3 statistical support Unknown. **No replication is selected under #62**, so its experiment cost is not applicable (not zero).

**Done.** [benchmark-validation.md](benchmark-validation.md) via [#83](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/83), [#189](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/189) (pooled-vs-general table scope; mean vs full-credit), [#204](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/204) and [#213](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/213) (public release/result audit, 2026-10-18); five bounded receiving decisions for #25/#36/#39/#40/#41 ([6251565503](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/25#issuecomment-6251565503), [6253421648](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/62#issuecomment-6253421648)); background literature note [benchmark-validation-approaches.md](benchmark-validation-approaches.md) via [#510](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/510) (2026-10-25; proposed background, not accepted evidence).

**Left.** (1) Evaluated model/grader identities and immutable published-run bindings, if the publisher supplies them; accepting the negative audit does not meet the literal criterion. (2) Paired-result and task-overlap inputs for any ranking claim (none exist). (3) Named receiving-owner dispositions beyond the five recorded. (4) Rights: the inspected Harness-Bench repository has no detected repository-wide licence, and its tasks/trajectories are distinct from the separately licensed paper ([rights-validation.md](rights-validation.md)). Next-action owners per the issue: appletechie / PUSHINGSQUARES.

## #63 MR-05 Customer demand and willingness to pay (open, BLOCKED)

Assignees (live, read 2026-11-01): zwright8, appletechie.

**No recruitment, no participant contact and no outreach is drafted or authorised by this note.**

- Blocked on operational decisions. The brief for this note named D-01..D-06; the live issue lists the six **remaining** records as **D-01** (whole-package recruitment/consent disposition), **D-02** (actually permitted channels), **D-06** (actual controller/contact), **D-07** (lawful basis and rights text), **D-09** (private storage, access, deletion/expiry) and **D-16** (actual interviewer and conflict disclosure). The issue records D-03, D-04, D-05, D-08, D-10 and D-13 as selected instrument choices (see [customer-validation.md](customer-validation.md); D-05/D-08/D-10 delivered via [#467](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/467)). The discrepancy between the two lists is flagged for the coordinator; the issue is treated as authoritative.
- D-01 must be recorded before any contact. Participation is selected as deliberately unpaid (D-05), which is not a zero-budget or willingness-to-pay finding.
- Consequence: paid-demand gate stays Unknown.
