# T0: Catalog Data Sources & Freshness

Issue: #41 · Contract: v1 1.0.0 (adopted in PR #44) · Assignees: @tynamite, @PUSHINGSQUARES
Status: partial decision record for review, revision 3 (price-policy supplement proposed) · Last updated: 2026-10-18
Deliverable path: `research/T0-configuration/catalog-data-sources.md` · Related: `component-schema-compatibility.md` (#40), `research/market/rights-validation.md` (#60), `research/market/integrations.json` (#55)

This revision turns the interim positions posted in the [#75 review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75#pullrequestreview-5550616927) into #41's record. T1 (#88) and T2 (#75) already apply them, and #60's source decisions are merged. The price-policy supplement below supplies a concrete proposal for the recorded @PUSHINGSQUARES #41/#39 review scope: price-specific freshness, region/currency and price conflicts. It does not claim that owner’s acceptance or change assignments.

## User decision

Where does the builder get component facts and prices, may it reuse them, and how does it keep them current and trustworthy?

## Candidate options

| Option | Description | Assessment |
| --- | --- | --- |
| A. Manual capture only | Researchers paraphrase and cite; no automated retrieval | Rights still require per-source review; freshness depends on people |
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
- **Price supplement (proposed):** no invented maximum age; use explicit validity intervals, dated snapshots, source checks before a current recommendation, and the event/eligibility rules below.

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

## Price eligibility, refresh and conflicts (proposal for #39/#41)

This section specifies project behavior, not new vendor claims or rights. It applies across serving modes and builds on the [#64 dated rate/scenario audit](../market/pricing-validation.md), the [v1 pricing gates](../../contracts/v1/docs/PRICING_AND_GATES.md) and the [pricebook schema](../../contracts/v1/schemas/pricebook.schema.json), inspected 2026-10-18. No numerical rate is copied or promoted to a current quote here.

**Eligibility key.** Before choosing a price, match the item/version, provider/offering, meter/unit, billing class, selected region, currency, effective interval and all account/plan/commitment/cache/batch/volume conditions. A missing condition is unknown, not a wildcard. A publisher-explicit global rate can match a regional selection within that stated scope; an unstated region cannot be relabeled global.

**Currency and region.** Use the build's explicitly selected currency and each offering's evidenced region. With no currency answer, request the answer and keep the aggregate unknown; do not silently default to USD. With differing currencies, show separate qualified component lines; do not sum or infer an exchange rate. A future conversion policy needs a dated FX source, direction, rounding and treatment of fees/tax through #39/#40. No country or account region is inferred from the researcher’s location.

**Freshness and invalidation.** Prices always show capture/access date and effective period. A request for a current recommendation requires rechecking the source and its applicable scope. A new rate/pricebook revision, source correction, rights change, expired explicit validity interval, changed region/currency/plan, or changed workload/meter quantity triggers recomputation. Elapsed time alone does not fabricate a price change or a maximum-age cutoff. A declared `valid_until` is an actual eligibility condition, unlike an arbitrary refresh TTL. Preserve historical calculations with their pins and dates where rights permit; they are not current quotes.

**Failed refresh.** If the source cannot be fetched or no longer establishes the rate, retain only the permitted dated historical observation and mark current eligibility unresolved. Do not erase a historical measurement, silently substitute a newer SKU, or claim an old rate is current. If rights cease to permit display, hide affected values even in historical/shared views under #60/#42.

**Conflict precedence.** Normalize compatible units first, retaining raw units and precision; GB and GiB are not interchangeable. Resolve scope before recency: an ineligible regional/account rate cannot override the selected offering’s rate merely because it was checked later. Within the same eligible scope, compare effective dates, then governing billing documentation against an overview. Capture date is not effective date. Keep superseded values as history rather than averaging rates.

Only equal-rank, same-currency, same-meter, same-conditions numeric rates may use the conservative higher cost as a disputed estimate for a budget upper bound. Keep every source and the deciding step. A disputed estimate is not the provider’s confirmed invoice amount. Non-numeric eligibility conflicts or unmatched scopes remain unknown; they cannot be made safe by taking the maximum of unrelated prices. Missing cost components retain partial/unknown coverage under #39 rather than becoming zero.

### Synthetic decision cases

These cases are policy examples, not market evidence or executable rules.

| Case | Required interpretation |
| --- | --- |
| Same offering/meter/region/currency; new effective rate | New rate applies only in its effective interval; historical calculation retains the old revision |
| Source checked today but rate expired yesterday | Not eligible for a current quote; current price unknown until a valid rate is obtained |
| Older region-A billing page versus newer region-B overview | Region-B rate is ineligible for region A; do not compare their amounts |
| Currency absent, or USD and EUR component lines | No invented currency/FX; aggregate unknown, qualified separate lines visible |
| Two equal-rank eligible rates 2 and 3 synthetic currency units per identical meter | Budget upper-bound estimate uses 3 and is flagged disputed; actual charge remains unconfirmed |
| Documented zero-priced meter versus missing meter | Zero only for the documented eligible meter; missing meter remains uncovered |
| Source fetch fails without evidence of withdrawal | Historical dated value may remain where permitted; current recommendation cannot claim freshness |
| Explicit global rate, selected region within documented scope | Region matching may pass; remaining account/plan/meter conditions still require evidence |

**Handoff package.** #39 receives scope matching, explicit-currency/FX boundaries, conservative disputed estimates and uncovered-meter semantics; #42 receives expired-validity and failed-refresh states alongside the already accepted change-event interface. @PUSHINGSQUARES/@tynamite retain #41 acceptance; #39 co-assignees and #42 owners must record their scoped disposition. The supplement completes the draft policy detail, not those acceptance receipts.

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

## Typed source-policy inventory (proposal)

This dictionary separates **existing inventory fields** in [`research/market/integrations.json`](../market/integrations.json) from **claim-level policy dimensions** described above. It describes research records and existing decisions, not a new CatalogItem schema or a permission grant. Inspected 2026-10-18 against the merged inventory and this policy. Final wire locations and any new types remain proposals through #40; prices retain the frozen Pricebook schema until a reviewed successor exists.

| Inventory field | Type / unit | Evidence and unknown handling |
| --- | --- | --- |
| `product_id`, `source_ids` | String identifier; list of source identifiers | Resolve the product/source records; an identifier is not proof that a particular claim was read |
| `investigation_rank` | Integer ordering value | Research sequencing only; not a quality, permission or confidence score |
| `access`, `rights`, `maintenance`, `next_action` | Text | Describe documented access, scoped terms and remaining work; prose cannot silently become executable entitlement predicates |
| `review_owner`, `consumer_issue`, `status` | Owner string, integer issue number, status text | Routing metadata; live assignees govern ownership. A terms grant does not imply production integration approval |
| `access_date`, `last_checked` | Calendar date strings, YYYY-MM-DD | Record actual inspection; neither is a price's effective date or a promise that evidence remains current |
| `terms_urls` | List of public source URL strings | Identify the governing terms/license and scope; public access alone grants no reuse rights |
| `reuse_permitted` | Object keyed by automated_retrieval, internal_research, display, redistribution | Keep each use separate; a display grant does not authorize automated collection |
| Each reuse decision | `value` yes/no/unclear plus `conditions` and `basis` text | Conditions remain binding. No applicable grant → no for commercial display/redistribution; ambiguous terms → unclear. A missing row never becomes yes |
| `update_cadence` | Text description | Publisher/source observation, not an invented refresh TTL |
| `rights_evidence_grade` | Research grade text | Primary documentation identifies the source class; it does not certify independent reproduction or replace claim-level provenance |

The inventory stores per-source decisions; detailed claim eligibility additionally needs the following **conceptual fields**, without asserting a final JSON shape:

| Policy dimension | Known-value type / unit | Required scope / unresolved handling |
| --- | --- | --- |
| Claim identity and value | Identifier, typed scalar/list/object and explicit unit | Preserve raw value/unit plus normalized value and conversion method. No conversion between incompatible quantities |
| Source and version binding | URL/reference, publisher, version/revision and capture date | Match exact artifact/offering/route and conditions. Missing binding remains unresolved, not latest-by-default |
| Evidence grade and verification | Research grade, frozen-v1 provenance status, links to independent support when claimed | Apply the checked/verified mapping above; historical verified labels do not by themselves establish independent support |
| Support-list completeness | Explicit completeness assertion tied to the applicable source/version | Omitted member of a researched subset is unknown, not unsupported. Wire representation belongs to CD-3 |
| Freshness class | Version-pinned fact or current-state fact | Pinned facts do not expire arbitrarily; current recommendations require source rechecking and show dates |
| Price eligibility | Exact item/version/provider, meter/unit, region, currency, effective interval and account/plan/commitment/cache/batch/volume conditions | No missing condition is a wildcard; unknown currency is not USD; effective date differs from capture date |
| Price amount | Decimal with currency and per-meter unit | Zero only when documented in eligible scope. Missing meter remains uncovered. Currency conversion is not authorized by this policy |
| Rights eligibility | Per-use disposition, conditions, governing reference and decision date | Rights and statistical comparability are separate gates. Hide affected values when the applicable rights decision requires it |
| Conflict resolution | Competing claim references, selected interpretation, deciding step and disputed flag | Normalize → scope → version/date → authority → conservative equal-rank numeric value; nonnumeric ties stay unknown. Preserve discarded claims as permitted evidence history |
| Change events | Event identity/type, affected selected tuple and referenced revisions | Re-evaluate affected selections under #42; a new unrelated release alone does not invalidate a build |

### Existing receipts and remaining review

- [@tynamite's T4 evidence-interface acceptance](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/41#issuecomment-6242626857) covers checked-versus-verified labels, dated hosted-service snapshots, actually read rendered documentation, and the per-source rights inventory. It is not acceptance by every consumer.
- [The #114 review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/114#pullrequestreview-5558408384) confirms the original #41 change-event handoff as #42 co-assignee/#40/#41 owner. The later price supplement's expired-validity and failed-refresh semantics still need their own #39/#42 scoped dispositions.
- #40's merged outcome semantics use the evidence/conflict distinction. This does not resolve CD-3's final representation or every co-owner response. @PUSHINGSQUARES retains #41's price-policy acceptance scope; #39 owns meters and aggregation. No receipt here grants source rights beyond its recorded source/use conditions.

## Open questions

| # | Question | Accountable |
| --- | --- | --- |
| Q1 | Review the proposed no-arbitrary-TTL policy, explicit validity checks and refresh-before-current-recommendation behavior | #41 with #39 (@PUSHINGSQUARES) |
| Q2 | How the evaluator encodes the conflict order and records decisions (CD-3) | #41 with #40 |
| Q3 | Acceptance policy for community evidence (CD-8) | #41 |
| Q4 | Where fit reports live, and under what licence (#81 Q6) | #41 |

## Acceptance criteria coverage

| Criterion (issue #41) | Where | Status |
| --- | --- | --- |
| Source inventory with terms-of-use findings linked to primary documents | Source inventory; #60 table | Partial: 10 sources decided |
| Evidence-grade definitions adopted by #40 | Evidence grades and labels | Proposed; applied by T1 and T2 |
| Freshness and staleness policy | Freshness; price eligibility supplement | Concrete proposal with synthetic cases; receiving acceptance pending |
| Conflict-resolution rules | Conflict resolution | Proposed; applied by T1 and T2 |
| Change events handed to #42 | Change events; #114 review receipt | Original handoff confirmed; later price supplement receipt pending |
| Deployment modes covered | Applies to all modes; opaque-endpoint evidence per #81 | Proposed |
| Comparison fields with type, unit, evidence | Typed source-policy inventory; existing `integrations.json` | Research dictionary supplied; new claim wire shapes remain proposals |
| Rules in #40's format | Conflict order feeds #40's outcome semantics | Proposed |
| Primary sources with access dates | #60 table and `integrations.json` (2026-10-16) | Met for the 10 sources |
| Handoffs confirmed | Existing receipts and remaining review | Partial; original #42 change-event and T4 evidence scopes recorded |
| Open questions with owners | Open questions | Met |
| Decision record merged | PR #127; price supplement PR #137 | Merged partial research; receiving acceptance remains separate |
