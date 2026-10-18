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
| Knowledge/actions/customisation needs | Knowledge capability set or exclusive none/unknown; actions none/read_only/write; customisation none/prompt_only/fine_tune | A knowledge implementation identifies its route and selection IDs; long-context/direct lookup needs justification | workload dictionary and W-R2–W-R5; #13/#16/#25/#30 |
| Memory need and implementation | Need none/session/persistent; implementation via application/agent_framework/memory_store with IDs and justification | Persistent memory can accompany a single-turn conversation. Application session history need not select a memory store | workload dictionary and W-R11; #2/#28 |
| Request volume and concurrency | Request count integer ≥ 0 per day/month; peak concurrent requests integer ≥ 1 | Zero volume is distinct from absent volume. Service-wide demand cannot be combined with per-replica admission without allocation | workload dictionary and W-R6; #10/#11/#39 |
| Input/output token demand | Mean decimal and maximum integer; input 1 ≤ mean ≤ max; output 0 ≤ mean ≤ max | Mean 1.5 is valid. Output is not applicable only for an operation generating no tokens; thinking is counted once in output | workload dictionary; #7/#39 |
| Native non-text demand | Per-request image count integer max; audio/video seconds decimal max; decimal means ≥ 0 and ≤ max | These are native units, not invented token counts. Stage-specific limits remain CD-11 | workload dictionary; #6/#7 |
| Tokenizer and context policy | Tokenizer/model identity plus exact route's input/output/combined budget semantics | Independent caps 8,000 input and 4,000 output do not imply a 12,000 shared window; exact new wire fields remain CD-11 | #7; T1 gaps; worked context examples below |
| Latency and throughput targets | Latency metric ttft/tpot/e2e, positive integer ms, percentile 50/90/95/99; positive decimal throughput with unit and scope | At most one latency target per metric. Aggregate requests/s is distinct from per-request output tokens/s | workload dictionary; #36/#39 |
| Quality target | Protocol/metric/reference IDs, higher_better/lower_better, nonnegative absolute or relative-percent degradation | Relative-percent degradation is invalid when reference value is zero; unlike protocols are not comparable | workload dictionary and W-R10; #36 |
| Budgets | List of nonnegative decimal amount, ISO currency, period one_off/month/year and scope hardware/operating/total | Empty list explicitly means unconstrained; missing currency cannot default to USD | workload dictionary; #39/#41 |
| Hardware inventory | Stable unique device IDs, gpu/cpu/npu/other kind; positive decimal GB (10⁹ bytes), pool ID; reserved GB ≥ 0 per pool | CPU/GPU sharing one pool must not double-count its bytes; usable capacity needs separate evidence | workload hardware dictionary; CD-2/#10 |
| Device capabilities | memory_kind dedicated/unified/system; positive decimal GB/s with vendor_peak/measured basis; ISA set; NUMA count integer ≥ 1 | Published peak bandwidth is not a measured workload rate | deployment dictionary; #10/#11 |
| Engine build and admission | Version, fork URL/commit when applicable, launch options; positive integer sequence expansion/admission and matching domain | Missing expansion leaves sequence demand unknown; a per-step batch limit is not automatically a KV-residency cap | deployment dictionary and W-R6; CD-2/CD-3/#11 |
| Artifact representation | Format gguf/safetensors/onnx/pytorch/other; separate package convention; quantization method, positive logical/stored bits, packing | Package convention is not serialization; a quantization label alone supplies no byte estimate | deployment dictionary; #6/#10/#11 |
| Artifact `components` | List of role language_model/vision/draft/other, positive decimal size_gb and required boolean | A required vision component must be included in the scoped resource model | deployment dictionary; #6/#10 |
| Conditional support/list completeness | Supported values plus completeness and exact tuple/evidence metadata; wire shape open | Absence from exhaustive applicable list → fail; absence from researched subset → unknown | CD-3; #6/#9/#11 |
| Licence conditions and answers | Conditions have ID/text/source/kind eligibility or obligation/question; answers depend on kind | Eligibility met/not_met differs from obligation acknowledged/not_acknowledged. Answer/reference locations still require CD-6 | deployment dictionary; #30/#40 |
| Organisation attestations | Jurisdiction code, EU-market-placement boolean, lawful-basis reference; CD-12 also includes revenue and monthly active users. Revenue needs an amount, currency, reporting period and the licence-defined organisation/account scope; MAU needs a user count, monthly measurement period and the licence-defined product/organisation scope. Exact value types, aggregation and wire fields remain unresolved against the selected condition | A missing revenue or MAU answer leaves an applicable eligibility condition unknown; never infer zero or reuse a differently scoped total. These are sensitive user attestations, not inferred permission or transferable consent | workload dictionary; deployment CD-12 and licence-condition questions; #30/#31/#32/#42 |
| External connections | Entries with destination ID, purpose, provisioning/runtime lifecycle, enabled/disabled state, data-carrying and required booleans | Unknown state and absent inventory remain unresolved; runtime isolation also needs the selected boundary | deployment dictionary; CD-4/#37 |
| Destinations and residency | Destination IDs/host, processing/storage code lists and data scope; processing and storage constraints separate | Unconstrained residency is distinct from unknown; jurisdiction containment/group semantics remain CD-9 | both dictionaries; #37/#41 |
| Provider data terms | Training-use enum, scoped application-state/abuse-monitoring retention entries, zero-retention eligibility and conditions | Free-text conditions cannot silently become pass; endpoint/account/region evidence required | deployment dictionary; #5/#9 |
| Billing descriptor | charge_basis per_use/per_time/flat_subscription/none; ownership; optional commitment kind/term | Does not determine mode or substitute for a pricebook; new meter units require #39 disposition | deployment dictionary; #39 |
| Build links | Existing relation/from/to references; proposed role/access attribute | Multiple possible credential/base bindings without an evidenced disambiguation remain unknown; inheritance rules are CD-6 | CD-6 and T4 queue; #40 |
| Snapshot and pricebook locks | Existing IDs plus proposed explicit revisions; exact revision wire type/location pending | Missing revision produces “cannot be reproduced exactly”, never replacement by latest | CD-7, M5; #42 |
| Evaluation result | Fixed rule severity; outcome pass/fail/unknown/skipped; proposed reason code, disputed flag and evidence label | A passing error-severity rule is not a failure; evidence disagreement does not change severity | Rule semantics above; CD-1/CD-3 |
| Multi-selection evaluation | Quantify over enabled selections; reject duplicate primary roles semantically before evaluation | Two primary selections must not silently cause a required rule to skip; quantifier syntax remains open | CD-13; #40/T4 |

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

