# T5: Training Framework

Issue: #30 · Contract: 1.0.0 · Kinds: `training_framework`
Status: source corrections and receiving packet ready for review · Last researched: 2026-10-18

Decision-record revision: `training-framework-decision/0.2.0` (research proposal; not an adopted ruleset). The 2026-10-16 candidate inventory and source access dates remain historical. The **2026-10-18 source audit** below replaces the identified permission, component-license, method/backend and export claims; it does not silently refresh the other inventory cells or the four CatalogItem proposals.

## User decision

Can the selected model be customised, and with which method and tool?

The decision requires the selected base model and revision, applicable terms and weight access (#6), the exact provider offering/account/region/date (#5), and the framework, adapter library, method, backend and configuration that implement the requested operation. A positive fact on one axis cannot grant permission or technical support on another. This note compares three training channels:

- **First-party training API:** model APIs (OpenAI, Gemini API, Anthropic, Mistral, Cohere). Availability and artifact export are properties of the selected offering; the channel label itself establishes neither.
- **Managed training service:** cloud fine-tuning services (Vertex AI, Bedrock, Microsoft Foundry, Together, Fireworks). Some return downloadable weights or adapters.
- **User-operated training framework:** open frameworks run on user compute (TRL, PEFT, Axolotl, Unsloth, LLaMA-Factory, ms-swift, NVIDIA NeMo stack, torchtune).

These channel labels do not determine the serving deployment mode. T0's deployment mode (#3) decides the mode by who operates the *serving* runtime and on what capacity ([PR #81](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/81), merged), and that definition governs serving. A fine-tuned model's serving mode follows T0, not the channel used to train it. For example, a LoRA trained on Together, downloaded as an adapter and served with its matching base model on user-operated compute would be T0 "Self-hosted", even though its training channel above is a managed training service ([Together deployment documentation](https://docs.together.ai/docs/fine-tuning/deployment#run-locally), accessed 2026-10-17). T0 defines no mode for a training run; see K-08 in #31.

Compute sizing (#31) and dataset preparation (#32) are out of scope. Their required input handoffs, and the resulting artifact handoff to #33, are defined below. Selecting no training capability makes these training rules non-applicable; it does not invalidate an otherwise complete serving build.

## Candidate options

The following inventory records publisher-documented candidates as of **2026-10-16**, with specific later corrections identified by R-source IDs. Versions, dates, example counts, ranks, limits and billing quantities are **published**, not locally measured or estimated. Release identity does not pin a separate `main` documentation page to that release. Unqualified source branches, missing regions, stale lifecycle entries and method-specific limitations remain visible in the evidence register and must be resolved for a selected configuration.

The method and backend columns are discovery lists, **not a Cartesian-product support matrix**. SFT/DPO name objectives; LoRA/full fine-tuning describe parameter updates; QLoRA additionally depends on a supported quantized-base configuration. PEFT supplies adapters to a trainer rather than a standalone SFT/DPO training service (R1–R4). F-23 below requires evidence for their actual combination.

### Self-hosted frameworks

| ID | Version (release date) | License | Methods (contract enum) | Other documented methods | Backends (contract enum) | Output formats | Distributed | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `trl` | 1.16.0 (2026-10-15) | Apache-2.0 | sft, dpo, distillation; lora/qlora via PEFT | GRPO, KTO, reward modelling, RLOO; experimental CPO, GKD, online DPO, ORPO | cuda (implied), other (AWS Trainium) | HF checkpoints, PEFT adapters | yes (DDP, DeepSpeed, FSDP, multi-node) | F1–F4 |
| `peft` | 0.21.2 (2026-10-01) | Apache-2.0 | lora, qlora; adapter library used with a trainer | DoRA, AdaLoRA, IA3, LoHa, LoKr, OFT/BOFT, VeRA, prompt/prefix tuning | cuda (implied), tpu, metal, cpu; no per-method parity inferred | adapter safetensors or pytorch; conditional merge, not every method/quantization supports it | yes (DeepSpeed, FSDP; selected integration required) | F5–F7; R2 |
| `axolotl` | 0.21.0 (2026-10-16) | Apache-2.0 | sft, lora, qlora, full_finetune, dpo, distillation | continued pretraining, IPO, ORPO, SimPO/CPO, KTO, GRPO, reward models, QAT | cuda, rocm, metal (partial: no QLoRA or DeepSpeed on MPS), other (Ascend NPU, no parity) | safetensors (merged), gguf (`axolotl export`, merge first) | yes (FSDP/FSDP2, DeepSpeed, multi-node, TP/CP/EP) | F8–F13 |
| `unsloth` | PyPI 2026.10.6 (2026-10-15); package identity separate from current source snapshot | Component-specific: Apache-2.0 core plus AGPL components; current source includes Studio and MoE kernels (R7); exact wheel composition unknown | sft, lora, qlora, full_finetune, dpo | pretraining, GRPO, GSPO, FP8 training | cuda, rocm, oneapi, metal (MLX) discovery claims; library/Desktop/Studio and exact method need separate admission; CPU recipe support is not training support | LoRA adapters, merged 16-bit safetensors, gguf, NVFP4/FP8; selected exporter/configuration required | multi-GPU and DeepSpeed ZeRO-2/3 reported; multi-node unknown | F14–F17; R7 |
| `llamafactory` | 0.9.5 (2026-05-30) | Apache-2.0 | sft, lora, qlora, full_finetune, dpo | continued pretraining, reward modelling, PPO, KTO, ORPO, SimPO, freeze-tuning, OFT, DoRA | cuda, rocm, other (Ascend NPU) | merged weights via `llamafactory-cli export` plus an Ollama Modelfile; no gguf (F36) | yes (DeepSpeed ZeRO-3, FSDP, multi-node, Megatron-core) | F18–F20 |
| `ms-swift` | 4.6.0 (2026-10-13) | Apache-2.0 | sft, lora, qlora, full_finetune, dpo, distillation (GKD) | pretraining, DoRA, KTO, CPO, SimPO, ORPO, GRPO family, PPO | cuda, rocm, metal, cpu, other (Ascend, MetaX, MUSA) | merged safetensors; AWQ/GPTQ/FP8/BNB quantised export, Ollama Modelfile; no gguf (F37) | yes (DDP, DeepSpeed, FSDP/FSDP2, Megatron) | F21–F22 |
| `nemo-megatron-bridge` | 0.6.2 (2026-09-18) | Apache-2.0 | sft, lora | pretraining, DoRA | cuda | HF-format export via `save_hf_pretrained`; no gguf (F38) | yes (TP/PP/CP/EP, multi-node) | F23–F24 |
| `nemo-automodel` | 0.6.0 (2026-08-26) | Apache-2.0 | sft, lora, qlora, distillation | pretraining, QAT | cuda | safetensors (HF-compatible), PyTorch DCP; gguf input only, no export (F38) | yes (FSDP2, HSDP, TP, CP, SP, PP, multi-node) | F25–F26 |
| `nemo-rl` | 0.7.0 (2026-07-29) | Apache-2.0 | sft, lora, dpo, distillation | GRPO, DAPO, GDPO, GSPO, PPO | cuda | unknown | yes (FSDP2, Megatron, multi-node) | F27–F28 |
| `torchtune` | 0.6.1 (2025-04-07) | BSD-3-Clause | sft, lora, qlora, full_finetune, dpo, distillation | PPO, GRPO, QAT | cuda, rocm, oneapi, metal, other (Ascend) | safetensors (HF format) | yes (FSDP2, multi-node) | F29–F31 |

**Excluded or flagged:**
- **torchtune:** no longer maintained. Development stopped on 2025-07-15, and the README says it "wound down in 2025" (F29, F30). The builder should list it as `deprecated` and not recommend it for new builds.
- **NeMo:** the `NVIDIA/NeMo` repo now covers speech and multimodal only (F32). LLM fine-tuning moved to Megatron-Bridge, AutoModel and NeMo-RL, so those three replace the single "NeMo" candidate.
- **torchforge:** paused, with development consolidated into torchtitan (F33). Not a candidate.

### Managed services

| ID | Status | Methods (contract enum) | Other methods | Customisable models (summary) | Data format | Artifact / portability | Pricing unit | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `vertex-gemini-tuning` | active | sft | preference tuning (2.5 Flash, Flash-Lite only), RL fine-tuning (listed for 3.5 Flash), continuous tuning | Gemini 3.5 Flash, 3.1 Flash-Lite, 2.5 Pro / Flash / Flash-Lite | JSONL, documented minimum 100–500 examples | provider-hosted adapter-based model; no export documented | per 1,000 training tokens (dataset tokens × epochs) | M5, M6, M8 |
| `vertex-open-model-tuning` | active | sft, lora (`PEFT_ADAPTER`), full_finetune (`FULL`), distillation | — | Gemma 4/3, Qwen 3.x, Llama 3.1–3.3, Llama 4 Scout, GLM 4.7 Flash; distillation teachers include DeepSeek R1/V3.2, GLM 5.2, Kimi K2 Thinking | JSONL (prompt-completion, chat `messages`, GenerateContent) | **portable**: safetensors written to the user's Cloud Storage | per 1,000,000 training tokens | M7, M8 |
| `bedrock-customization` | active | sft, distillation | reinforcement fine-tuning (GRPO with Lambda or model-as-judge rewards), preference optimisation, full-rank fine-tuning, continued pretraining (Titan) | Nova family, Titan, Llama 3.1–3.3; RFT on Nova 2 Lite, gpt-oss-20B, Qwen3 32B; Claude 3 Haiku still listed but end-of-life in us-west-2 since 2026-09-10 (L30) | `.jsonl`; SFT schema unknown | **provider-locked**: Provisioned Throughput or on-demand custom deployment; no export documented | per 1,000 training tokens; monthly storage; Provisioned Throughput per model unit-hour | M9–M14 |
| `foundry-fine-tuning` | active | sft, dpo, distillation (teacher-generated SFT data) | RFT (o4-mini; gpt-5 by invitation) | gpt-4o, gpt-4.1 family, gpt-4o-mini; gpt-oss-20b/120b, Llama-3.3-70B, Qwen3 family, Ministral-3B and others | chat JSONL `messages`, separate train and validation files | **provider-locked** for OpenAI models; LoRA adapters run on managed compute; download not documented | training per 1M tokens (per hour for RFT); hosting per hour | M15–M17 |
| `together-fine-tuning` | active | sft, lora (default), full_finetune, dpo | GRPO (separate product) | DeepSeek V3.1/V4 Flash, GLM 5.x, Qwen 3.5–3.8, Kimi K2.x, Gemma 4, gpt-oss, Llama 3.x/4, Mixtral 8x7B | JSONL (conversational, instruction, preference, generic text) or tokenised Parquet; 100 GB file limit | Download depends on job type: LoRA supports `merged`, `adapter` or `model_output_path`; full fine-tuning supports only `model_output_path` (R5) | per 1M tokens, with a minimum charge per job | M18–M22; R5 |
| `fireworks-fine-tuning` | active | sft, lora (rank ≤32, power of 2), dpo, full_finetune (Training API) | ORPO, RL (Training API), vision SFT | most of the catalog for managed LoRA; full-parameter for DeepSeek V4, GLM 5.x, Kimi K3, Qwen3.x, Gemma 4 | OpenAI-compatible chat JSONL, 3 to 3M examples | **portable** for LoRA (`firectl model download`, needs the matching base model); full-weight download unknown | per 1M training tokens, tiered by model size and method | M23–M26 |
| `openai-fine-tuning` | **winding down; account/date eligibility required** | sft, dpo | RFT (o4-mini), vision fine-tuning (gpt-4o) | gpt-4.1, gpt-4.1-mini, gpt-4.1-nano historical offering inventory; check the selected base lifecycle | chat JSONL `messages`, minimum 10 examples | Provider-hosted; derived-model inference follows the selected base's shutdown, separately from the new-job cutoff (R8) | not extracted (page is rendered in JavaScript) | M1–M4; R8 |
| `mistral-fine-tuning-api` | **deprecated** | sft | Classifier Factory | open-mistral-7b, mistral-small, codestral, nemo, mistral-large, ministral-8b/3b, pixtral-12b | JSONL `messages` | unknown | $4 minimum per job plus $2/month storage per model; token unit unknown | M27–M29 |

**OpenAI new-job wind-down dates (M2; rechecked 2026-10-18 in R8):**
- 2026-05-07: organisations that never ran fine-tuning can no longer create jobs.
- 2026-07-02: organisations without fine-tuned inference in the last 60 days can no longer create jobs.
- 2027-01-06: job creation ends for all customers.

These dates do not establish a common inference shutdown. The same source lists 2026-10-23 for the fine-tuned GPT-3.5/GPT-4/GPT-4.1 nano/babbage/davinci groups and 2027-01-14 for the listed GPT-4o/GPT-4o mini/GPT-4.1/GPT-4.1 mini base snapshots and their fine-tuned derivatives. Preserve each exact provider/base identity and cutoff; the lifecycle handoff from #5 is accepted only with that separation (H2).

### First-party API fine-tuning availability

| Provider | Customer fine-tuning on own API | Alternate channel | Weights retrievable | Evidence |
| --- | --- | --- | --- | --- |
| OpenAI | winding down (see above) | Microsoft Foundry | no | M2, M15 |
| Google Gemini | not available in the Gemini API or AI Studio | Vertex AI (Gemini Enterprise Agent Platform) | no | L26, M5 |
| Anthropic Claude | not available | none current: Bedrock's fine-tuning table still lists Claude 3 Haiku (us-west-2), but AWS's lifecycle page shows it reached end of life there on 2026-09-10, and Legacy models accept no new fine-tuning jobs | no | M10, L30 |
| Mistral | deprecated | Forge (sales-led; pre-training, SFT, LoRA, DPO, RL; inference on private cloud, on-prem or Mistral compute) | unknown: no source states weight export or licence terms | M27, L31 |
| Cohere | deprecated on 2025-09-15 | — | no | L33 |

## Comparison fields

These fields cover the CatalogItem envelope plus `spec_training_framework`. The issue's conceptual fields map as follows:
- `framework / service id` → `/id`
- `methods` → `/spec/methods`
- `output artifact format` → `/spec/model_formats`
- `source` → `/provenance`

The issue lists `supported models`, `input data format` and `export path`. v1 has no field for these, so they stay in this note; see the proposed extensions under Open questions.

| Field / JSON pointer | Type and unit | Candidate finding | Evidence ID | Conditions / unknowns |
| --- | --- | --- | --- | --- |
| `/id` | string, stable catalog ID | see the candidate tables | — | One version per ID under current intake rules |
| `/version` | string, selected upstream release/package version | e.g. `trl` 1.16.0 | F1; R1 | Pin source commit and dependency/configuration evidence separately; a latest release lookup does not upgrade the selection |
| `/license` | optional object; `/license/spdx_id` string, `/license/commercial_use_allowed` and `/license/self_hosting_allowed` booleans, all optional | Framework license summary | [frozen CatalogItem schema](../../contracts/v1/schemas/catalog-item.schema.json); R7, R9 | An empty object is not permission. Component-specific licenses are not an interchangeable dual-license choice. Model `/spec/license_ref` is an opaque string and needs a separate normalized terms assessment (H1) |
| `/spec/methods` | array of enum `sft, lora, qlora, dpo, full_finetune, distillation`, min 1 | see the candidate tables | per row | v1 cannot express GRPO, PPO, KTO, ORPO, RFT, continued pretraining, preference optimisation or DoRA |
| `/spec/backends` | array of enum `cuda, rocm, oneapi, metal, tpu, cpu, other`, min 1 | see the candidate tables | per row | Managed services have no user-visible backend. `other` hides Trainium and Ascend. Support levels differ by method |
| `/spec/model_formats` | optional array of enum `safetensors, gguf, onnx, pytorch, api_only, other`; unique values, empty array permitted by v1 | Format discovery, separate from artifact kind and conversion route | per row; R2–R6 | Axolotl delegates GGUF export to a llama.cpp checkout and requires an eligible merged source; standalone adapter conversion has separate architecture/tensor/base restrictions. ONNX remains a [conditional downstream route](onnx-export-boundary.md) without an executed tuple. An empty or unmarked list is not an exhaustive negative |
| `/spec/distributed_supported` | boolean | true for all self-hosted candidates; not applicable to managed | per row | The boolean cannot distinguish multi-GPU from multi-node (Unsloth multi-node is unknown) |
| `supported models` (note only) | selected catalog ID/version plus immutable upstream checkpoint/revision and architecture/configuration; strings/references, no physical unit | summarised per service | per row | Family membership is insufficient; preserve source date, offering, region and completeness scope |
| `input data format` (note only) | selected trainer/loader/version plus objective-specific fields, template/tokenizer/processor revision and loss-mask configuration; no physical unit | TRL SFT text/messages or prompt-completion; DPO paired preference; other objectives have distinct schemas | R1, R3; per service row | JSONL/Parquet is a container, not evidence that the contents satisfy the selected trainer. No new enum is adopted; H3 receives the research requirement |
| `export path` (note only) | artifact kind plus exact source/base revisions, exporter/converter version/options, destination and integrity/rights references; no physical unit | Conditional adapter, merged checkpoint, raw training output or provider-hosted result | R2–R6; M7 | Unknown export is distinct from documented no export. Download capability does not establish delivery, base entitlement, conversion success or serving compatibility; H4 receives the boundary |
| `status` (lifecycle) | `/status` string in the frozen enum; offering availability additionally needs operation/account/region/effective-date evidence | torchtune maintenance warning; OpenAI new-job restrictions; Mistral/Cohere deprecation | F29, M2, M27, L33; R8 | A deprecated label alone proves neither disabled job creation nor stopped inference; executable lifecycle mapping belongs to #40 |

## Evidence

F/M/L entries retain their **2026-10-16** access dates. R entries record the bounded **2026-10-18** readback. Grades follow the interim policy in `docs/RESEARCH_METHOD.md` and the current #41 mapping; release identities, capability evidence, source checking and independent verification remain distinct.

Claims whose cited primary text was retrieved were source checked on the recorded access date; the limitations below remain unconfirmed. None of these claims is independently verified. The four CatalogItem proposals therefore carry `verification_status: unverified` for every provenance entry.

The original fetch work was split across three research passes. Claims not retrieved directly from the page are marked in the Limitations column. The later audit does not certify an unretrieved cell or rebind historical `main` documentation to a selected package. No training, conversion, provider job, paid benchmark or model download was executed for this record.

### Self-hosted frameworks (F)

| ID | Publisher and URL | Access date | Version / region | Evidence grade | Limitations / reuse terms |
| --- | --- | --- | --- | --- | --- |
| F1 | Hugging Face, https://github.com/huggingface/trl/releases/tag/v1.16.0 | 2026-10-16 | v1.16.0 | Primary documentation | — |
| F2 | Hugging Face, https://github.com/huggingface/trl/blob/main/README.md | 2026-10-16 | main | Primary documentation | Hardware support is only implied |
| F3 | Hugging Face, https://raw.githubusercontent.com/huggingface/trl/main/docs/source/dataset_formats.md | 2026-10-16 | main | Primary documentation | — |
| F4 | Hugging Face, https://raw.githubusercontent.com/huggingface/trl/main/docs/source/distributing_training.md | 2026-10-16 | main | Primary documentation | — |
| F5 | Hugging Face, https://github.com/huggingface/peft/releases/tag/v0.21.2 | 2026-10-16 | v0.21.2 | Primary documentation | — |
| F6 | Hugging Face, https://github.com/huggingface/peft/blob/main/README.md | 2026-10-16 | main | Primary documentation | Hardware listed via Accelerate |
| F7 | Hugging Face, https://raw.githubusercontent.com/huggingface/peft/main/docs/source/developer_guides/checkpoint.md | 2026-10-16 | main | Primary documentation | — |
| F8 | Axolotl, https://github.com/axolotl-ai-cloud/axolotl/releases/tag/v0.21.0 | 2026-10-16 | v0.21.0 (released 2026-10-16; capabilities checked against v0.20.0 docs and the current README) | Primary documentation | — |
| F9 | Axolotl, https://github.com/axolotl-ai-cloud/axolotl/blob/main/README.md | 2026-10-16 | main | Primary documentation | — |
| F10 | Axolotl, https://raw.githubusercontent.com/axolotl-ai-cloud/axolotl/main/docs/support-matrix.qmd | 2026-10-16 | main | Primary documentation | — |
| F11 | Axolotl, https://raw.githubusercontent.com/axolotl-ai-cloud/axolotl/main/docs/dataset-formats/index.qmd | 2026-10-16 | main | Primary documentation | — |
| F12 | Axolotl, https://raw.githubusercontent.com/axolotl-ai-cloud/axolotl/main/docs/export.qmd | 2026-10-16 | main | Primary documentation | — |
| F13 | Axolotl, https://raw.githubusercontent.com/axolotl-ai-cloud/axolotl/main/docs/mac.qmd | 2026-10-16 | main | Primary documentation | — |
| F14 | Unsloth, https://github.com/unslothai/unsloth/blob/main/README.md | 2026-10-16 | main | Primary documentation | Component-specific licenses; the former "dual license" summary is corrected by R7 |
| F15 | Unsloth, https://pypi.org/pypi/unsloth/json | 2026-10-16 | 2026.10.6 | Primary documentation | The GitHub "latest" release is a desktop beta, not the library |
| F16 | Unsloth, https://unsloth.ai/docs/basics/inference-and-deployment/saving-to-gguf | 2026-10-16 | — | Primary documentation | — |
| F17 | Unsloth, https://unsloth.ai/docs/get-started/fine-tuning-for-beginners/unsloth-requirements | 2026-10-16 | — | Primary documentation | — |
| F18 | hiyouga, https://github.com/hiyouga/LlamaFactory/releases/tag/v0.9.5 | 2026-10-16 | v0.9.5 | Primary documentation | — |
| F19 | hiyouga, https://github.com/hiyouga/LlamaFactory/blob/main/README.md | 2026-10-16 | main | Primary documentation | — |
| F20 | hiyouga, https://raw.githubusercontent.com/hiyouga/LlamaFactory/main/data/README.md | 2026-10-16 | main | Primary documentation | — |
| F21 | ModelScope, https://github.com/modelscope/ms-swift/blob/main/README.md | 2026-10-16 | main | Primary documentation | — |
| F22 | ModelScope, https://github.com/modelscope/ms-swift/releases/tag/v4.6.0 | 2026-10-16 | v4.6.0 | Primary documentation | — |
| F23 | NVIDIA, https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/main/README.md | 2026-10-16 | main | Primary documentation | — |
| F24 | NVIDIA, https://github.com/NVIDIA-NeMo/Megatron-Bridge/releases/tag/v0.6.2 | 2026-10-16 | v0.6.2 | Primary documentation | — |
| F25 | NVIDIA, https://github.com/NVIDIA-NeMo/Automodel/blob/main/README.md | 2026-10-16 | main | Primary documentation | — |
| F26 | NVIDIA, https://github.com/NVIDIA-NeMo/Automodel/releases/tag/v0.6.0 | 2026-10-16 | v0.6.0 | Primary documentation | — |
| F27 | NVIDIA, https://github.com/NVIDIA-NeMo/RL/blob/main/README.md | 2026-10-16 | main | Primary documentation | The PyPI `nemo-rl` package is a 0.0.0 placeholder |
| F28 | NVIDIA, https://github.com/NVIDIA-NeMo/RL/releases/tag/v0.7.0 | 2026-10-16 | v0.7.0 | Primary documentation | — |
| F29 | Meta PyTorch, https://github.com/meta-pytorch/torchtune/blob/main/README.md | 2026-10-16 | main | Primary documentation | Not maintained |
| F30 | Meta PyTorch, https://github.com/meta-pytorch/torchtune/issues/2883 | 2026-10-16 | 2025-07-15 | Primary documentation | — |
| F31 | Meta PyTorch, https://raw.githubusercontent.com/meta-pytorch/torchtune/main/docs/source/deep_dives/checkpointer.rst | 2026-10-16 | main | Primary documentation | — |
| F32 | NVIDIA, https://github.com/NVIDIA-NeMo/Speech/blob/main/README.md | 2026-10-16 | v3.0.0 | Primary documentation | — |
| F33 | Meta PyTorch, https://github.com/meta-pytorch/torchforge/blob/main/README.md | 2026-10-16 | main | Primary documentation | — |
| F34 | ggml-org, https://github.com/ggml-org/llama.cpp/blob/master/convert_lora_to_gguf.py | 2026-10-16 | master | Primary documentation | Takes a PEFT adapter directory (`adapter_config.json` + `adapter_model.safetensors` or `.bin`); `--outtype` f32, f16, bf16, q8_0, auto |
| F35 | Hugging Face TRL, https://github.com/huggingface/trl/blob/main/docs/source/unsloth_integration.md | 2026-10-16 | main | Primary documentation | GGUF only via Unsloth's `save_pretrained_gguf` |
| F36 | hiyouga, https://github.com/hiyouga/LlamaFactory/blob/main/README.md ; `src/llamafactory/train/tuner.py` | 2026-10-16 | main | Primary documentation | Export writes an Ollama Modelfile; no GGUF writer in source |
| F37 | ModelScope, https://github.com/modelscope/ms-swift/blob/main/docs/source/Instruction/Frequently-asked-questions.md | 2026-10-16 | main | Primary documentation | FAQ: only Modelfile export is supported, not direct GGUF |
| F38 | NVIDIA, https://github.com/NVIDIA-NeMo/Automodel/blob/main/nemo_automodel/components/checkpoint/utils.py ; Megatron-Bridge repository code search | 2026-10-16 | main | Primary documentation | AutoModel handles GGUF as input only; Megatron-Bridge has no GGUF writer |

### Managed services (M)

| ID | Publisher and URL | Access date | Version / region | Evidence grade | Limitations / reuse terms |
| --- | --- | --- | --- | --- | --- |
| M1 | OpenAI, https://developers.openai.com/api/docs/guides/model-optimization | 2026-10-16 | global | Primary documentation | — |
| M2 | OpenAI, https://developers.openai.com/api/docs/deprecations | 2026-10-16 | global | Primary documentation | — |
| M3 | OpenAI, https://developers.openai.com/api/docs/guides/supervised-fine-tuning | 2026-10-16 | global | Primary documentation | — |
| M4 | OpenAI, https://developers.openai.com/api/docs/pricing | 2026-10-16 | USD | Primary documentation | Training unit not extracted (JavaScript-rendered) |
| M5 | Google Cloud, https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/tune-models | 2026-10-16 | job region selectable; `us` and `eu` multi-region | Primary documentation | Vertex AI is now titled "Gemini Enterprise Agent Platform" |
| M6 | Google Cloud, https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/gemini-use-supervised-tuning | 2026-10-16 | — | Primary documentation | — |
| M7 | Google Cloud, https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/open-model-tuning | 2026-10-16 | global endpoint; us-central1, europe-west4, us-west1, us-east5, asia-southeast1, asia-southeast2 | Primary documentation | — |
| M8 | Google Cloud, https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing | 2026-10-16 | USD | Primary documentation | Units only; prices not recorded here |
| M9 | AWS, https://docs.aws.amazon.com/bedrock/latest/userguide/custom-models.html | 2026-10-16 | — | Primary documentation | — |
| M10 | AWS, https://docs.aws.amazon.com/bedrock/latest/userguide/custom-model-fine-tuning.html | 2026-10-16 | us-east-1, us-west-2 per model | Primary documentation | — |
| M11 | AWS, https://docs.aws.amazon.com/bedrock/latest/userguide/reinforcement-fine-tuning.html | 2026-10-16 | us-east-1, us-west-2 | Primary documentation | — |
| M12 | AWS, https://docs.aws.amazon.com/bedrock/latest/userguide/model-distillation.html | 2026-10-16 | — | Primary documentation | Teacher and student list not fetched |
| M13 | AWS, https://docs.aws.amazon.com/bedrock/latest/userguide/model-customization-use.html | 2026-10-16 | — | Primary documentation | — |
| M14 | AWS, https://aws.amazon.com/bedrock/pricing/ | 2026-10-16 | USD | Primary documentation | Units only |
| M15 | Microsoft, https://learn.microsoft.com/en-us/azure/foundry/fine-tuning/overview | 2026-10-16 | docs revision 2026-10-06 | Primary documentation | Training-region table not fetched |
| M16 | Microsoft, https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/fine-tuning | 2026-10-16 | v1 API | Primary documentation | — |
| M17 | Microsoft, https://azure.microsoft.com/en-us/pricing/details/cognitive-services/openai-service/ | 2026-10-16 | USD | Primary documentation | Units only |
| M18 | Together AI, https://docs.together.ai/docs/fine-tuning-overview | 2026-10-16 | — | Primary documentation | — |
| M19 | Together AI, https://docs.together.ai/docs/fine-tuning-models | 2026-10-16 | — | Primary documentation | Some tunable models cannot be deployed as dedicated endpoints |
| M20 | Together AI, https://docs.together.ai/docs/fine-tuning-data-preparation | 2026-10-16 | — | Primary documentation | — |
| M21 | Together AI, https://www.together.ai/pricing | 2026-10-16 | USD | Primary documentation | Units only |
| M22 | Together AI, https://docs.together.ai/docs/deploying-a-fine-tuned-model | 2026-10-16 | — | Primary documentation | — |
| M23 | Fireworks AI, https://docs.fireworks.ai/fine-tuning/fine-tuning-models | 2026-10-16 | — | Primary documentation | — |
| M24 | Fireworks AI, https://docs.fireworks.ai/fine-tuning/models | 2026-10-16 | — | Primary documentation | — |
| M25 | Fireworks AI, https://docs.fireworks.ai/fine-tuning/deploying-loras | 2026-10-16 | — | Primary documentation | — |
| M26 | Fireworks AI, https://fireworks.ai/pricing | 2026-10-16 | USD | Primary documentation | Units only |
| M27 | Mistral AI, https://docs.mistral.ai/resources/deprecated/finetuning/text_vision_finetuning | 2026-10-16 | — | Primary documentation | Deprecated |
| M28 | Mistral AI, https://docs.mistral.ai/resources/deprecated/customization | 2026-10-16 | — | Primary documentation | — |
| M29 | Mistral AI, https://mistral.ai/pricing | 2026-10-16 | USD | Primary documentation | Training token unit not found |

### Model licenses and provider terms (L)

| ID | Publisher and URL | Access date | Version / region | Evidence grade | Limitations / reuse terms |
| --- | --- | --- | --- | --- | --- |
| L1 | Meta, https://dev.meta.ai/llama/llama4/license/ | 2026-10-16 | Llama 4 Community License, effective 2025-04-05 | Primary documentation | — |
| L2 | Meta, https://dev.meta.ai/llama/llama4/use-policy/ | 2026-10-16 | Llama 4 AUP | Primary documentation | — |
| L3 | Meta, https://huggingface.co/meta-models/Muse-Spark-Open-816B-A42B | 2026-10-16 | Muse Model License; released 2026-10-15 | Primary documentation | License text is shown in the access gate; re-check after the launch week |
| L4 | Meta, https://huggingface.co/meta-models/Muse-Glimmer-30B | 2026-10-16 | Apache-2.0 | Primary documentation | — |
| L5 | Google, https://ai.google.dev/gemma/terms | 2026-10-16 | Gemma Terms of Use, modified 2026-04-01 | Primary documentation | Scope is the Terms' Appendix, not a numerical family range; see R11 |
| L6 | Google, https://ai.google.dev/gemma/prohibited_use_policy | 2026-10-16 | 2024-02-21 | Primary documentation | Incorporated by Terms §3.2 for the Appendix models; Gemma 4 has a separate license link (L5, L7; R11) |
| L7 | Google, https://ai.google.dev/gemma/docs/gemma_4_license | 2026-10-16 | Apache-2.0 | Primary documentation | — |
| L8 | Google, https://huggingface.co/google/gemma-4-31B-it | 2026-10-16 | — | Primary documentation | — |
| L9 | Mistral AI, https://huggingface.co/mistralai/Mistral-Medium-3.5-128B/raw/main/LICENSE | 2026-10-16 | Modified MIT | Primary documentation | — |
| L10 | Mistral AI, https://huggingface.co/mistralai/Devstral-2-123B-Instruct-2512/raw/main/LICENSE | 2026-10-16 | Modified MIT | Primary documentation | — |
| L11 | Mistral AI, https://mistral.ai/licences/MNPL-0.1.md | 2026-10-16 | MNPL-0.1 | Primary documentation | — |
| L12 | Alibaba Qwen, https://huggingface.co/Qwen/Qwen3.8-Flash-Next/raw/main/LICENSE | 2026-10-16 | Qwen Community License 1.0 | Primary documentation | — |
| L13 | Alibaba Qwen, https://huggingface.co/Qwen/Qwen3.8-2.4T-A95B/raw/main/LICENSE | 2026-10-16 | Qwen3.8-Max License | Primary documentation | — |
| L14 | Alibaba Qwen, https://huggingface.co/Qwen/Qwen3.8-27B | 2026-10-16 | Apache-2.0 | Primary documentation | Only three Qwen 3.8 checkpoints checked |
| L15 | DeepSeek, https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro-0813/raw/main/LICENSE | 2026-10-16 | MIT | Primary documentation | — |
| L16 | OpenAI, https://huggingface.co/openai/gpt-oss-120b | 2026-10-16 | Apache-2.0 | Primary documentation | — |
| L17 | OpenAI, https://github.com/openai/gpt-oss/blob/main/USAGE_POLICY | 2026-10-16 | — | Primary documentation | — |
| L18 | Microsoft, https://huggingface.co/microsoft/phi-4 | 2026-10-16 | MIT | Primary documentation | — |
| L19 | Moonshot AI, https://huggingface.co/moonshotai/Kimi-K3/raw/main/LICENSE | 2026-10-16 | Kimi K3 License | Primary documentation | — |
| L20 | Z.AI, https://huggingface.co/zai-org/GLM-5.3/raw/main/LICENSE | 2026-10-16 | GLM-5.3 License | Primary documentation | Other GLM-5.x checkpoints are MIT |
| L21 | OpenMDW, https://openmdw.ai/license/1-1/ | 2026-10-16 | OpenMDW-1.1 | Primary documentation | NVIDIA Nemotron 3.5 |
| L22 | Cohere Labs, https://huggingface.co/CohereLabs/tiny-aya-global, https://huggingface.co/CohereLabs/North-Small-Translate-1.0, https://huggingface.co/CohereLabs/North-Mini-Code-1.0 | 2026-10-16 | tiny-aya and North-Small-Translate: CC-BY-NC-4.0; North-Mini-Code and North-Micro-Vision: Apache-2.0 | Primary documentation | License varies per checkpoint within the North family |
| L23 | OpenAI Terms of Use, https://web.archive.org/web/20261012151003/https://openai.com/policies/row-terms-of-use/ | 2026-10-16 | Effective 2026-01-01; Wayback snapshot 2026-10-12 | Primary documentation (archived) | Live page returns 403. Unnumbered clause: "Use Output to develop models that compete with OpenAI" |
| L35 | OpenAI Services Agreement (API and business use), https://web.archive.org/web/20260213220105/https://openai.com/policies/services-agreement/ | 2026-10-16 | Effective 2026-01-01; Wayback snapshot 2026-02-13 | Primary documentation (archived) | §3.3(e) bars using Output to develop competing models "except for a Permitted Exception": non-distributed classifiers/embeddings, and fine-tuning OpenAI's own models |
| L24 | Google, https://ai.google.dev/gemini-api/terms | 2026-10-16 | — | Primary documentation | — |
| L25 | Anthropic, https://www.anthropic.com/legal/commercial-terms | 2026-10-16 | — | Primary documentation | Section D.4 |
| L26 | Google, https://ai.google.dev/gemini-api/docs/model-tuning | 2026-10-16 | — | Primary documentation | — |
| L30 | AWS, https://docs.aws.amazon.com/bedrock/latest/userguide/custom-model-fine-tuning.md (anchor `custom-model-supported`); https://docs.aws.amazon.com/bedrock/latest/userguide/model-lifecycle-legacy.md | 2026-10-16 | Claude 3 Haiku: legacy 2026-03-10, EOL 2026-09-10 (us-west-2 and most regions); ap-northeast-2, ap-south-1, ap-southeast-1 EOL 2026-10-17 | Primary documentation | The fine-tuning table is stale: it still lists a model already at EOL |
| L31 | Mistral AI, https://mistral.ai/products/forge/ | 2026-10-16 | — | Primary documentation | Licensing and export unknown |
| L32 | Mistral AI, https://legal.mistral.ai/terms/commercial-terms-of-service | 2026-10-16 | — | Primary documentation | — |
| L33 | Cohere, https://docs.cohere.com/docs/chat-starting-the-training | 2026-10-16 | — | Primary documentation | — |
| L34 | Cohere, https://cohere.com/terms-of-use | 2026-10-16 | — | Primary documentation | — |

### 2026-10-18 source audit (R)

Every R source was retrieved on **2026-10-18**. These are **Primary documentation**, source checked and **unverified**, not independent measurements. Web sources are current-state readbacks with region `not selected` and currency `not applicable` unless a cited source states otherwise. Pinned repository sources describe only the named commit. Public access and a blob identity do not establish reuse rights or a selected customer's entitlement.

| ID | Primary sources and exact identity | Supported correction and remaining limit |
| --- | --- | --- |
| R1 | Hugging Face TRL [v1.16.0 release](https://github.com/huggingface/trl/releases/tag/v1.16.0), commit `1b5c75ed94b7387f42532adb090c935166d4878d`; pinned [README](https://github.com/huggingface/trl/blob/1b5c75ed94b7387f42532adb090c935166d4878d/README.md), [dataset formats](https://github.com/huggingface/trl/blob/1b5c75ed94b7387f42532adb090c935166d4878d/docs/source/dataset_formats.md), [distributed training](https://github.com/huggingface/trl/blob/1b5c75ed94b7387f42532adb090c935166d4878d/docs/source/distributing_training.md) | Release published 2026-10-15; trainers, PEFT integration, objective-specific data and distributed configuration documented. Dataset blob `7fd3773e6480d6d7d0c9d1635484d12441badb95`; distributing blob `2d4a2c4c20624a35baa9565c742f038ce74f0ae6`. No selected workload fit or complete backend/method cross-product was tested |
| R2 | Hugging Face PEFT [v0.21.2 release](https://github.com/huggingface/peft/releases/tag/v0.21.2), commit `eaa35c777c7ba554a2a3639ac9c79bb690f39a57`; pinned [README](https://github.com/huggingface/peft/blob/eaa35c777c7ba554a2a3639ac9c79bb690f39a57/README.md) and [checkpoint guide](https://github.com/huggingface/peft/blob/eaa35c777c7ba554a2a3639ac9c79bb690f39a57/docs/source/developer_guides/checkpoint.md), guide blob `ea05731e56f0ad3582ab4831584ea7fe1204c422` | Release published 2026-10-01. Adapter weights exclude the base; config is required, but a nullable base name/revision is not an immutable binding. Merge support depends on method and quantization; merged models lose PEFT-specific functions |
| R3 | Axolotl [v0.21.0 release](https://github.com/axolotl-ai-cloud/axolotl/releases/tag/v0.21.0), commit `1f1eb05a391c43e65c1c5ee7ec6ea1b8a841d5d1`; pinned [Mac guide](https://github.com/axolotl-ai-cloud/axolotl/blob/1f1eb05a391c43e65c1c5ee7ec6ea1b8a841d5d1/docs/mac.qmd), blob `2e6c5c429e88ed4d1ad7cec10420ea962e030d6a`, and [support matrix](https://github.com/axolotl-ai-cloud/axolotl/blob/1f1eb05a391c43e65c1c5ee7ec6ea1b8a841d5d1/docs/support-matrix.qmd), blob `dc060e4a1bf3103a14fbf8ea9a29c0543a3e6e38` | Release published 2026-10-16. Mac guide lists full/LoRA support but no QLoRA, bitsandbytes or DeepSpeed; FSDP is untested. Matrix distinguishes objective, update strategy and quantization and explicitly blocks combinations. Its introduction still describes the 0.17.0 development line, so the pinned document is not proof that every listed feature shipped in 0.21.0 |
| R4 | Axolotl pinned [export guide](https://github.com/axolotl-ai-cloud/axolotl/blob/1f1eb05a391c43e65c1c5ee7ec6ea1b8a841d5d1/docs/export.qmd), blob `221255d2b8e597aaf789f18930770b9733b2261d`; llama.cpp [adapter converter](https://github.com/ggml-org/llama.cpp/blob/0878f7c304cc13915c831ae17694534c94940176/convert_lora_to_gguf.py), blob `f9adecbb11d8dcecd64794fd16a2a6bf6458fe27` | Axolotl shells out to a llama.cpp checkout, requires merged LoRA/QLoRA input and rejects prequantized source checkpoints. Standalone converter requires adapter config/tensors, an eligible base architecture and accepted tensor mappings; unsupported architectures or unexpected saved tensors can reject conversion. No universal PEFT-to-GGUF route or executed conversion is established |
| R5 | Together AI [fine-tuned deployment/download documentation](https://docs.together.ai/docs/fine-tuning/deployment) | LoRA supports `merged`, `adapter` and `model_output_path`; full fine-tuning supports only `model_output_path`. A raw training-output archive is not automatically a merged inference checkpoint. No actual job/checkpoint download was performed |
| R6 | Fireworks AI [LoRA deployment and download documentation](https://docs.fireworks.ai/fine-tuning/deploying-loras) | Downloadable PEFT addon, exact training base, local merge and subsequent serving are separate steps. The training base may differ from a public Hugging Face checkpoint. Platform-side merging is not evidence of a downloaded full checkpoint; this LoRA source does not establish Training API full-weight export |
| R7 | Unsloth commit `20531d9aac9cfd3c9faa0b1b42fa6c6e20d075b4`: [README](https://github.com/unslothai/unsloth/blob/20531d9aac9cfd3c9faa0b1b42fa6c6e20d075b4/README.md), [MoE README](https://github.com/unslothai/unsloth/blob/20531d9aac9cfd3c9faa0b1b42fa6c6e20d075b4/unsloth/kernels/moe/README.md), [grouped-GEMM source header](https://github.com/unslothai/unsloth/blob/20531d9aac9cfd3c9faa0b1b42fa6c6e20d075b4/unsloth/kernels/moe/grouped_gemm/interface.py), [MoE license](https://github.com/unslothai/unsloth/blob/20531d9aac9cfd3c9faa0b1b42fa6c6e20d075b4/unsloth/kernels/moe/LICENSE), [Studio license](https://github.com/unslothai/unsloth/blob/20531d9aac9cfd3c9faa0b1b42fa6c6e20d075b4/studio/LICENSE.AGPL-3.0) | Apache core and AGPL components are separately scoped. The MoE README (`0375c8d50796bd4aec2fdbadd2da0e0541d7ef42`) and source header explicitly identify AGPLv3, so "Studio only" is withdrawn. Both MoE license paths have blob `29ebfa545f5580919a4e884d7014d7a3eb2df762`; Studio license blob `be3f7b28e564e7dd05eaf59d64adba1a4065ac0e`. AGPL §13 concerns a modified version supporting remote interaction; distribution conditions remain separate. Exact 2026.10.6 wheel contents and the user's chosen components were not inspected |
| R8 | OpenAI [API deprecations](https://developers.openai.com/api/docs/deprecations) | New-job eligibility and exact base/derived-model inference shutdown are separate. Customer history is not public catalog data. No eligibility or continuing service is asserted for an unknown account |
| R9 | Apache Software Foundation [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0), January 2004 text | Copyright/patent grants have scope and conditions. Redistribution includes license/attribution duties and modified-file notices; NOTICE duties depend on the selected distribution containing NOTICE. An SPDX label alone does not settle the complete model, dataset, provider or intended-use assessment |
| R10 | Meta [Llama 4 Community License](https://dev.meta.ai/llama/llama4/license/), effective 2025-04-05, and [Acceptable Use Policy](https://dev.meta.ai/llama/llama4/use-policy/) | Distribution/product attribution, model-name requirements, the release-relative MAU condition and the multimodal EU eligibility condition have distinct applicability. A separate express grant and the specified end-user exceptions must be assessed, not erased by a family-wide rejection |
| R11 | Google [Gemma Terms](https://ai.google.dev/gemma/terms), modified 2026-04-01, §1.1(e), §3 and Appendix | Terms apply to Appendix models, with Gemma 4 linked separately. The derivative definition includes qualifying transfers of patterns/outputs for similar model behavior; outputs alone are not Model Derivatives. A distillation label alone does not prove every fact of that definition |
| R12 | Creative Commons [CC BY-NC 4.0 legal code](https://creativecommons.org/licenses/by-nc/4.0/legalcode.en), §1(i), §2 | NonCommercial concerns commercial advantage or monetary compensation; it is not the same predicate as non-production. The former combined MNPL/CC rule is withdrawn. L11's historical MNPL text was not freshly retrieved; admit its exact selected terms separately |
| R13 | Anthropic [Commercial Terms](https://www.anthropic.com/legal/commercial-terms), D.4; Google [Gemini API terms](https://ai.google.dev/gemini-api/terms), effective 2026-03-23 | Anthropic's express-approval exception is attached to D.4(a), not D.4(b)'s reverse-engineering/duplication or D.4(c)'s third-party assistance restrictions. Gemini API competing-model restrictions belong to that selected service; they do not determine every Google service's terms |

The original F/M/L register is retained as historical provenance. This audit withdraws the universal permission grants in F-01/F-06, the universal family/export implications in F-08/F-15/F-20, the combined non-production/non-commercial test in F-10, variable severity in F-16, the unsupported universal definition claim in F-17, and "Studio only" in F-24. Historical custom-license thresholds remain source leads, not executable catalog constants: F-06/F-07/F-09/F-11/F-12 require a normalized assessment of the selected terms, business scope and any alternative agreement. Lack of those facts remains an explicit unknown, not a favorable interpretation.

## Compatibility proposals

The following complete proposal uses the [#40 rule template](../../templates/rule-proposal.md). It preserves F-01–F-24 research identities while changing their assertions in revision `training-framework-decision/0.2.0`. #40 owns executable IDs, field placement, evidence admission, selection quantification, unknown policy and migration; no frozen v1 rule or field changes here.

### Shared participant and evaluation envelope

| Participant | Existing pointers and proposed information boundary |
| --- | --- |
| Enabled training selection and exact selected `training_framework` | Selection identity/role and catalog ID/version binding; framework `/spec/methods`, `/spec/backends`, `/spec/model_formats`, `/spec/distributed_supported`, `/license`, `/provenance`. Selected objective/update/quantization/configuration are note-only inputs until #40 defines them |
| Selected base `model` and, when used, a separately bound teacher `model` | `/spec/provider_ref`, `/spec/access_modes`, `/spec/weight_access`, `/spec/supports_fine_tuning`, `/spec/model_formats`, `/spec/license_ref`, `/license`, `/provenance`; immutable upstream checkpoint, normalized license version/terms, intended-use assessment and specific NOTICE/attribution artifacts remain note-only. No invented `weights_available` pointer |
| Exact `model_provider` offering | `/spec/supports_fine_tuning`, `/spec/supported_regions`, `/provenance`; service, account entitlement, operation, base revision, time interval and export policy are separately scoped note inputs. A provider-level positive boolean is not a complete model/method support assertion |
| User and intended use | Separate, authorized attestations/assessments for licensee, domicile/principal place, distribution, purpose, revenue/MAU period, and any required approval. These are not catalog facts. No actual user attestation or legal qualification is claimed here |
| Consumers | #31 receives configuration/resource inputs; #32 receives trainer/objective/data requirements; #33 receives exact artifact/base/export requirements; #11 owns serving compatibility. #6/#5 remain fact owners and #40/#41 own adoption/evidence policies |

Apply these steps to **each exact enabled training selection**, not any unrelated component in the build. A teacher and student have distinct identities and cannot be substituted by matching provider/family names.

1. **Applicability:** known absence of the optional training capability, or a known-false row condition, is `skipped`; unresolved applicability is `unknown`. Missing operation, component identity or terms cannot be treated as a known non-applicable case. A malformed selection remains an input-validation problem, not a fabricated compatibility result.
2. **Evidence admission:** use the exact selected version/operation/method/backend/configuration, region/account/date and source authority. Explicit requirements and limitations govern over broad feature lists. Scoped, independently checked documentation may be eligible while still `unverified`; unknown eligibility, unresolved equal-rank contradictions, unchecked evidence and unbound family claims do not manufacture a positive result. Apply #41's current freshness/conflict policy without inventing a TTL or bulk-upgrading historical provenance.
3. **Assertion:** each row asks a positive, bounded question. Eligible evidence satisfying it gives `pass`; an eligible explicit negative, failed required obligation or absence from a source explicitly complete for the same scope gives `fail`; missing facts or absence from an unmarked list gives `unknown`. An API or model `supports_fine_tuning: false` that actually covers the selected operation is a technical negative even if its license permits modification. A broad provider `true` does not override a selected-model negative.
4. **Severity and unknown policy:** severity is fixed by the row for `pass`, `fail`, `unknown` and `skipped`. No missing-data fallback changes it to `warning`. Proposed `on_unknown: review` keeps an unknown visible and does not grant permission to train, distribute or serve; any deployment-blocking policy must be separately adopted by #40. These are decision proposals, not authorization or executed rules.
5. **Explanation:** report the selection/roles, exact unmet or unknown condition, eligible source IDs, scope, proposed remediation and evidence grade actually used. A skipped, ineligible or wholly missing-source result has no checked-evidence badge. A `pass` on checked primary documentation retains `unverified`; neither repository tests nor a reviewer reading the source establishes an independently reproduced training/export result.

### Permission rules (model license → requested methods)

All rows use the shared envelope, dependencies and version boundary above. `Terms` below means the **normalized, selected** license/agreement and related obligations, not the opaque `/spec/license_ref` string. A permission pass is only that row's decision; weight access, provider offering, data rights and technical support must pass their own applicable checks.

| Rule | Applicability and participating inputs | Positive assertion | Fixed severity | Evidence / status | Explanation and remediation |
| --- | --- | --- | --- | --- | --- |
| F-01 | Training or distribution uses a selected base; Terms and requested objective/update method/use | Selected grants and obligations permit the requested operation; the scoped license/NOTICE/attribution assessment is satisfied | error | R9; L4/L7/L14–L18/L20/L21 are historical license leads. Project assessment requirement | Do not map Apache/MIT/OpenMDW strings to "every method permitted". Obtain the exact grant, restrictions and base distribution's applicable notices; then evaluate technical support separately |
| F-02 | Llama 4 Terms apply and the selected materials/derivative/product is distributed or made available | Required agreement copy, attribution and applicable NOTICE duties are satisfied for that act | warning | R10; source-checked clauses, proposed policy | Preserve the distinction between product attribution and the model-name condition in F-05; record the artifact/notice evidence in #33 |
| F-03 | Llama 4 multimodal Terms/AUP apply to the selected licensee and use | The licensee/use is eligible under the specified domicile/principal-place restriction or an applicable documented exception/grant | error | R10; source-checked clause, user facts unresolved | EU location is not a universal end-user rejection. Obtain the specific licensee/use assessment and any qualifying exception |
| F-04 | Llama 4 §2 applies; licensee/affiliates and release-relative MAU are known | The selected use meets the license's threshold condition or has the necessary separate express grant | error | R10; source-checked clause | The 700 million MAU test concerns the preceding calendar month at release, not an arbitrary current count. Missing attestation or grant is unknown; above-threshold with a qualifying grant is not an automatic failure |
| F-05 | Llama 4 materials/outputs are used to create/train/improve an AI model that is distributed or made available | The resulting model satisfies the applicable Llama naming condition | warning | R10; source-checked clause | The condition is broader than a `distillation` flag, and does not rename every undelivered experiment. Supply the exact resulting-model/use and naming evidence |
| F-06 | Selected Muse terms apply; requested method/use and derivative obligations | The exact Muse grant covers the requested operation and its applicable obligations are met | error | L3 historical; current selected-terms assessment required | Withdraw "every method allowed". Retrieve and normalize the applicable terms/revision, obligations and any separate agreement before a result |
| F-07 | Selected custom terms impose a commercial-service/revenue condition | The selected activity, entity scope, currency, period and threshold are assessed and any required separate agreement qualifies | error | L3/L13/L19 historical; scope/mapping hypothesis | Do not combine different licenses' thresholds into one family rule or use a revenue number without its period/currency/entity scope. Preserve applicable alternative grants |
| F-08 | Selected model is covered by the Gemma Terms Appendix; derivative/distribution facts known | If the result meets the Terms' Model Derivative definition, the applicable downstream Terms/notice/use obligations are met | warning | R11; source-checked definition and obligations | Evaluate transfer and intended similar behavior; outputs alone are not derivatives. Do not apply this record to all Gemma generations; hand the scoped obligation assessment to #33 |
| F-09 | Selected Mistral Modified MIT terms apply; relevant organization/revenue/use known | The requested rights are available under the applicable clause or a qualifying separate agreement | error | L9/L10 historical; selected-terms assessment required | Do not infer all rights are absent from a threshold alone. Obtain selected terms, defined revenue scope and the actual grant |
| F-10 | The selected grant is MNPL or CC BY-NC; exact intended use known | The operation satisfies **that grant's own** non-production or NonCommercial condition, or a qualifying alternative grant applies | error | R12 supports the CC definition; L11 historical MNPL, not freshly retrieved | Production and commercial purpose are independent inputs. No single `production` boolean decides both licenses; unresolved use or applicable terms remains unknown |
| F-11 | Selected Qwen Community terms impose MaaS/assistant conditions | The chosen activity is covered by the selected grant, including any required separate commercial license | error | L12 historical; selected-terms assessment required | Do not apply one checkpoint's license to the Qwen family; obtain exact activity and agreement scope |
| F-12 | Selected GLM terms require a security/approval review for the assessed activity | The applicable required review/approval is complete and covers this use | warning | L20 historical; conditional assessment proposal | A threshold or license string is not proof of a completed review. Record authorized approval evidence; leave missing requirements or decisions unknown |
| F-13 | Any training selection needs a model permission determination | An eligible, normalized selected license/agreement assessment exists | warning | H1 input sufficiency; project policy | Missing/unrecognized terms or an opaque reference alone produce unknown. This gate does not substitute for the substantive permission rows |

### Provider, access and technical rules

| Rule | Applicability and participating inputs | Positive assertion | Fixed severity | Evidence / status | Explanation and remediation |
| --- | --- | --- | --- | --- | --- |
| F-14 | User-operated training needs selected base weights; model access modes/weight access and entitlement | Required weights are actually accessible for the selected operation | error | Frozen model fields; H1; technical requirement | `weight_access: none` is an explicit negative for local weight training. `restricted` needs the actual grant/access; public listing or `open` does not resolve every permission requirement |
| F-15 | The requested outcome requires a downloadable adapter or full checkpoint | The selected service/job/artifact has a documented and qualified export path for that outcome | error | R2–R6; M7/M13; scoped proposal | Known provider-only result fails a download requirement; undocumented export is unknown. Distinguish raw output, adapter, merged weights and object-storage destination; do not infer export policy from an API-only base or channel label |
| F-16 | Selected provider output is used for synthetic-data training/distillation; exact agreement and intended student/use known | The selected agreement permits that use or its expressly scoped exception/approval applies, with other restrictions still met | error | L23/L35 historical OpenAI terms; R13; L34 historical Cohere | Preserve OpenAI API Permitted Exceptions separately from consumer terms. Anthropic D.4(a) approval does not waive D.4(b) or D.4(c). Apply only the agreement governing this service/account; pass does not lower severity |
| F-17 | F-16 requires classifying the intended student/use under a restriction | An eligible, scoped interpretation/approval resolves whether the restriction applies | warning | Project review policy; H1/H2 | Withdraw "no provider defines competing". A label such as internal, research or non-competing is not a completed assessment. Route unresolved interpretation to #40's policy owner |
| F-18 | OpenAI new fine-tuning job creation on a selected date/account/base | The account and base are eligible for new jobs on that date | error | R8; H2 accepted lifecycle input | Apply the May/July 2026 account gates and January 2027 new-job cutoff exactly. Unknown account history is unknown. Evaluate derived-model inference against its separate exact base shutdown |
| F-19 | Requested operation is tuning through the Gemini API or AI Studio | That selected service supports the requested operation on the selected date | error | L26 and H2; source-checked scoped negative | The recorded unsupported API path fails. Vertex is a candidate remediation needing its own selected-model, method, region, account and export checks, not an automatically valid replacement |
| F-20 | Requested Claude tuning through the selected Anthropic API or exact Bedrock model/region/date | That exact offering accepts the requested new job | error | M10/L30; H2; historical scoped negative | Do not promote a stale supported-model table over its applicable lifecycle exclusion. Do not extrapolate a Claude 3 Haiku region/date to every future Claude or Bedrock offering |
| F-21 | Selected Mistral/Cohere self-service tuning route; maintenance/lifecycle assessment | The selected route meets the chosen lifecycle suitability requirement | warning | M27/L33; H2 | Deprecation produces a suitability warning/failure under that policy, not an invented shutdown date. Actual job availability needs separate explicit evidence |
| F-22 | New build selects torchtune and requires maintained training tooling | The selected tool meets the maintained-tool requirement | warning | F29/F30; published maintenance notice | Known unmaintained tooling fails this suitability assertion; technical executability remains a separate question. Choose a maintained candidate or explicitly accept the maintenance risk through the consuming policy |
| F-23 | Any enabled training selection; exact model, trainer/adapter versions, objective, update/quantization, backend and distributed configuration | Eligible evidence supports that complete requested combination | error | R1–R4; explicit Axolotl MPS negative in R3; project evidence/completeness policy | Feature lists do not prove all combinations. Axolotl QLoRA on MPS fails on its explicit negative; an untested FSDP/backend combination is unknown. Obtain exact configuration support before sizing or execution |
| F-24 | Selected framework/component and use impose source/distribution/network obligations | The actual selected component's applicable license obligations are satisfied | warning | R7; source-checked component licenses, selected-use assessment proposal | Unsloth AGPL is not limited to Studio in the pinned source tree. Inspect the selected distribution/components and modification/distribution/remote-interaction facts; do not declare an entire wheel AGPL or compliant from a different commit's README |

### Synthetic passing, failing, unknown and non-applicable examples

These are **illustrative inputs**, not vendor experiments, user attestations, legal decisions or runtime fixtures. For every row, hold its applicability and binding facts true: an eligible affirmative answer to that row's assertion is `pass`; an eligible explicit contrary fact or unmet required obligation is `fail`; a missing necessary fact is `unknown`; a known-false row applicability condition is `skipped`. The row's severity remains unchanged in all four cases. The following concrete cases make the boundaries reviewable:

| Synthetic case | Expected research decision and why |
| --- | --- |
| Training capability absent; unrelated model has restrictive terms | F-01–F-24 skipped for the absent training selection; no unrelated model is substituted as a participant |
| Selected Apache-labeled base; license text is bound but the actual base distribution's NOTICE contents are missing | F-01 unknown/error and F-13 assessed independently; the label cannot establish notice compliance |
| Llama distribution conditions known; all required copy/attribution/notice artifacts present versus a known required artifact missing | F-02 pass/warning versus fail/warning; neither decides the separate F-05 name condition |
| Llama §2 applies and the threshold is exceeded; qualifying separate grant present versus explicitly absent | F-04 pass/error versus fail/error; missing grant information gives unknown/error |
| Documented CC BY-NC operation is assessed commercial; system is called a non-production prototype | F-10 fail/error under that grant; the prototype label cannot substitute for the NonCommercial predicate. Without the intended-use assessment it is unknown/error |
| Selected base has `weight_access: none`; requested trainer needs local base tensors | F-14 fail/error even if the framework and license otherwise permit the method |
| Together full fine-tuning job with required adapter export; exact job kind and requested `checkpoint=adapter` known | F-15 fail/error on R5. LoRA with an eligible adapter-download path can pass that capability assertion, while actual delivery and serving remain H4 checks |
| Anthropic D.4(a) express approval supplied; D.4(b) compliance unresolved | F-16 remains unknown/error for the unresolved applicable restriction; approval is not a blanket exception |
| OpenAI account history unknown on the recorded date; model family appears in a training guide | F-18 unknown/error; no eligibility is fabricated and the inference lifecycle remains separate |
| Axolotl selected with QLoRA and MPS; versus a fully evidenced eligible configuration; versus a merely unlisted pair | F-23 fail/error, pass/error and unknown/error respectively; list absence is only fail when the source is marked complete for that scope |
| Unsloth selected package's components uninspected; only the current repository's root license is known | F-24 unknown/warning. Complete eligible component/use evidence satisfying obligations can pass; an explicitly required unmet obligation fails, with the same severity |

**Migration and interactions:** these are changed research assertions, not a reinterpretation of historical saved results. A consuming implementation must pin a new adopted ruleset revision and preserve prior rule/version/evidence identities under #40/#42. Permission, access, technical capability, data rights, resource fit, artifact delivery and serving suitability remain distinct. The handoff packet below names each receiving owner and exact unresolved adoption boundary.

## Pricing and capacity

Not applicable to this issue. Managed-service price **units** are recorded above only so that #39 and #31 know the billing basis:
- per 1,000 or 1,000,000 training tokens, where training tokens = dataset tokens × epochs (M8, M14);
- per training hour for Foundry RFT;
- minimum charge per job (Together, Mistral);
- monthly storage per tuned model (Bedrock, Mistral).

No Pricebook proposal is made here. Priced scenarios belong to #31.

## Recommendation and rationale

These are **project decision proposals**, conditional on the selected facts; no comparative performance measurement was made.

- **User-operated reference stack:** start the comparison with a selected TRL trainer plus PEFT when an adapter is wanted. R1/R2 establish their documented roles and interfaces. Consider Axolotl for a configuration-driven workflow and Unsloth where the exact component/backend/configuration is qualified. Do not recommend PEFT alone as a standalone SFT/DPO trainer, assume every backend supports every update strategy, or infer that all selected Unsloth components have the root license. Keep the broader historical candidates in the comparison for their evidenced capabilities; do not declare a universal hardware winner.
- **Artifact portability:** prefer a documented path to the needed artifact kind when moving providers is a requirement. Compare Vertex open-model output, Together's job-specific download kinds, and Fireworks' adapter plus exact base requirements. Provider-hosted and unknown-export outcomes must be visible during selection. A format label, successful training job, adapter download or platform-side merge does not prove conversion, full-checkpoint delivery, rights or serving compatibility (R2–R6; M7–M17).
- **API customisation:** offer only a qualified service/account/model/method/date path. Unknown account eligibility stays unknown. Preserve eligible existing OpenAI new-job paths until their applicable cutoff and evaluate existing-model inference separately; a blanket January 2027 inference stop is withdrawn. Gemini API/AI Studio and Vertex have separate offerings. Retain the Mistral/Cohere deprecation warnings without inventing a Mistral shutdown or a current customer entitlement (R8; H2).
- **Permissions:** require a per-checkpoint, per-operation terms assessment and the selected framework/component's own conditions. Model/provider technical limitations, access grants, data rights and derivative obligations remain independent conditions. A favorable framework license is not permission to train a selected base or reuse a provider's outputs (H1/H2; R7/R9–R13).
- **Maintenance:** exclude known unmaintained tooling from the recommended new-build path unless the consuming policy explicitly accepts that risk. The documented torchtune notice supports the warning; it does not claim a broken runtime (F29/F30).

## Structured artifacts

CatalogItem proposals for the recommended self-hosted stack, validated with `scripts/validate_research.py`:

| File | ID | Version |
| --- | --- | --- |
| `catalog/proposals/training_framework-trl.json` | `cat.training_framework.trl` | 1.16.0 |
| `catalog/proposals/training_framework-peft.json` | `cat.training_framework.peft` | 0.21.2 |
| `catalog/proposals/training_framework-axolotl.json` | `cat.training_framework.axolotl` | 0.21.0 |
| `catalog/proposals/training_framework-unsloth.json` | `cat.training_framework.unsloth` | 2026.10.6 |

These four historical proposals retain their original bytes, version and `unverified` provenance. Their independent methods/backend/format arrays are coarse discovery facts, not assertions about every combination or every bundled component. In particular, the Unsloth source snapshot in R7 does not prove the contents of the selected 2026.10.6 wheel, and the Axolotl support document's development-line caveat remains. This record supplies the narrower evidence-admission requirements; it does not silently upgrade catalog versions, add fictional schema fields or attest to package qualification. Methods v1 cannot express remain in prose rather than invented enum values.

Not proposed yet:
- **Managed services:** `backends` is required and they have no user-visible backend; `tier`, `billing_class` and lifecycle `status` mapping also needs #40.
- **Other self-hosted frameworks:** historical output discoveries do not by themselves complete every selected-version catalog/provenance field; `torchtune` has the documented maintenance exclusion. No missing value is filled merely to produce a proposal.

## Open questions and handoffs

### Exact receiving packet

These handoffs cover every dependency in #30. H1/H2 preserve actual incoming receipts; H3–H5 require actual consuming review of this revision. A source author's self-reconciliation is not an independent review, and a receipt for a related dataset, cost or lifecycle note does not implicitly accept this complete framework packet. The user has delegated project engineering work in this session; any resulting technical receiving review must state that scope instead of impersonating a named contributor.

| ID / dependency | Exact input or output to receive | Evidence, status and boundary |
| --- | --- | --- |
| H1 · #6 → #30 | Model ID/version/revision, `/spec/access_modes`, `/spec/weight_access`, selected-model `/spec/supports_fine_tuning`, opaque `/spec/license_ref`, normalized exact terms and inheritance/attribution/NOTICE requirements | [Actual #6 input-sufficiency receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/30#issuecomment-6245639699) accepts the access/negative-support boundary and requires normalized terms; the per-distribution NOTICE evidence remains a selected-artifact requirement. [#110 terminology receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/30#issuecomment-6242700387) accepts training channels separately from serving modes. This revision receives those exact constraints and does not invent a license interpretation |
| H2 · #5 → #30 | Offering/account/region/date operation eligibility, exact base and derived-model lifecycle, service-specific agreement and exceptions | [Actual delegated #5 lifecycle receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/30#issuecomment-6251442684) pins source `d81f4cb` and retains May/July/January OpenAI job gates separately from exact base inference dates; Gemini API versus Vertex, Mistral deprecation, Cohere's recorded deprecation and Anthropic D.4(a)/(b) remain separately scoped. R8/R13 read back the corrected clauses; no caller entitlement is inferred |
| H3 · #30 → #32 | Exact trainer/loader and versions, objective and update strategy, required input fields, tokenizer/processor/chat-template revision, loss-mask/packing configuration and source scope | Proposed receiving decision: R1/R3 specify data-shape requirements; JSONL/Parquet alone proves no trainer compatibility. #32 owns preparation/transformation lineage and actual dataset rights/privacy/split decisions. Its existing [#32 → #33 receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/33#issuecomment-6251984559) remains separate and is not relabeled as this handoff. Exact-candidate receiving review pending |
| H4 · #30 → #33 | Artifact kind, training job/configuration, exact base/checkpoint and adapter revision, method-specific merge support, source components/terms, export/converter version/options and destination | Proposed receiving decision: R2/R4/R5/R6 distinguish adapter weights, raw output, merged checkpoint and provider-hosted results. Require actual integrity/lineage/export evidence and the selected base; converter documentation is not an executed tuple. #33 owns artifact governance and #11 separately owns serving support. The [ONNX boundary](onnx-export-boundary.md) remains a conditional route without reproduction. Exact-candidate receiving review pending |
| H5 · #30 → #31 | Exact trainer/adapter/backend/dependency versions, objective/update/quantization, distributed topology/strategy, precision, batch/accumulation, sequence/packing and loss configuration, source support/exclusions | Proposed receiving decision: R1/R3 support configuration requirements only. A framework's distributed boolean is not a placement/topology, memory, runtime or cost measurement. #31 owns estimator assumptions, hardware allocations and measured/planned resource quantities; the [accepted cost-unit handoff](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/39#issuecomment-6251932295) remains separate. Exact-candidate receiving review pending |
| H6 · #40 / #41 review relationship | Shared envelope, all F-01–F-24 assertions, fixed severity, unresolved evidence, selection roles, note-only inputs and migration | Proposed for independent central review; no ruleset adoption, new enum, runtime permission or provenance upgrade occurs here. Selected package/license qualification and policy implementation remain explicit follow-up decisions |

### Named follow-up decisions

| Question | Follow-up issue / owner |
| --- | --- |
| Add v1 enum values for `methods` (`grpo`, `ppo`, `kto`, `orpo`, `rft`, `preference_optimization`, `continued_pretraining`, `dora`) and fields for `input_data_formats`, `export_path`, `supported_model_refs` and per-method backend support | #40 · @tynamite |
| How should `backends` be represented for managed services where no backend is user-visible? | #40 · @tynamite |
| Normalize per-checkpoint exact license/agreement, technical support and scoped obligations; keep existing `/spec/access_modes`, `/spec/weight_access` and opaque `/spec/license_ref` semantics | #6 · @zwright8; #40 owns proposed fields |
| Preserve selected service/account/model/region/date availability and new-job versus inference lifecycle | #5 · @zwright8 |
| Revenue, MAU and residency are user attestations needed by F-03, F-04, F-07 and F-09. Where are they captured? | #2 / #3 · @tynamite |
| Resolve the selected agreement/use interpretation when "competing model" or another restriction remains ambiguous; record qualifying exceptions separately | #40 · @tynamite |
| Mistral Forge licensing and weight export: not stated publicly; sales-led | #30 · @appletechie |
| Exact model/base/adapter/converter/backend qualification for GGUF or ONNX; source routes documented, successful selected conversions not reproduced | #30 · @appletechie; consumed by #33 and #11 |
| Inspect the selected Unsloth package/component distribution and applicable obligations; current source R7 must not be treated as a wheel inventory | #30 · @appletechie; component license intake by #41 and policy by #40 |
| Input data formats per framework and service (see tables) | handoff to #32 · @appletechie |
| Output artifact formats and portability (adapter vs merged, provider-locked) | handoff to #33 · @appletechie; serving support by #11 · @Mattycodes69 |
| Distributed training capability and backend list for training sizing | handoff to #31 · @appletechie; accelerator catalog by #10 · @Mattycodes69 |
| Price units for managed training | handoff to #39 · @PUSHINGSQUARES |
| Evidence grading of the interim labels used here | #41 · @tynamite |

### Literal #30 acceptance audit

| Original criterion | Record supporting review | Completion gate |
| --- | --- | --- |
| Permission rules in the #40 format | Shared participant/evaluation envelope, F-01–F-24, examples and migration boundary | Independent central review of this candidate |
| Method × framework matrix with sources | Historical inventory plus R1–R7 selected-version/source corrections and explicit non-Cartesian support rule | Review factual scope and retained unknowns; no executed capability matrix is claimed |
| Decision record merged at the required path | This existing decision-record path | Ordinary reviewed merge and default-branch readback |
| API / managed / self-hosted coverage or rationale | Three training channels, all candidate tables and T0 serving-mode separation | Covered research scope; no runtime deployment claimed |
| Fields with type, unit and evidence requirement | Comparison fields and participant table | Note-only inputs remain outside frozen v1 |
| Shared-format rules/warnings; verified versus hypotheses | Fixed per-rule severity, four outcomes, source admission, explicit policy/assessment hypotheses | No independently reproduced claim is asserted |
| Primary sources, dates and applicable scope for factual/numeric claims | Dated F/M/L historical register, correction register R1–R13 and explicit published-number classification | Unrechecked historical cells remain historical; unsupported universal claims are withdrawn |
| Every Dependencies handoff confirmed by consuming owner | H1/H2 actual receipts and H3/H4/H5 exact outgoing packet | H3–H5 actual delegated consuming review still required; related receipts do not substitute |
| Named open-question owner | Follow-up table above | Preserves source/consumer ownership; implementation and selected-customer facts remain follow-up scope |

The issue remains open until the independent review, actual H3–H5 receiving decisions and reviewed merge are recorded. Research acceptance may retain owned, bounded selection/implementation questions; it cannot turn a missing source, customer grant or measurement into a passed compatibility result.
