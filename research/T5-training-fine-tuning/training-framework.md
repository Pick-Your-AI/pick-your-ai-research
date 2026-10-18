# T5: Training Framework

Issue: #30 · Contract: 1.0.0 · Kinds: `training_framework`
Status: ready for review · Last researched: 2026-10-16

## User decision

Can the selected model be customised, and with which method and tool?

The answer depends on three joint facts: the base model's license and weight access (#6), the provider's offering (#5), and the framework or service that implements the method. This note compares three training channels:

- **First-party training API:** model APIs (OpenAI, Gemini API, Anthropic, Mistral, Cohere). Customisation is hosted, and the artifact cannot leave the provider.
- **Managed training service:** cloud fine-tuning services (Vertex AI, Bedrock, Microsoft Foundry, Together, Fireworks). Some return downloadable weights or adapters.
- **User-operated training framework:** open frameworks run on user compute (TRL, PEFT, Axolotl, Unsloth, LLaMA-Factory, ms-swift, NVIDIA NeMo stack, torchtune).

These channel labels do not determine the serving deployment mode. T0's deployment mode (#3) decides the mode by who operates the *serving* runtime and on what capacity ([PR #81](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/81), merged), and that definition governs serving. A fine-tuned model's serving mode follows T0, not the channel used to train it. For example, a LoRA trained on Together, downloaded as an adapter and served with its matching base model on user-operated compute would be T0 "Self-hosted", even though its training channel above is a managed training service ([Together deployment documentation](https://docs.together.ai/docs/fine-tuning/deployment#run-locally), accessed 2026-10-17). T0 defines no mode for a training run; see K-08 in #31.

Compute sizing (#31) and dataset preparation (#32) are out of scope.

## Candidate options

### Self-hosted frameworks

| ID | Version (release date) | License | Methods (contract enum) | Other documented methods | Backends (contract enum) | Output formats | Distributed | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `trl` | 1.16.0 (2026-10-15) | Apache-2.0 | sft, dpo, distillation; lora/qlora via PEFT | GRPO, KTO, reward modelling, RLOO; experimental CPO, GKD, online DPO, ORPO | cuda (implied), other (AWS Trainium) | HF checkpoints, PEFT adapters | yes (DDP, DeepSpeed, FSDP, multi-node) | F1–F4 |
| `peft` | 0.21.2 (2026-10-01) | Apache-2.0 | lora, qlora | DoRA, AdaLoRA, IA3, LoHa, LoKr, OFT/BOFT, VeRA, prompt/prefix tuning | cuda (implied), tpu, metal, cpu | safetensors (default), pytorch; merged weights via `merge_and_unload()` | yes (DeepSpeed, FSDP) | F5–F7 |
| `axolotl` | 0.21.0 (2026-10-16) | Apache-2.0 | sft, lora, qlora, full_finetune, dpo, distillation | continued pretraining, IPO, ORPO, SimPO/CPO, KTO, GRPO, reward models, QAT | cuda, rocm, metal (partial: no QLoRA or DeepSpeed on MPS), other (Ascend NPU, no parity) | safetensors (merged), gguf (`axolotl export`, merge first) | yes (FSDP/FSDP2, DeepSpeed, multi-node, TP/CP/EP) | F8–F13 |
| `unsloth` | PyPI 2026.10.6 (2026-10-15) | Apache-2.0 core; AGPL-3.0 optional components (Studio UI) | sft, lora, qlora, full_finetune, dpo | pretraining, GRPO, GSPO, FP8 training | cuda, rocm, oneapi, metal (MLX); cpu for data recipes only, not training | LoRA adapters, merged 16-bit safetensors, gguf, NVFP4/FP8 | multi-GPU and DeepSpeed ZeRO-2/3; multi-node unknown | F14–F17 |
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
| `together-fine-tuning` | active | sft, lora (default), full_finetune, dpo | GRPO (separate product) | DeepSeek V3.1/V4 Flash, GLM 5.x, Qwen 3.5–3.8, Kimi K2.x, Gemma 4, gpt-oss, Llama 3.x/4, Mixtral 8x7B | JSONL (conversational, instruction, preference, generic text) or tokenised Parquet; 100 GB file limit | **portable**: `checkpoint=merged` or `adapter` download | per 1M tokens, with a minimum charge per job | M18–M22 |
| `fireworks-fine-tuning` | active | sft, lora (rank ≤32, power of 2), dpo, full_finetune (Training API) | ORPO, RL (Training API), vision SFT | most of the catalog for managed LoRA; full-parameter for DeepSeek V4, GLM 5.x, Kimi K3, Qwen3.x, Gemma 4 | OpenAI-compatible chat JSONL, 3 to 3M examples | **portable** for LoRA (`firectl model download`, needs the matching base model); full-weight download unknown | per 1M training tokens, tiered by model size and method | M23–M26 |
| `openai-fine-tuning` | **winding down** | sft, dpo | RFT (o4-mini), vision fine-tuning (gpt-4o) | gpt-4.1, gpt-4.1-mini, gpt-4.1-nano | chat JSONL `messages`, minimum 10 examples | **provider-locked**; inference continues until the base model is deprecated | not extracted (page is rendered in JavaScript) | M1–M4 |
| `mistral-fine-tuning-api` | **deprecated** | sft | Classifier Factory | open-mistral-7b, mistral-small, codestral, nemo, mistral-large, ministral-8b/3b, pixtral-12b | JSONL `messages` | unknown | $4 minimum per job plus $2/month storage per model; token unit unknown | M27–M29 |

**OpenAI wind-down dates (M2):**
- 2026-05-07: organisations that never ran fine-tuning can no longer create jobs.
- 2026-07-02: organisations without fine-tuned inference in the last 60 days can no longer create jobs.
- 2027-01-06: job creation ends for all customers.

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
| `/version` | string, upstream release tag | e.g. `trl` 1.16.0 | F1 | Releases move weekly for trl and unsloth; record the release date |
| `/license` | SPDX identifier where one exists | Apache-2.0, BSD-3-Clause; Unsloth is dual | F2, F14 | Framework license ≠ base-model license; both must be checked |
| `/spec/methods` | array of enum `sft, lora, qlora, dpo, full_finetune, distillation`, min 1 | see the candidate tables | per row | v1 cannot express GRPO, PPO, KTO, ORPO, RFT, continued pretraining, preference optimisation or DoRA |
| `/spec/backends` | array of enum `cuda, rocm, oneapi, metal, tpu, cpu, other`, min 1 | see the candidate tables | per row | Managed services have no user-visible backend. `other` hides Trainium and Ascend. Support levels differ by method |
| `/spec/model_formats` | array of enum `safetensors, gguf, onnx, pytorch, api_only, other` | managed locked services = `api_only` | per row | Native ONNX output was not confirmed for any candidate; a [conditional downstream conversion route](onnx-export-boundary.md) is documented separately, without an executed tuple. Native GGUF export only in axolotl and unsloth; PEFT LoRA adapters from any framework convert with llama.cpp `convert_lora_to_gguf.py` (F34) |
| `/spec/distributed_supported` | boolean | true for all self-hosted candidates; not applicable to managed | per row | The boolean cannot distinguish multi-GPU from multi-node (Unsloth multi-node is unknown) |
| `supported models` (note only) | list of model catalog IDs (→ #6) | summarised per service | per row | Changes often; must be date-stamped |
| `input data format` (note only) | enum proposal: `chat_messages_jsonl`, `prompt_completion_jsonl`, `preference_jsonl`, `alpaca`, `sharegpt`, `raw_text`, `tokenized_parquet` | see tables | per row | Handed to #32 |
| `export path` (note only) | enum proposal: `none`, `adapter_download`, `merged_download`, `object_storage` | Vertex open = `object_storage`; Together and Fireworks = `adapter_download`/`merged_download`; Bedrock, Foundry (OpenAI models), OpenAI = `none` | M7, M22, M25 | Handed to #33 |
| `status` (lifecycle) | contract `/status` | torchtune, openai-fine-tuning and mistral-fine-tuning-api should not be `active` | F29, M2, M27 | Mapping to the contract status enum needs review by #40 |

## Evidence

All entries accessed on 2026-10-16. Grades follow the interim policy in `docs/RESEARCH_METHOD.md` until #41 finalises it. Version and release dates come from the GitHub Releases API, the PyPI JSON API and the license files fetched on that date.

Claims whose cited primary text was retrieved were source checked on the recorded access date; the limitations below remain unconfirmed. None of these claims is independently verified. The four CatalogItem proposals therefore carry `verification_status: unverified` for every provenance entry.

The fetch work was split across three parallel research passes. Claims not retrieved directly from the page are marked in the Limitations column.

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
| F14 | Unsloth, https://github.com/unslothai/unsloth/blob/main/README.md | 2026-10-16 | main | Primary documentation | Dual license; check which components a build uses |
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
| L5 | Google, https://ai.google.dev/gemma/terms | 2026-10-16 | Gemma Terms of Use, modified 2026-04-01 | Primary documentation | Applies to Gemma ≤3 |
| L6 | Google, https://ai.google.dev/gemma/prohibited_use_policy | 2026-10-16 | 2024-02-21 | Primary documentation | Binds Gemma 1–3n through Terms §3.2. It does not bind Gemma 4: the Terms say "For Gemma 4 terms, see the Gemma 4 license", which is plain Apache-2.0 (L5, L7) |
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

## Compatibility proposals

These rules are proposed for review by #40 using the [rule proposal template](../../templates/rule-proposal.md). Each is written against `training_framework` × `model` (#6) × `model_provider` (#5).

- **Source checked** means the cited primary text was read on its access date and supports the assertion. This follows the interim "checked" definition in the owner's adopted #41 policy ([#75 review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75#pullrequestreview-5550616927)). A rule may pass on source-checked evidence, and its result carries "unverified".
- **Verified** is not claimed for any rule here. It would mean independently reproduced (a second source or a reproducible test). No such evidence exists yet.
- **Hypothesis** means the assertion needs a definition, a re-fetch, or a contract field that does not exist yet.

When a required license or method fact is missing, the outcome is `unknown` with severity `warning`. The rule must not default to pass.

### Permission rules (model license → allowed methods)

| Rule | Participating fields | Assertion | Outcome / severity | Evidence | Status |
| --- | --- | --- | --- | --- | --- |
| F-01 | `model.license`, `training_framework.spec.methods` | License ∈ {Apache-2.0, MIT, OpenMDW-1.1} permits every method; redistribution keeps the license and notices | pass / info | L4, L7, L14–L18, L20, L21 | source checked |
| F-02 | `model.license`, selection distributes a derivative | Llama 4 Community License: a distributed derivative must show "Built with Llama" and its name must begin with "Llama" | pass / warning | L1 §1.b.i | source checked |
| F-03 | `model.license`, user residency, `model` modality | Llama 4 multimodal model and an EU-domiciled licensee: the license grant does not apply (end users are exempt) | fail / error | L2 | source checked; residency field needed from #2/#3 |
| F-04 | `model.license`, organisation MAU | Llama 4 and over 700M MAU on the release date: a separate Meta license is required | fail / error | L1 §2 | source checked; MAU is a user attestation, not a catalog fact |
| F-05 | teacher `model.license`, `methods` contains `distillation` | Llama teacher and a distributed student: the student must carry the "Llama" name prefix | pass / warning | L1 §1.b.i | source checked |
| F-06 | `model.license` = Muse Model License | Every method allowed; the derivative carries "Built with Muse Spark Open" and the Usage Policy | pass / warning | L3 | source checked |
| F-07 | `model.license` ∈ {Muse, Qwen3.8-Max, Kimi K3}, Model-as-a-Service use, revenue | Serving as a Model as a Service above the stated revenue threshold ($20M / $50M / $20M in 12 months) needs a separate agreement | fail / error | L3, L13, L19 | source checked; revenue is a user attestation |
| F-08 | `model.license` = Gemma Terms (Gemma ≤3), `distillation` | A distilled student is a Model Derivative and inherits the Gemma Terms and Prohibited Use Policy | pass / warning | L5 §1.1(e), §3.1 | source checked |
| F-09 | `model.license` = Mistral Modified MIT, organisation revenue | Company monthly revenue over $20M: no rights to the model or its derivatives | fail / error | L9, L10 §2 | source checked |
| F-10 | `model.license` ∈ {MNPL-0.1, CC-BY-NC-4.0}, production deployment | Fine-tuning is allowed for non-production or non-commercial use only | fail / error when production | L11, L22 | source checked |
| F-11 | `model.license` = Qwen Community License 1.0, commercial MaaS or assistant use | Commercial Model-as-a-Service or "AI Work Assistant" use requires a separate license, with no revenue floor | fail / error | L12 §2 | source checked |
| F-12 | `model.license` = GLM-5.3 License, MaaS revenue over $10B | Z.AI security review is required | unknown / warning | L20 §2 | source checked |
| F-13 | `model.license` = null or unrecognised | No permission determination is possible | unknown / warning | — | policy proposal |

### Provider and access rules

| Rule | Participating fields | Assertion | Outcome / severity | Evidence | Status |
| --- | --- | --- | --- | --- | --- |
| F-14 | `model.weights_available` = false (API-only), self-hosted framework selected | A self-hosted framework cannot customise an API-only model | fail / error | L24, L25, L34 | source checked; the weight-access field name depends on #6 |
| F-15 | API-only base model, required artifact = downloadable weights | Customised API models are hosted only; no weights are retrievable | fail / error | L24, L34, M13 | source checked |
| F-16 | teacher = OpenAI / Gemini / Anthropic / Cohere API, `distillation` or synthetic-data training, student competes with provider | Provider terms prohibit using outputs to train competing models. OpenAI API exception: fine-tuning OpenAI's own models, and classifiers/embeddings that are not distributed (L35) | fail / error (pass / info when the OpenAI exception applies) | L23, L35, L24, L25 D.4, L34 | source-checked clauses; "competing" remains undefined (see F-17) |
| F-17 | same as F-16 with a student that is not clearly competing | No provider defines "competing" | unknown / warning | L23–L25, L34, L35 | hypothesis: needs a policy decision, not more evidence |
| F-18 | provider = OpenAI, organisation fine-tuning history, date | New or inactive organisations are blocked now; everyone is blocked from 2027-01-06 | fail / error | M2 | source checked; date-dependent, so it must be re-evaluated against the catalog snapshot date |
| F-19 | provider = Gemini API or AI Studio, any tuning method | Not available; route to Vertex for the listed Gemini models | fail / error, with remediation "Vertex" | L26, M5 | source checked |
| F-20 | provider = Anthropic API or Bedrock, any tuning method on a Claude model | Not available on Anthropic's API. On Bedrock, the only listed Claude model (Claude 3 Haiku) is end-of-life, and Legacy models accept no new fine-tuning jobs | fail / error | L25, L30, M10 | source checked |
| F-21 | provider ∈ {Mistral API, Cohere}, self-serve tuning | Deprecated | fail / warning | M27, L33 | source checked |
| F-22 | framework = torchtune | Not maintained since 2025 | pass / warning (deprecated) | F29, F30 | source checked |
| F-23 | framework method/backend pair | A method is supported only on the backends the framework documents for it (e.g. Axolotl QLoRA unavailable on `metal`) | fail / error | F13 | source checked for Axolotl; v1 cannot express per-method backend support |
| F-24 | framework license = AGPL-3.0 component used in a hosted product | Network-use source obligations apply (Unsloth Studio only) | pass / warning | F14 | hypothesis: the scope of the AGPL components needs confirming |

## Pricing and capacity

Not applicable to this issue. Managed-service price **units** are recorded above only so that #39 and #31 know the billing basis:
- per 1,000 or 1,000,000 training tokens, where training tokens = dataset tokens × epochs (M8, M14);
- per training hour for Foundry RFT;
- minimum charge per job (Together, Mistral);
- monthly storage per tuned model (Bedrock, Mistral).

No Pricebook proposal is made here. Priced scenarios belong to #31.

## Recommendation and rationale

- **Self-hosted default:** recommend `trl` + `peft` as the reference stack, with `axolotl` and `unsloth` as config-driven alternatives.
  - All four are Apache-2.0 at the core and actively released (last release within 16 days).
  - Each covers sft, lora, qlora and dpo.
  - Only Axolotl and Unsloth export GGUF natively, which matters for #11 and #33. TRL documents GGUF only through Unsloth (F35); PEFT, LLaMA-Factory, ms-swift and the NeMo repos have none (F36–F38). A PEFT LoRA adapter from any of them can be converted with llama.cpp `convert_lora_to_gguf.py` (F34).
  - Treat `ms-swift` as a strong alternative with the broadest documented hardware coverage. Treat the NVIDIA NeMo stack as CUDA-only, multi-node-first.
  - Do not recommend torchtune for new builds.
- **Managed default:** prefer services that return a portable artifact when the user may later move off the provider: Vertex open-model tuning, Together, and Fireworks (LoRA).
  - Bedrock, Foundry (OpenAI models) and Vertex Gemini tuning yield provider-locked models. The builder must show this before selection.
- **API-only builds:** treat first-party API fine-tuning as unavailable by default. The builder should not offer OpenAI, Gemini API, Anthropic, Mistral or Cohere self-serve tuning as a path. Route Gemini to Vertex. Mark OpenAI as closing on 2027-01-06.
- **Licensing:** license checks must be done per checkpoint, not per model family. Qwen 3.8, Mistral, Meta, Gemma and Cohere each ship mixed licenses across checkpoints (L3–L14, L22). This should be a #6 catalog requirement.

## Structured artifacts

CatalogItem proposals for the recommended self-hosted stack, validated with `scripts/validate_research.py`:

| File | ID | Version |
| --- | --- | --- |
| `catalog/proposals/training_framework-trl.json` | `cat.training_framework.trl` | 1.16.0 |
| `catalog/proposals/training_framework-peft.json` | `cat.training_framework.peft` | 0.21.2 |
| `catalog/proposals/training_framework-axolotl.json` | `cat.training_framework.axolotl` | 0.21.0 |
| `catalog/proposals/training_framework-unsloth.json` | `cat.training_framework.unsloth` | 2026.10.6 |

Each entry lists only methods, backends and formats documented in its provenance sources. Methods that v1 cannot express (GRPO, KTO, ORPO, RFT, continued pretraining) are named in `description` rather than invented as enum values.

Not proposed yet:
- **Managed services:** `backends` is required and they have no user-visible backend; `tier`, `billing_class` and lifecycle `status` mapping also needs #40.
- **Other self-hosted frameworks:** `llamafactory`, `ms-swift` and the NeMo repos have unconfirmed output formats; `torchtune` would be `deprecated`.

## Open questions and handoffs

| Question | Follow-up issue / owner |
| --- | --- |
| Add v1 enum values for `methods` (`grpo`, `ppo`, `kto`, `orpo`, `rft`, `preference_optimization`, `continued_pretraining`, `dora`) and fields for `input_data_formats`, `export_path`, `supported_model_refs` and per-method backend support | #40 · @tynamite |
| How should `backends` be represented for managed services where no backend is user-visible? | #40 · @tynamite |
| #6 must carry per-checkpoint `license`, `weights_available` (gated / open / API-only), and the attribution or naming obligations used by F-01 to F-13 | #6 · @zwright8 |
| #5 must carry managed fine-tuning availability and lifecycle dates (OpenAI 2027-01-06; Mistral and Cohere deprecated; Gemini API not tunable) | #5 · @zwright8 |
| Revenue, MAU and residency are user attestations needed by F-03, F-04, F-07 and F-09. Where are they captured? | #2 / #3 · @tynamite |
| Policy for "competing model" (F-17): no provider defines it | #40 · @tynamite |
| Mistral Forge licensing and weight export: not stated publicly; sales-led | #30 · @appletechie |
| Native ONNX support and exact conversion tuple; [downstream route documented](onnx-export-boundary.md), not reproduced (GGUF is resolved: F34–F38) | #30 · @appletechie; consumed by #33 and #11 |
| Input data formats per framework and service (see tables) | handoff to #32 · @appletechie |
| Output artifact formats and portability (adapter vs merged, provider-locked) | handoff to #33 · @appletechie; serving support by #11 · @Mattycodes69 |
| Distributed training capability and backend list for training sizing | handoff to #31 · @appletechie; accelerator catalog by #10 · @Mattycodes69 |
| Price units for managed training | handoff to #39 · @PUSHINGSQUARES |
| Evidence grading of the interim labels used here | #41 · @tynamite |

None of the handoffs above is confirmed yet.
