# llmfit — desk-research profile

Status: draft for owner review. Operator: AlexsJones repository; seed-site operator unconfirmed. Classification: Partial competitor, Open-source integration candidate (analyst judgement).

## Workflow and competitive overlap
A hardware-first MVP competes with an existing recommendation engine and must improve a specific decision rather than repeat model fit.

## Technical evidence and limitations
The seed page documents Rust-based hardware detection, local metadata, quantization selection, fit scoring, CLI/TUI, JSON and local REST paths. Upstream additionally advertises a benchmark contribution workflow; these are documented, not run in this study.

## Economics, access and rights
Upstream code is MIT. The seed-site operator has not been established as the upstream maintainer. Software licensing does not automatically license model metadata or weight distribution.

## Strategic implication and next test
Evaluate its pinned algorithms with #10 and #11; compare memory predictions at multiple contexts and batch sizes. Reuse may be cheaper than reproducing the implementation, but integration is not approved.

## Evidence
- [https://www.llmfit.org/](https://www.llmfit.org/) — accessed 2026-10-16.
- [https://github.com/AlexsJones/llmfit](https://github.com/AlexsJones/llmfit) — accessed 2026-10-16.
- [https://raw.githubusercontent.com/AlexsJones/llmfit/main/LICENSE](https://raw.githubusercontent.com/AlexsJones/llmfit/main/LICENSE) — accessed 2026-10-16.

Scope: public documentation and limited browser observation. No performance benchmark, paid trial, market-share measurement or commercial-rights approval was conducted. Confidence: Medium for the documented surface; Low for demand and comparative advantage. Related work: MR-03, MR-08, MR-09; exact technical consumers are in the handoff register.
