# Maintainer research prompts

Each prompt coordinates one existing technical research workstream. Read [the shared execution rules](SHARED.md) with the selected prompt. Keep the issue's existing deliverable, acceptance criteria, assignees, and Project metadata authoritative.

| Workstream | Parent issue | Prompt |
| --- | --- | --- |
| T0 Configuration | [#1](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/1) | [T0.md](T0.md) |
| T1 Model Selection | [#4](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/4) | [T1.md](T1.md) |
| T2 Infrastructure | [#8](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/8) | [T2.md](T2.md) |
| T3 Knowledge & Retrieval | [#12](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/12) | [T3.md](T3.md) |
| T4 Agents & Integrations | [#24](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/24) | [T4.md](T4.md) |
| T5 Training & Fine-Tuning | [#29](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/29) | [T5.md](T5.md) |
| T6 Deployment & Operations | [#34](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/34) | [T6.md](T6.md) |

## Run a workstream

Use a checkout containing these files and an agent with the appropriate repository/GitHub access. Give it this instruction, replacing T0 with the intended workstream:

```text
Read AGENTS.md and the current contributor/research workflow instructions.
Then read prompts/SHARED.md and prompts/T0.md, and execute the T0 research
workstream within my existing authority. Refresh live issues, Project fields,
assignees, and active work first. Coordinate with any existing run instead of
starting a duplicate. Preserve the frozen v1 contract and require the specified
reviews. Complete independent work and report exact remaining blockers.
```

For delegated component work, explicitly limit execution to the assigned issue:

```text
Read AGENTS.md, the current contributor/research workflow instructions,
prompts/SHARED.md, and the applicable workstream prompt. Execute only issue
#NUMBER and its agreed handoffs within my existing authority. Preserve its
live assignees and acceptance criteria. Coordinate with the workstream owner;
do not start the entire workstream or another contributor's active task.
```

The prompts do not grant new account permissions, waive reviews, or authorize production deployment. Publishing a prompt does not start research or establish issue completion. The issue and Project handoffs link a pinned publication revision so maintainers can identify exactly which version they are running. While its PR is open, that revision is proposed guidance awaiting review.

## Keep the set aligned

Change common rules in `SHARED.md`, and update affected workstream text in the same PR. Recheck live Project fields and the existing issue paths before publishing a new handoff revision. Validate with `docs/RESEARCH_WORKFLOW.md`; separately review instructions, links, and evidence because schema tests cannot establish prompt correctness or research acceptance.
