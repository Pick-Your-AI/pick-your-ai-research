# T5: Fine-Tuned Model

Issue: #33 · Contract: 1.0.0 · Kinds: `fine_tuned_model`
Status: ready for review · Last researched: 2026-10-16

## User decision

What artifact does customisation produce, and what does it require from serving, hosting and evaluation?

The artifact is one of:
- a **LoRA (or other PEFT) adapter** that needs its exact base model at serving time;
- **merged full weights**;
- a **GGUF** conversion of either;
- a **provider-hosted model** whose weights never leave the provider.

The builder must know which, because it decides the compatible inference engines (#11), the GPU sizing (#10), the hosting options (#9) and the evaluation gate (#36).

Deployment modes:
- **API:** artifact is provider-hosted (`api_only`).
- **Managed:** hosted, or downloadable, depending on the service (#30).
- **Self-hosted:** adapter, merged weights or GGUF.

Serving support matrices are owned by #11, and evaluation methodology by #36. This note defines the artifact and the facts those issues consume.

## Candidate options

### Artifact types

| Type | `artifact_format` / `adapter_only` | Produced by | Needs at serving time | Evidence |
| --- | --- | --- | --- | --- |
| PEFT LoRA adapter | `safetensors` / `true` | TRL+PEFT, Axolotl, Unsloth, LLaMA-Factory, ms-swift, NeMo; Together and Fireworks downloads (#30) | Exact base model (id + revision); engine with LoRA support; rank and target modules within engine limits | V1, V4, G2 |
| Merged full weights | `safetensors` / `false` | PEFT `merge_and_unload()`, framework export commands (#30) | Any engine supporting the architecture; same VRAM as the base | V1, V11 |
| GGUF (merged) | `gguf` / `false` | Axolotl, Unsloth natively; llama.cpp converters (#30 F34) | llama.cpp-family engines; vLLM support is experimental | V5, V6 |
| GGUF LoRA adapter | `gguf` / `true` | llama.cpp `convert_lora_to_gguf.py` | llama.cpp with the matching base GGUF; **not** Ollama ≥0.34.1 | V5, V7 |
| Provider-hosted | `api_only` / n/a | OpenAI, Vertex Gemini tuning, Bedrock customisation, Foundry (OpenAI models) | The provider's endpoint; lifecycle tied to the provider | V13–V17 |

### Inference engines: adapter and format support

This is support for **fine-tuned artifacts** specifically; the full serving matrix belongs to #11.

| Engine (release, licence) | Dynamic LoRA | Documented limits | LoRA on quantised base | Merged HF | GGUF / GGUF LoRA | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| vLLM v0.31.0 (2026-10-05, Apache-2.0) | Yes: runtime load/unload API, resolver plugins, MoE expert LoRA | `max_lora_rank` ∈ {1, 8, 16, 32, 64, 128, 256, 320, 512}, default 16; `max_loras` default 1. Rejects DoRA, bias, and `modules_to_save` other than `score`/`classifier` | AWQ, GPTQ, bitsandbytes (examples and tests) | Yes | GGUF "highly experimental and under-optimized"; GGUF LoRA unknown | V1, V2 |
| SGLang v0.5.21 (2026-10-02, Apache-2.0) | Yes: load/unload endpoints, pinning | `max_loras_per_batch` default 8. Max rank and target modules inferred from startup adapters unless set. Rejects DoRA and adapters that add vocabulary | Code present, undocumented (unknown) | Yes | `gguf` listed as a quantisation; GGUF LoRA unknown | V3 |
| TGI v3.3.7 (2025-12-19, Apache-2.0) | Startup only (`LORA_ADAPTERS`) | unknown | unknown | Yes | unknown | V4 |
| llama.cpp b11699 (2026-10-16, MIT) | Yes: `--lora`, `--lora-scaled`, `POST /lora-adapters`, per-request `lora`; requests with different LoRA configs are not batched together | Rank limit unknown | Adapter applied without modifying base weights; quantised-base behaviour undocumented | After GGUF conversion | Native GGUF and GGUF LoRA. The converter errors on adapters containing `embed_tokens`/`lm_head` ("new tokens added during fine tuning") | V5, V6 |
| Ollama v0.40.5 (2026-10-14, MIT) | **No**: since v0.34.1 `create` rejects any `ADAPTER` with "LoRA adapters are no longer supported", and rejects GGUF files of adapter type | n/a | n/a | Yes (`FROM` a safetensors directory) | GGUF full models only | V7 |
| TensorRT-LLM v1.2.1 (2026-04-20, Apache-2.0) | Multi-LoRA via `LoRARequest`; HF and NeMo adapter formats | `max_lora_rank`, `max_loras`, `max_cpu_loras`, `lora_target_modules`. DoRA only on the legacy build path | FP8 example ("LoRA works with quantized models") | Yes | No GGUF | V8 |
| MLX-LM v0.32.2 (2026-10-16, MIT) | `adapters` path in server | lora, dora, full | QLoRA when the model is quantised | `mlx_lm.fuse` (`--dequantize`) | `--export-gguf` limited to Mistral/Mixtral/Llama-style in fp16; MLX adapter format is not PEFT (unconfirmed) | V9 |

TGI's GitHub repository is archived. Its README says: "text-generation-inference is now in maintenance mode" (V4). It should be catalogued as `deprecated` for new builds.

### Managed serving of fine-tunes

| Provider | Import / export | Serving mode | Lock-in | Lifecycle | Evidence |
| --- | --- | --- | --- | --- | --- |
| Together | Imports PEFT adapters (HF or S3) against a supported `baseModelId`; validates format, base and rank. Exports `adapter` or `merged` | **Dedicated endpoints only**: "Serverless LoRA inference (including Serverless Multi-LoRA) has been discontinued". Multi-LoRA on one dedicated endpoint, or merged deploy | Low | Billed per minute per replica, even idle; adapter versioning not supported | V12, #31 P1 |
| Fireworks | Uploads PEFT adapters: rank 4–64; fixed target-module list; no `embed_tokens`; no `quantization_config`. Downloads LoRA | On-demand deployments only; "Serverless deployment is not supported for LoRA models". FP8/FP4 deployment shapes cannot enable add-ons | Medium | unknown | V13 |
| Vertex (open models) | Tuned safetensors checkpoints in the user's Cloud Storage; "You can also export the tuned model … and deploy it elsewhere" | Model Garden custom-weights deployment | Low | — | V14, #30 M7 |
| Vertex (Gemini) | No export documented | Tuned-model endpoint | High | Behaviour when the base is deprecated: unknown | V14 |
| Bedrock | Bedrock-tuned models: no export documented. Custom Model Import accepts HF-format safetensors for a fixed architecture list (Llama, Mistral/Mixtral, Qwen2/2.5/3, GPT-OSS and others), <200 GB text, <128K context, transformers 4.51.3 | Provisioned Throughput; on-demand for some Nova and Llama 3.3 70B customisations made on or after 2025-07-16 | High for Bedrock-tuned | unknown | V15 |
| Microsoft Foundry | No export for OpenAI models | Standard, Global, Data Zone, Developer (no hourly hosting fee; deployment lasts 24 h); managed compute for LoRA adapters (preview) | High for OpenAI models | A deployment with no calls for more than 15 days "is automatically deleted… The underlying customized model remains available" (classic Foundry FAQ) | V16 |
| OpenAI | No export | Hosted | Total | "Fine-tuned versions of these models follow the same shutdown schedule as their underlying base models"; job creation ends for everyone on 2027-01-06 | V17, #30 M2 |

## Comparison fields

These cover the CatalogItem envelope plus `spec_fine_tuned_model`. The issue's conceptual fields map as follows:
- `artifact id` → `/id`
- `base model (→ #6)` → `base_model_ref`
- `format` → `artifact_format` and `adapter_only`
- `portability` → `supported_access_modes` (`api` vs `weights`)
- `method`, `license`, `version` and `evaluation results link` need the fields proposed below.

| Field / JSON pointer | Type and unit | Finding | Evidence | Conditions / unknowns |
| --- | --- | --- | --- | --- |
| `/spec/base_model_ref` | `model` catalog ID | Immutable lineage. Must equal the selected model (baseline `rule.training.base.lineage`) | contract | v1 IDs carry no revision; pin the revision in provenance (see below) |
| `/spec/training_framework_ref` | `training_framework` catalog ID | e.g. `cat.training_framework.trl` (#30) | contract | — |
| `/spec/training_dataset_ref` | `training_dataset` catalog ID | (#32) | contract | — |
| `/spec/artifact_format` | enum `safetensors, gguf, onnx, pytorch, api_only, other` | Checked against `inference_engine.spec.model_formats` (baseline `rule.training.artifact.engine`) | contract | The format alone cannot tell an adapter from merged weights; `adapter_only` is needed too |
| `/spec/adapter_only` | boolean | True for LoRA/PEFT adapters | V1–V8 | — |
| `/spec/supported_access_modes` | array of `api`, `weights` | `api` for provider-hosted; `weights` for downloadable | V12–V17 | — |
| `base_model_revision` (proposed) | full 40-character commit SHA or digest | Hugging Face rejects short hashes; branches and tags move | G1, G3 | Proposal to #40 |
| `adapter.rank`, `adapter.target_modules`, `adapter.peft_variant` (lora / dora / …), `adapter.modules_to_save` (proposed) | integer; list; enum; list | Determine engine and provider acceptance (V1, V3, V13) | G2 | Proposal to #40 |
| `base_quantization` (proposed) | enum `none, nf4, int8, awq, gptq, fp8, fp4` | Affects LoRA serving (V1, V13) and merge accuracy (V11) | — | Proposal to #40 |
| `added_tokens` (proposed) | boolean | Blocks adapter serving on SGLang, llama.cpp conversion, Fireworks and vLLM | V1, V3, V6, V13 | Proposal to #40 |
| `method` (proposed) | enum shared with #30 | — | #30 | — |
| `license` (envelope) | SPDX id or `other` + link | Derived from the base licence and the training-data licences (table below) | G6–G10 | — |
| `evaluation_report_ref` (proposed) | EvaluationReport ID | Gate results from #36 | Q1–Q6 | — |
| `signature` (proposed) | URI of an OpenSSF model-signing bundle | Optional integrity proof | G5 | — |

### Provenance record

| Field | Meaning | Evidence |
| --- | --- | --- |
| HF `base_model`, `base_model_relation` (`adapter`, `merge`, `quantized`, `finetune`) | Builds the Hub model tree; can be set explicitly | G1 |
| HF `datasets`, `license`, `license_name`, `license_link`, `model-index` | Training datasets, licence, structured evaluation results with a `source` | G1 |
| PEFT `base_model_name_or_path`, `revision`, `peft_type`, `peft_version`, `r`, `lora_alpha`, `target_modules`, `modules_to_save` | Written to `adapter_config.json` | G2 |
| SPDX 3.0.1 `AIPackage`, relationships `trainedOn`, `testedOn`, `descendantOf` | AI-BOM | G4 |
| CycloneDX `machine-learning-model` component, `modelCard`, `pedigree.ancestors` | AI-BOM | G4 |
| OpenSSF `model_signing` (PyPI 1.1.1, 2025-10-10) | Signs a manifest of file digests as an in-toto statement in a Sigstore bundle; verification re-hashes files | G5 |

### Licence obligations on the fine-tuned artifact

| Base licence | Naming / attribution | Notice | Use restrictions carry? | Evidence |
| --- | --- | --- | --- | --- |
| Llama 4 Community | Name must begin with "Llama"; display "Built with Llama" | Copy of the agreement plus the Meta notice | Yes (Acceptable Use Policy); >700M MAU needs a separate licence | G6, #30 L1 |
| Gemma Terms (Gemma 1–3n) | — | Copy of the agreement; "prominent notices" on modified files; Gemma notice | Yes: §3.2 restrictions must be an enforceable provision downstream | G7, #30 L5 |
| Gemma 4 / Apache-2.0 | — | §4(a) licence copy for every recipient; §4(b) change notices on modified files; §4(c) keep copyright, patent, trademark and attribution notices in the Source form of distributed Derivative Works; §4(d) carry the applicable NOTICE attributions only if the base distribution includes a NOTICE file (A-18a to A-18c) | No | G8, #30 L7 |
| MIT | — | Copyright and permission notice | No | #30 L15, L18 |
| CC BY-NC 4.0 (base or dataset) | Attribution | — | Yes: non-commercial only | G9, #32 R16 |
| CC BY-SA (dataset) | Attribution | — | Creative Commons' guidance says publicly shared models "based on" SA content would need the same licence; whether this reaches weights is legally unsettled | #32 R16 |
| OpenMDW-1.1 | — | Agreement copy and notices of origin | No; rights end on patent or copyright litigation | G10, #30 L21 |

## Evidence

Entries accessed on 2026-10-16 unless a later re-check is recorded in the row. Grades follow the interim policy in `docs/RESEARCH_METHOD.md` until #41 finalises it. Engine facts come from release-tagged sources.

### Serving (V)

| ID | Publisher and URL | Access date | Version / region | Evidence grade | Limitations / reuse terms |
| --- | --- | --- | --- | --- | --- |
| V1 | vLLM, https://github.com/vllm-project/vllm/blob/v0.31.0/docs/features/lora.md ; `vllm/config/lora.py`; `vllm/lora/peft_helper.py`; `examples/features/lora/lora_with_quantization_offline.py` | 2026-10-16 | v0.31.0 | Primary documentation | — |
| V2 | vLLM, https://github.com/vllm-project/vllm/blob/v0.31.0/docs/features/quantization/gguf.md ; PR https://github.com/vllm-project/vllm/pull/28545 | 2026-10-16 | v0.31.0 | Primary documentation | `lora_extra_vocab_size` removed 2025-11-21 |
| V3 | SGLang, https://github.com/sgl-project/sglang/blob/v0.5.21/docs/docs/advanced_features/lora.mdx ; `python/sglang/srt/lora/lora_manager.py` | 2026-10-16 | v0.5.21 | Primary documentation | — |
| V4 | Hugging Face, https://github.com/huggingface/text-generation-inference (README; `docs/source/conceptual/lora.md`) | 2026-10-16 | v3.3.7; repository archived | Primary documentation | Maintenance mode |
| V5 | ggml-org, https://github.com/ggml-org/llama.cpp/blob/b11699/tools/server/README.md ; PR #8332 | 2026-10-16 | b11699 | Primary documentation | — |
| V6 | ggml-org, https://github.com/ggml-org/llama.cpp/blob/b11699/convert_lora_to_gguf.py | 2026-10-16 | b11699 | Primary documentation | Added-token adapters rejected |
| V7 | Ollama, https://github.com/ollama/ollama/blob/v0.40.5/server/create.go (lines 42, 107–108) ; `docs/import.mdx` | 2026-10-16 | v0.40.5; removal since v0.34.1 | Primary documentation | Re-checked directly |
| V8 | NVIDIA, https://github.com/NVIDIA/TensorRT-LLM/blob/v1.2.1/docs/source/features/lora.md ; `docs/source/legacy/advanced/lora.md` | 2026-10-16 | v1.2.1 | Primary documentation | — |
| V9 | Apple MLX, https://github.com/ml-explore/mlx-lm/blob/v0.32.2/mlx_lm/LORA.md ; `mlx_lm/SERVER.md` | 2026-10-16 | v0.32.2 | Primary documentation | — |
| V11 | Hugging Face PEFT, https://github.com/huggingface/peft/blob/v0.21.2/src/peft/tuners/lora/bnb.py ; `docs/source/developer_guides/checkpoint.md`, `quantization.md`, `troubleshooting.md` | 2026-10-16 | v0.21.2 | Primary documentation | Warns: "Merge lora module to 4-bit linear may get different generations due to rounding errors"; AQLM merges impossible |
| V12 | Together AI, https://docs.together.ai/docs/lora-inference ; https://docs.together.ai/docs/dedicated-endpoints/adapter ; https://docs.together.ai/docs/custom-models | 2026-10-16 | — | Primary documentation | Serverless LoRA discontinued (re-checked directly) |
| V13 | Fireworks AI, https://docs.fireworks.ai/fine-tuning/deploying-loras ; https://docs.fireworks.ai/models/uploading-custom-models | 2026-10-16 | — | Primary documentation | — |
| V14 | Google Cloud, https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/open-model-tuning ; https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/gemini-use-supervised-tuning | 2026-10-16 | updated 2026-10-15 | Primary documentation | Whether PEFT_ADAPTER output is merged is unknown |
| V15 | AWS, https://docs.aws.amazon.com/bedrock/latest/userguide/model-customization-import-model.html ; https://docs.aws.amazon.com/bedrock/latest/userguide/deploy-custom-model-on-demand.html | 2026-10-16 | — | Primary documentation | Whether import accepts adapters is unknown |
| V16 | Microsoft, https://learn.microsoft.com/en-us/azure/foundry/fine-tuning/overview ; https://learn.microsoft.com/en-us/azure/foundry-classic/openai/faq | 2026-10-16 | — | Primary documentation | 15-day auto-delete stated in the classic FAQ only |
| V17 | OpenAI, https://developers.openai.com/api/docs/deprecations | 2026-10-16 | — | Primary documentation | — |

### Provenance and licences (G)

| ID | Publisher and URL | Access date | Version / region | Evidence grade | Limitations / reuse terms |
| --- | --- | --- | --- | --- | --- |
| G1 | Hugging Face, https://huggingface.co/docs/hub/model-cards | 2026-10-16 | — | Primary documentation | — |
| G2 | Hugging Face PEFT, https://github.com/huggingface/peft/blob/main/src/peft/config.py ; `src/peft/tuners/lora/config.py` | 2026-10-16 | main | Primary documentation | — |
| G3 | Hugging Face, https://huggingface.co/docs/huggingface_hub/guides/download | 2026-10-16 | — | Primary documentation | Full-length commit hash required |
| G4 | SPDX, https://spdx.github.io/spdx-spec/v3.0.1/model/AI/Classes/AIPackage/ ; CycloneDX, https://cyclonedx.org/docs/1.6/json/ | 2026-10-16 | SPDX 3.0.1; CycloneDX 1.6 (1.7.2 latest release) | Primary documentation | — |
| G5 | OpenSSF, https://github.com/sigstore/model-transparency ; https://pypi.org/project/model-signing/ | 2026-10-16 | 1.1.1 (2025-10-10) | Primary documentation | — |
| G6 | Meta, https://dev.meta.ai/llama/llama4/license/ | 2026-10-16 | effective 2025-04-05 | Primary documentation | Acceptable Use Policy text not re-fetched here (#30 L2) |
| G7 | Google, https://ai.google.dev/gemma/terms | 2026-10-16 | modified 2026-04-01 | Primary documentation | Gemma 1–3n only |
| G8 | Apache Software Foundation, https://www.apache.org/licenses/LICENSE-2.0 ; Google, https://ai.google.dev/gemma/apache_2 | 2026-10-16 | 2.0 | Primary documentation | Section 4(a)–(d) conditions re-read for A-18a to A-18c. The Google page was not re-fetched for that correction. Section 4(c) is not encoded as a rule |
| G9 | Creative Commons, https://creativecommons.org/licenses/by-nc/4.0/legalcode.en | 2026-10-16 | 4.0 | Primary documentation | — |
| G10 | OpenMDW, https://raw.githubusercontent.com/OpenMDW/OpenMDW/refs/heads/main/1.1/LICENSE.OpenMDW-1.1 | 2026-10-16 | 1.1 | Primary documentation | Derivatives not mentioned explicitly |

### Evaluation (Q)

| ID | Publisher and URL | Access date | Version / region | Evidence grade | Limitations / reuse terms |
| --- | --- | --- | --- | --- | --- |
| Q1 | Qi et al., https://arxiv.org/abs/2310.03693 | 2026-10-16 | — | Independent measurement | GPT-3.5 Turbo and Llama-2-7b-Chat, 2023 |
| Q2 | Biderman et al., LoRA Learns Less and Forgets Less, https://arxiv.org/abs/2405.09673 | 2026-10-16 | — | Independent measurement | Llama-2-7B; code and math domains |
| Q3 | Microsoft, https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/fine-tuning-safety-evaluation | 2026-10-18 | Updated 2026-07-31; preview guide | Primary documentation | Re-checked directly: separate data/model assessments; predefined thresholds and a modification-request route, not an account-specific exception |
| Q4 | OpenAI, https://developers.openai.com/api/docs/guides/supervised-fine-tuning | 2026-10-16 | — | Primary documentation | Training-data moderation not described in current docs |
| Q5 | Mazeika et al., HarmBench, https://arxiv.org/abs/2402.04249 ; MLCommons, https://mlcommons.org/ailuminate/ | 2026-10-16 | AILuminate Safety v1.0 | Independent measurement | — |
| Q6 | EleutherAI, https://pypi.org/project/lm-eval/ | 2026-10-16 | 0.4.13 (2026-08-31), MIT | Primary documentation | — |
| Q7 | Google Cloud, https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/evaluation-overview ; AWS, https://docs.aws.amazon.com/bedrock/latest/userguide/custom-models.html | 2026-10-16 | — | Primary documentation | No Bedrock training-time safety gate found |

## Compatibility proposals

These rules are proposed for review by #40 using the [rule proposal template](../../templates/rule-proposal.md). They refine the baseline rules:
- `rule.training.artifact.engine` checks format only;
- `rule.training.base.lineage` checks base identity;
- `rule.training.model.capable` checks that the training path is complete.

When an artifact field is missing, the rule returns `unknown`, never `pass`.

"Source checked" in the Status column means the cited primary text was read on its access date and supports the assertion. It follows the interim "checked" definition in the owner's adopted #41 policy ([#75 review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75#pullrequestreview-5550616927)). Nothing here is independently verified (reproduced or confirmed by a second source), and a result that passes on checked evidence stays unverified. Licence rules state a document's conditions; whether they apply to a particular artifact is a legal question this note does not decide.

| Rule | Participating fields | Assertion | Outcome / severity | Evidence | Status |
| --- | --- | --- | --- | --- | --- |
| A-01 | `adapter_only` = true, `inference_engine` = Ollama ≥0.34.1 | Adapters rejected; merge or convert to a full model first | fail / error | V7 | source checked |
| A-02 | `adapter.peft_variant` = dora, engine ∈ {vLLM, SGLang} | DoRA adapters rejected; merge first | fail / error | V1, V3 | source checked |
| A-03 | `added_tokens` = true or `modules_to_save` includes `embed_tokens` / `lm_head`, `adapter_only` = true | Adapter serving fails on SGLang, the llama.cpp converter, Fireworks and vLLM; serve merged weights | fail / error | V1, V3, V6, V13 | source checked |
| A-04 | `adapter.rank` > engine or provider max | Rejected (Fireworks r ∉ 4–64; vLLM above `max_lora_rank`, configurable) | fail / error (warning on vLLM: raise the limit) | V1, V13 | source checked |
| A-05 | adapter base id / revision ≠ served base | Lineage mismatch | fail / error | G2, V12 | source checked (extends `rule.training.base.lineage` to revision) |
| A-06 | `base_quantization` ∈ {nf4, int8}, merge into the quantised base | Rounding deviations expected; merge into the 16-bit base instead | pass / warning | V11 | source checked warning; "merge into 16-bit" is an inference (no PEFT doc states it positively) |
| A-07 | provider = Fireworks, deployment shape FP8/FP4, multi-LoRA | Add-ons unavailable; use BF16 or live merge | fail / error | V13 | source checked |
| A-08 | provider ∈ {Together, Fireworks}, `adapter_only` = true | No serverless serving; dedicated or on-demand cost applies | pass / warning (cost) | V12, V13 | source checked |
| A-09 | `artifact_format` = gguf, engine = vLLM | Experimental support | pass / warning | V2 | source checked |
| A-10 | engine = TGI | Maintenance mode, archived | pass / warning (deprecated) | V4 | source checked |
| A-11 | `supported_access_modes` = [`api`] and the build needs self-hosting or portability | Provider-locked artifact cannot move | fail / error | V14–V17 | source checked |
| A-12 | provider = OpenAI fine-tune, base model deprecation date | Fine-tune shuts down with its base | pass / warning (lifecycle) | V17 | source checked |
| A-13 | provider = Foundry, no calls for 15 days | Deployment auto-deleted; model kept | pass / info | V16 | partial: classic-FAQ wording |
| A-14 | Bedrock Custom Model Import, architecture not listed or size/context limits exceeded | Import unsupported | fail / error | V15 | source checked |
| A-15 | `base_model_revision` is a branch, tag or short hash | Lineage not immutable | fail / error | G3 | source checked (needs the proposed field) |
| A-16 | base licence = Llama 4, distributed, name lacks the "Llama" prefix or "Built with Llama" is missing | Licence condition unmet | fail / error | G6 | source checked |
| A-17 | base licence = Gemma Terms (≤3n), distributed, downstream terms lack the §3.2 restrictions | Licence condition unmet | fail / error | G7 | source checked |
| A-18a | established distribution of the Apache-2.0 Work or a Derivative Work; licence copy absent | Section 4(a): recipients of the Work or a Derivative Work must receive a copy of the licence | fail / error when applicable and missing; unknown / warning when applicability is unresolved; skipped / info when known not applicable | G8 | source checked; classification is not inferred from artifact format |
| A-18b | established distribution of modified files of the Apache-2.0 Work; prominent change notices absent | Section 4(b): modified files must carry prominent notices stating that they were changed | fail / error when applicable and missing; skipped / info when no modified files are distributed; unknown / warning when modification or legal applicability is unresolved | G8 | source checked; neither modified-file status nor exemption follows from `adapter_only` |
| A-18c | established distribution of an Apache-2.0 Derivative Work; the pinned base distribution includes a NOTICE file; applicable attribution notices absent | Section 4(d): preserve a readable copy of applicable NOTICE attributions in one of the permitted locations, excluding notices that do not pertain to the Derivative Work | fail / error when applicable and missing; skipped / info when known not applicable or the base includes no NOTICE; unknown / warning when applicability or base NOTICE presence is unresolved | G8 | source checked; needs the proposed `base_notice_file_present` fact |
| A-19 | base or any training-data licence = CC BY-NC, commercial use | Non-commercial restriction carries | fail / error | G9, #32 R16 | source checked |
| A-20 | `evaluation_report_ref` missing, or safety gate not passed (see handoff to #36) | Not deployable | unknown / error | Q1, Q3 | policy proposal for #36 |

## Pricing and capacity

Not priced here:
- **Serving cost** of a fine-tune is the base model's serving cost plus:
  - dedicated-endpoint hours for adapters on Together and Fireworks (V12, V13);
  - hosting hours on Foundry (#31 P5);
  - storage and Provisioned Throughput on Bedrock (#31 P4).
- **VRAM:** a merged model needs the same VRAM as its base. An adapter adds roughly 2·N_lora bytes per loaded adapter (#31). Sizing belongs to #10, aggregation to #39.

## Recommendation and rationale

1. **Keep both an adapter and a merged checkpoint**, pinned to the base's full commit SHA.
   - Adapters are small and portable across vLLM, SGLang, TensorRT-LLM, Together and Fireworks.
   - Merged weights are the only form that works everywhere: Ollama, adapters with added tokens, DoRA, TGI, Bedrock import.
2. **Merge into the 16-bit base, then quantise.** PEFT warns that merging into 4- or 8-bit weights changes generations (V11).
3. **Avoid adding tokens** unless required. Added tokens block adapter serving on most engines and providers (A-03).
4. **Prefer portable managed paths** (Vertex open models, Together, Fireworks) unless lock-in is acceptable. Show the lifecycle risk for OpenAI and Foundry fine-tunes (A-12, A-13).
5. **Record provenance:**
   - HF card `base_model` / `base_model_relation`;
   - PEFT config;
   - a training-data reference (#32 Croissant record);
   - licence obligations (table above);
   - optionally an OpenSSF model-signing bundle.
6. **Gate deployment on #36's evaluation set.** Minimum proposal:
   - **Safety and refusal regression against the base** on the same suite. Fine-tuning on 10 adversarial examples took GPT-3.5 Turbo's harmfulness rate from 1.8% to 88.8%, and benign Alpaca fine-tuning took it from 5.5% to 31.8% (Q1).
   - **Separate pre-training data and post-training model assessments.** The Foundry preview guide describes a data screen that fails a job when detected harmful content exceeds its severity threshold, followed by a separate model evaluation before deployment. Its predefined evaluation thresholds are not customer-configurable or tied to a custom content-filter configuration, but the guide also provides a request route for modified fine-tuning safety thresholds (Q3; re-read 2026-10-18). That route establishes neither approval nor eligibility for a particular account. This aligns with the [#36 safety-screen supplement](../T6-deployment-operations/evaluation.md#foundry-training-data-harm-screen); provider checks do not establish the proposed builder evaluation gate or receiving-owner acceptance.
   - **Capability retention against the base** on general benchmarks, because both LoRA and full fine-tuning forget (Q2).
   - **Target-task gain over the base** (Q4).
   - **Provenance and licence integrity checks** (A-15 to A-19).

## Structured artifacts

No CatalogItem proposals. A `fine_tuned_model` is specific to the user and produced by a run. Its references must resolve to catalog items that do not exist yet: a `model` (#6), a `training_dataset` (#32), and `training_framework` items (proposed in #30 / PR #68). The reusable facts here belong to:
- `inference_engine` items, owned by #11. The engine facts above are a handoff, not proposals from this issue.
- the proposed `fine_tuned_model` fields, sent to #40.

## Open questions and handoffs

| Question | Follow-up issue / owner |
| --- | --- |
| Serving support matrix: adopt the adapter and format facts above in `inference_engine` items (vLLM, SGLang, llama.cpp, Ollama, TensorRT-LLM, MLX-LM; TGI as deprecated) | #11 · @Mattycodes69 |
| VRAM for adapters (per loaded adapter) and merged models | #10 · @Mattycodes69 |
| Evaluation gate: safety regression vs base, capability retention, task gain, training-data harm screen; thresholds and suites (HarmBench, AILuminate, lm-evaluation-harness) | #36 · @PUSHINGSQUARES |
| Fine-tune serving and hosting costs next to training cost | #39 · @PUSHINGSQUARES |
| Proposed fields: `base_model_revision`, adapter rank / target modules / PEFT variant / `modules_to_save`, `base_quantization`, `added_tokens`, `method`, `evaluation_report_ref`, `signature`, `base_notice_file_present` (needed by A-18c); revision-pinned catalog references | #40 · @tynamite |
| Base-model licence, revision, whether the base distribution at that revision includes a NOTICE file, and provider fine-tuning lifecycle facts | #6, #5 · @zwright8 |
| Deployment-time handling of lifecycle (OpenAI shutdown with base; Foundry 15-day deletion) | #37 · @PUSHINGSQUARES |
| Unknowns: vLLM/SGLang LoRA on GGUF bases; SGLang on quantised bases; TGI and llama.cpp LoRA limits; Vertex PEFT_ADAPTER output form; Bedrock import of adapters; Fireworks retention; tuned-Gemini lifecycle on base deprecation | #33 · @appletechie |

None of the handoffs above is confirmed yet.
