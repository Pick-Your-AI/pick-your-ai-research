# Research adoption of contract 1.0.0

Start with [the researcher workflow](../../docs/RESEARCH_WORKFLOW.md). The original README describes an implementation handoff; researchers need only their issue's schemas and the shared evidence rules.

This directory imports the supplied `ai-builder-contract-v1` package. All 43 original manifest entries were verified against their SHA-256 hashes before import. `IMPORT_MANIFEST.json` records source paths, repository paths, and hashes. `UPSTREAM_SHA256SUMS` is the unchanged original checksum list; two files were relocated:

- `AGENTS.md` → `docs/IMPLEMENTATION_AGENTS.md`
- `HANDOFF_PROMPT.md` → `docs/IMPLEMENTATION_HANDOFF.md`

Those documents are retained as implementation reference, not active researcher instructions. The original README's links to those old paths should be read through this mapping. The original ZIP remains with its supplier; no release or archive upload is required to use this checked-in contract.

Schemas, source generators, API/storage references, synthetic examples, tests, and baseline rules are retained together to preserve reproducibility. No original schema or external API field was changed during adoption. The schema `$id` URLs under `schemas.ai-builder.example` are identifiers resolved locally by the validator, not a hosted service.

## Review boundaries

The baseline's 59 dependency edges and 45 rules are starting proposals. Passing fixture tests does not validate real vendor facts, GPU capacity, pricing, or production readiness. The reference evaluator is an illustrative implementation, not an approved deployment gate.

Research submission checks add evidence URL requirements without modifying v1: its provenance type permits an absent URL. Incomplete required facts stay in notes; missing values must not become false, zero, or a made-up value. Current v1 also lacks some billing meters (such as egress), so report uncovered costs and propose extensions through #40/#39.

The optional `model.spec.license_ref` is an opaque string in v1; no license registry or reference format is defined. Intake resolves catalog references to component kinds but leaves this field for evidence review. Link the actual license and its terms in the research note. Any stronger license-reference contract requires #40 review.

Rule outcomes are `pass/fail/unknown/skipped`; rule severity is `info/warning/error`. Earlier issue wording that grouped compatibility states as severity is conceptual, not a JSON enum to copy.

## Maintenance

The import is a frozen baseline. Propose a reviewed next version through #40 rather than changing these bytes in place. Keep generator, generated schemas, docs, fixtures, and tests together in the new version. Record compatibility/migration consequences and affected workstreams. Import-hash verification deliberately fails if the frozen baseline changes.

`tests/test_research.py` also regenerates schemas, fixtures, and component documentation in a temporary copy and compares their content. Run generators only in that temporary copy when checking this baseline.
