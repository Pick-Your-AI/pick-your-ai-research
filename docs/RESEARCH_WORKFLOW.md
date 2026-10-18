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
python prompts/mobile/validate_prompts.py
```

To inspect one payload separately:

```bash
python contracts/v1/reference/validate_payload.py contracts/v1/schemas/catalog-item.schema.json catalog/proposals/YOUR-FILE.json
```

CI runs the same checks. It validates schemas, import integrity, generator consistency, canonical-kind coverage, local catalog references, exact price references, duplicate IDs, public provenance URL shape, date ordering, and external-artifact metadata. It rejects reserved fixture IDs/example domains in real proposals. Catalog, pricebook and evidence JSON must have unique object keys at every level; conflicting or repeated keys are rejected before schema validation rather than silently choosing a value. Non-finite numeric literals and numbers that overflow the intake's finite numeric range are also rejected. This stricter submission parsing does not change the frozen v1 contract. It does not fetch sources, verify remote hashes or rights, establish freshness, prove claims, or guarantee secrets are absent. Reviewers must check those matters and compare prior revisions for unintended fact changes.

Catalog and price provenance URLs and evidence-manifest locators reject whitespace, raw ASCII control characters, user information (including empty credential syntax), and invalid specified ports. Validation checks the original string before parsing: Python's [URL parser](https://docs.python.org/3.12/library/urllib.parse.html#urllib.parse.urlsplit) (checked 2026-10-18) can strip control characters and defers port validation until the port property is read. Public provenance remains HTTP(S); external manifests remain stable HTTPS/S3/GS locators without queries or fragments. These syntax checks perform no network access or source/rights verification.

The market integrity reader applies the same duplicate-key, non-finite-number and numeric-overflow rejection to its four inputs: `competitors.json`, `sources.json`, `features.json` and `research-backlog.json`. It rejects ambiguous raw JSON before interpreting the market evidence or priority records, including under optimized Python.

Every non-Unknown feature cell also needs its existing claim-level fields: `basis`, `verification_method`, `evidence_grade`, `evidence_url`, `access_date`, `confidence`, `limitations` and `audit_scope`, in addition to resolvable `evidence_ids`. These must be nonempty text; both the source-register and exact claim URLs must use HTTP(S) with a hostname, without credentials, whitespace or raw ASCII control characters, and with a valid port when specified. Shared URL checks inspect the original string as well as the parsed fields so parser normalization cannot conceal invalid control bytes. The claim access date must be an actual calendar date in `YYYY-MM-DD` form. Unknown cells may remain incomplete. These checks enforce record shape, not source support, freshness, rights, evidence-grade correctness or completion of the feature's bounded test.

The 21 original tests exercise the synthetic contract examples. They are not a substitute for the separate submission validator. Arbitrary resource/evaluation JSON files are not automatically ingested by this validator; add explicit validation coverage in their PR.

The handoff audit validator checks consistency among `handoffs.json`, `handoff-audit-readback.json` and `audit.json`. Its reader first rejects duplicate JSON object keys, non-finite constants and numeric overflow in all three files, including under optimized Python. It then rejects duplicate snapshot issue IDs, pull-request IDs, declared handoff pairs and historical review pairs before relying on their indexed identities. Conflicting entries cannot be silently discarded to obtain a passing audit. These checks preserve recorded attribution; they do not fetch live GitHub state or establish receiving-owner acceptance.

The public-provenance shape check requires an IP literal's globally reachable classification and excludes multicast, reserved and deprecated IPv6 site-local addresses. This conservative intake also excludes reserved translation-prefix literals. IPv4-mapped IPv6 literals use the embedded address's classification. Hostnames pass through Python's IDNA codec before the reserved-domain and IP checks, so Unicode forms that normalize to those hosts receive the same checks. Ambiguous legacy numeric hosts, percent-encoded or interface-scoped hosts, and hostnames containing a backslash are rejected; use a canonical public IP literal or publisher hostname. This is an offline intake check: DNS names still require an actual public-access and source-evidence review, and an accepted IP shape does not establish that a publisher or document exists there.

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
