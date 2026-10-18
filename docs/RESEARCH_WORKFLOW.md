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

CI runs the same checks. It validates schemas, import integrity, generator consistency, canonical-kind coverage, local catalog references, exact price references, duplicate IDs, public provenance URL shape, date ordering, and external-artifact metadata. It rejects reserved fixture IDs/example domains in real proposals. It does not fetch sources, verify remote hashes or rights, establish freshness, prove claims, or guarantee secrets are absent. Reviewers must check those matters and compare prior revisions for unintended fact changes.

The 21 original tests exercise the synthetic contract examples. They are not a substitute for the separate submission validator. Arbitrary resource/evaluation JSON files are not automatically ingested by this validator; add explicit validation coverage in their PR.

## Review and ownership

- Existing issue assignees own research decisions. Request affected owners' review for handoffs; preserve live assignments.
- #40 is the contract and compatibility review entry point. #41 owns evidence/freshness policy; #39 owns pricing semantics. These issues remain open until their full research acceptance criteria are met.
- New fields, kinds, enum values, or units require a contract proposal with owner, examples, dependency impact, and version/migration plan. Do not silently alter v1.
- Review proposed rules centrally; a catalog author must not publish a final universal compatibility boolean. Record outcomes and severities separately.

## What belongs in Git

Commit small textual research notes, sanitized structured proposals, source manifests, schemas, generators, and regression fixtures. Keep fixtures clearly synthetic. Store raw crawls, large datasets, model weights, recordings, private documents, and credentials outside this public repository. Manifest URLs must be stable locators without signed query strings or credentials; record how authorized users obtain access. A checksum describes an artifact, not permission to redistribute it.
