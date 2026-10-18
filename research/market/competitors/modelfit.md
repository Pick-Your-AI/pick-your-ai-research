# ModelFit — competitor profile

Status: draft for owner review ([#50](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/50)). Entity ID: `modelfit`. Classification: Direct competitor, Data source, Open-source integration candidate (analyst judgement). Evidence classes are defined in the [index](README.md#evidence-classes).

| Field | Value |
| --- | --- |
| Product | ModelFit device-first local-model recommender (site, `@wecko-ai/modelfit` CLI, JSON dataset, MCP endpoint) |
| Operator | ModelFit (terms); copyright "Wecko / ModelFit"; about page names an independent developer as maintainer |
| URLs | [site](https://modelfit.io/), [dataset](https://modelfit.io/data/), [about](https://modelfit.io/about/), [terms](https://modelfit.io/terms/), [CLI repo](https://github.com/Wecko-ai/modelfit), [dataset repo](https://github.com/Wecko-ai/modelfit-hardware-dataset) |
| Access date | 2026-10-16 |
| Version / revision | Dataset "Updated 2026-10-13"; CLI repo head `8c1df5f` (2026-10-16); dataset repo head `6fa130d` (2026-10-15); terms "Last updated: October 1, 2026" |
| Access tier observed | Public pages and repository metadata; CLI not run, MCP and `/api/dataset/` not called |
| robots.txt | Allows all (including ClaudeBot); `Content-Signal: search=yes, ai-input=yes, ai-train=no` |

## Workflow

| Stage | Finding | Class | Source |
| --- | --- | --- | --- |
| Inputs | Three-step flow: 01 Device (MacBook Air/Pro, Mac Mini/Studio, iPhone, NVIDIA GPU, AMD Strix Halo), 02 Setup, 03 Results; search by model or hardware; CLI auto-detects hardware | Observed (page structure) / Documented (CLI) | [site](https://modelfit.io/) |
| Constraints | Exact memory and architecture; picks sized to about 70% of unified memory (about 85% at 128 GB+) | Documented | [site](https://modelfit.io/) |
| Selection logic | "The single best local LLM it can actually run": one pick per device; quality from third-party scores "raw-confirmed against the model's primary source" | Documented / Vendor claim ("verified pick", "honest" estimates) | [site](https://modelfit.io/) |
| Explanation | Speed and quality estimates; terms state recommendations and speed figures are estimates | Documented | [site](https://modelfit.io/), [terms](https://modelfit.io/terms/) |
| Save/share/export | One-line Ollama install command; JSON/CSV dataset; MCP endpoint; saved/share Unknown | Documented | [site](https://modelfit.io/), [dataset](https://modelfit.io/data/) |

## Architecture and data

- Dataset: 156 models (116 local), 189 devices/GPUs; parameter size, quantization, minimum RAM, estimated memory load at Q4_K_M ("estimates, not measured"); all local entries are GGUF builds via Ollama. Observed (page counts) / Documented.
- Mirrored on GitHub and Hugging Face; machine endpoint `/api/dataset/`. Documented.
- Freshness: dataset updated 2026-10-13; "refreshed as new open-weight releases ship". Observed / Vendor claim.
- MoE handling and bandwidth-derived speed (prior profile) remain unreviewed against residency/offloading behaviour.

## Commercial access, code licence and data rights

| Layer | Finding | Class | Source |
| --- | --- | --- | --- |
| (a) Commercial access | Free; site sells sponsor slots ("Your product here ... 30 days"); affiliate revenue from the prior profile was not re-confirmed today | Observed / Unknown | [site](https://modelfit.io/) |
| (b) Code licence | CLI repo LICENSE is MIT text; GitHub API reports `NOASSERTION` (licence not auto-detected), so SPDX is MIT by file reading, not API detection | Observed | [CLI repo](https://github.com/Wecko-ai/modelfit) |
| (c) Data reuse | Dataset repo LICENSE: CC BY 4.0, "even commercially, provided you give appropriate credit"; terms §7: credit "ModelFit (modelfit.io)"; cited third-party benchmark figures keep their own terms | Observed (LICENSE) / Documented (terms) | [dataset repo](https://github.com/Wecko-ai/modelfit-hardware-dataset), [terms](https://modelfit.io/terms/) |

Historical comparison with merged [PR #82](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/82): all four uses Yes with attribution and change notice; figures are ModelFit estimates. This profile agrees and adds the NOASSERTION detail.

## Counterexample

- **Suffices (hypothesis, documented basis):** a Mac, iPhone or single-GPU owner asking "what is the best model I can run locally right now?" gets one pick plus an install command. For that segment Pick Your AI is redundant and should consider reusing the CC BY dataset.
- **Falls short (hypothesis):** one model per device, GGUF/Ollama only, estimates not measurements, no hosted alternatives, retrieval, agent or cost composition, and no versioned record of a recommendation.

## Matrix consistency

Historical comparison with merged [PR #87](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/87): `hardware_fit`, `model_versions`, `quantization`, `mcp`, `export`, `api_access` Documented; `saved`, `share` Unknown. Agrees.

## Open questions and routing

- #10/#11: compare ModelFit's 70% memory budget with MR-09 measurements at long context.
- #41: dataset version pinning (repo commit) before any ingestion.
- #66: preserve the bounded device-flow observation below; runtime accuracy and other scenarios remain separate.

## Reviewed scenario supplement — 2026-10-17

[#125](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/125), merged as
`6b14b7f50dbf5ceecbc43ca77c3a62ee9b2242d0`, records the anonymous device-flow
session and its [independent review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/125#pullrequestreview-5558972678).
The common local-PDF Q&A scenario on a 16 GB Windows laptop without a discrete
GPU was not expressible in that session's device choices. That is a bounded
workflow observation, not evidence of universal CPU incompatibility or measured
model accuracy. Export/API/CLI claims concern model/device data, not an observed
saved full-stack configuration.

The independent reviewer also saw Radeon choices, so the author's precise
device inventory is session-specific rather than a stable complete list. No
new session occurred during the 2026-10-18 profile reconciliation. The original
desk findings retain their original dates; #66 and #50 acceptance remain open.
