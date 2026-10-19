# T0: Saved, Shared & Compared Builds

Issue: #42 · Contract: v1 1.0.0 (adopted in PR #44; inspected at `f297ac5`) · Kinds: `BuildSnapshot`, `Selection`, `CatalogSnapshot` (with `EvaluationReport`, `CostEstimate`, `Pricebook`, `Ruleset`, `DependencyGraph`, `Event` as referenced records)
Status: research decision record delivered; dated current receiving decisions and their coordinating sufficiency assessment are recorded below (P24–P28), separately from the earlier named requests and final delivery checks · Last researched: 2026-10-19 · Guidance: PR #74 Track E (P7)
Deliverable path: `research/T0-configuration/saved-shared-builds.md`

Labels used in this note:
- **V** IDs cite the v1 contract in this repository; **X** IDs cite external primary sources; **P** IDs cite project decisions and drafts.
- **SB-n** IDs retain this note's research decisions and remaining integration questions, routed to #40 unless stated. They are separate from #81's CD-1 to CD-12, which this note references but does not renumber, extend or settle.
- **SB-Rn** IDs retain the original rule proposals. P22 records reception of their dated common-format research companion; no executable successor ruleset is released.
- **Proposal:** a design choice made in this note, not a sourced fact.
- "Source checked" means the claim was compared with the cited source on its access date. The separately labelled synthetic historical-replay experiments exercise their exact supported profiles; they do not establish independently measured vendor behavior or upgrade documentary claims to reproduced evidence (P3, P9).

## Proposal sequencing decision — 2026-10-18 (historical state)

The 2026-10-18 sequencing decision allowed this partial design record to proceed through ordinary PR review and merge while the contract prerequisite was open, giving #40 and the other receiving issues concrete semantics to review. Publishing the proposal does not adopt SB or CD field shapes, release a successor contract, activate a consumer, or supply pending receiving-owner acceptance. At that decision, #40 and #42 remained open and #42 retained its #40 prerequisite. The earlier draft-hold reviews remain historical records; the decision changed only the order in which the partial proposal could merge, not the issues' completion requirements. P21 records the later actual completion of #40; P22 and P23 separately record this note's later central intake and reviewed delivery.

