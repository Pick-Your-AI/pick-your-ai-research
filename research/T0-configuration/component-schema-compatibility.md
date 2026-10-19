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

- **Catalog item:** `schema_version`, `id`, `kind`, `tier`, `name`, `version`, `status`, `billing_class`, `spec`, `provenance`, `updated_at` (required), plus optional `description`, `tags`, `license` and `extensions`. This covers #40's minimum fields for entity ID, category (`kind`, `tier`), version, lifecycle status and source references (`provenance`). `valid_from`/`valid_to` have no direct field (versioning, below).
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

**Remaining decisions, not invented defaults:** CD-1 answer-state encoding; CD-2 byte placement/pool semantics; CD-3 eligible-evidence/completeness/result wire shapes; CD-4 candidate adoption and source admission; CD-5 per-stage workload; CD-6 reference/credential/inheritance resolution; CD-7 revision resolution and next-version migration; CD-8 community evidence; CD-9 jurisdiction groups; CD-10 non-model-service runtime requirements; CD-11 context-budget shape; CD-12 attestation placement and CD-13 multi-selection syntax remain with their accountable owners in the companion decision register. This dictionary neither releases v1.1 nor removes #42's recorded #40 prerequisite.

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
| `missing` | `state` only | No recorded answer in this experiment; the interface can ask for it. An otherwise unrecorded path has this state; the parent-visibility rule below preserves an explicitly withheld descendant. No reason for a historical v1 absence is invented |
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

