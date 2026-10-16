# Project 2 — issue-by-issue orchestration prompts

Twenty prompts for the twenty retrieved market-research issues in [Pick Your AI Project #2](https://github.com/orgs/Pick-Your-AI/projects/2), prepared 2026-10-16. Each issue has exactly one prompt and retains its original deliverable, acceptance and ownership boundaries. Read [SHARED.md](SHARED.md) with the selected prompt.

This extends the approach of the [technical maintainer prompt set](https://github.com/Pick-Your-AI/pick-your-ai-research/tree/docs/maintainer-research-prompts/prompts) without modifying it. These files belong under `prompts/market/`. They do not start research, close issues, approve evidence, change Project metadata or authorize implementation merely by being published.

## Run one issue

Give an authorized agent the repository and this instruction, replacing both occurrences of 66 with the selected issue number:

```text
Read AGENTS.md and the current contributor, governance and research workflow instructions.
Read prompts/market/SHARED.md and prompts/market/issue-066.md.
Execute only issue #66 and its authorized coordination/handoffs. Refresh the live
issue, comments, active PRs, actual assignees, Project #2 fields and permissions first.
Complete authorized research, validation, commit, push, branch synchronization,
required review and qualifying merge. Preserve existing work and unresolved criteria.
Do not mark Done until accepted evidence reaches the canonical default branch.
If an external gate blocks delivery, finish independent work and return the exact
blocker, reviewable ZIP/diff and replay steps. Do not claim an unperformed action.
```

A parent orchestrator may coordinate native children within a confirmed program mandate; each child still uses its own prompt, owner and acceptance boundary. Do not launch all twenty prompts against one shared checkout or start a second controller for an already active issue.

## One prompt per issue

| Issue | Scope | Prompt |
| --- | --- | --- |
| [#47](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/47) | Market Research Program — Pick Your AI | [issue-047.md](issue-047.md) |
| [#48](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/48) | MR-01 — Competitive Landscape Discovery | [issue-048.md](issue-048.md) |
| [#49](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/49) | MR-02 — Competitive Feature Matrix | [issue-049.md](issue-049.md) |
| [#50](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/50) | MR-03 — Competitor Deep Dives | [issue-050.md](issue-050.md) |
| [#51](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/51) | MR-04 — PCPartPicker Product Experience | [issue-051.md](issue-051.md) |
| [#52](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/52) | MR-05 — Customer Research & Personas | [issue-052.md](issue-052.md) |
| [#53](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/53) | MR-06 — Market Size, Demand & Trends | [issue-053.md](issue-053.md) |
| [#54](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/54) | MR-07 — Pricing & Monetization | [issue-054.md](issue-054.md) |
| [#55](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/55) | MR-08 — Data Sources & Integration Opportunities | [issue-055.md](issue-055.md) |
| [#56](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/56) | MR-09 — Technical Feasibility | [issue-056.md](issue-056.md) |
| [#57](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/57) | MR-10 — Competitive Differentiation | [issue-057.md](issue-057.md) |
| [#58](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/58) | MR-11 — MVP Definition & Prioritization | [issue-058.md](issue-058.md) |
| [#59](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/59) | MR-12 — Research Quality, Synthesis & Handoffs | [issue-059.md](issue-059.md) |
| [#60](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/60) | MR-08: Validate commercial display and redistribution rights | [issue-060.md](issue-060.md) |
| [#61](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/61) | MR-09: Validate GPU sizing against pinned runtime measurements | [issue-061.md](issue-061.md) |
| [#62](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/62) | MR-09: Validate benchmark comparability and harness effects | [issue-062.md](issue-062.md) |
| [#63](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/63) | MR-05: Validate customer demand and willingness to pay | [issue-063.md](issue-063.md) |
| [#64](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/64) | MR-07: Validate price freshness and total-cost scenarios | [issue-064.md](issue-064.md) |
| [#65](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/65) | MR-09: Review RAG interoperability market claims | [issue-065.md](issue-065.md) |
| [#66](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/66) | MR-03: Test direct stack-builder substitutes | [issue-066.md](issue-066.md) |

## Recommended coordination order

This is a launch/acceptance guide, not new Project priorities or a new native dependency graph.

1. **Coordinate from the start:** #47 owns program decisions and #59 owns audit/handoffs. Start their coordination early; their final acceptance comes after the required evidence. Inspect PR #67’s proposal branch and existing active work before launching contributors.
2. **Prioritize premise and data risk while research proceeds in parallel:** #48 feeds #49/#50; #55 feeds #60; #66 tests direct substitution. #52 prepares customer hypotheses and the #63 approval package. #56 coordinates the existing #61/#62/#65 technical validation work; do not restart PR #79’s dense runs. #54 and #64 coordinate monetization/cost work. #51, #53 and the remaining independent desk research can proceed within their access limits.
3. **Respect acceptance gates:** #63 cannot contact participants without its explicit approval. #51 and #61 preserve account/resource permissions. #57 and #58 can draft and review, but neither can be accepted before #66. #60/#61/#63/#64 inform #58 without becoming extra native blockers.
4. **Complete children and reconcile acceptance:** parents #50/#52/#54/#55/#56 cannot close before their respective children and own criteria. #59 records actual receiving-owner decisions; #47 finalizes its synthesis and closes only when the program’s children and its own acceptance are satisfied.

## Coverage and starting-state limits

The coverage snapshot is the twenty GitHub issue search results, followed by all twenty individual issue reads. It does not claim inspection of draft, archived or PR cards. Project custom-field IDs/options were not directly inspected; agents must discover them live before writes. Do not infer current assignees from narrative owner sections.

PR #79 was verified merged into `research/market-intelligence`, not `main`. The market proposal PR #67 and technical prompt PR #74 were still open when inspected. Refresh those states before execution. PR #80 is a linked follow-up that this package instructs agents to inspect; no unverified content from it is treated as accepted evidence.

## Validate this prompt package

From the repository root:

```bash
python prompts/market/validate_prompts.py
```

This checks the twenty-file coverage, captured criteria, declared relationships, local prompt links and required execution sections. It does not query GitHub, evaluate research evidence or replace the repository’s research tests and required human review. See [manifest.json](manifest.json) for the dated issue mapping and source references.

## Publication provenance

The original authoring session prepared the ZIP on 2026-10-16 but could not publish it because its GitHub integration rejected branch creation with `403: Resource not accessible by integration`. That failure describes the original session, not subsequent repository publication.

This repository revision imports the supplied twenty prompts and supporting files. Publication-time checks confirmed that Project #2 contains issues #47–#66 and that all twenty titles, captured acceptance criteria and deliverable paths match the live issue bodies. The original dated starting-state notes remain historical; refresh them before executing a prompt. Git history and the associated publication PR record the actual commit, review and merge state. Publishing these files does not execute or accept the research.