The sequencing change is recorded at [f56b0fc](https://github.com/Pick-Your-AI/pick-your-ai-research/commit/f56b0fcdb34d91e1751edc3b4cd44dba9bc04960), with independent reviews [5561898533](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/114#pullrequestreview-5561898533) and [5561921315](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/114#pullrequestreview-5561921315) submitted before [squash merge 649f5870](https://github.com/Pick-Your-AI/pick-your-ai-research/commit/649f5870e9729ec1aaf1b5f07e9290ce0f777833). These reviews concern publication of this partial record and retain the receiving-owner gates; they do not replace the earlier revision-specific reviews or the scoped #41 receipt.

## Summary

- **A saved build is an immutable `BuildSnapshot` revision plus the derived records that cite that revision.** Every edit creates a new revision (V5); old revisions remain distinct where retention is permitted, subject to the unresolved SB-9 policy. The v1 locks already pin the catalog snapshot, ruleset version and dependency graph revision (V1).
- **Two validity views, never merged.** *Historical validity* is the `EvaluationReport` produced under the build's own locks. *Current validity* is a fresh evaluation of the same selections against the currently published catalog snapshot, ruleset and pricebook. A revisit offers the permitted historical view and, when the required eligible inputs and supported reader exist, a separately identified current candidate with per-rule differences. Neither overwrites the other, and nothing in the user's selections changes without consent (V5, V6).
- **Sharing stores the build server-side behind an opaque link and shares a redacted projection.** Credentials references, endpoints, free text, budgets, residency, data classification and organisation attestations are withheld by default. A recipient who forks receives withheld inputs as unanswered and supplies its own applicable answers; the new evaluation follows the existing missing-input, applicability and SB-R5 behavior.
- **Comparisons align selections by kind and role and show "not comparable" with the reason** when currency, pricing period, workload, ruleset version, evidence protocol or cost coverage differ. Modes are compared per serving component using #81's merged definitions (P1).
- **A new release or elapsed time alone does not invalidate an immutable selected snapshot.** Under the #41 interim policy, version-pinned facts don't expire and current-state facts are shown "as of" their access date with no arbitrary TTL (P3). Publications can prompt a separate current evaluation; selected-input changes, source corrections or retractions, explicit validity conditions, rights decisions and build edits retain their specific effects. Historical reproducibility, current recommendation eligibility and permission to disclose are separate questions in the accepted H41-42 receiving scope (P9).
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

All four modes appear in the comparison semantics. Mode is the operator-plus-capacity classification of each serving component under the received [classification test](deployment-mode.md#the-classification-test). If any required component's mode is unresolved, the aggregate is `unknown`. Otherwise, it has their common mode when all agree and is `hybrid` when they do not all agree (P1, P12, P18). v1 instead has one `deployment_mode` selection with `cardinality: one` (V9). The accepted #3 → #42 receipt (P12) supplies the researched per-component definition. Versioned representation and migration remain with #40/CD-7; the definition is not an undecided mode choice or a new frozen-v1 field.

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
| per-component mode | — (`deployment_mode` selection, cardinality one, V9) | Research definition received (P12); CD-7 wire/migration separate | Not an SB decision |
| several workloads on one machine | — (`workload` cardinality one, V9) | **Gap: SB-7** | #81 Q7 handoff |

### What makes a build reproducible (Proposal)

Re-evaluation of (build id, revision) yields the same findings when all of these are pinned and retrievable: every selection's `catalog_item_id` + `catalog_item_version`, its settings and links, the build inputs, the catalog snapshot (id and revision, SB-2), the ruleset id + version, the dependency graph id + revision, the pricebook id + revision (SB-3), the evaluator version (SB-5), and any external evidence the rules consumed, such as resource estimates, pinned by their own versions (V7). If a required replay input is unavailable, reproduction cannot be claimed. A permitted historical projection may remain available with a permitted explanation of the missing prerequisite; the explanation must not reveal a private locator or an excluded value. Applicable rights restrictions still govern historical and shared views (P8, P9). Retaining inputs and actually demonstrating reproduction remain distinct.

### Derived records

A saved revision is the root of: its `EvaluationReport`s, `CostEstimate`s, `ResourceEstimate`s and any `DeploymentManifest`. Association requires this exact `build_id` and `build_revision`, together with each record's required lock/selection identities. Another build's numerically equal revision is not a match. Earlier-revision evidence is historical and cannot satisfy the current revision's gates (V6, V8).

## Save, share and compare semantics

### Save and revisit (Proposal)

1. Every change persists a new immutable revision under compare-and-swap (V5). "Save" names a revision; it doesn't freeze the build.
2. On revisit, show the permitted projection of the correctly associated historical report for that revision's locks.
3. Offer a current report for the same selections against separately identified published snapshot, ruleset, graph and pricebook inputs. Compute it only when the required inputs are eligible and its reader/migration path is supported; otherwise show the qualified current-view limitation below. This is a candidate, not a revision. It doesn't change the saved build. A candidate using different lock inputs is not evidence for the saved revision and cannot satisfy its gates. Any later accepted revision must carry its own matching locks and associated evidence.
4. Show the differences per `rule_id`: outcome (`pass`/`fail`/`unknown`/`skipped`) and severity (`info`/`warning`/`error`) side by side, with the rule message, remediation and evidence path (V10). Price differences show both pricebooks' "as of" dates.
5. The user can adopt the current locks, which creates a new revision. Replacements for retired components are offered, never applied automatically (V6).

### Revisit states shown to the user (Proposal; storage is SB-5)

States are derived on read, not stored. More than one can apply.

| State | Condition | What the viewer sees |
| --- | --- | --- |
| Published references unchanged | The compared publication identities equal the saved locks, and the retained report has this exact Build ID/revision and required lock associations | Permitted historical result with its original dates, plus the actual comparison's as-of date/time and time zone, tied to the identities compared. If its timestamp is unavailable, say so; never substitute the display time, publication date or pricebook capture date. Reference equality establishes neither current eligibility, successful reproduction nor disclosure permission and refreshes no source-access date |
| Report unavailable or unassociated | No report is resolved for this exact Build ID/revision and its required lock associations | Evaluation for this revision is not established. Preserve any original report with its actual association/availability explanation; do not infer that no historical evaluation occurred |
| Newer data available | A newer catalog snapshot, ruleset version, graph revision or pricebook exists | Permitted historical result with its lock dates; offer a separately qualified current candidate, or explain why that evaluation is unavailable |
| Result changed | Current findings differ from historical findings for any rule | The per-rule diff; changes to `fail` or `unknown` listed first |
| Now indeterminate | A historical `pass` is `unknown` in the current report | "Can no longer be confirmed", with the missing evidence |
| Now valid | A historical `fail` is `pass` in the current report | "This now passes under ruleset <version>"; the historical failure stays visible |
| Component deprecated | The selected item's applicable lifecycle evidence says `deprecated` | SB-R4a `fail/warning`; SB-R4b still passes availability. Offer a replacement without claiming the item is unavailable |
| Component unavailable | The selected item is `retired`, or an exhaustive current snapshot establishes absence for its exact item/version scope | SB-R4b `fail/error`, with the evidence scope |
| Availability unknown | Snapshot retrieval, lifecycle evidence or item/version coverage is unresolved | SB-R4b `unknown/error`, not an unavailable claim; omission from an incomplete list proves no retirement |
| Prices as of | Always for current-state facts | "Prices as of <captured_at>". A newer pricebook or a rate past `valid_until` makes the old estimate historical, not current |
| Values withheld | A #60 decision removes display rights, or a share withheld an input | Only independently permitted historical outcomes or other content; a generic withholding notice when the outcome, association or reason would itself disclose restricted information |
| Cannot be reproduced | A required pinned record is missing | Permitted historical projection with a permitted explanation of the unavailable prerequisite |
| New contract available | A successor contract is published while this revision still pins its original schema | Preserve the original bytes, historical findings and reproducibility under the retained reader; offer an explicit migration as a new revision |
| Current evaluation unavailable | The proposed current evaluation needs an unsupported contract/ruleset or an unavailable migration | Show the historical result with its original version and explain the unavailable current path; do not mark the historical result irreproducible solely because a successor exists |

`EvaluationReport.result = valid` means the configured rules passed for the locked revision, not production readiness (V6). Shares say so.

**Synthetic boundary examples (proposal, no runtime measured):** an item marked `deprecated` remains available with a warning; an item omitted from a non-exhaustive snapshot has unknown availability. A v1 revision with all original records and its v1 evaluator retained remains reproducible after a v1.1 publication. If the v1.1 migration is unavailable, only the proposed current view is unavailable. If the original pinned evaluator or a required record is actually lost, a permitted historical projection can remain visible but its reproducibility is qualified with that specific missing dependency. These cases follow SB-R4a/SB-R4b and #40's [CD-7 migration boundary](component-schema-compatibility.md#contract-versions-and-migration-cd-7-proposal); they do not release a successor contract.

### Sharing (Proposal)

| Aspect | Decision |
| --- | --- |
| What a link points to | One immutable revision by default. An owner may choose "follow latest revision"; the viewer is told which. |
| Access modes | `private` (owner only); `unlisted` (anyone with the token); `public` (listed and discoverable). Organisation-scoped sharing needs accounts and is out of scope. Mode is a property of the share, not of the build, so changing it doesn't create a build revision (SB-4). |
| Read-only vs fork | Every share is read-only. Fork creates a new build id at revision 1 with a lineage pointer to the source (id, revision) (SB-6). Withheld inputs arrive unanswered; attestations are never copied. |
| Revocation | Revoking a token stops future access through that token. It does not prove physical deletion or erase already exported copies or independently permitted forks; the lifecycle boundaries below apply. |
| What the viewer sees | Permitted projections of both validity views and their dates; permitted withholding notices rather than private field names or values |
| Retention | Lifecycle proposal below is proposed for the #42 owners (P19). Concrete periods and deletion-completion choices in P20 remain an unadopted proposal. No retention default or hosted completion promise is adopted. |

### Retention and access lifecycle (SB-9: proposed for the #42 owners, 2026-10-19)

The lifecycle distinctions below are proposed for #42's owners, @tynamite and
@appletechie, pending their disposition as requested in the co-owner review
(P19). They separate the events whose concrete policies must be considered
before a hosted service promises permanence, expiry or deletion. They are
research design proposals, not observed storage behavior, adopted durations or
a new source licence. This proposal status does not waive the existing
complete-projection restrictions, forbidden forked values or source-use limits.

| Event or artifact class | Proposed research behavior | Remaining policy/evidence |
| --- | --- | --- |
| Share expiry or revocation | Stop future access through the expired/revoked token. Never recycle it for another target. While active, a deliberately following share retains its disclosed revision policy. | Actual expiry duration, token/revocation-record lifetime and enforcement implementation |
| Owner deletion | Stop serving the owner's deleted revisions and associated shares. A deletion request, access denial and completed physical purge are distinct events. | Completion deadline, backups/residual copies, any independently applicable retention basis and evidence of actual purge |
| Retained payload, token, audit and lineage records | Apply a separate purpose and permitted retention policy to each class. A revocation marker need not retain the full private payload, and its identities or associations can themselves be restricted. | Concrete durations, triggers, access and deletion policy for each class |
| Independent fork | Keep its new Build ID/revision and own lifecycle. Origin deletion does not automatically erase independently permitted fork content; source identity or token possession supplies no continuing permission. An applicable #60 denial immediately excludes the affected material and disclosing derived assertions from every served view, including a fork's historical/shared view; continued display cannot await a purge or another qualification review. Private attestations and withheld values never transfer. | Physical purge, any permitted retained original and lineage handling are separately qualified after the relevant rights or deletion event; no guarantee of perpetual fork survival or adopted duration (P29) |
| External export | Explain the limits of control over a copy already delivered. Revoking a hosted link neither recalls that file nor creates a new right to retain or redistribute it. | The actual recipient/use conditions; no promise of remotely erasing an uncontrolled copy |
| Replay prerequisite becomes unavailable or unusable | Retain only permitted history and qualify the missing prerequisite. Some prerequisites prevent evaluator execution entirely. Never substitute latest inputs, relabel a partial projection as the original artifact, or rewrite a historical outcome. | Whether each original input remains available, usable and permitted under its actual profile |

**Accountable follow-up:** #42's existing assignees, @tynamite and @appletechie,
with #41 for source/data governance and #40 for versioned representation.
Before a hosted retention promise is made, choose the periods and triggers for
the distinct classes, deletion-completion and residual-copy policy, and
permitted fork/lineage survival. This records the remaining research question;
it neither requires implementing accounts/storage in #42 nor implies an
indefinite default. Absence of an arbitrary source-freshness TTL is not a grant
to store or disclose material forever.

P20 records @tynamite's concrete artifact-class duration and deletion proposal
of 2026-10-19. Its stated end-of-day 2026-10-23 UTC objection deadline is the
proposer's process, not an acceptance receipt. The numeric table remains in that
linked proposal; this amendment adopts none of its periods or promises. An
actual owner disposition and the proposal's #41 data-governance review, with
legal review where a legal basis applies, must precede a hosted commitment.
Those operating-policy follow-ups are not a blanket new prerequisite for
publishing this partial research note.

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
| #81 `hardware.devices[]` model names and memory | Origin configuration | Included as the origin's configuration; never copied as the reporter's actual device or placement | #81 already excludes serial numbers and hostnames (P1); a fit report needs its own applicable run identity (P18) |
| #81 CD-12 organisation attestations (establishment jurisdiction, EU market placement, lawful basis, revenue, MAU), `licence_answers` (with `grant_ref`), zero-retention or account approvals in `data_terms` conditions | Organisation attestation | Never, and never copied on fork | An attestation is made by one organisation about itself; it can't transfer to the recipient |
| Origin-specific private, dedicated or reserved capacity arrangements | Account-specific capacity | Any independently eligible display is labelled as the origin's fact; the fork's capacity is unanswered and its component mode is `unknown` until the recipient establishes its own | Published offering terms can fix operator and capacity for that offering/scope; merely offering a dedicated option does not establish an account's selection (P18) |
| Private training/run lineage and adapter configuration, including origin-supplied proposed `base_model_revision`, adapter rank, targets and configuration evidence | Private training provenance | Never, and never copied on fork | This class concerns the origin's private job/artifact evidence. Separately eligible published catalog facts retain their own classification; they do not prove which base or settings a private job used |
| Dataset, training-job and lineage-record locators supplied by the origin, including private paths, object locations and account-scoped artifact identifiers | Private data/artifact access identifier | Never, and never copied on fork | A separately eligible catalog source ID is not the origin's dataset location or access grant; do not place a withheld locator in a label, link, finding or derived summary |
| Dataset/source-scoped consent, rights, privacy or documentary attestations and their private condition/grant references | Private scoped attestation | Never, and never copied on fork | The recipient needs its own applicable, correctly scoped evidence. A D-01 document URI or inherited origin answer establishes neither applicability nor satisfaction |
| Established origin-account availability of a provider-held fine-tune | Account-specific artifact availability | Any independently eligible display remains the origin's fact; fork availability is unresolved until the recipient establishes its own exact artifact/account/operation association | Capacity and artifact access are separate. Neither an `api_only` label nor a provider name proves universal account lock, export prohibition or recipient eligibility |
| #81 `destinations[].host`, `external_connections` | Infrastructure | Included without hosts | Mode and residency findings stay explainable |
| Engine/launch settings beyond the eligible IDs/pins above; decoding method, KV-cache precision and admission limits | Unclassified fit-run settings | Withheld from origin prefill; the harness records actual-run settings it can detect under the applicable evidence profile | Detection supplies no disclosure permission; missing applicable essential CD-3 keys leave a report unqualified (P18) |
| Reporter device, OS, driver and NUMA/placement | Actual run identity | Obtain from the recipient's actual run detection or confirmation where its profile permits; do not copy the origin's hardware record | Distinguish selected target, detected facts and recipient declarations; unknown provider hardware cannot be replaced by the API client's device (P18) |
| Fit-protocol workload lengths, concurrency and arrival process | Actual protocol/run evidence | Obtain from the actual executed protocol and run evidence, with independent view/purpose eligibility; never prefill from the origin's business-volume inputs | Configured protocol inputs and observations retain their different meanings (P18) |
| Catalog workload preset | Preset reference and assumption provenance | Transfer only the exact eligible preset reference, labelled assumed; user-entered values retain their opt-in class | No latest fallback, expansion of withheld fields or default represented as a recipient answer (P18) |
| Report findings, evidence, results and summaries; estimate lines, assumptions and warnings; projection/export metadata | Derived | Only where the field's contents and derived meaning are eligible for this view | Restrictions apply beyond `observed`; text, outcomes, associations and aggregates can disclose an excluded input or restricted assertion |
| Catalog-sourced values (prices, benchmark figures) in findings or cost lines | Third-party data | Only where the applicable #60 decision permits the actual material and intended display or redistribution use, with its conditions (P8, P15) | A public share is display; an export does not inherit display-only permission. |

The account-capacity rule follows the same scope distinction as organisation
attestations. A selected offering whose eligible published terms fix both its
operator and capacity, such as a shared API in that exact scope, can supply
eligible offering-level facts for the recipient's established selection of
that exact offering. This does not transfer the origin account's provisioning,
capacity result or entitlement. A list of available capacity options does not
prove which arrangement an account selected. An origin-specific arrangement
remains the origin's fact; its recipient must supply their own capacity before
that component's mode can become known. Neither route transfers a private
attestation, licence answer, grant reference or zero-retention approval (P18).

### Training lineage and recipient artifact availability (response to P29)

This clarification applies the disclosure boundary to the T5 interface; it does
not add fields to frozen v1. The [Fine-tuned Model participant bindings and
A-05/A-11/A-15 interpretations](../T5-training-fine-tuning/fine-tuned-model.md#participant-role-and-evidence-bindings)
distinguish the artifact, its actual served base, original training lineage and
selected account/operation. The [Dataset D-01 interpretation](../T5-training-fine-tuning/training-dataset.md#d-01-the-qualified-c2c3-documentary-requirements)
and CD-12 keep each responsible assessment's actual subject, revision, purpose,
period and attribution. This note selects disclosure treatment for those inputs;
it supplies no new technical or legal assessment.

**Fork lineage and model lineage are different.** SB-6's source Build ID/revision
records the fork relationship only. It cannot establish the trained artifact's
base revision, configuration, dataset or original job. Retain any permitted
original lineage evidence in its separately controlled source record. Do not
copy private evidence through a share/export/fork or replace it with a later
resolved base, the catalog record version, an assumed default or an empty
complete inventory. A separately eligible public catalog fact can describe
that catalog item; it does not bind the origin's private job to the item.

For a private user-trained artifact without an existing valid catalog
association, the missing artifact/base-lineage representation remains an
explicit SB-1/#40 integration question. Do not fabricate a CatalogItem, catalog
ID or version, or hide private lineage in a name, free-text field or unreviewed
extension to make the frozen Build appear complete. P10/P11's accepted
provided-value attribution is the research basis for separately labelled
assumptions and origin facts; the exact released projection mapping still needs
its own versioned integration. No new answer state or frozen wire field is
selected here.

A recipient's **new evaluation** follows the selected concern's actual
applicability and evidence, including the T5 common known-failure precedence:

| Concern | Result of the recipient's actual evidence boundary |
| --- | --- |
| A-05 base association | An applicable separate adapter/base association with unresolved required identity or revision remains `unknown / error` when no eligible known violation is established. A qualified base mismatch remains `fail / error`, even if another operand is unavailable. An evidenced full artifact with no separate served adapter/base association can be `skipped / error` for this concern only. |
| A-15 immutable original lineage | Required original base-lineage evidence withheld or otherwise unavailable leaves the concern `unknown / error` when no eligible known violation remains. A qualified violation of the immutable-pin requirement remains `fail / error`; evidenced non-applicability is `skipped / error`. A later name resolution cannot repair the original job's missing pin. |
| A-11 access/export requirement | Qualify the recipient's exact artifact, account, intended operation and destination. An established exclusive endpoint-only artifact fails an applicable portable-weight requirement; undocumented export stays unknown. An evidenced endpoint-only requirement can make that export concern non-applicable without proving recipient access or deployment readiness. |

These are reasoned disclosure/interface examples, not executed rules or actual
artifact findings. T5's proposed `on_unknown: review` and each fixed severity
remain distinct from the independent frozen blocking rules. Withheld adapter
rank concerns A-04's actual operands; it is not itself proof of an A-05 or A-15
lineage failure. Known non-applicability is not inferred merely because a share
omits evidence. Historical findings retain their original meanings and exact
associations; disclosure redaction cannot relabel them as this new evaluation.

An origin-account capacity answer does not establish who may use its trained
artifact. Retain the recipient's unresolved availability independently of its
component mode, and obtain the recipient's own applicable access and provenance
evidence without copying an origin approval. An eligible published offering
description is not an origin account's artifact entitlement. Complete-projection
review also covers any outcome, association or count that would disclose one of
the private T5 inputs above.

### Disclosure across complete projections (proposal, 2026-10-18)

The sensitivity table applies to the complete historical, shared or exported
projection. Removing an `observed` value alone is insufficient if a finding's
`code`, `message`, `remediation`, `selection_ids`, evidence `path`, `expected` or
`source_version` still discloses the same excluded information. The same review
applies to report outcomes, `result`, `deployment_readiness` and summary counts,
and to estimate quantities, amounts, assumptions, warnings and identifiers
(field locations: V10). The restriction covers a derived assertion as well as a
verbatim copy. An included configuration field is not an unrestricted channel
for private identifiers or free text.

**Proposed boundary:** release only fields whose contents and meaning have been
reviewed as eligible for that projection. Unclassified extensions, new fields
and unreviewed nested content remain withheld until that projection's disclosure
mapping is reviewed. An opt-in input group does not authorize secret locators,
organisation attestations or excluded third-party data. If a finding's outcome
or association itself discloses restricted information, withhold that finding
with a generic notice; do not merely remove its evidence value. Historical
outcomes whose disclosure is permitted retain their original meaning. Do not
turn a historical `pass` into `unknown` to represent redaction.

A projected subset must be labelled as incomplete. Original report-level
results or counts may accompany it only when separately eligible for disclosure,
and must be identified as the original report's summary, not a summary of the
visible subset. Otherwise withhold them too. Do not recompute the subset and
present it as the producer's complete result, complete coverage or a new
evaluation. A generic notice must itself avoid revealing a private identifier,
excluded value or restricted assertion. Use a notice for the projection rather
than one placeholder per hidden finding if placeholders would reveal a
restricted count or association.

Where retention remains permitted, the original artifact remains separate from
the served projection. Redaction does not rewrite its historical findings or
establish complete deletion, and retained bytes do not grant disclosure rights.
The redacted serialization must not be presented as an unchanged, schema-valid
original report or inherit its byte binding, signature or evidence qualification.
A released projection/withheld representation remains a #40 decision under
SB-4, SB-5, SB-8 and SB-10. Applicable withdrawal and deletion requirements remain
in force; this proposal grants no unlimited retention and leaves SB-9 open.

**Synthetic review cases, not executed redactor tests:** a hidden workload count
repeated in a finding message is still excluded; a warning or cost quantity that
reveals a withheld budget must also be withheld. An organisation-attestation
finding may require withholding its code/outcome and an affected summary, even
with empty evidence. A separately permitted catalog compatibility outcome may
remain visible despite another withheld finding. In each case the permitted
historical record and a recipient's new evaluation retain different identities.
These examples describe the proposal; they do not qualify an implemented
redactor, source-use permission or a successor wire format.

**Withheld remains distinct from unknown (SB-8).** A viewer may see the historical findings the owner's inputs produced only to the extent their disclosure is permitted under the boundary above. A fork has no value for withheld inputs. Its new evaluation applies the existing missing-input and applicability behavior, including SB-R5's recommendation-only behavior, and prompts the recipient for applicable answers. Withholding supplies no affirmative evidence of a pass and authorizes no default. The historical projection is not the fork's new evaluation.

### Report-from-build prefill and actual run identity (research interface, P18)

A report-from-build action may start with only the configuration references
already classified as eligible for that view and purpose. It must not expand
unclassified settings into prefill. For the fit key's remaining engine/launch,
decoding, KV-cache precision and admission settings, the harness records
actual-run facts it can detect; it does not promise visibility into opaque
provider internals. A missing essential key required by the
applicable CD-3 profile leaves the report unqualified; a default or the
origin's setting cannot repair it. A profile that does not require opaque
provider hardware does not gain an invented hardware prerequisite.

The reporter's device, OS, driver and NUMA/placement describe their actual
run, using detection or recipient confirmation only where the applicable
evidence profile permits. Permitted origin hardware remains labelled as origin
configuration, never proof of the reporter's environment. The selected target,
detected facts and recipient declarations retain their distinct provenance.
If the actual run differs from an eligible pinned target, keep both identities
and the mismatch; confirmation or successful execution alone does not prove a
match. The API client's hardware is not evidence of the provider's hardware.
Detection itself neither proves qualified measurement nor grants disclosure
permission for launch secrets, host identifiers, excluded content or revealing
derived assertions; the complete-projection policy still applies.

Lengths, concurrency and arrival process come from the actual protocol run and
its evidence, never from copied Build workload inputs in an opt-in business-volume
group. Label configured protocol inputs separately from observed run facts.
Any submitted fit report is separate EV-1 evidence with its own actual identity
and qualification; it edits neither the saved revision nor its original
EvaluationReport. Report submission itself grants no consent, community
admission or licence. Any performance statement is limited to the evidence
actually obtained and its qualification. Eligible training
services and rented compute remain visible as destinations without private
hosts; withholding a host neither removes the destination nor fabricates an
essential placement key.

On fork, a catalog workload preset transfers only as its exact eligible preset
reference, labelled assumed, with its source and meaning qualified. If that
pinned preset is unavailable, record the limitation without resolving latest.
Do not expand the preset to recover withheld values or present a default,
including a default zero, as the recipient's answer. User-entered values follow
their opt-in disclosure class. "Assumed" describes provenance/presentation; it
is not a new frozen answer state. Omitted, unknown, withheld, not applicable and
a real supplied zero retain their distinct meanings.

One primary workload remains the present scope; comparison proves no combined
residency fit. A recipient supplies its own applicable inputs and is evaluated
under the relevant rule policy. In particular, a withheld activating memory
need skips W-R11's recommendation; a known session or persistent need with a
withheld implementation declaration remains unknown, fixed warning / defer.
No generic prefill rule overrides that distinction or rewrites a historical
outcome.

### Comparison (Proposal)

Builds, or revisions of one build, are aligned per selection by (`kind`, `role`). A kind present in one build and absent in the other is displayed as "not selected". Only predicates whose applicability is false for an optional or disabled branch are `skipped`; required-presence and cross-component predicates still evaluate. Comparison presentation never rewrites evaluator outcomes. Absence is never zero cost or a pass.

For example, `rule.required.foundation` always applies: a build missing its primary model retains its foundation failure in the comparison. In contrast, an absent optional T5 tier skips its adapter/training-only predicates when their applicability is false (P6); it does not skip unrelated foundation or cross-component checks.

**Comparison fields**

| Field | Type and unit | Source | Comparable when | Evidence requirement |
| --- | --- | --- | --- | --- |
| Selection per (kind, role) | `catalog_item_id` + `catalog_item_version` | `Selection` | Always | Pinned snapshot |
| Mode per serving component | enum `api`, `managed`, `self_hosted`, `unknown`; build: plus `hybrid` | Per-component operator-plus-capacity [classification test](deployment-mode.md#the-classification-test), received in P12 and named reverse review P18 | Compare eligible classifications; `unknown` if any required component mode is unresolved; otherwise their common mode when all agree, or `hybrid` when they do not all agree | Evidence for the actual offering/account scope; historical v1 `deployment_mode` does not supply component mode, and billing belongs only to cost comparison |
| Compatibility result | `EvaluationReport.result` enum, plus counts from `summary` | `EvaluationReport` | Both reports use the same ruleset id and version; otherwise offer a separately qualified current evaluation | Each report matches the compared Build ID/revision and its required locks; a different-lock candidate is separate evidence |
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

Future lean: (b), because co-resident memory can only be checked where all resident components are known together. The present research choice remains one primary workload per build (P12). Multi-workload/co-residency representation remains SB-7 for #40 with #10; comparing separate builds proves no combined residency fit.

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
| Withheld input on a fork | SB-8 | New evaluation follows existing missing-input and applicability behavior, including SB-R5 | Prompt to answer |

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

- **Pointers:** `EvaluationReport#/build_id`, `#/build_revision`, `#/catalog_snapshot_id`, `#/ruleset_id`, `#/ruleset_version`, `#/dependency_graph_id`, `#/dependency_graph_revision` against the build's `id`, `revision` and `locks`.
- **Assertion:** all required identities equal. Another build's numerically equal revision is not a match; exact Build ID/revision and required locks govern association (V6, V8).
- **Outcome / severity:** known mismatch: `fail`, `warning`; retain the original record with its actual foreign-build, revision or lock identity, never as this revision's result. A missing report or unresolved required association is `unknown`, `warning`, `on_unknown: review`. A known mismatch remains a failure alongside an unrelated unknown; this review policy does not satisfy separate deployment gates.
- **Examples:** pass: Build B revision 4 with matching locks. Fail: Build B revision 3, or Build C revision 4, presented as B revision 4. Unknown: a required report or association pin is unavailable.

### SB-R3 Cost is compared only on complete, current quotes (contract-derived)

- **Pointers:** `CostEstimate#/build_id`, `#/build_revision`, `#/pricebook_id`, `#/currency`, `#/coverage`, `#/period_days`.
- **Applies when:** a budget is set or a cost comparison is requested.
- **Assertion:** the estimate cites this exact Build ID/revision and the locked pricebook, coverage is `complete`, and currency matches. For comparisons, apply this binding independently to each side; compared builds need not share an identity. V8: stale or partial quotes yield `unknown`, never budget-pass.
- **Outcome / severity:** stale or partial: `unknown`, `warning` for display; the budget rule itself keeps its own severity. Currency mismatch in a comparison: `skipped` with reason "not comparable" (no FX policy).

Both estimates and their component lines may still be shown where disclosure is independently permitted, labelled with pricebook dates and their qualifications. A non-comparable total alone is not a reason to hide either estimate or its components. The proposed comparison disposition does not rewrite a retained evaluator finding or transfer a historical budget pass to a current candidate.

Historical compatibility replay consumes the exact retained cost estimate; it does not recalculate rates or amounts. A separate cost-recomputation claim needs the original quantities, rate inputs applicable to that calculation's time and scope, and applicable calculation, allocation, aggregation and rounding-policy identities. Missing that basis prevents that claim even when a cost/report association remains checkable. The #39 intake (P13) accepts this distinction. Its still-proposed FX, default currency/region and presentation choices do not enable conversion or supply invented values in frozen v1.

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
- **Assertion:** any rule operand that resolves to a withheld input is unresolved. A fork's new evaluation follows the dependent rule's own applicability, assertion and unknown policy. Recommendation-only rules skip when their activating need is unresolved; withholding an assertion operand does not itself skip an applicable recommendation. Under the [W-R11 continuation in #401](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/401), a withheld memory need skips the recommendation, but a known `session` or `persistent` need with a withheld implementation declaration gives `unknown`, with fixed `warning`/`defer`. Historical P1 records, retained reader profiles and original findings keep their own revisions and semantics.
- **Severity:** the dependent rule's own. `on_unknown` per that rule.
- **Example:** a share withholds `data_classification`; on the fork, the rule reading `/objectives/data_classification` (V13) is `unknown`, not `pass`.
- **Dependency:** CD-1's typed answer states; v1's evaluator treats the string `"unknown"` as a known value (P1), so a withheld marker must not be a string sentinel.

## Common-format companion for SB-R1–SB-R5

**Status:** research proposal for #40 review. **Research revision:** 2026-10-19,
companion draft 1. This maps the existing rules to the actual
[rule proposal template](../../templates/rule-proposal.md) and the central
[rule format and outcome semantics](component-schema-compatibility.md#rule-format-and-outcome-semantics-decided).
It introduces no new wire fields, selectors, frozen-profile changes or released
ruleset. References to a rule's existing pointers incorporate its literal list.
The original rule text, identifiers and evidence labels remain above.

Where an original rule leaves applicability or an outcome unspecified, this
companion proposes a completion for central disposition; it is not a claim
that the completion is already frozen-contract behavior. In particular,
SB-R3's binding-failure finding and review policy below are research proposals.
The original contract-derived labels identify their source basis, not
independent vendor verification or acceptance of every proposed completion.

SB-R1, SB-R2, SB-R3, SB-R4a and SB-R4b each keep one fixed severity.
**SB-R5 is the shared withheld-operand policy consumed by specific rules. It
does not emit a separate finding with a severity that varies by consumer.**

### Participants, applicability and assertions

| ID | Participants, roles and pointers | Applicability | Single assertion and supporting evidence | Fixed severity and unknown policy |
| --- | --- | --- | --- | --- |
| SB-R1 | The Build supplies its locked catalog reference; each enabled Selection supplies the selected item ID/version; the exact locked CatalogSnapshot supplies membership evidence. Use the original SB-R1 selection, lock and membership pointers. | Each enabled Selection whose membership in the locked snapshot is evaluated. Disabled selections skip. | The selected ID/version is present in that exact locked snapshot. Identify the resolved snapshot and matching entry, or establish absence within that snapshot. Membership does not establish a capability or permission. | error. Known absence fails. An unavailable or unresolved required snapshot gives unknown; on_unknown: block. |
| SB-R2 | The Build supplies its id, revision and existing locks. The EvaluationReport supplies the original SB-R2 build_id, build_revision and required report-association pointers. | A view or receiving operation proposes to use a report as the result for a specified Build revision. A requested but unresolved report remains applicable. No report display/use requested: this display assessment skips, without waiving another consumer's mandatory report prerequisite. | Every required report association matches this exact Build ID, revision and locks. Record the actual compared identities and unresolved prerequisites. | warning. A proven mismatch fails; in its absence, a missing report or unresolved required association gives unknown; on_unknown: review. Retain an unrelated missing prerequisite as supporting detail or a separately scoped assessment, without erasing a proven mismatch. |
| SB-R3 | Each Build supplies its own id/revision, lock and applicable budget/context. Each CostEstimate supplies its original SB-R3 build_id, build_revision, pricebook_id, currency, coverage and period_days pointers. Identify the stated operation, its time/scope and currency counterpart. Each estimate binds independently to its own Build. | A budget assessment or cost comparison is requested. Assess each estimate for its own stated operation; neither requested: skip. Comparison applicability is separately scoped to the pair, as specified below. | The estimate is usable for that stated cost operation with the required association, quote coverage, time/scope, currency and period basis. Evidence identifies each prerequisite; the operation and outcome precedence below distinguish binding integrity, V8 quote eligibility and pair comparability. | warning. Proposed binding failure and on_unknown: review follow the explicit precedence below. The frozen V8 derived metric and budget rule retain their own unknown classification, applicability and fixed severity. This is never itself a budget-exceeded verdict. |
| SB-R4a | The enabled Selection/Build supply the original selected identity; a separately identified current catalog item supplies the original SB-R4a status pointer. #41 supplies evidence-resolution policy. | Current-view review of an enabled selection. Disabled selections or historical-only display skip. Established absence skips deprecation and is handled by SB-R4b; unresolved presence/status remains unknown. | The resolved current item is not deprecated. Identify the item, status, publication/scope and applicable source resolution. A retired item's narrow deprecation pass cannot suppress SB-R4b's availability error or establish usability. | warning. Deprecated fails; another resolved known status passes this predicate only. Unresolved required presence/status gives unknown; on_unknown: review. |
| SB-R4b | The same selected identity and current catalog participants as SB-R4a, with the original presence/status evidence. An absence claim requires a qualified exhaustive snapshot for the exact relevant scope. | Current-view review of an enabled selection. Disabled selections or historical-only display skip. | The item is present and not retired within the qualified scope. Active, preview or deprecated satisfies this availability predicate; retired or established absence does not. | error. Retired or established absence fails. Incomplete, unavailable or unresolved required evidence gives unknown; on_unknown: review. Preview-specific information remains a separate #40 question. |
| SB-R5 | The recipient's new Build/answers and each consuming rule's own participant pointers. Withheld operands use the received CD-1 representation; no private field, attestation or excluded derivation supplies an operand. | A specific rule evaluates the recipient's new inputs and encounters a withheld operand. This does not re-evaluate or rewrite a read-only historical report. | Operand policy: preserve the unresolved operand and follow that consumer's actual applicability, assertion and unknown behavior. Withholding supplies no affirmative fact or default value. | No standalone finding or severity. Each consuming rule keeps its own fixed severity and on_unknown policy. Do not place an "unknown" string in a typed value field. |

### SB-R3 operation scope and outcome precedence

Estimate eligibility is assessed for the stated operation and its applicable
time and scope. Present-day rate eligibility is not retroactively imposed on
historical compatibility replay. A retained estimate can support that replay
with the retained inputs required for that historical compatibility evaluation,
even when its rates are no longer current today.
This establishes neither separate cost recalculation nor current budget
eligibility. A newly published pricebook can support a separately labelled
candidate; it never silently becomes the saved revision's locked pricebook.

An assessment identifies one estimate, its claimed Build/revision and its
requested operation. A pair comparison additionally identifies both estimates
and the basis being compared. Its comparability disposition is not a
replacement for either estimate's binding or eligibility assessment.

1. **Binding integrity:** a directly proven false claim that an estimate belongs
   to the stated Build/revision or exact required locked record produces the
   proposed SB-R3 fail/warning display finding. Retain unrelated unresolved
   prerequisites as supporting detail or separately scoped assessments. A
   correctly associated historical record is not falsely bound merely because
   a successor or newer pricebook exists.
2. **Quote eligibility:** absent a proven binding violation, an essential
   unresolved prerequisite or a V8-defined stale/partial condition gives
   unknown/warning. Passing requires the applicable prerequisites to be
   established. V8's existing stale-input classification controls the frozen
   derived metric and budget rule: this proposed cross-record display finding
   does not convert their unknown to fail, pass or a budget-exceeded result.
   If a discrepancy is only staleness under V8, do not relabel it as a false
   binding. Stored coverage and original findings remain unchanged.
3. **Currency and period counterparts:** a budget assessment compares its
   estimate to that Build's budget currency and exact V8 30-day quote basis.
   A pair comparison compares the two estimates' currencies, periods and
   relevant charge bases. A USD estimate eligible for its USD budget does not
   lose that eligibility because a separate comparison includes a EUR estimate.
   An independently applicable budget rule still evaluates only under its own
   actual prerequisites. A skipped comparison does not authorize budget
   arithmetic; the budget rule's own prerequisites must hold.
4. **Pair comparability:** known incompatible currencies or charge/period bases
   make that comparison skipped with the not-comparable reason. Unknown
   required comparability inputs remain unknown. Neither disposition erases
   a proven binding failure on one estimate. No implicit FX, period conversion,
   amortization or one-off/recurring combination is introduced. "Select a
   comparable basis" means obtain the permitted matching inputs; it does not
   change frozen v1's exact 30-day monthly budget requirement.

These are proposed research assessments, not new serialized assessment fields
or released finding identities. #40 must settle their final representation and
review the indicated policy completions before adoption. A skipped comparison,
an eligibility pass and a historical association each retain their limited
meaning.

### Explanation, remediation and dependencies

| ID | Explanation and remediation | Dependency edges and affected consumers |
| --- | --- | --- |
| SB-R1 | Explain which selected identity could not be established in which locked snapshot. Restore eligible access to that exact snapshot, or explicitly adopt a new revision with appropriate selections/locks. Do not silently repin or substitute a current item. | Frozen Build/Selection/catalog identity and snapshot resolution; SB-2/CD-7 revision disambiguation. Saved-build review and downstream evaluation consume membership, which supplies no deployment approval or source-use permission. |
| SB-R2 | Explain the actual report identity and the mismatched or unavailable association. Preserve the original under its actual identity where disclosure permits. Resolve the intended report and pins, or obtain correctly associated evidence for the appropriate revision; never edit a foreign record's identity to make it fit. | Frozen Build/report associations, report resolution and disclosure eligibility. Historical/current views and receiving consumers retain their stronger mandatory report and deployment gates. |
| SB-R3 | Explain the exact association, coverage, time/scope, currency or period limitation for the stated operation. Obtain eligible, complete, correctly associated inputs and preserve pricebook dates and qualifications. Keep one-off and recurring amounts separate, perform no implicit FX or period conversion, and preserve V8's 30-day monthly budget basis. | Frozen cost/pricebook associations, V8, #39 cost semantics, #41 quote evidence and the independently defined budget rule. Cost display, comparison and budget consumers cannot infer a budget pass from partial/stale evidence or this display predicate. |
| SB-R4a | Identify the deprecated item and current evidence. Offer a reviewed replacement proposal; never automatically swap the saved selection. Preserve the original revision and historical findings. | #41 evidence resolution and SB-R4b presence treatment. Current-view review and proposed revisions do not rewrite historical results. |
| SB-R4b | Explain the exact scope establishing retirement/absence, or name the unresolved prerequisite. Verify current evidence or offer an explicitly revised selection. Do not generalize scoped absence to every offering or target. | Current catalog scope/completeness and #41. Current-view review does not establish live target access, credentials or deployment readiness. |
| SB-R5 | Explain the missing prerequisite using only eligible information; obtain the recipient's own applicable answer. Do not recover withheld values through messages, IDs, summaries or derived disclosures, or copy private attestations. | Received CD-1 representation, #40 representation decisions and each actual consuming rule. New recipient evaluations remain separate from permitted historical findings. |

### Synthetic examples

These are hand-worked proposed cases, not executed tests, measurements or
implementation qualification.

| ID | Pass | Fail | Unknown | Non-applicable / skipped |
| --- | --- | --- | --- | --- |
| SB-R1 | Enabled item X at version 2 is present in the resolved locked snapshot. | That exact ID/version is absent from the resolved locked snapshot. | The exact required snapshot cannot be resolved. | Selection disabled. |
| SB-R2 | A report for Build B revision 4 matches every required B/4 lock. | A B/3 or C/4 report is presented as B/4, or a required lock is known to differ. | The requested B/4 report or a required association cannot be resolved; this does not prove that no historical evaluation occurred. | No report display/use requested; no mandatory receiving prerequisite is thereby satisfied. |
| SB-R3 | Each estimate establishes the required inputs for its own stated operation. An eligible pair has comparable currency/period/basis. This is not a budget verdict. | An estimate for C/4 is presented as B/4's estimate: proposed binding fail/warning, while any frozen budget metric follows its existing unknown policy for unusable inputs. | A correctly associated quote is stale for the current operation, or required coverage/evidence is partial or unresolved. Permitted historical amounts may remain displayable. | Neither budget nor comparison requested; or known currency/basis incompatibility makes the separately scoped pair comparison not comparable. No implicit FX or conversion occurs. |
| SB-R4a | Active, preview or retired is not deprecated; a retired item still fails SB-R4b. | Current item explicitly deprecated. | Current status or presence unresolved. | Disabled selection, historical-only display, or established absence handled by SB-R4b. |
| SB-R4b | Qualified current evidence establishes active, preview or deprecated status. | Qualified evidence establishes retirement or absence in the exact exhaustive scope. | Source incomplete/unavailable or required status/presence unresolved. | Disabled selection or historical-only display. |
| SB-R5 | A consuming rule's own assertion passes on sufficient eligible operands; no SB-R5 finding is emitted. | That rule's own assertion fails under its existing fixed severity; SB-R5 does not change it. | Known session/persistent-memory need plus withheld implementation gives W-R11 unknown/warning/defer. | W-R11's unresolved activating need skips that recommendation; this is not a universal policy for withheld operands. |

Intersecting cases preserve assessment scope and deterministic precedence:

- An exact original estimate whose rates expired after the historical evaluation
  may still support that historical evaluation. Historical compatibility replay
  consumes the retained estimate without recalculating it. A current budget
  attempt requires its own eligible quote. Separately reproducing historical
  cost arithmetic requires the original quantities, applicable rates and
  calculation-policy basis; it does not replace the retained estimate.
- A foreign-Build estimate plus a missing unrelated quote prerequisite keeps
  the proposed binding failure and the unresolved detail. An additional
  incompatible comparison currency does not erase either.
- A complete, eligible 30-day USD estimate can be evaluated against its own USD
  budget while a USD/EUR pair comparison is not comparable. Neither that
  comparison nor the display predicate decides whether the USD budget passes.
- Retired yields the narrow SB-R4a pass/warning and the independent SB-R4b
  fail/error. Deprecation and availability are not one interchangeable verdict.

### Conflicting evidence

Follow #41's existing resolution sequence: normalize the claim, establish
scope and version/date, compare authority, and apply its conservative treatment
where equally ranked numeric evidence is applicable. Do not average
categorical statuses, identities or currencies.

- SB-R1: if competing evidence prevents resolution of the exact locked snapshot,
  retain the dispute and give unknown/block. Once resolved, known absence
  within that snapshot remains a failure.
- SB-R2: directly observed unequal record identities are a mismatch, not an
  evidence vote. Unresolved reference resolution can remain unknown without
  erasing a separately known mismatch.
- SB-R3: unresolved applicable rate disputes prevent establishing quote
  eligibility under #41. They do not rewrite an immutable estimate's recorded
  coverage or historical finding. Currency differences are a comparability
  limitation, not a reason to average or convert them.
- SB-R4a/b: genuinely tied categorical status/presence evidence stays unknown,
  with the dispute retained in eligible explanation/evidence. Different scope,
  a newer publication or lower authority is not automatically an equal-rank tie.
- SB-R5: withholding is an unavailable operand, not itself conflicting evidence.
  An actual dispute follows the consuming rule and #41.

Disputed describes the evidence condition using the existing representation.
It introduces no additional finding outcome or typed-value sentinel.

### Version and migration boundary

Every row carries this section's dated research proposal revision, not a
released rule, schema or implemented ruleset version. Existing reports keep
their producing versions and original outcomes; this companion does not relabel
or migrate them. Future #40 acceptance must identify the actual accepted
version and any required reader/migration behavior before implementation uses
it. An unsupported path remains a qualified limitation; it authorizes no
silent conversion, latest-input substitution or historical rewriting.

## Pricing and capacity

No prices or capacity figures are recorded. Cost snapshots reference #39's `CostEstimate` semantics (V8); historical estimates are kept and labelled with their pricebook's `captured_at`. Whether historical prices may be shown at all depends on each source's applicable #60 display and export decision. The current product decision excludes GPUs.io API retrieval, display and export, including saved/shared build cost views (P8). The paid API and attribution conditions recorded in P4 do not establish eligibility for this product. Reconsider only on a specific permitted-use basis covering this product and a new #39/#41/#60 review.

## Recommendation and rationale

1. Adopt option C: immutable revisions with separate historical and current validity, and derived revisit states.
2. Share by opaque, revocable link to a redacted projection of one revision; apply the sensitivity table to shares and exports alike.
3. Never copy organisation attestations; forks receive withheld inputs as unanswered and apply the existing missing-input, applicability and SB-R5 behavior.
4. Compare by (kind, role) with explicit "not comparable" reasons; never sum across currencies, charge bases or one-off/operating scopes.
5. Keep historical reproducibility, current eligibility and disclosure separate. Publications can prompt a current evaluation; apply selected-input, correction, validity and rights events to their actual scope without inventing a TTL or invalidating history solely because a successor exists (P9).
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

The table retains the original SB identities. Rows marked received record the
accepted base research choice and name its remaining integration scope; they do
not reopen that choice as an undecided alternative. A future implementation or
released wire format is not a new prerequisite for research acceptance. P22
subsequently receives this register's bounded research mapping and dated
common-format companion, with SB-9 received only as a proposal for #42's owners.

| ID | Decision | Accountable | Consulted |
| --- | --- | --- | --- |
| SB-1 | The CD-1 typed answer and explicit provided-value attribution representation is received in P10. Remaining build-assumption mapping includes presets and FX/tax assumptions with their actual sources; receipt does not add fields to v1 | #40 | #81 (CD-1), #39 |
| SB-2 | Receive the explicit positive revision beside the catalog ID selected by the CD-7 exact-pin candidate (P11); do not assume an ID is unique per revision or infer a latest/sole artifact. Released representation and consumer integration remain with #40 | #40 | #41 |
| SB-3 | Receive the CD-7 explicit pricebook revision and historical manifest association candidate (P11). P13 retains the original snapshot/comparison intake; P26 receives the current interface and P28 records its coordinating sufficiency, separately from P19's historical named request. Calculation policy and complete/current coverage retain their own evidence. Final versioned Build/CostEstimate association remains #40 integration | #40 | #39 |
| SB-4 | Select the separate share record and explicit access/pinned-or-following/revocation semantics in Sharing; it does not mutate a saved revision or grant source rights. #42 owns the policy; #40 owns its future versioned representation | #40 | product owner (#42 assignees) |
| SB-5 | Derive displayed state from exactly associated reports and their supported evaluator/profile. A stored `lifecycle: validated` claim cannot certify current eligibility or deployment readiness. CD-7 replay supplies a bounded evaluator-binding candidate; final representation remains #40 | #40 | — |
| SB-6 | Select a new Build ID/revision 1 with the source ID/revision as separately qualified lineage; no copied private attestations, withheld inputs or approvals. Wire placement remains #40; access and lifecycle limits are in Sharing and SB-9 | #40 | #42 assignees |
| SB-7 | The initial research choice is one primary workload per build (P12). A later multi-workload model and complete physical co-residency accounting stay with #40/#10; grouping or comparing builds cannot establish combined fit | #40 | #10, #81 |
| SB-8 | The five-state CD-1 research representation, including distinct `withheld`, is received in P10. Apply its exact profile and migration boundary to the separately reviewed share/fork projection; do not reinterpret the delivered 0.1 reader | #40 (with CD-1) | #81 |
| SB-9 | Proposed for the #42 owners (P19): lifecycle distinctions above and the separate unadopted numeric proposal P20 await actual disposition. Artifact-class durations, deletion completion/residuals and permitted fork survival must be settled before a hosted retention promise | product owner (@tynamite, @appletechie; #42) | #41 (data governance), #40 (representation) |
| SB-10 | Receive the CD-7 historical wrapper preflight as the bounded research placement for exact cross-record checks (P11). Preserve the frozen evaluator and original findings; production/successor placement remains #40 integration | #40 | — |

## Open questions and handoffs

| Handoff | What is asked | Status |
| --- | --- | --- |
| #40 | Receive selected answer/attribution, exact identity, immutable-history and private-attestation representations; reconcile remaining SB mappings and integrity proposals | Actual H40-42 receiving scope accepted (P10), with selected representations delivered by #403 (P11). #40's research prerequisite is completed (P21). P22 separately receives the final #431 SB mappings, complete projection and dated common-format policy completions as a bounded research interface; released representation and consumer implementation retain their own review |
| #41 | Confirm the invalidation table and the separate retained/current/disclosure boundaries | Original interim scope confirmed by @tynamite in [review 5558408384](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/114#pullrequestreview-5558408384). The actual delegated H41-42 receiving decision on 2026-10-18 accepts the later scoped interface (P9); no arbitrary TTL or whole sharing/migration policy is adopted |
| #39 | #42 → #39: SB-3 snapshot and comparison input (currency, period, charge basis, one-off vs operating) | P13 retains the original intake; P26 accepts the current interface with constraints, including delivery of the corrected material/use-qualified disclosure row and P28 records its sufficiency under the current engineering delegation. P19's named request is preserved as history, without a reply attributed to @appletechie / @PUSHINGSQUARES. Final versioned integration and unadopted cost policy stay separate |
| #37 | #42 → #37: a "deploy from saved build" path uses the exact pinned revision and its own actual approvals (V8) | P14 retains the original intake; P25 accepts the current interface with constraints and P28 records its sufficiency under the current engineering delegation. P19's named request is preserved as history, without a reply attributed to @appletechie / @PUSHINGSQUARES. No deployment approval or execution follows |
| #81 (#2/#3) | Incoming workload/mode inputs and the separate reverse share/report-prefill interface; Q7 is SB-7 | P12 records incoming intake; P16/P17 retain the separate engineering reverse decisions. P18 is @tynamite's named reverse acceptance with constraints at `03e347b4`. P24 independently verifies the five implemented constraints in the current producer; P28 records that review's sufficiency. The actual reviewer is the in-session Apple engineer, without a reply attributed to @appletechie |
| #60 | #42 → #60: qualify historical/shared/exported views after a relevant material, use or permission change | P15 retains the original intake; P27 accepts the current interface with constraints, conditional on delivery of the corrected display/export permission row and P28 records its sufficiency under the current engineering delegation. P19's named request is preserved as history, without a reply attributed to @appletechie / @tynamite. No blanket history deletion, retention grant or new source permission follows |
| #51 | PCPartPicker save and share flows remain unobserved (P5); this note doesn't rely on them | Informational |

The original #41 invalidation-policy handoff and the later H41-42 scope are
confirmed. The [actual H41-42 receiving decision](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/42#issuecomment-6254389540)
reviewed proposed source `13b11b7eb9a84af200ea9f0577fcb0e5182a4c46`, note blob
`c7d36a3c6c5ff305080867ec98763019d5e365bb`. At that receipt the source was unsigned
and unmerged; the receipt itself establishes no producer delivery or validation
result. It accepts selected-input change events, corrections/retractions,
current-state eligibility and source-use boundaries, including preserved
permitted history after failed refresh and withheld values after a rights
exclusion. It keeps secrets, private condition/grant references and organisation
attestations out of share/fork, and does not treat CD-7 configuration-only work
as a blanket sharing/history migration.

This was an actual delegated engineering receiving decision, not a reply
attributed to another named assignee. The new proposal covering all fields above
is separately offered for review; it is not retroactively attributed to P9.

The subsequent [actual H40-42 receiving decision](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/42#issuecomment-6254602552)
accepts the selected research representation at proposed source
`45b20960cbc4652fb3341c977a025821c96595f9`, note blob
`375506eea95bd7fc30883c0e4f2a2f5496f77cfd` (P10). It receives the pointer-indexed
five answer states with explicit provided-value attribution, exact
Build/revision/selection/catalog and rule/report identities, immutable original
bytes and explicitly versioned successor projections. These accepted base
choices are not reopened as missing alternatives by the SB table.

Retained 0.1 records stay in their original profile: a new projection cannot
invent `assumption: false`, discard an old source, copy a current value or supply
a missing identity. Private scoped organisation attestations and condition/grant
references do not transfer through share/fork; the recipient supplies its own
applicable answers. The configuration-only #383 reader is not a complete shared
historical/current view. This actual delegated research intake supplies neither
producer delivery nor another named person's response; the source was unsigned
and unmerged at the receipt. It does not retrospectively accept this note's new
disclosure proposal. Other receiving decisions, retention, share access and the
remaining SB mapping/projection work stay separate. Neither source-only receipt
removed the #40 prerequisite; its later actual research completion is recorded
in P21. P22 supplies the actual later receiving decision for this new packet,
without reattributing it to either historical receipt.

### Earlier receiving and delivery reconciliation — 2026-10-19

The earlier P9/P10 statements that their sources were unsigned and unmerged
describe the time of those receipts. They remain historical facts. The selected
#40 representations and #41 source policy were subsequently delivered by
[#403](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/403) at signed
`cebbf59345e01d34b8ad4c20d0b57782f6e05369`. #41's
[actual completion receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/41#issuecomment-6256107246)
records its twelve-criterion decision and later closed/completed readback;
that receipt did not itself complete #40. The later CD-2 research decision was
delivered by #429 at signed `449a29be1752a3c545709da466c7d53fc18fef73`.
The actual twelve-criterion completion review and the closed/completed issue
readback on 2026-10-19 establish #40's research completion (P21).
That prerequisite is satisfied; its native relationship history is retained.
The coordinating engineer read the original completion receipts and issue
state; that is not a new full central-source or execution audit. Completion of
#40 did not itself accept the later #431 packet. P22 records that separate
central intake and P23 the actual producer delivery; neither releases a
successor contract or declares whole-#42 completion.

The complete-projection correction was delivered by #396, the dependent-rule
applicability clarification by #412, and retained-association diagnostics by
#397. At inspected accepted main
`45b8fe1c7ee3a010cc294e751a3424ccb81366d4`, this note before the present
amendment is blob `2f3dc5b22b0e77fa7c496865bb4f20b8a81ae8f2`.
That delivery is distinct from any later receiving decision or from accepting
a production implementation.

The complete incoming
[#3 → #42 receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/42#issuecomment-6255453677)
and
[#2 → #42 receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/42#issuecomment-6256110870)
are now recorded explicitly (P12). Their exact producer/consumer pins and later
source guards remain in the receipts. Receive the evidenced per-component
operator/capacity definition, actual workload/answer states, one primary
workload, and the report-from-build qualification boundary. They supply no new
measurement, automatic private-attestation reuse or blanket permission for a
partial fit record.

The three new outgoing decisions below are actual receiving-side decisions by
the coordinating ChatGPT engineer through CompleteDotTech under delegated
project authority, with independent reasoning review of the supplied
interfaces. The producer was read completely. The cost and deployment
receiving reads covered the bounded sections named in each receipt; the rights
note and named frozen gate documents were read completely. No absent named
assignee, full-vendor re-audit or new test run is attributed to those reviews.

| Direction / receipt | Exact receiving basis at the accepted main above | Accepted scope |
| --- | --- | --- |
| [#42 → #39 / 6256564986](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/39#issuecomment-6256564986) | Cost Estimate blob `6df5e3c30e1bef38a6a75b576e7eaa889262338e` | Original versus current estimate, calculation identity, exact quantity/comparison basis, coverage, one-off/recurring separation and disclosure. Unadopted FX/default/aggregation policies remain proposals. |
| [#42 → #37 / 6256565553](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/37#issuecomment-6256565553) | Deployment blob `64685127aa4477b323d0f72479abddac21cfcae9` | Exact Build/revision/target and associated evidence; actual required approvals and readiness gates. A fork or conforming manifest does not inherit approvals or prove readiness. |
| [#42 → #60 / 6256566108](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/60#issuecomment-6256566108) | Rights blob `2fb0aa8d4c51448f111dbc82a8123206646f61c6` | Material/use-qualified complete projections, retained-history limits and current exclusions. Relevant changes require qualification without automatically cancelling every historical grant or permitting every later use. |

These engineering decisions receive the existing producer at the stated blob;
they are not replaced or withdrawn by the later review. P19 explicitly requests
named consuming-owner confirmations for #37/#39 from @appletechie /
@PUSHINGSQUARES and for #60 from @appletechie / @tynamite. Those confirmations
remain outstanding. **The separate central disposition of the reconciled SB
choices, complete projection and common-format companion is now received in
P22**; it was not inferred from #40's research completion (P21).
The reverse configuration/report-prefill decisions below retain their own
directions and source pins; incoming P9/P10/P12 receipts are not silently
reversed. #42's current assignees coordinate these remaining decisions, the
requested independent producer read. P23 records the reviewed #431 delivery.

On 2026-10-19, the complete producer at PR #431 source
`03e347b44b8d03bc2e9abda10a97b43cfcd430c8`, note blob
`c576628557274c611f52ad36c8de8c27281ec8bb`, was received in the two reverse
interfaces below. The root engineer read that complete producer and the
consumer sections named in each receipt; an in-session peer independently
assessed those supplied interfaces. Fresh complete-tree readback at accepted
`ec29b802ff1a3c8a2f1e89384a0c4dc9b89c8a60` confirmed the exact consumer
leaves originally inspected at `45b8fe1c`. These are actual delegated project
engineering decisions through CompleteDotTech, without an absent assignee's
reply, full-consumer/vendor audit or execution claim.

| Direction / receipt | Exact consumer leaf | Accepted scope and retained limit |
| --- | --- | --- |
| [#42 → #2 / 6256878974](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/2#issuecomment-6256878974) | Workload `d8e86c8794ce175020e3457e62cba86c124f82ca` | One primary workload, own Build/revision associations, independent fork inputs and specific W-R11/CD-12 scopes. No cross-build co-residency, invented quantities or fit evidence. |
| [#42 → #3 / 6256879792](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/3#issuecomment-6256879792) | Deployment mode `8d64fcc0bf16222b0ed3e06dc53c396e525c0741` | Exact historical association, current EV-1 eligibility, complete disclosure and prefill-only reporting. No inferred measurement, consent, community admission or purge/retention guarantee. |

These receipts accept their exact producer interface. They do not
retroactively accept the later common-format companion's policy completions.
The already completed #2/#3 research records retain their own original
acceptance; this additional intake neither reopens them nor completes #42.

### Named-owner review and follow-up recorded for #431 — 2026-10-19

P19 is @tynamite's actual #42 co-owner review of source
03e347b44b8d03bc2e9abda10a97b43cfcd430c8. Its text accepts the research
proposal with constraints; GitHub records its formal state as COMMENTED.
The delivered #431 follow-up applies the requested SB-9 proposal labels, explicit outstanding
named consuming-owner confirmations and actual reference-comparison timestamp.

P18 is the separate actual reverse #42 → #2/#3 receiving review by @tynamite,
who also co-owns producer #42. It accepts with constraints the same 03e347
producer against the consumer notes at accepted 170f0f7. The prefill sensitivity
rows, actual-run section, account-capacity rule, assumed preset treatment and
comparison citation to the classification test above implement its five requests. P16/P17 remain the
earlier engineering reviews, not substitutes for this named disposition.

Neither receipt is relabelled as a review of this later amendment. P18's
requested independent producer read by @appletechie remains outstanding, and
P19's requested consuming-owner confirmations remain explicit above. The
co-owner stated that the reverse review would not hold this partial PR; this
reconciliation does not introduce a blanket new merge restriction. SB-9's
numeric choices remain the separate unadopted P20 proposal pending an actual
owner disposition. The central packet and reviewed #431 delivery are now
recorded in P22/P23. Each of the eleven criteria retains its own evidence;
no absent person's reply is inferred.

### Actual delivered record and central intake — 2026-10-19

The final #431 producer `473995df3e95f551a9b573d068ef1c9c441136ec` was
delivered to main as signed
`73403ebd91437a4bf718ccf9b3857f955e16732f` at 01:08:18 UTC (P23).
Its note blob `b7c4e0867acaaafd88023125447ecf1a5f3fc781` is
112,643 UTF-8 bytes, SHA-256
`fa205db0995712eb98162d7769720a5102d93b17916e3b778dee3be082a538b6`.
The exact delivered tree `b6bbd22e521a729a4408530e1cb13f641c06ae57`
matches the actual tested PR preparation. The original post-main output records
21 contract and 1,101 repository tests: the same 1,122 unique passing methods,
with zero failures, errors or skips, and the same four validator results.
P23 links the original run, source/prepared reviews and output hashes; those
executions concern that exact delivered tree, not a later reconciliation.

At 01:14:33 UTC, the actual #42 → #40 receiving decision (P22) accepted the
bounded final producer's SB mappings, complete-projection policy and
**2026-10-19 companion draft 1**. It explicitly settles that companion's
research policy completions: exact membership and report binding, separate
SB-R3 association/display and frozen V8 cost/budget behavior, scoped
SB-R4a/SB-R4b applicability, and SB-R5's consumer-owned withheld-operand policy.
The companion's original proposal wording describes its submitted revision;
this later receipt supplies its central research disposition without rewriting
the original rule identities, cases or historical evidence.

The received scope preserves five answer states and explicit assumptions,
exact Build/revision/required-lock identity, immutable history and separately
qualified current candidates. Complete projections must qualify fields and
derived meaning for the actual material, purpose and view; redaction does not
inherit the complete artifact's binding, signature, qualification or total.
Original calculation reproduction needs its own quantities, eligible rates and
calculation/allocation/rounding basis. The receipt receives the corrected
recipient-run, account-capacity and assumed-preset interface. It receives SB-9
only **as a proposal for the #42 owners**, adopting no numeric period or hosted
retention promise.

The actual receiving basis is central note blob
`d3d53f3c135556a3bd227e8008dceb9f08676749`, complete rule template
`380bcdb40f2a1d1d02ec6ddffe367729763ed526` and frozen pricing/gates
`1e9e64ffe1138ffab456fd8b39c832d9f41e11ea` at the receipt's stated source.
Its independently attributed source and semantic reads supply that decision;
they are not new runtime, vendor, retention or installed-native tests.
No later central edit is retroactively included in those source pins.

P22 supplies the requested central research intake. It does not supply the
P19-requested named #37/#39/#60 confirmations or P18's independent producer
read, grant source rights, serialize new fields, adopt a runtime adapter or
migrate frozen v1. Named follow-up questions and any future implementation
retain their stated owners and scope.

### Current receiving decisions and coordinating sufficiency — 2026-10-19

The following are actual current reviews of the accepted Saved Builds note,
separate from the earlier P13–P19 source identities and named requests. The
reviewed producer is `7ec5742529997fbb466a8bdafc8d9379f476ca4b` (118,240 UTF-8
bytes, SHA-256 `59cbb50a0a7e8e1bec2acef747d0f395328cda631e7ebe7beda026b725a136e8`)
as reviewed for P24/P26/P27 at signed accepted main
`0009c66a611abc02d6bde2821efe8b4905606bad`, tree
`d7115e3e7bf1056a9fccbd2ade7693b913821276`. P25 has its own actual
`05270b91b746dc828390ad4fd44f6597fe651405` /
`bbf1c90fbe13fd13d20226f40e7b70b75e99bc3d` source read at 04:02:30 UTC.
The later complete-tree readback at
signed `528c46b35bbd9cb180eaf20958adaacf3f7e8798`, tree
`b367aa327516aa0362784a594e9c737a06550ee1`, preserves the literal receiving
inputs. This later source-preservation check does not relabel an earlier read
or repository execution.

| Actual review / time | Actual reviewer and input scope | Accepted interface and retained limits |
| --- | --- | --- |
| [P24 / 6259327497](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/42#issuecomment-6259327497) · 03:58:20 UTC | In-session Apple engineer; bounded Saved Builds prefill/disclosure/fork/mode interface against Workload `d8e86c8794ce175020e3457e62cba86c124f82ca` and Deployment Mode `8d64fcc0bf16222b0ed3e06dc53c396e525c0741` | All five implemented P18 constraints are present: actual-run versus origin identities, profile-specific essentials, the recipient's own account capacity, explicitly assumed pinned presets, and the received per-component classification/reverse citation. P18's named author and earlier source remain historical; this is not a reply from @appletechie or a new complete-note/vendor/runtime audit. |
| [P25 / 6259463607](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/37#issuecomment-6259463607) · 04:11:06 UTC | Actual coordinating deployment decision, supported by an independent in-session Apple interface read at `05270b91`; Saved Builds `7ec57425`, Deployment `08c3dacf4ce574071a4ce88a13509be42ace5f38`, complete frozen manifest and pricing/gates, with a separate 04:10:02 UTC `528c46b3` preservation guard | Accept with constraints exact Build/revision/target and applicable records/locks; historical/current and fork identity; independently required approvals and full G1–G12 applicability; effective offering/account/control evidence; and actual rollout/rollback qualification. The receipt's independent read covers the receiver's complete R1–R36 table, comparison fields, revision 0.2, readiness and current lifecycle/retention context. It neither certifies the separately owned 90-rule follow-up nor the remaining display/export correction. No unpublished duplicate review is substituted. |
| [P26 / 6260214302](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/39#issuecomment-6260214302) · 05:15:49 UTC | In-session Research engineer; complete Saved Builds producer and bounded Cost Estimate method `dc97759ed922326ddf8d270e1861f627725a5a31`; complete pricing/gates and CostEstimate/Pricebook schemas, relevant source-policy interface | Accept with constraints each side's exact Build/selection/Pricebook associations, native units, workload/period/charge basis, conditional eligibility and coverage. Historical compatibility replay may consume an eligible retained estimate; recalculation needs the actual quantities, rates, allocation/rounding/calculation policy and implementation. Current candidates remain separate. Disclosure acceptance is conditional on reviewed delivery of the corrected Shared / exported row above. No latest substitution, zero for missing cost, reserve/fit inference, FX/default adoption or new price intake follows. |
| [P27 / 6260217715](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/60#issuecomment-6260217715) · 05:16:06 UTC | In-session Research engineer; complete Saved Builds and Rights Validation `2fb0aa8d4c51448f111dbc82a8123206646f61c6`, all ten integration decisions `159766a48d7ec4460cbdc327dd5033d9f1b137a7`, and source-policy interface `c862112312d45bbe13b9e9261b8f83ee581cafa6` | Accept with constraints the actual material/use/purpose/recipient-view qualification, including nested values, derived findings and counts. Retained bytes supply no disclosure permission, and partial views inherit no full-artifact binding or grade. Relevant changes do not automatically cancel every historical grant or permit later use. Acceptance is conditional on reviewed delivery of the corrected Shared / exported row above. All ten product statuses and the three false GPUs.io flags remain unchanged; revocation, deletion, purge, lineage and independently permitted forks remain distinct. |

The actual [source finding6259351017](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/42#issuecomment-6259351017), also recorded in P25, identified the earlier Shared / exported catalog-value row's display-only wording. This amendment changes only its permission and explanation cells to require the applicable decision for the actual material and intended display or redistribution use, with its conditions (P8/P15). An export inherits no display-only permission. The complete-projection policy and all historical evidence rows remain unchanged; this is a precise documentary correction, not a new rights grant.

P26 and P27 expressly condition their disclosure intake on reviewed delivery of that exact correction. The changed row is present in this candidate, while actual reviewed source delivery and final main qualification remain required before treating that condition as fulfilled. P25's exact saved-revision/own-approval acceptance retains its separately stated source-use limit.

The separate coordinating decision [P28 / 6260273948](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/42#issuecomment-6260273948) at 05:20:47 UTC accepts these
actual current reviews under the user's engineering delegation for the literal
research handoff criterion. It does not claim that the people named in P18 or
P19 replied, change the assignee fields, or backdate any acceptance. The earlier
requests, their then-outstanding state and their exact source pins remain in
the historical sections above. P24 supplies the requested independent producer
integrity review; P25–P27 supply the three current outgoing technical intakes.
Incoming P9/P10/P12, reverse P16–P18 and central P22 retain their own directions
and limits. No incoming receipt is silently reversed.

The Research engineer read the complete current producer; its cost-policy read
was limited to the sections and rows named in P26, while the rights note,
ten integration decisions and named frozen gates/schemas were read completely.
The coordinating and Apple engineers retain the bounded methods actually
specified in their own receipts. These reviews add no vendor or legal-source
refresh, hardware/native/runtime execution, new released contract, source-use
grant, numerical estimate or deployment approval. Original source, execution
and contributor attributions remain separate.

SB-9 and P20's numeric periods remain proposals. Artifact-class retention,
deletion completion, residual copies and permitted fork survival keep their
named follow-up owners before a hosted promise. The Track E research acceptance
requires resolved **or documented** retention questions; these current reviews
do not adopt a numeric policy or report implemented storage behavior. The exact
amendment's source review, configured validation, ordinary delivery and actual
main readback remain separate from receiving sufficiency. The final issue
assessment must use those real results; this note does not itself mutate issue
checkboxes, state or Project fields.

### Subsequent T5 and lifecycle review — 2026-10-19

P29 is the actual appletechie interface review at delivered producer
`31ac26c95e43908602a17bb4a8964adbc26cf131`, note
`3e4a67aafd5fba569ab68ed603a72dd3d232e406`. The author disclosed original #114
authorship, limited independence to the interface review, and reported no test,
source/rights/vendor refresh, CI qualification or issue-state verification.
The five P18 constraints and SB-9's structure were accepted with the explicitly
stated limits; no numeric retention period was adopted.

The present engineering clarification receives the concrete T5 and fork-display
findings. It explicitly classifies private training provenance, dataset
locators and scoped attestations, separates origin-account artifact availability
from capacity, and preserves the actual A-05/A-11/A-15 outcome semantics.
The supporting current T5 source was read at accepted
`7d5b98ad53a3c92ac5b4e7c049d3f5197e1f28ec`; these interpretations keep their
original source dates and proposal limits. P29's suggested unknown results are
qualified by each concern's actual applicability and any established violation;
they do not replace a known failure or assert that every omitted input is
required. Public eligible catalog facts keep their separate classification.

P29's quoted "qualification review, not an automatic purge" wording belongs to
the external P20 proposal, not the delivered note's independent-fork row. The
clarified row makes the existing #60 denial effective for all served views
without waiting for purge; actual physical deletion, residual copies and any
permitted retained original remain separate decisions. The original comments
and permitted historical reports are not rewritten. Token renewal/non-reuse,
revocation-record retention, backup restoration and deletion-completion evidence
remain SB-9/#41/#40 follow-ups before a hosted promise; no duration, legal
conclusion or implementation is supplied.

This is a later bounded source clarification, not a reversal of the completed
research acceptance recorded in [6261594584](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/42#issuecomment-6261594584).
All eleven literal criteria, earlier dated receiving decisions, original
assignees and native relationships retain their scope. Its source review,
configured validation and ordinary delivery require their own actual records.

## Acceptance criteria coverage

The following first column preserves all eleven literal issue criteria. This is
a readiness map, not a change to their checkboxes or a declaration of whole
issue completion. Research acceptance does not require implementing the builder.

| Literal issue criterion | Evidence location | Current disposition |
| --- | --- | --- |
| Build record definition referencing #40 schema | Build record definition; SB-1–SB-10; P10/P11/P21/P22 | Frozen mapping and selected research choices documented. #40's research prerequisite is completed, and P22 receives the final bounded SB/projection/common-format research interface. |
| Sharing and privacy rules | Sharing; complete projection; SB-9 proposal; P18–P23 | Access, fork and disclosure semantics are documented, centrally received in P22 and delivered in P23. SB-9 remains proposed for the #42 owners, including P20's unadopted numeric choices and named follow-up; no hosted retention promise is inferred. |
| Comparison semantics with examples | Comparison and its synthetic examples; SB-R3 | Mode, workload, rule/protocol and cost-basis distinctions are explicit; historical display, new evaluation and cost recomputation remain separate claims. |
| Invalidation triggers (from #41) and resulting user-visible states | Invalidation triggers; corrected Revisit states; P9/P11 | Actual #41 input received and delivered. Equal references alone no longer imply current eligibility, disclosure permission or reproduction. |
| Decision record merged at `research/T0-configuration/saved-shared-builds.md` following the research method | Proposal sequencing; current delivery reconciliation; P23 | Original #114 and later #396/#412/#397 contributions are delivered. P23 records the reviewed #431 source, actual signed main 73403ebd and original post-main verification. This establishes the record's delivery, not whole-#42 completion. |
| Candidate set covers the relevant deployment modes (API / managed / self-hosted) or states why a mode does not apply | Candidate options; Deployment modes covered; Comparison; P12 | API, managed and self-hosted serving plus hybrid composition covered with their separate historical-v1 and researched per-component representations. |
| Comparison fields defined with type, unit, and evidence requirement | Comparison fields; frozen field mapping; SB-R3, P13 and P26 | Types, units, evidence and comparison basis recorded; missing quantities, cost coverage or calculation policy do not become invented values. |
| Compatibility rules and warnings use the shared format from #40; verified rules are separated from hypotheses | Compatibility proposals; complete common-format companion; CD-7 historical candidate; P10/P11/P22 | Original SB identities and contract-derived/hypothesis labels are retained. P22 receives the actual template mapping and dated policy completions, including SB-R5's consumer-owned operand policy. Hand-worked synthetic cases and bounded historical replay retain their own scope; neither is independent vendor verification or a released successor ruleset. |
| Every factual or numeric claim cites a primary source with access date (and version / region / currency where relevant) | Evidence V1–V13, X1–X3, P1–P28 | Primary contract/external references retain actual access dates and scopes. P24–P28 add only actual current project reviews and the separately attributed coordinating decision; this reconciliation introduces no new vendor measurement, price or licence claim. |
| Each handoff listed under Dependencies is confirmed by the consuming issue's owner (link the comment or PR review) | Open questions and handoffs; P9/P10/P12/P16–P18/P22; current reviews P24–P27 and coordinating decision P28 | P25/P26/P27 receive the current #37/#39/#60 interfaces, and P24 supplies the independent producer review of the implemented P18 constraints. P28 accepts these actual decisions under the current engineering delegation for this literal research handoff criterion. The original named requests and earlier receipts remain historical; no absent person's reply, assignee reassignment, unanimity requirement, SB-9 numeric adoption or implementation acceptance is inferred. Final source/delivery and issue assessment remain separately evidenced. |
| Open questions recorded with a named follow-up owner | Open decisions (SB-); SB-9 accountable follow-up | All remaining decisions have accountable workstreams; retention periods/deletion completion are documented with @tynamite/@appletechie and #41/#40 consultation. |

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
| P9 | [Actual H41-42 receiving decision](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/42#issuecomment-6254389540); [reviewed producer source](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/13b11b7eb9a84af200ea9f0577fcb0e5182a4c46/research/T0-configuration/catalog-data-sources.md) | 2026-10-18 | Proposed source `13b11b7e`, note blob `c7d36a3c`; receipt submitted 2026-10-18 19:51:29 UTC | Project engineering receiving decision | Accepts the stated saved-build event/current/disclosure interface; unsigned source at receipt, no producer-delivery claim, attribution to absent people, whole-issue completion or blanket sharing/history migration |
| P10 | [Actual H40-42 receiving decision](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/42#issuecomment-6254602552); [reviewed producer source](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/45b20960cbc4652fb3341c977a025821c96595f9/research/T0-configuration/component-schema-compatibility.md) | 2026-10-18 | Proposed source `45b20960`, note blob `375506ee`; receipt submitted 2026-10-18 20:12:44 UTC | Project engineering receiving decision | Accepts the stated base research representations and conditions; unsigned source at receipt, no producer-delivery, complete shared/history implementation, new disclosure-proposal acceptance or #42 completion claim |
| P11 | [Accepted central record](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/45b8fe1c7ee3a010cc294e751a3424ccb81366d4/research/T0-configuration/component-schema-compatibility.md), CD-7 exact pins/native envelope/historical replay and selected representations; [#41 delivery receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/41#issuecomment-6256107246) | 2026-10-18 | Accepted main `45b8fe1c7ee3a010cc294e751a3424ccb81366d4`; central blob `8ee5a7b7a960ae63c073c996cfdc73b80d939e7c`; #403 delivered at `cebbf593` | Project research and delivery evidence | Bounded candidate/source sections checked; no whole central/vendor re-audit, CD-2 acceptance, successor release or #42 closure |
| P12 | [#3 → #42](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/42#issuecomment-6255453677) and [#2 → #42](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/42#issuecomment-6256110870) actual receiving decisions | 2026-10-18 | Original complete producer/consumer pins and later source guards retained in each receipt | Project engineering receiving decisions | Per-component mode, workload, private non-transfer and complete projection intake; incoming receipts do not substitute for reverse acceptance |
| P13 | [#42 → #39 receiving decision](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/39#issuecomment-6256564986) | 2026-10-18 | Producer/consumer at `45b8fe1c`, exact blobs in reconciliation above | Project engineering receiving decision | Bounded snapshot/cost/comparison interface; no refreshed vendor rates, adopted FX defaults or production estimator |
| P14 | [#42 → #37 receiving decision](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/37#issuecomment-6256565553) | 2026-10-18 | Producer/consumer at `45b8fe1c`, exact blobs above; frozen manifest and gates read | Project engineering receiving decision | Pinned revision and actual approvals; schema conformance or historical evidence is not deployment approval |
| P15 | [#42 → #60 receiving decision](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/60#issuecomment-6256566108) | 2026-10-18 | Producer/consumer at `45b8fe1c`, exact blobs above | Project engineering receiving decision | Complete-view qualification consumes existing project exclusions; no new primary terms check, publisher grant or retention duration |
| P16 | [#42 → #2 receiving decision](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/2#issuecomment-6256878974) | 2026-10-19 | Producer `03e347b4` / saved leaf `c5766285`; consumer `d8e86c87`, confirmed at accepted `ec29b802` | Project engineering receiving decision | Bounded workload/share/fork interface; no execution, named-assignee reply, released schema or retroactive common-format acceptance |
| P17 | [#42 → #3 receiving decision](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/3#issuecomment-6256879792) | 2026-10-19 | Producer `03e347b4` / saved leaf `c5766285`; consumer `8d64fcc0`, confirmed at accepted `ec29b802` | Project engineering receiving decision | Bounded comparison/report-prefill interface; no measurement, consent, new source permission or retroactive common-format acceptance |
| P18 | [Actual named reverse #42 → #2/#3 review](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/42#issuecomment-6256905580) | 2026-10-19 | Submitted 00:11:59 UTC; producer 03e347b4, consumer main 170f0f7 | Named owner receiving decision: accept with constraints | @tynamite co-owns producer and consumers; requested @appletechie producer read remains separate. Five prefill/mode requests, no tests, new wire adoption or review of this later amendment |
| P19 | [Actual #42 co-owner PR review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/431#pullrequestreview-5565750151) | 2026-10-19 | Submitted 00:04:39 UTC on 03e347b44b8d03bc2e9abda10a97b43cfcd430c8 | Named co-owner review; text accepts with constraints; formal state COMMENTED | SB-9 proposal status, requested named consuming-owner confirmations and comparison as-of date; no formal APPROVED vote, numeric adoption or review of this later amendment |
| P20 | [SB-9 numeric retention proposal](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/42#issuecomment-6256905325) | 2026-10-19 | Submitted 00:11:57 UTC; proposer @tynamite, stated deadline end of 2026-10-23 UTC | Unadopted project policy proposal | Actual owner disposition and stated governance qualifications remain; deadline or silence is not a receiving receipt, adopted default, operating promise or observed storage behavior |
| P21 | [Actual #40 completion review](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40#issuecomment-6257213742), [independent criterion support](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40#issuecomment-6257194682), and [#42 prerequisite update](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/42#issuecomment-6257241193) | 2026-10-19 | #429 delivered 449a29be1752a3c545709da466c7d53fc18fef73; #40 closed/completed at 00:41:11 UTC, read back on 2026-10-19 | Project engineering completion decision and actual issue state | Root read the original receipts and issue state; no new full central-source/test audit, named-assignee approval, successor release, acceptance of the new #431 packet or whole-#42 completion |
| P22 | [Actual central #42 → #40 receiving decision](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40#issuecomment-6257566405) and [receiving notice on #42](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/42#issuecomment-6257585573) | 2026-10-19 | Submitted 01:14:33 UTC; final producer 473995df, delivered 73403ebd, note b7c4e086; exact central/template/gate basis recorded above | Actual delegated central engineering receiving decision: accept the bounded research interface with stated conditions | Receives SB mappings, complete projection and companion draft 1 policy completions; SB-9 only as proposed. No absent named-assignee reply, successor release, implementation, numeric retention adoption or whole-#42 completion |
| P23 | [Reviewed #431 delivery and original post-main verification](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/42#issuecomment-6257698095), [signed delivered commit](https://github.com/Pick-Your-AI/pick-your-ai-research/commit/73403ebd91437a4bf718ccf9b3857f955e16732f) and [original main run](https://github.com/Pick-Your-AI/pick-your-ai-research/actions/runs/39183951002/job/117842338982) | 2026-10-19 | Merged 01:08:18 UTC; tree b6bbd22e521a729a4408530e1cb13f641c06ae57; actual prepared a41e6dab and delivered 73403ebd | Project source/delivery evidence and original workflow output, individually read and parsed | Same 1,122 unique passing methods and four validator results at the exact delivered tree; no failed/error/skipped methods. Repository checks do not certify source truth, owner acceptance or later-source execution |
| P24 | [P24 / 6259327497](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/42#issuecomment-6259327497) | 2026-10-19 | Submitted 03:58:20 UTC; producer 7ec57425 and exact Workload/Deployment Mode leaves at 0009c66a | Actual in-session Apple engineering producer-integrity review | Five implemented P18 interface constraints received; no named-assignee reply, complete-note/vendor/runtime audit, numeric retention adoption or whole-#42 completion |
| P25 | [P25 / 6259463607](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/37#issuecomment-6259463607) | 2026-10-19 | Submitted 04:11:06 UTC; actual 05270b91 source and separate 04:10:02 UTC 528c guard; producer 7ec57425 and Deployment 08c3dacf | Actual coordinating deployment intake supported by independent in-session Apple interface review | Exact revision/target, independently qualified evidence/approvals, effective deployment and rollback/lifecycle gates; excludes the separate 90-rule follow-up and display/export correction. No deployment execution, named reply or SB-9 numeric adoption |
| P26 | [P26 / 6260214302](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/39#issuecomment-6260214302) | 2026-10-19 | Submitted 05:15:49 UTC; producer 7ec57425 and Cost Estimate dc97759e with exact source/gate/schema pins | Actual delegated cost receiving decision: accept with constraints | Historical/current/quantity/calculation/coverage distinctions; disclosure conditional on reviewed delivery of the exact display/export correction; P13 and the reverse #39 → #42 receipt remain separate. No new rate, cost estimate, runtime execution or policy default |
| P27 | [P27 / 6260217715](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/60#issuecomment-6260217715) | 2026-10-19 | Submitted 05:16:06 UTC; producer 7ec57425, rights 2fb0aa8d, integrations 159766a4 and source policy c8621123 | Actual delegated source-use receiving decision: accept with constraints | Actual material/use/view and retained-history boundaries, conditional on reviewed delivery of the exact display/export correction; no new permission, source audit, blanket history deletion, operating retention guarantee or SB-9 numeric adoption |
| P28 | [P28 / 6260273948](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/42#issuecomment-6260273948) | 2026-10-19 | Submitted 05:20:47 UTC; separately receives the four literal P24–P27 reviews | Actual coordinating decision on research handoff sufficiency | Current engineering delegation and actual roles stated explicitly; original P18/P19 named requests preserved. No absent person's reply, changed criterion text, implementation acceptance or automatic source/delivery/whole-issue completion |
| P29 | [Actual T5/SB-9 interface review6261613750](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/42#issuecomment-6261613750) | 2026-10-19 | Created 07:01:45 UTC; updated 07:01:56 UTC; producer 31ac26c9, note 3e4a67aa | Actual appletechie interface review; original #114 authorship expressly disclosed | Five P18 constraints and lifecycle classes accepted with limits; T5 classification and fork-display findings received above. No numeric adoption, execution, rights/vendor refresh, CI qualification or independent source authorship claimed |

Historical review disposition (2026-10-17): #41 confirmed the invalidation-event handoff. #40 has routed SB-1 to SB-10 and SB-R1 to SB-R5 for review; SB-8 is decided together with CD-1 answer states. Routing did not settle those schema decisions, and the PR remained a draft blocked by #40 at that time. The 2026-10-18 sequencing decision above supersedes that proposal-only merge hold; those contract decisions and the #42 prerequisite remained open at that sequencing decision. P21 records #40's later actual research completion. P22 supplies the separate later #431 receiving decision and P23 its reviewed delivery; none is retroactively attributed to this historical disposition.

## Retained input association diagnostics (2026-10-18)

The local [historical replay prototype](../../tests/t0_historical_replay_prototype.py)
now retains independently checkable associations for all selected historical
inputs when another input prevents reproduction. This extends the retained-report
correction delivered in [#383](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/383)
to the existing SB-2/SB-3 and SB-R2 identity checks. It changes neither the frozen
schemas nor the replay manifest/profile or existing reason-code vocabulary.

Actual synthetic probes on accepted
[`a219392b`](https://github.com/Pick-Your-AI/pick-your-ai-research/commit/a219392b64f82849b00f7da373b13661518354c4)
showed that all eight complete-input controls exposed their known mismatch:
resource/cost Build ID or revision, and ruleset/graph lock ID or version/revision.
Removing only the unrelated catalog hid all eight diagnoses, although each
affected artifact still resolved to its exact manifest-bound bytes. No evaluator
callback ran and no original input bytes changed. The expanded
[regression matrix](../../tests/test_t0_saved_input_associations.py) also covers
selection, rate, missing-sidecar, digest, reader-profile and unselected-artifact
boundaries. These are synthetic source observations, not measured estimates or
observations of a saved-build UI.

| Association | Inputs needed to establish a mismatch |
| --- | --- |
| Ruleset ID/version; graph ID/revision | The original Build locks and the independently resolved ruleset or graph |
| Resource, cost and report Build ID/revision; report locks | The original Build and the independently resolved derived record |
| Resource selection IDs; priced/unpriced cost selection IDs | The original Build selections and the independently resolved estimate |
| Cost Pricebook ID | The original Build's Pricebook lock and the independently resolved cost; an absent optional lock cannot admit a retained cost |
| Cost rate ID, selected item/version and meter | The independently resolved cost, original Build selections and exact resolved Pricebook matching the cost's Pricebook ID |
| Rate-to-catalog membership | Both exact resolved Pricebook and catalog |

Unavailable, unpinned, digest-mismatched or explicitly unsupplied records cannot
supply association claims. An unrelated newer or foreign archived record cannot
replace them. In particular, a missing Pricebook leaves rate comparisons
unavailable; it does not hide a selection ID or Pricebook-lock disagreement
already established from the original Build and exact cost bytes. All available
diagnostics are emitted once. Existing input-availability, digest, selection and
reader-profile status precedence remains; a mismatch still prevents evaluation.

Original Build, sidecar, manifest, estimates and report bytes remain unchanged.
A resolved content binding means the selected bytes were recovered; the separate
association diagnostic explains why those bytes do not support this saved Build.
It does not establish numerical accuracy, current price or capacity eligibility,
source authenticity, source-use permission or a new compatibility result. Current
consumer presentation, retained-report storage, successor migration and the
remaining SB/CD receiving decisions keep their existing owners and scope. The
separately delivered #377 diagnostic view remains its original controller's work;
this correction adds no replacement view or callback protocol. #40 and #42
acceptance remains open.