**Numeric parser boundary (2026-10-18):** actual synthetic probes of the
accepted `be60732a` reader showed `1.0000000000000000000001` and
`0.999999999999999999999999` reaching a predicate as `1.0` after satisfying
integer bounds fixed at one. `9007199254740993.0` also satisfied a maximum of
9007199254740992 after rounding. The [Python 3.12 JSON decoder](https://docs.python.org/3.12/library/json.html#json.JSONDecoder)
normally converts decimal/exponent tokens to floats; its `parse_float` hook
provides the original token. JSON Schema's [numeric data model](https://json-schema.org/draft/2020-12/draft-bhutton-json-schema-00#section-4.2.1)
does not impose that binary-float precision limit (sources checked 2026-10-18).

This bounded reader now rejects unsupported numeric precision during parsing,
before a field schema or value predicate can interpret a rounded answer.
Decimal/exponent tokens must be finite and retain the same mathematical value
when compared with the float's shortest decimal readback. A whole-valued float
must also equal the original integer exactly: `1e23` has the expected printed
readback but its binary value is a different integer. Original integer tokens
continue to use Python integers; this imposes no new 53-bit integer limit.
Supported spellings such as `1.0`, `1e0`, `0.1` and `1.2500` keep their existing
float values/types, while numeric-looking strings remain strings. This is an
explicit parser representation limit, not arbitrary-precision arithmetic or a
new rule for valid historical v1 records. The original input bytes, sidecar
schema, caller field schemas and typed predicate/outcome interfaces are unchanged.
The [eight raw-number regression methods](../../tests/test_t0_answer_numeric_precision.py)
cover schema-boundary false passes, underflow, large integer preservation,
nested values and the terminal rule boundary, including actual API executions
in normal and optimized Python.

**Original Boolean/None rule boundary:** compatibility predicates receive an unresolved result for
all non-provided states, including unknown applicability. Recommendation
rules use the known-answer gate specified in #81 and therefore skip unresolved
needs. A known false applicability predicate still skips.
No selected component remains CD-13's distinct empty selection scope; it is
not a sixth answer state. The answer's original state/path remains available
alongside the selection findings so these explanations are not collapsed.
Severity, evidence eligibility and selection activation remain separate.

**Predicate API correction (2026-10-18):** the
[#40 owner disposition](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40#issuecomment-6249840407)
identified a concrete negation defect. At prototype blob
`70feb63f5626de28e7ea197cc28d9ced2e1db662`, each of withheld, unknown, missing,
not-applicable and absent answers returned Python `None`. A rule asserting
`not answers.predicate(...)` then received `True` and the existing selection
evaluator reported `pass` / `assertion_true`, without calling the value
predicate. The five cases were reproduced before this correction.

`AnswerIndex.predicate(pointer, value_schema, predicate)` now returns an immutable
`PredicateResult`, retaining the answer's state and source path. Its call
signature is unchanged, but its return contract deliberately changes: Python
`bool`, `not`, and truth-testing `and`/`or` raise `TypeError` for every result,
including provided true/false. Keeping a bare `None` return could not intercept
the false-pass negation. Explicit operations are:

| Operation | Meaning |
| --- | --- |
| `result.negated()` | Flip a known Boolean; preserve unresolved value, original answer state and source path. It does not call the value predicate again |
| `result.compatibility_value()` | Final lowering to the existing rule interface: true/false remain exact, and an unresolved predicate remains `None` |
| `result.recommendation_value()` | Final known-answer gate: a non-provided answer returns false so the recommendation skips. A provided answer retains its predicate's true/false/`None`; unresolved predicate evidence is not replaced by false |

Negation must happen on the typed result **before** either final lowering. The
adapter values are only inputs to the existing strict normalized-rule boundary;
they must not be intermediate operands for Python Boolean expressions. For
example, an assertion callback can return
`answers.predicate(path, schema, check).negated().compatibility_value()`. A
recommendation applicability callback can return
`answers.predicate(path, schema, check).recommendation_value()`.

The complete pre-change caller audit found eight direct `predicate` calls, all
in `tests/test_t0_answer_states.py`: six value consumers now lower explicitly,
and two malformed-input probes retain their existing rejection. Every other
prototype uses the unchanged `AnswerIndex.read` interface. The sidecar,
schema, fixtures, field dictionary and CD-13 evaluator are unchanged. This
bounded correction does not resolve the disposition's separate field-sentinel,
preset, parent-read or state-specific reason/policy questions, including when a
`not_applicable` answer should skip a dependent compatibility rule. The
legacy behavior is retained below; the subsequent typed outcome boundary
addresses the reason/policy mechanics without changing that interface.

The [20 executable cases](../../tests/test_t0_answer_states.py) cover nested
and escaped paths, array boundaries, parent withholding, explicit false/zero,
field-type rejection before predicates, malformed/duplicate/nonfinite inputs,
read isolation and compatibility/recommendation behavior through the CD-13
experiment. Five additional methods exercise the actual false-pass path,
Boolean shortcuts, safe known/unresolved negation, retained state/path and the
provided-but-unresolved recommendation case. They reproduce frozen v1's
literal-unknown comparison and verify unchanged historical findings when the
synthetic extension is present. No original build bytes, frozen evaluator,
measured artifact or receiving receipt is modified.


**Typed outcome/reason boundary (2026-10-18):** the same
[#40 owner disposition](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40#issuecomment-6249840407)
requires separate answer-state reasons and a skipped dependent predicate for an
explicit `not_applicable` answer. An actual 15-case probe of accepted
`dff6b480c437761c56cf60d6aa9999b2abfb3462`, prototype blob
`9f8cea0119b93c0fd14c0626412bf97a37ba6af1`, confirmed the remaining loss:
withheld, unknown, missing, not-applicable and absent answers all lowered to the
same generic compatibility reasons, and recommendation skips used
`not_applicable` even when the answer was withheld or missing. No value callback
ran in those probes. The corrected typed negation still prevented a false pass;
this is the separate policy and explanation gap.

The existing [CD-1 module](../../tests/t0_answer_state_prototype.py) now also
provides `AnswerRule`, explicit `RulePolicy` and
`evaluate_answer_rule(rule)` as the terminal boundary for these answer-aware
experiments. A rule declares one ID, one fixed severity and its compatibility or
recommendation policy. Both applicability and assertion are lazy callbacks
returning the existing immutable `PredicateResult`; plain Boolean/None or other
untyped callback returns reject instead of silently discarding answer metadata.
The assertion callback runs exactly once only after provided, known-true
applicability.

| Responsible input | Compatibility outcome | Recommendation outcome | Distinct reason |
| --- | --- | --- | --- |
| Unknown / missing / withheld applicability answer | `unknown` | `skipped` | `answer_unknown` / `answer_missing` / `answer_withheld` |
| Explicit not-applicable answer at either position | `skipped` | `skipped` | `answer_not_applicable` |
| Provided applicability predicate is false | `skipped` | `skipped` | `applicability_false` |
| Provided predicate is unresolved, at either position | `unknown` | `unknown` | `predicate_unknown` |
| Unknown / missing / withheld assertion after known-true applicability | `unknown` | `unknown` | The corresponding `answer_*` reason |
| Provided assertion is true / false | `pass` / `fail` | `pass` / `fail` | `assertion_true` / `assertion_false` |

Recommendation gating applies to an unanswered applicability input. It does not
turn unresolved assertion evidence into a known result once the recommendation
is applicable. A provided answer whose value predicate cannot decide remains a
provided answer with `predicate_unknown`; this adapter does not invent a claim
that the answer or eligible evidence was absent. An explicit not-applicable
answer is scoped to the caller-selected predicate, not a waiver of every rule
or of required-component presence.

The immutable terminal result retains the rule ID, unchanged severity, outcome,
reason, responsible position (`applies_when` or `assertion`), exact answer state
and original source path. A genuinely unrecorded path remains missing with no
invented source path; parent visibility and escaped paths retain the normalizer's
actual causal record as described below.
No original answer value is copied into this result. The typed result also
rejects implicit Boolean coercion, so an unknown/skipped result cannot become a
pass through Python negation or truth testing.

```python
finding = evaluate_answer_rule(AnswerRule(
    id="synthetic.network-isolation",
    severity="error",
    policy=RulePolicy.COMPATIBILITY,
    applies_when=lambda: answers.predicate(network_path, network_schema, needs_isolation),
    assertion=lambda: answers.predicate(boundary_path, boundary_schema, stays_inside),
))
```

This is the preferred terminal API for CD-1 state-aware rule experiments. The
two Boolean/None adapters above and all 20 existing tests retain their original
behavior for historical comparison and compatibility with the unchanged CD-13
prototype. Those adapters cannot carry the new state reasons or not-applicable
policy and must not be presented as satisfying this boundary. Negation still
happens on `PredicateResult` before evaluation; neither its callback nor the
original value is evaluated again.

[Eleven additional synthetic methods](../../tests/test_t0_answer_rule_outcomes.py)
exercise both policies, all three severities, direct/absent and parent-derived
states, both predicate positions, explicit not-applicable versus known-false
skips, provided predicate uncertainty, known truth controls, negation, strict
callback/metadata rejection, lazy exception behavior, immutable outcomes and
original-byte/escaped-path retention. They run alongside the unchanged 20 CD-1
methods. Actual final source and receiving executions retain their own PR
receipts.

This bounded extension addresses the disposition's reason/policy mechanics.
It does not select components, quantify over selections, aggregate findings,
qualify evidence, release a ruleset or add a wire format. At that terminal-boundary
checkpoint, the original `AnswerIndex.read` and `predicate` implementations,
sidecar/schema/fixtures, field-sentinel, parent-read and preset constraints were
unchanged. The later parent-visibility correction is recorded below. CD-13
required presence, CD-5 stage adaptation and other owner work keep their
separate scope and review; downstream adoption must explicitly consume this
typed result rather than silently reusing a lossy Boolean interface.

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

#### CD-1 known-value schema admission correction (2026-10-18)

This is the bounded response to **constraint 2** in the
[existing owner disposition](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40#issuecomment-6249840407),
under the [separate implementation reservation](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40#issuecomment-6251633973).
The earlier normalization and rule-outcome records above retain their original
scope. The remaining defect was at the supplied **field schema** boundary:
`{"enum": ["none", "session", "persistent", "unknown"]}` admitted a provided
`"unknown"` as a known value. Actual original-reader probes also admitted direct
`const`, locally referenced vocabularies, object properties and array items.
A typed `memory != "none"` assertion could consequently pass for the in-band
marker. Correct typed negation cannot recover an answer state already lost by
an unsafe field vocabulary.

The [test-only schema admission helper](../../tests/t0_known_value_schema.py)
now checks the local known-value profile before `AnswerIndex.read` validates
any provided value. It rejects `"unknown"` in finite `enum`/`const` value
declarations, including leaves of structured constants and nested field schemas.
The **schema** is rejected even when the current supplied answer happens to be
`"persistent"`; the reader does not silently remove an enum member, substitute a
value or rewrite the schema. The predicate never runs after this rejection.
The encoding remains `cd1-0.1`, and original answer bytes and the caller's schema
remain unchanged. No production field, wire, generator or ruleset is adopted by
this test-only admission profile.

| Input boundary | Result |
| --- | --- |
| Provided value with finite vocabulary containing `"unknown"` | Input error before a value predicate or terminal finding |
| Explicit `unknown`, `missing`, `withheld` or `not_applicable` record | Existing typed state, source path and rule policy; no value-schema check or value callback |
| Known enum/constant, including false, zero, empty or explicitly nullable values | Ordinary schema validation, exact value/type retention |
| Literal `"unknown"` under a free-text string schema | Provided text; never silently converted to an answer state |
| `unknown` as an object property name, description, example or default annotation | Not a provided-value vocabulary declaration; no default is applied |
| Direct `not: {const: "unknown"}` or `not: {enum: [...]}` exclusion | Ordinary exclusion semantics; the excluded value still fails field validation |

The supported schema profile is explicit. It uses draft 2020-12, follows
document-local JSON Pointer `$ref` targets (including RFC 6901 escaping and URI
fragment decoding) at supported schema locations, and inspects the standard
object/array applicators,
`allOf`/`anyOf`/`oneOf`, conditional locations and dependent schemas. Unused
`$defs` and annotations are not applied field declarations. Property-name
validation retains a separate context, so a reference used for names cannot
hide the same vocabulary when it is also used for values. Ordinary finite-data
recursive schemas remain usable; a nonprogressing recursive application is a
controlled input error, never a predicate result.

This is a conservative **admission profile**, not a JSON Schema equivalence or
satisfiability solver. A finite exclusion is admitted only when the immediate
`not` body consists solely of `enum` or `const` and is outside another negation.
Other occurrences of the sentinel in finite declarations, including conditional
or compound-negation forms, require an explicit field-schema rewrite; the
normalizer does not infer that another keyword makes them unreachable. Named
anchors, external/dynamic references, nested schema resources and other dialects
are outside this profile and reject before reference retrieval or predicates.
They cannot bypass the local vocabulary inspection. Root schema identifiers and
supported local references retain their ordinary meaning. This changes no
frozen contract resolver or other schema validator.

Independent review found that the first candidate inspected a reference target
without inspecting resource-bearing ancestors skipped by its pointer. A jump
through an unused `$defs` resource could make the admission helper inspect the
root's known enum while the actual validator used the nested resource's
`enum: ["unknown"]`. The original candidate admitted the marker and executed
the predicate; its otherwise successful test receipts do not cover this gap.
The correction tracks schema nodes separately from schema-map/array containers
through the full pointer path and rejects any nested resource ancestor. A field
or definition literally named `$id` remains a normal name, not a resource
keyword. Pointers into annotations or container maps are outside the supported
schema-location profile; no arbitrary dictionary is promoted to a field schema.

[Twenty-two additional synthetic methods](../../tests/test_t0_known_value_schemas.py)
exercise the actual reader, predicate and typed terminal-rule boundary, including
direct and nested sentinel vocabularies, known-value controls, exact free text,
literal property names, annotations, local/escaped/shared references, unused
definitions, recursion, direct exclusions and negation counterexamples. The
original six-method red run had 15 failed rejection subcases with the free-text
control passing. Normal/optimized and final source/receiving runs retain their
own PR receipts; a proposal or test count is not empirical source evidence.

Primary syntax checked **2026-10-18**: JSON Schema validation
[sections 6.1.2–6.1.3](https://json-schema.org/draft/2020-12/json-schema-validation#section-6.1.2)
define finite enum/constant equality, while core
[sections 10.2.1–10.2.2](https://json-schema.org/draft/2020-12/json-schema-core#section-10.2.1)
define applicators, negation and conditional behavior. Those standards do not
reserve the word `unknown`; excluding it from known answer vocabularies and
restricting this local profile are project decisions from the cited disposition.

The [parent-visibility correction](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40#issuecomment-6251507908)
retains its separate lookup/source-path scope. This correction changes only the
provided-value schema-validation footer in the existing reader. Preset
provenance, the complete owner-reviewed field registry, successor migration,
affected-consumer adoption and the full #40/#42 acceptance remain separate.
The workload-note and M1/W-R11 writer retains its dictionary/activation scope.

### CD-1 withheld-child visibility in parent reads (2026-10-18)

Constraint 5 in [the current #40 owner disposition](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40#issuecomment-6249840407)
identified a lost-state case: when only a child is explicitly withheld, reading
its otherwise unrecorded parent returned `missing` with no causal path. The
reader now reports that parent view as `withheld`, retaining a real withheld
descendant's original pointer in `source_path`. This means part of the requested
view was deliberately withheld, not that every child has that state.

Only a withheld record supplies this witness. Constructor-time indexing uses
decoded pointer segments, so similarly prefixed sibling names do not acquire
the state. If several descendants are withheld, the lexicographically first
recorded pointer is the deterministic causal witness, independent of input
object order. No parent record, value or source label is invented. Partial
provided children are not assembled into a known parent object; callers still
read each child independently when appropriate. Exact or recorded-ancestor
lookups, overlap rejection and provided-parent traversal retain their behavior.

The unchanged typed predicate and terminal rule boundary now carry this real
cause through `answer_withheld`: compatibility applicability remains unknown,
recommendation applicability skips, and a withheld assertion after known-true
applicability remains unknown for both policies. The value predicate receives
no partial object. Severity, lazy evaluation and all original answer bytes are
unchanged; a genuinely absent path still has `missing` and no invented source.

The [separate synthetic regression file](../../tests/test_t0_answer_parent_visibility.py)
exercises multiple witnesses/orderings, escaped and empty pointer segments,
sibling isolation, exact/ancestor/provided reads and both terminal policies.
This corrects visibility in the existing test-only reader. It adds no wire
field/state, default, evidence qualification, preset policy or successor
adoption. The other CD-1 constraints and full #40/#42 criteria remain open.

### CD-1 explicit preset attribution candidate (2026-10-18)

Constraint 6 in [the #40 owner disposition](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40#issuecomment-6249840407)
requires a constrained `preset:<name>` source and an explicit assumption flag.
The original `cd1-0.1` schema admits arbitrary nonblank source text and has no
assumption member. The separate [0.2 schema](../../tests/fixtures/t0-answer-attribution.schema.json),
[synthetic example](../../tests/fixtures/t0-answer-attribution.json),
[reader](../../tests/t0_answer_attribution_prototype.py) and
[regressions](../../tests/test_t0_answer_attribution.py) provide an explicit
opt-in candidate. Original 0.1 schemas, fixtures, readers and callers retain
their historical meaning; neither reader silently accepts the other version.

Every 0.2 `provided` record must include an exact Boolean `assumption`. Its
optional `source` must be `preset:<name>`, where this bounded candidate permits
a 1–64-character ASCII name starting with a letter or digit and continuing with
letters, digits, dots, underscores or hyphens. Whitespace, trailing control
characters, URLs and arbitrary source labels are rejected. Broader preset-name
vocabulary requires an explicit later candidate. Unresolved records retain the
existing four states and cannot carry a value, source or assumption flag.

`assumption: true` and `assumption: false` remain the caller's distinct explicit
declarations. The reader infers neither from a source name, a missing source,
the value's truthiness or another record. Both flags are valid with or without
a preset source: preserving the origin does not determine whether the caller
currently declares the value an assumption. Neither flag, nor a syntactically
valid source, establishes accuracy, confirmation, eligible evidence, publisher
identity or receiving-owner acceptance. No implicit false/default is supplied.

The reader retains the original UTF-8 bytes. After strict 0.2 admission, it uses
a private 0.1-shaped in-memory view only to reuse current pointer traversal,
field validation and answer-state mechanics. That view is not an exported
artifact, a changed identity or a migration of retained bytes. A provided
nested value inherits its actual recorded ancestor's source and assumption;
a missing member or unresolved answer receives no provided attribution.
Current parent-visibility and overlap behavior is reused unchanged.

The accepted original-token precision guard from [#359](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/359)
also runs at this candidate's first JSON parse, before any private view is
serialized. Otherwise an underflowed or excess-precision raw token could be
rounded first and the downstream reader would see only the replacement number.
Synthetic controls reject those tokens even in unread nested values before the
normalizer is called, while preserving supported decimal/exponent values and
exact JSON integers with their original bytes and explicit attribution.

The typed predicate preserves the explicit flag/source through safe negation.
The separate terminal wrapper keeps them alongside the unchanged typed rule
finding and its causal source path, using only the callback actually responsible
for the result. An unevaluated assertion is not called to obtain metadata.
Fixed severity, unknown/skipped policy and lazy value validation remain with
the existing rule evaluator; a false assumption flag cannot turn unresolved
predicate evidence into a pass. This wrapper rejects callbacks that have
already discarded attribution. Existing lossy adapters and consumers are not
silently upgraded to the candidate.

The synthetic cases cover both Boolean flags, absent sources, invalid/missing
flags, whole-string source admission, original-byte preservation, exact nested
causes, unresolved states, safe negation and both terminal policies. This
addresses the test-only attribution mechanics of constraint 6. It changes no
frozen v1 field, source grade, preset registry, field vocabulary or production
wire format; successor adoption and the complete #40/#42 criteria remain open.

### CD-3 synthetic support-membership experiment (2026-10-18)

The [normalized prototype](../../tests/support_membership_prototype.py) and
[regression cases](../../tests/test_support_membership.py) exercise the
[adopted completeness policy](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75#pullrequestreview-5550616927),
checked against the actual owner review on 2026-10-18 and corrected for
[the requested-inventory constraints in the owner disposition](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40#issuecomment-6249840407).
The [bounded correction claim](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40#issuecomment-6250948765)
changes completeness constraints 1 and 2 only. The unchanged frozen
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
| Documented supported member, without an equal-rank opposite claim | `pass`; `unverified` only when the used cohort has separately qualified checked-only provenance as specified below. Exhaustiveness is unnecessary for this positive claim |
| Explicit unsupported statement, without an equal-rank opposite claim | `fail`; an exhaustive inventory is unnecessary for this negative claim |
| Absent from a known list whose scoped source is exhaustive | `fail` |
| Absent from an unmarked/non-exhaustive list, or the list itself is missing | `unknown`; a missing list is not a known empty exhaustive list |
| Opposite yes/no claims still equally ranked after the preceding review | `unknown`, flagged disputed; a stronger requirement must already have superseded a weaker capability listing under #41 |
| Evidence known outside the query scope, or eligibility unresolved | `unknown` for an applicable compatibility query; an ineligible source is not evidence of incompatibility |

A singleton query models `contains`; alternative accepted formats use an
`any` query like `intersects`. Requested-inventory completeness is a separate,
caller-qualified fact, independent of publisher-inventory exhaustiveness.
Neither list presence, source ID nor a catalog digest establishes either fact.

| Applicable requested set | `any` reduction | `all` reduction |
| --- | --- | --- |
| At least one undisputed positive member | `pass`, even if other requested alternatives are unknown or the requested set is incomplete | Other members still matter; this witness alone cannot establish `pass` |
| At least one undisputed negative member | Other alternatives still matter; this counterexample alone cannot establish `fail` | `fail`, even if other requested members are unknown or the requested set is incomplete |
| Nonempty set, every member negative | `fail` only with independently eligible `requested_complete: true`; otherwise reasoned `unknown` | `fail` from the known counterexample |
| Nonempty set, every member positive | `pass` from a known witness | `pass` only with independently eligible `requested_complete: true`; otherwise reasoned `unknown` |
| Known empty requested set, including explicitly complete empty sets | `unknown / requirement_empty`, with no asserted member findings | `unknown / requirement_empty`, with no asserted member findings |

Where a definitive reduction needs requested completeness, a qualified `false`
yields `unknown / requested_set_incomplete`; an unresolved or unqualified marker
yields `unknown / requested_completeness_unknown`. Existing per-member outcomes,
reasons, ordering and disputes remain visible. Completeness cannot cure an
unmarked omission or an equal-rank dispute. These internal query names and
reason strings do not settle DSL syntax. A known irrelevant rule remains
`skipped`; missing requirements or applicability remain `unknown`. The normalized
API requires an actual `frozenset` of nonblank strings (or `None` for unknown),
rejects bare strings and malformed collections before shortcuts, and preserves
literal case and spacing without coercion.

The correction has retained prechange observations at main
`8df56f1d056bfd5d8ca8fbe88d7c70ab19a2ecea`, reducer blob
`4983904b98a83889df44bae0581a947f279793f6`. Without any requested-completeness
operand, an all-negative ANY example returned `fail`, an all-positive ALL
example returned `pass`, both empty quantifiers raised `ValueError`, and the
bare string `"gguf"` incorrectly passed against the character set `{"f", "g", "u"}`
with findings `f, g, g, u`. A positive ANY witness was also recorded as a control
that must continue to pass. The 3,868-byte original probe record has SHA-256
`aeac453c492249afd884ba4bd107e6465b1b4d42b96d1ef77e30bd4c5233e8be`.
The focused regression cases retain each counterexample and its corrected
outcome; explicit complete controls still permit the legitimate verdicts.

A member passing documents only that scoped support claim, with the source
identity retained. It does not establish joint architecture/backend/quantization
support, runtime execution, memory fit, an offering's allowed residency, or
independent verification. [T2's direct-loader completeness exception and its
unmarked support lists](../T2-infrastructure/inference-engine.md#release-keyed-artifact-and-hardware-matrix)
retain their original source/release scopes. The typed CD-3 binding below
selects a query/result candidate over CD-1; conflict resolution over real
sources, affected-owner adoption and the versioned ruleset/adapter remain
separate. Frozen v1 and #42's prerequisite are unchanged.

### CD-3 scoped source evidence candidate (2026-10-18)

Completeness constraint 3 in [the owner disposition](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40#issuecomment-6249840407)
requires evidence to say which version, date and scope its result covers.
The existing typed query below already retains query/cohort versions and the
exact selected scope; its closed cohort reference has no dated source register.
The [separate claim](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40#issuecomment-6252536259)
therefore adds a test-only carrier and admission wrapper, without changing the
existing query, reducer, binding schema or frozen v1. The before/control case
executes the actual current query: its qualified matching-scope control passes,
while adding a source URI or check date to its cohort rejects the closed shape.
This preserves the earlier binding's documented boundary.

The [new schema](../../tests/fixtures/support-evidence-admission.schema.json),
[synthetic record](../../tests/fixtures/support-evidence-admission.json),
[computed synthetic result](../../tests/fixtures/support-evidence-admission-result.json),
[wrapper](../../tests/support_evidence_admission_prototype.py) and
[regressions](../../tests/test_support_evidence_admission.py) select the explicit
research proposal `cd3-evidence-0.1` over `cd3-0.3`. Unsupported versions reject;
there is no implicit migration or latest-version selection.

| Retained field | Meaning and admission boundary |
| --- | --- |
| Original query-byte SHA-256 | Binds the complete query, including its exact original answer-byte digest; reformatting either retained input requires a new matching identity |
| Query, cohort and scope | Complete query identity/severity/quantifier, cohort ID/version, and all existing selection/catalog/item/version/kind/property/conditions dimensions must exactly match the retained query |
| Source register | One to 32 explicitly named source ID/revision pairs with `source_uri` and `checked_at`; duplicate pairs reject, and all entries retain their order and original strings |
| Caller qualification | `source_qualified: true / false / null` plus the SHA-256 of the exact source-record bytes the caller actually qualified; a missing or mismatched receipt leaves admission unresolved |
| Result | Complete dated source register and its original byte hash, requested and effective qualification context, plus the unchanged full membership result and all operand states/findings |

The carrier covers one already normalized, scoped and ranked cohort. It does
not map individual membership claims to individual sources within that cohort.
The caller must establish that every retained source applies to this exact
coverage and that preceding conflicts/ranks were resolved under
[#41's evidence policy](catalog-data-sources.md#conflict-resolution). A nonempty
register, matching digest, source ID or valid timestamp establishes neither
that review nor source truth, publisher authority, rights or current eligibility.

The wrapper validates the complete source record before any applicability
shortcut. It reuses the existing conservative public HTTP(S) locator checks and
requires query-free URLs, preserving section fragments. This avoids storing
signed URL query parameters; it does not fetch a URL or prove public access.
The existing timestamp profile validates actual Gregorian dates, explicit
offsets and fractional precision without optional format-checker packages or
normalizing the retained strings. The carrier is limited to 64 KiB, with the
schema's explicit source/string bounds; exceeding this prototype profile is an
input rejection, not an incompatibility finding.

Qualified source admission is additional to the existing independently supplied
applicability, requested values/completeness and cohort qualifications. It can
withhold an otherwise eligible cohort, but cannot override an ineligible one.
The membership result keeps its existing reasoned unknown/skipped dispositions
and fixed severity. Checked-only provenance remains a separate per-invocation
fact from the canonical label candidate: no date, URI or successful admission
supplies that grade. Neither eligibility nor a label is reused from a prior call.

The full-result verifier recomputes against the caller's current context and
compares every field. A changed check date, source revision, URI, scope, digest,
qualification or membership result cannot certify itself, including changes
that leave the verdict the same. Output JSON formatting may differ; retained
input bytes cannot. Returned objects are detached from the retained records.

No maximum evidence age is invented. Dates remain dated observations; version
or source corrections, current-state eligibility, rights and rank qualification
stay with the caller under #41. All committed inputs are explicitly synthetic;
their placeholder source path was not fetched and their qualification flags
claim no real review. This supplies bounded carrier/admission mechanics for
constraint 3, not successor wire adoption, actual source resolution, the separate
two-rule adapter, or completion of #40/#41/#42 and their receiving handoffs.

### CD-3 typed support query and result candidate (2026-10-18)

**Selected research design:** bind the corrected membership reducer through
closed `x_t0_support_query` / `x_t0_support_result` envelopes at proposal version
`cd3-0.3`. This is an explicit successor research candidate to historical
`cd3-0.1` and the [requested-completeness correction in `cd3-0.2`](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/349),
not a reinterpretation or implicit migration of retained old bytes.
The synthetic query version advances from `0.2.0` to `0.3.0`, so its scoped CD-1
paths change too. The unchanged claim cohort retains its own `0.1.0` version.
This reader rejects old or unsupported proposal versions; a current query
cannot reuse answers stored under the prior query-version paths.
The [query schema and `$defs/result`](../../tests/fixtures/support-membership-binding.schema.json),
[reader and result verifier](../../tests/support_membership_binding_prototype.py),
[query](../../tests/fixtures/support-membership-binding.json),
[CD-1 answers](../../tests/fixtures/support-membership-answers.json),
[result](../../tests/fixtures/support-membership-result.json) and
[focused binding regression cases](../../tests/test_support_membership_binding.py)
make this exact candidate reviewable. This chooses an encoding; it does not
claim that the normalized-mechanics receipt also adopted this new wire format.

| Field / boundary | Chosen type and interpretation |
| --- | --- |
| Query | Stable canonical-style ID, opaque nonempty version, `requirement: any` or `all`, fixed `info` / `warning` / `error` severity. A singleton is a membership query; no implicit default quantifier |
| Scope | Exact selection ID, catalog-byte SHA-256, item ID/version/canonical kind, non-root literal JSON Pointer for the support property, and configuration/conditions-byte SHA-256. All dimensions must match the caller's separately established selected scope |
| Evidence cohort | Stable ID and opaque version identifying the already normalized, scoped and ranked claim cohort. Neither field supplies a publisher URL, access date, completeness or source permission |
| Answer identity | SHA-256 of the complete original CD-1 file, including unrelated answers and whitespace. Field paths use `/support_checks/{selection_id}/{query_id}/{query_version}/{cohort_id}/{cohort_version}/{field}` with each literal token escaped through CD-1's pointer rules |
| `applies_when` | A provided Boolean or a distinct unresolved CD-1 state. Only a caller-qualified provided `false` skips a rule |
| `requested` | Provided list of unique, nonblank literal strings, possibly empty, or an unresolved CD-1 state. An empty list is a known empty request with an unknown verdict, distinct from an unresolved answer. Values are case sensitive, untrimmed and uncoerced; they carry no numeric unit or implicit vocabulary mapping |
| `requested_complete` | Provided Boolean or distinct unresolved CD-1 state. Its own caller qualification must be `true` before the value can establish requested-inventory completeness; a provided list, source label or publisher `exhaustive` marker cannot supply it |
| `supported` / `unsupported` | Provided unique string lists, possibly empty, or unresolved CD-1 states. The former is a positive inventory; the latter records explicit equal-rank negative claims in this cohort |
| `exhaustive` | Provided Boolean or unresolved CD-1 state, separate from source eligibility. Only a known positive inventory plus eligible `true` completeness can support an absence-based negative |
| Caller qualification | Exact Boolean or unresolved selection activation, plus four independently qualified input groups: applicability, requested values, requested completeness and cohort. Each omitted qualification is unresolved for that invocation; an answer's `source` label cannot qualify itself. Requested-completeness qualification is necessary only for the verdicts that require a complete requested set |
| Checked-only cohort provenance | Separate caller-established `cohort_checked_only: true / false / null` for this exact scoped/versioned cohort. Only `true` supplies checked-only provenance; false or omitted/null supplies no grade. Eligibility, source strings, hashes and result flags cannot establish this fact |
| Result | Exact query/answer hashes, query/scope/cohort identities, caller evaluation context including all four eligibility qualifications and checked-only provenance, all six operands' state/value/source/source path, and the reducer's outcome/reason/source ID/disputed flag/all sorted member findings. `evidence_label` is `unverified` only for actually used, eligible, checked-only cohort evidence; otherwise it is null. Severity stays on the versioned query |

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
missing. An explicit eligible unsupported member still supplies a negative
finding with a missing positive inventory. It can fail ALL directly; failing
ANY also requires a complete requested inventory and negative findings for all
alternatives. A missing positive inventory cannot become an empty exhaustive
inventory. A documented positive finding requires no completeness marker;
passing ALL additionally requires a complete requested inventory. Equal-rank
positive/negative claims remain disputed and unknown. ANY preserves
its other unresolved rows when one member passes; ALL preserves them when a
known counterexample fails. The committed synthetic ANY example contains one
documented member, one unmarked omission and one equal-rank dispute. Its pass
is scoped membership only, with `disputed: true` preserved and no evidence grade
asserted (`evidence_label: null`).
The example explicitly records a synthetic complete-request fact under its new
query-version path; that marker is not inferred from the frozen catalog or
claim lists. An unresolved or ineligible requested-completeness marker does not
block ANY's positive witness or ALL's negative counterexample. Its original
state/value/source/path and caller qualification remain in every result,
including when the verdict does not depend on completeness.

Provided values are validated before any disabled/applicability/eligibility
shortcut. Malformed lists or Boolean markers, duplicate decoded JSON keys,
non-finite numbers, invalid Unicode scalars, ambiguous parent/child paths and
malformed identities are input errors. A valid provided empty request reaches
its explicit unknown disposition instead of raising an input error.
Unresolved parent states propagate;
a provided object can supply grouped fields and retains its exact source path.
Valid but mismatched selected scope is unknown, never automatic incompatibility.
Disabled and unresolved activation have separate skipped/unknown dispositions.
Canonical kinds are checked against frozen v1's registry, while the new ID and
digest guards reject terminal controls across the complete value.

**Result consumption:** schema validation checks shape only. `verify_result`
recomputes from the retained query/answers and the **caller's** selected scope,
activation, eligibility and checked-only provenance inputs, then compares every reported field. A
self-reported eligible flag, changed requested-completeness state/value, changed
source/version/hash, removed disputed row or changed outcome cannot validate
itself, even when the mutation leaves the membership verdict unchanged.
Changing the result's provenance flag or grade cannot qualify that result;
the verifier never obtains its caller context from the reported context.
Result JSON formatting may vary;
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

**Evidence-label correction (2026-10-18):** the earlier `cd3-0.2` correction left
completeness constraint 5 in the owner disposition open. Against accepted main
`4f1c22bac91783a00384b3037bb64b040250c072`, four regression methods produced 13
failing subcases: the constant `unverified` label was attached to disabled,
unresolved, missing-request, ineligible and merely eligible cases without a
checked-only provenance fact. The separate [label regressions](../../tests/test_support_evidence_labels.py)
retain these counterexamples and exercise the corrected boundary.

The normalized reducer now receives `Evidence.checked_only` separately from
eligibility; the binding receives the same fact as caller-only
`cohort_checked_only`. This is a qualified input from the caller's actual #41
review of that exact cohort, not an assertion that a field or fixture performs
source checking. Only a true qualification **and actual use of eligible cohort
evidence** can attach `unverified`. Skipped, unresolved-activation/scope,
missing/empty-request and ineligible cases have no label. A missing positive
inventory with no relevant explicit negative claim remains ungraded even when
the caller supplied true. A provided unmarked inventory, exhaustive absence,
documented member or explicit/disputed claim can carry the scoped checked-only
label; unknown and disputed findings still retain their own reasons.

Null means this prototype establishes no evidence grade; it never implies
independent verification or a different grade. The checked-only fact does not
change membership outcomes, findings, completeness, disputes or fixed severity.
An answer's source string, an extra answer field or a result's own context cannot
establish it. Each verification recomputes against the caller's separately
supplied qualification, including when changing the grade leaves the outcome
unchanged. Arbitrary grade strings, including `verified`, and non-Boolean
qualification values are rejected. The prototype does not implement stronger
grades, authenticate the caller or perform the external evidence review.

This supplies the bounded label mechanic requested by constraint 5. Source/date/
rank admission, real rule adapters (including `rule.precision.engine` and
`rule.engine.model.format`), affected-owner adoption and frozen-rule adoption
remain separate work.

This bounded correction changes the existing test-only CD-3 reducer, binding,
fixtures and regression cases. It leaves the accepted CD-1 normalizer,
CD-2/CD-6/CD-7 work, frozen `contracts/v1`, measured artifacts and recorded
receiving receipts unchanged. #40's tynamite/zwright8
review owns successor adoption; #41 owns actual evidence qualification with
the affected component owner. Real source adapters, final ruleset dispatch,
migration and the remaining listed handoffs retain their own concrete work.
#40 remains open and #42/#114's substantive prerequisite is preserved.

### CD-3 actual frozen support-rule adapter candidate (2026-10-18)

**Selected research design:** explicitly opt into the test-only
`cd3-frozen-support-rules-0.1` [adapter](../../tests/frozen_support_rule_adapter_prototype.py)
for the two actual baseline identities named in completeness constraint 4 of
the [owner disposition](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40#issuecomment-6249840407).
This is a bounded per-rule experiment over the canonical `cd3-0.3` membership
interface, distinct from the default frozen evaluator and from a whole-build
replay. It supplies a concrete adapter candidate for the still-open task in
the [16:00 owner ledger](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40#issuecomment-6252011763).
It does not adopt a v1.1 ruleset, new production field/wire representation,
source qualification or migration.

| Actual frozen rule | Requested operand | Positive support operand | Completeness decision |
| --- | --- | --- | --- |
| `rule.precision.engine` (`contains`) | Selected primary model `/settings/precision` | Primary engine catalog `/spec/supported_precisions` | A resolved, schema-admitted scalar with separately qualified requested input is exactly one requested value. Only this scalar establishes a complete singleton |
| `rule.engine.model.format` (`intersects`) | Primary model catalog `/spec/model_formats` | Primary engine catalog `/spec/model_formats` | A researched format array supplies no completeness. An all-negative ANY result additionally requires the caller's separately qualified requested-completeness marker |

Both assertions reduce with ANY membership. The adapter reads the unchanged
actual baseline definitions, retaining their `error` severity, `on_unknown:
block`, applicability, operand references, message/remediation, affected kinds
and original owner metadata. It admits only these two rule IDs and verifies
the exact baseline and reference-reader byte hashes. Their existing
applicability still requires self-hosted deployment and an enabled primary
engine. Qualified known non-applicability skips; unresolved deployment facts
remain unknown. The adapter does not execute other assertions, change frozen
dispatch or calculate whole-build readiness.

Before any applicability or evidence shortcut, retained build/catalog bytes
receive the existing JSON intake and frozen shape checks, exact integer
revision admission, the existing strict build-wide selection identity/role
preflight, and a unique catalog-ID check. Disabled duplicates remain subject
to the accepted strict policy. These checks do not constitute full graph,
CD-7 replay, temporal-format or source admission. The explicit per-rule
experiment retains the build bytes, including its locks, but makes no
whole-build ruleset-lock or successor migration decision. A mismatched catalog
snapshot, unavailable selection/item/version, wrong item kind or absent
property cannot supply a compatible operand. The frozen catalog requires
nonempty support/format arrays; malformed missing or empty arrays reject
input shape instead of becoming evidence for a membership verdict. Missing
optional selected precision remains unknown, never a default or empty set.

The caller supplies a normalized cohort ID/version, exact support scope,
explicit negative inventory, publisher exhaustiveness and requested-inventory
completeness. Scope retains all seven existing CD-3 dimensions: selection,
catalog bytes, item ID/version/kind, property and complete build/conditions
bytes. An unchanged value in differently formatted bytes cannot reuse the
old scoped cohort. Positive claims come from the actual engine catalog
operand; the negative inventory must be explicitly recorded, including an
empty set. An unresolved negative inventory is not silently replaced by one.
The applicability, requested input, requested completeness and cohort retain
independent caller qualifications. The scalar completeness decision cannot
bypass the selected-value qualification, and cannot be generalized to a
researched array.

Unmarked omissions remain reasoned unknown. Qualified documented members,
explicit unsupported claims and eligible exhaustive absence retain their
distinct findings; an equal-rank contradiction stays disputed/unknown. An
ANY positive witness retains other unknown/disputed rows. The canonical
checked-only input stays separate from eligibility, and `unverified` appears
only when that independently qualified cohort evidence is actually used.
An absent label supplies no evidence grade. The normalized record carries
no publisher URL/access date or source admission: constraint 3 and #41's
source/date/rank/rights/currency review remain independent prerequisites.
Matching scope, source names, dates or hashes cannot perform that review.

Each detached Python receipt retains original build/catalog hashes, the
complete pinned rule definition, all four resolved or unresolved applicability
and assertion operands with actual source paths, exact scope/cohort and caller
context, recorded completeness plus its effective value/basis, and every
member finding/reason/dispute. It is a mechanics receipt, not an adopted wire
envelope or authenticated result; consumers must recompute from actual inputs
and caller qualifications rather than trusting a reported flag.

The [synthetic regressions](../../tests/test_frozen_support_rule_adapter.py)
exercise these actual named rules alongside the unchanged full frozen
evaluator. The original accepted-`c2bdd82` before record contains eight
schema-valid frozen executions and four separately schema-rejected controls.
Three admitted omission cases produced four target `fail` findings; this
prospective gate keeps them unknown while positive, inactive and unresolved
controls preserve their dispositions. Raw before-record SHA-256:
`c5e6031ac6617da6327d09c98c292ca9957242a6d12e5ed28f2a37059dd8effc`.
These are retained historical frozen outcomes, not a retrospective claim that
the imported contract violated a later proposal. Further controls cover
explicit/exhaustive negatives, independently qualified completeness, disputed
rows, each scope dimension, unresolved operands, malformed markers before
shortcuts, source order/identity and detached results. None supplies real
vendor support, runtime measurements or affected-owner adoption. #40, #42
and their remaining source/contract/replay requirements stay open.

### CD-4 typed isolation-boundary and inventory candidate (2026-10-18)

**Engineering decision:** represent one selected isolation boundary with an
explicit endpoint register and per-selection runtime footprints. Bind that
inventory to the complete original Build and CD-1 answer bytes. Use the existing
[W-R8 rule](workload-use-case.md#w-r8-air-gapped-builds-have-no-external-connections),
the [CD-4 decision](deployment-mode.md#open-contract-decisions) and the
[#37 isolation reconciliation](../T6-deployment-operations/deployment.md)
as the accepted semantic inputs. This chooses a concrete research encoding for
endpoint membership, connection lifecycle/state and exact artifact readiness;
it does not infer isolation from provider operation, self-operation or a
build-level deployment label.

The [schema](../../tests/fixtures/isolation-binding.schema.json),
[binding](../../tests/fixtures/isolation-binding.json),
[fictional Build](../../tests/fixtures/isolation-build.json),
[typed answers](../../tests/fixtures/isolation-answers.json),
[reference reader](../../tests/isolation_binding_prototype.py) and
[regressions](../../tests/test_isolation_binding.py) are synthetic test artifacts.
The narrow Build reuses fictional v1 model, engine and MCP selections; it is not
a complete runnable configuration. No endpoint is contacted, artifact acquired,
firewall configured or publisher evidence graded by this experiment.

| Field or answer | Type and scope | Interpretation |
| --- | --- | --- |
| `proposal_version` | Literal `cd4-0.1` | Versioned test encoding; no new frozen-v1 field |
| `build_sha256`, `answer_states_sha256` | 64 lowercase hexadecimal characters | SHA-256 of each complete supplied byte string, including whitespace and unrelated content; never a hash of a reconstructed document |
| `boundary_id`, `endpoint_ids[]` | Unique canonical ASCII identity strings, 1–80 characters | Exact declared isolation scope; a label provides no membership or physical-isolation evidence |
| `components[].selection_id` | Exact unique selection ID in the retained Build | Inventory binding covers every enabled selection, regardless of kind or primary role; an omitted selection remains unknown |
| `runtime_endpoint_ids[]` | Unique references to registered endpoint IDs | All declared runtime execution/service locations must be inside; a component with no runtime endpoint needs an explicitly complete empty inventory |
| `connections[]` | Unique local ID plus the existing purpose enum | Every declared connection is checked. Telemetry, licence checks and optional-looking purposes receive no runtime-egress exception |
| `runtime_artifacts[]` | Unique local ID and required SHA-256 | Enumerates required runtime material, including any required local code, weights, configuration or notices. The fixture hashes identify fictional descriptors, not real downloaded artifacts |
| `/workload/network` | CD-1 answer over `online`, `private_network`, `air_gapped` | Only an eligible provided air-gap requirement activates W-R8. Other provided values skip it; unresolved or ineligible applicability remains unknown |
| `/workload/isolation_boundary_id` | CD-1 answer over the identity type | Must equal the binding's boundary. A missing or different selected boundary remains unknown |
| Endpoint `inside_boundary` | CD-1 answer over Boolean | Membership applies to this exact boundary, not generic private networking or provider region membership |
| Connection `destination_id`, `lifecycle`, `state` | CD-1 answers over a registered endpoint ID, `provisioning`/`runtime`, and `enabled`/`disabled` | Unknown, missing, withheld and not-applicable use CD-1 states outside these known-value enums |
| Inventory `complete` | CD-1 Boolean scoped to the exact inventory digest | Only eligible `true` establishes complete coverage; `false` and all unresolved states leave coverage unknown |
| Artifact `present_inside_boundary` | CD-1 Boolean keyed by selection, artifact ID **and required SHA-256** | A same-named different revision cannot reuse a readiness assertion; a download path or a provisioning connection supplies no runtime readiness |

The reader validates complete raw JSON, frozen Build shape, exact integer
revision tokens, build-wide selection/role uniqueness, all inventory identities
and registered endpoint references before applying disabled or inapplicable
shortcuts. Duplicate keys, non-finite values, malformed provided states and
ambiguous identities reject. CD-1 retains source labels and source paths,
including unresolved parents; the reader neither equates a literal `unknown`
with a valid known state nor coerces numbers into Booleans.

**Completeness binds membership.** For each of the three inventories, the
completeness answer path contains SHA-256 of UTF-8
`cd4-0.1:<inventory-name>\n<canonical-descriptors>`. Descriptor arrays are sorted
by identity, object keys are sorted, JSON uses no insignificant whitespace and
non-ASCII escaping is disabled. These descriptors contain only strings, arrays
and objects. This exact encoding is specified by `inventory_path`; original
Build and CD-1 bytes remain untouched. Removing or adding a connection, runtime
endpoint or artifact changes that digest and makes the prior completeness answer
inapplicable. Reordering the same descriptors preserves its semantic scope.

**Evidence remains a separate input.** Each consumed answer path has its own
external eligibility value, exactly `true`, `false` or unresolved. The default
is unresolved. No source label, hash, completeness claim or syntax check grants
eligibility. Before real reuse, the consumer must establish the selected
configuration, actual endpoint boundary, complete connection lifecycle/state
inventory and exact artifact-presence evidence for this scope under #41.
The candidate does not derive those facts from a live deployment or catalog.

| Scoped observation | W-R8 finding |
| --- | --- |
| Enabled runtime connection to an endpoint known to be outside | `fail`, even when another inventory or component remains unknown |
| Explicitly disabled connection, or a connection known to occur only during provisioning | `skipped` for that connection; artifacts still require independent readiness |
| Destination known to be inside | `pass` for that connection even if its lifecycle or enabled state is unresolved, because neither alternative creates external egress |
| Runtime endpoint known to be outside, or a required exact artifact known not to be ready inside | `fail` |
| Any other unresolved connection, endpoint, artifact or inventory coverage | `unknown`; absent inventory is never an empty complete inventory |
| All enabled footprints accounted for, all runtime locations inside and exact artifacts ready | `pass` for this isolated predicate; it supplies no overall deployment approval |
| No enabled selections | `skipped` with `no_enabled_selections`; required-component activation remains a preceding contract decision |

The aggregate keeps all per-selection findings in stable order. A known
counterexample wins over unresolved rows; otherwise unknown wins over pass.
Rule identity `W-R8`, candidate version `cd4-0.1`, severity `error` and
`on_unknown: block` remain separate from the outcome. `block` is the proposed
rule policy, not an instruction for this reader to execute or prevent a real
deployment.

The focused suite includes the 27-case connection truth table, complete versus
absent/empty inventories, deletion of a descriptor without a new completeness
answer, exact artifact revision changes, eligibility isolation, disabled and
non-primary scopes, raw-byte identity and malformed/duplicate references. Run
`python -m unittest tests.test_isolation_binding -v` and
`python -O -m unittest tests.test_isolation_binding -v`.

This resolves CD-4's concrete candidate representation and executable research
examples. Actual source admission, broader receiving adoption, successor
schema/ruleset publication and migration remain separate. It supplies no
physical air-gap evidence, jurisdiction decision, hardware result or new
publisher permission. Frozen v1 is unchanged; #2/#3/#9/#37/#40 remain open for
their remaining acceptance criteria, and #42's substantive #40 prerequisite is
preserved.

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

### CD-13 required-presence mode (2026-10-18)

The [current #40 owner disposition, constraint 1](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40#issuecomment-6249840407)
requires a separate answer for missing required components. An actual comparison
against the unchanged frozen
[`rule.required.foundation`](../../contracts/v1/baseline/core-ruleset.json)
reproduces eight differences: removing or disabling each primary workload,
deployment mode, model and context policy makes the frozen required rule fail,
while the universal selection prototype skips its empty enabled scope. That
optional-scope behavior remains correct for the universal mode; it cannot be
used as the required-component answer.

The [required-presence prototype](../../tests/required_presence_prototype.py) and
[16 regression methods](../../tests/test_required_presence.py) add a separate
normalized mode. This is a synthetic mechanics proposal. It adopts no successor
field, sidecar, executable ruleset, migration or native implementation.

| Normalized input | Meaning |
| --- | --- |
| `PresenceSelection(id, kind, role, active)` | An explicit selection identity with independently qualified activation: exact `True`, `False` or `None`; unresolved activation is distinct from known inactive or absent |
| `PresenceRule(id, kind, role, severity)` | Always require the stated kind and exact role; explicit `role=None` permits any role of that kind. Role has no implicit primary default, and severity is fixed as `info`, `warning` or `error` |
| Complete inventory declaration | An explicit exact `inventory_complete=True` is required. Omitted, false, unresolved or malformed completeness and malformed inventory forms are precondition errors; they cannot prove absence or presence |

The declaration is **not proof of completeness**. The caller must first establish
the complete normalized selection inventory, canonical schema/reference
validity and eligibility of every activation fact. This experiment neither
reads a Build nor derives activation, source eligibility or inventory
completeness. It substitutes no defaults for those missing inputs.

The shared identity preflight checks the entire inventory before filtering by
the rule's exact kind/role. Disabled, unresolved and unrelated-kind entries still
participate. The existing strict `(kind, role)` policy is deliberately retained:
even a disabled alternative sharing a role rejects, and duplicate selection IDs
always reject. The earlier co-owner mechanics disposition retained this policy;
the newer owner's preference for allowing disabled alternatives is a separate
reconciliation decision. The frozen dependency/reference wording and protocol
wording are not silently rewritten here. The shared preflight's executable body
and the universal reducer remain unchanged; only its identity-only type
annotation is generalized for the separate normalized entry type.

For a valid complete inventory, reduction is scoped before examining witnesses:

| Matching activation observations | Required-presence outcome | Reason |
| --- | --- | --- |
| At least one known active selection | `pass` | `selected` |
| No known active selection, but at least one unresolved activation | `unknown` | `not_selected` |
| No matching selection, or all matching selections are known inactive | `fail` | `not_selected` |

This mode never returns `skipped`. A selection of another kind or role cannot
rescue an absent required primary or turn that absence into unknown. A known
matching witness establishes only existence, even if another matching candidate
has unresolved activation; that unresolved observation remains unchanged. It
does not establish compatibility, fitness or that another component is optional.
Every scoped activation observation is retained in stable selection-ID order.
An empty result has an empty observation tuple, without an invented selection ID.

The cases compare the four exact primary scopes against the unchanged frozen
foundation rule with all components present and each separately absent or
disabled. A separate normalized example gives each required kind unresolved
activation in turn. Additional cases retain exact role scope, any-role positive
witnesses alongside unresolved alternatives, all-input identity preflight, strict
Boolean identity, fixed severity, order independence and the existing universal
empty/inapplicable skips. The prototype evaluates one required scope at a time;
the foundation-style cases do not adopt a general multi-kind expression or
result wire encoding.

The `all_enabled` reader and its schema below remain unchanged. Conditional
requirements, real activation resolution, the disabled-alternative decision,
structured wire rejections, CD-1/CD-6 binding and affected-owner adoption remain
separate. Frozen v1 and #42's substantive #40 prerequisite are unchanged.

### CD-13 structured identity rejection proposal (2026-10-18)

Constraint 3 in the [#40 mechanics disposition](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40#issuecomment-6249840407)
requires a reason-coded rejection result. Three actual synthetic probes of the
accepted `79960b7` reducer produce a plain `ValueError`: duplicate selection IDs,
two enabled selections sharing a role, and a disabled alternative sharing that
role. All three correctly reject before any predicate. The missing piece is a
machine-readable rejection boundary, not a change to those identity decisions.

The [explicit result boundary](../../tests/selection_result_prototype.py),
[candidate result schema](../../tests/fixtures/selection-result.schema.json) and
[synthetic regressions](../../tests/test_selection_result.py) propose
`cd13-result-0.1`. The caller must select this exact version; there is no implicit
version, older-result reinterpretation or migration. The envelope explicitly
pins `identity_policy: strict_build_wide`. This is a separate test-only proposal
over normalized Python selections and a rule, not adoption of a final wire,
Build reader, ruleset or native adapter.

| Boundary result | Meaning |
| --- | --- |
| `status: rejected`, `phase: identity_preflight`, `reason_code: duplicate_selection_id` | One normalized selection ID appears more than once, including across kinds or disabled entries; the diagnostic retains that exact ID |
| `status: rejected`, `phase: identity_preflight`, `reason_code: ambiguous_selection_role` | More than one selection has the same kind and role under the strict build-wide policy; the diagnostic retains that exact kind/role pair |
| `status: evaluated` with the existing rule result | Identity preflight completed and the unchanged universal reducer returned its fixed severity, outcome, reason and individually attributed findings |

A rejection retains the supplied rule ID and its fixed severity but has **no
rule outcome or findings**. It is not a compatibility failure, an unknown
evidence finding or an inapplicability skip. The two envelope branches reject
extra fields and cannot combine a rejection with an evaluated result. The
schema defines the proposed shape only: it does not authenticate a result or
prove that its reported reason follows from any retained input.

The shared preflight now raises a typed `IdentityPreflightError` carrying its
reason and conflicting identity. It remains a `ValueError` subclass and keeps
the exact original message text for existing Python callers. Identity checks,
their order and the first encountered rejection are unchanged. This proposal
does not promise an exhaustive conflict list or a canonical first conflict when
several independent defects are reordered. Disabled and unrelated-kind entries
still participate; roles remain scoped to kind. The separately reserved
enabled-role policy needs its own explicit selection and review and cannot
silently change this result version.

Only the preflight call is inside the rejection handler. Rule evaluation runs
outside it. A callback's `ValueError`, even one deliberately using the new typed
exception, remains an execution error; a non-normalized predicate return still
raises. No exception message or partially accumulated finding is emitted as a
result. The boundary checks its Python argument shape, normalized identity text,
exact Boolean activation and fixed severity before preflight. Unsupported
versions and malformed Python calls remain API errors, not identity findings.
This bounded shape check supplies no canonical Build/schema/reference validation,
selection inventory completeness, source eligibility or truth of a callback.
Those remain independently established caller preconditions.

For valid inputs, every applicability/assertion truth pair, empty or disabled
scope, all-inapplicable scope, counterexample and unresolved row retains the
original reducer's result. Findings retain stable selection-ID order. Inputs
are not rewritten, and returned documents do not share mutable findings across
calls. The required-presence mode and existing typed binding retain their
current APIs and policy; required absence is still distinct from universal
empty-scope skipping.

The regression cases exercise both rejection codes, disabled/other-kind
ambiguity, all activation pairs and input orders, callback isolation, strict
version selection, malformed Python arguments and mutually exclusive schema
branches. Existing callers' exception compatibility and required-presence
behavior have explicit controls. These are synthetic mechanics checks only.
Frozen v1 is unchanged. A full untrusted-input reader, adopted result wire,
source-bound verification, affected-owner integration and #42's substantive
#40 prerequisite remain separate.

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
CD-7/SB-2 and part of SB-3/SB-R1. The catalog/pricebook resolver alone does not
establish complete replay: evaluator, ruleset, graph, derived estimates and
external evidence need their own exact pins. The bounded frozen-reference
profile below now exercises those additional retained inputs. Neither profile applies price eligibility
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
| `artifact_representation_unsupported` | The capture timestamp or a declared artifact ID/reference is outside the explicit consumer profile below. Return no artifact; retain the original bytes and independent artifact outcomes. Frozen-v1 validation remains unchanged. |
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
descriptor fields in this profile have ASCII values; the consumer explicitly
checks `captured_at` against the supported timestamp profile below, independently
of optional JSON Schema format support. This binds both artifacts
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

#### CD-7 timestamp and ID admission correction (2026-10-18)

The [#40 owner's constrained disposition](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40#issuecomment-6249840407)
identified an ASCII-only date check and incomplete ID anchors. The bounded
consumer now checks both advertised capture strings and the received original
artifact's `captured_at`, using the existing intake timestamp parser without
optional format-checker packages. Its explicit RFC 3339 subset requires an ASCII
Gregorian date with years `0001`–`9999`, seconds `00`–`59`, `T`/`t`, and either
`Z`/`z` or a numeric offset through `23:59`. Fractional seconds retain every digit;
neither strings nor original bytes are normalized. Valid leap-second spellings
remain explicitly unsupported by this profile. See [RFC 3339 sections 4.3, 5.6
and 5.7](https://www.rfc-editor.org/rfc/rfc3339.html#section-5.6), checked
2026-10-18. This is a representation check: it does not compare capture times,
establish freshness or interpret an unknown local offset as a new source fact.

A private consumer validation view adds complete-string bounds wherever the
frozen schemas already declare their entity-ID or selection-ID pattern,
including inlined catalog references. The frozen schema objects and files are
unchanged. Untyped extension fields named `id` or `captured_at` keep their
original values; they are not mistaken for declared contract fields.

A newline-suffixed rate ID is now withheld as
`artifact_representation_unsupported` before membership or result encoding.
The pair stays `incomplete`, the other artifact remains inspectable and no Build
verdict is produced. A well-formed rate referring to another catalog still
returns `rate_catalog_mismatch` with its exact unmatched ID. Invalid declared
Build IDs reject as `invalid_cd7_input`; malformed envelope selection IDs reject
as `malformed_envelope`. No ID is stripped or repaired.

The added offline regressions disable optional format checks, exercise invalid
calendar/offset and trailing-byte cases at both receiving points, preserve
supported fractional/offset strings and byte identities, and retain all original
wire fixtures. These are test-only admission corrections to the existing
candidate. The historical receiving receipts above retain their original source
scope; this correction does not adopt a successor interface, implement migration
M1–M5, qualify source use or supply native-owner acceptance.

#### CD-7 unresolved-record diagnostics and rule gate candidate (2026-10-18)

This bounded candidate addresses the presentation and dependent-rule mechanic in
[the #40 owner's CD-7 constraint 2](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40#issuecomment-6249840407).
Actual probes of accepted `d98fbe716f49c0da3782655acfd5d1b3f471cafc` found that
the existing consumer already retains each record's specific failure reason.
Its selection rows use `snapshot_unresolved` for a missing or withheld catalog;
it does not provide a presentation or dependent-callback boundary. This work
adds that boundary without describing the existing record resolver as defective.

The [local prototype](../../tests/t0_cd7_diagnostics_prototype.py) requires the
explicit proposal version `cd7-diagnostics-0.1`. Every inspection and rule call
invokes the actual `cd7-consumer-0.1` inspector against the supplied request,
original build, sidecar and immutable fixture archive. Callers cannot supply a
replacement inspection dictionary. The exact existing consumer response bytes
are retained, with no protocol or schema change. The new frozen Python result
objects are a normalized test API, not an adopted serialization or native wire.

Each diagnostic identifies the record kind, available ID and representable
revision, preserves the original reason code, and renders
`cannot be reproduced: <record>`. A revision omitted by the existing native
range boundary remains omitted; the helper does not round it or invent a pin.
Diagnostics contain these identifiers and reason codes, not record payloads.

| Actual consumer state | Dependent-rule behavior |
| --- | --- |
| Missing pin, unavailable exact pin or digest mismatch | `unknown` with `dependency_unresolved` and the original per-record reason code. The existing digest-mismatch precedence remains, including when a producer also withholds the record. |
| `revoked` or `temporarily_unavailable` catalog | Every enabled selection depending on that snapshot receives its specific catalog cause. Both applicability and assertion callbacks remain uncalled. |
| Unsupported native revision, artifact byte limit, structure or representation | `unknown` with the distinct existing reason and the record identity that the consumer can represent. No latest candidate or default is substituted. |
| Selected version absent or selected kind mismatch | `unknown` with that selection's membership reason. These are not assertions that a component capability is unsupported. |
| Pricebook unavailable, with a resolved catalog | Pricebook/pair-dependent rules remain unknown; independent catalog or selection rules retain their own evaluation. |
| Catalog/Pricebook rate mismatch | Rules requiring the complete pair remain unknown with `rate_catalog_mismatch`. A resolved individual record alone does not establish cross-record membership. |
| No Pricebook selected | No global error or zero price is synthesized. A rule explicitly requiring the Pricebook or pair gets `unknown` with `pricebook_absent`; a required pair also retains any independently unresolved catalog cause. |
| Known disabled selection dependency | A fully known disabled scope gets `skipped` with `not_enabled`. If another declared dependency is unresolved, the result remains `unknown` and also identifies the disabled dependency. |

Rules declare an immutable tuple of exact dependencies: `record` with
`catalog_snapshot` or `pricebook`, `selection` with an existing selection ID,
or `pair` with `catalog_pricebook`. Duplicate, malformed or nonexistent selection
references reject the local call rather than becoming an empty scope. A required
kind that has no selection is governed by the separate required-presence
candidate; this API does not infer a selection or replace that rule.

The tuple is a **reviewed-input assumption**, not a dependency compiler. The
helper cannot determine whether an arbitrary callback concealed an additional
read. Cross-record rate checks must declare the pair; declaring only the
Pricebook means only that individual record's identity/availability is checked.
An empty tuple explicitly declares an independent rule. It can run while other
records are unresolved, without making the build or those records valid.
Real ruleset dependency extraction and affected-owner adoption remain required.

After dependency gating, both callbacks must return exactly `True`, `False` or
`None`; truthy strings, numbers and containers reject. Known non-applicability
skips, unknown applicability stays unknown, and a resolved dependency set alone
never supplies a passing assertion. The caller supplies one fixed
`info`/`warning`/`error` severity for the rule. Callback exceptions, malformed
requests, unsupported protocol versions and invalid local declarations remain
execution/input errors; they are not caught as missing-record findings.

**Historical visibility is separate.** A caller may retain an existing
`ReplayResult` alongside the diagnostic view. Its original build and sidecar
must match the current call byte for byte; identical JSON values or IDs do not
transfer that binding. The helper preserves that same object, its original
manifest and report bytes, findings and status, without executing the evaluator,
rewriting the report or upgrading an unavailable historical replay. It does not
authenticate an arbitrary caller-created historical object. No prior `pass` is
used as a current rule result. This opaque local carrier is not a sharing/export
format, a sanitization pass, or authority to display restricted source material.
Publication, source use, historical authenticity and current compatibility remain
explicitly `not_established` by this inspection mechanic.

The [synthetic regressions](../../tests/test_t0_cd7_diagnostics.py) exercise these
cases through actual consumer and historical-replay fixture paths, including
both missing inputs in a required pair, all enabled selections, callback error
propagation, unchanged response bytes and separately retained historical reports.
Run `python -m unittest discover -s tests -p test_t0_cd7_diagnostics.py -v` and
the same command under `python -O`. The synthetic historical control reproduces
the retained 45-finding example; it supplies no real measurement or source grant.

The frozen import, existing consumer/replay implementation and original fixtures
remain unchanged. M1–M5 integration, per-component migration, successor schema
and protocol dispatch, original/current ruleset views, projection/share paths,
source admission and native receiving acceptance are separate tasks. This
mechanics candidate follows the owner's standing queue criteria; it does not
mark that owner's constraint closed or complete #40/#42's research acceptance.

### CD-7 configuration-only share and fork path (2026-10-18, test-only)

This versioned prototype addresses the byte-binding path in **CD-7 constraint 5**
of the [#40 owner disposition](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40#issuecomment-6249840407).
It applies the existing [share/export sensitivity table and fork proposal](saved-shared-builds.md#field-sensitivity-for-shared-links-and-exports)
to synthetic frozen-v1 inputs. This is a bounded mechanic for that queue; it does
not claim that the owner adopted a field, wire encoding, migration or native
adapter. The separate constraint-2 diagnostics work retains its
[canonical owner](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40#issuecomment-6252851908).

The complete experiment is
[`t0_cd7_projection_prototype.py`](../../tests/t0_cd7_projection_prototype.py),
its [closed-shape schema](../../tests/fixtures/t0-cd7-projection.schema.json), and
[synthetic controls](../../tests/test_t0_cd7_projection.py). Callers must explicitly
select **`cd7-projection-0.1`**; the sole profile is `configuration_only`.
The existing `cd7-consumer-0.1` envelopes and frozen v1 remain unchanged.

| Boundary | Concrete behavior |
| --- | --- |
| Private factory input | Read the original frozen Build bytes and optional original `x_t0_revision_locks` bytes locally. Reuse schema, strict build-wide selection identity and exact original sidecar checks. These private bytes never become fields of the new transport envelopes. |
| Projection | `x_t0_cd7_projection` retains schema version, component ID/kind/catalog item/version/role/enabled, exact links and locks. It also carries its identity, original source ID/revision/byte hashes, source catalog/Pricebook pins, explicit answer states and qualification limits. This is a partial view, not a schema-valid BuildSnapshot. |
| New sidecar | `x_t0_cd7_projection_binding` carries only the explicitly selected protocol and the **new projection's** SHA-256 and byte length. Source pin values are inside the hashed projection, so a sidecar cannot alter them independently. It never reuses the original Build digest as the projection digest. |
| Share and export | Both use the same private factory and default redaction. A downloadable export has no additional settings or secret-bearing path. No link, account, storage record or remote service is created by this prototype. |
| Read | Validate both closed envelopes, exact bytes, full-string IDs, exact integer representations, source/lock pin identity and the recomputed answer-state map before returning the partial view. No archive fetch, latest fallback or evaluation is dispatched. |
| Fork | Require an explicit new Build ID, different from the source. Produce `fork_draft` at revision **1**, retaining source ID/revision and the exact parent projection digest as lineage. Rebind these new bytes with a new sidecar. The result is an unanswered draft requiring completion before any frozen Build validation or evaluation. |

**Default redaction is conservative and explicit.** This profile omits every
selection's entire `settings`, `notes` and `extensions` groups, along with the
Build's name, owner, lifecycle, created/updated metadata, objectives, policy and
extensions. It therefore omits credential/account/encryption/connector references,
internal endpoints and artifact locators, free text, classification, region,
budget/volume inputs and organisation attestations. It offers no opt-in group in
this version. Declared omitted groups remain marked even when absent in the
source, so the projection does not disclose their presence or private child keys.
Public component/link identities and disabled flags remain exact; redaction does
not replace them with guesses or remove an inactive alternative.

The transport also rejects a decoded `secret://` locator, case-insensitively,
if it is disguised as an otherwise public version or object key. This is an
explicit locator and field-boundary check, not a claim of arbitrary secret-content
detection. Public configuration labels are still caller-supplied, unqualified
data. All test locators and private-field canaries are synthetic; no real
credential, user input or evidence payload is included.

**Unanswered fork inputs stay unresolved.** Shares mark omitted groups `withheld`.
Forks mark those same groups `missing`, without copying their source values,
presets, attestations or approvals. Public configuration leaves remain `provided`,
including `false` and exact integer values. The reader recomputes this complete
map from the declared profile and public configuration; a peer cannot change a
withheld owner or setting to `provided` or `not_applicable` merely by recomputing
the envelope digest. The existing typed CD-1 reader gives dependent compatibility
rules `unknown` with `answer_withheld` or `answer_missing`, including under
negation, without calling a predicate on the missing value. A known disabled
configuration retains its separate applicability semantics and fixed rule severity.

**Provenance is distinct from authority.** Original Build and sidecar hashes
identify the private source bytes the factory read; catalog and Pricebook pins
remain exact source provenance. A missing pin remains absent, including when no
source sidecar was supplied. A self-consistent public projection and digest do
not authenticate its issuer, prove derivation from those private bytes, resolve
an artifact, grant display rights or establish current compatibility. Those
qualification fields remain explicit. This profile copies no historical report,
finding observation, cost line, validation lifecycle or derived success into the
share or fork. A separately reviewed, rights-aware historical-result projection
is still needed for the full SB-R2/shared-view requirement; a report for the
original Build can never serve as the new fork's assessment.

The local profile admits frozen-v1 source bytes up to 512 KiB and each new envelope
up to 64 KiB, with the existing consumer's depth/node limits and Unicode-scalar/
decoded-key checks. Public revision identities use JSON integer tokens in
`1..2^63-1`; Boolean and floating-point aliases reject. These limits and the
`1.0.0` schema pin belong to this new experiment, not a frozen-contract edit.
Successor artifacts or another redaction profile need an explicit versioned path.

**Observed controls:** the unchanged resolver admitted all 29 original synthetic
selections but correctly rejected a required-field-redacted object, a new fork ID
with the old sidecar, and equivalent reformatted bytes with the old digest. Those
are correct original integrity checks demonstrating why a separate path is
needed. During local preparation, an initial candidate allowed a source-pin
revision to change outside the projection digest; that unpublished checkpoint
and actual observation are retained. The corrected shape moves those pins inside
the hashed projection and rejects the old extra sidecar field. The 22 focused
methods cover schema-defined private fields, new byte bindings, pin tampering,
fork identity/lineage, typed missing/withheld outcomes, false/zero distinctions,
malformed/oversized JSON, Unicode controls and original-byte preservation.
Actual final-source workflow results and independent review remain recorded with
the delivering PR, without relabelling an earlier checkpoint's execution.

The source Build, original sidecar, retained artifacts and historical results are
never rewritten. Migration M1–M5, component-mode adoption, source-rights decisions,
private-group opt-ins, authentication/revocable links, storage, complete shared
historical/current views and native receiving acceptance remain separate work.
#40 and #42 remain open with their current assignees and acceptance gates.

### CD-7 historical reference replay candidate (2026-10-18)

**Engineering decision:** extend the existing CD-7 archive with a separate,
versioned replay manifest. Keep the original build, revision sidecar, input
documents and historical report byte-for-byte. The
[manifest schema](../../tests/fixtures/t0-historical-replay.schema.json),
[synthetic manifest](../../tests/fixtures/t0-historical-replay.json) and
[executable prototype](../../tests/t0_historical_replay_prototype.py) implement
one supported historical path: the unchanged frozen-v1 Python reference
evaluator. This is a completed testable proposal for that path, not adoption of
a successor reader or migration of a saved build.

The frozen [evaluator source](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/907c1ed1ba5bc975cd8b0a9981e56a32648387c0/contracts/v1/reference/evaluate.py)
and [report schema](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/907c1ed1ba5bc975cd8b0a9981e56a32648387c0/contracts/v1/schemas/evaluation-report.schema.json)
were inspected on 2026-10-18. The evaluator consumes a build, catalog and
ruleset, plus explicitly supplied resource/cost estimates. It neither evaluates
the dependency graph's edges nor recalculates costs from price rates. Its report
copies graph locks and uses the fixed demonstration timestamp
`2026-10-16T09:00:00Z`. The replay preserves these historical behaviors instead
of substituting current data or assigning a new evaluation time.

The `x_t0_historical_replay` manifest uses proposal version `cd7-replay-0.1`:

| Retained identity | Exact binding and use |
| --- | --- |
| Build and existing CD-7 sidecar | SHA-256 of each original byte string. A changed build, whitespace-only rewrite or different sidecar cannot reuse the manifest. An explicitly absent sidecar remains missing pins. |
| Evaluator | Allowlisted profile `frozen-v1-reference-py312-decimal28`, evaluator source SHA-256 and frozen schema-bundle SHA-256. The manifest supplies no executable, path, URL, import name or metrics override. |
| Catalog and optional pricebook | Existing CD-7 exact kind/ID/revision/digest pins. A locked pricebook must resolve even when no cost estimate was supplied. |
| Ruleset | Exact ID, version and content digest, agreeing with the build locks. |
| Dependency graph | Exact ID, integer revision and content digest, agreeing with the build locks. Retained and checked as an associated historical input; edges are not newly interpreted. |
| Resource and cost estimates | Each slot is present and either explicitly `null` (not supplied to the original evaluation) or pinned by ID, build ID, build revision and digest. A missing pinned input aborts replay; the sole available estimate is never inferred. |
| Retained report | Exact ID, build ID, build revision and digest. A report is required to demonstrate reproduction, with all catalog/ruleset/graph locks cross-checked against this build. |

The allowlisted evaluator source digest is
`092c8a99495f9b5ae960df40b27e33f15eefe6d1a7cd80119658fdc79ada1a5a`.
The schema-bundle digest is
`eaaf51a04c9bd0c7fce23e7ecc75724226e26b337cc1da04b88a59d2a912914f`:
sort the 14 `contracts/v1/schemas/*.schema.json` filenames, construct the array
of `[filename, sha256-of-original-bytes]` pairs, serialize with ASCII escaping,
no spaces and no trailing newline, then hash those bytes. The local files and
loaded schemas must match before execution. The prototype compiles the exact
verified local evaluator bytes, with Python 3.12 and a fresh Decimal context
(28 digits, half-even rounding and the standard exponent/trap settings), so a
caller's changed Decimal precision cannot change the replay. Use the repository's
pinned validation dependencies from `requirements-research.txt`.

**Cross-record association.** The wrapper places these checks before evaluator
execution, providing an executable candidate for the historical portion of
SB-R1, SB-R2, SB-3, SB-5 and SB-10. After artifact resolution, every enabled
selection must resolve to its exact catalog ID/version and matching kind.
`selected_version_absent`, `selected_kind_mismatch` or another unresolved
enabled association produces `input_identity_mismatch`, with its selection ID
and resolver status in `issues`; `not_enabled` remains allowed. This boundary
matters because the frozen evaluator's metrics sometimes index by ID alone,
and some selected kinds can produce no rule finding for a broken reference.
A matching report cannot certify that missing association. The original report
bytes remain retained; the wrapper does not rewrite historical findings. An
ordinary historical rule failure or unknown with resolved input identities
still reproduces as invalid or indeterminate. Derived records must belong to
the exact build ID and revision. Resource-estimate selection references must
exist in that build;
cost lines must refer to a selection and an exact rate in the locked pricebook,
with matching selected catalog ID/version and meter. Unpriced selection IDs
must also exist. Every retained price rate must belong to the selected catalog
snapshot. These are identity checks, not pricing eligibility, estimator
calibration, billing arithmetic, source authenticity or evidence grading. The
frozen evaluator retains its own incomplete/nonmonthly/currency-mismatched cost
behavior and resource-confidence handling.

| Result | Meaning |
| --- | --- |
| `inputs_unavailable` | A required pin or its exact bytes are missing. Per-input bindings retain the missing-pin versus missing-artifact distinction. No evaluator call occurs. |
| `input_digest_mismatch` | An exact key exists but the bytes disagree. The binding returns no artifact values. |
| `input_identity_mismatch` | Retained artifacts resolve, but an enabled selection's exact catalog ID/version/kind or another build/lock/selection/rate association disagrees. |
| `profile_unavailable` | Requested evaluator/schema identity, local files or interpreter family do not match this supported profile. No archive-supplied code executes. |
| `profile_unsupported` | A catalog contains several versions of one item ID. CD-7 can resolve these, but the frozen evaluator indexes by ID alone; the wrapper refuses to select an arbitrary version for it. |
| `evaluation_failed` | The unchanged reference evaluator cannot evaluate these retained inputs or emit a conforming report. Original findings remain available in their retained bytes. |
| `report_mismatch` | A report was generated, but its complete typed JSON differs from the retained report, including ordered findings, summaries, identity, timestamp or numeric representation. |
| `reproduced` | The complete generated report matches. Historical `invalid` or `indeterminate` remains that outcome; reproduction does not make it valid or current. |

**Unavailable-reader retention correction (2026-10-18):** the original replay
candidate returned `profile_unavailable` before resolving input bindings. With
the evaluator file absent, the result had no report binding even when the exact
pinned historical report remained in the archive. Reader failure now preserves
all independently resolved data bindings and their diagnostics. The result keeps
`profile_unavailable` as its status and lists the evaluator issue first, followed
by any missing, digest-mismatched or cross-record identity issues. A resolved
report binding retains its original bytes; a missing or tampered report retains
its own unresolved status and no bytes. No evaluator instance runs on this path,
and no generated report, replacement input or validity claim is created.

**Independent retained-report association correction (2026-10-18):** a later
synthetic probe at accepted `1b3143c` found that an unavailable catalog could
conceal an independently checkable report mismatch. The same explicitly pinned
report for a different build produced `build_identity_mismatch` when the other
inputs existed, but only the catalog's unavailable diagnostic when that catalog
was removed. Its byte-bound report binding remained available in both cases.

Every return path now checks an independently resolved report's build ID,
revision and five historical lock fields against the retained build. Existing
`build_identity_mismatch` and `build_lock_mismatch` diagnostics remain visible
alongside an unavailable pin, artifact, digest or evaluator. Existing failure
precedence stays intact, duplicate diagnostics are not appended, and no
evaluator runs merely to establish these associations. An unavailable or
digest-mismatched report supplies no association assertion from unbound bytes.

The [eight synthetic regression methods](../../tests/test_t0_replay_association_retention.py)
include the actual original missing-diagnostic cases, unchanged complete-input
failures, all five report locks, both build identity fields, absent pins,
digest/profile failures, matching reports and an unrelated unselected report.
All retained bytes and historical findings remain unchanged. A binding's
`resolved` status still describes exact-key and byte resolution; consumers must
also inspect the association diagnostics before presenting those bytes as the
historical report for the requested revision. This is a prerequisite for the
unresolved-state view in [CD-7 constraint 2](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40#issuecomment-6249840407),
not that view, a released migration, native acceptance or completion of #40/#42.

Malformed JSON, invalid schemas, duplicate immutable keys and manifest/build/
sidecar binding errors fail explicitly as value errors before evaluation.
The candidate reuses the CD-7 strict Unicode/JSON and depth/node boundaries,
caps each artifact/build at 512 KiB and each manifest/sidecar at 64 KiB, and caps
the archive at 32 records and 8 MiB. New revision identities require positive
signed-64-bit JSON integer tokens. These are receiving-profile constraints;
the frozen schema files remain unchanged. Existing build-wide identity/role
preflight still includes disabled selections. The wrapper does not rewrite a
legacy input that this profile cannot admit.

**Integrity is separate from authenticity and availability.** Every result's
`qualification` keeps authenticity, source use and current compatibility at
`not_established`. A manifest records the declared original input set; creating
one after the fact cannot prove which inputs a real historical run used. In
particular, an unknown original estimate choice cannot be silently recorded as
`null`. Missing source records are not recovered by a matching report, and a
matching digest supplies no publisher or retention/display permission. The
prototype performs no network fetch, native cache activation, external-evidence
revalidation, new estimation, dual-ruleset migration or production publication.

The [focused regressions](../../tests/test_t0_historical_replay.py) reproduce all
45 findings of the existing synthetic report (41 pass, four skipped), preserve
hand-authored invalid/unknown historical cases, reject missing/tampered and
cross-build inputs, exercise explicit optional-input absence, and verify local
evaluator/schema changes, numeric context, input bounds and complete report
comparison. Run `python -m unittest discover -s tests -p
test_t0_historical_replay.py -v`. These findings are synthetic demonstrations,
not hardware, model-quality, source-rights or current-runtime evidence. #40 and
#42 remain open for the remaining contract, migration and receiving decisions.

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

## Current research decision and receiving packet — 2026-10-18

**Status: prepared for current-source and directional receiving review.** This
continuation uses accepted main [cae31f324f827cdeb73548b72cafd392dd777dfa](https://github.com/Pick-Your-AI/pick-your-ai-research/commit/cae31f324f827cdeb73548b72cafd392dd777dfa).
The preceding record is retained in full. Its earlier "open", "proposed",
"reserved" and execution statements describe their own checkpoints; the dated
dispositions below identify what has since been received or delivered. This
packet itself supplies no response on behalf of a consumer.

The research choice remains option B: retain the adopted frozen v1 interchange
and historical evaluation, and develop explicitly versioned successor proposals
with typed inputs, scoped evidence and an explicit migration. The issue asks
for the representation, rule and recomputation **research decision**. Its
literal scope excludes UI design and rule-engine implementation. A completed
research example need not execute a production model, service or native client;
a genuinely unresolved field, policy or receiving decision still needs its
stated review. The [adoption record](../../contracts/v1/ADOPTION.md), current
[research workflow](../../docs/RESEARCH_WORKFLOW.md) and
[rule proposal template](../../templates/rule-proposal.md) remain the governing
boundaries.

### Minimum comparison fields: exact current mapping

This table addresses all twelve minimum comparison fields in the
[original #40 issue](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40).
It refines the conceptual names against the actual imported
[CatalogItem](../../contracts/v1/schemas/catalog-item.schema.json),
[common definitions](../../contracts/v1/schemas/common.schema.json),
[Ruleset](../../contracts/v1/schemas/ruleset.schema.json),
[CatalogSnapshot](../../contracts/v1/schemas/catalog-snapshot.schema.json) and
[EvaluationReport](../../contracts/v1/schemas/evaluation-report.schema.json)
inspected at the accepted revision above on 2026-10-18. The larger component
dictionary remains a registry of proposed category fields with its own
per-field source requirements.

| Issue comparison field | Type, location and unit | Evidence and missing-value treatment |
| --- | --- | --- |
| entity_id | CatalogItem.id is the common canonical identifier string with the declared 3–120-character grammar. Receiving profiles separately enforce full-string identity. It is an identity, with no physical unit. Selection identity and selected catalog identity are separate. | Resolve the exact selected item/version in the declared snapshot. A matching name or ID alone supplies no capability, source permission or version match. |
| category | CatalogItem.kind is one of the canonical registry's string values; tier is the separate tier field. Neither is a numeric quantity. | Use the [component registry](../../contracts/v1/schemas/component-registry.json) and the kind-specific schema. A product name or provider name cannot choose a different kind or infer deployment mode. |
| version / snapshot | CatalogItem.version is a nonempty string, not a required SemVer. CatalogSnapshot has a canonical ID and integer revision ≥ 1. Build selections retain catalog_item_id and catalog_item_version; CD-7 separately proposes exact revision/digest pins. No physical unit. | Keep publisher release/commit/alias identity and snapshot capture distinct. Current one-version-per-ID intake stays in force. A missing exact revision is unresolved, never a request to select the newest artifact. |
| lifecycle status | CatalogItem.status is active, preview, deprecated or retired; a categorical value without a physical unit. | Retain source/date and exact item/offering/version coverage. Deprecation, availability and support are separate predicates. Omission from an incomplete snapshot cannot establish retirement; source use remains a separate #41/#60 decision. |
| valid_from / valid_to | These are conceptual temporal coverage bounds, not fields currently present on every CatalogItem. Existing snapshot captured_at, item updated_at and provenance checked_at are timestamp strings with different meanings. Price rates separately use valid_from and optional valid_until. | Do not turn observation/publication dates into effective validity bounds. Retain a publisher's stated interval where the applicable record supports it; an unestablished bound stays unestablished. Version-pinned facts do not gain a TTL, and current-state facts retain their dated scope under #41. A general claim-window encoding remains an explicit CD-7/#41 follow-up. |
| source refs (see #41) | CatalogItem.provenance is a nonempty array of records containing checked_at and verification_status, with source_uri and notes supported by the common definition. Submission policy separately requires a public HTTP(S) source URI for new catalog/price provenance. References and grade labels have no physical unit; dates retain their timestamp meaning. | Preserve primary URL, access date, version and relevant conditions. The frozen schema alone does not require or authenticate every source URI. Rule proposals carry claim-level sources in the note; frozen rule objects have no universal per-rule provenance field. The CD-3 carrier records dated scoped sources and caller qualification without performing that review. |
| rule_id | Each Ruleset.rules entry has a common canonical identifier string. No physical unit. | An ID identifies a rule within its exact ruleset version. Keep historical identity and source definition; do not interpret a later same-named rule as the historical one. |
| rule participants | Frozen expression operands identify build/catalog/selection scope and a pointer, with kind, role or selection_id where applicable. affected_kinds is a nonempty unique kind list for affected scope; it is not a complete relationship join. These are identities and paths, without physical units. | Record participating selections, roles, fields and relationships explicitly in the research template. Identity/role ambiguity rejects in the applicable preflight; missing eligible operands stay unknown. CD-6/CD-13 retain broader relationship and multi-kind binding decisions. |
| severity | One fixed enum value: info, warning or error. No physical unit. | Severity comes from the reviewed versioned rule, independently of pass/fail/unknown/skipped and any evidence label. A different required severity calls for a distinct rule or versioned decision. |
| explanation | Frozen rule message and remediation are nonempty strings; report findings retain their rule outcome and any supplied evidence context. Text has no physical unit. | Explain the actual known violation, unresolved input, inapplicability or rejection. CD-1 typed reasons preserve missing, unknown, withheld and not-applicable causes; a generic Boolean adapter cannot claim that richer output. |
| suggested correction | Frozen rule remediation and the research template's correction are text, without a physical unit. | Offer a changed selection, evidence request or explicit policy choice with its prerequisites. A suggested replacement is not a silent selection edit, a new entitlement or proof of compatibility. |
| rule version | Ruleset.version uses the imported SemVer-shaped string. Individual frozen rules have no version field; the research decision versions the ruleset and its changelog. A prototype's own proposal/rule version identifies that selected experiment only. No physical unit. | Build locks pin ruleset ID/version, and retained replay also binds content/evaluator identities. A rule change does not rewrite earlier findings. A successor result or migration must state its exact version; unsupported dispatch remains explicit. |

The source/grade rules above use the actual
[#75 interim-policy adoption](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75#pullrequestreview-5550616927)
and the current [#41 record](catalog-data-sources.md). That dated review's
historical sizing suggestions are not current headroom defaults: current
[compute research](../T2-infrastructure/gpu-compute.md) and the accepted
[context/KV interface](../T1-model-selection/context-window.md#current-kv-cache-handoff-to-10)
require explicit reserve and matching expansion/allocation/residency. This
continuation adds no price, measured value, vendor capability or source-access
claim.

### Current semantics and finite contract follow-ups

The [12:20 owner disposition](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40#issuecomment-6249840407)
separates accepted normalized mechanics from field, wire, ruleset and migration
adoption. The [16:00 ledger](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40#issuecomment-6252011763)
also distinguishes owner-checked constraints from delivered source awaiting
that owner's reread. Both distinctions are retained here. "Delivered" below
describes the contribution; it does not manufacture an owner "Closed" decision.

| Decision | Current research content and actual disposition | Finite remaining decision / accountable issue |
| --- | --- | --- |
| CD-1 answer states | Five distinct states, exact pointer/source causes, safe typed negation and state-specific terminal reasons are recorded. Known-value schema admission, withheld-parent visibility and the explicit 0.2 preset-attribution candidate are delivered. An unresolved value never acquires a default or evidence grade. | #40 selects the successor field/reader/result representation with #2/#3/#42; preserve explicit opt-in versions and actual assumption/source attribution. Existing 0.1 callers are not silently upgraded. |
| CD-2 memory placement | Per-rank and per-pool accounting, device instances, co-residency and placement remain the declared design scope. [6251561799](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40#issuecomment-6251561799) reserves the normalized physical-pool proposal. | The canonical #40 writer and #10 complete and review that exact candidate. No competing implementation, pooled nominal VRAM, inherited headroom default or measured residency is supplied here. |
| CD-3 evidence and support | Requested completeness, explicit/exhaustive negatives, unmarked omission, disputes and qualified checked-only labels have concrete mechanics. [#372](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/372) delivered the source/date carrier and the two actual frozen-rule gates at signed 3085e1f7; the [C3](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40#issuecomment-6252536259) and [C4](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40#issuecomment-6252523637) receipts retain actual source/test identities. | #41 with #40/#10/#62 owns actual source/rank/protocol qualification and comparable result evidence; #40 owns successor binding/adoption. The two explicit APIs remain separate: joint delivery did not wire them together or establish per-member source attribution. |
| CD-4 isolation | The typed endpoint, runtime-connection and exact-artifact inventory candidate makes W-R8's scoped known failure, unknown coverage and known non-applicability reviewable. | #40 with #2/#3/#9/#37 reviews the representation and actual boundary/evidence integration. Provider operation or a network label cannot prove physical isolation. |
| CD-5 stage workload | The workload note's explicit stage inputs separate requests, units, input/output applicability and readiness; its later corrections retain strict numeric/identity admission. Current context research separately receives complete input and sequence/allocation distinctions. | #40 with #10/#7/#39 owns exact successor stage/association fields and any aggregation rule. Means/maxima are not uncertainty intervals; stage peaks and retries are not an inferred simultaneous workload. |
| CD-6 relationships | Explicit credential-source selection has a bounded exact-byte candidate. Model/base/adapter, mount/fetch, provider, hardware and licence-condition relationships retain the wider documented scope. | #40 with #6/#11/#13/#30/#33/#35 decides the complete relationship/role and inheritance representation. Catalog/reference presence does not establish effective authorization, lineage, export rights or the actual serving tuple. |
| CD-7 versioning and migration | M1–M5 research semantics were accepted in [#126 review5560506323](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/126#pullrequestreview-5560506323); [5560765303](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/126#pullrequestreview-5560765303) resolved the earlier legacy-mode inference objection. Exact pins, bounded native interchange, historical replay and unresolved-record diagnostics now have separate delivered proposals. | #40/#42 with #41/#39 still decide successor dispatch, full M1–M5 migration and historical/current views. The separate [constraint-5 reservation6253669705](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40#issuecomment-6253669705) / [#383](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/383) owns configuration-only projection and report-association work; its current-source review and delivery remain with that writer. |
| CD-8 community evidence | Independence and qualification remain distinct from a source label, reporter identity or repeated observation. Existing #41 policy and dated evidence boundaries govern the research. | #41 defines reporter/execution independence, admitted comparison protocols and any policy allowing community evidence to decide a verdict, with #10/#36/#62. No numerical promotion threshold is invented. |
| CD-9 jurisdiction | The #41 hierarchy and exact provider-region mapping candidate preserves source, scheme/version and scoped containment; unresolved or ambiguous mapping stays unknown. | #41 with #9/#40 decides current qualified mappings and successor bindings. A region name, geographic hierarchy or valid mapping input is not residence, legal applicability or actual data-location evidence. |
| CD-10 non-model runtimes | The deployment matrix explicitly leaves non-model service requirements separate from model-engine CPU/ISA predicates. | #40 with #11/#15 defines source-backed requirements for the selected non-model service/operation. A vector database or other service does not inherit an inference-engine requirement from its kind alone. |
| CD-11 context | Shared versus separate input/output semantics, native fallback and exact route/tokenizer/settings binding have research examples and a typed candidate. Accepted #378 supplies the current complete-request, KV and cost receiving record. | #40 with #7 retains exact source/field normalization and successor adoption; #10 owns matching cache geometry, admission/residency and actual resource evidence. Context fit does not establish KV capacity. |
| CD-12 organisation attestations | The dictionary names jurisdiction, EU-market placement, lawful-basis, revenue and monthly-active-user questions, with sensitive provenance and condition scope; it does not settle the full type/aggregation/wire representation. | #40 with #30/#31/#32 decides exact condition/subject/period reuse and types. #42 preserves non-transfer on sharing/forking. A technical representation does not supply a legal assessment or another organisation's answer. |
| CD-13 selection and required presence | Universal all-enabled findings, required-presence pass/fail/unknown and typed identity rejections retain different meanings. The actual 16:00 owner ledger accepts the explicitly stated strict build-wide role policy for this prototype. The optional disabled-role experiment is [parked and released](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40#issuecomment-6251969365). | #40 retains strict identity behavior and its explicit result profile. Earlier paragraphs that call the disabled-role option reserved/open are historical; no policy rewrite is required for that accepted choice. Real per-component applicability, multi-kind rules, CD-1/CD-6 integration and final result-wire adoption remain separate. |

The generic research rule format is already usable for a proposed source,
rights or freshness predicate: state participants and pointers, applicability,
one assertion and its evidence, one fixed severity, missing-data policy,
explanation/remediation, dependencies, all outcome examples and version impact.
Its review is distinct from executing a source adapter or adopting an expression
language. A successful identity or shape check establishes that bounded check;
compatibility, evidence eligibility and permission retain their own predicates.

### Directional receiving packets

The original issue declares information inputs from #2/#3, bidirectional
compatibility with #6/#10/#11, and the ten downstream consumers below. The
directions must remain visible. The
[#75 #2/#3 and T2-C01–C06 disposition](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75#pullrequestreview-5550616927)
and [#126 T1/#40 review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/126#pullrequestreview-5560506323)
already receive their specified inputs and examples; a component's later
source revision still retains its own scope. The
[#14-to-#40 receipt6253659087](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/14#issuecomment-6253659087)
and [#62-to-#40 receipt6253421648](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/62#issuecomment-6253421648)
are incoming decisions, not approval of the reverse direction.

Each row supplies the current #40 input to assess against the linked consumer
record. These links identify the receiving source; they do not claim that this
author completed every consumer's source audit. A current receiving decision
must identify its actual producer and consumer revision, accept/narrow/reject
the concrete input and retain any required change. The project's delegated
technical reviewers may make those decisions under the user's authorization,
with their real attribution; an absent co-assignee's personal response is never
invented. No row below is marked accepted before that review.

| Packet / direction | Concrete #40 research input | Receiving question and retained boundary |
| --- | --- | --- |
| H40-42 / #40 → [#42 saved/shared builds](saved-shared-builds.md) | Five answer states and preset attribution; exact selection/item/version and original-byte pins; rule/report identity; separate historical replay and current evaluation; explicit successor migration and projection profiles. | Receive the documented immutable-history, unknown/withheld and exact-association semantics. Identify any remaining SB-1–SB-8/SB-10 type or policy decision needed by the research build record. The configuration-only #383 candidate is not the complete historical/current share view; retention/share access and organisation-attestation non-transfer remain #42 decisions. Its substantive #40 prerequisite stays until the actual contract decision is reviewed. |
| H40-39 / #40 → [#39 cost estimate](../T6-deployment-operations/cost-estimate.md) | Exact item/version/operation, separately qualified stage quantity/unit, currency/time/rate conditions, explicit assumptions, Pricebook/revision association, fixed severity and reasoned unresolved coverage. | Receive those identity/quantity/outcome interfaces without converting an absent quantity or price into zero. #39 decides meters, default preview versus explicit budget currency, regional eligibility, FX, rounding and aggregation; #41 separately qualifies source/date/use. Preserve unpriced lines, one-off versus operating scopes and dated historical quotes. |
| H40-5 / #40 → [#5 model provider](../T1-model-selection/model-provider.md) | Stable publisher/operator/offering and item/version identities; per-component operator/capacity mode; source/scope and structured support predicates; field/rule contribution format. | Confirm the shared base and research rule format can carry the provider's actual route/account/service distinctions. A provider ID, billing class, listed model or available API supplies no unrecorded account entitlement, mode or cross-route capability. Richer route/wire fields remain explicit proposals. |
| H40-6 / #40 → [#6 AI model](../T1-model-selection/ai-model.md) | Exact model/artifact/version and offering scope; support completeness and conflicting evidence; separate applicability and fixed severity; references for base, weights, tokenizer and licence conditions. | Receive the model-facing research representation and the accepted worked examples. Keep positive scoped evidence, explicit negatives and unmarked omissions distinct. Exact serving tuple, weight-access/licence and derivative obligations remain separately qualified, with CD-6's unresolved lineage representation explicit. |
| H40-7 / #40 → [#7 context window](../T1-model-selection/context-window.md) | Typed answer causes, complete-request input versus output reservation, shared/separate limits, exact route/tokenizer/settings binding and the CD-5/CD-11 candidate boundaries. | Receive those research inputs against the accepted #378 assembly/KV/cost record. Preserve native fallback, known counterexamples alongside unknowns, separate request/sequence/uncertainty meanings and complete-request recount. No generic token ratio or context pass establishes KV, quality or billing. |
| H40-10 / #40 → [#10 GPU/compute](../T2-infrastructure/gpu-compute.md) | Per-rank/per-pool memory family, eligible conservative bounds, original assumptions/source identity, component applicability, CD-2 placement and CD-5 stage inputs. | Receive the representation and unknown/failure rules with actual allocation/residency, units and reserve kept explicit. Accepting research mechanics adds no pooled capacity, universal headroom, calibrated estimate or new empirical requirement to completed #10 research. Review the canonical CD-2 candidate in its own source turn. |
| H40-11 / #40 → [#11 inference engine](../T2-infrastructure/inference-engine.md) | Joint support tuple, requested versus publisher completeness, explicitly negative/exhaustive evidence, exact selection and artifact references, reasoned missing operands and the two named support-rule experiments. | Receive the source-scoped membership/rule interfaces. Preserve engine/build/backend/kernel, model/tokenizer/template/quantization/adapter and request conditions; no Cartesian capability inference. The retained frozen evaluator and explicit experiments have different dispatch, and documentation does not certify a running tuple. |
| H40-14 / #40 → [#14 embedding model](../T3-knowledge-retrieval/embedding-model.md) | Typed scoped catalog and selection identities, conservative eligible limits, exact request/operation references, universal versus required-presence modes and shared proposal/result semantics. | Receive the common representation while the active embedding writer retains query/document profile and index-generation proposals. Equal vector width cannot supply model/profile/normalization compatibility or source permission. The actual EMB→#40 receipt stays distinct from this reverse review. |
| H40-15 / #40 → [#15 vector database](../T3-knowledge-retrieval/vector-database.md) | Exact selection/reference identity, scoped source facts, fixed outcome/severity/unknown policy, relationship/path proposal routing and the explicit CD-10 non-model-runtime boundary. | Receive the base/rule format for the actual selected collection/index/operation and required-versus-optional path. Backend capacity, query/document representation, metric/order, authorization and erasure claims need their own evidence. Preserve the active vector-note writer and any genuinely missing CD-6/CD-10 path field. |
| H40-33 / #40 → [#33 fine-tuned model](../T5-training-fine-tuning/fine-tuned-model.md) | Versioned artifact identity, base/adapter/merged distinction, source and inherited-condition references, all-enabled/required-presence outcomes and explicit lineage/migration proposals. | Receive the research representation with exact base/tokenizer/template and exported-artifact identity. A link, format, merge operation or model-family label grants no rights or serving/evaluation pass. #33/#11/#30/#32/#36 keep actual lineage, obligations, support and evaluation decisions; optional T5 remains optional. |

The CD-5 [#7](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/7#issuecomment-6249961699),
[#10](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10#issuecomment-6249962343)
and [#39](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/39#issuecomment-6249963035)
delivery comments are review inputs, not substituted consumer approvals. The
actual [#7 → #10 KV receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10#issuecomment-6253262636)
and [#7 → #39 cost receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/39#issuecomment-6253295884)
retain their own direction and revised source. Likewise, #383's projection
review, bounded native interchange acceptance and historical replay receipts
do not by themselves complete H40-42. The canonical market handoff ledger and
its active writer remain separate; this appendix does not create, rewrite or
count a market receipt.

### Literal #40 research acceptance map

All twelve criterion texts below are retained from the live issue. This is a
current evidence/remaining-action map for review, not an automatic checklist or
closure instruction.

| Original criterion | Current research evidence and remaining action |
| --- | --- |
| Schema document with field types and examples | Frozen base mapping, consolidated component dictionary, exact minimum-field table and versioned typed examples above. The selected research representation and finite unresolved field choices need the current packet's independent/receiving assessment; production implementation is outside this criterion. |
| Worked rule examples spanning T1/T2 (model ↔ engine format, model ↔ GPU memory, context ↔ KV cache) including `unknown` handling | Seven examples explicitly accepted from the T1/#40 scope in review5560506323, with the migration objection resolved in5560765303. Typed context and actual frozen support-rule experiments add separately attributed examples. Context versus KV evidence stays separate. |
| Documented approach to cycles and recomputation | The existing pure-rule and dependency-trigger method states how selection, link, catalog, evidence, policy and ruleset changes invalidate a view without modifying selections. A dependency cycle does not require an execution cycle. |
| Rule and catalog versioning approach | Exact ruleset/catalog identities, ruleset-level versioning, retained original readers/findings and additive/replacement migration plan with M1–M5. CD-7 successor dispatch and the wider release have their own concrete decisions; no latest fallback is introduced. |
| Contribution format that component issues can follow | Existing shared rule template and contribution section specify participants, fields, applicability/assertion/source, fixed severity, unknown policy, correction, dependencies, outcome examples and version impact. |
| Decision record merged at `research/T0-configuration/component-schema-compatibility.md` following the research method | The original reviewed record and subsequent contributions are delivered at this path. This current appendix still needs its ordinary independent review and protected delivery. Prior partial merges remain partial receipts. |
| Candidate set covers the relevant deployment modes (API / managed / self-hosted) or states why a mode does not apply | The retained alternatives and #81 component-mode classification cover provider/shared, provider/dedicated or reserved and customer-operated cases, with hybrid/unknown derivation and remote/local predicate applicability explicit. |
| Comparison fields defined with type, unit, and evidence requirement | The minimum-field table above covers all twelve original base/rule fields, including temporal and non-quantity meanings and absent frozen fields; companion dictionaries retain category-specific evidence requirements. |
| Rule format, severities, and `unknown` handling documented with examples | Existing fixed severity versus outcome, typed answer reasons, required versus optional scope, explicit completeness/conflicts and checked-only label mechanics. Current strict-role acceptance is reconciled without changing behavior. |
| Every factual or numeric claim cites a primary source with access date (and version / region / currency where relevant) | The prior claim-source audit and dated companion ledgers remain attributed; this appendix uses exact contract/project sources inspected on 2026-10-18 and adds no vendor measurement or new price. Actual test/measurement/source-read records keep their original revisions and limits. |
| Each handoff listed under Dependencies is confirmed by the consuming issue's owner (link the comment or PR review) | Existing incoming and narrowly scoped receipts are identified above. H40-42/39/5/6/7/10/11/14/15/33 require their actual current directional decisions before this criterion can be accepted. No request, same-author integration or reverse receipt substitutes for them. |
| Open questions recorded with a named follow-up owner | The finite CD table and owner map below identify each remaining field/policy/evidence/release decision. The independent assessment must retain any genuinely unresolved research choice rather than treating every future implementation task as an extra acceptance criterion. |

### Follow-up ownership and review boundary

Live issue readback on 2026-10-18 preserves **@tynamite / @zwright8 for #40**,
**@tynamite / @PUSHINGSQUARES for #41**, and **@tynamite / @appletechie for #42**.
The in-session coordinating engineer performs the delegated technical review
with that role stated explicitly; this does not rename an assignee or invent a
personal response.

- **#40, @tynamite / @zwright8:** select the remaining CD-1/CD-6/CD-10/CD-12
  research representations, reconcile the exact versioned candidates and the
  reciprocal #6/#10/#11 inputs, and assess this twelve-criterion record. The
  canonical CD-2 source owner and #383 projection owner keep their active work.
- **#41, @tynamite / @PUSHINGSQUARES:** source eligibility, date/scope/conflict
  qualification, community independence and jurisdiction/source-use policy;
  consult the actual affected component issue for the claim. #39 retains
  pricing-unit, currency/region, temporal eligibility and aggregation decisions.
- **#42, @tynamite / @appletechie, with #40:** saved/share record choices,
  non-transferable attestations, explicit fork/projection and migration,
  historical/current views and retention. A complete research disposition can
  leave implementation in its owning scope; an unresolved required record
  choice must be named before removing the substantive prerequisite.

Final review must identify the exact amended source and each actual receiving
decision, preserve historical outcomes and source rights, and follow the normal
current-source validation and issue-closure checks. No version release, native
activation, publisher permission, measured fit or future test result follows
from the status wording in this appendix.

## Selected research representations for CD-1, CD-6, CD-10 and CD-12 — 2026-10-18

**Decision for independent and receiving review:** select the four representations
below as the research design, rather than leave their types and relationships
undecided. This continuation uses current accepted
[a219392b64f82849b00f7da373b13661518354c4](https://github.com/Pick-Your-AI/pick-your-ai-research/tree/a219392b64f82849b00f7da373b13661518354c4);
the answer/credential candidates, workload/deployment dictionaries, model,
vector-service and frozen-contract inputs cited here are unchanged from the
preceding packet's accepted source. They were inspected on 2026-10-18. This is
a project representation choice, with synthetic examples, and adds no vendor
fact, legal conclusion, measurement or grant.

The local assessment checkpoint `93ada1ee012c6a55bc889f0c0311bf1d90acf116`
remains retained. For these four choices, this section supplies the specific
decision that its earlier remaining-action rows requested. Current independent
review and actual affected receiving decisions are still required. Research
acceptance records these selected semantics; a future contract/ruleset release
separately assigns and validates successor JSON locations and readers. Existing
v1 fields, readers, bytes and historical findings keep their exact meaning.
CD-2 placement remains with its canonical writer. The separately reviewed
[#383](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/383) is now delivered
at the accepted revision above: its configuration-only share/fork profile and
retained-report association diagnostics keep their actual source/review/test
receipts. The earlier packet's active-reservation wording describes its prior
checkpoint. Delivery does not adopt a full migration or shared historical/current
view, and this continuation does not change that code or claim a new execution.

### Alternatives and selected design

| Decision | Alternatives considered | Selected research representation and reason |
| --- | --- | --- |
| CD-1 | Nullable/sentinel domain values; a wrapper on every nested domain field; a separate pointer-indexed answer map | Use the explicit `cd1-0.2` indexed five-state and attribution design, with typed predicate/result handling. It preserves literal user data, partial disclosure and original causal paths without rewriting domain objects or inferring an assumption flag. |
| CD-6 | Infer relationships from catalog names/roles; duplicate bindings inside each deployment object; maintain one explicit directed selection-link graph | Keep one link graph, with explicit semantic role and operation scope in the successor representation. Use exact artifact, inventory and condition identities to qualify links. Graph identity, runtime composition, source support and authorization remain separate checks. |
| CD-10 | Apply model-engine requirements to every service; rely on a service kind/deployment label; bind requirements to the actual service runtime and operation | Use an exact service-runtime requirement profile. Required platform/feature checks and recommended features have separate fixed-severity rules. A provider-opaque runtime and a customer-supplied runtime have different applicable evidence, without guessing from a product name. |
| CD-12 | Copy answers into every licence condition; maintain one unscoped organisation cache; retain private typed facts with explicit condition bindings | Use a build-owned attestation registry, reusable only for the same subject, fact definition and temporal/use scope. Condition answers point to those facts and separately qualified grants. Reuse never implies automatic aggregation, consent or transfer to another organisation. |

The logical field names below specify a research schema, not additional members
accepted by frozen v1. In particular, the existing Build link object rejects
extra fields, and none of these tables changes that validator. A published
successor must carry an explicit profile/version and preserve unsupported-reader
and incomplete-migration states, rather than attempt best-effort v1 parsing.

### Shared identity and value types

| Type | Definition and admission rule |
| --- | --- |
| Selection reference | Exact build ID/revision and selection ID; resolve the selected catalog ID/version/kind under the retained snapshot identity. References have no physical unit. A matching display name, another version or the sole available item is not a substitute. |
| Artifact/source reference | Record namespace, repository or catalog identity, exact revision/version, record path or local evidence ID, and the retained digest when required by CD-7. A digest establishes byte agreement only; #41 still qualifies source scope, date, grade and use. |
| Operation key | Nonempty canonical identifier owned by the component's documented operation profile, such as a particular query or training/serving operation. An unsupported operation key remains an explicit profile gap; it does not activate a similarly named model rule. |
| Typed answer | The five CD-1 states over the field's declared type. Only `provided` carries a value; explicit attribution and the field schema remain required. False, zero, empty collections and nullable values retain their declared type and never become missing by truthiness. |
| Money | The existing common money research shape: a nonnegative base-10 decimal string and explicit currency, without binary-float conversion. Its existing decimal vocabulary allows up to twelve fractional digits. Unsupported precision or a value outside this chosen profile is rejected without rounding/clamping; a different revenue definition requiring another type needs an explicit field profile. No exchange rate or currency default is supplied. |
| Count | A nonnegative whole count, represented in this research design by a canonical base-10 integer string without a sign, fraction, exponent or redundant leading zero. This prevents loss before validation in an inexact-number parser. It is a proposed attestation encoding, not a rewrite of existing integer fields or a claim that every consumer already reads it. |
| Calendar window | Explicit start date, exclusive end date and the applicable calendar/time-zone definition; start must precede end. An as-of instant is a distinct tagged temporal scope. Observation time, a reporting month and a release-relative reference period are not interchangeable. |

The [common definitions](../../contracts/v1/schemas/common.schema.json),
[current CD-1 attribution candidate](../../tests/fixtures/t0-answer-attribution.schema.json)
and [exact artifact reader](../../tests/t0_revision_lock_prototype.py) are the
existing project inputs for these distinctions. The
[Android integer receiving observation](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40#issuecomment-6254042968)
is separately attributed evidence that a particular JavaScript parse path lost
numeric identity before validation; it is not a new execution by this appendix
or a claim about every production consumer.

### CD-1: select the indexed 0.2 answer and attributed result model

The research answer store is the current `x_t0_answer_states` index with
`proposal_version: "cd1-0.2"`, as defined by the
[attribution schema](../../tests/fixtures/t0-answer-attribution.schema.json) and
[reader](../../tests/t0_answer_attribution_prototype.py). Non-root JSON Pointers
address a logical answer tree. Each `provided` entry has its declared `value`
and an exact Boolean `assumption`; optional `source` is the existing bounded
`preset:<name>` vocabulary. The other entries are exactly `unknown`, `missing`,
`withheld` and `not_applicable`, with no value or provided attribution.
General source evidence belongs in its scoped evidence record; a preset source
string is not repurposed as a publisher URL, grade or authorization token.

The selection includes the current known-value schema admission, original-token
precision guard, overlap rejection and withheld-parent witness behavior. An
unrecorded parent with a withheld descendant retains that actual cause;
partially provided children are not assembled into an invented known object.
Use a provided object only when that whole object is available; otherwise index
its separately disclosed leaves. Exact/ancestor/descendant lookup and the
deterministic original-pointer witness retain the implemented candidate's
meaning. Every value predicate still receives a value validated against an
explicit admitted field schema. A free-text literal "unknown" remains text;
an in-band unknown marker in a finite known-value vocabulary is not admitted.

The selected result boundary is the typed predicate and attributed terminal
finding, not implicit Boolean truth testing. Negation happens before final
lowering. Compatibility with unresolved applicability stays unknown;
recommendation applicability uses the explicit known-answer gate. A declared
not-applicable answer does not alone prove every dependent rule inapplicable.
Fixed severity, reason/source path, any actually used attribution and the
selection's own activation/presence result remain distinct.

**Migration decision:** continue to read retained 0.1 records with their original
profile. A 0.1 `provided` value without an explicit assumption declaration
cannot silently acquire `assumption: false`; an arbitrary old source string
cannot be dropped or recast as a preset. Preserve the original record and mark
the new projection's missing attribution decision unresolved until explicitly
supplied. Omission in a legacy record supplies no invented withholding reason.
This defines the conversion decision, without performing a migration or
silently upgrading existing callers.

The delivered `cd7-projection-0.1` profile retains its existing answer reader and
public/omitted-field representation. Selecting the attributed 0.2 research model
does not reinterpret its old provided records, add flags to its hashes or claim
that a current CD-7/native reader already implements this future mapping.

### CD-6: select one qualified link graph and explicit condition answers

The [deployment relationship proposal](deployment-mode.md#per-component-mode-and-relationships-decision-proposal)
already chooses selection links as the relationship representation. Retain that
choice. A successor link has the existing ID/from/to/relation identity plus
a semantic role and an explicit operation scope where a role is operation
dependent. These are link roles, distinct from the existing selection-role
preflight. Do not store a second authoritative engine, host or base link in the
deployment object.

| Relationship use | Selected link/reference and cardinality | Required interpretation |
| --- | --- | --- |
| Host | `runs_on` from the service/model selection to its host, role `host`; one resolved host for the applicable deployment/operation | Several candidates without explicit scope disambiguation are `unknown/ambiguous_binding`. A required host known not selected fails the owning configuration predicate; an unresolved inventory is unknown. |
| Devices | `runs_on` links with role `device`, with all participating device selections retained | Add an explicit `selection_id` identity association to each proposed physical `hardware.devices[]` record, alongside its existing unique `device_id`. One instance maps to one device selection; distinct instances may select the same catalog SKU. A nominal count, SKU or shared pool ID cannot invent that map. Byte placement and shared-pool arithmetic remain CD-2. |
| Serving engine | `served_by` with role `serving_engine` for the exact operation; one resolved engine where that operation requires one | An unrelated engine selection or an unqualified second edge cannot satisfy the relation. Known wrong-kind/disabled required targets are configuration failures; unresolved exact versions retain their own unknown result. |
| Base lineage | `derived_from`, role `base_artifact`, retaining exact selected artifact identities and source lineage | An adapter's selected base must agree with the catalog's stated `base_model_ref` identity. Known disagreement fails the consistency predicate. ID agreement is necessary but insufficient when the source still lacks the actual base revision; no version is inferred. Multiple unresolved bases or a cyclic adapter path remain unresolved with their causes. |
| Speculative draft | `feeds` from the draft to the target, role `speculative_draft`, bound to the exact operation/engine configuration | Use this explicit direction and role; a general `feeds` edge is not a draft binding. The initial operation profile requires one target per draft binding. Exact draft-target/engine support still needs its own scoped source tuple. |
| Data access | Existing `reads_from`, `stored_in` or other appropriate declared relation with an explicit input/output role; qualified access metadata records read-only/read-write intent, provisioning/runtime lifecycle and mount/fetch/API method where relevant | Intent is not effective access. Each method has its own actual storage/connection/source conditions. Do not infer a mount from a URL or elevate an opaque reference into a read/write grant. An unsupported method remains a typed profile gap for #13/#15/#35. |
| Credential source | Retain the existing `cd6-0.1` explicit direct/integration/model_provider/none choice and exact `provided_by` target link | The [credential sidecar](../../tests/fixtures/t0-credential-bindings.schema.json) remains the chosen bounded credential-binding candidate; it is not replaced with role inference. Direct versus inherited reference conflicts, missing pins and unsupported metadata keep their existing results. No secret string enters general findings or a share projection. |

All IDs and primitive types are admitted before lookup. Duplicate identities,
malformed references and dangling explicit link endpoints are input errors;
competing semantically possible links retain all candidates and an ambiguity
result rather than being chosen by array order. Known empty required scope,
unanswered scope and an optional inapplicable relation retain separate results.
The general graph may have legitimate cycles: rules read an immutable selected
graph and recompute affected views without mutating the selection set. A
lineage traversal uses a visited set and returns an explicit unresolved cycle;
it cannot recurse indefinitely or substitute a newer base.

**Runtime composition decision:** an adapter participates with its exact base
and that base's serving tuple; both selected artifacts' applicable requirements
remain visible. A full or merged fine-tuned artifact has its own support facts,
format and serving tuple. Its provenance edge does not copy all base capabilities
or prove an adapter loader can serve the merged output. Model/base/tokenizer/
template/quantization/adapter conditions remain a joint source-qualified tuple,
not a Cartesian product of capability lists. The
[fine-tuned artifact comparison](../T5-training-fine-tuning/fine-tuned-model.md#comparison-fields)
and [framework permission/technical separation](../T5-training-fine-tuning/training-framework.md#permission-rules-model-license--requested-methods)
supply the owning research inputs.

**Condition storage decision:** keep `licence_answers` at the logical build root,
beside `workload` and its organisation answer registry, rather than editing catalog facts.
Each answer binds the subject selection to a source condition identity:
originating catalog/artifact ID and exact version, terms/evidence revision and
local `condition_id`. A bare condition ID is not globally unique. An
eligibility answer is a typed `met`/`not_met` value; an obligation answer is
typed `acknowledged`/`not_acknowledged`. CD-1 carries unresolved states outside
those vocabularies. Condition references and the CD-12 fact references are
separate from the answer itself.

Traverse qualified base lineage to retain potentially applicable inherited
conditions, including across provider-operated serving. The link supplies
provenance, not a legal conclusion that every condition applies to every act or
derived artifact. Use the exact selected terms, activity, licensee and derivative
assessment from #30/#33; keep unresolved applicability unknown. An eligibility
`grant_ref` is a private reference to separately assessed grant evidence,
allowed only on eligibility answers. Its presence is never a bypass: the
assessment must cover this subject, condition, activity and period. It does not
acknowledge unrelated obligations or demonstrate technical access. These choices
refine the earlier blanket shorthand in D-R2 with the current
[selected-terms boundaries](../T5-training-fine-tuning/training-framework.md#permission-rules-model-license--requested-methods);
they do not decide new legal facts.

### CD-10: select scoped requirements for the actual service runtime

A non-model service such as a vector database has a **service-runtime requirement
record**, bound to the selected service ID/version, runtime build/distribution,
operation and deployment. Its logical home is the service's source-qualified
requirement profile plus the selected deployment's actual observations. Keep
requirements and observed capacity separate; no catalog kind is itself a
runtime requirement.

| Requirement input | Selected type and evidence boundary |
| --- | --- |
| Subject and runtime | Exact selection/artifact references and operation key. Runtime version/build/options are stated when they affect the claim; a catalog family name cannot substitute for a selected distribution. |
| Execution responsibility | Reuse the existing per-component `runtime_operator`, `runtime_supplied_by` and capacity fields. Do not create a competing mode field. Who operates a host and who supplies a runtime remain different facts. |
| Platform tuple | Typed OS/platform, architecture/ABI and any required accelerator/backend identity, each under its declared field vocabulary and exact source scope. Exact versions/conditions remain attached. A free-text or unsupported version requirement is retained unresolved until its component's field/predicate mapping is explicit. |
| Required features | Scoped feature identifiers such as ISA features, with an explicit known requirement inventory. All required features must be satisfied. An absent requirements record is not an empty requirement set; an observed feature list cannot be treated as exhaustive without its own qualification. |
| Recommended features | A separate scoped feature set, evaluated by a distinct fixed-warning rule. Recommendations cannot be merged into the required-error predicate or change its severity on unknown. |
| Resource and operation requirements | Explicit references to the component's typed memory/storage/concurrency/transport/index-operation predicates. The relevant #10/#15/#39 records retain units, allocation and evidence; this field does not implement a new resource estimator or interpret arbitrary prose. |
| Source and observations | Qualified scoped evidence for each requirement and the actual matched host/runtime observation. Documentary support, published limits, estimates and measurements keep their own grades. Missing actual resource/support evidence remains unknown. |

The initial platform/support family uses the existing CD-3 scoped membership
and completeness semantics. The required-feature family checks all explicitly
required features against the eligible observed platform; recommended features
use their separate predicate. These research types use the existing typed
predicate families. A requirement outside those families is an
explicit component-schema contribution, retaining unknown evaluation until
mapped; it is not silently ignored or mislabeled not applicable.

**Applicability decision:** inspect the selected component and operation. For
a customer-supplied/self-operated runtime, its actual host/runtime prerequisites
are applicable. For a provider-operated, provider-supplied opaque service, a
customer-device ISA check is inapplicable; the actual service's offered operation,
account/region eligibility, connections and other known requirements remain
separate applicable predicates. When responsibility or the required boundary
cannot be established, applicability is unknown, not skipped. A model running
inside a larger service is checked as its actual selected model/engine component;
the non-model service does not acquire D-R7a/b merely from its kind.

A known absent required capability from complete applicable evidence fails its
fixed-error rule; a missing/incomplete observation is unknown. A known absent
recommended feature fails its separate warning rule. Positive documented support
can pass that scoped predicate while retaining unverified where appropriate;
none of those outcomes proves a running service, a retrieval-quality result or
capacity. The [vector service record](../T3-knowledge-retrieval/vector-database.md)
continues to own its selected index/operation, representation, metric/order,
authorization, deletion and resource evidence. This resolves how to represent
its runtime requirements without taking over that note's active completion work.

### CD-12: select private scoped attestations and explicit reuse

Use a private build-owned registry at the **logical**
`workload.organisation.attestations` location, with build-owned
`licence_answers` referencing it. These are proposed successor locations,
not fields accepted by frozen Build. The registry is an evidence/answer store,
not a global account-profile default.

| Attestation field | Selected type and meaning |
| --- | --- |
| `attestation_id` | Unique canonical identity within the retained build/revision. A later correction has a new revision and preserves the earlier answer. |
| `fact_kind` | Establishment jurisdiction, EU market placement, lawful-basis reference, revenue or monthly active users. Each kind selects exactly one value schema below. |
| `subject_ref` | Exact private organisation/licensee/account identity, as the applicable fact definition requires. Affiliated entities or an account are not silently identical to the whole organisation. |
| `definition_ref` | Exact claim/measurement or attestation definition, including the source condition where it defines entity coverage, revenue basis or user-count semantics. Two definitions with the same short label need an explicit equivalence decision before reuse. |
| `use_scope` | Explicit applicable model/system, dataset/version, processing purpose, product/service or entity set as required by that definition. An absent scope is unresolved, not universal. |
| `temporal_scope` | Tagged calendar window or as-of instant. Record the period the condition actually asks about, including a release-relative reference when relevant; do not replace it with the current month or the attestation's capture date. |
| `answer` | CD-1 typed answer over the chosen value schema, preserving explicit source/assumption declaration and every unresolved state. A hypothetical preset is not a completed organisation attestation. |
| `attested_at`, `attested_by_ref` | Explicit observation/statement time and private declarant reference. They preserve attribution, not independent verification or legal authority. Do not infer them from the viewer or repository operator. |
| `evidence_refs` | Private, scoped references to supporting records/assessments. An opaque ID or supplied URL is not automatically fetched, authenticated or treated as a grant. |
| Condition bindings | Explicit build-owned links from the exact source condition/subject selection to the chosen attestation ID/revision, with any independently qualified derivation recorded. No first-match or last-write-wins selection. |

| Fact kind | Provided value type | Meaning that must remain separate |
| --- | --- | --- |
| Establishment jurisdiction | Exact jurisdiction code under its declared scheme/version, using the #41/CD-9 reference convention | Establishment of the specified licensee; not data residency, the researcher's location or a legal applicability verdict. Multiple relevant establishments require explicit scoped records rather than an invented principal country. |
| EU market placement | Exact Boolean for the named system/model and act | A user attestation about that scope, not a universal status for every product or a complete provider-duty assessment. |
| Lawful-basis reference | Opaque private assessment/reference identity for the exact dataset/version, processing purpose and subject | Presence retains the cited assessment; it does not establish lawfulness or infer consent from a data category. #32 and the responsible dataset/source rights/privacy assessor retain the actual assessment and source conditions. |
| Revenue | Money value plus the exact entity set, definition and reporting period above | Preserve amount, currency and the selected gross/net/other definition. No zero default, FX, annualisation, affiliate sum or reuse of a differently scoped total. |
| Monthly active users | Exact Count plus the definition's product/entity coverage and monthly window | Preserve the counting/deduplication definition. Counts from products, accounts or months cannot be added or compared to another condition without an explicit justified derivation. |

**Reuse and aggregation decision:** a condition may reuse a recorded answer only
after the complete subject/definition/use/temporal binding matches its request.
An already assessed equivalent definition can be referenced explicitly; a
matching label, value or organisation ID is insufficient. Direct attestation
is the default source for this registry, not an automatically computed total.
No generic sum, maximum, currency conversion or time extrapolation is adopted.
If an owning condition requires aggregation, record a separate derived fact
with the exact input fact revisions, coverage, deduplication/overlap treatment,
units, period and rule identity. Until that derivation is qualified, the
dependent condition is unknown; the existing component facts remain available.

A provided answer with `assumption: false` preserves that declaration only.
It is not independently verified and cannot qualify its own grant or legal
applicability. An assumed scenario can be compared as a labeled scenario, but
cannot stand in for the required actual attestation. Eligibility and obligation
findings still use their fixed rule, source conditions and explicit answer/grant
qualification; numerical comparison alone does not authorize the activity.

**Privacy/migration decision:** retain the existing
[#42 non-transfer rule](saved-shared-builds.md#field-sensitivity-for-shared-links-and-exports).
Organisation attestations, private condition/grant references and their values
are never included in a share and are never copied on fork. A recipient's
withheld/unanswered input remains unresolved until supplied for the recipient's
own scope. Private retained history may preserve an old scoped answer where
permitted; that does not make it current, transferable or authorized for public
disclosure. Migration must not turn a legacy unscoped organisation value into
a scoped current attestation or invent its subject, period or declarant.

### Synthetic decision examples for the selected representations

These examples define expected research behavior. They are not executed fixtures,
source measurements, user attestations, permissions or receiving decisions.

| Case | Explicit illustrative input | Expected bounded result |
| --- | --- | --- |
| R40-01 | A memory need is explicitly unknown, then its typed predicate is negated | Still unknown with its original cause. A Boolean negation cannot turn the unresolved answer into pass. |
| R40-02 | A schema-permitted zero demand is provided with `assumption: true` and `source: "preset:demo"` | Preserve zero and the explicit editable assumption. It is not missing and gains no checked/verified badge from its source label. |
| R40-03 | A retained 0.1 provided answer has no assumption declaration and a non-preset source | Preserve the original profile/bytes; the 0.2 projection's attribution choice is unresolved. No false flag or source deletion is invented. |
| R40-04 | An adapter's exact declared base identity differs from the selected `derived_from` target | Known consistency failure; neither catalog name similarity nor a newer available base repairs it. |
| R40-05 | Two possible engine links share the same component/operation without a disambiguating role | Unknown ambiguous binding with both retained candidates; no array-order selection. |
| R40-06 | A merged fine-tune retains a base lineage link but lacks its own selected engine support evidence | Unknown support for that output tuple. Provenance does not copy the base's capability matrix. |
| R40-07 | A storage link declares read/write intent and an opaque credential reference | Retain the requested binding; actual access/grant qualification remains separate and may be unknown. |
| R40-08 | A user-supplied service build requires feature `demo_feature_a`; its complete matched observation explicitly lacks it | Fail the required-feature rule at its fixed error severity. This proves the known mismatch, not a measured service crash. |
| R40-09 | A provider-supplied opaque vector service is selected, with responsibility known | A customer-device ISA rule is skipped; the service's operation/account/connection checks still run under their own applicability and evidence. |
| R40-10 | An exact service requirement's feature is absent from an unmarked observed subset | Unknown, not a negative manufactured from incomplete coverage. |
| R40-11 | Two conditions request the same synthetic subject/definition/month/currency and explicitly bind the same revenue fact | Reuse that fact for the two scoped questions; each condition still has its own threshold/grant/obligation assessment. |
| R40-12 | A second condition requests affiliates or a different month from the available MAU record | Unknown until the requested scope is supplied or an explicit derivation is qualified; no sum or current-month substitution. |
| R40-13 | A condition references a grant without evidence that it covers this subject and activity | Unknown grant qualification; the reference's existence cannot make eligibility pass or acknowledge another obligation. |
| R40-14 | A private build with revenue and lawful-basis attestations is shared and forked | Neither attestation transfers. The recipient supplies its own applicable answers; retained private history is unchanged. |

### What this selection resolves and what receiving review must decide

This chooses the answer/attribution representation, one relationship authority
with concrete role/cardinality and lineage rules, the non-model runtime
requirement families, and the location/type/reuse rules for the five attestation
facts. New component-specific claim definitions and actual observations remain
in their owning research; they are not additional unresolved alternatives to
these base representations.

The existing directional packets now include these explicit choices:
H40-5/6/11/33 receive relationship and condition scope; H40-7/10 receive typed
answers and exact resource/runtime bindings; H40-14/15 receive service-operation
and data-access boundaries; H40-39 receives exact quantity/currency/period
references; H40-42 receives the selected answer/attestation and immutable-history
boundaries. #2/#3 retain the workload/deployment inputs, and actual #30/#31/#32/#35
receiving review must assess the scoped condition/attestation/access interfaces.
No receipt for those choices is claimed by listing them.

The final research disposition must record which of these choices the actual
reviewers accept or require changing. A concrete remaining required choice must
be named and resolved rather than hidden under a future implementation label.
Conversely, a new frozen schema, production reader, general interpreter, selected
vendor agreement, provider account, physical deployment or empirical test is
not manufactured as a prerequisite for this documentation-only representation
decision. Normal source review, current validation and the issue's literal
directional acceptance criteria still govern delivery and completion.

## Reviewed representation and receiving disposition — 2026-10-18

**Status: the four selected research representations have independent source
review and actual directional receiving decisions.** This continuation records
those decisions and the literal research criteria; ordinary current-main
composition, final source review, required validation and protected delivery
remain the delivery gates. It does not mark an issue complete by itself.

The reviewed producer is the [corrected source-only
packet](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/45b20960cbc4652fb3341c977a025821c96595f9/research/T0-configuration/component-schema-compatibility.md)
at `45b20960cbc4652fb3341c977a025821c96595f9`, tree
`8f61e2845e6f3a73e5afc8215efe2720bf95765b`, note blob
`375506eea95bd7fc30883c0e4f2a2f5496f77cfd`. That unsigned publication preserved
the original remote `9916c1705367279f5dffbfdf522176e7236be6c4` checkpoint;
the local `93ada1ee012c6a55bc889f0c0311bf1d90acf116`,
`97c4f23bab41f2823041521ce31482b177185b88` and corrected
`9e494d184ecbd955da5e94d560ff797fd7f267cc` checkpoints remain retained.
The complete corrected producer text precedes this appendix without a rewrite.
Earlier pending/remaining-action statements describe their dated checkpoints;
the dispositions here supply the later decisions.

The coordinating reviewer independently read the complete 189-line assessment,
326-line selection and exact one-line assessment-ownership correction, checked
the relevant frozen definitions/readers, and performed the ten downstream
consumer reviews below. The packet author separately read the six additional
consumer interfaces and their material owner instructions. Each linked receipt
is an actual delegated project engineering decision with an exact producer and
consumer identity, not a response attributed to an absent named assignee.
The source-only publication and these document reviews are not test executions,
vendor checks, legal grants or a released successor contract.

### Accepted choices and preserved conditions

| Selected research choice | Current disposition |
| --- | --- |
| CD-1 answer and attribution | Accept the explicit `cd1-0.2` pointer-indexed five-state representation, provided-value/assumption admission and bounded preset attribution. Existing `cd1-0.1` bytes and reader behavior retain their original profile; no projection invents an assumption flag, source or value. Typed unresolved causes survive until their applicable terminal policy. #2's recommendation applicability remains distinct from compatibility evaluation. |
| CD-6 relationships and condition answers | Accept one directed selection graph with the stated semantic role, operation scope, exact identities and cardinalities; retain the explicit credential-choice profile. Catalog/reference existence, graph integrity, technical support and actual authority remain separate. Adapters bind their exact base/serving tuple; full or merged outputs require their own facts. A condition answer or grant locator cannot determine legal applicability, acknowledge another obligation or override a technical false. |
| CD-10 non-model runtime requirements | Accept the actual selected non-model service/runtime build and operation profile, with source-qualified requirements and explicit runtime responsibility. Required and recommended families keep distinct fixed severities. A service kind or customer cloud account does not fabricate an engine, local ISA requirement, feature inventory or evidence of support. |
| CD-12 private scoped facts | Accept the build-owned registry and exact subject/definition/use/period reuse for jurisdiction, model/system market placement, lawful-basis assessment, revenue and MAU. Private attestations and grants do not transfer on sharing/forking. #32 and the responsible dataset/source rights/privacy assessor retain the assessment; #31 receives only its configuration/compute-quantity interface and consumes no CD-12 attestation. Other source-specific condition questions remain explicit rather than being inferred from these five fact kinds. |

The receivers requested no further alternative to these four selected base
representations. Their conditions are part of the acceptance, including
unknown evidence, exact selected terms and scopes, non-transferable private
facts, and the distinction between a research representation and an actual
permission, capability or deployment. The [lawful-basis owner
instruction](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/2#issuecomment-6245701804)
and [training-residency clarification](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/3#issuecomment-6252011942)
remain operative: personal training dataset/source scope governs that
assessment; training is outside serving-mode membership but destinations that
receive training data still participate in D-R6.

### Ten literal downstream handoffs

Every row below receives the corrected producer identified above. These ten
consumer reads are pinned to accepted
`c9ed2d15523c66b57202639ec03b5f9fe886f1ef`; their full blob identities and
scope remain in the linked receipts. Later receiving composition must retain
subsequent accepted source, rather than relabel these reads as a newer audit.

| Direction / exact consumer blob | Actual receiving decision and retained boundary |
| --- | --- |
| H40-42 / #40 → #42; `98af34c75cf0fabeaea13e8d2fd28c7e174b9f20` | [Accepted — 6254602552](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/42#issuecomment-6254602552). Five-state attribution, exact pins and report association, immutable history, explicit projection profiles and private-fact non-transfer are received. The configuration-only #383 reader is not a complete implementation of the shared/historical view. #42 retains retention, share access, export/replay implementation and its other criteria; its live #40 delivery prerequisite is not removed by this receipt alone. |
| H40-39 / #40 → #39; `6405fd07b1465178c82bcfeab18d13990ad2836e` | [Accepted — 6254603370](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/39#issuecomment-6254603370). Exact operation, separately qualified quantity/unit, Decimal money/currency, period and immutable pricebook/revision association. Missing lines stay unpriced; the USD preview does not supply a user's budget answer. Meters, eligible rates, rounding, allocation, aggregation and FX remain #39 policy. |
| H40-5 / #40 → #5; `719b072daf2d213024bde7fd6816e5387389c131` | [Accepted — 6254604068](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/5#issuecomment-6254604068). Exact publisher/distributor/operator/offering and route/account identities, one graph authority and the scoped credential choice. Provider/API/billing labels supply no missing entitlement, runtime responsibility or cross-route capability. |
| H40-6 / #40 → #6; `652bee45b1d72e2c883cbcb3457e47baecfcde29` | [Accepted — 6254604724](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/6#issuecomment-6254604724). Exact artifact/route and joint support tuple; positive, explicit negative and unmarked omission remain distinct. CD-6 resolves the earlier lineage alternative while keeping technical capability, selected terms and source-qualified condition answers independent. Non-token families retain their own task/shape semantics. |
| H40-7 / #40 → #7; `5384081104cc2d872a4173138fc00a00c115c072` | [Accepted — 6254605318](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/7#issuecomment-6254605318). Complete serialized input, exact route/tokenizer/settings and once-counted output/thinking reservation; selected cap, native limit, mean/max and uncertainty remain distinct. Recount after a transform or new tool/retrieval round; context fit supplies no KV, quality, billing or execution result. |
| H40-10 / #40 → #10; `32f2e8a48f69c51e3517a15e28dbc162eda6b725` | [Accepted — 6254605905](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10#issuecomment-6254605905). Exact hardware instance/selection, qualified conservative bounds, typed causes and stage bindings. CD-2's canonical owner retains byte placement and pool arithmetic. No device count, nominal SKU or accepted type invents pooled capacity, a universal reserve, calibration or a new empirical prerequisite for completed #10 research. |
| H40-11 / #40 → #11; `7c3e45b4b4a1d68676cf9fa31fc529432c1aacf4` | [Accepted — 6254606510](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/11#issuecomment-6254606510). Exact engine/build/backend/kernel/artifact/request tuple and operation-scoped engine link. Publisher inventory and requested completeness stay independent; ANY/ALL preserve eligible witnesses, violations and unresolved members. Required presence differs from all-enabled findings; experiments and frozen dispatch retain their own versions. |
| H40-14 / #40 → #14; `2e7831ced848c5c12d1520c35b86c5bce5d2fcdb` | [Accepted — 6254607131](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/14#issuecomment-6254607131). Exact query/document role, operation, index field/namespace and population generation. Width equality, backend/type capacity, compatible encoder profiles, normalization/operator/score scale and content policy remain separate; the earlier reverse EMB receipt keeps its direction. |
| H40-15 / #40 → #15; `e9850147fcf58fe14d8e753c7b577108a2760196` | [Accepted — 6254607941](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/15#issuecomment-6254607941). Exact collection/index/named field/namespace/operation, real service-runtime profile and qualified requirements. Capacity, encoder/generation compatibility, score interpretation, actual principal/resource/action authority and scoped serving/deletion lifecycle remain distinct. No kind, filter, credential or transport creates permission or a universal limit/TTL. |
| H40-33 / #40 → #33; `dc5cb3c7718aad4c49b2263ddd649bf7be575ec9` | [Accepted — 6254608662](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/33#issuecomment-6254608662). Exact base/adapter/export and serving tuple. The existing modality-inheritance case keeps full base commit, no added tokens and no embedding change through `modules_to_save`; JSON-schema support is rechecked on the actual route. Lineage, selected legal conditions and technical/evaluation facts remain separate; optional T5 stays optional. |

### Six additional condition, workload and deployment interfaces

These consumer reads receive the same corrected producer and are pinned to
accepted `cceaa676ab34e02941d8dc7aa552c9a70a7251ba`. All six blobs were
independently compared with the inspection at
`c9ed2d15523c66b57202639ec03b5f9fe886f1ef` and are byte-for-byte unchanged.
Their complete issue/comment inventories were refreshed; the public receipts
retain the actual source-read limits and earlier owner attributions.

| Direction / exact consumer blob | Actual receiving decision and retained boundary |
| --- | --- |
| #40 → #30; `c3cfc458fcd9272fc0b4f969ccef131f7eae7e07` | [Accepted with scoped conditions — 6254653703](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/30#issuecomment-6254653703). CD-1/CD-6/CD-12 supply the H6 representation for actual enabled training participants, selected terms and condition facts. Teacher/student remain separate, F-23 requires the complete technical tuple and F-20 keeps its corrected historical Bedrock scope. Five attestation kinds do not answer every licence question. The current closed research disposition of #30 is preserved. |
| #40 → #31; `e20e49ce3e078847e37ceeffb2eb2cdf7f2885cf` | [Accepted with narrowed scope — 6254657215](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/31#issuecomment-6254657215). CD-1 and relevant CD-6 configuration/quantity bindings only; current K-rules consume no CD-12 attestation. Exact trainer/device/allocation, per-device memory and non-overlapping phases stay explicit. No missing managed profile, fit, duration, calibration, meter or price is fabricated. The active compute/cost writer retains its work. |
| #40 → #32; `af0fc0772759410c6d63baf1b96e0dc1ff316674` | [Accepted with scoped conditions — 6254657922](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/32#issuecomment-6254657922). Exact dataset/source version, purpose, subject, operation and actual assessment; personal training data governs lawful-basis applicability and EU placement names model versus system. Frozen flags and JSONL are insufficient evidence by themselves. Preserve current E-R44 error policy and the actual H3/evaluation receipts; the component reconciliation writer remains separate. |
| #40 → #35; `62eac8a99b407e3063a4ed0c10196ac442988bd0` | [Accepted with scoped conditions — 6254658636](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/35#issuecomment-6254658636). Answers, resource/operation/credential intent, real runtime requirements and applicable private licence facts are inputs. W-R4 selection remains a weak recommendation; G-series control evidence, violation-style predicates, exact tool approval, deletion layers and key-state bindings remain their own checks. No blanket rule adoption or security certification follows. |
| #40 → #2; `b9691e48704a5ffa35db7741ad1d26a93f6a3187` | [Accepted with scoped conditions — 6254659633](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/2#issuecomment-6254659633). Build-owned answers, attributed editable assumptions, exact device/stage/condition scope and private fact reuse. Recommendation applicability remains separate from unresolved compatibility. The later W-R11 owner conditions retain the light declaration recommendation, separate stronger recovery boundary, eligible checked-only evidence and the designated home for the verbose recovery candidate; this receipt does not claim those follow-up edits occurred. |
| #40 → #3; `7d88a23348768dfaab9630f6194bc3971bbfcbae` | [Accepted with scoped conditions — 6254660533](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/3#issuecomment-6254660533). Qualified deployment graph, licence-answer distinctions, actual runtime responsibility and private fact scope. Training destinations remain in D-R6 without changing serving-mode membership. A missing condition inventory or unqualified grant stays unknown; only qualified complete absence can justify no applicable conditions. Lineage is not a legal derivative assessment. |

### Incoming evidence and directions retained

The [actual #41 → #40 receipt
6254387986](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40#issuecomment-6254387986)
receives the source-policy packet at
`13b11b7eb9a84af200ea9f0577fcb0e5182a4c46`, blob
`c7d36a3c6c5ff305080867ec98763019d5e365bb`, against the then-current
#40 record at `e9159891422bb33046433ef1229c498861b218e7`. It accepts the
four claim-level research grades and DS-R1–DS-R5 as shared-template proposals:
source eligibility, requested completeness, ANY/ALL contributors, known
source-use mismatch, unresolved binding and checked-only evidence keep their
different meanings. This does not add a frozen provenance enum, default TTL,
rights grant or historical rewrite. The finite source/material/use decisions
from #60 remain binding.

The [#15 → #40 R4 receipt
6254104576](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40#issuecomment-6254104576)
receives `vector-database-decision/0.2.0` at source
`4438baf70cc3fce1ee63d09ef8a24308d6dd6613`, exact note blob
`e9850147fcf58fe14d8e753c7b577108a2760196`. Its VDB-01–VDB-04 shared
rule format, field/outcome and source-completeness acceptance is distinct from
the H40-15 reverse receipt. VC-01–VC-14 remain synthetic reasoning fixtures.

The earlier #75 #2/#3 and T2 disposition, #126 T1/#40 worked examples, and
the incoming #14 and #62 receipts cited above retain their real directions and
review scope. The [Android exact-number receiving observation
6254042968](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40#issuecomment-6254042968)
retains its own reference pin and native/interface follow-up; it is neither a
fresh execution here nor acceptance of a changed frozen numeric meaning.
No outgoing packet, reverse receipt or linked implementation is counted as an
unrecorded market handoff.

### CD-2 remains an explicit research decision

The sixteen receipts above do **not** adopt the normalized physical-pool and
co-residency representation. At inspected accepted main
`cceaa676ab34e02941d8dc7aa552c9a70a7251ba`, the deployment dictionary still
leaves byte allocation to CD-2, and W-R6 explicitly counts `on_demand`
components as resident until CD-2 defines co-residency scenarios. The complete
57-line [memory screen](../T2-infrastructure/compute/memory_screen.py), blob
`dc332df651f6e0ae3a2abda210b526ff7585258d`, compares already supplied bounds
for one matching domain; it explicitly leaves adapters, runtime/workspace,
co-residency and demand-versus-pool accounting upstream. That bounded screen
does not choose the missing allocation representation.

The [original CD-2 claim6246869445](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40#issuecomment-6246869445)
and [resumed canonical claim6251561799](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40#issuecomment-6251561799)
own that specific research choice: a versioned synthetic encoding binding
resident byte allocations to unique physical pools and declared device/rank
consumers, explicit co-residency and completeness, once-only shared-pool/reserve
accounting, separate pool failures and unresolved evidence. The resumed claim
describes four prepared fixture/prototype/test files plus its explanatory
section, with current validation and independent receiving still required
before publication; it supplies no affected-owner adoption.

The unresolved item is the exact normalized representation and its actual
research disposition, **not merely a missing production implementation**.
H40-10 receives the common types and exact associations while explicitly
preserving this allocation question. The canonical CD-2 author, #40 and #10
must review that concrete candidate and record acceptance or a required
correction. No competing implementation is introduced here, and no current
hardware measurement is required to review a synthetic research encoding.
Whole-issue completion remains unassessed while this substantive question and
the final delivery gates are open.

### Literal twelve-criterion disposition after receiving review

The criterion text is unchanged from the original issue. The table records
what this research revision supplies and what must be demonstrated by its
ordinary delivery receipt; it does not convert document text into a merge,
validation result or response from another person.

| Original criterion | Reviewed research evidence and delivery obligation |
| --- | --- |
| Schema document with field types and examples | The original frozen-base mapping, component dictionary and exact twelve-field type/unit/evidence table are retained. The four concrete selected representations, fourteen explicitly synthetic cases, independent source assessment and sixteen actual receiving decisions supply their choice/receiving record. No additional alternative to these four choices was requested; CD-2's separate normalized allocation/co-residency representation still requires its actual research disposition above. |
| Worked rule examples spanning T1/T2 (model ↔ engine format, model ↔ GPU memory, context ↔ KV cache) including `unknown` handling | The seven examples retain actual #126 reviews5560506323/5560765303; current typed support/context and resource boundaries are received by H40-6/7/10/11. Original code/test observations remain pinned to their executions; neither a new measurement nor a production engine is invented. |
| Documented approach to cycles and recomputation | The retained pure-rule, dependency and invalidation method covers changes to selections, links, catalog/evidence, policy and ruleset without mutating selections. The selected graph preserves cycle/ambiguity causes and exact references; it does not turn a dependency cycle into recursive mutation or a latest-value lookup. |
| Rule and catalog versioning approach | Exact catalog/ruleset/record identities, retained original readers/findings and M1–M5 additive/replacement migration remain the research approach. Explicit CD-1 and CD-7 profile boundaries and H40-42's immutable-history acceptance preserve old bytes and outcomes; the full successor release and implementation remain separately versioned work. |
| Contribution format that component issues can follow | The existing shared template covers participants/fields, applicability, assertion, evidence, fixed severity, unknown policy, explanation/remediation, dependencies, outcomes and version impact. Actual H41-40, VDB R4 and the downstream receipts demonstrate its research intake without adopting an arbitrary runtime expression language. |
| Decision record merged at `research/T0-configuration/component-schema-compatibility.md` following the research method | Earlier record revisions are delivered at this path. This continuation has the explicit choices and receiving record ready for final current-source review and protected delivery. Fulfilment for the new revision requires its actual accepted merge and post-main validation receipt; a source-only branch does not satisfy that delivery evidence. |
| Candidate set covers the relevant deployment modes (API / managed / self-hosted) or states why a mode does not apply | Retained alternatives and per-component runtime/operator/capacity classification cover provider/shared, provider/dedicated or reserved, customer-operated, hybrid and unknown cases. H40-5/10/11/15 and #2/#3 preserve actual runtime responsibility and predicate applicability; training's out-of-mode status does not exempt its data locations. |
| Comparison fields defined with type, unit, and evidence requirement | All twelve minimum base/rule fields remain explicitly mapped, including conceptual temporal/rule-version fields absent from frozen v1. The selected typed answers, graph scope, runtime profiles and exact private Money/Count/period definitions add the reviewed choices; category-specific factual qualifications remain with the actual component/source. |
| Rule format, severities, and `unknown` handling documented with examples | Fixed severity versus outcome, typed unresolved causes, required presence versus all-enabled, requested versus source completeness, ANY/ALL evidence, disputes and checked-only labels remain separate. The fourteen synthetic cases and receiving conditions preserve both known failures and unresolved rows; strict role policy and original profile meanings are unchanged. |
| Every factual or numeric claim cites a primary source with access date (and version / region / currency where relevant) | The retained claim-source audits and companion ledgers keep their original attributions. This appendix uses exact project sources and receiving comments read on 2026-10-18; it adds no vendor price, measurement, legal conclusion or newly executed result. All older source, test and fixture evidence retains its own version and limitations. |
| Each handoff listed under Dependencies is confirmed by the consuming issue's owner (link the comment or PR review) | All ten literal downstream directions now have linked actual delegated receiving decisions against the corrected producer; the six additional affected interfaces and original incoming/reciprocal receipts retain separate directions. The narrower #31 decision is recorded explicitly. No request, same-author producer review or absent named person's response is substituted for a receiver decision. |
| Open questions recorded with a named follow-up owner | The original CD register and the concrete ownership boundaries below remain visible. The four selected representations now have actual source/receiving disposition. CD-2 remains a genuine normalized-representation question with its canonical author and #40/#10 review; remaining source qualification, component predicates, wire/readers/migration and delivery retain their own owners. Whole-issue completion is not inferred from the sixteen receipts. |

### Remaining work with its actual owner and scope

- **#40 with #10 and the canonical CD-2 writer:** review and dispose of the exact
  normalized allocation/co-residency representation described above. Retain the
  per-rank/per-pool and device/selection boundaries. H40-10 accepts the shared
  base representation; it does not resolve that research question, take over
  its source, create calibrated resource evidence or waive its required review.
- **#40 with #41/#39 and the affected component issue:** qualify real source
  facts, date/scope/completeness/rank and selected source-use conditions; retain
  the versioned CD-3/CD-4/CD-5/CD-9/CD-11 candidate and result boundaries. A
  carrier, source pointer or successful shape check supplies no actual source
  qualification, geography, measured resource or price.
- **#40 with #42 and native consumers:** assign and validate any successor
  field/ruleset/reader release, retained-history dispatch and migration. Preserve
  the accepted #383 configuration-only projection and report-association
  continuation in the receiving tree. Its bounded delivery is distinct from a
  full shared/historical implementation, and #42 retains access/retention and
  its own remaining research/delivery criteria.
- **#2/#28/#40:** retain the later W-R11 recommendation/recovery and document-home
  conditions at [6252162416](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/2#issuecomment-6252162416).
  This base representation receipt does not assert the existing follow-up
  implementation or relocation has happened.
- **#30/#32 and the responsible dataset/source rights/privacy assessor, with
  #33/#35 as applicable:** retain exact selected terms, assessed activity and
  source conditions, actual data/evaluation/control evidence and non-transferable
  private facts. #31 retains configuration and compute quantities; it acquires
  no attestation or legal-assessment duty from the older broad owner row.
- **The current coordinating reviewer and canonical #40/#41 note writers:**
  compose both reviewed documentation slices with current accepted main,
  preserve every unrelated path and historical checkpoint, obtain the normal
  current-head review and required gates, and record actual merge/post-main
  evidence before changing issue completion or removing a substantive delivery
  prerequisite. The named issue assignees and active component/market writers
  retain their existing roles.

These are explicit boundaries of the reviewed research decisions and their
remaining delivery or follow-up work. They do not create a new production,
account, paid-job or empirical requirement for a documentation criterion, and
they do not waive any actual unresolved required research choice, source review
or current delivery gate.

## CD-2 explicit physical-pool accounting decision — 2026-10-18

**Status:** engineering selection prepared for independent source and affected
consumer review. This is a prospective research representation, named
`cd2-physical-pools/0.1.0`; no existing schema, reader, Ruleset or runtime accepts
that tag merely because it appears here. Its eventual receiving and delivery
record must be appended separately. The earlier CD-2 unresolved-status section
remains an accurate record of what the #403 packet had not yet decided.

### Scope, source and preserved contributor work

This decision makes the normalized accounting choice concrete. It does not
adopt the four unpublished fixture/prototype/test files described in
[claim6251561799](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40#issuecomment-6251561799).
That claim, [its original reservation6246869445](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40#issuecomment-6246869445),
and the [immutable-checkpoint request6254818212](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40#issuecomment-6254818212)
retain their author and scope. No timed expiry rule was found in the current
contributor/workflow instructions; none is invented here. The separate
[one-note coordination6256307406](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40#issuecomment-6256307406)
reserves this additive documentary decision and its review, without a main hold
or ownership of those four files. A later supplied checkpoint must be compared
with the actual decision and reviewed on its own merits.

The following project inputs were inspected on 2026-10-18 at accepted main
`0659dac2a439893b7765048c1ef7c8442ba6cb25`. The canonical note before this
continuation is blob `8ee5a7b7a960ae63c073c996cfdc73b80d939e7c`. These are
source/contract observations, not a fresh vendor, hardware or execution audit.

| Input | Exact source and relevant boundary |
| --- | --- |
| Workload W-R6 and CD-5 | [workload-use-case.md](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/0659dac2a439893b7765048c1ef7c8442ba6cb25/research/T0-configuration/workload-use-case.md), blob `7b39b1ce03697d7bca4f87c75984f8851a6fddf2`: one physical pool, once-only reserve, eligible evidence, all-resident fallback, and exact request/sequence/admission/stage scope. |
| Deployment placement | [deployment-mode.md](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/0659dac2a439893b7765048c1ef7c8442ba6cb25/research/T0-configuration/deployment-mode.md), blob `8d64fcc0bf16222b0ed3e06dc53c396e525c0741`: relationships remain `build.links`; typed whole/layer/expert/tensor shares do not supply byte allocations. |
| #10 screen and rules | [memory_screen.py](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/0659dac2a439893b7765048c1ef7c8442ba6cb25/research/T2-infrastructure/compute/memory_screen.py), blob `dc332df651f6e0ae3a2abda210b526ff7585258d`, and [compute-capacity.md](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/0659dac2a439893b7765048c1ef7c8442ba6cb25/research/T2-infrastructure/rules/compute-capacity.md), blob `e9813b80dfd638fdb8f3b8a1e96a57420a069d15`: already qualified same-domain bounds, explicit headroom, separate per-rank limits and conditional capacity outcomes. |
| #10 receiving interface | [gpu-compute.md](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/0659dac2a439893b7765048c1ef7c8442ba6cb25/research/T2-infrastructure/gpu-compute.md), blob `32f2e8a48f69c51e3517a15e28dbc162eda6b725`, and [H40-10 receipt6254605905](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10#issuecomment-6254605905): distinct actual devices, demand/pool responsibility, uncertainty and no automatic pooling or calibrated ResourceEstimate. |
| #11 engine interface | [inference-engine.md](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/0659dac2a439893b7765048c1ef7c8442ba6cb25/research/T2-infrastructure/inference-engine.md), blob `7c3e45b4b4a1d68676cf9fa31fc529432c1aacf4`: exact build/backend/parallelism, offload, adapter/KV placement and admission; a capacity screen supplies no engine-support verdict. |
| #7 context interface | [context-window.md](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/0659dac2a439893b7765048c1ef7c8442ba6cb25/research/T1-model-selection/context-window.md), blob `5384081104cc2d872a4173138fc00a00c115c072`, and [context-fit.md](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/0659dac2a439893b7765048c1ef7c8442ba6cb25/research/T1-model-selection/rules/context-fit.md), blob `ab4fb08f1a64c607a918c2aef02d60e93e322a91`: context/route limits and native fallback remain separate from KV geometry, allocation and capacity. |
| Contract boundary | [T2 contract proposals](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/0659dac2a439893b7765048c1ef7c8442ba6cb25/research/T2-infrastructure/contract-proposals.md), blob `1a03a710f2febe7575eacf2e67a6e1172ae57a1d`, and [frozen ResourceEstimate](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/0659dac2a439893b7765048c1ef7c8442ba6cb25/contracts/v1/schemas/resource-estimate.schema.json), blob `9dbafa69f59f8667a4e124ec34d8df17606c8f2e`: scalar v1 metrics do not encode this pool/scenario ledger; bounds are scenario assumptions, not statistical confidence intervals. |

### Alternatives and selected representation

| Alternative | Disposition and reason |
| --- | --- |
| Retain only device capacities and typed deployment shares | Preserve these existing inputs. They identify requested placement but leave storage, co-residency and reserve domains unresolved. They cannot supply the normalized CD-2 answer by themselves. |
| Divide a global estimate by device count, sum advertised VRAM, or infer bytes from a layer/expert/tensor share | Do not select. These operations manufacture an allocation, usable capacity or topology that the input does not establish. Equal SKUs, device counts and model artifact identities are insufficient. |
| Use one global peak scalar for a build | Do not select as the normalized representation. It cannot retain a failed individual pool, a per-rank ceiling, a host offload charge or unified-memory aliasing. A source scalar may remain evidence within its exact original domain. |
| Explicit physical pools, unique storage charges, qualified consumers and explicit residency coverage | **Selected for this research decision.** Keep physical storage ownership separate from logical consumers, compare every applicable capacity domain, and require source-qualified completeness before a pass. The representation records a supplied plan; it does not search for or execute one. |

The selected profile has two explicit coverage modes: `conservative_all_resident`
and `qualified_scenarios`. A caller must select the new profile and its mode;
there is no inferred profile or mode. Inputs without the profile retain W-R6's
existing conservative treatment of both `always` and `on_demand` components as
resident. No existing result, native reader or saved artifact is reinterpreted.

### Typed logical fields

These are the proposed logical field names and constraints. They are sufficient
to specify the research encoding; an executable schema, parser and adapter are
separate versioned deliverables. `ID` means nonempty text within an explicitly
named identity scope, not a catalog name substituted for an actual instance.
`ByteCount` is logically an exact nonnegative integer number of bytes. Its
**selected serialization is a canonical unsigned base-10 integer string**: the
ASCII string `0`, or an ASCII digit `1`–`9` followed by zero or more ASCII
digits. Parse and calculate with arbitrary-precision integers, never through
binary floating point. Signs, fractions, exponent notation, redundant leading
zeros, whitespace, non-ASCII digits, Boolean values and JSON-number substitutes
are rejected in these new ByteCount fields. This reuses the selected Count
vocabulary above without changing any frozen numeric field or old helper input.
Source quantities keep their original value, unit, method and rounding record.
Lower bounds round down and upper bounds round up when conversion needs rounding;
the resulting exact byte count uses the selected string encoding.

An `Answer<T>` uses the selected CD-1 terminal states and attribution: `provided`
contains a T; `missing`, `unknown`, `withheld` and `not_applicable` retain their
distinct causes. No unresolved answer is a zero, an empty set or a supplied
value. A required applicable capacity cannot be skipped merely because its
answer is `not_applicable`. Source eligibility, completeness, conflict rank and
checked-only labels remain the separate CD-3/#41 decisions.

| Field / record | Type and required meaning |
| --- | --- |
| `profile` | Exact tag `cd2-physical-pools/0.1.0`; interpretation is version-bound. |
| `basis` | Exact Build ID and positive integer revision plus an immutable reference to the retained complete Build content. Include exact input references for hardware inventory, selections/settings/links, deployment, workload/stages, engine builds and the source/qualification policy used. An ID/revision pair without its actual retained content does not establish a matching basis. |
| `component_scope[]` | Actual selected component/operation and `Answer<applicable \| inapplicable>` for the local capacity predicate, with the exact responsibility, placement and source basis. Known opaque provider internals do not require invented customer devices. Unresolved required placement or responsibility remains unknown, not an empty applicable set. |
| `devices[]` | Unique primary `device_id`; `selection_id: Answer<ID>` for its exact CD-6 selection; and `local_pool_id: Answer<ID>`, with scoped inventory evidence. Several actual devices may share one physical pool; several instances may select the same catalog SKU. Neither association is inferred from SKU, position or count. |
| `pools[]` | Unique primary `pool_id`, exact physical address-space / partition / tenancy scope, local `device_ids: Answer<set<ID>>`, an `Answer<capacity>` and `Answer<ByteCount>` reserve. The capacity contains `basis: before_reserve \| after_reserve` and `lower_bytes: ByteCount`, with retained source and qualification references. Provided device/pool memberships must agree in both directions. Pool disjointness or aliasing must be established, not asserted by two different string IDs. |
| `consumers[]` | Unique primary `consumer_id`; exact component/operation and device references as typed answers. `runtime_binding` is an answer over two explicit alternatives: `model_engine` references the actual inference-engine selection/build and operation; `service_runtime` references the selected CD-10 non-model service-runtime record, distribution/build and operation. Retain applicable runtime-instance, replica, rank, admission-domain and stage identities. Non-model services acquire no fictitious inference-engine selection. A genuinely non-applicable role differs from a required unresolved one; service-wide demand cannot silently become per-replica demand. |
| `allocations[]` | Unique primary `allocation_id` for one non-overlapping physical storage charge; `pool_id: Answer<ID>` and `consumer_ids: Answer<nonempty set<ID>>`. A qualified charge has exactly one owning pool and resolved consumers. Retain the memory term/extent, physical identity, method and evidence references. Terms may include weights, adapters, KV, workspace/runtime and transfer/load transients. Their completeness and lifetime are runtime/scenario-specific, not inferred from these labels or from the component placement label. |
| `coverage_mode` | `conservative_all_resident` or `qualified_scenarios`, explicitly selected and retained as an assumption. The second mode requires an independently qualified exhaustive residency/transition envelope for the requested scope. |
| `scenarios[]` | Unique `scenario_id` and exact workload/runtime/stage envelope. Each scenario retains the required placed-component inventory and a complete set of allocation-residency rows for its scoped charges; missing rows remain unresolved. The conservative mode has one explicit upper envelope; the qualified mode may have several evidenced envelopes. |
| Scenario allocation row | Exactly one `(scenario_id, allocation_id)` pair; `residency: Answer<resident \| excluded>`; and, when resident, `live_upper_bytes: Answer<ByteCount>` with optional supplied lower bound not exceeding that upper bound. Preserve source/assumption/eligibility references per row. A supplied exclusion needs its own scoped lifetime/transition evidence; it is not a supplied zero allocation or permission to omit an always-placed component. |
| `rank_limits[]` | Every applicable independent rank/engine-allocation ceiling, with unique `limit_id`, exact consumer/domain and already qualified demand-upper/capacity-lower/reserve-basis inputs. Whole-buffer membership can be derived from named charges only if that ceiling's accounting definition supports it; otherwise retain a separately qualified bound or unknown. This does not create additional physical capacity. |
| `coverage_assessments` | Scoped records for the required consumer inventory, memory terms/charges, physical-pool map, independent ceilings and scenario/transition coverage. Retain the qualification decision, evidence and unresolved causes. A `complete` assertion or well-formed reference is an input claim, never self-authenticating proof of completeness. |

Primary record IDs are required nonempty text, unique within their declared
complete inventories. Factual references retain their typed answer state; a
provided reference must resolve to the pinned scope, while an unresolved one
stays unresolved. Whenever both sides are provided, `device.local_pool_id = p`
and membership in `p.device_ids` must agree reciprocally. A contradictory
provided map, repeated membership or dangling provided ID is rejected; an
unknown counterpart prevents map qualification rather than being filled from
the other side. Reciprocal strings still do not prove physical aliasing or
disjointness. Lower/upper bounds are ordered, and a repeated pair or
contradictory physical identity is rejected before any applicability or outcome
shortcut. Preserve the current strict CD-13 identity/role and required-presence
paths; this profile supplies no more permissive role policy. Well-formed but
unresolved source scope, physical aliasing, allocation, confidence or coverage
produces unknown reasons. It is not malformed merely because a fact is missing.
Invalid structure is a diagnostic, not a compatibility pass or synthetic fail.

### Physical charge and host-offload semantics

Count a physical allocation once in its owning pool and scenario, even when
several qualified consumers refer to it. A shared model file, matching content
hash, equal byte amount, common catalog selection or common pool ID does not
establish one shared in-memory allocation. Known distinct copies have distinct
charges. Overlapping extents must be normalized into qualified non-overlapping
charges or remain unresolved; they cannot be silently deduplicated by amount.

Each logical consumer names its actual device, but its storage need not be in
that device's local pool. For example, an explicitly qualified GPU consumer may
use a host-pool offload buffer. Charge the host bytes to the host pool and any
device copy to the device pool. Pin transfer/staging and load/unload transients
when they can coexist. This accounting relationship neither adds a `runs_on`
link nor proves supported access, offload, zero-copy, bandwidth or lifetime.
Those actual runtime/backend/placement predicates remain #11/#3 or the
selected CD-10 service-runtime inputs. Unknown access
or copy/residency behavior remains visible even if a supplied numeric screen
passes. Unified memory is one qualified physical pool, not CPU capacity plus
GPU capacity counted twice.

A per-rank or engine quota is an additional independently scoped constraint.
It is not another disjoint pool that can be added to physical capacity. A shared
buffer's charge against such a quota depends on that quota's actual accounting
definition; it is not automatically divided among consumers or counted in full
for each rank. TP/PP/EP/DP labels identify a proposed plan but do not supply its
per-rank byte allocations. Missing rank mapping or applicable limits prevents
an overall pass while retaining already established pool failures.

### Reserve and exact comparison

For scenario s and physical pool p, let D(s,p) be the sum of the eligible
`live_upper_bytes` for unique resident charges in that pool. Let C(p) be its
qualified `capacity.lower_bytes` and R(p) its explicitly supplied reserve upper
bound. Use exact integer arithmetic and the declared capacity basis:

| Capacity basis | Required conditional screen |
| --- | --- |
| `before_reserve` | `D(s,p) + R(p) <= C(p)`; add the pool reserve once, not once per consumer, device, charge or scenario result. Each scenario is a separate comparison, not a sum across time. |
| `after_reserve` | `D(s,p) <= C(p)`; C already denotes the qualified reduced budget. Retain R and its source/method for traceability; do not subtract it again. The record must establish which reservation the reduced capacity already includes. |

The same basis distinction applies independently to any rank/engine ceiling;
it does not authorize an additional subtraction from the same physical budget.
An unknown reserve, capacity basis, deduction scope or required qualification
stays unknown. `R = 0` is valid only when explicitly supplied; no default reserve
or headroom percentage is selected. An advertised capacity is not an allocatable
or free-memory measurement; the recorded capacity scope limits the conclusion.

An explicit headroom fraction may be normalized only with its actual reference
capacity and exact conversion record. For integer C and exact `0 <= h < 1`, a
before-reserve comparison with integral D is equivalently
`D <= floor(C * (1 - h))`, or `D + ceil(C * h) <= C`. Record that rounding and
the original h; do not reconstruct an asserted headroom policy from two bounds.
Other already reduced bounds retain their actual source basis rather than being
forced into this conversion.

The existing 57-line #10 helper is unchanged: it requires positive capacity,
an explicit finite Decimal headroom below one, declared reserve basis and
caller-established confidence/domain eligibility. It computes its one-domain
comparison with exact Fraction arithmetic. A prospective zero usable budget
is representable here: positive demand fails its conditional screen, while a
known zero demand can pass that budget predicate if all required scope and
coverage are established. Such a zero-capacity record is **outside that helper's
current accepted input domain**. No execution or adapter for it is claimed.
For before-reserve input, R greater than C fails even with D zero; no clamp hides
an over-reserved budget. A new adapter requires its own implementation/review
and cannot silently relax or relabel the old helper's validation.

### Residency, evidence and result policy

In `conservative_all_resident`, retain every placed resident component and its
qualified charges, including `on_demand`, as one explicit conservative upper
envelope. Record that assumption. This is not a claim that all independent
stage peaks were observed simultaneously. Independent stage maxima do not
supply the routing, simultaneous request allocation or memory inventory needed
to qualify that envelope; those remain the existing CD-5/W-R6 inputs.

In `qualified_scenarios`, every component whose exact placement is `always`
remains in the required component inventory of every applicable scenario. Its
weights, KV, workspace and transient buffers need not have one identical
lifetime: each charge retains its own independently qualified residency, byte
bound and transition evidence. There is no allocation-level `always` field
and no lifetime inferred solely from a component label. Excluding an
`on_demand` component or any temporary charge requires actual scoped lifecycle
and transition evidence; no charge exclusion may silently remove an always
component. Omitted cold-load, retained KV, overlapping stages or
transfer buffers may invalidate the claimed coverage. Proving every listed
row passes does not prove the scenario list exhaustive. Missing coverage keeps
the overall screen unknown even when the supplied row results pass. If an
exhaustive scenario assessment is unavailable, a separately and explicitly
selected, fully qualified conservative envelope may be evaluated; the reader
must not silently change mode or hide the unresolved original result.

Memory bounds use the existing W-R6 request-to-sequence and EV-1 policy. Expand
the exact decoding demand before applying an applicable sequence admission
cap; the cap must bound all resident KV. Unknown admission may retain the
existing qualified expanded-demand fallback, not an assumed one sequence per
request. Memory precision/layout, context maxima, replicas, rank placement,
sharing and overhead keep their own evidence and assumptions. Source rank is
resolved before an equal-rank conservative maximum; an ineligible measurement
cannot displace an eligible estimate merely because it is called measured.

Preserve W-R6's fixed `error` severity and `on_unknown: review`. For each required
pool/scenario and independent limit, retain outcome, participating charge IDs,
exact bounds/reserve, assumptions, source/qualification/conflict references and
all unresolved causes. A conservative upper-bound failure is labelled **may
not fit under the supplied bounds**; it does not prove a measured OOM. A pass is
conditional capacity arithmetic, not engine support, quality, SLO or measured
fit. Checked-only evidence receives the existing scoped unverified label only
where the result depends on it; structural eligibility is no evidence upgrade.

A qualified failing required row remains fail alongside unknown rows elsewhere.
A known, identity-disjoint resident subset whose conservative upper charges
already exceed the supplied budget is a failing screen witness under this same
upper-bound policy; additional unresolved nonnegative charges cannot rescue
that policy comparison. Retain those missing charges and the limited witness.
Unresolved aliasing, residency or evidence needed for that witness prevents it
from becoming a fail. Aggregate fail if a required qualified witness fails;
otherwise unknown if any required value, scope or coverage is unresolved; pass
only when all required comparisons and coverage qualify. Within this profile,
skipped requires established non-applicability or a qualified absence of any
applicable placement in the requested scope. A missing or unknown required
placement, runtime responsibility, device or pool is unknown; an empty ledger
cannot supply either a pass or that skip. For an established opaque provider
component, the local-device/KV predicate is inapplicable, while undocumented
remote capacity stays unknown and known service predicates remain separate.
An exposed managed allocation uses its actual qualified scope. This explicit
profile does not alter unprofiled W-R6, including its documented no-placement
case or conservative treatment of `on_demand`.

Changes to the exact Build, selections/links, devices/pools, artifact/engine,
decoding/admission/stages, reserve, policy or evidence invalidate the dependent
receipt. Stable labels cannot rebind old bytes or findings to a new basis.
Retain original IDs and source order for audit; any canonical diagnostic order
must be explicitly defined by the eventual reader. Reordering a valid ledger
must not change its arithmetic or invent a different physical identity.

### Synthetic worked cases for the selected decision

These are hand-worked research examples, not fixture executions, allocations,
hardware measurements or engine-support claims. In this table U is exactly
1,000,000,000 bytes. All provided facts, evidence eligibility and complete scopes
are hypothetical except where a row explicitly leaves one unresolved.

| Case | Explicit inputs | Expected research disposition |
| --- | --- | --- |
| CD2-E1 Separate terms in one pool | Before-reserve C=24U, R=2U; resident charges 14U and 6U | D+R=22U; conditional pass. The two components do not each receive a fresh 2U reserve. |
| CD2-E2 Pool over upper-bound budget | C=24U, R=0; distinct resident charges 18U and 8U | 26U>24U; fail, may not fit. |
| CD2-E3 Unified physical memory | CPU charge18U and GPU charge8U belong to the same qualified 24U pool, R=0 | 26U>24U; fail. Two device records do not create 48U capacity. |
| CD2-E4 Separate pool failure survives | Two disjoint 24U pools, R=0; demands30U and6U respectively | First pool fails; second passes. The combined36U does not pass against an invented48U pool. |
| CD2-E5 Real sharing versus copies | C=20U, R=2U; one qualified physical8U allocation has two consumers, plus a separate6U charge | Shared case16U total passes. If the two8U buffers are established distinct copies, 24U total fails; equal contents or amounts do not deduplicate them. |
| CD2-E6 Once-only reduced reserve | Before-reserve C=24U/R=2U/D=22U, or after-reserve C=22U with the same recorded reservation/D=22U | Both budget predicates pass at equality. The after-reserve case does not subtract another2U. |
| CD2-E7 Known zero budget | After-reserve C=0 bytes with explicit reserve trace; D=1 byte, or D=0 with complete qualified scope | Positive demand fails; zero demand can pass this predicate. Both cases remain outside the unchanged #10 helper's positive-capacity domain. |
| CD2-E8 Explicit residency choice | C=24U/R=4U; two on-demand components have distinct qualified14U and8U charges. Conservative mode includes both | Conservative26U fails. A separately qualified exhaustive scenario set that proves mutual exclusion, including transitions, has18U and12U comparisons that pass. A statement that the two requests usually run serially is insufficient. |
| CD2-E9 Incomplete scenario set | Every supplied scenario fits, but retained-KV or transition coverage is unresolved | Keep those row passes and overall unknown. Their success is not evidence that no omitted peak exists. |
| CD2-E10 Known fail and unknown | One qualified pool has30U demand against24U; another placed component has a missing allocation bound | Retain first-pool fail and the missing-bound unknown; overall fail under the required-constraint policy, without a whole-build measured-fit conclusion. |
| CD2-E11 Host offload | GPU-local12U/16U budget; distinct host18U in a32U pool with4U reserve; both copies and lifetime known | Numeric pool screens pass at12U and22U. Unknown engine access remains a separate unknown; it is not certified by the arithmetic. |
| CD2-E12 Transfer overlap | Same host case, plus a distinct coexisting16U staging charge | Host38U exceeds32U, so fail. Treating transfer/load as automatically nonresident would miss this conditional failure. |
| CD2-E13 Replica and rank scope | Two replicated14U physical buffers in one24U pool; no actual shared-storage identity | 28U fails; a shared artifact identity does not share storage. A separate per-rank quota must also retain its actual membership/byte accounting, not an equal split. |
| CD2-E14 Missing is not zero | One required resident charge is `withheld` or `unknown`; another is explicitly provided0 bytes | Preserve the withheld/unknown reason and the real zero distinctly. In the absence of an independent failing witness, overall unknown. |
| CD2-E15 Structure before shortcut | Duplicate allocation ID, repeated scenario/allocation pair, Boolean/JSON-number byte token, dangling provided consumer reference or contradictory provided device/pool membership, even if another pool is over budget | Reject the malformed input before outcome shortcuts; do not hide it behind a fail or skipped result. Unestablished physical aliasing or an unknown membership counterpart in otherwise well-formed evidence remains unknown instead. |
| CD2-E16 Exact scope and separate constraints | A passing byte bound belongs to another engine/build/replica, or a context limit passes while the required KV geometry is unknown | The mismatched bound is ineligible and allocation stays unknown; a passing context predicate does not manufacture memory eligibility or a fit result. |
| CD2-E17 Exact byte-token identity | Provided after-reserve budget `"9007199254740992"`; demand `"9007199254740993"`; explicit reserve trace and complete qualified scope | The demand exceeds the budget by exactly one byte and fails. An intervening binary-float parse cannot erase that difference. `"00"`, `"+1"`, `"1e3"` and numeric `1` are not valid ByteCount tokens. |
| CD2-E18 Component, runtime and applicability | An always-placed vector service has a qualified CD-10 runtime, resident index charge and independently evidenced temporary-workspace lifetimes; a separate provider component has established opaque internals | Retain the service in every applicable scenario without forcing all its buffers to share one lifetime or inventing an inference-engine selection. The opaque component supplies no local device or pool. Unknown required placement for another local component remains unknown, not an opaque-service skip. |

### Receiving and migration obligations

The selected representation requires actual bounded dispositions against its
fixed source. Existing H40 base-field receipts and the closed #10 research issue
remain valid for their recorded scopes; they are not silently enlarged into
acceptance of this new allocation decision. Required receiving review covers:

| Consumer | Concrete question for this decision |
| --- | --- |
| #10 | Accept or correct physical-pool ownership, exact charge aggregation, reserve basis, conservative bound outcomes, independent rank limits and the explicit zero-budget/helper boundary. This does not reopen its completed hardware research or require a new empirical result. |
| #11 | Accept or correct consumer/rank/replica/admission identity, offload/copy/lifetime accounting and the separation of memory bounds from engine/backend support. No engine capability or measured residency is supplied by this record. |
| #7 | Accept or correct the separation of exact context/route limits from qualified KV geometry, sequence demand and placement; retain native fallback and the existing conservative context policy. |
| #2 / #3 | Accept or correct exact workload/stage and selection/device bindings, all-resident preservation, scenario completeness, transition scope and physical-pool applicability across exposed API/managed/self-hosted components. Opaque capacity remains opaque; missing placement is not fabricated. |

No consumer note is edited by this one-path decision. The actual reviewer,
source pin, conditions and retained unknowns must be recorded in each receiving
receipt; no reply is attributed to an absent assignee. The earlier four-file
author retains that implementation and may supply its existing checkpoint for
comparison. A distinct wire/schema/adapter release must name its version,
source fixtures, validation and affected-reader acceptance. It must preserve
all frozen v1 bytes and historical result dispatch, and may not put pool/scenario
fields into a scalar ResourceEstimate or invent a Build ID to satisfy it.

No #40 checkbox, #42 prerequisite or native API decision is changed by this
draft. The concrete research choice can be assessed independently of a future
runtime, but source review, actual receiving disposition and protected delivery
remain real gates before its acceptance or a new whole-issue assessment.
