# Vision

**The website has a synthetic-data preview. Research-backed production capabilities
and native applications remain subject to their delivery and evidence gates.**

AI Builder aims to be a PCPartPicker-style planner for AI across web and planned mobile
clients: a tool for assembling, checking, comparing and costing complete AI stacks.
Where a PC builder picks CPUs, motherboards and GPUs, AI Builder users pick workloads,
deployment modes, models, infrastructure, retrieval, agents, training and operations
components. PCPartPicker is a functional reference only; AI Builder uses its own brand,
interface and code. The [Apple/iOS delivery plan](APPLE_DELIVERY_PLAN.md) follows the
Android plan's 18-epic, 110-work-package structure and separates shared services from
platform-specific implementation. Its publication does not create a mobile application.

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

This is the canonical research and requirements repository: component catalogs,
compatibility rules, shared contracts, benchmarks and cost intelligence for application
consumers. It can hold delivery planning and research-to-implementation handoffs.
Production web/mobile runtime code and service operation belong in implementation
repositories. Merged proposals are not automatically published production data.

## Principles

- Evidence first: facts, estimates, assumptions and unverified claims are kept distinct.
- Unknown is not compatible.
- No provider, model or platform is endorsed by default.
- Optional tiers (T3 to T5) stay optional.
