# Research submissions

## Start with your issue

1. Read the issue's user decision and deliverable path. Use [the mapping](CONTRACT_MAPPING.md) to find your canonical kinds and schemas.
2. Copy [the research note template](../templates/research-note.md) to the existing `research/<workstream-slug>/<component-slug>.md` path. Record incomplete findings there immediately.
3. Compare candidates and collect claim-level sources, dates, versions, units, conditions, and unknowns. Link each claimed field to its evidence in the note. A vendor statement and an independently reproduced result are different evidence grades.
4. When required facts are available, add one `CatalogItem` JSON file per item/version under `catalog/proposals/`. Add complete `Pricebook` proposal files under `pricing/proposals/` for prices. Use the matching schema's required fields, not arbitrary fields from an issue's conceptual comparison list.
5. Run validation and open a PR referencing the issue. Include the research note and any structured files. Use `Refs #n` for partial work; use `Closes #n` only when the issue's acceptance criteria and handoffs are satisfied.

Merging a proposal makes it reviewed research. It does not publish a production catalog, approve a deployment, or certify that every claim is correct forever.

## Formats and unknowns

| Finding | Format |
| --- | --- |
| Incomplete discovery, comparison, decision, source-to-field mapping | Research note |
| Sufficiently documented component facts | `contracts/v1/schemas/catalog-item.schema.json` |
| Dated rates and conditions | `contracts/v1/schemas/pricebook.schema.json` |
| Proposed cross-component rule | Research note using [rule proposal template](../templates/rule-proposal.md); reviewed by #40 before a versioned ruleset |
| Actual measured quality or capacity evidence | Matching `quality-evaluation-run` or `resource-estimate` schema, with real version-pinned inputs; agree placement/consumer with #36 or #10 before submission |
| Large or restricted supporting artifact | One metadata JSON per artifact under `evidence/`, using [the manifest schema](../schemas/evidence-manifest.schema.json) |

For a catalog item, consult `spec_<kind>` in the schema and the [field guide](../contracts/v1/docs/COMPONENTS.md). Do not copy a fictional example and leave demo values behind. If a required model context limit is unknown, the note is valid research but the item is not yet a complete catalog proposal. Do not use `null`, zero, or an estimate as a substitute unless the field's documented semantics permit it.

Each catalog provenance entry and price-rate provenance must contain a public HTTP(S) source URL and the contract's date/status fields. Link unavailable/private evidence through a note and sanitized manifest; keep those catalog claims in notes until they meet the public proposal requirement. Distinguish source checking from independent verification: a source-checked claim was read against its cited source on the access date; independently verified means reproduced or corroborated with eligible independent evidence, as described in the claim note. For new provenance, use `unverified` for source-checked claims lacking that evidence, and reserve `verified` for claims with linked independent support. Historical `verified` entries admitted under the former source-check convention are not automatically independently verified; inspect the claim note before presenting that grade. Keep `user_supplied` and `estimated` distinct, and do not bulk-relabel old records or change frozen v1 enums. See the [#41 label mapping](../research/T0-configuration/catalog-data-sources.md#mapping-evidence-labels-to-frozen-v1). Missing or uncertain billing classification remains `unknown`.

Catalog references must resolve to proposals in this repository. Submit referenced providers, hosts, or sources in the same PR or reference already merged records. Because v1's catalog spec references use IDs without versions, this intake currently permits one version per catalog ID to avoid ambiguous resolution. Propose multi-version snapshot intake through #40 before adding historical versions under a single ID. Price rates must reference that item's exact version.

## Validation

From the repository root, with Python 3.12:

```bash
python -m pip install -r requirements-research.txt
python -m unittest discover -s contracts/v1/tests -v
python -m unittest discover -s tests -v
python scripts/validate_research.py
python scripts/validate_market_research.py
python scripts/validate_handoff_audit.py
python prompts/mobile/validate_prompts.py
```

To inspect one payload separately:

```bash
python contracts/v1/reference/validate_payload.py contracts/v1/schemas/catalog-item.schema.json catalog/proposals/YOUR-FILE.json
```

