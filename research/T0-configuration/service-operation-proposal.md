# Service-operation proposal for capacity evidence and saved builds

Status: **unaccepted research proposal**, observed 2026-10-18. Supplement to [#40's decision record](component-schema-compatibility.md), not a replacement. Refs research #10, #11, #40, #41, #42; receiving requests [website #16](https://github.com/Pick-Your-AI/pickyour.ai/issues/16) and [website #17](https://github.com/Pick-Your-AI/pickyour.ai/issues/17).

This document supplies reviewable choices for missing operations. It does not release an API version, select authentication or retention policy, assert a backend exists, or supply calibrated estimates. Do not merge it as an accepted shared contract without the affected owners' dispositions. Frozen `contracts/v1/` stays unchanged. #114's explicit hold until #40 closes remains in force.

## Inspected baseline and boundary

Primary repository sources, inspected 2026-10-18 at [`7115e77caf2d766b98d42dd8d75ee65325f2d4e7`](https://github.com/Pick-Your-AI/pick-your-ai-research/tree/7115e77caf2d766b98d42dd8d75ee65325f2d4e7):

- [OpenAPI](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/7115e77caf2d766b98d42dd8d75ee65325f2d4e7/contracts/v1/api/openapi.yaml): `POST /builds/{build_id}/resource-estimates` publishes evidence; no corresponding GET. `/builds` has POST; `/builds/{build_id}` has GET and conditional PUT, but no collection GET or DELETE. The relative `/v1` server is not a deployed service address.
- [ResourceEstimate](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/7115e77caf2d766b98d42dd8d75ee65325f2d4e7/contracts/v1/schemas/resource-estimate.schema.json): exact `build_id`, integer `build_revision >= 1`, immutable estimate identity, timestamp, estimator/version, metric/unit/value, confidence, assumptions and selection IDs. `source_uri` is optional; shape validity alone cannot establish calibration.
- [Reference evaluator](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/7115e77caf2d766b98d42dd8d75ee65325f2d4e7/contracts/v1/reference/evaluate.py): consumes one resource document, checks build identity/revision, and uses the first matching metric meeting the build's confidence threshold (default `calibrated`). It does not resolve competing documents, validate calibration evidence, or establish per-selection applicability merely by accepting a confidence label.
- [#114](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/114), inspected at `ea4c599501229f03c88d477f7530940ee1cfcc46`: proposed redacted sharing and revisit behavior; auth and SB-9 retention remain decisions. Its scoped #41 invalidation receipt is not general saved-build acceptance.
- [#146](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/146), inspected at `e7377460961651dea5b5dac950ebd7e726f22f5d`: field-dictionary proposal, not these service operations. Keep reviews separate; adopting field names would not approve transport or access policy.

## SO-1: revision-scoped resource-evidence read

**Proposed choice for #40 review:** add a GET collection under the same logical build resource in a separately published service-contract version. Preserve the v1 ResourceEstimate payload as a nested record; do not change its `schema_version` or put collection fields into that schema. API release identifier, version negotiation (path/header/media type), generated artifacts and migration notice need explicit #40 acceptance. No `/v1` addition is silently assumed.

Candidate operation, relative to that future version's root:

`GET /builds/{build_id}/resource-estimates?build_revision={revision}`

| Proposed element | Type / invariant | Why |
| --- | --- | --- |
| Path `build_id` | Canonical BuildSnapshot ID | One build scope, never a cross-account query |
| Required query `build_revision` | Integer >= 1 | No implicit current head; a build edit cannot silently change the evidence request |
| Optional query `cursor` | Opaque string | Continue the same revision-scoped result traversal; reject a cursor reused for another scope |
| Response `build_id`, `build_revision` | Same types and exact request values | Client checks envelope and every returned record against the requested immutable revision |
| Response `items` | Array of unchanged v1 ResourceEstimate records, possibly empty | Do not fabricate an estimate or a zero-valued metric when none exists |
| Response `next_cursor` | Opaque string or null | Null means collection traversal complete; no default page size selected here |

Proposed response envelope fields above are a design candidate, not a published schema. #40 must settle page-size bounds, stable ordering and snapshot/cursor semantics, error envelopes, and exact version encoding before generation. A traversal must not silently omit or duplicate evidence if new records are published between pages. Record IDs deduplicate retries. Client completion tests need a pinned response set, not a claim that an empty first page proves no evidence.

**Proposed handling:** 200 with an empty `items` collection for an existing, authorized build revision with no evidence. Reject missing/invalid revision rather than falling back to head. A missing revision and an unauthorized revision must follow the owner-approved disclosure/error policy; this proposal does not choose whether unauthorized existence is concealed with 404. Service/network failures remain distinguishable from a successful empty collection in the provider state, although neither can yield a confident fit result. Authentication applies to evidence as well as the build; access to a shared redacted build does not automatically authorize raw assumptions or source URLs.

The read operation returns evidence, not a compatibility verdict. Preserve all candidate records. No newest-record, first-record or highest-confidence selection is approved. Before passing one record to the existing evaluator, a client needs a separately accepted eligibility/conflict policy covering selection IDs, engine/model versions, workload/admission scope, estimator version, metric/unit consistency and conflicting same-metric rows. An unresolved selection or contradictory equally eligible evidence remains Unknown. Pagination order and timestamps cannot decide scientific validity.

### Synthetic receiving scenarios (not measurements)

| Example | Proposed observable behavior / gate |
| --- | --- |
| Request revision 7; head advances to 8 while reading | Return only revision-7 records. Never substitute revision 8; verify every row's `build_id` and `build_revision` |
| Revision 7 exists; complete result set is empty | Provider reports no evidence; capacity rules stay Unknown, never zero demand or a fit |
| Response envelope says revision 7; an item says revision 8 | Reject the mismatched response for evaluation; expose a scoped data error |
| One record labels a metric `estimated`; build requires `calibrated` | Display provenance with its actual confidence; metric stays Unknown for that policy |
| Two otherwise eligible records disagree on the same metric | Retain both for review; no first/newest wins shortcut; Unknown pending accepted conflict handling |
| Cursor is reused for another build/revision | Reject; do not leak or append records from the original scope |
| The source URI or a `calibrated` label exists without reviewed calibration | It does not satisfy website #16's genuine-evidence prerequisite |

### Evidence acceptance distinct from API acceptance

#10/#11 must provide or accept actual version-pinned estimator evidence for the consuming build scope: model/artifact and engine versions, device/topology and memory conditions, workload/context/concurrency/admission assumptions, estimator identity/version, measured-versus-estimated quantities and units, and reproducible calibration method/results or a scoped owner receipt referencing them. #41 reviews evidence eligibility and conflicts; source access and redistribution remain subject to rights review. Do not invent measurements, confidence upgrades, source rights or a threshold to make a fixture pass. Keep genuine external artifacts in authorized storage with permitted evidence manifests; fixtures stay synthetic.

An agreed read endpoint can unblock provider implementation and HTTP tests. It cannot by itself complete website #16: genuine eligible evidence and receiving-owner acceptance remain separate gates.

## SO-2: list and delete operations for saved builds

These operations need #42's privacy, authorization, sharing and retention decisions before an implementable wire contract. The table narrows the decision rather than choosing product policy.

| Candidate operation | Concrete contract work after owner decision | Owner decision still required |
| --- | --- | --- |
| `GET /builds` | Paginated summaries with stable identity/revision and cursor scope; payload has its own schema rather than pretending to be a BuildSnapshot. Test cross-account isolation and repeated-page consistency | Which principal can list which builds; whether shared/forked/archived builds appear; fields safe to list; authentication mechanism; order/filter/page bounds |
| `DELETE /builds/{build_id}` | Specify target (whole logical build vs revision), precondition and retry semantics, and observable terminal state. If asynchronous, define an operation/status resource before returning an accepted-but-incomplete result | Who may delete; tombstone vs immediate deletion; share revocation; retained historical evidence; backup/retention policy and erasure obligations |
| Read/revisit of a deleted or revoked share | Define status/body and cache behavior without returning prohibited retained data; test previously cached/shared references | Which retained metadata may be disclosed, to whom, and for how long; stale-source and comparison behavior from #114 |

For deletion, candidate choices for review are (A) synchronous completion with an explicit success response only after the defined deletion boundary is met, or (B) asynchronous acknowledgement plus an inspectable operation state. Neither acknowledgement nor tombstoning proves physical erasure. Do not select a retention duration, default visibility, auth provider, share capability format or deletion status code until the owners accept the semantics. Whole-build deletion and immutable revision history need an explicit reconciliation; a missing endpoint cannot be implemented by treating PUT as deletion.

### Synthetic receiving scenarios (owner outcomes pending)

- Account A attempts to list or delete account B's build: must not disclose or mutate B's data; exact error/disclosure policy awaits #42.
- An edit races with deletion: approved revision/precondition policy must produce a deterministic result; no silent deletion of a newer revision by an old client.
- The same delete request is retried after a lost response: specified retry semantics must avoid false completion claims or a second unrelated operation.
- A share link is visited after revocation/deletion: apply the accepted privacy and retention policy, including cached views; do not infer permission from a previously valid URL.
- A saved view is revisited after source changes: preserve historical versus current results per accepted #42 semantics; do not update history in place or invent freshness TTLs.

## Receiving checklist and owner decisions

Live assignees observed 2026-10-18; refresh before requesting acceptance. Routing is not acceptance and does not appoint a service implementer.

| Gate | Accountable research recipients | Exact evidence needed to unblock consumers |
| --- | --- | --- |
| SO-1 operation and release | #40 @tynamite / @zwright8 | Accept/narrow/reject proposed revision scope, collection/error/pagination semantics and API versioning; publish immutable generated contract reference |
| Capacity eligibility and real calibration | #10 @Mattycodes69 / @appletechie; #11 @zwright8 / @Mattycodes69; #41 @tynamite / @PUSHINGSQUARES | Scoped method/data and acceptance receipts; decide ambiguity handling and selection/metric applicability; no synthetic confidence substitution |
| SO-2 saved-build policy | #42 @tynamite / @appletechie, with #41 and affected #37/#60 handoffs | Accepted privacy/auth/retention/sharing/revisit decisions, then list/delete schemas and lifecycle/error cases; retain #114's hold |
| Backend implementation | Existing service-delivery owner to be identified through parent coordination | Authorized service base URL/version, supported operations, access policy, persistence behavior and contract/integration test evidence; research approval does not supply these |
| Website/mobile integration | Receiving repository issue owners | Immutable accepted contract revision plus actual provider tests; compatibility remains Unknown without eligible evidence; do not enable HTTP persistence merely because this note exists |

For website #16, sequence the receipts: operation agreement → generated/versioned artifacts → backend read capability → provider tests and real evidence eligibility → scoped receiving acceptance. Backend delivery and calibration can proceed independently once their inputs are agreed. For website #17, #42 acceptance and concrete backend authorization/persistence behavior must precede enabling `VITE_BUILD_STORE=http`. Neither issue is closed by this proposal.

## Validation and migration plan

This prose-only supplement introduces no executable schema or fixture, so existing validators check repository integrity, not this proposed behavior. Before adopting it, #40 must add versioned schema/OpenAPI generation and tests for every agreed request/response/error scenario, preserve imported v1 hash/evaluator checks, document supported client versions and fallback behavior, and request affected-owner review. Existing v1 consumers keep their current behavior; no transport auto-upgrade is authorized. Client and backend tests belong in their implementation repositories after the contract is accepted.
