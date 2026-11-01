# Market Research Program status synthesis (MR-01–MR-12)

Issue: [#47](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/47) (`Refs #47`). Status: **proposed status note for owner review; not accepted evidence.** Compiled 2026-11-01 from `main` at `fef30de` and read-only `gh` readbacks of the issues named below. This note changes no finding, decision, assignee, Project field or acceptance state, and it does not replace [synthesis.md](synthesis.md), which remains #47's deliverable. Live issue state is authoritative where this note and GitHub differ.

## Summary

- Closed/completed (all on 2026-10-18): MR-01–04, MR-06–08 and MR-10–12, plus validation children #60, #64, #65 and #66. Open: **MR-05 (#52, child #63), MR-09 (#56, children #61 and #62)** and program issue #47.
- #52's own seven criteria are all checked; it stays open only because its child #63 (participant work) is unperformed. #56's seven criteria are all checked; it stays open for children #61 and #62.
- Program disposition on record: **NARROW** to the accepted #58 decision-record comparison ([synthesis.md](synthesis.md), [#47 comment 6254035935](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/47#issuecomment-6254035935), delivered via [#389](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/389)). #47 shows 5 of 6 listed criteria evidenced; the first (coordinate twelve workstreams and independent validations) stays open.
- No new research, source retrieval, price capture, experiment or participant contact was performed to write this note.

## Five invalidation gates (state per synthesis.md)

| Gate | State | Owner issue |
| --- | --- | --- |
| Direct substitute | Scoped observation accepted; narrowing adopted (guest-path test only) | #66 (closed) |
| Commercial data rights | Unrestricted reuse not established; ten sources remain Not approved for integration; GPUs.io excluded | #60 (closed) |
| Benchmark comparability | G1 pinning fails; G3 statistical support Unknown | #62 (open) |
| Sizing reproducibility | Whole-runtime calibration Unknown; matched whole-runtime peak pairs = 0 | #61 (open) |
| Paid demand | Unknown; no observed buyer or transaction outcome | #63 (open) |

## Coverage by workstream

"Evidenced" means merged to `main` and recorded in the issue as accepted at a bounded scope. "Open" means a stated criterion or interface that is still unmet.

| MR | Issue (state) | Evidenced (paths; PRs) | Open |
| --- | --- | --- | --- |
| MR-01 Competitive landscape | #48 (closed 2026-10-18) | [competitors.json](competitors.json), [mr01-acceptance.md](mr01-acceptance.md), [sources.json](sources.json); [#67](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/67) initial, [#330](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/330) completion incl. CanIRun.ai intake | Original undocumented seed intent stays unknown; five operational seeds adopted forward |
| MR-02 Feature matrix | #49 (closed) | [features.json](features.json), [mr02-acceptance.md](mr02-acceptance.md); [#357](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/357) | Documentary only. Current matrix intake is 121 Documented / 1,463 Unknown cells overall; Unknown cells imply no capability |
| MR-03 Competitor deep dives | #50 (closed); child #66 (closed) | [competitors/README.md](competitors/README.md) (14 profiles), [substitute-validation.md](substitute-validation.md); [#336](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/336), [#227](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/227), [#304](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/304) | #66 tested one guest path only; runtime feasibility, other tiers and uninspected export paths unknown |
| MR-04 PCPartPicker experience | #51 (closed) | [pcpartpicker.md](pcpartpicker.md); [#404](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/404) | Accepted as hypothesis-only (option c). The literal public-selection walkthrough was never performed; H1–H5 remain hypotheses |
| MR-05 Customer research | **#52 (open)**; child **#63 (open)** | [customers.md](customers.md), [customer-validation.md](customer-validation.md); desk deliverable 2026-10-18, instrument PRs [#457](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/457), [#460](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/460), [#467](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/467), [#477](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/477), [#494](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/494), [#501](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/501) | See [progress-notes-2026-11-01.md](progress-notes-2026-11-01.md). #63 is blocked on operational decisions and unperformed fieldwork; no outreach is drafted or authorised here |
| MR-06 Market size and demand | #53 (closed) | [market-sizing.md](market-sizing.md); [#334](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/334) | Annual sizing is assumed, not measured; no paid-demand, conversion or recurring-use evidence |
| MR-07 Pricing and monetization | #54 (closed); child #64 (closed) | [monetization.md](monetization.md), [pricing-validation.md](pricing-validation.md), [pricing/](../../pricing/); [#326](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/326), [#317](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/317) | Thirteen captured rates and two conditional scenarios are component subtotals, not deployment bills; unpriced transfer meters remain; neither revenue concept is qualified |
| MR-08 Data sources and integration | #55 (closed); child #60 (closed) | [integrations.json](integrations.json), [rights-validation.md](rights-validation.md); [#294](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/294), [#299](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/299), [#82](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/82), [#204](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/204) | All ten rows Not approved for integration; unestablished upstream uses stay unknown and excluded |
| MR-09 Technical feasibility | **#56 (open)**; children **#61, #62 (open)**, #65 (closed) | [technical-feasibility.md](technical-feasibility.md), [sizing-validation.md](sizing-validation.md), [benchmark-validation.md](benchmark-validation.md), [rag-validation.md](rag-validation.md), [measurements/](measurements/), [mr09-acceptance.md](mr09-acceptance.md), [../../evidence/](../../evidence/) (`mr09-*.json`); [#83](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/83), [#213](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/213), [#251](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/251), [#252](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/252), [#332](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/332) | See [progress-notes-2026-11-01.md](progress-notes-2026-11-01.md) and [execution-plan-61-draft.md](execution-plan-61-draft.md) |
| MR-10 Differentiation | #57 (closed) | [differentiation.md](differentiation.md); [#313](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/313) | Original exclusivity claims rejected or narrowed; H3/H4/H5b unproved |
| MR-11 MVP definition | #58 (closed) | [mvp-analysis.md](mvp-analysis.md); [#322](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/322) | Recommendation is for validation only; fit, cost, demand and implementation evidence remain behind their own gates |
| MR-12 Quality, synthesis, handoffs | #59 (closed 2026-10-18) | [handoffs.md](handoffs.md), [handoffs.json](handoffs.json), [risk-register.md](risk-register.md), [audit.json](audit.json); [#371](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/371), [#381](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/381), [#389](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/389), [#404](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/404), [#419](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/419) | Metadata QA complete; Project field values were not newly verified by that delivery |

Catalog and pricing proposals under [catalog/proposals/](../../catalog/proposals/) belong to the T0-T6 workstreams, not to MR evidence; no `catalog/` file is cited as MR evidence above.

## What is left for the program to close

1. #61: three empirical criteria (vary context/cache precision/concurrency; measure peak allocated and reserved memory; report error bounds). Needs authorised hardware. Plan: [execution-plan-61-draft.md](execution-plan-61-draft.md).
2. #62: the literal criterion "Pin models, harnesses, budgets and task versions" stays open until the publisher supplies evaluated model/grader identities and immutable run bindings. No replication is selected.
3. #63: blocked (see progress notes). No recruitment or contact.
4. #47: first criterion plus the program-level close depend on 1-3. Coordinator review of the narrowed comparison itself is a separate, unperformed step.

## Caveats

- Open PRs [#511](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/511), [#513](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/513) (coverage ledger) and [#508](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/508) (OLMoE plan-reader fix) were not read for content or touched; any overlap with this note is unchecked.
- Issue states and closure timestamps come from `gh issue view`, not from Project #2 fields, which were not read.
