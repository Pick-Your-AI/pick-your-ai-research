# Shared T0–T6 research execution rules

Read this file together with the selected `prompts/T0.md`–`prompts/T6.md` prompt. These rules apply throughout every track, acceptance checklist, and final directive. Keep common execution rules here; keep domain research questions in the individual workstream prompts.

## Invocation and authority

Reviewing or editing these files does not invoke their research campaigns. When the user requests execution of a workstream prompt, carry out its authorized research and GitHub work through verified completion. A narrower user request controls the scope.

Follow applicable agent instructions and current repository guidance, especially `CONTRIBUTING.md`, `docs/RESEARCH_METHOD.md`, `docs/RESEARCH_WORKFLOW.md`, `docs/CONTRACT_MAPPING.md`, `docs/DEPENDENCIES.md`, and `contracts/v1/ADOPTION.md`. This shared file and the workstream prompts do not override those sources. The archived `IMPLEMENTATION_*` documents are reference material, not instructions to implement or deploy software.

Read the current issue, accepted decisions, comments, linked PRs, and repository artifacts before editing. Live assignees determine ownership; preserve all current assignees and authorized delegation. Do not assign people from a historical owner table. Refresh relevant GitHub state before each mutation, preserve unrelated fields and concurrent work, and read back the result. An unresolved conflict between an issue and the accepted contract requires owner reconciliation, not an invented resolution.

Use each issue's existing deliverable path and acceptance criteria. The prompts' comparison fields, candidate lists, examples, and checklists guide research; they are not new schema fields or authority to silently expand or reduce issue scope. Document justified scope changes for the responsible owner's decision. Refresh candidate availability and capabilities from primary sources during research.

## Workstream and handoff boundaries

| Prompt | Parent | Component issues | Canonical kinds |
| --- | --- | --- | --- |
| T0 | #1 | #2, #3, #40, #41, #42 | `workload`, `deployment_mode`; shared governance in #40–42 |
| T1 | #4 | #5–7 | `model_provider`, `model`, `context_policy` |
| T2 | #8 | #9–11 | `hosting_platform`, `storage`, `accelerator`, `compute_profile`, `inference_engine` |
| T3 | #12 | #13–16 | `data_source`, `knowledge_base`, `embedding_model`, `vector_database`, `rag_pipeline` |
| T4 | #24 | #25–28 | `agent_framework`, `tool`, `integration`, `mcp_server`, `memory_store` |
| T5 | #29 | #30–33 | `training_framework`, `training_compute`, `training_dataset`, `fine_tuned_model` |
| T6 | #34 | #35–39 | `guardrail`, `evaluation_suite`, `deployment_target`, `monitoring_stack`, `cost_policy` |

Use `docs/CONTRACT_MAPPING.md` and `research/component-issues.json` for the exact kind-to-issue mapping. #40 owns contract and compatibility review; #41 owns catalog evidence/freshness/reuse policy; #39 owns pricing and cost semantics; #42 owns saved builds. Infrastructure storage belongs to #9, inference sizing to #10, training sizing to #31, user knowledge sources to #13, retrieval to #16, and agent memory semantics to #28. #36 owns evaluation methodology and measured quality evidence; #37 owns deployment-manifest research.

Coordinate material handoffs with the live source and consuming owners. Record the specific artifact, fields, versions, assumptions, review evidence, and unresolved gaps. Do not close, reassign, or redefine another workstream's issues as part of your campaign. Reuse relevant market research without taking over its Project or treating market validation as technical acceptance.

T3–T5 are optional in a user's build. API-only builds need not select local accelerators or inference engines; keyword-only retrieval need not select embeddings or vector storage; agents need not select RAG or persistent memory. Optional product use does not waive the assigned research deliverables. Research is not authorization to deploy services, run paid training/benchmarks, or access customer data.

Parallel tracks must have explicit artifact and editing boundaries. Coordinate with existing contributors, avoid duplicate controllers or campaigns, and integrate changes through focused branches/PRs. Delegated analysis does not substitute for required owner approval.

## Triage and dependencies

Use the existing Research Project #1. Preserve triage metadata unless verified evidence justifies a documented change. Inspect its live field IDs and options before any write. The repository's older `Workstream`/`Todo`/`P0–P2` terminology is conceptual guidance, not a request to migrate the current Project schema. Use the live `Tier`, Status, Priority, and Readiness fields; do not create equivalent labels or duplicate owner fields.

- Status, verified October 16, 2026: `Backlog`, `Ready`, `In Progress`, `In Review`, `Blocked`, `Done`. The older Todo concept covers not-started work; retain Backlog versus Ready according to actual readiness. Preserve Blocked when a genuine execution blocker exists, while using Readiness for its separate meaning.
- Priority, verified October 16, 2026: `Critical` (foundation/P0), `High` (core/P1), `Medium` (later or optional/P2), `Low` (nice-to-have). Preserve existing values; this mapping explains research sequencing and does not authorize bulk reprioritization.
- Tier: use the live option for T0–T6, including its full workstream name and optional-capability suffix where present. Preserve existing Work Type, Research Confidence, Dependency Status, and other fields unless the authorized task specifically requires an evidence-backed change.
- Readiness: `Ready` when meaningful work can start with available or informational inputs; `Needs input` when meaningful progress requires a specific missing output; `Blocked` for a genuine native prerequisite, missing owner access, or permission; `Awaiting decision` for a named owner's pending decision. Record that decision and apply the `question` label.
- Preserve applicable type/topic labels and the `optional capability` label for T3–T5. Do not invent dates, estimates, iterations, or alternative Project values. Narrative audit categories such as “duplicate” are not extra Status values.