CI runs the same checks. It validates schemas, import integrity, generator consistency, canonical-kind coverage, local catalog references, exact price references, duplicate IDs, public provenance URL shape, date ordering, and external-artifact metadata. It rejects reserved fixture IDs/example domains in real proposals. Catalog, pricebook and evidence JSON must have unique object keys at every level; conflicting or repeated keys are rejected before schema validation rather than silently choosing a value. Non-finite numeric literals and numbers that overflow the intake's finite numeric range are also rejected. This stricter submission parsing does not change the frozen v1 contract. It does not fetch sources, verify remote hashes or rights, establish freshness, prove claims, or guarantee secrets are absent. Reviewers must check those matters and compare prior revisions for unintended fact changes.

Price validity ordering supports ASCII timestamps with Gregorian years `0001` through `9999`, seconds `00` through `59`, uppercase or lowercase `T`/`Z`, and numeric offsets through `23:59` in either direction. It compares whole UTC seconds and the full fractional digit sequence without rounding or truncating to microseconds. Offset-equivalent timestamps and fractions differing only in trailing zeros are equal, so they cannot define a positive validity interval. Numeric offsets are subtracted from local time; see [RFC 3339 sections 4.2 and 5.6](https://www.rfc-editor.org/rfc/rfc3339.html#section-4.2) (checked 2026-10-18). The original timestamp strings and submission bytes are preserved.

Both `valid_from` and any supplied `valid_until` receive this intake check, including an open-ended rate's start. The pinned requirements do not install the optional `date-time` format checker, so passing the frozen-schema validation step does not establish timestamp format support. Unicode-digit and leap-second representations that reach intake ordering are deliberately unsupported by this profile and produce a field-specific diagnostic instead of a traceback. [RFC 3339 section 5.7](https://www.rfc-editor.org/rfc/rfc3339.html#section-5.7) permits leap seconds under its stated conditions; this intake does not implement that calendar. The frozen v1 schema remains unchanged. Successful ordering establishes neither a price's freshness nor its eligibility for a consumer.

Catalog and price provenance URLs and evidence-manifest locators reject whitespace, raw ASCII control characters, user information (including empty credential syntax), and invalid specified ports. Validation checks the original string before parsing: Python's [URL parser](https://docs.python.org/3.12/library/urllib.parse.html#urllib.parse.urlsplit) (checked 2026-10-18) can strip control characters and defers port validation until the port property is read. Public provenance remains HTTP(S); external manifests remain stable HTTPS/S3/GS locators without queries or fragments. These syntax checks perform no network access or source/rights verification.

The market integrity reader applies the same duplicate-key, non-finite-number and numeric-overflow rejection to its five inputs: `competitors.json`, `sources.json`, `features.json`, `research-backlog.json` and `integrations.json`. It rejects ambiguous raw JSON before interpreting the market evidence or priority records, including under optimized Python.

Each top-level source-register record also requires nonempty text for
`access_date` and `access_status`. Its access date must be an actual calendar
date in `YYYY-MM-DD` form. Free-form statuses, including blocked or unverified
access, retain their original text. This checks the two existing fields without
rewriting source or recheck records; a well-formed date/status does not establish
successful retrieval, freshness, source truth or receiving acceptance.

Source-register `rechecks`, when present, must be an array. Each entry retains
one of the existing representations: a singular `claim` record or a nonempty
`claims` array. They cannot appear together. Each recheck needs a real
`YYYY-MM-DD` access date and nonempty access status, version, region, confidence,
limitations and rights text. Each claim needs its own text, publisher, evidence
class and either a single `url` or a nonempty `source_urls` list; every supplied
URL representation receives the existing HTTP(S) syntax checks. Grouped records
also need their method and nonempty `reviewed_urls` entries with URL, publisher
and access status. This preserves the seven historical singular claim records
as well as grouped claims, without converting or rewriting either format.
Empty recheck arrays and records that explicitly describe unknowns or failed
access remain valid. These checks do not retrieve the URLs, authenticate the
metadata, judge claim support or evidence grades, establish freshness or grant
source-use permission.

The market backlog's issue numbers and specified parent numbers must be positive JSON integers. Boolean or floating-point aliases cannot identify an issue; only an absent or null parent means no parent. Its six priority factors follow the existing [ordinal 1–5 rubric](market-research/research-methodology.md#priority-rubric): each is a JSON integer token or null. The total must be a JSON number matching the unchanged weighted calculation, or null when any factor is unknown. Its original numeric token must equal that result exactly; float rounding cannot conceal a fractional difference. Numerically equivalent decimal or exponent spellings remain valid for the total, while factors retain their integer-token requirement. Booleans cannot stand in for a numeric total. These checks preserve the recorded graph and score shape; they do not assess the scoring judgments or establish issue completion.

Every non-Unknown feature cell also needs its existing claim-level fields: `basis`, `verification_method`, `evidence_grade`, `evidence_url`, `access_date`, `confidence`, `limitations` and `audit_scope`, in addition to resolvable `evidence_ids`. These must be nonempty text; both the source-register and exact claim URLs must use HTTP(S) with a hostname, without credentials, whitespace or raw ASCII control characters, and with a valid port when specified. Shared URL checks inspect the original string as well as the parsed fields so parser normalization cannot conceal invalid control bytes. The claim access date must be an actual calendar date in `YYYY-MM-DD` form. Unknown cells may remain incomplete. These checks enforce record shape, not source support, freshness, rights, evidence-grade correctness or completion of the feature's bounded test.

The 21 original tests exercise the synthetic contract examples. They are not a substitute for the separate submission validator. Arbitrary resource/evaluation JSON files are not automatically ingested by this validator; add explicit validation coverage in their PR.

The handoff audit validator checks consistency among `handoffs.json`, `handoff-audit-readback.json` and `audit.json`. Its reader first rejects duplicate JSON object keys, non-finite constants and numeric overflow in all three files, including under optimized Python. It then rejects duplicate snapshot issue IDs, pull-request IDs, declared handoff pairs and historical review pairs before relying on their indexed identities. Conflicting entries cannot be silently discarded to obtain a passing audit. These checks preserve recorded attribution; they do not fetch live GitHub state or establish receiving-owner acceptance.

Each scoped response in both the ledger and readback must retain nonempty text
for `reviewer`, `url`, `scope`, `retained_unknowns_and_next_action`, `submitted_at`
and `commit_basis`. Matching copies of a Boolean, number, container or blank
string do not satisfy these fields. Validation preserves the original text and
permits an explicitly unknown `reviewed_commit` with a nonempty basis; it does
not certify the statement, source URL, timestamp or receiving decision.

An identical scoped response cannot be recorded more than once for the same
producer/consumer pair. The ledger and readback are checked separately before
totals are compared. Different handoff pairs and distinct scoped records may
cite the same source URL; duplication checks do not infer source authority or
receiving acceptance. Reordering the response records does not affect their
reconciliation; every field and nested-array order remains part of the complete
record identity.

The snapshot cutoff and every historical or new receipt's `submitted_at` must
be real, timezone-aware timestamps. The audit profile accepts ASCII
`YYYY-MM-DDTHH:MM:SS`, optional one-to-six-digit fractional seconds, and an
explicit `Z` or signed `HH:MM` offset. It compares the resulting UTC instants,
including the cutoff itself, so lexical ordering or duplicate copies of an
invalid date cannot admit a post-cutoff receipt. Original evidence strings are
preserved; valid timestamps alone do not authenticate a review or its scope.

Issue and pull-request identities in the audit, snapshot, handoff pairs and native
parent/child/blocker references must be positive JSON integers. Booleans and
floating-point aliases cannot match an integer identity through Python equality.
This identity check does not change numeric fields in unrelated evidence metadata.

Native parent/sub-issue links must be reciprocal, contain no repeated child IDs,
and form an acyclic hierarchy. The validator checks these captured relationships
without reordering or rewriting the snapshot. Separate information handoffs and
`blocked_by` links are not treated as parent edges. This offline consistency
check does not fetch live GitHub relationships or establish issue completion.

Technical audit classifications must reference captured issue IDs without
repeating an issue. They may cover a subset of the captured issues; this check
does not create classifications or establish current receiving-owner acceptance.

The public-provenance shape check requires an IP literal's globally reachable classification and excludes multicast, reserved and deprecated IPv6 site-local addresses. This conservative intake also excludes reserved translation-prefix literals. IPv4-mapped IPv6 literals use the embedded address's classification. Domain hosts pass through UTS #46 compatibility mapping and IDNA label validation from pinned `idna==3.20` before the reserved-domain and IP checks; bracketed IPv6 literals retain their separate address check. Python's standard-library IDNA2003 codec alone misses some mappings, including segmented digits and modifier letters that browsers normalize to loopback or reserved hosts. Valid internationalized publisher names remain eligible, while malformed labels, ambiguous legacy numeric hosts, percent-encoded or interface-scoped hosts, and hostnames containing a backslash are rejected. See the [pinned package documentation](https://pypi.org/project/idna/3.20/) and [Unicode UTS #46 processing](https://www.unicode.org/reports/tr46/) (checked 2026-10-18). This is a conservative offline intake check, not a complete browser URL implementation: DNS names still require an actual public-access and source-evidence review, and an accepted IP shape does not establish that a publisher or document exists there. The stricter label check supplies no DNS resolution, connection or redirect protection.

The market validator also reads `research/market/integrations.json`. Its research
shortlist must reference existing competitor/source IDs, use distinct positive
integer investigation ranks covering the shortlist, and retain dated access and
rights observations, governing HTTP(S) terms links, and all four intended-use
decisions with their conditions and basis. The shortlist remains `Not approved
for integration`: a conditional source permission is separate from product
eligibility. A recorded current-product exclusion must keep retrieval, display
and redistribution disabled. These checks establish record integrity, not legal
permission, source freshness or a receiving owner's acceptance.

Each shortlist row's `research_assessment` explains its investigation priority,
estimated maintenance assumptions, separate code/data material boundaries and
named unresolved decisions. Its assessment date is the analyst-review date;
`access_date` and `last_checked` retain their actual source-check scope. A new
assessment does not refresh terms or turn an estimate into a measurement. These
are market research notes, not a new frozen contract, runtime entitlement or
integration approval format.

## Review and ownership

- Existing issue assignees own research decisions. Request affected owners' review for handoffs; preserve live assignments.
- #40 is the contract and compatibility review entry point. #41 owns evidence/freshness policy; #39 owns pricing semantics. These issues remain open until their full research acceptance criteria are met.
- New fields, kinds, enum values, or units require a contract proposal with owner, examples, dependency impact, and version/migration plan. Do not silently alter v1.
- Review proposed rules centrally; a catalog author must not publish a final universal compatibility boolean. Record outcomes and severities separately.

## What belongs in Git

Commit small textual research notes, sanitized structured proposals, source manifests, schemas, generators, and regression fixtures. Keep fixtures clearly synthetic. Store raw crawls, large datasets, model weights, recordings, private documents, and credentials outside this public repository. Manifest URLs must be stable locators without signed query strings or credentials; record how authorized users obtain access. A checksum describes an artifact, not permission to redistribute it.

## Pre-merge issue-closure check

Immediately before each merge, fetch the **current PR body, commit messages and linked-issue state**, even when CI already passed. GitHub recognizes closing keywords in PR descriptions and commit messages; plain-English negation does not provide a safe cancellation mechanism. A range can still contain a closing reference to its first issue. See [GitHub's linking documentation](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue) (checked 2026-10-18).

For partial work, use `Refs` and write that the issues remain open. Remove keyword/reference combinations from negated sentences, quotations and examples in PR metadata. Inspect manually linked issues too: this text check cannot see or unlink them.

Save the freshly fetched PR body and commit messages as local UTF-8 text files, then run:

```bash
python scripts/check_closing_directives.py /tmp/pr-body.txt /tmp/commit-messages.txt
```

The conservative checker rejects detected directives by default. For an intentional closure, first verify every acceptance criterion and required receiving-owner receipt. Put each intended directive on its own unindented plain line in an isolated paragraph containing only reviewed directives; pass its exact target with `--allow '#123'` (or the exact repository-qualified reference/issue URL). Repeat for each reviewed target. An allowlist is a reviewer declaration, not proof of completion. Negated, ranged, prose-embedded or indented directives still fail even if a target is allowed. Fenced examples remain ineligible across blank lines, including unclosed fences.

This offline check uses a deliberately limited detector, not GitHub's full Markdown/linking parser. Passing it does not certify all issue links, current permissions or acceptance. Re-read live metadata and any proposed merge message before the expected-head merge. Afterward verify intended issue states **and Project statuses**; reopening an accidentally closed issue does not prove its Project status was restored. Report inaccessible Project fields without bypassing access restrictions.
