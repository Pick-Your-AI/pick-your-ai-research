# Local AI VRAM Calculator / GPU Planner — competitor profile

Status: draft for owner review ([#50](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/50)). Entity ID: `local-ai-planner`. Classification: Partial competitor (analyst judgement). Evidence classes are defined in the [index](README.md#evidence-classes).

| Field | Value |
| --- | --- |
| Product | LLM VRAM Calculator & Local AI GPU Planner |
| Operator | Logarithmic Spirals, a personal site of an individual software engineer (name not stated on the about page) |
| URLs | [planner](https://logarithmicspirals.com/tools/local-ai-vram-calculator-gpu-planner/), [about](https://logarithmicspirals.com/about/) |
| Access date | 2026-10-16 |
| Version / revision | Unknown; no version or update date on the page |
| Access tier observed | Public page, static HTML; no signup offered or needed |
| robots.txt | Allows the planner (only `/social` disallowed) |

## Workflow

| Stage | Finding | Class | Source |
| --- | --- | --- | --- |
| Inputs | Hardware type (discrete GPU, Apple Silicon, no GPU), GPU model or custom VRAM, GPU count, RAM sticks; primary goal (coding agent, tools/agents, chat, writing, RAG, image generation); optional public Hugging Face model URL | Observed (form fields in page) | [planner](https://logarithmicspirals.com/tools/local-ai-vram-calculator-gpu-planner/) |
| Constraints | Min/target input and output TPS, input:output ratio, performance margin, desktop VRAM reserve, K/V cache precision, runtime (GGUF/llama.cpp or MLX), quantization, context | Observed (form fields) | [planner](https://logarithmicspirals.com/tools/local-ai-vram-calculator-gpu-planner/) |
| Selection logic | Heuristic rating combining fit, estimated speed against TPS targets, context support, quantization penalty and quality; quality from LiveBench/UGI CSVs, else a log-parameter-count fallback | Documented | [planner](https://logarithmicspirals.com/tools/local-ai-vram-calculator-gpu-planner/) |
| Explanation | "Why these models?" names goal, runtime, quantization and context used, with the heuristic limits | Observed (default-state text) | [planner](https://logarithmicspirals.com/tools/local-ai-vram-calculator-gpu-planner/) |
| Save/share/export | None found in the static page | Unknown (not proof of absence) | [planner](https://logarithmicspirals.com/tools/local-ai-vram-calculator-gpu-planner/) |

## Architecture and data

- Memory model: weights + K/V cache + runtime overhead, following a cited ApX Machine Learning guide; K/V uses Hugging Face architecture metadata when available. Documented.
- Data: "curated TechPowerUp GPU Database snapshot"; Apple-published bandwidth; curated model snapshot; LiveBench and UGI leaderboard CSVs. Origin third-party; snapshot dates Unknown.
- GPU count "multiplies VRAM and bandwidth" for identical GPUs. Observed. Topology, sharding and runtime constraints are not modelled in the documented method (hypothesis to test with #10).
- The prior profile noted the page reporting missing context metadata for its model set; today's static fetch did not show that text (it may render client-side). Status: unreconciled.

## Commercial access, code licence and data rights

| Layer | Finding | Class | Source |
| --- | --- | --- | --- |
| (a) Commercial access | Free, "no signup"; no paid tier, ads or API found | Observed | [planner](https://logarithmicspirals.com/tools/local-ai-vram-calculator-gpu-planner/) |
| (b) Code licence | No public repository identified | Unknown | — |
| (c) Data reuse | No terms page found (only a privacy policy link). No grant, so display and redistribution default to no under the [#82 decision rule](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/82). TechPowerUp, LiveBench and UGI data keep their own terms | Observed (no terms link) | [planner](https://logarithmicspirals.com/tools/local-ai-vram-calculator-gpu-planner/) |

Not in the PR #82 shortlist; route to #55/#60 if any reuse is proposed.

## Counterexample

- **Suffices (hypothesis, observed inputs):** a hobbyist with one consumer GPU or a Mac choosing a local model for coding agents, chat or local-document RAG with a speed target. The form covers goal, hardware, runtime, quantization, context and throughput, and explains the ranking. Pick Your AI is redundant for that single-tier choice.
- **Falls short (hypothesis):** no saved or shareable result found; no hosted/API alternative; RAG is a goal label, not retrieval component selection; multi-GPU is linear scaling.

## Matrix consistency

Pending [PR #87](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/87): `constraints`, `explanation`, `multi_gpu` and related cells Documented; `saved`, `share`, `export`, `model_versions` Unknown. Agrees.

## Open questions and routing

- #10: test linear GPU-count scaling against measured multi-GPU behaviour.
- #48: snapshot dates for the GPU and model data.
