# T0: Catalog Data Sources & Freshness

Issue: #41 · Contract: v1 1.0.0 (adopted in PR #44) · Assignees: @tynamite, @PUSHINGSQUARES
Status: partial decision record for review, revision 2 (adopts the interim policy already applied by T1 and T2) · Last updated: 2026-10-17
Deliverable path: `research/T0-configuration/catalog-data-sources.md` · Related: `component-schema-compatibility.md` (#40), `research/market/rights-validation.md` (#60), `research/market/integrations.json` (#55)

This revision turns the interim positions posted in the [#75 review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75#pullrequestreview-5550616927) into #41's record. T1 (#88) and T2 (#75) already apply them, and #60's source decisions are merged. Sections marked **To do (@PUSHINGSQUARES)** follow the split proposed on #41: price-specific freshness, region/currency and price conflicts, next to #39.

## User decision

Where does the builder get component facts and prices, may it reuse them, and how does it keep them current and trustworthy?

## Candidate options

| Option | Description | Assessment |
| --- | --- | --- |
| A. Manual capture only | Researchers paraphrase and cite; no automated retrieval | Safe for rights, but freshness depends on people |
| **B. Per-source policy** (recommended) | Automated retrieval and display only where a source's terms permit it (#60 table); manual capture elsewhere; freshness by class of fact | Matches the rights findings; keeps decisions explicit per source |
| C. Aggregate everything | Ingest aggregators' compiled data | Rejected: several aggregators bar this product category or redistribution (#60) |

## Evidence grades and labels

- **Grades** (from the research method): Primary documentation, Vendor claim, Independent measurement, Estimate. They are graded per claim, not per source: one publisher can provide primary documentation of its terms and vendor claims about its capabilities.
- **Checked:** a claim's provenance was confirmed against the cited primary source on its access date.
- **Verified:** independently reproduced (governance's second source or reproducible test). A rule may pass on checked evidence; the result carries "unverified" until reproduced.
- **Community reports:** trust grades in #81 (`self_reported` to `project_measured`) are informative until CD-8's acceptance policy says otherwise.
- **Comparable benchmark claims:** a benchmark figure is comparable only when its reproducibility tuple is fully pinned (R1–R15 in the T6 evaluation draft, #115). For a one-factor comparison, exactly one independent experimental control differs. Precision/quantization, context limit and chat template within R5 are separate controls. Evidence identity fields (source, measurement date and uncertainty) may differ without becoming experimental controls. A known incomplete protocol or known multiple-control change displayed as comparable is `fail` with an explanatory reason; use `unknown` only when the necessary evidence cannot be determined. Statistical eligibility does not grant reuse rights; apply #60 separately. Protocol identity is encoded under CD-3.
- **Status labels for feature claims:** `Exercised`, `Documented`, `Unsupported`, `Unknown`, as adopted in #67.

## Mapping evidence labels to frozen v1

The research labels above describe the claim's evidence strength. Frozen v1 provenance `verification_status` has `verified`, `user_supplied`, `estimated` and `unverified`; it has no separate `source_checked` value. Existing `verified` entries were admitted under the older workflow's source-check definition. They establish a checked citation only unless linked evidence independently establishes reproduction or corroboration. Never upgrade an existing claim to independently Verified solely because its v1 value is `verified`.

For new source-checked claims without independent corroboration, retain the access date and source in provenance, use `unverified`, and explain the checked claim in the research note. `user_supplied` and `estimated` retain their distinct meanings. Use `verified` for new entries only with linked independent corroboration or reproduction described in the note. Do not mass-relabel historical records; review claim-level evidence when adopting the next-version mapping through #40. The contributor workflow in this PR follows this distinction. No frozen schema or generator is changed.

## Freshness

- **Version-pinned facts don't expire.** Examples: an engine release's support matrix, a hardware SKU's specification, a model card at a revision. They are re-checked when the selected version changes or the source is corrected.
- **Current-state facts carry dates.** Examples: prices, availability, quotas, region lists, terms. They are shown "as of <access date>". No time-to-live is adopted, because there is no evidence yet for a specific interval.
- **Display states:** current (pinned or recently checked), "as of <date>" for current-state facts, unverified, disputed (conflict resolved on the conservative value), unavailable.
- **To do (@PUSHINGSQUARES):** price refresh and invalidation; whether any price class needs a maximum age before it is shown with a warning.

## Conflict resolution

1. **Normalise.** Differences in units, rounding, currency or naming aren't conflicts.
2. **Scope.** Drop evidence whose stated coverage excludes the selection. Among the rest, the most specific coverage wins.
3. **Version and date.** For version-pinned facts, the source for the selected version wins. For current-state facts, the latest effective date wins; older values stay as history.
4. **Authority.**
   - The publisher beats third parties for facts it controls.
   - Within one publisher, a stated requirement or limitation beats a capability listing, and billing or legal pages beat overview pages.
   - For fit and performance, a matching measurement beats an estimate, which beats a vendor claim.
5. **Equal rank.** Numbers of equal rank are decided on the conservative value in the rule's direction, and the result is flagged as disputed.

`unknown` remains only with no eligible evidence, or when equally ranked sources make opposite yes/no claims; those are flagged for a reproducible test. Each conflict is resolved once and recorded with the winning claim, the others and the deciding step. Worked cases:
- vLLM v0.31.0 on Volta: the release's stated CUDA minimum beats its matrix cells (steps 3 and 4), so `fail`.
- vLLM W8A8 on Arm: the CPU page beats the general chart (steps 2 and 4), so `fail`, flagged as disputed (#81).
- Bedrock vs Anthropic output caps for Sonnet 4.6: the route-specific value applies to the Bedrock route (step 2, #88).

**To do (@PUSHINGSQUARES):** pricing-page vs billing-documentation conflicts, and region or currency mismatches.

## Reuse and automated retrieval

- The publisher's own licence or terms decide. Where no grant is found, commercial display and redistribution are `no`. `unclear` is reserved for ambiguous terms.
- Decisions for the 10 shortlisted sources, covering automated retrieval, internal research, commercial display and redistribution, are in [`research/market/rights-validation.md`](../market/rights-validation.md) (#60). Per-source evidence is in [`integrations.json`](../market/integrations.json). Summary:
  - **Usable for display:** models.dev, ModelFit, llmfit, MCP registry metadata, Hugging Face factual identifiers, Harness Bench paper results, and GPUs.io values under its attribution and non-compete conditions.
  - **Not usable without agreement:** BenchLM-owned outputs, Artificial Analysis data (its terms bar model-selection products), and automated OpenRouter collection.
- Research notes may use short factual paraphrases with links. No bulk copying of vendor tables.
- A new source is added by recording its terms URL, a decision per use, update cadence and last-checked date, as `integrations.json` does.

## Change events handed to #42

A saved build is re-evaluated when any of these happen:
- the selected component version changes, or a selected item is deprecated or removed;
- the evidence for a selected tuple changes, is corrected or is retracted;
- the ruleset version or dependency-graph revision changes;
- a current-state fact used by the build changes (price, availability, region, terms);
- a #60 rights decision changes (affected values are hidden in every view, including historical and shared ones);
- the contract version changes (migration per CD-7).

A newer release alone doesn't invalidate a build; it is shown as "newer version available".

## Source inventory

| Category | Typical sources | Access | Notes |
| --- | --- | --- | --- |
| Publisher documentation | Model cards, engine docs, hardware specifications, licences | Manual; versioned URLs or commits where available | Primary documentation; pin revisions |
| Pricing and terms pages | Provider pricing, billing docs, terms of service | Manual; current-state | Dated; region and currency recorded (#39) |
| Registries and open datasets | models.dev, ModelFit dataset, MCP registry, Hugging Face Hub | Automated where #60 says yes | Licence notices retained |
| Benchmark publications | Papers, leaderboards | Manual citation; display per terms | Protocol and version pinned (#36, #62) |
| Community fit reports | LocalScore, LocalMaxxing and others (#81) | Link or import only where terms allow (#81 Q7) | Informative until CD-8 |

## Open questions

| # | Question | Accountable |
| --- | --- | --- |
| Q1 | Maximum age, if any, for price classes before a warning | #41 with #39 (@PUSHINGSQUARES) |
| Q2 | How the evaluator encodes the conflict order and records decisions (CD-3) | #41 with #40 |
| Q3 | Acceptance policy for community evidence (CD-8) | #41 |
| Q4 | Where fit reports live, and under what licence (#81 Q6) | #41 |

## Acceptance criteria coverage

| Criterion (issue #41) | Where | Status |
| --- | --- | --- |
| Source inventory with terms-of-use findings linked to primary documents | Source inventory; #60 table | Partial: 10 sources decided |
| Evidence-grade definitions adopted by #40 | Evidence grades and labels | Proposed; applied by T1 and T2 |
| Freshness and staleness policy | Freshness | Proposed; price detail to do |
| Conflict-resolution rules | Conflict resolution | Proposed; applied by T1 and T2 |
| Change events handed to #42 | Change events | Proposed |
| Deployment modes covered | Applies to all modes; opaque-endpoint evidence per #81 | Proposed |
| Comparison fields with type, unit, evidence | `integrations.json` fields | Partial |
| Rules in #40's format | Conflict order feeds #40's outcome semantics | Proposed |
| Primary sources with access dates | #60 table and `integrations.json` (2026-10-16) | Met for the 10 sources |
| Handoffs confirmed | — | Open |
| Open questions with owners | Open questions | Met |
| Decision record merged | — | Open |
