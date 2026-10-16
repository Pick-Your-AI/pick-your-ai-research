# Contributing and triage conventions

This repository holds **research**, not implementation. Every issue tracks evidence and decisions that will shape the Pick Your AI builder. Closing an issue means the research deliverable is complete and reviewed. It does not mean the builder implements it.

- [Research Project](https://github.com/orgs/Pick-Your-AI/projects/1) is the cross-workstream board.
- [Research method](docs/RESEARCH_METHOD.md) defines the decision-record template and evidence rules.
- [Dependency map](docs/DEPENDENCIES.md) defines relationships, handoffs, and component boundaries.

## Issue hierarchy

| Level | What it is | Label |
| --- | --- | --- |
| Workstream (T0–T6) | Parent issue that groups research for one area and records cross-workstream handoffs | `type: workstream` |
| Component research | Native sub-issue with one independently reviewable deliverable | `type: research` |
| Step | A small task inside a research issue, kept as a checklist item | none |

- Use GitHub's native sub-issues for parent/child links. Do not track the same child in a body checklist as well.
- Open a new sub-issue only when the work needs its own owner, review, or tracking. Otherwise add a checklist item to the existing issue.
- Title format: `T<n>: <Component>`. Keep titles short and use the component names from the dependency map.
- Every research issue body has the same sections: user decision, scope (in / out), research questions, deliverable, comparison fields and evidence, dependencies and relationships, acceptance criteria, open questions.
- Use the **Research finding** issue template to record evidence that does not need a new component issue.

## Ownership

GitHub **Assignees** are the source of truth for ownership. Do not duplicate owners in Project fields or labels. Component issues are assigned to their workstream owner unless the owner delegates.

| Workstream | Owner |
| --- | --- |
| T0 Configuration | @tynamite |
| T1 Model Selection | @zwright8 |
| T2 Infrastructure | @Mattycodes69 |
| T3 Knowledge & Retrieval (optional) | @zabyxc01 |
| T4 Agents & Integrations (optional) | @CompleteDotTech |
| T5 Training & Fine-Tuning (optional) | @appletechie |
| T6 Deployment & Operations | @PUSHINGSQUARES |

## Deliverables

- Put decision records at `research/<workstream-slug>/<component-slug>.md`. The exact path is in each issue's Deliverable section, e.g. `research/T2-infrastructure/gpu-compute.md`.
- Put workstream summaries at `research/<workstream-slug>/README.md`.
- Follow [the submission workflow](docs/RESEARCH_WORKFLOW.md) and [canonical-kind mapping](docs/CONTRACT_MAPPING.md). Put complete catalog JSON proposals in `catalog/proposals/`, dated pricebooks in `pricing/proposals/`, and metadata for external artifacts in `evidence/`. Incomplete findings remain research notes.
- Run the workflow's validation commands. Schema validity does not certify source accuracy or complete the issue's review requirements.
- Deliver research by pull request that references the issue (`Closes #n` once acceptance criteria are met). Ask the owners of affected handoff issues to review.
- Never commit fabricated findings, prices, or citations. Every factual or numeric claim needs a primary source with an access date (see the research method).

## Labels

Labels describe *what kind of issue* it is and *which cross-cutting topic* it serves. Status, priority, workstream, and readiness live in Project fields, not labels.

| Label | Meaning | Apply when |
| --- | --- | --- |
| `type: workstream` | Parent workstream issue | T0–T6 parents only |
| `type: research` | Research deliverable | Every component research issue |
| `optional capability` | Optional builder capability (T3–T5). Scope marker, **not** a priority | All T3, T4, T5 issues |
| `topic: compatibility` | Defines or supplies compatibility rules between components | The issue's primary output includes hard rules in the shared format (#40) |
| `topic: pricing` | Defines pricing units, sources, or cost assumptions | The issue's primary output includes priced data or the cost model |
| `topic: data-governance` | Data rights, licensing, privacy, retention, deletion | The issue must resolve rights or retention questions |
| `documentation` | Changes to repository guidance | Docs-only work |
| `question` | Needs clarification or a decision | Pair with Readiness = *Awaiting decision* |
| `duplicate` | Closed in favour of a canonical issue | Only when closing; link the canonical issue first |

Add a topic label only when it is a primary concern of the issue, not because the topic is mentioned. Do not create workstream, priority, or status labels.

## Project fields

| Field | Values | Rule |
| --- | --- | --- |
| Status | Backlog · Ready · In Progress · In Review · Blocked · Done | Set from evidence. *Backlog* when not yet prepared or started; *Ready* when qualified and actionable but not started; *In Progress* when research is actively under way (including a draft PR); *In Review* when a decision record PR is open for owner / handoff review; *Blocked* when a real constraint prevents execution; *Done* only when the PR is merged and acceptance criteria are met. A merged partial contribution does not make an issue Done. |
| Priority | Critical · High · Medium · Low | Sequencing, see below |
| Tier | T0 Configuration … T6 Deployment & Operations | Matches the parent issue; T3–T5 option names include "(optional)" |
| Readiness | Ready · Needs input · Blocked · Awaiting decision | See below; independent of Status |
| Work Type | Epic · Research · Specification · Dataset · Validation | Epic for T0–T6 parents |
| Research Confidence | Unverified · Low · Medium · High | Unverified until evidence has been reviewed |
| Dependency Status | Unblocked · Waiting · Blocked | Mirrors native "blocked by" relationships |

Built-in fields (Assignees, Labels, Parent issue, Sub-issues progress) are used as-is. Assignees are the source of truth for ownership. No dates, estimates, or iterations are tracked; do not invent them. Use the live field and option IDs from the Project, not names from older documents.

### Priority criteria

Priority expresses **research sequencing**, not product importance.

- **Critical, foundation:** core build path (T0–T2) whose outputs most other issues consume: workload, deployment mode, component schema and rules, model and provider catalogs, GPU sizing, inference engines.
- **High, core:** needed for a complete core build summary and consumes Critical outputs: context window, hosting, catalog data sources, saved builds, guardrails, evaluation, deployment, cost estimate.
- **Medium, later:** optional capabilities (T3–T5) and operational depth (monitoring), sequenced after the core path.
- **Low:** lower-impact or nice-to-have research.

Optional capabilities are Medium because they depend on core outputs, not because they matter less. If the product direction makes an optional capability part of the first release, raise its priority and record why in the issue.

### Readiness criteria

- **Ready:** work can start now. Inputs exist or are only informational.
- **Needs input:** meaningful progress needs a specific output from another issue first (name it in the issue).
- **Blocked:** cannot proceed because of a native blocker, missing owner access, or missing permission.
- **Awaiting decision:** a named owner must make a decision before research continues. Add the `question` label and state the decision in the issue.

## Dependency semantics

| Relationship | How to record it | Example |
| --- | --- | --- |
| Parent / child | Native sub-issue | #10 under #8 |
| Delivery blocker | Native **blocked by** relationship, only for genuine prerequisites | #42 saved builds is blocked by #40 schema |
| Information dependency | "Information inputs" row in the issue body | #10 uses facts from #6 |
| Compatibility relationship | "Compatibility relationships" row; bidirectional, may be cyclic | model ↔ GPU ↔ inference engine (#6, #10, #11) |
| Optional integration | Body link plus `optional capability` label on the optional side | RAG (#16) feeding agents (#25) |

Never model a compatibility cycle as blocking. Research both sides in parallel, record assumptions, and reconcile rules in the shared format from #40.

## Duplicates and closure

Do not delete issues. Before closing a duplicate, link the canonical issue, copy any unique information into it, then close with the `duplicate` label.

## Committing documentation

Change documentation through a branch and pull request against `main`. Keep README, this guide, and `docs/` consistent with the live labels and Project fields.