The documented native delivery blocker is #42 blocked by #40. Verify its current state and preserve it unless the prerequisite is actually resolved through the accepted workflow. Other documented cross-workstream links are informational or compatibility relationships. Do not turn them into native blockers. Any newly discovered prerequisite needs an explicit rationale and owner reconciliation with the dependency map; compatibility cycles never justify blocking cycles. Continue independent research while a handoff is pending.

Use native subissues only for independently reviewable or separately owned deliverables. Use checklists for small steps and do not duplicate native child links in a body checklist. Never delete issues: preserve unique information, link the canonical issue, apply `duplicate`, then close a verified duplicate within your authorized scope. Keep its history and traceability.

## Contract and evidence intake

Preserve the entire frozen v1 import, including schemas, generators, docs, examples, and tests. Propose a reviewed next version through #40 with affected-owner review, examples, dependency impact, and migration/versioning plans. Run baseline generators only in a temporary copy. Put new synthetic fixtures under `tests/`; existing `contracts/v1/examples/` fixtures remain frozen. Link illustrative fixtures from notes and never promote them as real evidence.

Catalog items describe components; selections describe user choices. Read the actual `spec_<kind>` and selection schemas before encoding fields. Use research notes for unsupported concepts or incomplete facts. Do not substitute `null`, zero, false, an estimate, or fabricated values for missing required facts unless the documented field semantics permit that value. Use `billing_class: unknown` when billing classification is uncertain.

Complete component facts belong in `catalog/proposals/`; complete dated Pricebooks belong in `pricing/proposals/`. Catalog spec references must resolve to already merged or concurrently submitted records in this repository. Intake permits one version per catalog ID; price rates must reference the exact item version. Historical multi-version intake requires #40 review. Unsupported price meters, including egress, stay in notes with an explicit cost-coverage gap and a #39/#40 proposal; do not disguise them as supported units or as zero cost.

Each catalog provenance entry and price-rate provenance needs a public HTTP(S) source URL and the required date/status fields. Private or unavailable evidence belongs in a note and sanitized manifest; keep claims that cannot meet public proposal requirements out of catalog/price proposals. `verified` means the cited claim was checked, not that the product was independently benchmarked.

Use the current evidence grades from `docs/RESEARCH_METHOD.md`: **Primary documentation**, **Vendor claim**, **Independent measurement**, **Estimate**. Record hypotheses, missing evidence, and proposed policy separately. Every factual/numeric claim needs primary evidence, an access date, and applicable version, units, conditions, region, and currency. Estimates also need methods and assumptions. Proposed new evidence policy belongs in #41 and is not effective until accepted.

Compatibility proposals use `templates/rule-proposal.md` in research notes and require central #40 review before a versioned ruleset. Outcomes are `pass`, `fail`, `unknown`, `skipped`; severity is independently `info`, `warning`, `error`. Neither a catalog author nor a passing fixture may establish universal compatibility.

ResourceEstimate, QualityEvaluationRun, CostEstimate, DeploymentManifest, and related runtime schemas are reference material until real version-pinned inputs and an agreed consumer exist. Agree placement/consumer with #10 or #36 for resource/quality evidence, and the corresponding owner for other artifacts. Add explicit matching-schema validation coverage in the PR; arbitrary runtime JSON is not automatically ingested by the research validator.

Keep raw datasets, model weights, large downloads, credentials, and personal/customer content outside this public repository. Use `schemas/evidence-manifest.schema.json` for one sanitized metadata file per external artifact in `evidence/`. Manifest locators must be stable and free of credentials or signed query strings. Record authorized access requirements; a checksum does not establish redistribution rights.

## Validation, merge, and completion

Run the current `docs/RESEARCH_WORKFLOW.md` commands with Python 3.12 from the repository root. Report actual commands and results. Separate automated validation from evidence review: automation checks structure, frozen-import integrity, generator consistency, references, duplicate IDs, provenance URL shape/date ordering, reserved fixture data, and manifest metadata. It does not fetch sources, verify remote hashes or rights, establish freshness, prove claims, or guarantee the absence of secrets. Review those separately, including unintended fact changes against prior revisions.

A focused partial PR may merge with `Refs #n` once its own deliverable, evidence, checks, reviews, and repository protections are satisfied. The entire issue need not be complete to merge useful partial research. Keep unmet acceptance criteria and pending handoffs visible. A documented concern that invalidates the submitted slice must be resolved before that slice merges.

Use `Closes #n` only when the PR's merge will satisfy all issue acceptance criteria and required handoffs. After merge, verify the default-branch commit and artifacts, then reconcile closure and Project `Done`. A merged partial PR alone does not make an issue Done; reflect remaining active work or review. A parent closes only after its children, merged summary, material handoffs, and own acceptance criteria are satisfied. Nonblocking open questions may remain only when recorded with owners and consistent with acceptance.

Do not bypass checks, branch protections, independent reviews, or owner holds. Do not fabricate approval or repeat requests indefinitely when an external decision is pending. Complete all independent authorized work, preserve the existing run and review state, and report exact blockers and remaining actions. Final reports distinguish proposed, submitted, merged, accepted, and verified GitHub state. Research completion never means production implementation or deployment is complete.

## Public organization handoff

When accepted findings make repository descriptions, topics, links, or public profile claims outdated, link the evidence and affected surface in the existing organization-maintenance issue. The separately invoked [organization maintenance prompt](ORGANIZATION.md) owns that task. This is an informational handoff, not an additional research deliverable, native blocker, or permission to launch another campaign. Preserve the research issue's scope, owner, and completion criteria.
