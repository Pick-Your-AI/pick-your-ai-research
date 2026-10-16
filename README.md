# Pick Your AI research

[Research Project](https://github.com/orgs/Pick-Your-AI/projects/1) · [Issues](https://github.com/Pick-Your-AI/research/issues) · [Organization](https://github.com/Pick-Your-AI)

Research workspace for an AI system builder inspired by [PCPartPicker](https://pcpartpicker.com/). The intended product lets a user choose compatible AI components, understand tradeoffs and estimated costs, save and share a configuration, and inspect evidence behind each recommendation.

This repository gathers evidence and decisions before implementation. It does not endorse a provider, model, or hosting platform by default.

## Scope

The builder starts with workload and deployment mode (T0), then guides model selection (T1), infrastructure (T2), optional knowledge and retrieval (T3), optional agents and integrations (T4), optional training (T5), and deployment and operations (T6). A choice may constrain earlier choices; the builder must recompute compatibility as selections change.

The [research method](docs/RESEARCH_METHOD.md) defines evidence and decision records. The [dependency map](docs/DEPENDENCIES.md) preserves the supplied cross-workstream relationships. GitHub Issues hold the active research tasks, with T0–T6 as parent issues and each topic as a native sub-issue. The GitHub Project is the cross-workstream board.

| Workstream | Owner |
| --- | --- |
| [T0: Configuration](https://github.com/Pick-Your-AI/research/issues/1) | @CompleteDotTech |
| [T1: Model Selection](https://github.com/Pick-Your-AI/research/issues/4) | @zwright8 |
| [T2: Infrastructure](https://github.com/Pick-Your-AI/research/issues/8) | @Mattycodes69 |
| [T3: Knowledge & Retrieval](https://github.com/Pick-Your-AI/research/issues/12) | @zabyxc01 |
| [T4: Agents & Integrations](https://github.com/Pick-Your-AI/research/issues/24) | @CompleteDotTech |
| [T5: Training & Fine-Tuning](https://github.com/Pick-Your-AI/research/issues/29) | @appletechie |
| [T6: Deployment & Operations](https://github.com/Pick-Your-AI/research/issues/34) | @PUSHINGSQUARES |

## Product research questions

- Which component categories and attributes are needed to make useful selections for API, managed, and self-hosted deployments?
- How should compatibility, unknowns, warnings, and hard conflicts be represented and explained?
- How should users compare candidates using current, sourced prices and capability data without implying false precision?
- What should a build summary, saved configuration, and shareable link contain?
- Which data sources permit automated updates, and how will stale or conflicting facts be handled?

## Inspiration and boundaries

PCPartPicker is a reference for the selection flow, compatibility feedback, and price comparison. This project should develop its own design, wording, data model, and implementation. Research should cite primary sources for AI product facts, prices, licenses, benchmarks, and operational claims.
