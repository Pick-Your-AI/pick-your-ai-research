# T0: Component Schema & Compatibility Rules

Issue: #40 · Contract: v1 1.0.0 (adopted in PR #44) · Assignees: @tynamite, @zwright8
Status: partial decision record for review, revision 2 (consolidates decisions already posted) · Last updated: 2026-10-17
Deliverable path: `research/T0-configuration/component-schema-compatibility.md` · Companion records: `workload-use-case.md` and `deployment-mode.md` (PR #81), `catalog-data-sources.md` (#41)

This revision consolidates what #40's owner has already decided in reviews of submitted proposals: T2 in [#75](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75#pullrequestreview-5550616927), market research in [#67](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/67#pullrequestreview-5550697545), T1 in [#88](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/88#pullrequestreview-5554964868), and T0's own proposals in PR #81. Sections marked **To do** are open, and the split proposed on #40 assigns the worked T1/T2 examples and the T5 triage to @zwright8. Nothing here changes the frozen v1 contract; changes go to a reviewed next version.

## User decision

How does the builder represent every component, and decide, explain and recompute whether a set of selections is compatible?

## Candidate options

| Option | Description | Assessment |
| --- | --- | --- |
| A. v1 as-is | The adopted contract and its 45 baseline rules | Executable today, but its build-level mode gate skips 17 self-hosted rules on hybrid builds, and two membership rules fail on omissions from incomplete lists (below) |
| **B. v1 plus a reviewed next version** (recommended) | Keep v1; collect proposals as rule families and contract decisions (CD-n); release them as a versioned ruleset and contract version | Preserves v1 readers; each change carries examples and migration (CD-7) |
| C. Replace the contract | Redesign the schema around the proposals | Rejected: discards adopted work and its tests |

## What v1 already provides

- **Catalog item:** `id`, `kind`, `tier`, `name`, `version`, `status`, `billing_class`, `spec`, `license`, `provenance`, `updated_at` (required), plus `description`, `tags` and `extensions`. This covers #40's minimum fields for entity ID, category (`kind`, `tier`), version, lifecycle status and source references (`provenance`). `valid_from`/`valid_to` have no direct field (versioning, below).
- **Build:** `selections`, `links` (typed relations such as `runs_on`, `served_by`, `stored_in`, `provided_by`, `derived_from`), `objectives`, `policy`, `locks`, `revision`.
- **Rule:** `id`, `severity` (`error`/`warning`/`info`), `applies_when`, `assert`, `on_unknown` (`block`/`review`/`defer`), `message`, `remediation`, `affected_kinds`. A ruleset has `id`, `version` and `published_at`; individual rules carry no version.
- **Also:** `catalog-snapshot` (captured items with a revision) and `dependency-graph` (edges with a revision).

## Consolidated next-version field dictionary (research proposal)

This dictionary makes the proposed shapes reviewable for #40's “field types and examples” criterion. It consolidates the merged [workload dictionary](workload-use-case.md#field-dictionary), [deployment dictionary](deployment-mode.md#field-dictionary), [CD-1–CD-12](deployment-mode.md#open-contract-decisions), CD-13 below, and the CD-7 fixtures. These are project proposals, not new publisher facts or a released schema. The companion dictionaries retain their per-field evidence requirements and are authoritative where this summary groups several fields. No new enum, required field or JSON location is adopted here.

**Notation and unknowns.** Types describe known values only. The CD-1 wire encoding for missing, explicitly unknown, withheld and not-applicable answers is unresolved; none is an ordinary member of a vendor capability enum. In the synthetic examples below, “unknown” describes the expected interpretation, not a literal to send to the frozen evaluator. An omitted list is not an empty list; an incomplete supported-values list cannot prove an unsupported value. A zero is known data only where the field allows zero, never a replacement for absent evidence. References must resolve within their declared snapshot/version scope; a string identifier alone supplies no fact or permission.

| Proposed object / field group | Known-value type, unit and constraints | Synthetic example / unresolved boundary | Source and accountable issue |
| --- | --- | --- | --- |
| Catalog identity and lifecycle | Existing v1 strings `id`, `kind`, `tier`, `name`, `version`, `status`; preserve schema enums | A different release is a different version, not proof that the old release is unusable. ID+version resolution and retention remain CD-7 | v1 CatalogItem; #40/#41/#42 |
| Catalog provenance | Existing source URL, accessed date and status; next-version evidence identity/completeness needs a reviewed shape | Source-checked documentation remains `unverified`; the exact tuple and independent support must be recorded before `verified` | #41 evidence grades; CD-3 |
| Selection `deployment.runtime_operator` | `self` or `provider` | User-operated model plus provider/shared moderation model derives hybrid; a legacy `self_hosted` label cannot override either | deployment dictionary; #3/#40, M3 |
| `runtime_supplied_by`, `capacity` | Provider case: supplier `operator` or `customer`; capacity `shared`, `reserved_throughput`, `dedicated_instances` | Provider with missing capacity has unknown mode, even if billed monthly. Supplier does not alone choose mode | deployment dictionary; #3/#9 |
| `deployment.placement` | Typed device shares; devices linked by `runs_on` | Shares are not byte allocations; per-pool/rank accounting remains CD-2 | deployment dictionary; #10/#11 |
| Build-owned `workload` taxonomy | Task enum plus optional secondary-task set; `turns` single/multi; interaction interactive/background/batch | Primary task excluded from secondary tasks; `other` needs 1–500-character description. Per-stage workloads remain CD-5 | workload dictionary; #2/#40 |
| Workload modalities and output | Nonempty input/output modality sets; output format free/json/json_schema with schema when required | A format requirement is not model support evidence | workload dictionary; #2/#6 |
| Knowledge/actions/customisation needs | Knowledge capability set or exclusive none/unknown; actions none/read_only/write; customisation none/prompt_only/fine_tune | `knowledge_implementation` is keyed by capability, with via rag/knowledge_base/long_context/tool/direct_lookup, selection IDs and justification; long_context/direct_lookup require justification | workload dictionary and W-R2–W-R5; #13/#16/#25/#30 |
| Memory need and implementation | Need none/session/persistent; implementation via application/agent_framework/memory_store with IDs and justification | Persistent memory can accompany a single-turn conversation. Application session history need not select a memory store | workload dictionary and W-R11; #2/#28 |
| Request volume and concurrency | Request count integer ≥ 0 per day/month; peak concurrent requests integer ≥ 1 | Zero volume is distinct from absent volume. Service-wide demand cannot be combined with per-replica admission without allocation | workload dictionary and W-R6; #10/#11/#39 |
| Input/output token demand | Mean decimal and maximum integer; input 1 ≤ mean ≤ max; output 0 ≤ mean ≤ max | Mean 1.5 is valid. Output is not applicable only for an operation generating no tokens; thinking is counted once in output | workload dictionary; #7/#39 |
| Native non-text demand | Per-request image count integer max; audio/video seconds decimal max; decimal means ≥ 0 and ≤ max | These are native units, not invented token counts. Stage-specific limits remain CD-11 | workload dictionary; #6/#7 |
| Tokenizer and context policy | `tokenizer_assumption`: tokenizer/model ID string or model_native; exact route's input/output/combined budget semantics | Independent caps 8,000 input and 4,000 output do not imply a 12,000 shared window; exact new wire fields remain CD-11 | #7; T1 gaps; worked context examples below |
| Latency and throughput targets | Latency metric ttft/tpot/e2e, positive integer ms, percentile 50/90/95/99; positive decimal throughput with unit output_tokens_per_second/requests_per_second/items_per_hour and scope aggregate/per_request | At most one latency target per metric. Aggregate requests/s is distinct from per-request output tokens/s | workload dictionary; #36/#39 |
| Batch completion window | `completion_window_hours`: decimal > 0 hours, for batch workloads | A synthetic 2.5-hour completion target is not an observed runtime or an inferred throughput guarantee | workload dictionary; #2/#36 |
| Availability target | `availability_target`: decimal percent 0–100 and period day/month/year | A synthetic 99 percent per month requirement is user input, not a provider SLA; period must remain explicit | workload dictionary; #2/#37 |
| Precision preference | `precision_preference.min_stored_bits_per_weight`: optional decimal > 0 bits/weight | A requested minimum must be checked against actual artifact evidence under W-R9, not inferred from a quantization label | workload dictionary and W-R9; #6/#10/#11 |
| Network requirement | `network`: online/private_network/air_gapped | An air-gapped requirement activates W-R8; provider operation alone neither proves nor disproves isolation. Missing answer remains unresolved | workload dictionary; CD-4/#37 |
| Data classification and categories | `data_classification`: v1 enum, level definitions remain Q1; `data_categories`: set of personal_data/special_category or exclusive none/unknown | Explicit none is not unknown and cannot be mixed with personal-data categories; classification labels alone prove no lawful basis | workload dictionary; #40/#35/#31/#32 |
| Quality target | Protocol/metric/reference IDs, higher_better/lower_better, nonnegative absolute or relative-percent degradation | Relative-percent degradation is invalid when reference value is zero; unlike protocols are not comparable | workload dictionary and W-R10; #36 |
| Budgets | List of nonnegative decimal amount, ISO currency, period one_off/month/year and scope hardware/operating/total | Empty list explicitly means unconstrained; missing currency cannot default to USD | workload dictionary; #39/#41 |
| Hardware inventory mode | `hardware.mode`: required use_existing/acquire/undecided; `devices[]`: list with at least one entry for use_existing | CPU-only devices are valid; acquire/undecided does not switch W-R6 fit requirements off | workload hardware dictionary; #2/#10 |
| Hardware device identity and capacity | Stable unique `device_id` string; kind gpu/cpu/npu/other; optional accelerator `catalog_ref`; required `model_name` string; positive decimal `memory_gb` (10⁹ bytes), `memory_pool_id`; `reserved_memory_gb` ≥ 0 per pool | CPU/GPU sharing one pool must not double-count its bytes; CPU memory describes system memory available to inference. Catalog references do not replace the inventory's actual capacity evidence | workload hardware dictionary; CD-2/CD-6/#10 |
| Hardware inventory location | `hardware.location`: jurisdiction ISO 3166 code and `site_label` string; jurisdiction required when residency is constrained | An owned-machine site replaces a cloud-region input but does not establish all downstream processing/storage locations | workload hardware dictionary; #2/#37 |
| Host hardware location | `hardware_location` on host: kind personal_device/own_server/rented_server/provider, ISO 3166 jurisdiction and `site_label` string | Jurisdiction required when residency is constrained; a rented server's location is not inferred from its billing address or the researcher's location | deployment dictionary; #3/#9/#37 |
| Device capabilities | memory_kind dedicated/unified/system; positive decimal GB/s with vendor_peak/measured basis; ISA set; NUMA count integer ≥ 1 | Published peak bandwidth is not a measured workload rate | deployment dictionary; #10/#11 |
| Engine build and admission | Version, fork URL/commit when applicable, launch options; positive integer sequence expansion/admission and matching domain | Missing expansion leaves sequence demand unknown; a per-step batch limit is not automatically a KV-residency cap | deployment dictionary and W-R6; CD-2/CD-3/#11 |
| Artifact representation | Format gguf/safetensors/onnx/pytorch/other; package convention mlx/transformers/other/none; open-vocabulary quantization method, positive decimal logical/stored bits per weight and packing string | Package convention is not serialization; a quantization label alone supplies no byte estimate | deployment dictionary; #6/#10/#11 |
| Artifact `components` | List of role language_model/vision/draft/other, positive decimal size_gb and required boolean | A required vision component must be included in the scoped resource model | deployment dictionary; #6/#10 |
| Conditional support/list completeness | Typed CD-3 query/cohort/result candidate below, bound to exact CD-1 bytes and normalized component/property/configuration scope | Absence from exhaustive applicable list → fail; absence from researched subset → unknown. Source qualification and real tuple resolution remain separate | CD-3; #6/#9/#11 |
| Licence conditions and answers | Conditions have ID/text/source/kind eligibility or obligation/question; answers depend on kind | Eligibility met/not_met differs from obligation acknowledged/not_acknowledged. Answer/reference locations still require CD-6 | deployment dictionary; #30/#40 |
| Organisation attestations | Jurisdiction code, EU-market-placement boolean, lawful-basis reference; CD-12 also includes revenue and monthly active users. Revenue needs an amount, currency, reporting period and the licence-defined organisation/account scope; MAU needs a user count, monthly measurement period and the licence-defined product/organisation scope. Exact value types, aggregation and wire fields remain unresolved against the selected condition | A missing revenue or MAU answer leaves an applicable eligibility condition unknown; never infer zero or reuse a differently scoped total. These are sensitive user attestations, not inferred permission or transferable consent | workload dictionary; deployment CD-12 and licence-condition questions; #30/#31/#32/#42 |
| External connections | Entries with destination ID, purpose, provisioning/runtime lifecycle, enabled/disabled state, data-carrying and required booleans | Unknown state and absent inventory remain unresolved; runtime isolation also needs the selected boundary | deployment dictionary; CD-4/#37 |
| Destinations and residency | Destination IDs/host, processing/storage code lists and data scope; processing and storage constraints separate | Unconstrained residency is distinct from unknown; jurisdiction containment/group semantics remain CD-9 | both dictionaries; #37/#41 |
| Provider data terms | Training-use enum, scoped application-state/abuse-monitoring retention entries, zero-retention eligibility and conditions | Free-text conditions cannot silently become pass; endpoint/account/region evidence required | deployment dictionary; #5/#9 |
| Billing descriptor | charge_basis per_use/per_time/flat_subscription/none; ownership owned/rented/provider; commitment kind none/reservation and integer term_months ≥ 0 | Does not determine mode or substitute for a pricebook; new meter units require #39 disposition | deployment dictionary; #39 |
| Build links | Existing relation/from/to references including per-component runs_on/served_by host/device/engine links; proposed role/access attribute | Multiple possible credential/base bindings without an evidenced disambiguation remain unknown; inheritance rules are CD-6 | CD-6 and T4 queue; #40 |
| Snapshot and pricebook locks | Existing IDs plus proposed explicit revisions; exact revision wire type/location pending | Missing revision produces “cannot be reproduced exactly”, never replacement by latest | CD-7, M5; #42 |
| Evaluation result | Fixed rule severity; outcome pass/fail/unknown/skipped; proposed reason code, disputed flag and evidence label | A passing error-severity rule is not a failure; evidence disagreement does not change severity | Rule semantics above; CD-1/CD-3 |
| Multi-selection evaluation | Quantify over enabled selections; reject duplicate primary roles semantically before evaluation | Two primary selections must not silently cause a required rule to skip; the CD-13 typed binding below proposes one concrete quantifier encoding, with final ruleset adoption separate | CD-13; #40/T4 |

### Reviewable examples and migration boundaries

The [CD-7 synthetic fixtures](../../tests/fixtures/t0-migration.json) and [projection prototype](../../tests/t0_migration_prototype.py) already exercise component operator/capacity, independent and derived modes, conflicting workload copies, unresolved/cyclic adapter bases and revision locks. They accept normalized fixture evidence only. They do not define the final wire encoding or resolve arbitrary real catalog sources.

- **Mode:** M1 preserves the old API label for historical evaluation while projecting model API + user-operated retrieval to hybrid. M2 cannot project managed capacity from a legacy label.
- **Workload:** M4 chooses the documented projection precedence (objectives, selection settings, preset), preserving disagreeing values and a conflict flag. Precedence is not acceptance of the chosen answer; the user still must reconcile the conflict. Zero is preserved rather than treated as missing.
- **Locks:** M5 records missing revision evidence rather than fetching a current revision. Historical v1 evaluator output and original bytes stay unchanged.
- **Context:** the worked T1/T2 examples below separate shared-session failure from independent input/output passes; neither supplies a KV-memory fit result.

**Remaining decisions, not invented defaults:** CD-1 answer-state encoding; CD-2 byte placement/pool semantics; CD-3 eligible-evidence/completeness/result wire shapes; CD-4 boundary representation; CD-5 per-stage workload; CD-6 reference/credential/inheritance resolution; CD-7 revision resolution and next-version migration; CD-8 community evidence; CD-9 jurisdiction groups; CD-10 non-model-service runtime requirements; CD-11 context-budget shape; CD-12 attestation placement and CD-13 multi-selection syntax remain with their accountable owners in the companion decision register. This dictionary neither releases v1.1 nor removes #42's recorded #40 prerequisite.

## Rule format and outcome semantics (decided)

1. **Severity is fixed per rule; the outcome is separate.** Outcomes are `pass`, `fail`, `unknown`, `skipped`. A passing `error` rule is not a failure.
2. **One rule per concern.** Missing evidence and "not applicable vs not yet known" are reason codes on the outcome (CD-1), not separate evidence or applicability clauses. A rule is split only when a genuinely different severity is needed (as with D-R2a/b and D-R7a/b in #81).
3. **`unknown` is reserved for missing eligible evidence or genuine ties.** Conflicting eligible evidence is resolved by #41's conflict order:
   1. normalise;
   2. scope;
   3. version and date;
   4. authority;
   5. the conservative value among equal ranks, with the result flagged as disputed.
4. **Estimates that straddle a limit are decided on the conservative bound and flagged** ("may not fit"), not left `unknown`.
5. **Passing on documentation.** A rule may pass on eligible, versioned publisher documentation. The result carries "unverified" until it is independently reproduced (governance's second source or reproducible test).
6. **List completeness.** Absence from a list marked complete from an exhaustive source is `fail`; absence from an unmarked list is `unknown`. Until that metadata exists (CD-3), `rule.engine.model.format` (`intersects`) and `rule.precision.engine` (`contains`) must not fail on omissions from researched arrays.
7. **Applicability is per component.** Rules key on the component's deployment mode (operator and capacity, #81), not the build-level `deployment_mode`.
8. **`on_unknown`:** `review` for evidence-dependent rules; `block` only where proceeding is unsafe (for example air-gap isolation, W-R8); `defer` for recommendations.

### CD-1 concrete answer encoding and normalization experiment (2026-10-18)

The [#81 answer-state policy](workload-use-case.md#unknown-and-missing-answers-proposal)
already distinguishes `provided`, `unknown` and `missing`. Its compatibility
and recommendation rules deliberately handle unresolved inputs differently.
The #42 [partial saved-build proposal](saved-shared-builds.md)
also needs `withheld`. This experiment chooses a concrete candidate encoding
for those requirements and for an explicit `not_applicable` answer. It does
not release a successor contract or claim that those owners adopted this shape.

**Selected design:** a versioned, discriminated answer map in the synthetic
`x_t0_answer_states` extension, with `proposal_version: "cd1-0.1"`. Each key is
a non-root JSON Pointer naming a field in the experimental answer tree. The
[schema](../../tests/fixtures/t0-answer-states.schema.json),
[synthetic example](../../tests/fixtures/t0-answer-states.json) and
[normalizer](../../tests/t0_answer_state_prototype.py) live under `tests/`, as
the pre-release migration boundary requires. These paths do not resolve real
catalog items or change the frozen BuildSnapshot shape.

| State | Wire members | Normalized meaning |
| --- | --- | --- |
| `provided` | Required `state`, `value`; optional nonempty `source` | A stated value, validated against the requested field's local schema before a predicate receives it. `preset:<name>` retains editable-assumption attribution, not independent verification |
| `unknown` | `state` only | Explicitly unresolved answer; no replacement value |
| `missing` | `state` only | No recorded answer in this experiment; the interface can ask for it. Absence of a path has the same normalized state, without claiming why a historical v1 value was absent |
| `withheld` | `state` only | Deliberately unavailable; retained as distinct from an unanswered question |
| `not_applicable` | `state` only | Declared absence of a value in this field's scope. It does not itself establish that every dependent rule is inapplicable |

A tagged value avoids interpreting a user's literal string `"unknown"` as a
state. Field validation still rejects that string where, for example, the
network enum allows only known network modes. Zero, false, empty arrays and
empty strings remain provided when their field schema permits them. Explicit
provided null is valid only for a nullable field; it never substitutes for an
unknown numeric, boolean or enum answer. Bare sentinel strings/null cannot
stand in for an answer record.

An indexed representation keeps answer metadata out of ordinary domain
objects; an object-valued answer can itself contain a field named `state`
without being recursively reinterpreted as metadata. Compared with wrapping
every nested domain field, the index also permits a single withheld or unknown
parent answer to cover its descendants. Overlapping parent/child declarations
are rejected: a provided parent cannot conceal a withheld child, or vice versa.
Partially disclosed objects must use separate leaf answers. A provided parent
can supply a nested object/array value; absent members or indices become
`missing`. Malformed pointer/index syntax and scalar traversal are errors.
Duplicate JSON keys and nonfinite numbers are rejected before normalization.

**Rule boundary:** compatibility predicates receive an unresolved result for
all non-provided states, including unknown applicability. Recommendation
rules explicitly test the known-answer gate specified in #81 and therefore
skip unresolved needs. A known false applicability predicate still skips.
No selected component remains CD-13's distinct empty selection scope; it is
not a sixth answer state. The answer's original state/path remains available
alongside the selection findings so these explanations are not collapsed.
Severity, evidence eligibility and selection activation remain separate.

The [15 executable cases](../../tests/test_t0_answer_states.py) cover nested
and escaped paths, array boundaries, parent withholding, explicit false/zero,
field-type rejection before predicates, malformed/duplicate/nonfinite inputs,
read isolation and compatibility/recommendation behavior through the CD-13
experiment. They reproduce frozen v1's literal-unknown comparison and verify
unchanged historical findings when the synthetic extension is present. No
original build bytes, frozen evaluator, measured artifact or receiving receipt
is modified.

Primary syntax references inspected **2026-10-18**:
[RFC 6901, sections 3–4 and 7](https://www.rfc-editor.org/rfc/rfc6901) defines
pointer token escaping, traversal and application-specific error handling;
[JSON Schema draft 2020-12 validation](https://json-schema.org/draft/2020-12/json-schema-validation)
defines the field-validation vocabulary used in the local fixture. The
answer states, non-root restriction, overlap rejection and missing-value policy
are project design choices, not requirements attributed to either source.

Remaining integration is concrete: #40/#2/#3/#42 review this exact encoding;
CD-3 binds eligible evidence; CD-6/CD-13 bind real selection/reference paths;
CD-7 provides original/successor reader dispatch, migration and version locks.
The final schema/generator/ruleset, full field registry and affected-owner
handoffs remain separate successor-release work. #42/#114's recorded
prerequisite is unchanged by this synthetic normalization experiment.

### CD-3 synthetic support-membership experiment (2026-10-18)

The [normalized prototype](../../tests/support_membership_prototype.py) and
[regression cases](../../tests/test_support_membership.py) exercise the
[adopted completeness policy](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75#pullrequestreview-5550616927),
checked against the actual owner review on 2026-10-18. The unchanged frozen
evaluator's `contains` and `intersects` return false for an absent member;
those Boolean operations alone cannot tell an incomplete research inventory
from an exhaustive negative claim. The synthetic cases reproduce that gap.

The input represents an already normalized and scoped publisher-evidence
cohort. Actual source inspection, selected version/configuration/condition
matching, and #41's scope/date/authority ordering must happen first. The
prototype does not derive eligibility from a nonempty list or its completeness
marker, merge independent support dimensions, or resolve catalog sources.

| Eligible evidence for a requested value | Proposed member result |
| --- | --- |
| Documented supported member, without an equal-rank opposite claim | `pass`, evidence still `unverified`; exhaustiveness is unnecessary for this positive claim |
| Explicit unsupported statement, without an equal-rank opposite claim | `fail`; an exhaustive inventory is unnecessary for this negative claim |
| Absent from a known list whose scoped source is exhaustive | `fail` |
| Absent from an unmarked/non-exhaustive list, or the list itself is missing | `unknown`; a missing list is not a known empty exhaustive list |
| Opposite yes/no claims still equally ranked after the preceding review | `unknown`, flagged disputed; a stronger requirement must already have superseded a weaker capability listing under #41 |
| Evidence known outside the query scope, or eligibility unresolved | `unknown` for an applicable compatibility query; an ineligible source is not evidence of incompatibility |

A singleton query models `contains`; alternative accepted formats use an
`any` query like `intersects`. One documented alternative passes that membership
check, while failure requires negative evidence for every alternative. An
`all` query requires every requested member and fails on a known counterexample;
unresolved rows remain visible in either mode. These internal query names and
reason strings do not settle DSL syntax. The experiment requires a nonempty
applicable query; a known irrelevant rule is explicitly `skipped`, while missing
requirements/applicability remain `unknown`.

A member passing documents only that scoped support claim, with the source
identity retained. It does not establish joint architecture/backend/quantization
support, runtime execution, memory fit, an offering's allowed residency, or
independent verification. [T2's direct-loader completeness exception and its
unmarked support lists](../T2-infrastructure/inference-engine.md#release-keyed-artifact-and-hardware-matrix)
retain their original source/release scopes. The typed CD-3 binding below
selects a query/result candidate over CD-1; conflict resolution over real
sources, affected-owner adoption and the versioned ruleset/adapter remain
separate. Frozen v1 and #42's prerequisite are unchanged.

### CD-3 typed support query and result candidate (2026-10-18)

**Selected research design:** retain the accepted membership reducer and add
closed `x_t0_support_query` / `x_t0_support_result` envelopes at proposal version
`cd3-0.1`. The [query schema and `$defs/result`](../../tests/fixtures/support-membership-binding.schema.json),
[reader and result verifier](../../tests/support_membership_binding_prototype.py),
[query](../../tests/fixtures/support-membership-binding.json),
[CD-1 answers](../../tests/fixtures/support-membership-answers.json),
[result](../../tests/fixtures/support-membership-result.json) and
[25 focused regression methods](../../tests/test_support_membership_binding.py)
make this exact candidate reviewable. This chooses an encoding; it does not
claim that the normalized-mechanics receipt also adopted this new wire format.

| Field / boundary | Chosen type and interpretation |
| --- | --- |
| Query | Stable canonical-style ID, opaque nonempty version, `requirement: any` or `all`, fixed `info` / `warning` / `error` severity. A singleton is a membership query; no implicit default quantifier |
| Scope | Exact selection ID, catalog-byte SHA-256, item ID/version/canonical kind, non-root literal JSON Pointer for the support property, and configuration/conditions-byte SHA-256. All dimensions must match the caller's separately established selected scope |
| Evidence cohort | Stable ID and opaque version identifying the already normalized, scoped and ranked claim cohort. Neither field supplies a publisher URL, access date, completeness or source permission |
| Answer identity | SHA-256 of the complete original CD-1 file, including unrelated answers and whitespace. Field paths use `/support_checks/{selection_id}/{query_id}/{query_version}/{cohort_id}/{cohort_version}/{field}` with each literal token escaped through CD-1's pointer rules |
| `applies_when` | A provided Boolean or a distinct unresolved CD-1 state. Only a caller-qualified provided `false` skips a rule |
| `requested` | Provided nonempty list of unique, nonempty literal strings, or an unresolved CD-1 state. Values are case sensitive, untrimmed and uncoerced; they carry no numeric unit or implicit vocabulary mapping |
| `supported` / `unsupported` | Provided unique string lists, possibly empty, or unresolved CD-1 states. The former is a positive inventory; the latter records explicit equal-rank negative claims in this cohort |
| `exhaustive` | Provided Boolean or unresolved CD-1 state, separate from source eligibility. Only a known positive inventory plus eligible `true` completeness can support an absence-based negative |
| Caller qualification | Exact Boolean or unresolved selection activation, plus independently qualified applicability, requested values and cohort. Each omitted qualification is unresolved for that invocation; an answer's `source` label cannot qualify itself |
| Result | Exact query/answer hashes, query/scope/cohort identities, caller evaluation context, every operand's state/value/source/source path, and the reducer's outcome/reason/source ID/disputed flag/all sorted member findings. Evidence label remains `unverified`; severity stays on the versioned query |

**The negative-claim readiness decision is explicit.** The accepted reducer
requires a concrete set of explicit negative claims. This encoding therefore
requires a **provided** `unsupported` list before admitting a cohort to that
reducer. `[]` means the normalized cohort has no recorded explicit negative
claims; it does not mean the publisher supports every other value or that its
positive inventory is exhaustive. Missing, unknown, withheld or not-applicable
negative-claim data yields `unknown / unsupported_claims_unresolved`, with all
input states and the requested values retained, and no asserted member findings.
That deliberately conservative readiness check also defers an otherwise
possible exhaustive-absence verdict until the cohort's negative inventory is
recorded. It never converts an unresolved answer into an empty set.

The positive inventory has a different existing reducer contract: it can be
missing. An explicit eligible unsupported member may still fail with a missing
positive inventory; a missing positive inventory cannot become an empty
exhaustive inventory. Documented positives require no completeness marker.
Equal-rank positive/negative claims remain disputed and unknown. ANY preserves
its other unresolved rows when one member passes; ALL preserves them when a
known counterexample fails. The committed synthetic ANY example contains one
documented member, one unmarked omission and one equal-rank dispute. Its pass
is scoped membership only, with `disputed: true` and `unverified` preserved.

Provided values are validated before any disabled/applicability/eligibility
shortcut. Known empty requirements, malformed lists, duplicate decoded JSON
keys, non-finite numbers, invalid Unicode scalars, ambiguous parent/child paths
and malformed identities are input errors. Unresolved parent states propagate;
a provided object can supply grouped fields and retains its exact source path.
Valid but mismatched selected scope is unknown, never automatic incompatibility.
Disabled and unresolved activation have separate skipped/unknown dispositions.
Canonical kinds are checked against frozen v1's registry, while the new ID and
digest guards reject terminal controls across the complete value.

**Result consumption:** schema validation checks shape only. `verify_result`
recomputes from the retained query/answers and the **caller's** selected scope,
activation and eligibility inputs, then compares every reported field. A
self-reported eligible flag, changed source/version/hash, removed disputed row
or changed outcome cannot validate itself. Result JSON formatting may vary;
the original query and answer byte identities cannot. Returned data is detached
from the reader. This is a consistency check, not a signature or evidence grade.

**Evidence and release boundary:** the example's catalog digest names the
frozen synthetic catalog and its conditions digest names the complete frozen
synthetic build. The claim lists are independent synthetic counterexamples,
not facts extracted from that catalog. The reader consumes neither artifact;
the caller must resolve the actual selection/item/property/conditions and
establish the request's and cohort's eligibility under #41 before evaluation.
This format can name canonical API, managed or self-hosted component scopes,
but a kind, digest or matching label proves no joint tuple support, activation,
rights, currency, residency, runtime fit or independent verification.

The new test-only files and this decision supplement leave the accepted
CD-1 normalizer, CD-3 reducer, CD-2/CD-6/CD-7 work, frozen `contracts/v1`, measured
artifacts and recorded receiving receipts unchanged. #40's tynamite/zwright8
review owns successor adoption; #41 owns actual evidence qualification with
the affected component owner. Real source adapters, final ruleset dispatch,
migration and the remaining listed handoffs retain their own concrete work.
#40 remains open and #42/#114's substantive prerequisite is preserved.

## Rule families (decided, pending a versioned ruleset)

| Family | Merges | Notes |
| --- | --- | --- |
| Memory fit | COMPUTE-01, T1-M2, W-R6 | Per-rank and per-memory-pool; admitted sequences per #81's request-to-sequence accounting; EV-1 rank before the conservative maximum (CD-2) |
| Joint support | COMPUTE-02, ENGINE-02, T1-M1, D-R3 | One rule keyed by the configuration tuple; D-R3 is its quantization case (CD-3) |
| Context fit | CTX-01, `rule.model.context.fit`, COMPUTE-03 (KV half) | Separate input/output budgets wait on CD-11; context-limit checks stay in v1's rule |
| Long-context configuration | CTX-02 | Unknown scaling configuration is evaluated against the native limit |
| Multi-device plan | COMPUTE-04 | Expressed through #81's `placement` |
| Loader, adapters, API features | ENGINE-01, ENGINE-03, ENGINE-04 | Adapter lineage under CD-6; structured output read from the workload profile |
| Hosting | Private networking, mounted-storage locality (generalised from Runpod), offering membership | Completeness gate applies; offering presence is not residency |
| Route and offering | T1-O1, T1-O2 (split) | Offering via `provided_by` and the opaque-endpoint key; licence conditions under D-R2a/b |
| Licence and rights | D-R1, D-R2a/b | Any mode where the weights' licence binds; inherited through `derived_from` (CD-6, #30) |
| Residency and isolation | D-R6, W-R8 (absorbs T4's MCP air-gap rule) | Processing and storage evaluated separately |
| Workload | W-R1 to W-R5, W-R7, W-R9, W-R10 | As proposed in #81 |
| Price classification | CTX-04 | #39 owns rates; budget checks use the higher tier when estimates straddle |
| Agent capability and trust | T4 framework, tool, MCP and memory rules (24 v1-valid proposals plus contract-dependent ones) | One severity per rule; queue disposition only, accepted on #40; credential-binding ambiguity gives `unknown` (CD-6) |

**Recorded T5 routing disposition:** [@zwright8 accepted the routing with constraints in #126](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/126#pullrequestreview-5560506323). The inventory below preserves the remaining source-specific receiving decisions; queue acceptance is not approval of fields, rights or executable rules.

## Contract decisions

CD-1 to CD-12 are defined in #81 (`deployment-mode.md`, "Open contract decisions") and remain the base list. CD-13 is added here, from T4's findings on #40:

| ID | Decision | Accountable |
| --- | --- | --- |
| CD-13 | Rules over several selections of one kind: a quantifier over all enabled selections, and semantic rejection of duplicate `primary` roles before evaluation, so that "not selected", "not relevant" and "not yet known" are not collapsed into `skipped` (T4 finding 1; CD-1) | #40 |

### CD-13 synthetic selection experiment (2026-10-18)

[The normalized prototype](../../tests/selection_quantifier_prototype.py) and
[its regression cases](../../tests/test_selection_quantifier.py) make the
[accepted queue item](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40#issuecomment-6242626523)
reviewable without choosing a quantifier wire syntax. The experiment uses only
synthetic selections and Boolean/unknown predicate facts. It does not resolve
real catalog evidence, publish executable compatibility rules or release a
contract version.

The baseline counterexample is reproduced against the unchanged
[`Evaluator.selected` and `exists` implementation](../../contracts/v1/reference/evaluate.py).
With one enabled primary tool and no enabled framework, the historical
`rule.agent.tools.framework` fails. Adding a second enabled primary tool makes
the selection reference ambiguous, `exists` false and the rule `skipped`.
That historical rule is used only to expose the selection bug: the experiment
does not reinstate its framework requirement; W-R3 still permits tool or MCP
execution without a framework.

The prototype's proposed execution order is:

1. Check selection identities and `(kind, role)` uniqueness across the build
   before running any rule predicate. This is the identity slice of the frozen
   [validation protocol](../../contracts/v1/docs/AGENT_PROTOCOL.md#validation-layers--mandatory-in-order),
   which also requires other schema/reference checks outside this experiment.
   Duplicate primary roles are therefore a semantic input error, never a
   `skipped` finding. Other duplicate roles are rejected too; roles are scoped
   to kind. Disabled selections retain their identities and roles, so disabling
   a duplicate does not make the ambiguous build valid.
2. Evaluate every enabled selection of the rule's kind, including non-primary
   roles. Keep each selection's finding. A known false applicability predicate
   yields `skipped`; unknown applicability yields `unknown` without evaluating
   its assertion. A known applicable rule with missing eligible assertion
   evidence also yields `unknown`.
3. Summarize the universal check as `fail` when any applicable selection fails,
   otherwise `unknown` when any selection is unresolved, otherwise `pass` when
   at least one applicable selection passes. No enabled selection, or an
   entirely inapplicable scope, is `skipped`; their reason/row details remain
   distinct. A failed universal check retains other selections' unknown rows.
   Rule severity stays fixed and separate from every outcome.

The cases also cover a scope with no primary role, mixed kinds, disabled
selections, a counterexample in each input order, duplicate IDs, a duplicate in
an unrelated kind, and rejection of non-normalized predicate values. Empty
scope is not a vacuous compatibility pass; required-component cardinality
still belongs to the preceding activation layer. These checks establish only
the proposed mechanics. The later binding below joins them to CD-1 answers;
CD-3 evidence resolution/result encoding, a general predicate DSL, affected-owner
review and the versioned adapter / ruleset remain open. #42's prerequisite is
unchanged.

### CD-13 typed selection binding proposal (2026-10-18)

The [versioned sidecar schema](../../tests/fixtures/selection-binding.schema.json),
[binding fixture](../../tests/fixtures/selection-binding.json),
[paired CD-1 answers](../../tests/fixtures/selection-answers.json),
[reader](../../tests/selection_binding_prototype.py) and
[integration cases](../../tests/test_selection_binding.py) choose a concrete
encoding for the accepted universal selection mechanics. These are synthetic
project design examples. They add no publisher claim or released v1 field.

| Proposed field | Type and meaning |
| --- | --- |
| `x_t0_selection_rule.proposal_version` | Exact `cd13-0.1`; one bounded rule-input binding, not a general ruleset |
| `build_sha256`, `answer_states_sha256` | 64 lowercase hexadecimal characters; each binds the complete original UTF-8 byte sequence, including whitespace and unrelated fields |
| `rule.id`, `rule.version` | Full-string canonical rule ID and bounded exact version string in the frozen semver shape; changes do not inherit another rule/version's answers |
| `rule.kind` | One canonical frozen component kind; no arbitrary first or primary selection is chosen |
| `rule.quantifier` | Exact `all_enabled`; evaluate every enabled selection of that kind |
| `rule.severity` | `info`, `warning` or `error`, fixed independently of every finding and overall outcome |

Each applicability/assertion answer lives at the literal JSON Pointer
`/selection_checks/{selection_id}/{rule_id}/{rule_version}/{field}`, where
`field` is `applies_when` or `assertion`. Tokens are escaped as JSON Pointer
tokens, not interpreted as dotted paths or positions in the build's selection
array. For example the fixture's assertion is
`/selection_checks/sel_tool/rule.fixture.cd13/0.1.0/assertion`. Grouped parent
objects and unresolved parents retain CD-1's source path and state behavior.

The reader first validates the sidecar and complete-byte bindings, the frozen
build's schema and integer revision, and build-wide selection identity/role
uniqueness. Selection IDs and roles must match their entire canonical string;
a terminal newline is rejected even though the frozen regex's `$` can accept it.
Disabled and unrelated-kind entries still participate in identity preflight.
Every provided Boolean operand for the scoped kind is then type-checked,
including disabled selections and assertions whose applicability will be false
or unresolved. Numeric/string aliases and malformed parent traversal reject
before a predicate runs. Existing CD-1 and CD-13 implementations are unchanged.

The caller must establish eligibility separately for **each** selection's
applicability and assertion operand. Omitted, unresolved or ineligible inputs
cannot become known facts merely because they have a value or source label.
Even a provided false applicability answer only produces `skipped` when that
answer is eligible. Otherwise applicability remains `unknown`; a known eligible
assertion false remains a counterexample only under known eligible applicability.
Missing, unknown, withheld and not-applicable CD-1 answers all stay unresolved
for this compatibility predicate, with their distinct states retained. This
does not change the separate recommendation policy or required-component layer.

The accepted CD-13 reducer retains individual pass/fail/unknown/skipped findings,
keeps a definite failure alongside other selections' unknowns, and distinguishes
an empty enabled scope from an entirely inapplicable scope. Results also retain
the exact rule version, all scoped answer states (including disabled entries)
and per-operand eligibility. Repeated evaluation cannot inherit an earlier
eligibility decision. The binding never requires a framework for a tool: W-R3's
explicit no-framework path remains available.

This reader performs schema and selection-identity preflight; it does not supply
the remaining catalog/version, relationship or evidence-resolution preconditions
from the frozen validation protocol. Callers must establish those prerequisites
before treating their Boolean rule inputs as eligible. A digest binds bytes; it
does not authenticate a rule, source, support claim or complete build. Arbitrary
predicate expressions, relationship joins, catalog/source eligibility, final
result wire format and actual successor migration remain separate integration.
#40 and affected T4/other consumers must review this exact proposal before a
versioned adapter/ruleset adopts it. Historical build bytes and frozen findings
remain unchanged; #42's native #40 prerequisite remains in place.

Routing from the reviews:

| Source | Decision | Routed to |
| --- | --- | --- |
| T2-C01 | Price dimensions; canonical storage unit is decimal GB, with the source value kept | #39, then #40 |
| T2-C02 | Capacity intervals in the next ResourceEstimate | CD-2/CD-3 |
| T2-C03 | Allocation and topology | CD-2 |
| T2-C04 | Conditional engine support | CD-3, CD-6 |
| T2-C05 | Host completeness and mount relationships | CD-3, CD-6, CD-9 |
| T2-C06 | Multi-version intake and retention | CD-7, #41, #42 |
| T1 gaps 1–4 | Offering identity, budgets, tokenizer and lineage, price applicability | CD-6, CD-11, CD-5/CD-6, #39 then CD-7 |
| T1 limits (#123) | Typed, stage-specific limits for non-text inputs and outputs (units such as seconds, rows and pixels, never forced into token fields) | CD-11, CD-3 |
| T6 drafts (#113, #118, #120, #121) | New price meters G1–G10; monitoring enums, `content_capture`, multiple exporters and telemetry edges; guardrail `supported_enforcement[]` and `operated_by` | #39 then #40; CD-4 for telemetry destinations |
| T4 findings 1–7 (#25–#28, merged in #124) | Multi-selection quantifier (CD-13); memory-framework rule review (`on_unknown: review`, severity changed in a ruleset version); MCP transports, protocol versions and client capabilities; MCP hosting through #81's `deployment` object, with the air-gap rule folded into W-R8; credential resolution (T4-B6); side-effect classes and tool metrics; memory evidence fields; injected-token metric as a component of `input_tokens.max`; framework fields; snapshot-date `version` for unversioned hosted services | CD-13, CD-6, CD-4, CD-7, CD-3; #39 for meters and rate limits; #41 for versioning; #2 for the memory persistence need |
| #42 partial proposal (#114) SB-1 to SB-10, SB-R1 to SB-R5 | Saved-build record gaps (assumptions, snapshot and pricebook revision locks, visibility, derived validation state, fork lineage, several workloads, `withheld` answer state, where cross-record checks live) and integrity rules | #40; SB-8 with CD-1; SB-7 with #10 |

### CD-6 concrete credential-binding wire experiment (2026-10-18)

**Engineering decision for this candidate:** represent each tool's explicit
credential source in a closed, versioned sidecar bound to the exact retained
Build and CD-7 pin-file bytes. This makes the
[T4-B6 proposal](../T4-agents-integrations/tools-apis.md#t4-b6-rulet4toolcredentialref-credential-source-and-resolution-needs-contract-change-via-40)
readable from concrete fixtures, beyond the earlier normalized-Boolean
[experiment](../../tests/credential_binding_prototype.py). It chooses a testable
wire shape for review; it does not adopt a successor contract or resolve the
receiving authorization, connection-boundary or saved-build decisions.

The [closed schema](../../tests/fixtures/t0-credential-bindings.schema.json),
[example](../../tests/fixtures/t0-credential-bindings.json),
[read-only reader](../../tests/t0_credential_wire_prototype.py) and
[regressions](../../tests/test_t0_credential_wire.py) use the unchanged fictional
v1 examples and the accepted
[CD-7 exact artifact resolver](../../tests/t0_revision_lock_prototype.py)
([#273](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/273)).
The sidecar's `x_t0_credential_bindings` object contains:

| Field | Candidate representation and meaning |
| --- | --- |
| `proposal_version` | Exactly `cd6-0.1`; other versions require a separate reviewed reader |
| `build_sha256` | Exactly 64 lowercase hexadecimal characters, checked against the original Build bytes |
| `revision_locks_sha256` | Same digest shape, checked against the complete supplied CD-7 sidecar bytes, including formatting |
| `bindings` | At most 1,000 explicit choices; an empty array supplies no credential source |
| `bindings[].selection_id` | Exact retained tool-selection ID, using the canonical 3–80 character selection-ID grammar with full-string validation |
| `bindings[].source` | `direct`, `integration`, `model_provider` or `none`; no automatic or role-based choice |
| `bindings[].auth_method` | One explicit `api_key`, `oauth2`, `service_account` or `mTLS` method for authenticated sources; exactly `none` for source `none` |
| `bindings[].target_selection_id` | Required only for inherited integration/provider sources; exact retained connection-selection ID |

Unknown properties and credential-reference fields are rejected by the sidecar.
The current method vocabulary comes from the frozen
[selection settings](../../contracts/v1/schemas/selection.schema.json) and
[catalog specs](../../contracts/v1/schemas/catalog-item.schema.json); future
authentication modes need a versioned change, not string coercion.

The reader validates the Build and selected `(catalog_item_id,
catalog_item_version, kind)` through CD-7. It never chooses the newest artifact
or another available item version. Missing pins, unavailable retained revisions
and digest mismatches retain their distinct catalog status and yield `unknown`
requirements. A supplied credential sidecar without the CD-7 file leaves its
required digest **unverified**: `revision_binding` is `revision_pins_missing`
and each applicable explicit choice has an unknown
`credential_revision_pins_bound` check. This cannot produce a fully bound
metadata `pass`. The status remains visible when tools are disabled. The other
statuses are `credential_sidecar_missing` and `exact_pin_bytes_verified`; the
latter verifies only the sidecar byte binding, not catalog availability or
authorization. A different supplied Build or pin file is an input error.

Before constructing lookup maps, CD-7's inherited identity check rejects
duplicate selection IDs and duplicate `(kind, role)` pairs across the entire
Build, including disabled entries. This reader also rejects duplicate link
IDs, dangling endpoints and identifiers with trailing control characters.
Every enabled tool gets its own result. The outer `Selection.enabled` field
controls participation; nested settings do not establish effective runtime
enablement. Disabled tools are `skipped`, and an empty tool inventory has no
tool results. Missing bindings remain `unknown` even when a local reference
exists. Repeated or competing binding records remain `unknown` rather than
being deduplicated or selected by array order.

For `direct`, only the selected tool's opaque reference presence is required.
For an inherited source, the exact target must exist, have the expected kind,
be enabled, resolve to its selected catalog version and contain a reference.
Exactly one tool-to-target `provided_by` link is required: no link is a known
failure, while repeated matching links with different IDs remain ambiguous.
An `exposes` link, an item association or another connection cannot replace
the explicit target. Conflicting tool-local and inherited references remain
`unknown`, even when the strings are identical; neither overrides the other.

Positive selected-auth membership and an integration's
`associated_tool_refs` membership establish only catalog metadata presence.
Absent, empty or unlisted entries are `unknown`: the frozen lists have no
completeness marker supporting a negative conclusion (CD-3). Explicit `none`
therefore passes this bounded metadata check only with positive `none` support.
Provider targets retain unknown `provider_hosted_execution_evidence` and
`provider_api_operation_evidence` checks because frozen v1 has no fields proving
that execution location and exact provider/API operation tuple. A provider
name, API URL, link or reference does not fill either gap. Eligible source
evidence and the chosen deployment's actual support remain separate #41/CD-3
and affected-owner review inputs.

Known missing required references or absent/disabled/wrong-kind targets fail;
unresolved versions and support remain unknown. A known failure takes
precedence while its other unknown checks remain available. Per-tool severity
is fixed at `error` with `on_unknown: review`. Results contain validated
selection IDs, fixed status/check codes and the Build digest, never opaque
reference strings or submitted free-form text; invalid-input diagnostics are
also sanitized. `authorization: not_evaluated` and
`secret_resolution: not_performed` remain explicit. This is neither secret
resolution nor a public/share export format, and a metadata pass proves no
credential validity, effective grant, scope, entitlement or permission to run.

The published example deliberately fails for its missing direct reference.
Positive cases use only fictional opaque locators. The regressions cover
exact-byte authority, legacy absence, source choice, inherited links,
identity/role ambiguity, completeness, per-selection outcomes, sanitized
diagnostics and immutable input/history. Run
`python -m unittest discover -s tests -p test_t0_credential_wire.py -v`.

The retained v1 Build, schemas, examples, evaluator and historical outcomes
are unchanged. This sidecar does not silently migrate saved builds or alter
the active CD-2/CD-7 work. Before adoption, #40 still needs the successor
schema/reader/ruleset and migration decisions with actual receiving review;
#35 owns effective authorization/scope review, #13 the connection boundary,
and #42 saved/share handling and its existing prerequisite. These fixtures
provide mechanics for that review, not receiving acceptance or issue closure.

## Cycles and recomputation (Proposal)

- **Rules evaluate; they never change selections.** Model ↔ GPU ↔ engine is a cycle in the dependency graph, not in evaluation. Every rule is a function of the current selections, links, catalog snapshot and evidence, so evaluation needs no ordering and always terminates.
- **Recompute by participants.** Index each rule by the selections and fields it reads (`affected_kinds` plus its pointers). When a selection, link, catalog item, evidence record, policy or ruleset version changes, re-evaluate only the rules that read it.
- **Recommendations are separate from verdicts.** Ranking or suggesting alternatives may search over candidates, but the verdicts it shows come from the same pure evaluation.

## Versioning (Proposal)

- **Rules:** v1 versions rulesets, not rules. Keep that. Give each published ruleset a semantic version and changelog; a saved build pins the ruleset version it was evaluated with (#42) and is re-evaluated on upgrade.
- **Catalog:** keep one version per ID until CD-7 adds ID+version resolution, then retain every version referenced by a saved build, evidence record or rule. A new release changes no existing outcome by itself.
- **Validity windows:** derive `valid_from`/`valid_to` from catalog snapshot revisions rather than adding per-item fields, unless CD-7 decides otherwise.

## Contract versions and migration (CD-7, Proposal)

**Constraints from v1.** The import is frozen: a next version is a new sibling (`contracts/v1.1/`, later `contracts/v2/`) that carries its own generator, schemas, docs, fixtures and tests, and the import-hash test keeps v1 untouched (`contracts/v1/ADOPTION.md`). v1 pins `schema_version` to `1.0.0`, the build rejects unknown top-level fields, and only namespaced `x_` keys are allowed in `extensions` (`common.schema.json`).

**v1.1, additive.** A v1.1 reader accepts every 1.0.0 document unchanged, and a 1.0.0 document evaluates exactly as before under the v1 baseline ruleset.

| Area | Additions | Source |
| --- | --- | --- |
| Selections | Per-component `deployment` object (`runtime_operator`, `runtime_supplied_by`, `capacity`, `placement`); `licence_answers` | #81 |
| Build | Build-owned `workload` profile, including the CD-12 organisation attestations; `destinations`; typed answer states (CD-1), including `withheld` (#114 SB-8) | #81, #114 |
| Links | Optional `role` and an access attribute (mount vs fetch) | CD-6, T2-C05 |
| Locks | Catalog-snapshot and pricebook revisions | #114 SB-2, SB-3 |
| Catalog | Artifact `quantization` and `components`; device memory kind, bandwidth, instruction sets, NUMA nodes; list-completeness metadata; `context_semantics` and `max_input_tokens` | #81, CD-3, CD-11 |
| Results | Outcome reason codes; a `disputed` flag; evidence labels (checked, verified) | #126, #127 |
| Ruleset | v1.1 baseline ruleset: the 17 self-hosted rules re-gated on the component's mode; the two membership rules return `unknown` on omission from unmarked lists | This record |

**v2.0, breaking.**
- One workload record: remove the `objectives` and `workload` selection copies.
- `deployment_mode` becomes derived; the catalog kind and its selection are removed.
- The evaluator treats the string `"unknown"` only as a typed answer state.

**Reading 1.0.0 builds under v1.1** (a migration adapter; the original bytes are kept):
1. **Mode.** Preserve the legacy build-level `deployment_mode` label for historical v1 evaluation. Populate each new component deployment only from eligible component/offering evidence or an explicit answer identifying its runtime operator and, for provider operation, capacity. A build-level label alone never supplies those facts, including labels `api`, `managed` and `self_hosted`. Unresolved component facts remain `unknown`; derive the new overall mode only after evaluating the components under #81.
2. **Workload.** Build a profile from the three copies with this precedence: build `objectives`, then the `workload` selection's settings, then a catalog `workload` preset. Values that disagree are flagged for the user rather than silently merged.
3. **Locks.** A lock without a snapshot or pricebook revision is marked "cannot be reproduced exactly" (#114).
4. **Rulesets.** Show results under both the 1.0.0 and 1.1.0 rulesets, with the per-rule differences, as #114's revisit states describe.

**Before v1.1 lands.** Prototype the proposed fields only in synthetic fixtures under `tests/`, using `x_t0_*` extension keys. Never put them in catalog proposals.

**Acceptance for v1.1.**
- Every v1 example still validates and evaluates identically under the v1 ruleset.
- Migration tests cover the cases below, including independent component modes, conflicting workload copies and a lock without a revision.
- The affected workstreams are listed in the changelog.

### CD-7 exact catalog and pricebook pin experiment (2026-10-18)

**Engineering decision for the candidate:** retain explicit positive integer
revisions alongside catalog/pricebook IDs, using the artifact's existing revision
value. Do not reinterpret an ID as inherently unique per revision, infer a
revision from a date, or select the only/latest available artifact. This chooses
the explicit-revision option in #114 SB-2 and the pricebook part of SB-3. The
frozen [build locks](../../contracts/v1/schemas/build.schema.json),
[catalog snapshot](../../contracts/v1/schemas/catalog-snapshot.schema.json) and
[pricebook](../../contracts/v1/schemas/pricebook.schema.json) were inspected at
`a9f0e6efd67e8d7d7ddf1327e95b000c20e8f5f3` on 2026-10-18: the artifacts have
revisions, while the build locks retain only their IDs. This is a contract fact;
the following sidecar and digest policies are new project design choices.

The [schema](../../tests/fixtures/t0-revision-locks.schema.json) and
[fixture](../../tests/fixtures/t0-revision-locks.json) select this synthetic shape:

```text
x_t0_revision_locks:
  proposal_version: "cd7-0.1"
  build_sha256: SHA-256 of the original UTF-8 build bytes
  artifacts:
    catalog_snapshot: {id, revision, sha256}
    pricebook: {id, revision, sha256}  # only if the build locks a pricebook
```

Hashes bind the exact retained bytes, including whitespace, rather than an
unstated canonical JSON serialization. A digest is an integrity comparison,
not source authentication, evidence verification or a right to retain/display
the document. The sidecar's artifact IDs must match the build's IDs. Editing,
redacting, forking or reserializing the build invalidates this sidecar's byte
binding; it cannot silently transfer assertions or pins to another document.
All supplied pins require a full-string canonical ID (3–120 characters, without
whitespace/control suffixes), an integer revision and a lowercase 64-digit digest.
An absent pin is allowed so the reader can explain a legacy omission. A
malformed supplied pin is rejected rather than treated as a missing answer.

The [offline archive](../../tests/t0_revision_lock_prototype.py) validates the
retained frozen-format fixture documents using the local schema registry and
strict JSON parsing. It rejects duplicate artifact keys, duplicate catalog
ID/version pairs and duplicate rate IDs. Exact-key lookup distinguishes:

| Condition | Resolution result |
| --- | --- |
| No revision pin, even with one available candidate | `revision_pin_missing` |
| Exact kind/ID/revision absent, including when a newer revision exists | `pinned_revision_unavailable` |
| Exact key present but retained bytes disagree with the selected digest | `content_digest_mismatch`; no artifact values returned |
| Exact key and bytes agree | `resolved` for that artifact only |

For a resolved catalog, every enabled selection binds its exact item ID and
version, then checks kind. A known absent version or wrong kind is an explicit
membership-integrity diagnostic; it is not a claim of unsupported capability.
An unresolved snapshot cannot establish missing membership. Disabled selections
are identified separately; build-wide identity/role ambiguity is still rejected
before resolution, reusing CD-13's preflight. Distinct versions of the same item
ID can coexist in this test-only archive and are selected without order
dependence. Frozen intake still requires one version per ID, and the frozen
evaluator must not be used to interpret this proposed multi-version behavior.

The original build bytes and resolved artifact bytes are retained unchanged;
returned item dictionaries are detached from each other and subsequent reads.
The [20 synthetic test methods](../../tests/test_t0_revision_locks.py) exercise
the wire schema, actual fixture resolution, newer/absent/tampered versions,
partial catalog/pricebook resolution, selection membership and input isolation,
strict duplicate/nonfinite handling and unchanged historical v1 evaluation.
Run `python -m unittest discover -s tests -p test_t0_revision_locks.py -v`.

This completes a reviewable revision and membership-binding candidate for
CD-7/SB-2 and part of SB-3/SB-R1. It does not claim complete replay: evaluator,
ruleset, graph, derived estimates and external evidence must still be retained
and resolved under their own exact pins. It neither applies price eligibility
or rights policy nor interprets arbitrary catalog references, migrates a build,
publishes a successor reader/ruleset, or generates a current report. Those
integration decisions remain with #40/#41/#39/#42. The technical candidate can
be reviewed independently of named receiving-owner adoption; #40 remains open
and #42's substantive #40 prerequisite is retained. The
[partial saved-build note in #114](https://github.com/Pick-Your-AI/pick-your-ai-research/commit/649f5870e9729ec1aaf1b5f07e9290ce0f777833)
is now merged; that delivery does not adopt this candidate or release a
successor contract.

### CD-7 native consumer envelope candidate (2026-10-18)

**Engineering decision:** reuse the merged CD-7 archive and sidecar rather than
invent another exact-revision resolver. Add a separately versioned inspection
envelope, `cd7-consumer-0.1`, for native receiving adapters. The
[request/result schema](../../tests/fixtures/t0-cd7-consumer.schema.json),
[request bytes](../../tests/fixtures/t0-cd7-consumer-request.json),
[result bytes](../../tests/fixtures/t0-cd7-consumer-response.json),
[negative response matrix](../../tests/fixtures/t0-cd7-consumer-negative.json)
and [reference adapter](../../tests/t0_cd7_consumer_prototype.py) are synthetic
test artifacts. They leave the original CD-7 sidecar, frozen documents,
generators and historical evaluator unchanged. This selects a receiving
interface for the CD-7/SB-2 integrity work; it is not a v1.1 release or a
publisher manifest.

The request names the SHA-256 of the exact build bytes, the SHA-256 of the exact
sidecar bytes (or explicit `null` when absent), and the receiving byte limit.
Those two documents are supplied separately as immutable UTF-8 bytes. The
result binds the exact request bytes and build bytes. A client must retain
them; equivalent JSON serialization is not an interchangeable request. The
schema resolves its references through the local frozen schema registry and
the existing CD-7 pin schema, registered at `urn:pick-your-ai:cd7-pins:0.1`.
There is no HTTP endpoint or network retrieval in this experiment.

| Result boundary | Required interpretation |
| --- | --- |
| `revision_pin_missing` | No pin exists; omit the revision and artifact. A sole available artifact does not supply a pin. |
| `pinned_revision_unavailable` | The exact requested kind/ID/revision is absent; never substitute a newer revision. |
| `content_digest_mismatch` | Retained bytes disagree with the pin; return no artifact. Preserve this observed failure even when a producer also reports unavailability or revocation. |
| `native_revision_unsupported` | A positive revision exceeds signed 64-bit range. Omit the numeric revision and artifact; retain the original request/sidecar for inspection. Never round, truncate, wrap or reinterpret it as a missing pin. |
| `artifact_too_large` / `artifact_structure_unsupported` | Bytes fail the receiving profile; return no artifact and retain independent outcomes for the other artifact. |
| `artifact_representation_unsupported` | The descriptor's capture timestamp is outside the new ASCII profile, even if the frozen timestamp format checker admits its Unicode decimal digits. Return no artifact; frozen-v1 validation remains unchanged. |
| `revoked` / `temporarily_unavailable` | An external producer adapter explicitly withholds this exact kind/ID/revision. The fixture adapter can represent these dispositions; it does not discover revocation or implement a publisher. |
| Per-artifact `resolved` | Exact bytes, frozen structure and this artifact identity agree. This conveys no price eligibility, capability or publication/source-use approval. |
| Selection outcomes | Preserve `not_enabled`, `snapshot_unresolved`, `selected_version_absent`, `selected_kind_mismatch` and `resolved`. Only a resolved selection carries its exact ID/version/kind reference. |

Each resolved artifact descriptor includes `kind`, `schema_version`, exact ID,
revision, the document's unchanged `captured_at` string, exact-byte SHA-256,
byte length and `/artifacts/sha256/{digest}.json`. This is a proposed immutable
retrieval path under a separately configured trusted HTTPS origin. A transport
adapter must keep it on that origin, reject credentials, query strings,
fragments and redirects, check the advertised length before transfer, and also
bound actual bytes. Descriptor/path equality with the digest is rechecked;
accepting a syntactically valid path is insufficient. CD-7 `catalog_snapshot`
maps explicitly to Apple's internal `CatalogArtifact.catalog`; frozen schema
field names remain unchanged.

**Complete-pair boundary.** Catalog and pricebook results remain independent.
The pair is `resolved` only when both resolve and every price rate's exact
`catalog_item_id`/`catalog_item_version` exists in this catalog. An unresolved
side produces `incomplete`; a cross-catalog rate produces
`rate_catalog_mismatch` with sorted unmatched rate IDs. A build without a
pricebook produces a `null` pricebook binding and `pricebook_absent`. None of
these states synthesizes an empty pricebook or a zero price. Catalog item
references other than price-rate membership, source-use rights, billing
eligibility, currency/date/region applicability and full evaluator replay
remain separate decisions.

The pair's deterministic `identity` is the SHA-256 of the ASCII bytes
`cd7-consumer-0.1` plus one LF byte, followed by compact JSON containing exactly
the `catalog_snapshot` and `pricebook` descriptors. Sort every object key
lexicographically, use no insignificant whitespace or escaped solidus (`\/`),
encode JSON integers without a decimal/exponent, and preserve descriptor strings unchanged. All
descriptor fields in this profile have ASCII values; the new descriptor schema
explicitly restricts `captured_at` to ASCII in addition to the frozen timestamp
format. This binds both artifacts
and their metadata in fixed roles. It is an integrity identity, not a publisher
release identity, signature or publication receipt.

`verify_complete_pair` checks the received request binding, lengths and exact
hashes, strict raw JSON, full frozen CatalogSnapshot and Pricebook schemas,
immutable identities, duplicate members and catalog/rate relationships. It
then reproduces the complete result from the supplied bytes and rejects any
descriptor, path, selection or pair disagreement. It returns the original two
byte strings only after all checks pass. Native callers must validate through
their complete typed boundaries and atomically activate the complete pair;
partial/error/cancelled refreshes preserve the previous pair. No cache is
written by this reference function, and its result cannot admit production.

**Receiving profile and migration.** New envelope integer fields require JSON
integer tokens in `1...9223372036854775807` for revisions. The existing CD-7
resolver also requires integer tokens; frozen JSON Schema's mathematically
integral-number semantics are unchanged. The profile defaults to 512 KiB per
build/artifact, permits an explicit receiving maximum up to 64 MiB, and caps
request/result/sidecar envelopes at 64 KiB. It also caps values at 48 levels
(root is level one) and 16,384 value nodes per document, rejecting duplicate
decoded keys, canonically equivalent Unicode object keys, invalid UTF-8,
isolated surrogate escapes in keys or values, and nonfinite numbers. Correctly
paired surrogate escapes and other valid Unicode scalars remain accepted. It
does not normalize retained bytes. Each native adapter
applies the stricter of these negotiated limits and its own parser, transport
and memory limits. These are new consumer-profile constraints, not additional
claims about frozen-v1 conformance.

Receiving source inspection on 2026-10-18 included Apple's
[catalog cache](https://github.com/Pick-Your-AI/pick-your-ai-apple/blob/a12ab324e499907bd15abf4b80709d0f02667ae1/Packages/PlannerCatalog/Sources/PlannerCatalog/CatalogCache.swift)
and [bounded transport](https://github.com/Pick-Your-AI/pick-your-ai-apple/blob/a12ab324e499907bd15abf4b80709d0f02667ae1/Packages/PlannerCatalog/Sources/PlannerCatalog/PublicArtifactClient.swift),
and Android's
[verified artifact cache](https://github.com/Pick-Your-AI/pick-your-ai-android/blob/526c05c6528be1313bb8b1bf71b89cc131eb2d75/core/src/main/kotlin/ai/pickyour/core/cache/VerifiedArtifactCache.kt).
Apple's internal preview cache manifest and Android's caller-supplied hash
boundary do not supply publisher authority. Apple already has a typed
Pricebook decoder in PlannerCore; raw-parser and cache wiring changes remain
client implementation work. The Python prototype checks value structure after
decoding; it does not demonstrate native protection before allocation.

**Scoped receiving review.** Both in-session Apple and Android engineering
lanes independently reviewed this packet, including the final ASCII timestamp
correction at local source `f301b1b2f5574be968fb715e40ffafc9e9876826`,
the shared schema and adapter, and ran all 19 focused methods including 21 portable response
mutations. Android also reproduced and then verified the correction for
isolated surrogate escapes; Apple verified the immutable-source links and
unescaped-solidus pair encoding. A separate coordinating engineer reproduced
the Unicode-decimal timestamp gap and reviewed its new-envelope correction;
both native lanes rechecked that correction with frozen-v1 acceptance retained.
Both accepted the resulting interface as
technically suitable for native inspection and complete-pair integrity adapter
reuse, with no remaining blocker in that scope. The reviewed adapter, schema
and test blobs are respectively
`4887aeb101e36ceee121132e82af72e0d84505b4`,
`be473bff00f1335313a8fb83280f2bbd352a32b4` and
`506557082a72ee2e9da877aecc1946f7e7643481`.
These are actual in-session technical receiving reviews. They do not
impersonate a named maintainer or claim publisher/source-rights approval,
native implementation/device execution, production adoption or full #40/#42
acceptance. The later documentation-only receipt preserves all six reviewed
implementation/schema/fixture/test blobs unchanged.

The `qualification` object is deliberately fixed to `publication` and
`source_use` both `not_established`; an `approved` field or value is invalid.
A future, separately reviewed publisher adapter must bind a real release to
both exact descriptors and an authenticated publication receipt, distinguish
synthetic from real provenance, and evaluate evidence for each requested
source use. This packet neither invents that evidence nor changes Apple's
closed production gate. Research acceptance can assess this bounded technical
interface independently of those external evidence stages. The
[focused tests](../../tests/test_t0_cd7_consumer.py) include exported wire
replay, 21 portable response mutations, independent missing/mismatch outcomes,
native integer bounds, raw JSON ambiguity, resource limits and cross-catalog
rate rejection. Run `python -m unittest discover -s tests -p
test_t0_cd7_consumer.py -v`. #40 and #42 remain open for their remaining
contract/migration, replay and receiving requirements.

## Contribution format

Use `templates/rule-proposal.md`, plus these conventions:
- one fixed severity per rule;
- reason codes rather than extra clauses;
- examples covering pass, fail, unknown, skipped, and a disputed case where evidence can conflict;
- new contract needs stated as CD candidates with migration notes.

## To do

- T1/#40 worked-example review is [recorded on #126](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/126). Other affected-owner dispositions remain separate.
- T5 routing is accepted with constraints by @zwright8 in #126; the source-specific #10/#31/#39/#30/#32/#33/#36/#37 decisions remain with their owners.
- The synthetic CD-7 projection experiment below now exercises migration boundaries. A released v1.1 adapter, actual evidence resolution, schema/generator changes and consumer acceptance remain open.

## Claim-source traceability audit

Inspected 2026-10-18 at [`61e1c9a83bbcd22a672b53e06c544ee3ddd7689d`](https://github.com/Pick-Your-AI/pick-your-ai-research/tree/61e1c9a83bbcd22a672b53e06c544ee3ddd7689d). This record's factual claims concern the imported contract and recorded project decisions; its candidate designs and worked quantities are explicitly proposals/synthetic examples, not vendor measurements. The consolidated dictionary delegates publisher-specific evidence to the cited companion dictionaries and their dated primary-source ledgers. This audit does not independently reproduce those publisher claims or approve the proposed wire shapes.

| Claim group | Primary project source, inspected 2026-10-18 | Check and boundary |
| --- | --- | --- |
| 45 baseline rules; 17 rules gated on literal self-hosted mode | [Frozen baseline](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/61e1c9a83bbcd22a672b53e06c544ee3ddd7689d/contracts/v1/baseline/core-ruleset.json) | Parsed `rules`: 45 entries; 17 `applies_when` expressions contain `self_hosted`. These are code counts, not benchmark results |
| Incomplete-list membership behavior | [Baseline](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/61e1c9a83bbcd22a672b53e06c544ee3ddd7689d/contracts/v1/baseline/core-ruleset.json), [reference evaluator](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/61e1c9a83bbcd22a672b53e06c544ee3ddd7689d/contracts/v1/reference/evaluate.py) | `rule.engine.model.format` uses `intersects`; `rule.precision.engine` uses `contains`. The proposed completeness gate is not implemented by frozen v1 |
| Existing field names, versions and extension boundary | [Canonical schemas](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/61e1c9a83bbcd22a672b53e06c544ee3ddd7689d/contracts/v1/schemas), [adoption policy](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/61e1c9a83bbcd22a672b53e06c544ee3ddd7689d/contracts/v1/ADOPTION.md) | Catalog/build/ruleset/snapshot/graph shapes are contract facts; `schema_version` is 1.0.0. Build extra-field rejection and common `x_` extension namespace are inspected in their schemas |
| Outcome, conflict and rule-family decisions | Owner reviews linked in the introduction ([#75](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75#pullrequestreview-5550616927), [#67](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/67#pullrequestreview-5550697545), [#88](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/88#pullrequestreview-5554964868)); [#41 record](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/61e1c9a83bbcd22a672b53e06c544ee3ddd7689d/research/T0-configuration/catalog-data-sources.md) | Project decisions, not new universal compatibility claims; preserve scope and fixed severity |
| Workload/deployment field evidence and modes | [Workload](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/61e1c9a83bbcd22a672b53e06c544ee3ddd7689d/research/T0-configuration/workload-use-case.md), [deployment](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/61e1c9a83bbcd22a672b53e06c544ee3ddd7689d/research/T0-configuration/deployment-mode.md) | Their field dictionaries map conditions to dated C/E/D primary-source references. Open CD shapes remain unresolved; examples in this consolidation add no price or performance claim |
| 24 v1-valid T4 rule proposals and accepted queue scope | [T4 summary](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/61e1c9a83bbcd22a672b53e06c544ee3ddd7689d/research/T4-agents-integrations/README.md), [#40 disposition](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40#issuecomment-6242626523) | Count describes contributed proposal pointers, not approved executable rules; retain the queue-only disposition |
| T5 routing and later T6/saved-build inputs | [T5 summary](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/61e1c9a83bbcd22a672b53e06c544ee3ddd7689d/research/T5-training-fine-tuning/README.md), [#126 receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/126#pullrequestreview-5560506323), linked draft PRs in the routing table | Routing accepted with constraints; #114 and T6 drafts do not become merged decisions through citation |
| M1–M5 and T1/T2 worked quantities | [Synthetic fixtures](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/61e1c9a83bbcd22a672b53e06c544ee3ddd7689d/tests/fixtures/t0-migration.json), [projection tests](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/61e1c9a83bbcd22a672b53e06c544ee3ddd7689d/tests/test_t0_migration.py) | Synthetic semantic examples only; no access date, region or currency is invented for nonexistent vendor measurements |

## Acceptance criteria coverage

| Criterion (issue #40) | Where | Status |
| --- | --- | --- |
| Schema document with field types and examples | What v1 provides; consolidated next-version dictionary; #81 field dictionaries; CD-7 examples | Consolidated research shapes and examples; final encodings and affected-owner acceptance remain open |
| Worked rule examples spanning T1/T2, including `unknown` | Synthetic worked examples below | T1/#40 scoped acceptance in #126; broader handoffs remain open |
| Approach to cycles and recomputation | Cycles and recomputation | Proposed |
| Rule and catalog versioning | Versioning; Contract versions and migration | Proposed |
| Contribution format | Contribution format | Proposed |
| Deployment modes covered | Rule format, item 7; #81 | Proposed |
| Rule format, severities, `unknown` handling | Rule format and outcome semantics | Decided in reviews |
| Primary sources with access dates | Claim-source traceability audit; companion primary-source ledgers | Contract/project claims traced with inspection date; synthetic quantities and proposed fields remain explicitly separate |
| Handoffs confirmed | — | Open |
| Open questions with owners | Contract decisions; #81 | Partial |
| Decision record merged | PR #126 | Merged partial record; not issue completion |

## Synthetic migration cases for CD-7 review

These are proposed acceptance examples, not measured configurations or a migration implementation. Preserve original v1 bytes and historical outcomes in every case.

| Case | Input | Required migrated interpretation |
| --- | --- | --- |
| M1 | Legacy build label `api`; model offering documents provider/shared runtime; retrieval service explicitly operated by user | Model `api`, retrieval `self_hosted`, derived build `hybrid`; the old label cannot overwrite retrieval evidence |
| M2 | Legacy build label `managed`; component operator/capacity absent | Component `unknown`; do not infer dedicated/reserved capacity from the legacy label |
| M3 | Legacy build label `self_hosted`; model is user-operated, external moderation **model** offering provider/shared | Primary model `self_hosted`, moderation model `api`; derive hybrid over applicable serving components. A `guardrail` selection alone does not set mode |
| M4 | Build objectives and workload settings disagree | Preserve both source values and flag a decision; do not manufacture a reconciled workload |
| M5 | Lock references a pricebook ID without revision | Historical cost cannot be reproduced exactly; do not substitute the latest revision silently |

The [synthetic fixtures](../../tests/fixtures/t0-migration.json) encode M1–M5 and additional boundary cases. The [test-only projection prototype](../../tests/t0_migration_prototype.py) takes already-normalized eligible fixture facts in `x_t0_migration_inputs`, preserves original historical bytes and emits a separate `x_t0_migration_projection`. It does not parse arbitrary real selections, resolve source conflicts or publish a next-version schema. Null means missing fixture evidence, not a contract answer encoding.

Run `python -m unittest discover -s tests -p test_t0_migration.py -v`. The tests cover all operator/capacity pairs, unknown dominance, non-serving/disabled components, adapter inheritance and missing/cyclic/disabled bases, rejection of unrelated serving kinds as adapter bases, duplicate IDs, conflicting workload copies including zero, absent snapshot/pricebook revisions, and unchanged v1 historical evaluator findings. They are synthetic semantics checks, not runtime measurements or validation of a released migration adapter. The separate CD-7 pin experiment above now resolves actual retained fixture snapshot bytes; a released resolver and dual-ruleset evaluation remain future versioned implementation.

## Worked rule examples for receiving-owner review

The quantities and labels in this section are synthetic fixtures, never catalog evidence or measurements. They illustrate the proposed families; #40 co-owners and affected T1/T2 owners still decide adoption.

| Family | Synthetic inputs | Expected interpretation |
| --- | --- | --- |
| Joint format support | Artifact format A; engine's version-matched exhaustive supported set contains A | `pass`; source checked does not mean independently reproduced |
| Joint format support | Artifact format A absent from an exhaustive version-matched set | `fail`; if list completeness is unknown, `unknown/missing_evidence` instead |
| Memory fit | Estimated demand [10,14] GiB; usable pool 12 GiB under identical placement/dtype/admission scope | Conservative upper demand does not fit: `fail`, labelled may not fit and estimated; no measured OOM is claimed |
| Memory fit | Demand or pool scope cannot be matched to the selected rank | `unknown/missing_evidence`; do not combine unmatched memory pools |
| Context/KV | Native context 8,000 tokens, input 7,000 plus reserved output 2,000, same tokenizer and shared-session semantics | Context predicate `fail`; a separate KV/memory predicate still needs its own evidence |
| Context/KV | Independent input/output caps, input 7,000 under input cap 8,000 and output 2,000 under output cap 4,000 | Both budget predicates pass; do not compare their sum against either separate cap |
| Applicability | No adapter selected | Adapter-only predicate `skipped/not_applicable`; a missing adapter lineage on a selected adapter is `unknown` |

The context rows above also have [executable synthetic CTX-01/02 cases](../../tests/test_context_budget.py)
and a [test-only arithmetic prototype](../../tests/context_budget_prototype.py).
They distinguish shared and separate budgets, upper-bound decisions, missing
operands, exact-route applicability and native-limit fallback. These exercise the
existing research proposal; the bounded encoding candidate below adds typed
input and route binding without releasing a ruleset, establishing a KV-memory
fit or migrating real saved builds. See the
[context proposal's scope](../T1-model-selection/rules/context-fit.md#executable-synthetic-cases-cd-11).

### CD-11 typed context and exact route binding candidate (2026-10-18)

**Decision for review:** use the [CD-1 answer encoding](../../tests/fixtures/t0-answer-states.schema.json)
for context operands and a separate versioned binding to their original bytes.
Keep shared and independent vendor caps explicit. A route-specific record is
complete in its own scope; missing operands cannot borrow limits from another
route or silently inherit a model-native value. CTX-02's separately evidenced
native-limit fallback remains a prior normalization decision, not something
this reader can establish from a missing extension field.

The [synthetic binding schema](../../tests/fixtures/context-budget-binding.schema.json),
[binding example](../../tests/fixtures/context-budget-binding.json),
[answer example](../../tests/fixtures/context-budget-answers.json),
[reader](../../tests/context_budget_binding_prototype.py) and
[regressions](../../tests/test_context_budget_binding.py) choose these shapes:

| Field or answer path | Known value and scope | Unresolved or inapplicable behavior |
| --- | --- | --- |
| `x_t0_context_budget.proposal_version` | Literal `cd11-0.1`; synthetic candidate only | Unsupported shapes reject before predicates |
| `scope` | Exact selection ID, model/route/tokenizer ID and version pairs, operation ID, and SHA-256 of the normalized route settings bytes | Active scope is supplied by a separately reviewed resolver. Any mismatch or missing active scope gives `unknown`; a digest or matching label does not authenticate an artifact or source |
| `answer_states_sha256` | SHA-256 of the complete original CD-1 answer document, including whitespace | A different document rejects; no reserialization or last-value-wins parsing repairs its identity |
| `/context/semantics` | `shared` or `separate` | Unknown is an answer state, not a third capability enum value. Known input/output violations remain visible while combined applicability is unresolved |
| `/context/input_tokens` | Positive integer `lower` and `upper`, ordered; bounded count of the complete assembled request for the bound tokenizer | Missing, withheld or unknown counts remain unresolved. This derived interval is distinct from workload `mean`/`max`; assembly must already include history and injected memory exactly once |
| `/context/reserved_output_tokens` | Integer ≥ 0; includes all generated tokens covered by the reservation | Missing or not-applicable output is not zero. This candidate covers a generating operation; it does not infer the activation of embedding-only or other non-generating operations |
| `/context/output_cap_tokens` | Integer ≥ 0 in the same route scope | An unresolved cap prevents an unconditional fit pass; known violations of other caps remain visible |
| `/context/shared_cap_tokens` | Positive integer shared vendor window when semantics are shared | Separate semantics skips the combined predicate and rejects a simultaneously provided shared vendor window; it never invents one by adding separate caps |
| `/context/input_cap_tokens` | Positive integer independent or additional input cap | Separate semantics requires this operand. For an optional additional cap under shared semantics, explicit `not_applicable` means no added predicate; omission, unknown and withheld add an unknown predicate |
| `/context/policy_total_cap_tokens` | Integer ≥ 0 user policy ceiling on input plus reserved output; distinct from vendor caps | Explicit `not_applicable` means no selected policy ceiling. Omission, unknown and withheld do not silently mean unconstrained |

All counts require JSON integer tokens, excluding Boolean and integral-float
aliases. Bounds, namespace/version, duplicate JSON keys, nonfinite numbers,
identifiers and scope shapes are validated before any applicability skip. The
CD-1 normalizer retains unresolved parent states and answer provenance; an
unresolved context parent cannot become a collection of zero-valued operands.

The caller separately supplies exact Boolean or unresolved activation and
source-eligibility dispositions. Only explicit disabled activation skips the
screen. Ineligible or unresolved evidence yields unknown even if unadmitted
numbers would fail; it is not evidence of unsupported capability. Passing true
does not cause this experiment to verify a publisher fact: actual source,
version, configuration, tokenizer/count completeness and rights review remain
with #7/#40/#41 and the selected route's receiving owners.

The existing CTX arithmetic decides from upper bounds, retains lower-bound
findings and reports `may_not_fit` for an uncertain violation. Known zero output
and a zero user ceiling retain their numeric meanings. The synthetic 7,000-input,
2,000-output case fails an 8,000 shared window but passes separate 8,000-input and
4,000-output caps. It adds no KV-memory, runtime, quality or throughput result.
Returned scope and answer values are detached, and both original documents are
retained. No source request, model execution, catalog change or file publication
is performed by the reader.

This chooses a concrete CD-11 wire candidate and composes the reviewed CD-1 and
CTX mechanics for technical and affected-owner review. Final catalog/selection
extraction, support/source conflict resolution, extension normalization,
successor schema/ruleset and migration remain separate. Frozen v1 is unchanged;
#40 and #42's substantive contract prerequisite remain open. Run
`python -m unittest discover -s tests -p test_context_budget_binding.py -v`.

## Proposed T5 routing inventory

This routing synthesis comes from the merged T5 README and component notes, inspected 2026-10-17. [@zwright8's #126 review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/126#pullrequestreview-5560506323) accepts it with the constraints below. It accepts routing for review, not new enums, evidence truth, legal permission or execution.

| T5 input | Proposed family or contract decision | Remaining acceptance |
| --- | --- | --- |
| F-series framework method/backend support | Joint support and loader/API families; CD-3/CD-6, keep managed-service backend optionality distinct | #30/#40 confirm scope and supported methods |
| K-series resource estimates and training meters | Memory fit via CD-2/CD-3; price dimensions through #39, then #40 | #10 confirms estimator dimensions; #39 confirms meter semantics |
| D-series dataset governance and provenance | Licence/rights and CD-3/CD-6; replace boolean-only evidence through versioned fields | #32/#30/#60 source-specific rights; D-20 leakage/freeze remains #36 policy |
| A-series base revision, adapter metadata and notices | Loader/adapter and licence families; CD-6/CD-7; applicability-aware A-18a/b/c remains separate | #33/#11/#30 confirm lineage and notice predicates |
| A-13 deployment lifecycle; A-20 evaluation gate | Lifecycle to #37; gate to #36, with references in the shared rule record | #36/#37 dispositions remain separate from #40 schema routing |

No T5 candidate is promoted into the executable baseline by this inventory. Field and fixture implementation remains a next-version proposal requiring affected-owner review.
