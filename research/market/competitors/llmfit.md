# llmfit — competitor profile

Status: draft for owner review ([#50](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/50)). Entity ID: `llmfit`. Classification: Partial competitor, Open-source integration candidate (analyst judgement). Evidence classes are defined in the [index](README.md#evidence-classes).

| Field | Value |
| --- | --- |
| Product | llmfit terminal tool (TUI, CLI, local REST server, web dashboard) |
| Operator | Upstream repository: AlexsJones on GitHub. Seed site llmfit.org: operator unconfirmed ("© 2026 llmfit"; links to the repository, but the repository's homepage field is empty, so no reciprocal link) |
| URLs | [seed site](https://www.llmfit.org/), [repository](https://github.com/AlexsJones/llmfit), [licence](https://github.com/AlexsJones/llmfit/blob/main/LICENSE) |
| Access date | 2026-10-16 |
| Version / revision | Latest release v1.1.17 (2026-10-08); `main` head `eb8db38` (2026-10-15) |
| Access tier observed | Public site and repository metadata; not installed or run |
| robots.txt | llmfit.org allows all |

## Workflow

| Stage | Finding | Class | Source |
| --- | --- | --- | --- |
| Inputs | Detected RAM, CPU cores, GPU VRAM and installed runtimes; overrides `--memory`, `--max-context`, `--use-case`; search by model name | Documented | [seed site](https://www.llmfit.org/) |
| Constraints | Memory and context caps; fit tier filter (`--perfect`, `min_fit`) | Documented | [seed site](https://www.llmfit.org/) |
| Selection logic | Composite score across quality, speed, fit and context; picks quantization and run mode (GPU, CPU+GPU, CPU, MoE offload); Plan mode estimates hardware for a chosen model | Documented | [seed site](https://www.llmfit.org/) |
| Explanation | Fit/speed/quality columns and compare views; assumption detail via `info` output (per #87) | Documented | [seed site](https://www.llmfit.org/), [repository](https://github.com/AlexsJones/llmfit) |
| Save/share/export | `recommend --json`, `fit --json`, REST `/api/v1/models/top`; benchmark runs saved locally; contribution workflow for benchmark configs | Documented | [seed site](https://www.llmfit.org/), [repository](https://github.com/AlexsJones/llmfit) |

## Architecture and data

- Rust binary; model catalogue `data/hf_models.json` shipped with the binary, described as "a curated Hugging Face model database"; scores computed at runtime for the detected hardware. Documented, [seed site](https://www.llmfit.org/).
- Freshness: catalogue updates ship with releases; repository pushed 2026-10-15. Observed (metadata).
- Runtime providers: Ollama, llama.cpp, MLX, Docker Model Runner, LM Studio. Documented.

## Commercial access, code licence and data rights

| Layer | Finding | Class | Source |
| --- | --- | --- | --- |
| (a) Commercial access | Free open-source tool; no hosted or paid tier found | Observed (absence of a pricing page is not proof) | [seed site](https://www.llmfit.org/) |
| (b) Code licence | SPDX `MIT` (`gh api repos/AlexsJones/llmfit/license`) | Observed | [licence](https://github.com/AlexsJones/llmfit/blob/main/LICENSE) |
| (c) Data reuse | Repository data (including `data/hf_models.json`) under MIT; llmfit.org page content is "All rights reserved" and is not covered. Upstream Hugging Face model metadata keeps its own terms | Observed / Documented | [repository](https://github.com/AlexsJones/llmfit), [seed site](https://www.llmfit.org/) |

Historical comparison with merged [PR #82](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/82): all four uses Yes for repository data with the MIT notice; website content excluded. This profile agrees.

## Counterexample

- **Suffices (hypothesis, documented basis):** a developer asking "which open model and quantization run well on this machine for coding?" llmfit detects hardware, ranks fits, and emits JSON. For a single-machine local model choice Pick Your AI is redundant.
- **Falls short (hypothesis):** it covers the local model tier only. Hosted APIs, retrieval, agents, evaluation and multi-machine cost are outside the documented scope. Its memory and speed estimates are heuristics; accuracy at long context and batch sizes is untested here (#10/#11).

## Matrix consistency

Historical comparison with merged [PR #87](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/87): `saved`, `share`, `export` Documented; `model_versions` Unknown. Agrees.

## Open questions and routing

- #10/#11: compare pinned v1.1.17 memory predictions against MR-09 measurements at several contexts.
- #48: confirm llmfit.org operator before citing the site as upstream.
