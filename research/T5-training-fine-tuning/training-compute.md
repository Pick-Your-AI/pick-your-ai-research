# T5: Training Compute

Issue: #31 · Contract: 1.0.0 · Kinds: `training_compute`
Status: ready for review · Last researched: 2026-10-16
Decision revision: `training-compute-decision/0.2.0` · Scope correction: 2026-10-18

## User decision

What compute, time, storage and cost does a training run need?

This covers three things:
- memory and time estimates for training objectives (SFT, DPO, GRPO, distillation), parameter-update methods (full or adapters) and quantization choices;
- storage and distributed-training needs;
- managed per-token training prices vs self-run GPU-hours.

Training channels (these do not determine T0 serving deployment modes):
- **Provider-operated training:** billing is offering-specific: training tokens, GPU/time units or job minimums, with post-training hosting or storage where applicable (P1–P6). Capacity choices and responsibility for underlying allocation vary by offering; dedicated training may require selecting capacity.
- **User-operated training:** the user picks accelerators (#10) on a host (#9). The builder must estimate whether the run fits in memory and how long it takes.

Inference GPU sizing is owned by #10, and cost aggregation by #39.

## Candidate options

Compare **provider-operated training offerings**, including shared per-token and dedicated/GPU-time offerings where documented, with a **user-operated compute profile**. Billing alone does not identify allocation controls or a serving deployment mode. API and managed training are covered by the offering-specific P1–P6 inventory; self-run training uses explicit hardware/profile inputs. Training itself remains outside the T0 serving-mode calculation. The estimation method below supplies conditional quantities for comparison on a stated dataset.

### Estimation method

**Inputs:**
- model catalog (#6): N total params, layers L, hidden size h, heads a, KV dimension, FFN size, vocabulary V;
- accelerator catalog (#10): VRAM, bf16/fp8 support, peak dense TFLOP/s, count G;
- user settings: sequence length s, micro-batch b, LoRA rank r and target modules, epochs E, dataset tokens D, gradient checkpointing, optimiser, ZeRO stage.

All formulas are bytes per GPU unless stated. Each term is tagged with its evidence; anything tagged **estimate** is this project's derivation.

These are conditional component-accounting models, not universal requirements for a named method. Bind the exact model revision, objective, updated parameters, weight/gradient/optimizer dtypes, quantizer, trainer/backend versions, sequence and microbatch sizes, accumulation, checkpointing, optimizer schedule, sharding/offload policy and per-rank residency. Sum tensors that coexist within each execution phase, then take the peak; account separately for activations, loss/logit buffers, temporary workspaces, communication buffers and runtime overhead. Published VRAM is a capacity fact, not a measurement of memory available to this job. Preserve source GB/GiB units and do not pool the VRAM of separate devices (E1–E11; accepted #30 H5).

The `16·N` state example assumes 2-byte weights, 2-byte gradients, a 4-byte master copy and two 4-byte Adam states for every simultaneously resident parameter. Changing only gradients to 4 bytes gives `18·N`. Neither includes activations or runtime workspaces. Different optimizer states, no master copy, optimizer-in-backward, sharding, offload or another residency schedule require different accounting. Selecting full fine-tuning alone therefore does not imply `16·N` on every GPU; B1 retains its distinct published conditions and explicitly inferred configuration link.

| Term | Formula | Evidence | Grade |
| --- | --- | --- | --- |
| Full FT, AdamW mixed precision | 16·N bytes for the stated simultaneous bf16 weights/grads, fp32 master and two fp32 Adam states; 18·N with fp32 gradients under the otherwise unchanged state set | E1 §3.1; E2 | Primary documentation; conditional state accounting, not a universal full-FT floor |
| Full FT, 8-bit Adam | Adam states drop from 8 to 2 bytes/param: 10·N (ZeRO accounting) or 12·N (HF accounting). The 6·N figure holds only for pure-bf16 training with no master copy | E3 §2 | Primary documentation |
| LoRA, bf16 base | 2·N + 16·N_lora, where N_lora = Σ_layers Σ_targets r·(d_in + d_out) | E4 §4.2 | Primary documentation (component accounting is an estimate) |
| QLoRA (NF4 + double quant) | ≈0.55–0.75·N + 16·N_lora. Double quant costs 0.127 bits/param of constants; the paper's 7B base used 5,048 MB, i.e. ≈0.75 bytes/param | E5 | Primary documentation |
| Activations | No checkpointing: L·s·b·h·(34 + 5·a·s/h) (16-bit, GPT-style block). FlashAttention removes the 5·a·s/h term. Full checkpointing: 2·s·b·h·L | E6 Eq. 1 | Primary documentation; the constant 34 is approximate for SwiGLU / no-dropout models (estimate) |
| Logits | k·4·s·b·V with k ≈ 2–3 for loss and gradient; k ≈ 0 with fused or chunked cross-entropy (Cut Cross-Entropy, Liger) | E6 §4.1; E7; E8 | Primary documentation (k from E7's figures, estimate) |
| DPO | Account for chosen/rejected sequences under the actual batching schedule. An additional resident bf16 reference contributes 2·N; sharing, precomputed reference log-probabilities and offload change its allocation and phases | E17 | Primary documentation; no universal zero-reference-memory or 2·N rule |
| GRPO / RL | Policy as SFT, plus rollout KV cache, plus logits × number of generations (`2·2·generations·s·V` bytes in bf16 per E9) | E9 | Vendor claim (Unsloth) |
| Distillation | Student as SFT, plus teacher weights (inference only), plus teacher logits (2–4·s·b·V) | — | Estimate |
| ZeRO data parallel (Nd GPUs) | stage 1: 4·N + 12·N/Nd; stage 2: 2·N + 14·N/Nd; stage 3: 16·N/Nd. The DeepSpeed estimator is more conservative: ZeRO-3 = 4·largest_layer + 18·N/Nd | E10 Table 1; E11 | Primary documentation |
| Runtime overhead | +10–20% for CUDA context and fragmentation | — | Estimate; no source fixes it |
| Training FLOPs | Full FT model FLOPs: 6·N per token (+ attention 12·L·a·d_head·s). Full gradient checkpointing adds 2·N executed hardware FLOPs; exclude this recomputation from an MFU numerator | E12, E13, E14 §4 / App. B | Primary documentation |
| LoRA / QLoRA FLOPs | ≈4·N per token: no weight gradients for frozen parameters. LoRA reports 25% higher throughput (43.1 vs 32.5 tokens/s per V100) | E4 §4.2, fn. 5; E14 | **Estimate**: no primary source states 4·N |
| Time | T = model FLOPs/token × D × E / (G × peak × MFU), with matching dtype and FLOP conventions. Default MFU 0.35–0.45 on dense multi-GPU H100/A100 (PaLM 46.2%; Megatron 54.2% at scale); 0.2–0.35 on consumer GPUs. Prefer matched measured tokens/s | E14; E6 | Primary documentation (consumer range is an estimate) |
| Training tokens billed | dataset tokens × epochs (Together, Fireworks, Vertex, Bedrock); Together also bills validation tokens × evaluations; Fireworks multi-turn reasoning traces × (average turns / 2) | P1, P2, P3, P4 | Primary documentation |
| Storage | Full checkpoint: 2·N weights + optimiser state if resumable (12·N, or 4·N with 8-bit), × checkpoints kept. LoRA adapter: 2·N_lora (bf16). The LoRA paper reports GPT-3 175B 350 GB → 35 MB at r=4 on q and v | E4; E15; E16 | Primary documentation |

`accelerate estimate-memory` (E18) is a model-state estimate under its selected dtype and estimator assumptions. Its illustrative "Training using Adam" output omits activation and logit/workspace terms; neither that number nor the weight-only output is a fit test or a universally required state allocation for another optimizer/residency recipe. Pin the actual estimator version/options before using it as a component input.

QLoRA multipliers and activation/logit formulas retain their source and implementation assumptions. Sharing a base or precomputing DPO reference values does not establish zero total reference-related memory; precomputation, stored values, loss buffers and transfer still need their own phase accounting. A fused loss may avoid a materialized full logits tensor while retaining other workspaces. The displayed MFU ranges remain uncalibrated planning assumptions, not transferable performance evidence (E5–E8, E14, E17).

PaLM defines model FLOPs utilization (MFU) without rematerialization work. Use model forward/backward FLOPs with that denominator. An accounting numerator that includes executed checkpoint recomputation instead requires a correspondingly defined hardware FLOPs utilization (HFU) or matched measured throughput. Mixing recomputation-augmented hardware FLOPs with MFU double-counts that overhead (E14 §4 / App. B). The historical priced scenarios below retain their published-token-throughput basis.

### Worked memory example: Qwen3-8B

Model config (E19): N = 8,190,735,360; h = 4096; L = 36; 32 heads; 8 KV heads; head_dim 128; FFN 12,288; V = 151,936.

LoRA at r = 16 on all linear layers gives N_lora = 1,212,416 per layer × 36 = **43,646,976**.

| Setup | Static memory (GB) | Notes |
| --- | --- | --- |
| Full FT, AdamW (16 B/param) | 131.1 | This specific unsharded, simultaneously resident state set exceeds 80 GB before overhead; 147.4 GB with fp32 grads |
| Full FT, 8-bit Adam | 81.9–98.3 | Above 80 GB under the table's retained master-copy/state schedule; other recipes need their own accounting |
| LoRA, bf16 base | 16.4 + 0.7 | Plus activations and logits |
| QLoRA | 4.5–6.1 + 0.7 | Plus activations and logits |
| Logits, s = 4096, b = 1, fp32 | 2.5 raw; 5.0–7.5 with loss and gradient | ≈0 with fused cross-entropy |
| Activations, full checkpointing, s = 4096, b = 1 | 1.2 | 2·s·b·h·L |

QLoRA on Qwen3-8B at s = 4096 is therefore ≈ 6–8 GB with fused cross-entropy, or ≈ 11–15 GB without. The difference is the logits term. The builder must ask whether a fused-loss framework is selected (#30: Unsloth, Liger-enabled TRL, torchtune chunked cross-entropy).

These are estimates. The published rows below provide comparison inputs, not a completed calibration: no row measures this Qwen3-8B configuration, B1 has an inferred configuration, and B12 reports capability without memory or throughput measurements. A calibration must match model revision, objective/update/quantizer, optimizer and state dtypes, trainer/backend, loss implementation, sequence/batch/accumulation, topology/hardware and measurement boundary, then compare predicted and observed memory/time with residuals and uncertainty. Until that evidence exists, retain the uncalibrated estimate label and do not use these examples as a general fit guarantee. Any planning decision still needs the separate accepted evidence-admission policy in K-01.

### Published measurements

| ID | Source | Grade | Conditions | Result |
| --- | --- | --- | --- | --- |
| B1 | torchtune README | Vendor claim (PyTorch's reported measurement) | Llama 3.1 8B full FT, 1× RTX 4090, bs 2, packed 2048, `torch.compile`, measured over one epoch | 18.9 GiB, 1,650 tok/s. The README names no config. The only single-device full-FT config at the commit that added the row uses `PagedAdamW8bit`, `optimizer_in_bwd: True`, activation checkpointing and bf16 — a different state schedule from the 16 B/param example. Linking the row to that config is an inference |
| B2 | torchtune README | Vendor claim (PyTorch's reported measurement) | Same, LoRA, 1× RTX 4090 | 16.2 GiB, 3,083 tok/s |
| B3 | torchtune README | Vendor claim (PyTorch's reported measurement) | Same, QLoRA, 1× RTX 4090 | 7.4 GiB, 2,413 tok/s |
| B4 | torchtune README | Vendor claim (PyTorch's reported measurement) | Llama 3.2 3B, A100, bs 2, s 4096, bf16, compile, chunked cross-entropy, activation checkpointing and offload, 8-bit AdamW | full FT 17.6 GiB; LoRA 8.5 GiB; QLoRA 4.6 GiB |
| B5 | QLoRA paper Fig. 6 | Primary documentation (authors' reported experiment; unverified) | bs 1, s 512, gradient checkpointing | 7B 6.9 GB; 13B 11.3 GB; 33B 24.7 GB; 65B 45.0 GB. 65B Guanaco: 24 h on one 48 GB GPU |
| B6 | NeMo 25.04 performance summary | Vendor claim (NVIDIA) | Llama3-8B SFT, 8× H100, FP8, SQuAD packed 4096, global batch 32 | 16,222 tok/s/GPU, 733 TFLOP/s/GPU |
| B7 | NeMo 25.04 | Vendor claim | Llama3-70B SFT, 32× H100, TP4/PP4 | 1,619 tok/s/GPU |
| B8 | NeMo 25.04 | Vendor claim | Llama3-70B LoRA, 8× H100 | 2,621 tok/s/GPU, 730 TFLOP/s/GPU |
| B9 | Unsloth benchmarks | Vendor claim | Llama 3.1 8B QLoRA r = 32, all linear layers, bs 1 | Max context: 78,475 tokens on 24 GB (HF + FA2: 5,789); 342,733 on 80 GB |
| B10 | Unsloth RL guide | Vendor claim | Llama 3.1 8B GRPO, 20K context, 8 generations | 54.3 GB vs 510.8 GB "standard"; GRPO logits 9.8 vs 78.3 GB |
| B11 | Liger Kernel paper | Vendor claim (LinkedIn's reported experiment; not reproduced here) | Llama 3-8B, 4× A100-80G, bf16, AdamW, s 512, bs 64 | +42.8% throughput, −54.8% memory |
| B12 | Answer.AI FSDP + QLoRA | Vendor claim | 70B on 2× 24 GB (RTX 3090) | Capability only; no sequence length, memory or time published |

### Distillation and GRPO time/cost accounting (2026-10-18)

This is a **project-derived accounting method**, not a benchmark or a price quote. E20–E21 identify stages that the SFT-only FLOP estimate omits; they supply no transferable throughput for this note's selected profiles. Keep time and cost unknown until phase durations or matched throughput bounds and applicable rates exist.

**GRPO.** TRL generates groups of completions, scores rewards, and can perform multiple updates per generation via `num_iterations`. A nonzero KL coefficient adds reference-policy work. Generation can share training GPUs or use a separate server allocation. Its logged `step_time` includes generation (E20). For a defined generation cycle, record disjoint durations in seconds:

`T_cycle = t_generation + t_reward + t_reference + t_updates + t_sync_other`

`t_updates` covers all updates using that cycle's samples; do not multiply the entire cycle by `num_iterations`. Count prompt prefill, sampled completion lengths, reward/tool latency and weight synchronization in their actual phases. When using inclusive `step_time`, do not add generation a second time. This sum describes serial execution; overlapping pipelines require a measured schedule or critical-path estimate, not addition of overlapping wall times.

**Distillation.** Separate fixed teacher-generated data plus student SFT from online teacher-feedback training. TRL GKD uses `lmbda` to select student-generated batches and `seq_kd` to enable teacher-generated sequences; teacher token-level feedback is additional work (E21). Record:

`T_total = t_prepare_once + sum(t_generate + t_teacher_feedback + t_student_update + t_transfer_other)`

Sum over actual batches. Charge reusable offline preparation once per artifact, then student passes separately. Count online generation and feedback at their executed frequency, not once for the dataset. Do not assume token-distribution access from a text-only API or infer permission to distil from technical access. The exact teacher/student revisions, tokenizers, sequence distributions, generation settings, caching, batch schedule and resource assignments are required inputs.

**Allocation and billing.** For either method, derive allocated GPU-hours as `H = sum_a(G_a × allocated_seconds_a / 3600)` over disjoint allocations. A dedicated rollout or teacher allocation counts while reserved, including idle periods; shared hardware is counted once. For per-GPU-hour rates, cost is `sum_a(H_a × rate_a)`; for instance-hour rates use allocated instance-hours directly, without another GPU-count multiplier. Add applicable API/reward calls, minimum billing, storage and egress separately with exact units and rate scope. This is accounting notation, not adoption of new #39/#40 meters. Missing rates or durations remain unknown, not zero. Phase bounds produce a conditional serial-time range only when all terms have bounds; no finite upper bound is justified for unbounded tool latency, retries or generation.

Next evidence request to #31: matched phase timings and allocation lifetimes for one specified GRPO or distillation configuration. #39 must confirm its billing scope. No hardware run or numeric cost is claimed here.

## Comparison fields

These cover the CatalogItem envelope plus `spec_training_compute`. The issue's conceptual fields map as follows:
- `accelerator (→ #10)` → `compute_profile_ref` → `compute_profile.spec.accelerator_ref`
- `storage` → `storage_ref`
- `time estimate` → ResourceEstimate `training.estimated_gpu_hours`; catalog `max_gpu_hours` is a separate optional component fact, not the derived estimate or a user's budget
- `method`, `model size`, `memory estimate`, `price basis`, `assumptions` and `measured vs estimated` have no v1 catalog field and live in ResourceEstimate or this note.

| Field / JSON pointer | Type and unit | Candidate finding | Evidence ID | Conditions / unknowns |
| --- | --- | --- | --- | --- |
| `/spec/compute_profile_ref` | `compute_profile` catalog ID | Must reference a compute SKU already in the catalog (T2) | contract; T2 records on `main` | Two documented profiles exist: `aws-ec2-g6e-xlarge-us-east-1` (1× `nvidia-l40s`) and `aws-ec2-p4de-24xlarge-us-east-1` (8× `nvidia-a100-80gb`), both on `aws-ec2` in `us-east-1`. Their exact versions and limits remain in [Upstream T2 records](#upstream-t2-records). The other priced SKUs still lack matching profile records; no historical rate is automatically bound to either profile. |
| `/spec/max_gpu_hours` | optional number ≥0, GPU-hours | Sourced component/offer limit when its exact semantics are established | frozen schema; offering evidence required | Not automatically an estimated duration, caller budget or permission to spend; billing scope is offer-specific |
| `/spec/ephemeral` | optional boolean | Sourced component/offer lifecycle property | offering evidence required | An intention to release capacity after a run does not establish this fact |
| `/spec/storage_ref` | `storage` catalog ID | Checkpoint store | E15, E16 | Size from the storage formula |
| ResourceEstimate `training.estimated_gpu_hours` | decimal, `gpu_hour`; confidence `verified/calibrated/estimated/unverified` | Conditional phase/allocation accounting; retain `estimated` until matched calibration is actually recorded | E14, E20, E21; K-09 | B1–B12 are comparison inputs, not automatic calibration; the v1 metric enum has no training-memory metric |
| Objective / update / quantizer (note only) | separate scoped strings and configuration records | Objective such as SFT/DPO/GRPO/distillation; updated parameters or adapter; exact weight quantizer/dtypes | #30 H5 and its pinned framework sources | Do not conflate these dimensions, assume a supported Cartesian product, add fields or reinterpret frozen enums |
| `memory estimate` (note only) | GB per device, with a breakdown | Formula above | E1–E11 | Proposal: add `training.estimated_peak_per_device_vram_gb` to ResourceEstimate |
| `price basis` (note only) | enum proposal: `per_training_token_1m`, `per_training_token_1k`, `gpu_hour`, `training_hour`, `job_minimum`, `model_storage_month`, `hosting_hour` | see pricing tables | P1–P11 | Pricebook meter enum lacks training-token and job-minimum meters |
| `measured vs estimated` | ResourceEstimate `confidence` | — | — | — |

The frozen catalog records component facts; selections, estimates and caller intentions have separate roles. Only `compute_profile_ref` is required in `spec_training_compute`; `max_gpu_hours`, `ephemeral` and `storage_ref` are optional. Preserve reference kind and current intake resolution. A hardware-abstracted offering has an explicit representation gap until #40 adopts an appropriate shape; do not invent a profile. Missing limits or lifecycle facts stay missing, rather than becoming an estimate, false value or requested budget.

## Evidence

Entries accessed on 2026-10-16 unless their row specifies a 2026-10-18 supplement. Apply the adopted #41 checked-versus-verified distinction in [SHARED.md](../../prompts/SHARED.md#contract-and-evidence-intake) and the [current claim-level policy](../T0-configuration/catalog-data-sources.md#evidence-grades-and-labels). A paper may be primary documentation of its method while its own performance figures remain publisher claims. This project has not independently reproduced B1–B12, E7 or E8; source checking and arithmetic do not confer that grade. Original measurement conditions and dates remain attached to the numerical records. Prices are historical USD observations with the provider's stated region, not current quotes.

### Estimation (E)

| ID | Publisher and URL | Access date | Version / region | Evidence grade | Limitations / reuse terms |
| --- | --- | --- | --- | --- | --- |
| E1 | Rajbhandari et al., ZeRO, https://arxiv.org/abs/1910.02054 | 2026-10-16 | — | Primary documentation | Assumes fp16/bf16 gradients |
| E2 | Hugging Face, https://huggingface.co/docs/transformers/main/en/model_memory_anatomy | 2026-10-16 | main | Primary documentation | Assumes fp32 gradients (18 B/param) |
| E3 | Dettmers et al., 8-bit optimizers, https://arxiv.org/abs/2110.02861 | 2026-10-16 | — | Primary documentation | — |
| E4 | Hu et al., LoRA, https://arxiv.org/abs/2106.09685 | 2026-10-16 | — | Primary documentation | GPT-3 figures |
| E5 | Dettmers et al., QLoRA, https://arxiv.org/abs/2305.14314 | 2026-10-16 | — | Primary documentation | — |
| E6 | Korthikanti et al., https://arxiv.org/abs/2205.05198 | 2026-10-16 | — | Primary documentation | GPT-style block |
| E7 | Wijmans et al., Cut Cross-Entropy, https://arxiv.org/abs/2411.09009 | 2026-10-16 | — | Primary documentation for method; Vendor claim for reported performance | Gemma 2 2B; no independent project reproduction |
| E8 | Hsu et al., Liger Kernel, https://arxiv.org/abs/2410.10989 | 2026-10-16 | — | Primary documentation for method; Vendor claim for reported performance | No independent project reproduction |
| E9 | Unsloth, https://unsloth.ai/docs/get-started/reinforcement-learning-rl-guide ; blog https://web.archive.org/web/20251205171033/https://unsloth.ai/blog/grpo | 2026-10-16 | Blog dated 2025-02-20; Wayback snapshot 2025-12-05 | Vendor claim | Live blog returns 403. "5GB VRAM for Qwen2.5 (1.5B)" is stated without sequence length, rank or generation count; the 8B / 20K-context figures are fully specified |
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
| E20 | Hugging Face TRL, [GRPO trainer](https://github.com/huggingface/trl/blob/6d6901c5e3963108076131ac4979d344566b13a2/docs/source/grpo_trainer.md) | 2026-10-18 | commit `6d6901c5e3963108076131ac4979d344566b13a2` | Primary documentation, source checked | Stages and configuration semantics only; no matched throughput or billing guarantee |
| E21 | Hugging Face TRL, [GKD trainer](https://github.com/huggingface/trl/blob/6d6901c5e3963108076131ac4979d344566b13a2/docs/source/gkd_trainer.md) | 2026-10-18 | same commit; experimental trainer | Primary documentation, source checked | Teacher/student generation and feedback semantics; no permission grant or calibrated runtime |

### Benchmarks (B-source)

| ID | Publisher and URL | Access date | Version / region | Evidence grade | Limitations / reuse terms |
| --- | --- | --- | --- | --- | --- |
| BS1 | PyTorch, https://github.com/meta-pytorch/torchtune/blob/main/README.md ; config https://github.com/meta-pytorch/torchtune/blob/30b8519e86/recipes/configs/llama3_1/8B_full_single_device.yaml | 2026-10-16 | v0.6.1 (unmaintained, see #30); row added in commit 30b8519e86 (PR #1664) | Primary documentation | Config-to-row link is inferred (see B1) |
| BS2 | NVIDIA, https://docs.nvidia.com/nemo-framework/user-guide/25.04/performance/performance_summary.html | 2026-10-16 | NeMo 25.04 | Vendor claim | FP8; older release than the current NeMo split |
| BS3 | Unsloth, https://unsloth.ai/docs/basics/unsloth-benchmarks | 2026-10-16 | — | Vendor claim | — |
| BS4 | Answer.AI, https://www.answer.ai/posts/2024-03-06-fsdp-qlora.html | 2026-10-16 | 2024-03-06 | Vendor claim | Alpha release; no measurements |

### Pricing (P)

| ID | Publisher and URL | Access date | Version / region | Evidence grade | Limitations / reuse terms |
| --- | --- | --- | --- | --- | --- |
| P1 | Together AI, https://www.together.ai/pricing ; https://docs.together.ai/docs/fine-tuning/pricing | 2026-10-16 | USD | Primary documentation | Tables labelled "LoRA fine-tuning" and "Full fine-tuning". After training, dedicated-endpoint hosting is billed per minute until the endpoint is stopped; no separate storage fee stated |
| P2 | Fireworks AI, https://fireworks.ai/pricing | 2026-10-16 | USD | Primary documentation | No job minimum stated |
| P3 | Google Cloud, https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing | 2026-10-16 | USD | Primary documentation | — |
| P4 | AWS, https://aws.amazon.com/bedrock/pricing/ (values resolved from AWS price data files) | 2026-10-16 | USD; us-east-1 / us-west-2 | Primary documentation | Placeholders on the page; values from AWS price data |
| P5 | Microsoft, https://prices.azure.com/api/retail/prices | 2026-10-16 | USD; eastus2, northcentralus | Primary documentation | The pricing web page renders no numbers without JavaScript |
| P6 | OpenAI, https://developers.openai.com/api/docs/pricing | 2026-10-16 | USD | Primary documentation | Historical price source; new-job eligibility and exact base/derived-model inference lifecycle are separate (C1; #30 R8) |
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

### Lifecycle scope correction (C)

| ID | Primary source | Access date | Supported scope and remaining unknowns |
| --- | --- | --- | --- |
| C1 | OpenAI, [API deprecations](https://developers.openai.com/api/docs/deprecations), self-serve fine-tuning and exact model shutdown sections | 2026-10-18 | Account-history conditions govern new-job availability; existing active customers lose job creation on 2027-01-06. Derived-model inference follows the applicable base-model lifecycle, not that shared job cutoff. Current-state source, region/account not selected; no historical price refresh or customer eligibility established |

Match the exact provider, base/derived model, operation, account, region and intended date before using a historical training price. The former statement that the entire OpenAI platform closes on the new-job cutoff was too broad. The accepted #30 R8/H5 record supplies the separate lifecycle/configuration input boundary; it does not make an unknown customer's job eligible.

## Compatibility proposals

This note proposes `training-compute-decision/0.2.0` through the [#40 template](../../templates/rule-proposal.md), retaining K-01–K-09 identities and superseding the earlier unscoped assertions. #40 owns executable IDs, input placement, admission/confidence policy and migration. These are reviewed-research candidates, not a published ruleset or changes to frozen v1.

### Shared participants and evaluation envelope

| Participant | Existing fields and additional research inputs |
| --- | --- |
| Exact enabled training selection and `training_compute` | Bound catalog ID/version, `/spec/compute_profile_ref`, optional `/spec/max_gpu_hours`, `/spec/ephemeral`, `/spec/storage_ref`, provenance; the requested operation, objective and allocation plan remain separately identified research inputs |
| Referenced `compute_profile`, accelerator and storage | Exact IDs/versions and `/spec/accelerator_ref`, hardware `/spec/vram_gb` and `/spec/precisions`, sourced host/region/device inventory; per-rank usable capacity, allocation lifetimes, reserved resources and storage quantities need their own scope and units |
| Selected model and training framework, with separate teacher/reference roles when used | Exact model revision and parameter count; framework `/spec/methods`, `/spec/backends`, `/spec/distributed_supported` and provenance; objective/update/quantizer, optimizer/dtypes, topology, batch/accumulation, sequence/packing, loss, checkpoint/offload and phase schedule remain note inputs under accepted #30 H5 |
| Estimate, measurement, policy and offering | ResourceEstimate `training.estimated_gpu_hours` where applicable; note-only per-device memory intervals and uncertainty, matched measurement provenance/residuals, named headroom policy, offer/account/region/date and billing controls. None is inferred from an unrelated selection or price meter |
| Owners and consumers | #31 owns training sizing; #10/#9 supply scoped infrastructure facts; #30 supplies configuration support; #39 receives quantities and units; #40/#41 govern contract/evidence adoption. Dataset/source lawful-basis assessments remain with #32 and its responsible assessor |

Evaluate each exact enabled selection and its bound participants. Multiple devices do not create a pooled VRAM limit; a teacher/reference is not interchangeable with the policy model.

1. **Applicability:** known absence of optional training or a positively false row condition is `skipped`; unresolved applicability is `unknown`. Malformed identities or selections remain validation errors, not fabricated compatibility outcomes.
2. **Admission:** bind sources, dates, units and exact recipe/hardware/operation scope. Apply the accepted [#41 policy](../T0-configuration/catalog-data-sources.md#conflict-resolution) and [shared rules](../../prompts/SHARED.md#contract-and-evidence-intake), including scope/authority precedence and complete-list qualification. No arbitrary TTL, confidence threshold or evidence upgrade is introduced. Unresolved equal-rank yes/no conflicts, missing/unqualified inputs and unmarked list absence remain `unknown`; retain the deciding policy and any disputed numeric bound.
3. **Outcomes and severity:** use `pass`, `fail`, `unknown`, `skipped`; each row's severity is fixed for all four. Eligible evidence satisfying the positive predicate passes; an eligible explicit contrary fact or proven unmet requirement fails. Missing resource evidence uses proposed `on_unknown: review`, not an invented permission or universal deployment block.
4. **Estimates:** preserve the accepted conservative-bound policy. An eligible bounded estimate meeting the applicable admission/confidence requirements may decide a planning predicate using its upper bound. Straddling a memory limit fails conservatively with "may not fit" and the uncertainty shown; it is not proof of runtime OOM. A bare heuristic point, partial counter, unmatched measurement or unqualified interval remains unknown. A declared uncalibrated estimate may still qualify under that existing policy; K-09 does not require calibration for every estimate.
5. **Explanation and remediation:** report participant identities/roles, predicate, actual bound or missing input, source/grade, deciding policy, uncertainty and a concrete next action. A pass covers only that predicate. Checked documentation stays unverified; a skipped or unsupported-evidence result acquires no checked-evidence badge. No numerical run is claimed by these research examples.

### K-01 — Per-device capacity planning; severity `error`

**Applicability and predicate:** for a self-run or explicitly hardware-bound training plan, the admitted peak-memory upper bound `U` does not exceed the per-rank available capacity `C`, in matching units and phase scope. Known hardware abstraction skips this hardware-capacity predicate; unresolved abstraction or binding is unknown.

**Outcomes:** an eligible inclusive estimate/measurement bound under the applicable confidence policy gives pass when `U <= C`, otherwise conservative fail with "may not fit", including an interval crossing capacity. A known required resident-state lower bound exceeding `C` also establishes failure of this capacity predicate. Missing workspace/phase scope, unqualified estimates, partial tensor counters or mismatched configurations give unknown, not an automatic impossibility claim (E1–E11; #41 policy).

**Explanation/remediation:** display the complete admitted interval, capacity, provenance and uncertainty; distinguish a conservative planning failure from a measured failure or required-state contradiction. Obtain qualified evidence or revise batch, precision, optimizer, checkpoint, sharding or offload settings and reevaluate; none of those alternatives is promised to work.

### K-02 — Selected planning headroom; severity `warning`

**Applicability and predicate:** for a hardware-bound plan with the named project headroom policy selected, the admitted upper bound is at most `(1-h)·C`, with proposed `h = 0.15`. This 15% is a project policy choice, not a vendor capacity fact.

**Outcomes:** pass when `U <= 0.85·C`; otherwise fail/warning using the conservative bound and visible interval. Missing or unqualified interval/policy inputs give unknown. Positively unselected policy or hardware abstraction skips this row. No new confidence threshold is supplied.

**Explanation/remediation:** show the chosen policy, threshold, full interval and uncertainty. A failure is a headroom warning, not proof of OOM. Request matched calibration or revise the plan; preserve K-01 as its separate capacity decision.

### K-03 — Conditional full-parameter state budget; severity `error`

**Applicability and predicate:** only for the explicitly unsharded, non-offloaded, simultaneously resident full-parameter state set of 2-byte weights + 2-byte gradients + 4-byte master + two 4-byte Adam states, `16·N <= C` for the selected rank (E1/E2/E10).

**Outcomes:** pass or fail this state-only predicate from those admitted quantities. Undeclared dtypes, optimizer schedule or residency give unknown. A positively different optimizer/master-copy/sharding/offload/schedule skips this particular 16·N rule and still needs appropriate K-01 accounting; merely saying "full fine-tuning" does not establish applicability.

**Explanation/remediation:** a pass excludes activations, workspaces and overhead and does not establish job fit. Show the exact state terms or use a separately qualified recipe's accounting. Never infer a universal 80 GB minimum from the method name.

### K-04 — Selected quantized-training support; severity `error`

**Applicability and predicate:** when training uses a quantized base, the exact model revision, update method, quantizer, trainer/backend versions and hardware combination are supported. Pass on an admitted joint positive, fail on an admitted scoped negative, unknown for partial or unmatched support; a positively unquantized plan skips this row (#30 H5/F-23 and its pinned R1–R3 sources).

**Explanation/remediation:** retain Axolotl's documented Metal exclusion only for its exact scope. QLoRA does not universally select bitsandbytes, and a hardware precision feature is not joint training support. Identify the missing/negative combination and propose a separately qualified backend/quantizer or unquantized recipe.

### K-05 — DPO reference accounting; severity `error`

**Applicability and predicate:** for DPO, the allocation/phase plan represents every required reference allocation under the admitted strategy, precision, sharing/precomputation/offload and workspace configuration (E17). A known non-DPO objective skips the row.

**Outcomes:** pass a complete consistent plan; fail only when a complete admitted ledger omits a known required allocation or an explicit recorded zero/denial contradicts that requirement. Missing strategy, fields or residency scope give unknown. A separate resident bf16 reference may require 2·N; an absent duplicate base does not make all reference memory zero.

**Explanation/remediation:** identify the actual reference strategy, its memory and timing phases, and the omitted or unknown component. Complete the plan or change the strategy and recompute the phase peak.

### K-06 — Selected execution precision; severity `error`

**Applicability and predicate:** for an identified dtype-dependent training operation, the selected dtype/trainer/backend/kernel/hardware combination is supported. An admitted joint positive passes; an explicit scoped incompatibility fails; native hardware precision alone or missing software scope gives unknown. A positively excluded dtype-specific operation skips the rule (#10 facts; #30 H5/F-23).

**Explanation/remediation:** distinguish native, emulated and software-supported operation where evidence establishes them. Missing native bf16 proves neither that fp16 is the only alternative nor that all bf16 recipes overflow. Suggest a separately qualified dtype/backend recipe; loss scaling is not a universal remedy.

### K-07 — Selected distributed plan; severity `error`

**Applicability and predicate:** for multiple devices, the exact model/objective/update/quantizer/trainer/backend versions, distribution method and device topology are jointly supported. Pass admitted support, fail an explicit admitted negative covering that plan, and retain unknown when only a generic catalog boolean/count or incomplete matrix is available. A positively single-device plan skips this row (#30 H5/F-23 and pinned R1/R3).

**Explanation/remediation:** show the exact supported, excluded or unresolved topology/configuration. Select a separately qualified strategy or reevaluate a single-device plan. A framework boolean does not measure placement, pooled memory, runtime or cost.

### K-08 — Offering and allocation consistency; severity `error`

**Applicability and predicate:** for an evaluated training offering/allocation claim, the exposed allocation fields agree with its admitted operation, account/region/date and controls. A complete consistent binding passes; an explicit contradiction fails; unknown offering controls or meter/allocation relationship remain unknown. Positively no such claim to evaluate skips the row (P1–P6; C1).

**Explanation/remediation:** per-token billing alone does not prove absent compute controls; dedicated/GPU-time managed offerings retain their own scope. Identify a documented contradiction or request the missing offering facts. For positively hardware-abstracted offers, preserve the frozen required-profile representation gap with #40 rather than inventing a selectable profile. Passing this consistency predicate does not resolve that gap or grant account entitlement.

### K-09 — Requested or claimed calibration; severity `warning`

**Applicability and predicate:** when calibration is requested, claimed or relied upon, the estimate's measurement matches model revision, objective/update/quantizer, optimizer/dtypes, sequence/batch, trainer/backend, hardware/topology and measurement boundary, with residuals and uncertainty recorded. Admitted matching evidence passes; a demonstrated mismatch in the specific calibration claim fails/warning. Missing evidence or an unrecorded scope gives unknown. Positively no calibration claim or reliance skips this row while retaining the estimate's uncalibrated label (B1–B12; #41).

**Explanation/remediation:** a neighboring model family is not matched calibration. Show the mismatch or missing dimension and request a matched measurement with residuals. Publisher results retain their source grade; this review supplies no project reproduction. Separately eligible estimated bounds may still decide K-01/K-02 under the accepted policy.

### Synthetic decision cases

These are hand-worked examples of the proposed predicates, not executed tests, vendor observations or admitted training estimates. Their stated eligibility assumptions apply only inside each example.

| Case | Expected decision |
| --- | --- |
| Training positively disabled versus enablement unknown | All K rows skipped versus unknown applicability; no unrelated component is substituted |
| K-01 bare heuristic 20 GiB versus 24 GiB, with no qualified peak bound | Unknown; the point is not an admitted fit result |
| K-01 admitted interval [20, 26] GiB versus 24 GiB | Fail/error, "may not fit", using 26 GiB conservatively; no runtime OOM claim |
| K-01 admitted upper bound 20 GiB versus 24 GiB; separately an exact required-state lower bound 26 GiB | Pass for the bounded capacity predicate; fail for the separate required-state contradiction |
| K-02 selected h = 0.15 and C = 24 GiB | Threshold 20.4 GiB: admitted [18, 20] passes; [21, 23] and [20, 22] fail/warning conservatively. Unqualified intervals remain unknown |
| K-03 explicit 16·N state recipe versus different optimizer/sharding; method named "full" without state facts | Apply the state predicate; skipped for the different recipe with K-01 still required; unknown for missing state scope |
| K-04/K-06/K-07 generic feature list versus scoped explicit negative versus qualified joint positive | Unknown, fail and pass respectively, with fixed error severity; positively excluded operations skip |
| K-05 "precomputed reference" with no precomputation/storage/loss-buffer scope | Unknown; no blanket zero-memory pass |
| K-08 managed per-token rate without allocation-control evidence | Unknown; no automatic incompatibility or invented profile |
| K-09 claimed calibration with an admitted mismatching model revision or optimizer; no calibration claim | Fail/warning for the demonstrated mismatch; skipped and explicitly uncalibrated for the latter |

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
| OpenAI | gpt-4.1-mini / gpt-4.1 / gpt-4.1-nano | per 1M training tokens | 5.00 / 25.00 / 1.50 | Historical rate; account/date job eligibility and exact base/derived inference lifecycle remain separate | P6, C1 |

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

**In the historical Azure scenario, a month of hosting exceeds the training charge.** A fine-tuned Azure OpenAI gpt-4.1-mini deployment bills $1.70/hour while deployed, about **$1,241 per month** at 730 hours (P5). Training it on Scenario A's 30M tokens costs $150 (30,000 × $0.005 per 1k global), so one month of hosting is about 8× the training cost. Bedrock custom models need storage plus Provisioned Throughput or on-demand custom-model inference (P4).

The builder must show the post-training serving cost next to the training cost. This is a handoff to #39.

## Recommendation and rationale

- **Memory:** use the component formula, with the gradient dtype, optimiser and fused-loss choice as explicit inputs. Show a range, not a point.
  - Logits are often the largest swing for long sequences and large vocabularies (Qwen3-8B example: 2.5–7.5 GB per sequence).
  - Seek matched calibration before presenting a near-capacity estimate as measured fit. B1–B12 remain comparison inputs until their full configuration and measurement scope match (K-09).
- **Time:** prefer matched measured tokens/s with its exact recipe/hardware scope and residuals. Otherwise retain the conditional FLOP/phase estimate and MFU uncertainty; a nearby family is not calibration.
- **Candidate plans:** consider consumer/L40S adapter or quantized recipes and full-parameter recipes only under their exact documented support and conditional memory accounting. The 16·N example does not imply that every 8B full-parameter plan needs more than one 80 GB GPU.
- **Historical cost tradeoffs:** the displayed small-job amounts illustrate the stated tokens, epochs, rates, regions, dates and omitted costs. They establish no universal cheapest choice or current quote. Compare qualified training cost alongside artifact portability (#30, #33), complete cost coverage and post-training hosting (#39); do not transfer historical throughput to a different configuration.

## Structured artifacts

No CatalogItem, Pricebook or ResourceEstimate files in this draft:
- `training_compute.spec.compute_profile_ref` must reference a `compute_profile` already in the catalog. T2 records merged to `main` in #75 (`ec612eb`) and the later A100/P4de follow-up cover some of what this note needs; the remaining gaps are listed under [Upstream T2 records](#upstream-t2-records). Both documented profiles are valid reference targets within their sourced hardware scope; their presence does not bind the historical prices, pool device memory or establish training fit. This submission remains a research note and does not propose a `training_compute` item.
- Pricebook rates must reference catalog items and versions in this repository. The meter enum has `gpu_hour`, which can represent per-GPU-hour billing such as the Fireworks Dedicated Training API row once matching catalog references exist. The training-token, job-minimum, training-hour and model-month rows need separate meter review; these limitations do not exclude all managed training prices from v1.
- ResourceEstimate has `training.estimated_gpu_hours` but no training-memory metric.

The prices above are recorded with provenance so they can be converted once the missing items and meters exist.

### Upstream T2 records

2026-10-18 supplement: the [T2 hardware/profile capture](../T2-infrastructure/gpu-compute.md#additional-hardware-and-profile-capture-2026-10-18) supplies A100 80GB, RTX 4090 and P4de facts. The [precision follow-up](../T2-infrastructure/gpu-compute.md#precision-follow-up-and-bounded-retrieval-2026-10-18) supplies the complete RTX 4090 catalog proposal; A100/P4de were note-only at that check. The later [A100/P4de assessment](../T2-infrastructure/gpu-compute.md#a100-and-p4de-precision-and-profile-follow-up--2026-10-18) supplies their two scoped proposals after additional native-precision evidence, with joint runtime compatibility still separate. The [S3 identity](../T2-infrastructure/hosting.md#s3-standard-identity-supplement-2026-10-18) adds [`aws-s3-standard`](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/14cd2d0328e6290552d03e32460456cf47e78c95/catalog/proposals/t2-aws-s3-standard.json) (merged in #158), resolving the missing storage identity. Other SKUs, rates, measured training capacity and proposed contract fields remain unresolved. No historical price is silently rebound to a new item/version. Training minimums, storage IOPS requirements and egress costs remain separate unresolved scope; the identity does not establish them.

The original table was checked on 2026-10-16 after #75 merged. Its current availability is corrected by the [2026-10-18 precision intake review](../T2-infrastructure/gpu-compute.md#incomplete-precision-intake-correction-2026-10-18): H100 SXM and MI300X remain sourced note-only inputs and cannot be referenced as current catalog records. These are research proposals and observations, not approved catalog data. Historical prices, measurements and receiving receipts remain unchanged; no earlier receipt is acceptance of this new withdrawal.

| Need in this note | Current research input or catalog record | Notes |
| --- | --- | --- |
| H100 80 GB accelerator (P7–P12 rows) | Note-only `nvidia-h100-sxm`: published 80 GB, CUDA, positive BF16/FP8 evidence and NVLink facts retained in T2 | Incomplete precision semantics prevent a current catalog-reference target; K-01/K-03/K-06 may retain sourced research inputs without treating them as joint compatibility |
| L40S 48 GB accelerator (g6e.xlarge row) | `nvidia-l40s`: `vram_gb` 48, `cuda`, precisions incl. `bf16`, `fp8`, `int4` | Existing catalog-reference target supplies scoped VRAM and native-dtype inputs; joint artifact/engine compatibility still needs its own evidence |
| MI300X accelerator | Note-only `amd-mi300x`: published up-to 192 GB and ROCm evidence retained in T2, with the source GB/GiB distinction | No current catalog-reference target while precision scope remains unresolved; not priced in this note |
| `aws g6e.xlarge` (1× L40S, $1.861/h, P7) | `compute_profile` `aws-ec2-g6e-xlarge-us-east-1`: `hosting_ref` `aws-ec2`, `accelerator_ref` `nvidia-l40s`, count 1, region `us-east-1` | A valid `compute_profile_ref` target. The T2 pricebook has no rate for it yet |
| A100 80 GB hardware identity | [`nvidia-a100-80gb` / `2026-10-18`](../../catalog/proposals/t2-compute-nvidia-a100-80gb-2026-10-18.json) | Common full-device PCIe/SXM facts; the T2 follow-up supplies six positive native precisions and a scoped native-FP8 exclusion. No joint runtime or historical training-run equivalence is established |
| AWS P4de profile | [`aws-ec2-p4de-24xlarge-us-east-1` / `2026-10-18`](../../catalog/proposals/t2-compute-aws-p4de-24xlarge-us-east-1-2026-10-18.json) | Existing profile retains its A100 reference and eight separate devices; no historical rate is automatically bound to this new version and no pooled allocation or training fit is established |
| AWS and RunPod hosting | `hosting_platform` `aws-ec2` (`us-east-1`), `runpod-pods`; also `runpod-serverless`, `modal-functions`, `huggingface-endpoints-aws` | Hosting records exist for two of the self-run providers priced here |
| RTX 4090 hardware identity | [`nvidia-geforce-rtx-4090` / `2026-10-18`](../../catalog/proposals/t2-compute-nvidia-geforce-rtx-4090-2026-10-18.json) | Complete hardware proposal; no matching RunPod profile, current rate or training-run equivalence is established |
| Checkpoint storage (`storage_ref`) | `storage` `aws-ebs-gp3` (block, `aws-ec2`), `cloudflare-r2-standard` (object), `modal-volumes-v1` (file), `runpod-network-standard-us-ks-2` (file, `runpod-pods`, US-KS-2) | `aws-s3-standard` (object; no EC2 hosting dependency) was added in #158; P13 remains historical note-only pricing, not a rate bound to this item/version |

| Gap | Kind | Route |
| --- | --- | --- |
| `compute_profile` for `p5.48xlarge`, `a3-highgpu-8g`, `Standard_ND96isr_H100_v5`, Lambda, RunPod and CoreWeave SKUs | Missing record. Required spec fields: `hosting_ref`, `cpu_cores`, `ram_gb`, `region`. The later P4de proposal supplies its CPU/RAM/region and companion A100 reference; those two records no longer belong to this missing-record list. Other price evidence here was not collected for CPU/RAM, and P11 states no RunPod region; those fields still need scoped sources | #10 owns profiles. This note supplies the SKU and price list only |
| Accelerator records for H100 SXM and MI300X | Note-only while precision coverage and native/storage/compute semantics remain unresolved. A100 80GB is now supplied by the separate scoped T2 follow-up. RTX 4090 has `nvidia-geforce-rtx-4090` version `2026-10-18`; B2/B3 remain historical measurements, not newly calibrated to this catalog version | #10 and #40, with #11 for exact engine/artifact dtype scope |
| `hosting_platform` for Google Cloud, Azure, Lambda and CoreWeave | Missing record | #9 |
| Peak dense TFLOP/s per accelerator, needed by the time formula | Unresolved field: `spec_accelerator` has `vram_gb` and `precisions` but no throughput field | Contract proposal through #40, with #10 |
| Training-token, job-minimum, training-hour and model-storage meters; `compute_profile_ref` optional for managed services | Unresolved meters and field (v1 contract) | #40 and #39 |
| `training.estimated_peak_per_device_vram_gb` | Unresolved ResourceEstimate metric | #40, with #10 |
| Whether a multi-GPU instance-hour price maps to the `gpu_hour` meter per GPU or per instance | Unresolved pricing semantics | #39 |
| Training memory, time and throughput for the existing profiles | Training-specific estimates; T2's `gpu-compute.md` leaves these to #31 and none of its inference estimates apply | #31 (this note's estimator); matched calibration remains follow-up and B1–B12 are comparison inputs |

## Open questions and handoffs

| Question | Follow-up issue / owner |
| --- | --- |
| Accelerator/profile records still missing for the SKUs priced here, including note-only H100 SXM/MI300X and profiles except `aws-ec2-g6e-xlarge-us-east-1` and `aws-ec2-p4de-24xlarge-us-east-1`; a peak dense TFLOP/s field. H100/MI300X hardware observations remain research inputs while their precision/reference semantics are reviewed. See Upstream T2 records | #10 · @Mattycodes69, @appletechie; #40 and #11 for scoped precision semantics |
| Hosting platform records for Google Cloud, Azure, Lambda and CoreWeave. `aws-ec2` and `runpod-pods` already exist | #9 · @Mattycodes69 |
| Pricebook meters for `training_tokens_1m`, `training_tokens_1k`, `training_hour`, `job_minimum` and `model_storage_month`; a ResourceEstimate metric `training.estimated_peak_per_device_vram_gb`; `compute_profile_ref` optional for managed services | #40 · @tynamite |
| Price normalisation: per-1k vs per-1M tokens, epochs and validation tokens, job minimums, and post-training hosting shown next to training cost. The bounded quantity/unit intake is accepted with the constraints recorded below; new meters, current quote binding and complete aggregation remain separate | #39 · @PUSHINGSQUARES |
| Matched phase timings, allocation lifetimes and scoped rates for the distillation/GRPO accounting method above; no numeric calibration yet | #31 · @appletechie |
| Run a 20-step dry run to calibrate the Qwen3-8B worked example (no published measurement for it) | #31 · @appletechie |
| Exact methods/framework configuration consumed from #30, with the actual H5 boundary below | #30 · @zwright8, @appletechie; delivered #375/#380 |
| Current rate eligibility and any future freshness-policy revision; no TTL is currently adopted | #41 · @tynamite, with #39 for cost use |

The historical requests above are narrowed by the actual receiving dispositions below. Only their stated boundaries are accepted; the other questions remain open.

### Bounded receiving dispositions — 2026-10-18

**Hardware availability, #10 → #31.** The later [actual receiving decision 6250287107](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10#issuecomment-6250287107), recorded at 13:07:48 UTC, accepts the current L40S, RTX 4090 and A100 hardware inputs and the G6e/P4de profiles within their sourced scope. It explicitly retains H100 SXM and MI300X as note-only inputs. This is a new bounded decision following the precision withdrawal, not a retrospective expansion of an earlier receipt. It does not rebind historical rates, pool device memory, establish training fit or make inference measurements training calibrations. The upstream table and two profile references above retain those limits.

**Cost quantities and units, #31 → #39.** The [actual receiving decision 6251932295](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/39#issuecomment-6251932295), recorded at 15:52:51 UTC, accepts this note's bounded quantity, unit and uncertainty input after reading the complete training note and the applicable unit, W5, uncertainty and coverage sections of the cost note. Its exact source basis is accepted main `4f1c22bac91783a00384b3037bb64b040250c072`, training-note blob `76d4da4a2ffd60d36d20dafc98007102c06bedd0` and cost-note blob `6405fd07b1465178c82bcfeab18d13990ad2836e`. The two later profile-sentence corrections do not change those cost equations or historical data.

The receiver independently recomputed all 15 displayed historical scenario amounts and the three W5 synthetic cases, including the job-minimum top-up, separate recurring hosting and explicitly partial first-period subtotals. The receiving decision requires exact provider/model/method and tokenization/packing scopes; distinct per-1K/per-1M divisors; provider-specific evaluation billing; minimum charges applied once; instance-hour versus GPU-hour dimensional accounting; disjoint GRPO/distillation allocation lifetimes; and separate one-off and recurring periods. It preserves the explicitly different 720-hour and 730-hour assumptions. Missing rates, capacity, entitlement, overhead or timing remain unknown and unpriced, never zero or a budget pass.

The linked decision records the receiver's 2026-10-18 primary-document checks for Together and Microsoft, the exact 16-row Azure public pricing response and its SHA-256, and the note's pinned TRL phase documentation. Those checks establish only their stated billing and phase semantics. They do not refresh every historical quote, supply an eligible account, measure training performance or establish distillation rights. Existing benchmark conditions, dates and evidence grades are unchanged.

Both linked decisions are explicitly attributed to the actual in-session engineering reviewers acting under the user's delegated project authority through the CompleteDotTech account; neither is a statement by an absent named co-assignee. The #39 intake adopts no new Pricebook meter or frozen field, supplies no #42 cost-snapshot acceptance, and does not complete #31 or #39. The existing #30/#40/#41 rights, contract, lifecycle, freshness, currency/region and aggregation decisions retain their owners. No account, model, training, payment or hardware operation was performed for this receiving review.

**Hosting/storage, #9 → #31.** The [original receiving decision 6230482274](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/9#issuecomment-6230482274) accepts host/storage ID reuse with training sizing, time and cost retained by #31. The later [actual delegated review 5563649987](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/355#pullrequestreview-5563649987) accepts that interface against published hosting source `f007736206697f58c0d28cf24dae94598f3e8a07`, blob `1e552281a2d844eb9fe28c37beb879b890c06e42`, delivered in signed main `26a82d0aba1fa9f382b143089434f65fdd4c1f83`. It preserves the four Google Cloud, Azure, Lambda and CoreWeave host-record requests. The [delivery receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/9#issuecomment-6251909151) confirms its bounded source/review scope; no training fit, current rate, provisioned capacity or customer entitlement is inherited.

**Framework/configuration, #30 → #31.** The [actual H5 receiving decision 6253126908](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/31#issuecomment-6253126908) reviewed producer `b59cbb87bf0ac670bb20b5ce34600c2f29147c7d`, framework blob `f4ff09bfe2274d4854721bf1ac4f942a1c93457d`, against this note's earlier exact `e20e49ce3e078847e37ceeffb2eb2cdf7f2885cf` consumer. It accepts exact trainer/adapter/backend/dependency identities, objective/update/quantizer, topology/strategy, precision, batch/accumulation, sequence/packing and loss as research inputs. #375 delivered the framework decision in `d116296757f66c3e2fd984174b120d88b147b07d`; #380 subsequently corrected two unrelated offering-scope rows, leaving this H5 interface intact. The current accepted framework blob at this amendment's `cceaa676` base is `c3cfc458fcd9272fc0b4f969ccef131f7eae7e07`. These are distinct source and receipt identities, not a claim that a named co-assignee accepted this new compute revision.

**Shared configuration/quantity boundary, #40 → #31.** The [actual receiving decision 6254657215](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/31#issuecomment-6254657215) accepts CD-1 and relevant CD-6 bindings from producer `45b20960cbc4652fb3341c977a025821c96595f9`, blob `375506eea95bd7fc30883c0e4f2a2f5496f77cfd`, against unchanged compute blob `e20e49ce` at `cceaa676`. It does not admit CD-12 attestations or adopt the K rules wholesale. Preserve explicit unknown/withheld configuration and quantities, per-device capacity, exact operation/device/host bindings and separate allocation phases. Training stays outside the serving-mode calculation; managed services and rented training compute that receive data remain D-R6 destinations. Lawful-basis assessment remains with #32 and the responsible dataset/source assessor. Location evidence is separate from organization jurisdiction and preferences.

These receipts retain their actual reviewer attribution, direction, source revisions and limitations. The estimator/rule corrections here preserve the accepted #39 historical quantities and phase-allocation interface; no new billing meter, measurement, numerical calibration, eligibility, rights grant or final ruleset is created. The current source amendment still requires its own independent review and delivered-main receipt.

## Original research-completion criteria

This maps the nine literal #31 criteria without adding implementation or actual-training gates to a research deliverable. Delivery and final source/receiving review are pending for this amendment until linked from its PR and issue. Named selection-specific evidence and versioned adoption questions remain follow-up work, not invented completed observations.

| Original criterion | Concrete record and remaining review boundary |
| --- | --- |
| Estimation method with assumptions and uncertainty | Conditional component/state equations, full worked example, phase/allocation time accounting, admitted conservative bounds and K-01/K-02/K-09 distinctions |
| Priced scenarios with provenance | Dated P1–P13 scope and the unchanged Scenario A/B quantities, rates and conditions; historical illustrations remain separate from current quote eligibility |
| Decision record merged at `research/T5-training-fine-tuning/training-compute.md` following the research method | Existing record is merged; this exact 0.2.0 amendment needs independent source review, ordinary PR delivery and accepted-main readback |
| Candidate set covers the relevant deployment modes (API / managed / self-hosted) or states why a mode does not apply | Provider-operated shared and dedicated/GPU-time offerings plus self-run profiles; billing does not choose mode and training is excluded from serving-mode derivation |
| Comparison fields defined with type, unit, and evidence requirement | Comparison table, optional/required catalog roles, explicit note-only objective/update/quantizer inputs and participant/boundary table |
| Compatibility rules and warnings use the shared format from #40; verified rules are separated from hypotheses | K-01–K-09 stable IDs, participants, applicability, positive predicates, four existing outcomes, fixed severity, admission, explanation/remediation and synthetic cases; 15% remains proposed policy, final #40 executable adoption separate |
| Every factual or numeric claim cites a primary source with access date (and version / region / currency where relevant) | Dated E/B/P sources and C1 lifecycle readback; published versus derived quantities, corrected claim-level grades, exact source scopes and historical quote boundaries remain explicit |
| Each handoff listed under Dependencies is confirmed by the consuming issue's owner (link the comment or PR review) | Actual #9/#10/#30 input decisions and #31→#39 quantity/unit decision linked above; no missing co-assignee response or whole-consumer completion is inferred. This amended interface requires its own review of preserved boundaries |
| Open questions recorded with a named follow-up owner | Existing infrastructure breadth, rate/meter/field adoption, matched training calibration and selected-configuration questions retain their named owners; no actual training run or new quote is fabricated |