**For @zwright8 review:** confirm, narrow or reject the proposed T5 routing inventory below for #68/#76/#77; no disposition is inferred.

## Contract decisions

CD-1 to CD-12 are defined in #81 (`deployment-mode.md`, "Open contract decisions") and remain the base list. CD-13 is added here, from T4's findings on #40:

| ID | Decision | Accountable |
| --- | --- | --- |
| CD-13 | Rules over several selections of one kind: a quantifier over all enabled selections, and semantic rejection of duplicate `primary` roles before evaluation, so that "not selected", "not relevant" and "not yet known" are not collapsed into `skipped` (T4 finding 1; CD-1) | #40 |

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
| #42 draft (#114) SB-1 to SB-10, SB-R1 to SB-R5 | Saved-build record gaps (assumptions, snapshot and pricebook revision locks, visibility, derived validation state, fork lineage, several workloads, `withheld` answer state, where cross-record checks live) and integrity rules | #40; SB-8 with CD-1; SB-7 with #10 |

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
| Primary sources with access dates | Contract files at the merged revision; reviews linked | Partial |
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

Run `python -m unittest discover -s tests -p test_t0_migration.py -v`. The tests cover all operator/capacity pairs, unknown dominance, non-serving/disabled components, adapter inheritance and missing/cyclic bases, duplicate IDs, conflicting workload copies including zero, absent snapshot/pricebook revisions, and unchanged v1 historical evaluator findings. They are synthetic semantics checks, not runtime measurements or validation of a released migration adapter. Actual snapshot resolution and dual-ruleset evaluation remain future versioned implementation.

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

## Proposed T5 routing inventory

This is an initial routing synthesis from the merged T5 README and component notes, inspected 2026-10-17; it does not accept their hypotheses or replace @zwright8's triage disposition.

| T5 input | Proposed family or contract decision | Remaining acceptance |
| --- | --- | --- |
| F-series framework method/backend support | Joint support and loader/API families; CD-3/CD-6, keep managed-service backend optionality distinct | #30/#40 confirm scope and supported methods |
| K-series resource estimates and training meters | Memory fit via CD-2/CD-3; price dimensions through #39, then #40 | #10 confirms estimator dimensions; #39 confirms meter semantics |
| D-series dataset governance and provenance | Licence/rights and CD-3/CD-6; replace boolean-only evidence through versioned fields | #32/#30/#60 source-specific rights; D-20 leakage/freeze remains #36 policy |
| A-series base revision, adapter metadata and notices | Loader/adapter and licence families; CD-6/CD-7; applicability-aware A-18a/b/c remains separate | #33/#11/#30 confirm lineage and notice predicates |
| A-13 deployment lifecycle; A-20 evaluation gate | Lifecycle to #37; gate to #36, with references in the shared rule record | #36/#37 dispositions remain separate from #40 schema routing |

No T5 candidate is promoted into the executable baseline by this inventory. Field and fixture implementation remains a next-version proposal requiring affected-owner review.
