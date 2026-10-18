# Hugging Face Hub — competitor profile

Status: draft for owner review ([#50](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/50)). Entity ID: `hugging-face`. Classification: Partial competitor, Data source, Infrastructure provider (analyst judgement). Evidence classes are defined in the [index](README.md#evidence-classes).

| Field | Value |
| --- | --- |
| Product | Hugging Face Hub model directory, model cards, Inference Providers / Endpoints |
| Operator | Hugging Face |
| URLs | [models](https://huggingface.co/models), [model cards docs](https://huggingface.co/docs/hub/model-cards), [terms of service](https://huggingface.co/terms-of-service) |
| Access date | 2026-10-16 |
| Version / revision | ToS "Effective Date: September 15, 2022" as displayed; Hub is continuously updated; individual repositories are git-versioned |
| Access tier observed | Logged-out public pages; no account, token or API call |
| robots.txt | Allows all |

## Workflow

| Stage | Finding | Class | Source |
| --- | --- | --- | --- |
| Inputs | Filters for task (50+), parameter-count range, library (PyTorch, Transformers, GGUF, ...), language, licence, inference provider; sort | Observed (filter UI in page) | [models](https://huggingface.co/models) |
| Constraints | Filters only; a per-user hardware list exists in the page state (`userHardwareItems`, empty when logged out). Hardware-fit behaviour requires an account and was not seen | Observed (field) / Unknown (behaviour) | [models](https://huggingface.co/models) |
| Selection logic | None beyond filter and sort; the user chooses | Observed | [models](https://huggingface.co/models) |
| Explanation | Publisher-authored model cards (Markdown plus metadata: licence, datasets, eval results) | Documented | [model cards docs](https://huggingface.co/docs/hub/model-cards) |
| Save/share/export | Collections and likes exist (account); repositories cloneable at an exact commit; no build record | Documented / Unknown for build save | [model cards docs](https://huggingface.co/docs/hub/model-cards) |

## Architecture and data

- Data: publisher-uploaded repositories; model-card metadata is self-reported and may be incomplete. Documented.
- Versioning: every repository is git; commit hashes give reproducible citations. Documented. This is a stronger revision primitive than most profiled products.
- Inference: list of inference providers (including OpenRouter, DeepInfra and HF Inference) shown as filters. Observed.

## Commercial access, code licence and data rights

| Layer | Finding | Class | Source |
| --- | --- | --- | --- |
| (a) Commercial access | Free public Hub; paid PRO, Team & Enterprise, Inference Providers, Inference Endpoints and storage (rates not recorded) | Observed (navigation) | [models](https://huggingface.co/models) |
| (b) Code licence | Hub service closed; client libraries open source (not assessed here). Each model repository carries its own declared licence | Documented | [model cards docs](https://huggingface.co/docs/hub/model-cards) |
| (c) Data reuse | ToS defines "Content" as material posted by "you, we, or any third party"; rights follow each repository's licence and gating terms | Documented (terms) | [terms of service](https://huggingface.co/terms-of-service) |

Historical comparison with merged [PR #82](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/82): automated retrieval via the documented API, internal research and display of factual identifiers (id, revision, declared licence, size) with a link: yes; redistribution of card text or files only where the repository licence permits. This profile agrees.

## Counterexample

- **Suffices (hypothesis, observed filters):** an ML engineer who already knows the task and runtime (e.g. GGUF text generation under 12B, permissive licence) finds candidates by filter and pins a commit. For that model-search step Pick Your AI is redundant.
- **Falls short (hypothesis):** no workload intake, no ranking for the user's constraints in the logged-out view, cards are publisher claims, and nothing composes runtime, retrieval, hosting or cost.

## Matrix consistency

Historical comparison with merged [PR #87](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/87): `model_search`, `model_compare`, `model_versions`, `export` Documented; `saved`, `share` Unknown. Agrees. `hardware_fit` stays Unknown until an account-based check.

## Open questions and routing

- #6/#41: prefer metadata links and exact revisions over copying assets; reuse #30/PR #68 training work rather than another framework inventory.
- #66 or a later authorised check: logged-in hardware compatibility view.
