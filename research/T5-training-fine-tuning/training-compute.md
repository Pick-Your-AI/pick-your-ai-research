# T5: Training Compute

Issue: #31 · Contract: 1.0.0 · Kinds: `training_compute`
Status: draft · Last researched: 2026-10-16

## User decision

What compute, time, storage and cost does a training run need?

This covers three things:
- memory and time estimates per training method (full fine-tuning, LoRA, QLoRA, DPO, GRPO, distillation);
- storage and distributed-training needs;
- managed per-token training prices vs self-run GPU-hours.

Deployment modes:
- **API / managed:** cost is per training token plus post-training hosting or storage. The user sizes no hardware.
- **Self-hosted:** the user picks accelerators (#10) on a host (#9). The builder must estimate whether the run fits in memory and how long it takes.

Inference GPU sizing is owned by #10, and cost aggregation by #39.

## Candidate options

The decision is between a **managed per-token service** and a **self-run compute profile**. The estimation method below lets the builder compare them on the same dataset.

### Estimation method

**Inputs:**
- model catalog (#6): N total params, layers L, hidden size h, heads a, KV dimension, FFN size, vocabulary V;
- accelerator catalog (#10): VRAM, bf16/fp8 support, peak dense TFLOP/s, count G;
- user settings: sequence length s, micro-batch b, LoRA rank r and target modules, epochs E, dataset tokens D, gradient checkpointing, optimiser, ZeRO stage.

All formulas are bytes per GPU unless stated. Each term is tagged with its evidence; anything tagged **estimate** is this project's derivation.

| Term | Formula | Evidence | Grade |
| --- | --- | --- | --- |
| Full FT, AdamW mixed precision | 16·N bytes (bf16 weights + bf16 grads + fp32 master + 2 fp32 Adam states). The HF accounting with fp32 gradients gives 18·N | E1 §3.1; E2 | Primary documentation; parameterise the gradient dtype |
| Full FT, 8-bit Adam | Adam states drop from 8 to 2 bytes/param: 10·N (ZeRO accounting) or 12·N (HF accounting). The 6·N figure holds only for pure-bf16 training with no master copy | E3 §2 | Primary documentation |
| LoRA, bf16 base | 2·N + 16·N_lora, where N_lora = Σ_layers Σ_targets r·(d_in + d_out) | E4 §4.2 | Primary documentation (component accounting is an estimate) |
| QLoRA (NF4 + double quant) | ≈0.55–0.75·N + 16·N_lora. Double quant costs 0.127 bits/param of constants; the paper's 7B base used 5,048 MB, i.e. ≈0.75 bytes/param | E5 | Primary documentation |
| Activations | No checkpointing: L·s·b·h·(34 + 5·a·s/h) (16-bit, GPT-style block). FlashAttention removes the 5·a·s/h term. Full checkpointing: 2·s·b·h·L | E6 Eq. 1 | Primary documentation; the constant 34 is approximate for SwiGLU / no-dropout models (estimate) |
| Logits | k·4·s·b·V with k ≈ 2–3 for loss and gradient; k ≈ 0 with fused or chunked cross-entropy (Cut Cross-Entropy, Liger) | E6 §4.1; E7; E8 | Primary documentation (k from E7's figures, estimate) |
| DPO | SFT terms × 2 sequences (chosen + rejected), plus a reference model: +2·N for full FT, 0 with PEFT or precomputed log-probs | E17 | Primary documentation |
| GRPO / RL | Policy as SFT, plus rollout KV cache, plus logits × number of generations (`2·2·generations·s·V` bytes in bf16 per E9) | E9 | Vendor claim (Unsloth) |
| Distillation | Student as SFT, plus teacher weights (inference only), plus teacher logits (2–4·s·b·V) | — | Estimate |
| ZeRO data parallel (Nd GPUs) | stage 1: 4·N + 12·N/Nd; stage 2: 2·N + 14·N/Nd; stage 3: 16·N/Nd. The DeepSpeed estimator is more conservative: ZeRO-3 = 4·largest_layer + 18·N/Nd | E10 Table 1; E11 | Primary documentation |
| Runtime overhead | +10–20% for CUDA context and fragmentation | — | Estimate; no source fixes it |
| Training FLOPs | Full FT: 6·N per token (+ attention 12·L·a·d_head·s). Full gradient checkpointing adds 2·N hardware FLOPs | E12, E13, E14 App. B | Primary documentation |
| LoRA / QLoRA FLOPs | ≈4·N per token: no weight gradients for frozen parameters. LoRA reports 25% higher throughput (43.1 vs 32.5 tokens/s per V100) | E4 §4.2, fn. 5; E14 | **Estimate**: no primary source states 4·N |
| Time | T = FLOPs/token × D × E / (G × peak × MFU). Default MFU 0.35–0.45 on dense multi-GPU H100/A100 (PaLM 46.2%; Megatron 54.2% at scale); 0.2–0.35 on consumer GPUs. Prefer measured tokens/s from the benchmark table | E14; E6 | Primary documentation (consumer range is an estimate) |
| Training tokens billed | dataset tokens × epochs (Together, Fireworks, Vertex, Bedrock); Together also bills validation tokens × evaluations; Fireworks multi-turn reasoning traces × (average turns / 2) | P1, P2, P3, P4 | Primary documentation |
| Storage | Full checkpoint: 2·N weights + optimiser state if resumable (12·N, or 4·N with 8-bit), × checkpoints kept. LoRA adapter: 2·N_lora (bf16). The LoRA paper reports GPT-3 175B 350 GB → 35 MB at r=4 on q and v | E4; E15; E16 | Primary documentation |

`accelerate estimate-memory` (E18) covers weights only, for batch size 1. It reports "Training using Adam" as roughly 4× model size and excludes activations and logits, so it is a lower bound, not a fit test.

### Worked memory example: Qwen3-8B

Model config (E19): N = 8,190,735,360; h = 4096; L = 36; 32 heads; 8 KV heads; head_dim 128; FFN 12,288; V = 151,936.

LoRA at r = 16 on all linear layers gives N_lora = 1,212,416 per layer × 36 = **43,646,976**.

| Setup | Static memory (GB) | Notes |
| --- | --- | --- |
| Full FT, AdamW (16 B/param) | 131.1 | Does not fit one 80 GB GPU without ZeRO or offload; 147.4 GB with fp32 grads |
| Full FT, 8-bit Adam | 81.9–98.3 | Still above 80 GB |
| LoRA, bf16 base | 16.4 + 0.7 | Plus activations and logits |
| QLoRA | 4.5–6.1 + 0.7 | Plus activations and logits |
| Logits, s = 4096, b = 1, fp32 | 2.5 raw; 5.0–7.5 with loss and gradient | ≈0 with fused cross-entropy |
| Activations, full checkpointing, s = 4096, b = 1 | 1.2 | 2·s·b·h·L |

QLoRA on Qwen3-8B at s = 4096 is therefore ≈ 6–8 GB with fused cross-entropy, or ≈ 11–15 GB without. The difference is the logits term. The builder must ask whether a fused-loss framework is selected (#30: Unsloth, Liger-enabled TRL, torchtune chunked cross-entropy).

These are estimates and must be calibrated against the measured rows below.

### Published measurements

| ID | Source | Grade | Conditions | Result |
| --- | --- | --- | --- | --- |
| B1 | torchtune README | Primary documentation (PyTorch) | Llama 3.1 8B full FT, 1× RTX 4090, bs 2, packed 2048, `torch.compile` | 18.9 GiB, 1,650 tok/s. Recipe settings not stated; below the 16 B/param floor, so it relies on optimiser and offload tricks |
| B2 | torchtune README | Primary documentation | Same, LoRA, 1× RTX 4090 | 16.2 GiB, 3,083 tok/s |
| B3 | torchtune README | Primary documentation | Same, QLoRA, 1× RTX 4090 | 7.4 GiB, 2,413 tok/s |
| B4 | torchtune README | Primary documentation | Llama 3.2 3B, A100, bs 2, s 4096, bf16, compile, chunked cross-entropy, activation checkpointing and offload, 8-bit AdamW | full FT 17.6 GiB; LoRA 8.5 GiB; QLoRA 4.6 GiB |
| B5 | QLoRA paper Fig. 6 | Independent measurement | bs 1, s 512, gradient checkpointing | 7B 6.9 GB; 13B 11.3 GB; 33B 24.7 GB; 65B 45.0 GB. 65B Guanaco: 24 h on one 48 GB GPU |
| B6 | NeMo 25.04 performance summary | Vendor claim (NVIDIA) | Llama3-8B SFT, 8× H100, FP8, SQuAD packed 4096, global batch 32 | 16,222 tok/s/GPU, 733 TFLOP/s/GPU |
| B7 | NeMo 25.04 | Vendor claim | Llama3-70B SFT, 32× H100, TP4/PP4 | 1,619 tok/s/GPU |
| B8 | NeMo 25.04 | Vendor claim | Llama3-70B LoRA, 8× H100 | 2,621 tok/s/GPU, 730 TFLOP/s/GPU |
| B9 | Unsloth benchmarks | Vendor claim | Llama 3.1 8B QLoRA r = 32, all linear layers, bs 1 | Max context: 78,475 tokens on 24 GB (HF + FA2: 5,789); 342,733 on 80 GB |
| B10 | Unsloth RL guide | Vendor claim | Llama 3.1 8B GRPO, 20K context, 8 generations | 54.3 GB vs 510.8 GB "standard"; GRPO logits 9.8 vs 78.3 GB |
| B11 | Liger Kernel paper | Independent measurement (LinkedIn) | Llama 3-8B, 4× A100-80G, bf16, AdamW, s 512, bs 64 | +42.8% throughput, −54.8% memory |
| B12 | Answer.AI FSDP + QLoRA | Vendor claim | 70B on 2× 24 GB (RTX 3090) | Capability only; no sequence length, memory or time published |

## Comparison fields

These cover the CatalogItem envelope plus `spec_training_compute`. The issue's conceptual fields map as follows:
- `accelerator (→ #10)` → `compute_profile_ref` → `compute_profile.spec.accelerator_ref`
- `storage` → `storage_ref`
- `time estimate` → `max_gpu_hours` and ResourceEstimate `training.estimated_gpu_hours`
- `method`, `model size`, `memory estimate`, `price basis`, `assumptions` and `measured vs estimated` have no v1 catalog field and live in ResourceEstimate or this note.

| Field / JSON pointer | Type and unit | Candidate finding | Evidence ID | Conditions / unknowns |
| --- | --- | --- | --- | --- |
| `/spec/compute_profile_ref` | `compute_profile` catalog ID | Must reference a compute SKU already in the catalog (T2) | contract | No T2 compute profiles exist yet (#9, #10) |
| `/spec/max_gpu_hours` | number ≥0, GPU-hours | Cap from the time estimate | E14 | Managed per-token services have no GPU-hour meter |
| `/spec/ephemeral` | boolean | True for rented capacity released after the run | — | — |
| `/spec/storage_ref` | `storage` catalog ID | Checkpoint store | E15, E16 | Size from the storage formula |
| ResourceEstimate `training.estimated_gpu_hours` | decimal, `gpu_hour`; confidence `verified/calibrated/estimated/unverified` | The time formula, `confidence = estimated` unless calibrated against B1–B11 | E14 | The v1 estimate metric enum has no training-memory metric |
| `method` (note only) | enum shared with #30 | sft, lora, qlora, dpo, full_finetune, distillation + GRPO/RL | #30 | v1 method enum gap, raised in #30 |
| `memory estimate` (note only) | GB per device, with a breakdown | Formula above | E1–E11 | Proposal: add `training.estimated_peak_per_device_vram_gb` to ResourceEstimate |
| `price basis` (note only) | enum proposal: `per_training_token_1m`, `per_training_token_1k`, `gpu_hour`, `training_hour`, `job_minimum`, `model_storage_month`, `hosting_hour` | see pricing tables | P1–P11 | Pricebook meter enum lacks training-token and job-minimum meters |
| `measured vs estimated` | ResourceEstimate `confidence` | — | — | — |

## Evidence

All entries accessed on 2026-10-16. Grades follow the interim policy in `docs/RESEARCH_METHOD.md` until #41 finalises it. Prices are in USD; the region is given where the provider states it.

### Estimation (E)

| ID | Publisher and URL | Access date | Version / region | Evidence grade | Limitations / reuse terms |
| --- | --- | --- | --- | --- | --- |
| E1 | Rajbhandari et al., ZeRO, https://arxiv.org/abs/1910.02054 | 2026-10-16 | — | Primary documentation | Assumes fp16/bf16 gradients |
| E2 | Hugging Face, https://huggingface.co/docs/transformers/main/en/model_memory_anatomy | 2026-10-16 | main | Primary documentation | Assumes fp32 gradients (18 B/param) |
| E3 | Dettmers et al., 8-bit optimizers, https://arxiv.org/abs/2110.02861 | 2026-10-16 | — | Primary documentation | — |
| E4 | Hu et al., LoRA, https://arxiv.org/abs/2106.09685 | 2026-10-16 | — | Primary documentation | GPT-3 figures |
| E5 | Dettmers et al., QLoRA, https://arxiv.org/abs/2305.14314 | 2026-10-16 | — | Primary documentation | — |
| E6 | Korthikanti et al., https://arxiv.org/abs/2205.05198 | 2026-10-16 | — | Primary documentation | GPT-style block |
| E7 | Wijmans et al., Cut Cross-Entropy, https://arxiv.org/abs/2411.09009 | 2026-10-16 | — | Independent measurement | Gemma 2 2B |
| E8 | Hsu et al., Liger Kernel, https://arxiv.org/abs/2410.10989 | 2026-10-16 | — | Independent measurement | — |
| E9 | Unsloth, https://unsloth.ai/docs/get-started/reinforcement-learning-rl-guide | 2026-10-16 | — | Vendor claim | The unsloth.ai/blog/grpo page returned 403 |
| E10 | ZeRO paper §5, Table 1 (E1) | 2026-10-16 | — | Primary documentation | — |
| E11 | DeepSpeed, https://deepspeed.readthedocs.io/en/latest/memory.html | 2026-10-16 | — | Primary documentation | — |
| E12 | Kaplan et al., https://arxiv.org/abs/2001.08361 | 2026-10-16 | — | Primary documentation | Non-embedding parameters |
| E13 | Hoffmann et al., Chinchilla, https://arxiv.org/abs/2203.15556 | 2026-10-16 | — | Primary documentation | — |
| E14 | Chowdhery et al., PaLM, https://arxiv.org/abs/2204.02311 (App. B) | 2026-10-16 | — | Primary documentation | MFU values are for pretraining at scale |
| E15 | Hugging Face PEFT, https://huggingface.co/docs/peft/main/en/developer_guides/checkpoint | 2026-10-16 | main | Primary documentation | — |
| E16 | Hugging Face, https://huggingface.co/docs/transformers/main/en/main_classes/trainer (`save_only_model`) | 2026-10-16 | main | Primary documentation | — |
| E17 | Hugging Face TRL, https://huggingface.co/docs/trl/main/en/dpo_trainer | 2026-10-16 | main | Primary documentation | — |
| E18 | Hugging Face Accelerate, https://huggingface.co/docs/accelerate/main/en/usage_guides/model_size_estimator ; https://github.com/huggingface/accelerate/blob/main/src/accelerate/commands/estimate.py | 2026-10-16 | main | Primary documentation | — |
| E19 | Qwen, https://huggingface.co/Qwen/Qwen3-8B/raw/main/config.json | 2026-10-16 | revision b968826d | Primary documentation | — |

### Benchmarks (B-source)

| ID | Publisher and URL | Access date | Version / region | Evidence grade | Limitations / reuse terms |
| --- | --- | --- | --- | --- | --- |
| BS1 | PyTorch, https://github.com/meta-pytorch/torchtune/blob/main/README.md | 2026-10-16 | v0.6.1 (unmaintained, see #30) | Primary documentation | Recipe settings for B1 not stated |
| BS2 | NVIDIA, https://docs.nvidia.com/nemo-framework/user-guide/25.04/performance/performance_summary.html | 2026-10-16 | NeMo 25.04 | Vendor claim | FP8; older release than the current NeMo split |
| BS3 | Unsloth, https://unsloth.ai/docs/basics/unsloth-benchmarks | 2026-10-16 | — | Vendor claim | — |
| BS4 | Answer.AI, https://www.answer.ai/posts/2024-03-06-fsdp-qlora.html | 2026-10-16 | 2024-03-06 | Vendor claim | Alpha release; no measurements |

### Pricing (P)

| ID | Publisher and URL | Access date | Version / region | Evidence grade | Limitations / reuse terms |
| --- | --- | --- | --- | --- | --- |
| P1 | Together AI, https://www.together.ai/pricing | 2026-10-16 | USD | Primary documentation | Which table is LoRA vs Full is inferred from tab order; post-training hosting fees not listed |
| P2 | Fireworks AI, https://fireworks.ai/pricing | 2026-10-16 | USD | Primary documentation | No job minimum stated |
| P3 | Google Cloud, https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing | 2026-10-16 | USD | Primary documentation | — |
| P4 | AWS, https://aws.amazon.com/bedrock/pricing/ (values resolved from AWS price data files) | 2026-10-16 | USD; us-east-1 / us-west-2 | Primary documentation | Placeholders on the page; values from AWS price data |
| P5 | Microsoft, https://prices.azure.com/api/retail/prices | 2026-10-16 | USD; eastus2, northcentralus | Primary documentation | The pricing web page renders no numbers without JavaScript |
| P6 | OpenAI, https://developers.openai.com/api/docs/pricing | 2026-10-16 | USD | Primary documentation | Platform closing to all customers on 2027-01-06 (#30 M2) |
| P7 | AWS, https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/us-east-1/index.json | 2026-10-16 | USD; us-east-1; publication 2026-10-15 | Primary documentation | p5.48xlarge, p4de.24xlarge and g6e.xlarge re-checked directly |
| P8 | Google Cloud, https://cloud.google.com/products/compute/pricing/accelerator-optimized | 2026-10-16 | USD; us-central1 (page default) | Primary documentation | Other regions load by JavaScript |
| P9 | Microsoft, Azure Retail Prices API (as P5) | 2026-10-16 | USD; eastus | Primary documentation | Reservation figure is a per-term total |
| P10 | Lambda, https://lambda.ai/pricing | 2026-10-16 | USD; excludes tax | Primary documentation | H100 SXM $3.99 and A100 SXM 80 GB $2.79 re-checked directly |
| P11 | RunPod, https://www.runpod.io/pricing | 2026-10-16 | USD; region not stated | Primary documentation | Page dated 2026-10-08 |
| P12 | CoreWeave, https://www.coreweave.com/pricing | 2026-10-16 | USD; North America | Primary documentation | — |
| P13 | AWS, https://aws.amazon.com/s3/pricing/ | 2026-10-16 | USD; us-east-1 | Primary documentation | — |

### Secondary input (S)

| ID | Publisher and URL | Access date | Version / region | Evidence grade | Limitations / reuse terms |
| --- | --- | --- | --- | --- | --- |
| S1 | Internal guide supplied by the workstream owner, `ai_training_methods_local_guide_2026-10-16.md` (not committed) | 2026-10-16 | — | Estimate (secondary compilation) | Its author states that hardware figures are estimates and some paper results are cited from memory. Each claim used here was re-checked against E1–E9 |

S1 claims re-checked:
- **16 B/param full FT:** confirmed under ZeRO accounting only; HF accounting is 18 B.
- **8-bit Adam ≈ 6 B/param:** refuted as stated. It is 10–12 B with an fp32 master copy; 6 B holds only without a master copy.
- **QLoRA ≈ 0.55 B/param:** the low end. The QLoRA paper's 7B example is ≈ 0.75 B/param.
- **Logits ≈ 2.5 GB per 4,096-token sequence at a 152k vocabulary:** confirmed arithmetically (E6).
- **Unsloth 5 GB GRPO for a 1.5B model:** vendor claim; the original blog page could not be fetched.
- **70B on 2× 24 GB:** capability claim only (B12).

## Compatibility proposals

These rules are proposed for review by #40 using the [rule proposal template](../../templates/rule-proposal.md). Rules that depend on the estimator return `unknown` when an input is missing, never `pass`.

| Rule | Participating fields | Assertion | Outcome / severity | Evidence | Status |
| --- | --- | --- | --- | --- | --- |
| K-01 | estimated peak per-device memory, `accelerator.spec.vram_gb` | Estimate > VRAM | fail / error | E1–E11 | verified formula components; overhead factor is an estimate |
| K-02 | same | Estimate within 15% of VRAM | pass / warning ("may not fit; dry-run recommended") | — | hypothesis: threshold is a policy choice |
| K-03 | method = full_finetune, single device, no ZeRO / offload | 16·N exceeds VRAM | fail / error, with remediation "LoRA / QLoRA, ZeRO-3 or offload" | E1, E10 | verified |
| K-04 | method = qlora, framework / accelerator backend | QLoRA requires bitsandbytes-style 4-bit kernels on the backend; Axolotl documents no QLoRA on `metal` | fail / error | #30 F13 | verified for Axolotl; others unknown |
| K-05 | method = dpo, reference model not precomputed, full FT | Adds 2·N for the reference model | pass / warning | E17 | verified |
| K-06 | accelerator lacks bf16 (e.g. T4 / V100 class) | fp16 with loss scaling only; bf16 recipes fail or overflow | pass / warning | — | hypothesis: needs #10 accelerator dtype facts |
| K-07 | multi-device, framework `distributed_supported` = false | Cannot use more than one device | fail / error | #30 | verified for listed frameworks |
| K-08 | managed service selected, `training_compute.compute_profile_ref` set | Managed per-token services have no user compute profile; use a price-only selection | unknown / warning | P1–P6 | contract gap: `compute_profile_ref` is required in v1 |
| K-09 | estimate confidence = `estimated` and no calibration row for the model family / method | Show the estimate as a range with assumptions | pass / info | B1–B11 | policy proposal |

## Pricing and capacity

### Managed training prices (USD, captured 2026-10-16)

| Provider | Model / tier | Meter | Price | Conditions | Evidence |
| --- | --- | --- | --- | --- | --- |
| Together | Llama 3.1 8B / Qwen3.5 ≤9B, LoRA | per 1M tokens SFT / DPO | 0.34 / 0.84 | min $4.00 per job | P1 |
| Together | Llama 3.3 70B, LoRA | per 1M SFT / DPO | 2.03 / 5.08 | min $4.00 | P1 |
| Together | Llama 3.1 8B / Llama 3.3 70B, full | per 1M SFT | 0.38 / 2.24 | min $4.00 | P1 |
| Fireworks | ≤16B | per 1M: LoRA SFT / LoRA DPO / full SFT / full DPO | 0.50 / 1.00 / 1.00 / 2.00 | — | P2 |
| Fireworks | 16.1–80B | same | 3 / 6 / 6 / 12 | — | P2 |
| Fireworks | Dedicated Training API | per GPU-hour H100 / H200 / B200 | 8.00 / 8.00 / 13.00 | 1.5× in restricted regions | P2 |
| Vertex | Gemini 2.5 Flash / 2.5 Flash-Lite / 2.5 Pro | per 1k training tokens | 0.005 / 0.0015 / 0.025 | Tuned Gemini 3+ endpoints cost 1.5× base | P3 |
| Vertex | Llama 3.1 8B / Llama 3.3 70B | per 1M SFT | 0.67 / 6.72 | — | P3 |
| Bedrock | Nova Lite | per 1k SFT tokens; storage per model-month | 0.002; 1.95 | us-east-1 | P4 |
| Bedrock | Llama 3.1 8B Instruct | per 1M training tokens; storage per month | 1.49; 1.95 | us-west-2 only | P4 |
| Bedrock | Llama 3.1 8B Provisioned Throughput | per model-unit-hour: no commit / 1-month / 6-month | 24.00 / 21.18 / 13.08 | us-west-2 | P4 |
| Azure OpenAI | gpt-4.1-mini | per 1k training tokens global / regional; hosting per hour | 0.005 / 0.0055; 1.70 | eastus2; hosting billed while deployed | P5 |
| OpenAI | gpt-4.1-mini / gpt-4.1 / gpt-4.1-nano | per 1M training tokens | 5.00 / 25.00 / 1.50 | Closing to all customers 2027-01-06 | P6 |

### Self-run GPU list prices (USD, on-demand, captured 2026-10-16)

| Provider | SKU | GPUs | Price per hour | Region | Evidence |
| --- | --- | --- | --- | --- | --- |
| AWS | p5.48xlarge | 8× H100 | 55.04 | us-east-1 | P7 |
| AWS | p4de.24xlarge | 8× A100 80 GB | 27.45 | us-east-1 | P7 |
| AWS | g6e.xlarge | 1× L40S | 1.861 | us-east-1 | P7 |
| Google Cloud | a3-highgpu-8g | 8× H100 | 88.49 (spot 52.79) | us-central1 | P8 |
| Azure | Standard_ND96isr_H100_v5 | 8× H100 80 GB | 98.32 (spot 18.17) | eastus | P9 |
| Lambda | H100 SXM (8× node) / A100 SXM 80 GB | per GPU | 3.99 / 2.79 | — (plus tax) | P10 |
| RunPod | H100 SXM / RTX 4090 | per GPU, Secure / Community | 3.99 / 2.69; 0.89 / 0.34 | not stated | P11 |
| CoreWeave | HGX H100 | 8-GPU instance | 49.24 | North America | P12 |
| AWS | S3 Standard | — | 0.023 per GB-month (first 50 TB) | us-east-1 | P13 |

### Priced scenarios

Both scenarios use the same dataset: **10M tokens × 3 epochs = 30M training tokens**. They are **compute-only lower bounds**. Self-run times come from published throughput (B2, B3, B6, B8), not from the formula. They exclude setup, data loading, evaluation, idle time, minimum billing increments and egress.

**Scenario A, 8B model, SFT**

| Path | Basis | Cost (USD) |
| --- | --- | --- |
| Together, Llama 3.1 8B LoRA | 30 × 0.34 | 10.20 |
| Fireworks, ≤16B LoRA | 30 × 0.50 | 15.00 |
| Vertex, Llama 3.1 8B | 30 × 0.67 | 20.10 |
| Bedrock, Llama 3.1 8B | 30 × 1.49, plus $1.95/month storage | 44.70 |
| Self-run, 1× RTX 4090, LoRA | 30M / 3,083 tok/s (B2) = 2.70 h × RunPod 0.89 (Secure) / 0.34 (Community) | 2.41 / 0.92 |
| Self-run, 1× RTX 4090, QLoRA | 30M / 2,413 tok/s (B3) = 3.45 h × 0.89 / 0.34 | 3.07 / 1.17 |
| Self-run, 8× H100, full SFT in FP8 | 30M / (16,222 × 8) tok/s (B6) = 0.064 h × AWS p5.48xlarge 55.04 | 3.53 |

**Scenario B, 70B model, LoRA SFT**

| Path | Basis | Cost (USD) |
| --- | --- | --- |
| Together, Llama 3.3 70B LoRA | 30 × 2.03 | 60.90 |
| Fireworks, 16.1–80B LoRA | 30 × 3.00 | 90.00 |
| Vertex, Llama 3.3 70B | 30 × 6.72 | 201.60 |
| Self-run, 8× H100 | 30M / (2,621 × 8) tok/s (B8) = 0.40 h × Lambda 31.92 / CoreWeave 49.24 / AWS 55.04 | 12.69 / 19.57 / 21.87 |

Model-to-model differences (Llama 3 vs 3.1 vs 3.3) are ignored for throughput. B6 and B8 are NVIDIA vendor claims in FP8.

**Hosting after training dominates managed costs.** A fine-tuned Azure OpenAI gpt-4.1-mini deployment bills $1.70/hour while deployed, about **$1,241 per month** at 730 hours (P5). Training it on Scenario A's 30M tokens costs $150 (30,000 × $0.005 per 1k global), so one month of hosting is about 8× the training cost. Bedrock custom models need storage plus Provisioned Throughput or on-demand custom-model inference (P4).

The builder must show the post-training serving cost next to the training cost. This is a handoff to #39.

## Recommendation and rationale

- **Memory:** use the component formula, with the gradient dtype, optimiser and fused-loss choice as explicit inputs. Show a range, not a point.
  - Logits are often the largest swing for long sequences and large vocabularies (Qwen3-8B example: 2.5–7.5 GB per sequence).
  - Calibrate against B1–B5 before trusting fit-or-no-fit near the VRAM limit (K-02).
- **Time:** prefer measured tokens/s for the closest calibration row. Fall back to the FLOP formula with an MFU range, and label the result `estimated`.
- **Default for small budgets:** QLoRA or LoRA on a single consumer or L40S-class GPU. Compute cost for a 30M-token run is a few dollars, and a managed LoRA service costs $10–45. Fully fine-tuning an 8B model needs ZeRO or offload beyond a single 80 GB GPU.
- **Managed vs self-run:** at these dataset sizes the managed premium is small in absolute terms. The deciding factors are artifact portability (#30, #33) and post-training hosting cost, not training compute.

## Structured artifacts

No CatalogItem, Pricebook or ResourceEstimate files in this draft:
- `training_compute.spec.compute_profile_ref` must reference a `compute_profile` already in the catalog. No T2 compute profiles, accelerators or hosting platforms exist yet (#9, #10).
- Pricebook rates must reference catalog items and versions in this repository. The meter enum also has no per-training-token, job-minimum or training-hour meter, so managed training prices cannot be expressed in v1.
- ResourceEstimate has `training.estimated_gpu_hours` but no training-memory metric.

The prices above are recorded with provenance so they can be converted once those items exist.

## Open questions and handoffs

| Question | Follow-up issue / owner |
| --- | --- |
| Accelerator facts the estimator needs (VRAM, bf16/fp8 support, peak dense TFLOP/s) and compute profiles for the SKUs priced here | #10 · @Mattycodes69 |
| Hosting platforms and regions for the GPU price rows | #9 · @Mattycodes69 |
| Pricebook meters for `training_tokens_1m`, `training_tokens_1k`, `training_hour`, `job_minimum` and `model_storage_month`; a ResourceEstimate metric `training.estimated_peak_per_device_vram_gb`; `compute_profile_ref` optional for managed services | #40 · @CompleteDotTech |
| Price normalisation: per-1k vs per-1M tokens, epochs and validation tokens, job minimums, and post-training hosting shown next to training cost | #39 · @PUSHINGSQUARES |
| Training time and cost estimate for distillation and GRPO (only memory is sketched) | #31 · @appletechie |
| Re-fetch the Unsloth GRPO blog (403) and confirm the torchtune B1 recipe settings | #31 · @appletechie |
| Methods and frameworks consumed from #30 | #30 · @appletechie (PR #68) |
| Freshness threshold for prices (they change faster than specifications) | #41 · @CompleteDotTech |

None of the handoffs above is confirmed yet.
