# T0: Catalog Data Sources & Freshness

Issue: #41 · Contract: v1 1.0.0 (adopted in PR #44) · Assignees: @tynamite, @PUSHINGSQUARES
Status: decision record for review, revision 7 (eight source-policy receiving decisions recorded; amendment delivery pending) · Last updated: 2026-10-18
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

### Executable price-policy cases

The [test-only prototype](../../tests/price_policy_prototype.py) and
[synthetic cases](../../tests/test_price_policy.py) exercise the proposed
selection order and exclusion boundaries. They make scope-before-recency,
effective-date-before-capture-date, billing authority, disputed upper bounds,
explicit global scope, missing currency/conditions, documented zero, expired
validity, failed refresh and historical display-rights checks executable.
No fixture contains a real provider rate or invokes a source.

The inputs are normalized research facts, not a new Pricebook or Selection wire
format. `valid_for_query` requires prior interpretation of the actual source's
effective interval and boundaries; `refreshed_for_query` requires a successful
source and scope recheck for that request. Neither is inferred from the original
capture date. The rights boolean likewise represents a prior scoped review and
cannot be inferred from a source URL, public availability or a generic licence.
`None` is missing fixture evidence. A known empty condition tuple explicitly
means no further conditions after a complete review; a missing inventory or
missing key cannot match as a wildcard. Units must already share exact semantics;
there is no GB/GiB or FX conversion.

The bounded scope ordering distinguishes an exact region from explicitly global
coverage only. It does not rank partially overlapping region/account/volume
conditions or decide those unresolved wire shapes. Authority cases compare
billing and overview documents from the same publisher; cross-publisher authority
is outside the modeled cohort. An eligible cohort retains
superseded and permitted historical observations with their original identity
and dates; choosing a saved build's historical pin remains separate. Rights
exclusions hide values from that history as well as from a current candidate.
A selected amount is one conditional rate; it does not certify an invoice,
complete cost coverage, measured equivalence or a total build budget.

Run `python -m unittest discover -s tests -p test_price_policy.py -v`.
These cases support review of #41/#39/#40/#42's existing proposal. They do not
adopt its final schema, satisfy pending owner receipts or release an evaluator.

## Reuse and automated retrieval

