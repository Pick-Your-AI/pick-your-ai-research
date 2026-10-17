# Pick Your AI research

[Research Project](https://github.com/orgs/Pick-Your-AI/projects/1) · [Issues](https://github.com/Pick-Your-AI/pick-your-ai-research/issues) · [Organization](https://github.com/Pick-Your-AI)

Research workspace for an AI system builder inspired by [PCPartPicker](https://pcpartpicker.com/). The intended product lets a user choose compatible AI components, understand tradeoffs and estimated costs, save and share a configuration, and inspect evidence behind each recommendation.

This repository gathers evidence and decisions before implementation. It does not endorse a provider, model, or hosting platform by default.

## Scope

The builder starts with workload and deployment mode (T0), then guides model selection (T1), infrastructure (T2), optional knowledge and retrieval (T3), optional agents and integrations (T4), optional training (T5), and deployment and operations (T6). A choice may constrain earlier choices; the builder must recompute compatibility as selections change.

T3, T4, and T5 are optional capabilities: a build may omit them entirely.

- [Contributing and triage conventions](CONTRIBUTING.md) cover issue structure, labels, Project fields, priority and readiness criteria, and dependency semantics.
- [Research submission workflow](docs/RESEARCH_WORKFLOW.md) explains notes, structured proposals, external evidence, and validation.
- [Contract coverage](docs/CONTRACT_MAPPING.md) maps all 29 canonical kinds to existing issues; [contract adoption](contracts/v1/ADOPTION.md) explains the preserved v1 package.
- The [research method](docs/RESEARCH_METHOD.md) defines evidence rules and the decision-record template.
- The [dependency map](docs/DEPENDENCIES.md) links every component issue to its inputs, compatibility relationships, and ownership boundaries.

GitHub Issues hold the research tasks: T0–T6 are parent issues and each component is a native sub-issue. The [Project](https://github.com/orgs/Pick-Your-AI/projects/1) is the cross-workstream board, with views by workstream, priority, readiness, blockers, and missing metadata. Decision records go in `research/<workstream>/<component>.md` through pull requests.

| Workstream | Owner |
| --- | --- |
| [T0: Configuration](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/1) | @CompleteDotTech |
| [T1: Model Selection](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/4) | @zwright8 |
| [T2: Infrastructure](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/8) | @Mattycodes69 |
| [T3: Knowledge & Retrieval](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/12) (optional) | @zabyxc01 |
| [T4: Agents & Integrations](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/24) (optional) | @CompleteDotTech |
| [T5: Training & Fine-Tuning](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/29) (optional) | @appletechie |
| [T6: Deployment & Operations](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/34) | @PUSHINGSQUARES |

## Product research questions

- Which component categories and attributes are needed to make useful selections for API, managed, and self-hosted deployments? (component issues; schema in [#40](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40))
- How should compatibility, unknowns, warnings, and hard conflicts be represented and explained? ([#40](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40))
- How should users compare candidates using current, sourced prices and capability data without implying false precision? ([#39](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/39), [#41](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/41))
- What should a build summary, saved configuration, and shareable link contain, and what happens when data changes? ([#42](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/42))
- Which data sources permit automated updates, and how will stale or conflicting facts be handled? ([#41](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/41))

## Maintainers

- [@Alexi5000](https://github.com/Alexi5000)

## Early contributors

- [@bradAGI](https://github.com/bradAGI)
- [@DevvGwardo](https://github.com/DevvGwardo)
- [@Dropgunner](https://github.com/Dropgunner)
- [@KingdomMinded7x70](https://github.com/KingdomMinded7x70)

## Inspiration and boundaries

PCPartPicker is a reference for the selection flow, compatibility feedback, and price comparison. This project should develop its own design, wording, data model, and implementation. Research should cite primary sources for AI product facts, prices, licenses, benchmarks, and operational claims.
