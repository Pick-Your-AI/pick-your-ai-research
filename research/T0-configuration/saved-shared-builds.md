# T0: Saved, Shared & Compared Builds

Issue: #42 · Contract: v1 1.0.0 (adopted in PR #44; inspected at `f297ac5`) · Kinds: `BuildSnapshot`, `Selection`, `CatalogSnapshot` (with `EvaluationReport`, `CostEstimate`, `Pricebook`, `Ruleset`, `DependencyGraph`, `Event` as referenced records)
Status: partial research proposal; #42 completion remains blocked by #40 · Last researched: 2026-10-18 · Guidance: PR #74 Track E (P7)
Deliverable path: `research/T0-configuration/saved-shared-builds.md`

Labels used in this note:
- **V** IDs cite the v1 contract in this repository; **X** IDs cite external primary sources; **P** IDs cite project decisions and drafts.
- **SB-n** IDs are this note's open decisions, routed to #40 unless stated. They are separate from #81's CD-1 to CD-12, which this note references but does not renumber, extend or settle.
- **SB-Rn** IDs are rule proposals for #40 review.
- **Proposal:** a design choice made in this note, not a sourced fact.
- "Source checked" means the claim was compared with the cited source on its access date. Nothing here is independently reproduced ("verified" in the #41 interim sense, P3).

## Proposal sequencing decision — 2026-10-18

This partial design record can proceed through ordinary PR review and merge while the contract prerequisite remains open. Recording the proposal gives #40 and the other receiving issues concrete semantics to review. It does not adopt the SB or CD field shapes, release a successor contract, activate a consumer, or supply pending receiving-owner acceptance. #40 and #42 remain open, and #42 retains its #40 prerequisite. The earlier draft-hold reviews remain historical records; this decision changes only the order in which the partial proposal may merge, not the requirements for completing the issues.

The sequencing change is recorded at [f56b0fc](https://github.com/Pick-Your-AI/pick-your-ai-research/commit/f56b0fcdb34d91e1751edc3b4cd44dba9bc04960), with independent reviews [5561898533](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/114#pullrequestreview-5561898533) and [5561921315](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/114#pullrequestreview-5561921315) submitted before [squash merge 649f5870](https://github.com/Pick-Your-AI/pick-your-ai-research/commit/649f5870e9729ec1aaf1b5f07e9290ce0f777833). These reviews concern publication of this partial record and retain the receiving-owner gates; they do not replace the earlier revision-specific reviews or the scoped #41 receipt.

## Summary

- **A saved build is an immutable `BuildSnapshot` revision plus the derived records that cite that revision.** Every edit creates a new revision; old revisions are kept (V5). The v1 locks already pin the catalog snapshot, ruleset version and dependency graph revision (V1).
- **Two validity views, never merged.** *Historical validity* is the `EvaluationReport` produced under the build's own locks. *Current validity* is a fresh evaluation of the same selections against the currently published catalog snapshot, ruleset and pricebook. A revisit shows both and the per-rule differences. Neither overwrites the other, and nothing in the user's selections changes without consent (V5, V6).
- **Sharing stores the build server-side behind an opaque link and shares a redacted projection.** Credentials references, endpoints, free text, budgets, residency, data classification and organisation attestations are withheld by default. A recipient who forks gets the withheld inputs as unanswered, so the rules that read them give `unknown`, never `pass`.
- **Comparisons align selections by kind and role and show "not comparable" with the reason** when currency, pricing period, workload, ruleset version, evidence protocol or cost coverage differ. Modes are compared per serving component using #81's merged definitions (P1).
- **Time alone never invalidates a build.** Under the #41 interim policy, version-pinned facts don't expire and current-state facts are shown "as of" their access date with no TTL (P3). Invalidation comes from publications: a new catalog snapshot, ruleset version, dependency graph revision or pricebook; a lifecycle change; a #60 rights decision; or a build edit.
- **v1 gaps** (visibility, validation state, assumptions, cost snapshot link, snapshot revision lock, fork lineage, withheld-input state, multi-workload builds) are recorded as SB-1 to SB-10. No schema is patched.

## User decision

What should a saved or shared build contain, how are builds compared, and what happens to a saved build when catalog data, prices or rules change? This note covers builds in every deployment mode #81 defines (API, managed, self-hosted, hybrid; P1). Accounts, storage implementation and UI are out of scope (issue scope).

## Candidate options

### Save semantics

| Option | Description | Assessment |
| --- | --- | --- |
| A. Pinned only | Reopen shows the save-time result and nothing else | Reproducible, but hides retired components, new rule failures and newer prices. Rejected. |
| B. Live only | Reopen re-evaluates against current data and replaces the old result | Loses "what was valid when I saved it" and silently changes meaning. Conflicts with "do not physically rewrite old evidence" (V5). Rejected. |
| C. Pinned plus current (Proposal) | Keep the historical report; compute a current report for the same selections; show the difference; the user chooses whether to adopt current locks as a new revision | Matches V5/V6 and PCPartPicker note requirement 4 (P5). **Recommended.** |

### Share transport

| Option | Description | Assessment |
| --- | --- | --- |
| Self-contained URL | Encode the build in the link | Can't be revoked or re-redacted after a rights change. RFC 9110 recommends support for URIs of "at least 8000 octets" (X1), and a build with 2+ selections, settings and links has no size bound, so portability isn't assured. Rejected for the primary share. |
| Opaque link to a stored projection (Proposal) | The link carries a random token; the server returns a redacted projection of one revision | Revocable; redaction can be recomputed when #60 decisions change. **Recommended.** |
| Export file | Downloadable JSON of the build | Kept as a separate, explicit action. Prior art: Dify's DSL export excludes third-party tool API keys, knowledge content and logs, but can include Secret-type environment variables when the user opts in (X2). n8n's JSON export includes credential names and IDs; HTTP Request nodes imported from cURL can also contain authentication headers, which its documentation tells users to remove or anonymise before sharing (X3). These exclusions do not establish that an arbitrary export is safe. Pick Your AI exports apply the same redaction as shares. |

### Deployment modes covered

All four modes appear in the comparison semantics. Mode is a per-serving-component property in #81's merged decision; the build's mode is derived (`hybrid` when components differ, `unknown` when any is unknown) (P1). v1 instead has one `deployment_mode` selection with `cardinality: one` (V9). Until #40 decides CD-7, this note reads mode from #81's definitions and labels it pending.

## Build record definition

### Mapping the issue's minimum fields to v1

| Issue field | v1 location (JSON pointer) | Status | Note |
| --- | --- | --- | --- |
| `build_id` | `build.schema.json#/properties/id`, with `#/properties/revision` (integer ≥ 1) | Covered | A saved build is the pair (id, revision) |
| schema version | `build.schema.json#/properties/schema_version` (const `1.0.0`) | Covered | Migration across contract versions is CD-7 (#81) |
| selections (entity id + version) | `build.schema.json#/properties/selections` → `selection.schema.json#/properties/catalog_item_id`, `#/properties/catalog_item_version` | Covered | Nothing requires the version to be a member of the locked snapshot: SB-R1 |
| per-component settings | `selection.schema.json#/properties/settings` (typed per kind via `allOf`) | Covered | Several settings are sensitive (see privacy) |
| runtime wiring | `build.schema.json#/properties/links` | Covered | #81 uses links for host, devices and engine (P1) |
| workload inputs | `build.schema.json#/properties/objectives` and the `workload` selection's `settings` (`selection.schema.json#/$defs/settings_workload`) | Partial | v1 holds three copies with different names; #81 proposes one build-owned `/workload` profile (P1, Recommendation 3). This note adopts whichever #40 accepts. |
| assumptions | — (only `#/properties/extensions`, `x_` keys) | **Gap: SB-1** | Presets, defaulted values, "I don't know" answers and FX/tax assumptions have no field |
| rule snapshot id | `#/properties/locks/properties/ruleset_id`, `.../ruleset_version` | Covered | |
| dependency graph | `#/properties/locks/properties/dependency_graph_id`, `.../dependency_graph_revision` | Covered | |
| catalog snapshot id | `#/properties/locks/properties/catalog_snapshot_id` | Partial: **SB-2** | `CatalogSnapshot` has its own `revision` (`catalog-snapshot.schema.json#/properties/revision`) that the lock doesn't record |
| cost snapshot (currency, date) | `#/properties/locks/properties/pricebook_id` (optional); `#/properties/objectives/properties/currency`; `CostEstimate` cites `build_id`, `build_revision`, `pricebook_id`, `estimated_at`, `currency`, `coverage` | Partial: **SB-3** | The build doesn't reference its estimate, and the pricebook's `revision` isn't locked |
| price check date | `Pricebook#/properties/captured_at`; rate `valid_from`, `valid_until`, `provenance[].checked_at` | Covered at pricebook level | Shown as "as of" (P3) |
| visibility | — | **Gap: SB-4** | |
| validation state | — in the build. `EvaluationReport` cites `build_id`, `build_revision`, all four locks, `evaluated_at`, `result`, `deployment_readiness`, `findings[].outcome`/`.severity` | **Gap: SB-5** | `lifecycle: validated` (`#/properties/lifecycle`) is a stored claim that goes stale when locks change |
| created / modified | `#/properties/created_at`, `#/properties/updated_at` | Covered | |
| owner | `#/properties/owner_ref` (required) | Covered, sensitive | Withheld from shares |
| fork lineage | — | **Gap: SB-6** | |
| per-component mode | — (`deployment_mode` selection, cardinality one, V9) | Pending #81 / CD-7 | Not an SB decision |
| several workloads on one machine | — (`workload` cardinality one, V9) | **Gap: SB-7** | #81 Q7 handoff |

### What makes a build reproducible (Proposal)

Re-evaluation of (build id, revision) yields the same findings when all of these are pinned and retrievable: every selection's `catalog_item_id` + `catalog_item_version`, its settings and links, the build inputs, the catalog snapshot (id and revision, SB-2), the ruleset id + version, the dependency graph id + revision, the pricebook id + revision (SB-3), the evaluator version (SB-5), and any external evidence the rules consumed, such as resource estimates, pinned by their own versions (V7). If any of these is gone, the historical report is still shown, labelled "cannot be reproduced: <missing record>".

### Derived records

A saved revision is the root of: its `EvaluationReport`s, `CostEstimate`s, `ResourceEstimate`s and any `DeploymentManifest`. A derived record whose `build_revision` differs from the build's is stale and is shown as such, never as current (V6, V8).

## Save, share and compare semantics

### Save and revisit (Proposal)

1. Every change persists a new immutable revision under compare-and-swap (V5). "Save" names a revision; it doesn't freeze the build.
2. On revisit, show the historical report for that revision's locks.
3. Compute a current report for the same selections against the latest published snapshot, ruleset, graph and pricebook. This is a candidate, not a revision. It doesn't change the saved build.
4. Show the differences per `rule_id`: outcome (`pass`/`fail`/`unknown`/`skipped`) and severity (`info`/`warning`/`error`) side by side, with the rule message, remediation and evidence path (V10). Price differences show both pricebooks' "as of" dates.
5. The user can adopt the current locks, which creates a new revision. Replacements for retired components are offered, never applied automatically (V6).

### Revisit states shown to the user (Proposal; storage is SB-5)

States are derived on read, not stored. More than one can apply.

| State | Condition | What the viewer sees |
| --- | --- | --- |
| Up to date | Locks equal the latest publications, and a report exists for this revision | Current result only |
| Not evaluated | No report has `build_revision` equal to the build's | "Not checked yet". Never shown as valid |
| Newer data available | A newer catalog snapshot, ruleset version, graph revision or pricebook exists | Historical result, labelled with its lock dates, plus the current result |
| Result changed | Current findings differ from historical findings for any rule | The per-rule diff; changes to `fail` or `unknown` listed first |
| Now indeterminate | A historical `pass` is `unknown` in the current report | "Can no longer be confirmed", with the missing evidence |
| Now valid | A historical `fail` is `pass` in the current report | "This now passes under ruleset <version>"; the historical failure stays visible |
| Component deprecated | The selected item's applicable lifecycle evidence says `deprecated` | SB-R4a `fail/warning`; SB-R4b still passes availability. Offer a replacement without claiming the item is unavailable |
| Component unavailable | The selected item is `retired`, or an exhaustive current snapshot establishes absence for its exact item/version scope | SB-R4b `fail/error`, with the evidence scope |
| Availability unknown | Snapshot retrieval, lifecycle evidence or item/version coverage is unresolved | SB-R4b `unknown/error`, not an unavailable claim; omission from an incomplete list proves no retirement |
| Prices as of | Always for current-state facts | "Prices as of <captured_at>". A newer pricebook or a rate past `valid_until` makes the old estimate historical, not current |
| Values withheld | A #60 decision removes display rights, or a share withheld an input | The finding's outcome without the value, and the reason |
| Cannot be reproduced | A pinned record is missing | Historical result labelled accordingly |
| New contract available | A successor contract is published while this revision still pins its original schema | Preserve the original bytes, historical findings and reproducibility under the retained reader; offer an explicit migration as a new revision |
| Current evaluation unavailable | The proposed current evaluation needs an unsupported contract/ruleset or an unavailable migration | Show the historical result with its original version and explain the unavailable current path; do not mark the historical result irreproducible solely because a successor exists |

`EvaluationReport.result = valid` means the configured rules passed for the locked revision, not production readiness (V6). Shares say so.

**Synthetic boundary examples (proposal, no runtime measured):** an item marked `deprecated` remains available with a warning; an item omitted from a non-exhaustive snapshot has unknown availability. A v1 revision with all original records and its v1 evaluator retained remains reproducible after a v1.1 publication. If the v1.1 migration is unavailable, only the proposed current view is unavailable. If the original pinned evaluator or a required record is actually lost, the historical findings remain visible but their reproducibility is qualified with that specific missing dependency. These cases follow SB-R4a/SB-R4b and #40's [CD-7 migration boundary](component-schema-compatibility.md#contract-versions-and-migration-cd-7-proposal); they do not release a successor contract.

### Sharing (Proposal)

| Aspect | Decision |
| --- | --- |
| What a link points to | One immutable revision by default. An owner may choose "follow latest revision"; the viewer is told which. |
| Access modes | `private` (owner only); `unlisted` (anyone with the token); `public` (listed and discoverable). Organisation-scoped sharing needs accounts and is out of scope. Mode is a property of the share, not of the build, so changing it doesn't create a build revision (SB-4). |
| Read-only vs fork | Every share is read-only. Fork creates a new build id at revision 1 with a lineage pointer to the source (id, revision) (SB-6). Withheld inputs arrive unanswered; attestations are never copied. |
| Revocation | Revoking a token stops access to the projection. Copies already exported or forked are outside control and the share flow says so. |
| What the viewer sees | Both validity views; the lock dates; "as of" price dates; which fields were withheld |
| Retention | Open product decision (SB-9) |

### Field sensitivity for shared links and exports

Default treatment. "Opt-in" means the owner explicitly includes the group for that share.

| Field (v1 pointer or #81 proposed field) | Class | Shared / exported | Why |
| --- | --- | --- | --- |
| `selections[].catalog_item_id`, `catalog_item_version`, `kind`, `role`, `enabled`, `links`, `locks`, `schema_version` | Configuration | Included | Needed to reproduce the build; catalog facts, not user data |
| Any `*credential_ref`, `account_ref`, `encryption_key_ref`, `connector_secret_ref` (`selection.schema.json#/$defs/settings_*`) | Secret locator | Never | A `secret://` reference is not the credential (`common.schema.json#/$defs/secret_ref`), but it discloses secret-manager paths. n8n warns that even credential names can be sensitive (X3). |
| `api_base_url`, `endpoint` (MCP, integration), `weights_uri`, `artifact_uri`, `index_name`, `approval_ticket` | Internal infrastructure identifier | Never | Locates private systems or internal processes |
| `owner_ref` | Personal / organisational identifier | Never; the share shows a display name chosen at share time, if any | |
| `name`, `selections[].notes`, #81 `task_description`, `site_label` | Free text | Opt-in, with a warning | Free text can contain anything |
| `objectives.data_classification`, #81 `data_categories` | Data-handling posture | Opt-in | Discloses what data the organisation processes; #81 maps categories to GDPR definitions (P1) |
| `objectives.region`, #81 `residency.*`, `hardware_location.jurisdiction`, settings `region` | Location | Opt-in | Reveals where data and systems sit |
| `objectives.monthly_budget_amount`, #81 `budgets`, `settings_cost_policy` amounts | Commercial | Opt-in | |
| Load inputs: `requests_per_day`, `max_concurrency`, token counts, #81 `requests`, `peak_concurrency`, `input_tokens`, `output_tokens`, latency and throughput targets | Business volume | Opt-in | Usually needed by a recipient to judge fit, but reveals scale |
| #81 `hardware.devices[]` model names and memory | Configuration | Included | #81 already excludes serial numbers and hostnames (P1) |
| #81 CD-12 organisation attestations (establishment jurisdiction, EU market placement, lawful basis, revenue, MAU), `licence_answers` (with `grant_ref`), zero-retention or account approvals in `data_terms` conditions | Organisation attestation | Never, and never copied on fork | An attestation is made by one organisation about itself; it can't transfer to the recipient |
| #81 `destinations[].host`, `external_connections` | Infrastructure | Included without hosts | Mode and residency findings stay explainable |
| `EvaluationReport.findings[].evidence[].observed` | Derived | Included, unless it echoes a withheld input | The observed value would leak the input |
| Catalog-sourced values (prices, benchmark figures) in findings or cost lines | Third-party data | Only where #60 grants commercial display (P4) | A share to the public is display |

**Withheld is not unknown, but evaluates like it (SB-8).** A viewer of a share sees the historical findings the owner's inputs produced, with withheld values hidden. A fork has no value for the withheld inputs, so rules that read them give `unknown` (CD-1's "not yet known" in #81 terms), and the recipient is prompted to answer. A withheld input never evaluates as `pass`, and it is never filled with a default.

### Comparison (Proposal)

Builds, or revisions of one build, are aligned per selection by (`kind`, `role`). A kind present in one build and absent in the other is displayed as "not selected". Only predicates whose applicability is false for an optional or disabled branch are `skipped`; required-presence and cross-component predicates still evaluate. Comparison presentation never rewrites evaluator outcomes. Absence is never zero cost or a pass.

For example, `rule.required.foundation` always applies: a build missing its primary model retains its foundation failure in the comparison. In contrast, an absent optional T5 tier skips its adapter/training-only predicates when their applicability is false (P6); it does not skip unrelated foundation or cross-component checks.

**Comparison fields**

| Field | Type and unit | Source | Comparable when | Evidence requirement |
| --- | --- | --- | --- | --- |
| Selection per (kind, role) | `catalog_item_id` + `catalog_item_version` | `Selection` | Always | Pinned snapshot |
| Mode per serving component | enum `api`, `managed`, `self_hosted`, `unknown`; build: plus `hybrid` | #81 `deployment` object (pending) | Always; `unknown` shown as unknown | #81 classification test |
| Compatibility result | `EvaluationReport.result` enum, plus counts from `summary` | `EvaluationReport` | Both reports use the same ruleset id and version; otherwise offer to evaluate both under the newer ruleset | Report `build_revision` equals the compared revision |
| Per-rule finding | outcome × severity | `findings[]` | Same `rule_id` and ruleset version | As above |
| Total cost | `money` (`decimal` string + ISO 4217), per `period_days` | `CostEstimate.total` | Same currency (v1 has no FX policy, V8), same `period_days`, same workload inputs, both `coverage: complete` | Pricebook dates shown; `partial`/`unknown` coverage shown as "incomplete" |
| Cost by charge basis | #81 `billing.charge_basis`: `per_use`, `per_time`, `flat_subscription`, `none` | #81 (pending) | Shown per component; a total across bases needs the same workload and period | #39 owns aggregation |
| One-off vs operating spend | #81 `budgets[].scope`: `hardware`, `operating`, `total` | #81 (pending) | Never summed without an amortisation policy (#39) | — |
| Context limits | tokens | catalog `spec` | Same tokenizer basis; separate input/output budgets wait on CD-11 | Pinned catalog item |
| Fit and performance | engine-specific units | resource estimates, measurements | Same protocol and configuration key (#81 EV-1, CD-3) | Version-pinned evidence |
| Lock dates | timestamps | `CatalogSnapshot.captured_at`, `Ruleset.published_at`, `Pricebook.captured_at` | Always shown | — |

**Examples (synthetic, for illustration only; no real prices)**

1. *API vs self-hosted, same workload.* Build A's model is on a shared provider API (`api`); build B runs the same open-weight model with an engine on an owned GPU (`self_hosted`). Both evaluate under ruleset `1.0.0`. The self-hosting rules are `skipped` in A and evaluated in B; the table shows "not applicable in A", not "passed in A". Cost: A has a per-token operating cost; B has a one-off hardware budget and an operating cost. The view shows them in separate rows and no single "cheaper" verdict.
2. *Same build, new ruleset.* Revision 3 was evaluated under ruleset `1.0.0` with a context rule `pass`. Ruleset `1.1.0` adds an output-budget check that has no evidence for the selected route. The current view shows that rule `unknown`/`error` ("Now indeterminate"), and the historical `pass` stays visible with its ruleset version.
3. *Hybrid vs managed, different currencies.* A is `hybrid` (self-hosted LLM, API embeddings) priced in EUR; B is `managed` priced in USD. Totals are "not comparable: different currency"; components, modes and findings are still compared.

### Several workloads on one machine (#81 Q7)

v1's `workload` kind has cardinality one (V9), and #81 keeps one primary workload per build (P1). Two candidate representations:

- **(a) One build per workload, plus a hardware group.** Builds stay simple, but memory-pool fit (#81 W-R6) must then be evaluated across builds, which v1 has no record for.
- **(b) One build with several workload selections distinguished by role,** each serving component linked to the workload it serves. One evaluation covers co-residency, but it needs a cardinality change and rules that address a workload by role.

Lean: (b), because co-resident memory can only be checked where all resident components are known together. Recorded as SB-7 for #40 with #10; not decided here.

## Invalidation triggers

| Trigger | Detection in v1 | Effect on the saved revision | User-visible state |
| --- | --- | --- | --- |
| Build edit | New `revision`; `build.selection.upserted`/`removed`, `build.link.upserted`, `build.objectives.updated` events (V11) | Prior derived records are stale for the new revision; affected kinds found both ways through the graph, honouring activation before and after (V5) | Not evaluated (until re-run) |
| Catalog snapshot published | `catalog.snapshot.published` event (V11) | Historical unchanged; current report computed | Newer data available; Result changed |
| Item lifecycle change | Eligible evidence establishes `deprecated`, `retired` or exact-scope absence in the newer snapshot | As above; incomplete coverage remains unresolved | Component deprecated (SB-R4a), Component unavailable (SB-R4b), or Availability unknown, as supported by the evidence |
| Source correction (#41) | New item revision in a new snapshot | Version-pinned facts are re-checked only when the version changes or the source is corrected (P3) | Result changed, if it did |
| Conflict re-resolution (#41) | New snapshot with the re-resolved claim | As above | Result changed |
| Time passing | — | **None.** No TTL exists under the interim policy (P3) | Prices as of <date> |
| Ruleset version published | `ruleset.published` event; `locks.ruleset_version` differs | Current report under the new version | Newer data available; Result changed |
| Dependency graph revision | `locks.dependency_graph_revision` differs | Activation and affected kinds may change | Newer data available |
| Pricebook published, or rate past `valid_until` | `pricebook.published` event; rate `valid_until` | Historical estimate kept; current estimate computed. A stale or partial quote makes budget checks `unknown`, never budget-pass (V8) | Prices as of; Result changed |
| #60 rights decision changes to "no" | #41/#60 per-source decision (P4) | Affected values are hidden in every view, including historical and shared views, because showing them is display | Values withheld |
| Mode or optional tier switched | Activation conditions (V5) | Re-evaluate required and cross-component rules; only predicates with actually false applicability become `skipped` | Not evaluated |
| Successor contract published | Available contract version differs from this revision's pinned `schema_version` | Preserve original bytes, locks, reader and historical findings; an explicitly adopted migration creates a new revision under CD-7 | New contract available; Current evaluation unavailable if the new path is unsupported. Original reproducibility changes only if its actual dependencies are missing |
| Withheld input on a fork | SB-8 | Dependent rules `unknown` | Prompt to answer |

When whether a branch is active is itself unknown, invalidate and re-evaluate (V5).

## Compatibility proposals

Status labels: **contract-derived** restates behaviour stated in the v1 docs (V5–V8); **hypothesis** is this note's proposal. These are not approved rules. The bounded historical replay candidate below now exercises selected cross-record checks using synthetic fixtures. Most proposals are integrity checks across records (build vs report vs snapshot) that v1's Ruleset expression language can't address, because its references resolve within one build (V12). Their released placement remains SB-10.

### SB-R1 Selected versions belong to the locked snapshot (contract-derived)

- **Kinds, pointers:** every enabled `Selection` (`/catalog_item_id`, `/catalog_item_version`); `CatalogSnapshot#/items` of `locks.catalog_snapshot_id`.
- **Applies when:** the selection is enabled.
- **Assertion:** an item with the same id and version is in the locked snapshot. V12 states that mismatched versions and broken catalog references return `unknown` for rule operands; this check makes the mismatch itself a finding.
- **Outcome / severity:** absent: `fail`, `error`. Snapshot not retrievable: `unknown`, `error`, `on_unknown: block`.
- **Remediation:** re-pin to a version in the snapshot, or adopt a snapshot that contains it.
- **Examples:** pass: version present. Fail: selection `2026.10` against a snapshot that lists only `2026.09`. Unknown: snapshot id not found.
- **Migration:** needs SB-2's revision lock to be unambiguous.

### SB-R2 Displayed findings belong to this revision and these locks (contract-derived)

- **Pointers:** `EvaluationReport#/build_revision`, `#/catalog_snapshot_id`, `#/ruleset_id`, `#/ruleset_version`, `#/dependency_graph_id`, `#/dependency_graph_revision` against the build's `revision` and `locks`.
- **Assertion:** all equal. V6: the UI accepts diagnostics only when `report.build_revision == current build.revision`, otherwise marks them stale.
- **Outcome / severity:** mismatch: `fail`, `warning` (the report is shown as historical, not current). No report: `unknown`, `warning`, `on_unknown: review` ("Not evaluated").
- **Examples:** pass: report for revision 4 with matching locks. Fail: report for revision 3 shown on revision 4. Unknown: no report.

### SB-R3 Cost is compared only on complete, current quotes (contract-derived)

- **Pointers:** `CostEstimate#/build_revision`, `#/pricebook_id`, `#/currency`, `#/coverage`, `#/period_days`.
- **Applies when:** a budget is set or a cost comparison is requested.
- **Assertion:** the estimate cites this revision and the locked pricebook, coverage is `complete`, and currency matches. V8: stale or partial quotes yield `unknown`, never budget-pass.
- **Outcome / severity:** stale or partial: `unknown`, `warning` for display; the budget rule itself keeps its own severity. Currency mismatch in a comparison: `skipped` with reason "not comparable" (no FX policy).

Both estimates and their component lines may still be shown, labelled with pricebook dates and their qualifications. A non-comparable total is not a reason to hide either estimate or its components.

### SB-R4a Selected components are not deprecated (hypothesis)

- **Pointers:** the selection's item in the current snapshot: `catalog-item.schema.json#/properties/status`.
- **Applies when:** the selected item is present in the current snapshot with a known lifecycle status. Known absence is handled by SB-R4b; unresolved presence/status gives `unknown`, not `skipped`.
- **Assertion:** status is not `deprecated`.
- **Severity:** fixed `warning`; `on_unknown: review`.
- **Outcomes:** `deprecated` gives `fail`; any other known status gives `pass` for this predicate only. A retired item still fails SB-R4b. Unretrievable snapshot or unknown lifecycle gives `unknown`.
- **Remediation:** offer supported replacements; do not swap automatically (V6).

### SB-R4b Selected components remain available (hypothesis)

- **Pointers:** selected item identity and lifecycle in the current snapshot, with evidence of snapshot coverage.
- **Applies when:** a selected component is checked in the current view.
- **Assertion:** the item is present and status is not `retired`.
- **Severity:** fixed `error`; `on_unknown: review`.
- **Outcomes:** `active`, `preview` or `deprecated` gives `pass` for availability only; SB-R4a separately warns on deprecation. `retired`, or absence established by an exhaustive current snapshot for that item/version scope, gives `fail`. An unavailable snapshot, incomplete coverage, or unknown lifecycle gives `unknown`; omission from an incomplete list is not proof of retirement (#40).
- **Remediation:** offer replacements; do not swap automatically. Both predicates affect the current view only; the historical view keeps its original findings.
- **Synthetic cases:** deprecated → SB-R4a `fail/warning`, SB-R4b `pass/error`; retired → `pass/warning`, `fail/error`; unavailable snapshot → both `unknown` with their fixed severities; incomplete snapshot omitting the item → availability `unknown`.
- **Open:** whether `preview` warrants a separate `info` predicate is for #40.

### SB-R5 Withheld inputs leave dependent rules unresolved (hypothesis)

- **Applies when:** a forked build has an input withheld at share time (SB-8).
- **Assertion:** any rule operand that resolves to a withheld input is unresolved, so the rule is `unknown`. A recommendation-only rule follows #81's policy and is `skipped` (P1).
- **Severity:** the dependent rule's own. `on_unknown` per that rule.
- **Example:** a share withholds `data_classification`; on the fork, the rule reading `/objectives/data_classification` (V13) is `unknown`, not `pass`.
- **Dependency:** CD-1's typed answer states; v1's evaluator treats the string `"unknown"` as a known value (P1), so a withheld marker must not be a string sentinel.

## Pricing and capacity

No prices or capacity figures are recorded. Cost snapshots reference #39's `CostEstimate` semantics (V8); historical estimates are kept and labelled with their pricebook's `captured_at`. Whether historical prices may be shown at all depends on each source's applicable #60 display and export decision. The current product decision excludes GPUs.io API retrieval, display and export, including saved/shared build cost views (P8). The paid API and attribution conditions recorded in P4 do not establish eligibility for this product. Reconsider only on a specific permitted-use basis covering this product and a new #39/#41/#60 review.

## Recommendation and rationale

1. Adopt option C: immutable revisions with separate historical and current validity, and derived revisit states.
2. Share by opaque, revocable link to a redacted projection of one revision; apply the sensitivity table to shares and exports alike.
3. Never copy organisation attestations; forks receive withheld inputs as unanswered, evaluated as `unknown`.
4. Compare by (kind, role) with explicit "not comparable" reasons; never sum across currencies, charge bases or one-off/operating scopes.
5. Invalidate on publications and rights decisions, not on elapsed time, until #41 adopts a TTL.
6. Route SB-1 to SB-10 and SB-R1 to SB-R5 to #40 rather than extending v1 locally.

## Structured artifacts

The [CD-7 historical replay manifest](../../tests/fixtures/t0-historical-replay.json)
now binds the existing frozen synthetic build, catalog/pricebook sidecar, exact
ruleset and dependency graph, explicitly supplied resource/cost estimates and
retained report. The [replay implementation and decision](component-schema-compatibility.md#cd-7-historical-reference-replay-candidate-2026-10-18)
provide a bounded engineering candidate for historical SB-R1, SB-R2, SB-3, SB-5 and
SB-10: perform cross-record association checks before the pinned local evaluator,
including exact catalog ID/version/kind for every enabled selection, then
compare the complete reproduced report. Disabled selections remain excluded
from that membership precondition. This does not add user build data
or a catalog proposal.

Original bytes survive every result. Unavailable or mismatched inputs cannot
be replaced by current versions, and explicit optional-estimate absence cannot
select an available estimate. The replay manifest carries the evaluator source
and schema identities without changing frozen reports or setting the build's
`lifecycle` to `validated`. A retained historical report and a demonstrated
reproduction are distinct; an invalid or indeterminate historical result stays
invalid or indeterminate. Source authenticity/use, current evaluation, released
report-version fields, sharing storage and actual successor migration remain
separate decisions. The fixture is synthetic; #42 retains its #40 prerequisite.

## Open decisions (SB-)

| ID | Decision | Accountable | Consulted |
| --- | --- | --- | --- |
| SB-1 | A typed `assumptions` record: presets, defaulted values, unanswered inputs, FX/tax assumptions, each with source | #40 | #81 (CD-1), #39 |
| SB-2 | Lock the catalog snapshot `revision`, or require snapshot ids to be unique per revision | #40 | #41 |
| SB-3 | Link a build revision to its cost snapshot: pricebook `revision` in `locks`, and how the build references its `CostEstimate` | #40 | #39 |
| SB-4 | Visibility as a separate share record (token, access mode, pinned or following revision, created/revoked dates) rather than a build field | #40 | product owner (#42 assignees) |
| SB-5 | Validation state is derived from reports, not stored; meaning of `lifecycle: validated`; recording the evaluator version in reports | #40 | — |
| SB-6 | Fork lineage: source build id and revision on the new build | #40 | — |
| SB-7 | Several workloads sharing one machine (#81 Q7) | #40 | #10, #81 |
| SB-8 | A `withheld` answer state, distinct from `unknown` and `missing`, for shared and forked builds | #40 (with CD-1) | #81 |
| SB-9 | Retention of shared links and revisions: expiry, effect of owner deletion, survival of forks | product owner (#42 assignees) | #41 (data governance) |
| SB-10 | Where cross-record integrity checks (SB-R1 to SB-R3) live: Ruleset, evaluator preconditions or a separate validator | #40 | — |

## Open questions and handoffs

| Handoff | What is asked | Status |
| --- | --- | --- |
| #40 | Accept, narrow or reject SB-1 to SB-8, SB-10 and SB-R1 to SB-R5; confirm the build record mapping | Pending; #42 stays blocked by #40 |
| #41 | Confirm the invalidation table against the interim policy; a future TTL decision would add a time trigger | Confirmed for this scope by @tynamite in [review 5558408384](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/114#pullrequestreview-5558408384); no TTL adopted |
| #39 | Confirm SB-3 and the cost comparison rules (currency, period, charge basis, one-off vs operating) | Pending |
| #37 | A "deploy from saved build" path must use the pinned revision and its own approvals (V8) | Pending |
| #81 (#2/#3) | Q7 answered as SB-7 (open); per-component mode, `/workload`, attestations and the "report from a saved build" pre-fill (P1, deployment-mode.md "Report from a build") consume the share redaction: a pre-filled fit report must take the configuration key only, never withheld inputs | Pending |
| #60 | Confirm that rights changes hide values in historical and shared views | Pending |
| #51 | PCPartPicker save and share flows remain unobserved (P5); this note doesn't rely on them | Informational |

The #41 invalidation-policy handoff above is confirmed. Other receiving-owner dispositions remain pending; #40 routing and the merge of its partial record in #126 do not complete #40 or remove the #42 prerequisite.

## Acceptance criteria coverage

| Criterion | Where | Status |
| --- | --- | --- |
| Build record definition referencing #40 schema | Build record definition | Drafted against v1; gaps routed to #40 |
| Sharing and privacy rules | Sharing; Field sensitivity | Drafted; retention open (SB-9) |
| Comparison semantics with examples | Comparison | Drafted, including required-foundation and optional-tier boundary cases |
| Invalidation triggers (from #41) and user-visible states | Invalidation triggers; Revisit states | Drafted on the interim policy |
| Decision record merged | Proposal sequencing decision | Partial record merged in [#114](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/114); #42 completion remains blocked by #40 |
| Deployment modes covered | Candidate options; Comparison | Covered using #81's merged definitions |
| Comparison fields with type, unit, evidence | Comparison fields | Drafted |
| Rules in #40 format; verified vs hypotheses | Compatibility proposals | Contract-derived vs hypothesis labelled; none reproduced |
| Primary sources with access dates | Evidence | Done for the claims made |
| Handoffs confirmed by owners | Open questions and handoffs | #41 invalidation scope confirmed; other handoffs pending |
| Open questions with named owner | Open decisions | Done |

## Evidence

| ID | Publisher and URL | Access date | Version / region | Evidence grade | Limitations |
| --- | --- | --- | --- | --- | --- |
| V1 | This repo, `contracts/v1/schemas/build.schema.json` (`/properties/locks`, `/objectives`, `/lifecycle`, `/owner_ref`, `/extensions`) | 2026-10-17 | v1 1.0.0 at `f297ac5` | Primary documentation (contract) | — |
| V2 | `contracts/v1/schemas/selection.schema.json` (`/properties/*`, `/$defs/settings_*`) | 2026-10-17 | as V1 | Primary documentation (contract) | — |
| V3 | `contracts/v1/schemas/catalog-snapshot.schema.json`; `catalog-item.schema.json` (`/properties/status`) | 2026-10-17 | as V1 | Primary documentation (contract) | — |
| V4 | `contracts/v1/schemas/common.schema.json` (`/$defs/secret_ref`, `money`, `decimal`) | 2026-10-17 | as V1 | Primary documentation (contract) | — |
| V5 | `contracts/v1/docs/DEPENDENCIES.md`, "Change handling" and activation conditions | 2026-10-17 | as V1 | Primary documentation (contract) | Imported guidance, not an implementation |
| V6 | `contracts/v1/docs/AGENT_PROTOCOL.md` (steps 6–8; "new snapshot/version, never in-place"); `DEPENDENCIES.md` "Required unknown-state handling" | 2026-10-17 | as V1 | Primary documentation (contract) | Archived implementation guidance |
| V7 | `contracts/v1/docs/IMPLEMENTATION_AGENTS.md` item 7 (immutable, reproducible records) | 2026-10-17 | as V1 | Primary documentation (contract) | Archived implementation guidance |
| V8 | `contracts/v1/docs/PRICING_AND_GATES.md` (complete quote; no FX; stale revision reports) | 2026-10-17 | as V1 | Primary documentation (contract) | — |
| V9 | `contracts/v1/schemas/component-registry.json` (`workload`, `deployment_mode`: cardinality `one`) | 2026-10-17 | as V1 | Primary documentation (contract) | — |
| V10 | `evaluation-report.schema.json` (`/properties/findings`), `cost-estimate.schema.json`, `pricebook.schema.json` (rates `valid_from`, `valid_until`) | 2026-10-17 | as V1 | Primary documentation (contract) | — |
| V11 | `contracts/v1/schemas/event.schema.json` (`/properties/type` enum) | 2026-10-17 | as V1 | Primary documentation (contract) | — |
| V12 | `DEPENDENCIES.md`, "Operand types" (references resolve within the build; mismatched versions → `unknown`) | 2026-10-17 | as V1 | Primary documentation (contract) | — |
| V13 | `contracts/v1/baseline/core-ruleset.json` (rules reading `/objectives/data_classification`, `/objectives/region`, `/objectives/monthly_budget_amount`) | 2026-10-17 | as V1 | Primary documentation (contract) | Baseline, not an approved production ruleset |
| X1 | IETF, RFC 9110 HTTP Semantics, §4.1: <https://www.rfc-editor.org/rfc/rfc9110.html> | 2026-10-17; rechecked 2026-10-18 | RFC 9110 | Primary documentation (specification) | Source checked: minimum recommended support is 8000-octet URIs. This is not a maximum. |
| X2 | Dify, app management docs: <https://docs.dify.ai/en/cloud/use-dify/workspace/app-management> | 2026-10-17; rechecked 2026-10-18 | Cloud docs; page last modified 2026-07-29 | Primary documentation | Source checked: export includes app configuration, node settings, model parameters, prompts and knowledge-base connections; excludes third-party tool API keys, knowledge content and logs; Secret-type environment variables may be included by explicit export choice. Warns on importing an older DSL version; no export was executed here |
| X3 | n8n, export and import docs: <https://docs.n8n.io/build/manage-workflows/export-and-import.md> | 2026-10-17; rechecked 2026-10-18 | docs, current | Primary documentation | Source checked: JSON includes credential names and IDs; HTTP Request nodes imported from cURL can contain authentication headers. The documentation calls for removing or anonymising sensitive material before sharing; no export was executed here |
| P1 | PR #81 drafts, `research/T0-configuration/deployment-mode.md` and `workload-use-case.md` at `028a116` | 2026-10-17 | reviewed revision 028a116 | Project decision record (#81 merged) | Read only; adopted definitions, schema changes remain subject to #40; CD-1 to CD-12 are #81's |
| P2 | This note's competitor context: `research/market/competitors/dify.md`, `n8n.md`, `skypilot.md` | 2026-10-17 | accessed by those notes 2026-10-16 | Project research | SkyPilot task YAML as a portable config is noted there; not relied on here |
| P3 | #41 interim policy, PR #75 review: <https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75#pullrequestreview-5550616927> | 2026-10-17 | review of `9e66622`, submitted 2026-10-16 | Project owner position | Not an approved contract; no TTL |
| P4 | #60 decisions, `research/market/rights-validation.md` | 2026-10-17 | terms checked 2026-10-16 | Project decision | Adoption by #41 pending |
| P5 | `research/market/pcpartpicker.md` (H4; requirement 4) | 2026-10-17 | 2026-10-16 | Project research (hypotheses) | PCPartPicker pages not fetched; robots.txt disallows AI agents. Save/share flows unobserved. |
| P6 | `research/T5-training-fine-tuning/README.md` (T5 rules `skipped` when removed) | 2026-10-17 | `main` at `f297ac5` | Project research | — |
| P7 | `prompts/T0.md` Track E on PR #74 (`docs/maintainer-research-prompts`) | 2026-10-17 | unmerged | Project guidance | Guidance, not acceptance |
| P8 | [#60 scoped receiving decision](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/60#issuecomment-6248616771), delivered by [PR #299](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/299); [accepted source-use record](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/3d395801742461aa82ac31a21857ec6f8d0270fb/research/market/rights-validation.md) | 2026-10-18 | Accepted main `3d395801742461aa82ac31a21857ec6f8d0270fb` | Project engineering receiving decision | Current GPUs.io API/display/export exclusion supersedes the historical P4 consumer guidance; no new permission, production integration approval or #42 contract adoption |

Historical review disposition (2026-10-17): #41 confirmed the invalidation-event handoff. #40 has routed SB-1 to SB-10 and SB-R1 to SB-R5 for review; SB-8 is decided together with CD-1 answer states. Routing did not settle those schema decisions, and the PR remained a draft blocked by #40 at that time. The 2026-10-18 sequencing decision above supersedes that proposal-only merge hold; the contract decisions and #42 prerequisite remain open.
