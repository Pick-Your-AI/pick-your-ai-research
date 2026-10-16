# Agent Handoff Prompt — AI Builder Shared Contract v1.0.0

Implement your assigned portion of the AI Builder (PCPartPicker for AI) using the **attached `ai-builder-contract-v1.zip` as the common source of truth**. Read `AGENTS.md` and `README.md` first. The authoritative data interfaces are in `schemas/`, the core dependency and compatibility starting rules are in `baseline/`, the integration API is in `api/openapi.yaml`, and examples/tests are in `examples/` and `tests/`.

All agents MUST use the identical 29 component `kind` values, typed spec/settings, stable catalog IDs, selection IDs and roles, immutable catalog/build versions, cross-tier dependencies, three-state compatibility (`pass/fail/unknown` plus skipped rules), sourced rates, and version-pinned evidence. A component selection can impact dependencies in any other tier. When something changes, invalidate affected compatibility, hardware, pricing, quality and deployment evidence in both directions. Do not auto-adjust user selections without consent and do not treat missing data as compatible or free.

Work only within your assigned ownership area. Do not change another agent's definitions, independently decide a final compatible status, or create competing schemas. If new fields, enum values or component kinds are needed, submit a schema change with migration, dependency updates and tests for coordinated review. Use `secret://` references, never real credentials or customer content in JSON artifacts or events.

**Required before completion:** validate artifacts with `reference/validate_payload.py` and `python -m unittest discover -s tests -v`; supply changed JSON schemas, cross-tier rule/dependency changes, new positive and negative test fixtures, impact on other agent APIs, and any unresolved capability/cost/resource/evaluation unknowns.

**Do not** treat synthetic fixtures in `examples/` as real model/GPU specifications, prices, benchmarks, or approved deployments.
