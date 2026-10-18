# SkyPilot — competitor profile

Status: draft for owner review ([#50](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/50)). Entity ID: `skypilot`. Classification: Substitute workflow, Open-source integration candidate (analyst judgement). Evidence classes are defined in the [index](README.md#evidence-classes).

| Field | Value |
| --- | --- |
| Product | SkyPilot open-source AI compute orchestrator; commercial SkyPilot Platform |
| Operator | SkyPilot (skypilot-org on GitHub) |
| URLs | [site](https://skypilot.ai/) (skypilot.co redirects here), [docs](https://docs.skypilot.ai/en/latest/docs/index.html), [YAML spec](https://docs.skypilot.ai/en/latest/reference/yaml-spec.html), [repository](https://github.com/skypilot-org/skypilot) |
| Access date | 2026-10-16 |
| Version / revision | Latest release v0.14.0 (2026-10-05); docs `latest` |
| Access tier observed | Public site, docs and repository metadata; no cluster launched, no cloud credentials |
| robots.txt | skypilot.ai has none (404); docs.skypilot.ai allows `/en/latest/` and `/en/stable/`, disallows other paths. Only `/en/latest/` pages were fetched |

## Workflow

| Stage | Finding | Class | Source |
| --- | --- | --- | --- |
| Inputs | Task YAML: accelerators (e.g. `H100:8`), CPUs, memory, instance type, disk, network tier, ports, image | Documented | [YAML spec](https://docs.skypilot.ai/en/latest/reference/yaml-spec.html) |
| Constraints | `max_hourly_cost`, `use_spot`, `any_of` and `ordered` candidate lists across infra/regions; supported infra: Kubernetes, Slurm, existing machines, 20+ clouds (vendor count) | Documented / Vendor claim | [YAML spec](https://docs.skypilot.ai/en/latest/reference/yaml-spec.html), [site](https://skypilot.ai/) |
| Selection logic | Scheduler places work "on the most available infra" among allowed candidates; ordered accelerator fallbacks | Documented | [docs](https://docs.skypilot.ai/en/latest/docs/index.html) |
| Explanation | Not reviewed (launch-time output not exercised) | Unknown | — |
| Save/share/export | Task YAML is the portable, version-controllable configuration | Documented | [YAML spec](https://docs.skypilot.ai/en/latest/reference/yaml-spec.html) |

## Architecture and data

- Client/API server that provisions clusters, jobs and services (SkyServe) across providers; autostop and bin-packing. Documented, [docs](https://docs.skypilot.ai/en/latest/docs/index.html).
- Data: provider instance catalogs and prices used for placement; Kubernetes pricing configurable. Documented (catalog refresh cadence Unknown).
- It does not choose models or application components; the user brings the workload.

## Commercial access, code licence and data rights

| Layer | Finding | Class | Source |
| --- | --- | --- | --- |
| (a) Commercial access | Free open source; commercial "SkyPilot Platform" via "Book a demo". Compute is billed by the user's own providers, a separate layer | Observed (site navigation) / Documented | [site](https://skypilot.ai/) |
| (b) Code licence | SPDX `Apache-2.0` (`gh api repos/skypilot-org/skypilot/license`) | Observed | [repository](https://github.com/skypilot-org/skypilot) |
| (c) Data reuse | Bundled instance catalogs derive from provider pricing pages and APIs; their reuse terms follow each provider (not reviewed) | Unknown | — |

Not in the PR #82 shortlist. Provider price data is a #39/#41 question.

## Counterexample

- **Suffices (hypothesis, documented basis):** an ML team that knows its model and GPU need ("8×H100, under a cost cap, spot if possible, any of these clouds") gets placement, fallback and execution. For "where should this run?" Pick Your AI's plan adds little and cannot reserve capacity.
- **Falls short (hypothesis):** it starts after the stack is chosen. No model, quantization, runtime, retrieval or agent advice, and no translation from a workload to an accelerator count. A bounded export of a Pick Your AI plan into a SkyPilot task YAML is a plausible complement (#9/#37).

## Matrix consistency

Historical comparison with merged [PR #87](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/87): `deployment`, `saved`, `share`, `export` Documented; `model_versions` Unknown. Agrees. `constraints` and `multi_gpu` appear documented in the YAML spec but are Unknown in #87; proposed to #49, not edited here.

## Open questions and routing

- #9/#37: whether a plan-to-YAML export is in scope; plans must not imply reserved capacity.
- #39: price-catalog freshness for cost estimates.