- The publisher's own licence or terms control the permission basis. Where no applicable grant is established, the project's current intake excludes commercial display and redistribution; unestablished legal scope remains unknown. Ambiguous terms likewise do not prevent a conservative project exclusion or become proof of a legal prohibition.
- Decisions for the 10 shortlisted sources, covering automated retrieval, internal research, commercial display and redistribution, are in [`research/market/rights-validation.md`](../market/rights-validation.md) (#60). Per-source evidence is in [`integrations.json`](../market/integrations.json). Summary:
  - **Conditionally available for display:** models.dev, ModelFit, llmfit, MCP registry metadata, Hugging Face factual identifiers and Harness Bench paper material, within each source's exact material and notice scope. Paper permission does not make a benchmark comparison valid or extend to separately unlicensed repository content.
  - **Not usable without agreement:** BenchLM-owned outputs, Artificial Analysis data (its terms bar model-selection products), and automated OpenRouter collection.
  - **GPUs.io:** [#204's source correction](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/204) is retained; the [current delegated engineering receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/60#issuecomment-6248616771) accepts exclusion from product retrieval/display/export. The [terms](https://gpus.io/en/terms), checked 2026-10-18, retain a broader competing-product restriction even inside a build estimate. A specific permitted-use basis remains unestablished, so the exclusion stands. The receipt accepts this conservative research decision under delegated authority; it supplies no external permission or production eligibility.
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
| Each reuse decision | `value` yes/no/unclear plus `conditions` and `basis` text | Conditions remain binding. An unestablished grant means exclusion from the project's current intake while legal scope can remain unknown; ambiguous terms remain unclear. A missing row never becomes yes |
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
| Q5 | Admit actual jurisdiction identities, containment/disjointness evidence, named-group definitions and provider-region mappings for the CD-9 candidate below | #41 with #9; #37 receives residency results and #40 owns successor-contract adoption |

## Historical acceptance coverage before the completion packet

This table preserves the earlier partial-record assessment. The separately dated
[completion packet](#source-policy-completion-packet-2026-10-18) below distinguishes
actual later receipts from remaining decisions; its current map supersedes these
status descriptions without backdating a review or a source check.

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
| Primary sources with access dates | #60 table and `integrations.json`; initial audit 2026-10-16, bounded recheck in #204 on 2026-10-18 | Source-scoped dates retained; the other seven sources were not rechecked by #204 |
| Handoffs confirmed | Existing receipts and remaining review | Partial; original #42 change-event and T4 evidence scopes recorded |
| Open questions with owners | Open questions | Met |
| Decision record merged | PR #127; price supplement PR #137 | Merged partial research; receiving acceptance remains separate |

## CD-9 jurisdiction and region resolution candidate (2026-10-18)

**Engineering decision for review:** use explicit, pinned location and allowed-set
descriptors, positive containment paths and separately evidenced disjointness.
Never infer a provider's processing or storage jurisdiction from its region name.
Never infer exclusion merely because one jurisdiction is absent from another's
ancestor list. A country-level location may be too coarse for an allowed
subdivision; two named scopes can also overlap. Those cases remain `unknown`
without an adequate containment or disjointness proof.

The [CD-9 register and D-R6 proposal](deployment-mode.md#open-contract-decisions),
[D-R6 assertion and fixed policy](deployment-mode.md#d-r6-residency-covers-processing-and-storage-across-the-data-flows),
[workload residency dictionary](workload-use-case.md#field-dictionary) and
[CD-1 answer-state candidate](component-schema-compatibility.md#cd-1-concrete-answer-encoding-and-normalization-experiment-2026-10-18)
were inspected at accepted main
[`250537e10c674e8d6ba19eb08921fda15511a23b`](https://github.com/Pick-Your-AI/pick-your-ai-research/tree/250537e10c674e8d6ba19eb08921fda15511a23b)
on 2026-10-18. These are primary project requirements and proposed semantics,
not geographic, provider or legal evidence. The policy above continues to govern
source qualification, conflict order, dates, conditions and rights.

### Concrete shape and evidence boundary

The [test-only schema](../../tests/fixtures/jurisdiction-binding.schema.json),
[binding fixture](../../tests/fixtures/jurisdiction-binding.json),
[CD-1 answers](../../tests/fixtures/jurisdiction-answers.json) and
[offline resolver](../../tests/jurisdiction_binding_prototype.py) select the
`x_t0_jurisdiction` / `cd9-0.1` candidate. All fixture identities, provider region
labels and geography are invented. The fixture's Boolean facts and the tests'
explicit eligibility assertions are synthetic inputs, not source approvals.

| Object / field | Candidate type and exact scope | Missing or changing evidence |
| --- | --- | --- |
| `answer_states_sha256` | SHA-256 of the complete original UTF-8 CD-1 sidecar | A byte mismatch is rejected; parsing-equivalent bytes are not substituted |
| `jurisdictions[]` | Distinct identity plus an ordered list of immediate `parent_ids` | Each node's identity, each positive parent edge and complete parent inventory have separate Boolean answers. Unknown referenced nodes remain unresolved; explicit cycles are rejected |
| `groups[]` | Distinct named-group identity plus an ordered list of jurisdiction `member_ids` | A member needs its own eligible assertion. A complete empty group is distinct from missing membership; groups cannot silently recurse through other group identities |
| `disjoint_pairs[]` | Distinct identity and two jurisdiction IDs | An eligible `true` explicitly establishes disjoint scopes. It is symmetric. Self-pairs and duplicate unordered pairs are rejected; absence or `false` supplies no disjointness proof |
| `regions[]` | Distinct mapping ID; exact `provider_id`, `service_id`, `region_id`, `context_id`, processing/storage `dimension`, and jurisdiction list | The context names the specific reviewed conditions; it is not a wildcard. Each mapped location and completeness need separate eligible facts. Identical region labels under different providers or dimensions remain separate |
| `queries[]` | Distinct query ID; `subject_id`, `context_id`, dimension and location references | An explicit query concerns one subject and dimension. Each subject-to-location association and its complete possible-location inventory need separate eligible facts. An empty inventory remains unknown |
| Location reference | Tagged jurisdiction/provider-region ID plus `descriptor_sha256` when known | Missing descriptor, missing pin or different descriptor gives unknown. There is no latest-descriptor fallback |
| Allowed reference | Tagged jurisdiction/group ID plus `descriptor_sha256` when known | Expanding a group or replacing a referenced descriptor cannot reinterpret the old constraint. Its pin must match the selected definition |
| Workload constraint | CD-1 answer at `/workload/residency/processing` or `/workload/residency/storage`: provided `{mode: unconstrained}` or `{mode: restricted, allowed: [...]}` | The restricted list is nonempty. Only eligible, provided `unconstrained` skips that dimension. Unknown, missing, withheld and not-applicable remain unresolved; none is silently unconstrained |

Identifiers are case-sensitive bounded ASCII tokens in this experiment; they are
not a validated ISO registry. Provider/account/route conditions must be encoded
in the admitted context and matched to the actual subject outside this resolver.
The schema caps the scoped experiment at 256 jurisdiction/group/region records,
512 disjoint pairs and 64 queries; it is not a global geographic database format.
Multiple explicit jurisdiction parents are allowed, but the declared graph must
be acyclic even when a query is unconstrained or an edge lacks eligible evidence.
Duplicate IDs, duplicate exact mapping/query scopes, malformed provided values,
ambiguous raw JSON and non-finite values are rejected before evaluation.

Each relationship/completeness answer uses a non-overlapping CD-1 path containing
the SHA-256 of its complete owning descriptor. The descriptor encoding is UTF-8
JSON with sorted object keys, no insignificant whitespace, and original array
order, prefixed with `cd9-0.1` and a newline. Descriptors contain only strings,
arrays and objects. Reordering an inventory therefore needs new scoped keys in
this candidate. Original binding and answer bytes are retained unchanged.
Location references also pin their target descriptors: proving a replacement
mapping's geography does not prove that the subject uses that replacement.

The caller supplies evidence eligibility separately for every exact answer path;
only Boolean `true` admits that fact. False, absent or unresolved eligibility
cannot become a known answer. A source label, matching hash, descriptor name or
complete-list flag establishes neither eligibility nor source rights. The caller
must first apply the existing normalization, scope, version/date and authority
policy. Opposite equally ranked facts must remain unresolved in the CD-1 input.

### Predicate, completeness and disagreement

For each eligible restricted dimension, compare every confirmed possible location
of the requested subject against the allowed alternatives. A possible footprint
is source-qualified scope, not proof that a data transfer actually occurred.
Provider mappings are additionally bound to the query's context and dimension.

- A positive chain from the location to an allowed jurisdiction proves
  containment. It does not require an exhaustive list of every other ancestor.
- If a location is within A, an allowed jurisdiction is within B, and eligible
  evidence establishes A and B are disjoint, that alternative is excluded.
  Name prefixes, different roots, sibling nodes and complete ancestry alone do
  not supply this negative.
- Contradictory containment/disjointness proofs, including two disjoint
  ancestors inside either positive ancestry closure, produce disputed unknown.
  A third common containing ancestor cannot hide an internally contradictory
  location. The result retains the conflicting paths.
- A named group matches when any confirmed member contains the location.
  Other unresolved member results are retained. It excludes the location only
  with eligible complete membership and exclusion by every member. A confirmed
  complete empty group excludes a known location; an incomplete empty group
  stays unknown.
- Any allowed alternative may establish membership; unknown alternatives remain
  visible. Every location must be covered for the subject to pass. The subject
  inventory and each provider mapping need their own eligible completeness
  assertion; an incomplete list cannot establish total residency coverage.
- One proven disallowed location makes the subject result fail while retaining
  other unknown locations and coverage gaps. Otherwise an unresolved required
  fact makes it unknown. Processing and storage return separate results.

The typed result retains query/subject/context/dimension identities, per-location
checks, allowed-alternative and group-member outcomes, proof paths, all read CD-1
answers and their eligibility, and both original input hashes. D-R6 retains fixed
`error` severity and the existing proposed `on_unknown: review`; this candidate
does not adopt the optional stronger block policy reserved for #41. A failed
predicate describes the supplied scope proof, not a legal finding or observed
data-residency incident.

| Synthetic case | Required result |
| --- | --- |
| Local subdivision explicitly within allowed country; other ancestry incomplete | Pass that location |
| Country-level source with only a narrower allowed subdivision | Unknown; coarse source cannot establish placement within or outside the subdivision |
| Two roots with complete ancestry but no disjointness evidence | Unknown |
| Explicit disjoint country scopes inherited through confirmed subdivision paths | Fail that alternative |
| Processing map inside A; same-named storage map in disjoint B | Processing pass and storage fail; no cross-dimension borrowing |
| Positive group member and another unresolved member | Membership passes with unresolved member retained; subject coverage still requires completeness |
| A location within disjoint A and B, both under allowed C | Disputed unknown |
| Fresh replacement provider mapping with the old subject reference pin | Unknown until the exact new subject association is supplied |
| A group adds a jurisdiction while the old workload constraint retains its pin | Unknown for that group reference; no implicit policy expansion |
| Known outside location plus missing destination/coverage | Fail with the unknown rows retained |

### Validation, migration and receiving scope

Run `python -m unittest tests.test_jurisdiction_binding -v`. The 32 focused
methods cover these semantic boundaries, independent processing/storage results,
exact input and descriptor binding, changed eligibility, original-byte retention,
cycles and ambiguous identities. These tests exercise invented facts only.
Repository validation remains a separate integrity check and does not qualify
any actual geography, provider service, source permission or runtime behavior.

There is deliberately no whole-build verdict: queries do not discover omitted
components, logs, backups, tool connections or other data flows. A receiving
adapter must construct and qualify the complete applicable subject inventory,
bind actual build/selection/route revisions and the admitted condition context,
and retain all per-dimension results. A cloud-region mapping cannot replace
provider data terms, actual configuration or processing/storage scope evidence.

This selects a concrete test-only CD-9 shape and resolver. Frozen v1, its
region-string rules and historical results remain unchanged. No ISO dataset,
real group-membership table or provider mapping is introduced. #41 with #9
must admit actual source-specific identities, boundaries, group versions,
mapping dates/conditions and rights; #37 receives scoped residency results.
#40 retains successor schema/reader/ruleset and migration adoption, with #42
receiving exact saved-build pins and changed-evidence handling. The active
CD-2/CD-7 implementation slices and canonical market ledgers are unchanged.
These concrete research mechanics do not close #41/#40 or supply an absent
owner's receiving disposition.

## Source-policy completion packet (2026-10-18)

This appendix is the in-session source-policy engineer's research proposal under
the user's delegated project engineering authority. The reviewed input is research
main [`cae31f324f827cdeb73548b72cafd392dd777dfa`](https://github.com/Pick-Your-AI/pick-your-ai-research/tree/cae31f324f827cdeb73548b72cafd392dd777dfa).
The independently reviewed producer was published without a PR or CI as
[`13b11b7eb9a84af200ea9f0577fcb0e5182a4c46`](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/13b11b7eb9a84af200ea9f0577fcb0e5182a4c46/research/T0-configuration/catalog-data-sources.md),
with blob `c7d36a3c6c5ff305080867ec98763019d5e365bb` and tree
`dc6a13749191a32aff44e21e234ddcd7adf3fda5`. Its separately retained local commit
`b618b96886ad4e4bb661cb0fb2be013a7f3f6698` has that exact tree; both source commits
have the accepted `cae31f324f827cdeb73548b72cafd392dd777dfa` parent. Source-only
publication is not a signed merge or a validation result.

The eight actual delegated receiving decisions below were recorded on
2026-10-18 after independent review of that exact producer and its current
receiving interfaces. They do not attribute replies to absent assignees. This
receipt reconciliation changes no source disposition or policy predicate; the
amendment still requires its own reviewed, validated main delivery.

The scope is a finite initial source-policy catalogue, with an explicit route for
later sources. Individual component research, cost aggregation and unit selection
remain with their existing issues. No new vendor fact, rate, source-use grant,
runtime, prototype, ruleset or frozen-v1 field is introduced. The historical
price and CD-9 experiments above retain their own source pins, execution results
and limits.

### Initial source coverage and evidence identity

The initial shortlist is the ten existing rows in
[`integrations.json`](../market/integrations.json), joined through `source_ids` to
[`sources.json`](../market/sources.json). The source register supplies publisher,
URL, access result, version/date, region, confidence and limitations; integrations
supplies access method, per-use decisions, terms URLs, cadence, last-check date
and review routing. The [typed dictionary](#typed-source-policy-inventory-proposal)
defines their types and distinguishes claim-level fields. A source-wide region
such as “global website” is not the serving or billing region of a rate. Every
price still needs the exact rate-level region, currency, unit and effective/access
dates; an absent applicable field remains unresolved.

| Existing source identity | Candidate research use and exact material boundary |
| --- | --- |
| `src-models-dev` | Provider/model discovery and repository compilation metadata, retaining the repository notice and separate upstream claim/measurement rights |
| `src-modelfit` | The licensed hardware-fit dataset, labelled as its publisher's estimates; dataset, generator/CLI and unverified upstream measurements remain separate |
| `src-llmfit` | Repository code/data discovery with its notice; the seed website's unconfirmed affiliation, model files and actual fit measurements remain separate from that repository licence |
| `src-openrouter` | Manual, limited research citation; the current automated collection and commercial republication exclusions remain |
| `src-mcp-registry` | Registry metadata discovery with source/annotation separation; server code, binaries and execution or security certification are outside that metadata use |
| `src-hugging-face` | Factual repository identifiers and declared metadata with links; cards, weights, datasets and other material require their own applicable basis |
| `src-artificial-analysis` | Manual research citation under the current exclusions; no product data-feed or commercial selection/ranking use is admitted |
| `src-benchlm` | Distinguish publisher-owned service/compiled outputs from separately licensed original measurements and permitted quotations; no display/feed agreement is inferred |
| `src-harness-bench` | Licensed paper material with author/version/notices; separately unlicensed repository tasks, code and trajectories stay excluded |
| `src-gpus-io` | Discovery/terms evidence only for this product; its API retrieval, value display and export remain excluded by the actual project decision |

These are cross-references to the [complete qualified source/use table and
separately dated ten-source check](../market/rights-validation.md#ten-source-material-check-and-modelfit-resolution--2026-10-18),
not new or broader permission determinations. The actual
[#60 → #41 receiving receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/60#issuecomment-6248616771)
accepts this bounded material/use input and current-product exclusions. All ten
integration rows remain **Not approved for integration**. A licence-only recheck
does not advance an API, data-update or measurement observation. The earlier
statement that #204 did not recheck seven sources remains true of that earlier
pass; it does not erase the later ten-source documentary review.

The shortlist is not an exhaustive list of publishers. The following policy
coverage admits research categories while preserving the rule that a source
without an applicable #60 row has no approved automated retrieval, product display
or redistribution. A component note may retain its short source-linked factual
paraphrase and an explicit unknown use decision. Adding a source, different
material or a new use requires a dated source/material/use review; it does not
inherit permission from a discovery catalogue.

| Deployment mode / cross-mode source class | Initial coverage and existing research references | Boundary or reason a category does not apply |
| --- | --- | --- |
| API | Provider documentation, model cards, route/version records and pricing/billing/terms pages in [T1 provider evidence](../T1-model-selection/model-provider.md) and [context evidence](../T1-model-selection/context-window.md#evidence); models.dev and Hugging Face are discovery inputs at the scopes above | A provider-hosted opaque implementation does not supply a local hardware/engine benchmark. Route, model, account, feature and regional eligibility remain claim-specific; direct-provider values are not copied onto another serving route |
| Managed | Exact provider/offering/region, capacity and responsibility records in [hosting](../T2-infrastructure/hosting.md), with separately dated provider price/terms material in [cost evidence](../T6-deployment-operations/cost-estimate.md#evidence) | An advertised region is not current quota/stock, private connectivity or a measured SLO. AWS/Azure price reuse is not silently admitted by the shortlist; the existing #39/#41 questions and per-use exclusions remain |
| Self-hosted | Pinned model/card/licence, [engine-release documentation](../T2-infrastructure/inference-engine.md#evidence), [compute and hardware evidence](../T2-infrastructure/gpu-compute.md), and the qualified ModelFit/llmfit discovery inputs above | Repository licensing does not license the model or dataset. An estimated fit, support listing or published allocation is not an executed workload or available local memory; no cloud account/region is inferred for a local device |
| Benchmark publications, all applicable modes | [Evaluation's protocol/evidence requirements](../T6-deployment-operations/evaluation.md) and the separate Harness paper/repository and BenchLM material decisions | Apply to an actual matching experiment, not automatically every candidate. Documentation, estimates and synthetic mechanics remain distinct from independent measurements; source rights and comparability are separate |
| Community fit and jurisdiction material | The existing [community-evidence question](#open-questions) and [CD-9 candidate](#cd-9-jurisdiction-and-region-resolution-candidate-2026-10-18) define informational and future-admission boundaries | No real community measurement, jurisdiction list, named group or provider mapping is added here. Missing evidence is explicitly unknown; no automatic hardware, geographic, legal or provider-name inference is permitted |

Publisher entries outside the ten-source shortlist are therefore explicit manual
research inputs or future candidates, with their component evidence and unresolved
uses retained. This is finite initial coverage across the three modes, not a
promise that every provider, territory, price or hardware SKU is researched.

For cross-record references, retain the repository commit, record path and local
evidence-row ID together. A local `D1`, `E05` or `CW09` alone is not a globally
unique source identity. This is a research citation convention, not a new wire
field or a claim that a pin authenticates source truth.

### Traceability of the carried conflict examples

The three short examples above preserve earlier research adjudications. This
appendix read their repository evidence registers on 2026-10-18; it did not
re-fetch those publisher pages, run the engines or make an API request. The dates
below are the actual historical checks recorded by their authors. The outcomes
remain source-checked/unverified at that scope.

| Carried example | Exact research and primary evidence | Date, scope and outcome boundary |
| --- | --- | --- |
| vLLM `v0.31.0` / Volta | [Pinned engine note, E05/E10/E27](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/cae31f324f827cdeb73548b72cafd392dd777dfa/research/T2-infrastructure/inference-engine.md#evidence); vLLM release [CUDA installation](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/getting_started/installation/gpu.cuda.inc.md) and [quantization matrix](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/features/quantization/README.md); actual [owner conflict decision](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75#pullrequestreview-5550616927) | Publisher documents checked 2026-10-16, owner decision accessed 2026-10-17. The release-specific minimum supersedes the positive matrix cells under that recorded decision. No conclusion about another release or runtime measurement; region/currency do not apply |
| vLLM W8A8 / Arm CPU | [Pinned deployment note, D1/D31 and D-R3](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/cae31f324f827cdeb73548b72cafd392dd777dfa/research/T0-configuration/deployment-mode.md); publisher [quantization page](https://docs.vllm.ai/en/latest/features/quantization/) and [CPU quantization FAQ](https://docs.vllm.ai/en/latest/getting_started/installation/cpu/#which-quantization-configs-does-vllm-cpu-support) | Checked 2026-10-16; recorded page dates 2026-09-14 and 2026-10-15 respectively. These were mutable `latest` documents, not an independently pinned release test. The recorded specific limitation wins, with disputed/unverified retained; no claim of a current reread |
| Bedrock / direct Sonnet 4.6 output limits | [Pinned context register CW09/CW10](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/cae31f324f827cdeb73548b72cafd392dd777dfa/research/T1-model-selection/context-window.md#evidence); [AWS model card](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-sonnet-4-6.html) and [Anthropic direct model page](https://platform.claude.com/docs/en/models/sonnet-4-6/overview); separate [2026-10-17 citation audit](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/cae31f324f827cdeb73548b72cafd392dd777dfa/research/T1-model-selection/citation-audit-2026-10-17.md) | Original check 2026-10-16, separate documentary recheck 2026-10-17. `bedrock-runtime`/model/profile and direct API are different scopes. The existing published token values are retained in their owning note, not new measurements or a cap for Sonnet 5.5; account/region entitlement stays separate and currency does not apply |

### Source-policy rules in the existing #40 research format

These proposed rule rows use the current
[`rule-proposal.md`](../../templates/rule-proposal.md) template and
[#40's decided outcome semantics](component-schema-compatibility.md#rule-format-and-outcome-semantics-decided).
They make source-policy findings reviewable; they do not publish executable rules
or turn a source-eligibility result into an overall component/build verdict.

The following template fields apply to every row:

- **Participating kinds/roles and pointers:** any selected catalog kind/role for
  which a fact is consumed. Existing CatalogItem `/id`, `/version`, `/provenance`
  and Pricebook `/rates` entries retain their frozen meaning. Exact claim,
  requested/supported-list completeness, conflict and per-use rights references
  are the conceptual research fields above; their successor JSON pointers remain
  a #40 decision. No invented pointer is sent to v1.
- **Evidence and labels:** the existing #41 policies, actual
  [#75 owner adoption](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75#pullrequestreview-5550616927),
  [checked/verified acceptance](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/41#issuecomment-6242626857),
  and [#60 current material/use decision](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/60#issuecomment-6248616771)
  are project primary decisions. The applicable fact still needs its own primary
  source, exact scope, date and grade. Documentation-only passes remain unverified;
  a synthetic example supplies no independent factual verification.
- **Dependencies/consumers:** #40 reviews these rule proposals; #41 owns source
  policy, #39 meters/aggregation, #42 saved evidence, #5/#6/#9/#14 the relevant
  component facts, and #36 comparable experiment conditions. No new execution-order
  dependency is introduced.
- **Version/migration:** this is the dated `DS` research proposal revision 1.
  Frozen v1 and historical results stay intact. A future released mapping must
  identify its ruleset/source-policy revision and preserve old findings rather
  than relabel them. Proposed fixed severity is separate from outcome, reason and
  evidence label.

#### DS-R1: Exact fact scope before use

- **Applicability:** a selected component, quote or comparison would consume a fact.
- **Assertion and source:** the fact's actual artifact/version, provider/route,
  conditions and relevant time/region/currency cover that use, under EV-1 and the
  existing [scope and price-eligibility policy](#conflict-resolution).
- **Severity / missing data:** `error`, proposed `on_unknown: review`. Missing,
  withheld or unresolved binding is `unknown`; no latest version, empty condition,
  inferred region or default source currency can supply it.
- **Explanation/remediation:** identify the missing or mismatched source scope;
  obtain a matching source/answer or keep the dependent result unresolved.
- **Synthetic examples:** matching release and documented route → `pass` for
  scope only; known other release/route applied to this selection → `fail`;
  unresolved account/region condition → `unknown`; no fact consumed → `skipped`.

#### DS-R2: Complete evidence for an omission-based negative

- **Applicability:** a support-membership comparison uses requested and supported
  values after DS-R1 eligibility.
- **Assertion and source:** use the adopted
  [#75 completeness policy](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75#pullrequestreview-5550616927)
  and its [scoped owner constraints](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40#issuecomment-6249840407).
  A documented member is supported; an eligible explicit unsupported statement can
  prove a negative. Absence only proves a negative with complete applicable source
  coverage and, where ANY logic requires it, complete requested coverage.
- **Severity / missing data:** `error`, proposed `on_unknown: review`. Missing or
  unmarked lists are unresolved, not exhaustive; empty/unknown requested scope and
  ineligible evidence cannot silently pass. Equal-rank opposite claims use DS-R3.
- **Explanation/remediation:** retain member-level reasons and source/version
  completeness; obtain the missing complete evidence or choose an evidenced member.
- **Aggregation:** retain all member rows and the declared ANY/ALL quantifier.
  One negative member cannot by itself fail ANY; one positive member cannot by
  itself pass ALL. Required requested/source completeness is assessed separately:
  in particular, ANY failure needs complete requested coverage. A member outcome
  does not assert either list is complete.
- **Synthetic per-member examples:** an explicitly supported requested member →
  `pass`; a known unsupported member, or its complete applicable exclusion →
  `fail`; an absent member of an unmarked researched subset → `unknown`;
  a known nonapplicable member comparison → `skipped`. These are member outcomes,
  not an aggregate result.

#### DS-R3: Preserve the resolved interpretation and dispute

- **Applicability:** potentially competing observations address the same claim
  scope; first establish whether their inventory and eligibility are known.
- **Assertion and source:** apply the [five-step conflict order](#conflict-resolution)
  once, retain the winning and superseded references and deciding step, and carry
  a disputed flag when the adopted policy requires it. Effective time is distinct
  from collection time. A more recently fetched out-of-scope claim cannot win.
- **Severity / missing data:** `warning`, proposed `on_unknown: review`. Unresolved
  competitor inventory or eligibility is `unknown`, as is a genuine equal-rank
  yes/no tie, with the tie disputed. A known inventory with no competing eligible
  claims is `skipped` for this conflict rule. Without eligible underlying evidence,
  the dependent fact/compatibility decision remains `unknown`. DS-R1 separately
  retains `fail` for a known scope mismatch applied to the use, versus `unknown`
  for an unresolved binding.
  Equal-rank eligible numeric values use the conservative value in the actual
  rule's direction; this does not change the underlying rule's fixed severity.
- **Explanation/remediation:** show the policy step and unresolved difference;
  seek better scoped evidence or independent support rather than hiding a conflict.
- **Synthetic examples:** retaining the more specific applicable requirement with
  both sources and its deciding step → `pass` for the resolution procedure;
  knowingly choosing an excluded generic value instead → `fail`; equally ranked
  opposite yes/no claims → `unknown` and disputed; unresolved competitor eligibility
  → `unknown`; a known inventory with no competing eligible claims → `skipped`.
  Passing this procedure does not mean the selected component itself is compatible.

#### DS-R4: Current-state eligibility without expiring retained facts

- **Applicability:** a current-state fact, such as a currently offered price or
  availability, is presented as eligible for a current recommendation or current
  budget comparison, rather than solely a dated historical observation. Consuming
  an immutable version-pinned fact in a current recommendation does not itself
  require a refresh; relevant correction and changed-selection events retain
  their separate existing handling.
- **Assertion and source:** use the [price supplement](#freshness), exact source
  scope, documented validity interval and successful applicable current source
  check. The [saved-build invalidation proposal](saved-shared-builds.md#invalidation-triggers)
  retains selected evidence and distinguishes re-evaluation from loss of history.
- **Severity / missing data:** `warning`, proposed `on_unknown: review`. An absent
  or failed required current refresh leaves current eligibility `unknown`. A known
  expired rate is ineligible for that current use. Without an eligible replacement,
  the dependent current quote/aggregate/budget decision remains unknown, not zero
  cost, a budget failure or a newly invalid historical build.
- **Explanation/remediation:** retain the prior quote's exact inputs and as-of
  date where permitted, show that current evidence is unavailable, and retry or
  obtain a new eligible snapshot. Do not invent a stale-after duration.
- **Synthetic examples:** successful scoped current check with applicable validity
  → `pass` for current eligibility only; a current label knowingly applied outside
  the selected rate's validity → `fail` for that label/use; current refresh failed
  → `unknown`; an immutable version-pinned fact outside this current-state scope,
  or a permitted solely historical observation → `skipped` by this rule.

#### DS-R5: Exact source material and intended use

- **Applicability:** evidence would be automatically retrieved, displayed or
  redistributed, or reused for a different material/use scope.
- **Assertion and source:** an actual applicable source/material/use decision
  covers the operation and its conditions, using the
  [qualified #60 table](../market/rights-validation.md#decisions) and later explicit
  current-product exclusions. Public readability, a compilation licence, a paid
  access plan or an attribution string does not supply missing permission.
- **Severity / missing data:** `error`, proposed `on_unknown: block`. Known excluded
  use → `fail`; unestablished applicable permission → `unknown` and excluded from
  that intake while its legal scope stays unknown. Conditions are evidence to
  review, not prose automatically executed as entitlement.
- **Explanation/remediation:** identify material, use, conditions and deciding
  receipt; omit or hide the affected values, use an independently reviewed
  alternative, or return for a scoped review. A rights change rechecks affected
  current and historical disclosures without deleting unaffected evidence.
- **Synthetic examples:** a specifically reviewed licensed metadata use with its
  required notices → `pass` for that use only; excluded current-product feed →
  `fail`; no applicable source/use row → `unknown` and excluded; no covered
  retrieval/display/redistribution operation → `skipped`. No example is a grant.

All five rows are **proposed research mechanics**, not independently verified
vendor compatibility rules. No new external hypothesis or unsupported numeric
claim is adopted; unknown source facts remain unknown rather than being promoted
through a policy example. Their receiving decisions below remain separate from
the earlier prototype tests.

### Exact price and saved-evidence interface for review

The proposed #41 → #39 disposition is deliberately narrower than every historical
cost-policy proposal. It preserves exact rate identity, source currency, billing
unit, effective interval, provider/account/service/region and other eligibility
conditions. Scope is resolved before recency and before any cost arithmetic.
An unavailable meter or condition cannot become a covered zero-cost line.

The [dated USD cost-policy preview](../T6-deployment-operations/cost-estimate.md#usd-cost-policy-preview--2026-10-18)
supplies only an estimate-currency preference when no explicit estimate currency
is supplied. The T0 budget's currency remains explicit; rate currencies remain as
published. This preference supplies no FX rate or eligible conversion policy,
cannot compare unlike currencies against a budget, and cannot replace an unknown
source currency. The older cost narrative's global/reference-region fallback,
ECB display-conversion choice and FX band remain their stated proposals. This
packet neither adopts them nor treats an unknown residency/region answer as one
of those reference locations. #39 retains those separate pricing decisions.

The proposed #41 → #42 disposition distinguishes three questions: whether retained
evidence can still be reproduced exactly; whether a new current quote is eligible;
and whether its values may be disclosed under the current source/use decision.
A failed current refresh does not rewrite the old quote's amount, source date or
prior outcome and does not alone destroy reproducibility from available permitted
pins. Explicit expiry can make a quote ineligible for current use while leaving
its historical meaning intact. Conversely, a reproducible old quote cannot prove
current availability, price, rights or budget eligibility. Missing retained pins
or an actual disclosure restriction keep their own unavailable/withheld result.

Selected version/evidence/ruleset/graph/contract/rights changes and build edits
re-evaluate the affected scope. A newer unrelated release or elapsed time alone
does not invalidate a build. Retain old and new views, their independent source
and policy identities and visible unknown/unpriced states; do not manufacture a
complete quote merely because one unchanged line is reproducible.

### Eight recorded outgoing receiving decisions

The coordinating engineer using **CompleteDotTech** independently reviewed the
published producer above and recorded the following actual directional research
decisions under the repository owner's delegated project mandate. The receiving
records were checked at research
[`e9159891422bb33046433ef1229c498861b218e7`](https://github.com/Pick-Your-AI/pick-your-ai-research/tree/e9159891422bb33046433ef1229c498861b218e7);
each linked receipt pins its exact receiving record blob and conditions. These
decisions do not reverse incoming producer receipts, impersonate absent named
assignees, change ownership, or certify the consuming issue's other criteria.
Acceptance here is the stated research interface; no runtime, vendor, rights or
new wire authority follows from a prototype or PR result.

| #41 consumer | Concrete research input and required boundary | Actual directional receipt and preserved limits |
| --- | --- | --- |
| #40 | The four evidence grades and checked/verified mapping, DS-R1–R5 research proposals, exact source identity and source/output-label separation. Fixed severity, outcome, dispute and evidence grade remain distinct; unknown fields and unreleased pointers stay explicit | **Accepted [H41-40](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40#issuecomment-6254387986).** The current shared-template/output intake preserves the [original grade/conflict adoption](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75#pullrequestreview-5550616927). Member results and quantified completeness stay distinct. No frozen provenance enum, generic evaluator, legal grant or automatic history rewrite is adopted |
| #39 | Exact price eligibility and current-state policy, missing-meter coverage, source currency versus optional estimate preference, per-use rights and the bounded interface immediately above | **Accepted [H41-39](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/39#issuecomment-6254388872).** Missing eligible meter evidence stays unpriced, and no arbitrary TTL is invented. USD preview supplies no budget currency, FX or default region. [#60's exclusion receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/60#issuecomment-6248616771) remains binding; ECB, aggregation, Pricebook, actual rates and quotes are not adopted |
| #42 | The three separate retained/current/disclosure questions, selected-input change events, failed refresh and explicit rate validity, with historical evidence and unknown-budget states preserved | **Accepted [H41-42](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/42#issuecomment-6254389540).** The [original change-event review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/114#pullrequestreview-5558408384) and [owner confirmation](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/42#issuecomment-6233360821) retain their scope. Elapsed time or a new release alone does not invalidate an immutable pin; failed refresh does not rewrite permitted history, while changed rights can restrict historical disclosure. No full snapshot lifecycle, schema migration or private-grant sharing is adopted |
| #5 | Provider/route/account/version scope, primary source dates, evidence grades and per-material/use boundaries; an accessible model endpoint is not account entitlement, a current price or a source-use grant | **Accepted [H41-5](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/5#issuecomment-6254390145).** The reviewed [provider evidence](../T1-model-selection/model-provider.md) separates publisher, distributor, operator, offering and account. The finite source/use intake does not establish entitlement, integration, current availability, a licence grant or a new provider wire field |
| #6 | Model/revision/variant/card/licence provenance, claim-level grades, support completeness and scoped discovery-source constraints; derivatives, weights and benchmark measurements keep separate evidence/use bases | **Accepted [H41-6](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/6#issuecomment-6254390841).** The pinned [model-selection record](../T1-model-selection/ai-model.md) keeps artifact/revision, hosted alias/configuration, quantization, tokenizer/template and adapter support distinct. Unmarked absence stays unknown and scope precedes conflict resolution. This receipt does not adopt the separate #385 continuation, a capability, licence interpretation, run or new wire shape |
| #9 | Provider/offering/region/current-state and responsibility facts, conservative support/source conflict handling and the admitted-versus-future mapping boundary | **Accepted [H41-9](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/9#issuecomment-6254391509).** The reviewed [hosting record](../T2-infrastructure/hosting.md) retains exact service/operator, deployment, region and account context. A region listing supplies no quota, entitlement or jurisdiction proof. Unknown eligibility is not unrestricted use, and no actual CD-9 mapping, provider grant or deployment is admitted |
| #14 | Exact embedding model/revision/route and query/document/index-generation evidence, with recorded grade/scope and no similarity-quality inference from vector width alone | **Accepted [H41-14](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/14#issuecomment-6254392107).** The actual accepted embedding record and EMB-01–04 r0.2 were read at the receiving pin, including the [#384 amendment](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/384). Matching width is insufficient, query/document roles can legitimately differ, and token/request limits remain separate from generation context. No encoder run, vendor check, Pricebook, hosted endpoint, new vector path or wire shape is adopted |
| #36 | Evidence-grade and R1–R15/control distinctions, protocol/selection-specific comparability, current rights boundaries and unknown handling; documentary support is not a paired benchmark measurement. Additional E-H5 sample-size and E-H12 A/B/C-tier proposals remain unadopted by this packet | **Accepted [H41-36](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/36#issuecomment-6254392681).** The receiving review includes the [actual #382 corrections](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/382), preserving the [existing audit](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/36#issuecomment-6253043241). One independent controlled variable, complete comparison scope and unknown-versus-known-invalid outcomes remain explicit. Scientific comparability and reuse rights stay separate; no dataset, evaluation run, example-display permission, winner or scoring formula is certified |

### Accountable follow-ups and completion map

The coordinating project research engineer using **CompleteDotTech** takes the
follow-up routing and evidence reconciliation for this packet under the existing
user delegation. This is an actual engineering role, not a claim to be @tynamite,
@PUSHINGSQUARES or another absent owner. Existing issue assignees remain unchanged.

| Remaining question | Named follow-up and boundary |
| --- | --- |
| Later pricing policy beyond the accepted source interface | CompleteDotTech has recorded the bounded #39/#42 receipts above; @PUSHINGSQUARES and @tynamite retain their existing #41/#39 policy scopes. CompleteDotTech routes any later FX, region fallback or aggregation proposal for its own review |
| Final source/conflict/verification representation | CompleteDotTech has recorded #40's DS-R1–R5 template/output intake; @tynamite's actual decided outcome/grade scope is preserved. CompleteDotTech routes any final wire/ruleset/migration proposal separately; this note does not implement it |
| Community evidence admission and fit-report location/licence | CompleteDotTech records any proposed real material/use and routes it to #41/#60 and CD-8 owners before admission. Existing community results stay informative; this packet admits no report or storage service |
| Real jurisdiction/provider-region source admission | CompleteDotTech coordinates any requested exact identity/group/disjointness/provider-context source packet with #9/#41 and the #37/#40 consumers. Until such evidence is admitted, the CD-9 prototype remains synthetic and actual missing mappings unknown |
| Additional catalogue sources or changed source/material/use | CompleteDotTech routes the new primary evidence and intended operation through #41/#60. The finite shortlist, current exclusions and historical source dates cannot be silently widened |

| Literal #41 research criterion | Evidence in this record | Current completion-packet state |
| --- | --- | --- |
| Source inventory with terms-of-use findings linked to primary documents | Initial ten-source identity table, joined existing registers, qualified completed #60 review and explicit treatment of other manual/future sources | Independent producer/source-register review and bounded receiving decisions recorded; the ten dispositions and existing material/use limits remain unchanged |
| Evidence-grade definitions adopted by #40 | Actual #75 owner adoption, #127 correction, current #40 semantics and H41-40 | Original adoption and current template/output intake established; no successor schema release is required to record this research decision |
| Freshness and staleness policy proposal | Existing dated/pinned classes, no arbitrary TTL, price supplement and DS-R4 | H41-39 and H41-42 accept the bounded price/current-state and retained-history interfaces; no rate, current quote or FX policy is inferred |
| Conflict-resolution rules | Existing five-step policy, traced examples, current #40 semantics and DS-R3 | Independent producer review and H41-40 accept the research presentation, retaining eligible scope, disputed claims and separate dependent unknowns |
| List of change events handed to #42 | Original #114/issue42 confirmations and exact retained/current/disclosure packet | H41-42 additionally records the later price/current-refresh intake while preserving the original change-event boundary |
| Decision record merged at `research/T0-configuration/catalog-data-sources.md` following the research method | Existing #127/#137 and CD-9 deliveries at this path | Existing record merged; current appendix awaits its own normal reviewed delivery |
| Candidate set covers the relevant deployment modes (API / managed / self-hosted) or states why a mode does not apply | Explicit API/managed/self-hosted source coverage and cross-mode exclusions above | Independent review and H41-5, H41-6 and H41-9 accept the finite policy intake; no full component catalogue claim |
| Comparison fields defined with type, unit, and evidence requirement | Existing typed dictionary and explicit integrations/source-register join; price-level scope remains separate | Research definitions and H41-40 output intake recorded; final new wire locations remain separate #40 work |
| Compatibility rules and warnings use the shared format from #40; verified rules are separated from hypotheses | DS-R1–R5 with all generic template fields, source decisions, examples and version boundary | Independently reviewed shared-template proposals accepted by H41-40; they are not a released ruleset or verified vendor behavior |
| Every factual or numeric claim cites a primary source with access date (and version / region / currency where relevant) | Existing claim registers, qualified rights review and exact traceability table; current appendix adds no vendor rate or measurement | Full producer citation/source-register review is recorded in the receiving receipts; historical access dates remain explicit and no new external check is claimed |
| Each handoff listed under Dependencies is confirmed by the consuming issue's owner (link the comment or PR review) | All eight H41 directional receipts above, with exact reviewed producer and receiving identities | Actual linked acceptance is recorded by the delegated receiving engineer CompleteDotTech; no reply is attributed to absent named assignees and their ownership is unchanged |
| Open questions recorded with a named follow-up owner | Accountable routing table above, original owners and explicit admission boundaries | Named routing and actual bounded receiving decisions recorded; final amendment review and main delivery remain necessary |

The actual receiving decisions are recorded; research completion is assessed
against these literal criteria after this receipt reconciliation is reviewed and
the amendment completes the required validation and normal main delivery. It does not require
buying an agreement merely to exclude a source, executing a provider workload,
implementing native applications, or releasing the successor contract. Any
specific factual claim or source use actually admitted still needs its real
evidence and applicable authority. Nothing in this packet marks the issue,
Project state or another component complete.
