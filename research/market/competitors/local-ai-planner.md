# Local AI VRAM Calculator / GPU Planner — desk-research profile

Status: draft for owner review. Operator: Logarithmic Spirals. Classification: Partial competitor (analyst judgement).

## Workflow and competitive overlap
The planner already connects a user goal to local hardware and model suggestions, challenging simple hardware-first differentiation.

## Technical evidence and limitations
It documents weight memory plus KV cache and overhead, Hugging Face architecture inputs, runtime/quantization controls, and identical-GPU scaling. Its own page says context metadata is unavailable for the current model set.

## Economics, access and rights
The tool is free without signup. Public API, source-code license and dataset redistribution rights remain unknown. GPU specifications are described as a curated TechPowerUp snapshot.

## Strategic implication and next test
Check the consequence of multiplying bandwidth and VRAM by GPU count: topology, sharding and runtime constraints need empirical validation. Its quality fallback by parameter size is not measured task quality.

## Evidence
- [https://logarithmicspirals.com/tools/local-ai-vram-calculator-gpu-planner/](https://logarithmicspirals.com/tools/local-ai-vram-calculator-gpu-planner/) — accessed 2026-10-16.

Scope: public documentation and limited browser observation. No performance benchmark, paid trial, market-share measurement or commercial-rights approval was conducted. Confidence: Medium for the documented surface; Low for demand and comparative advantage. Related work: MR-03, MR-08, MR-09; exact technical consumers are in the handoff register.
