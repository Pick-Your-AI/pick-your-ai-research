# Vision

**AI Builder is in the research and planning stage. Nothing described here is implemented yet.**

AI Builder aims to be a PCPartPicker-style planner for AI: a web-based tool for assembling, checking, comparing and costing complete AI stacks. Where a PC builder picks CPUs, motherboards and GPUs, AI Builder users pick workloads, deployment modes, models, infrastructure, retrieval, agents, training and operations components. PCPartPicker is a functional reference only; AI Builder will use its own brand, interface and code.

## Intended capabilities

1. Search, browse, filter, compare and select AI components.
2. Determine compatibility between selected components.
3. Identify dependencies, conflicts, constraints and missing requirements.
4. Update available options dynamically when upstream selections change.
5. Support circular and cross-tier compatibility relationships.
6. Estimate deployment, inference, storage, training and recurring costs.
7. Support API, managed, hybrid and self-hosted architectures.
8. Generate shareable, reproducible stack configurations.
9. Compare multiple configurations.
10. Surface evidence, benchmarks, tradeoffs and alternatives.
11. Support optional components without imposing unnecessary dependencies.
12. Eventually produce deployment plans and configuration exports.

## This repository's role

This is the canonical research and requirements repository: component catalogs, compatibility rules, the shared contract, benchmarks and cost intelligence that the future application will consume. It does not contain the production web application.

## Principles

- Evidence first: facts, estimates, assumptions and unverified claims are kept distinct.
- Unknown is not compatible.
- No provider, model or platform is endorsed by default.
- Optional tiers (T3 to T5) stay optional.
