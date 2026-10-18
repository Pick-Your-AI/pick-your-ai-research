# GPU / Compute: inference capacity and provisionable profiles

Issue: [#10](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10) · Contract: 1.0.0 · Kinds: `accelerator`, `compute_profile`
Status: decision record merged in PR #75; follow-up rule proposal and remaining handoffs pending · Vendor-source dates: per evidence section · Method/receipt continuation: 2026-10-18

## User decision

Which accelerator, and how many, can serve a particular version of a model at the requested context and load? Keep an accelerator's physical specifications separate from a provisionable host SKU. A memory calculation is a capacity screen; passing it does not establish model quality, engine support, an SLO, regional stock, or a reservation.

The current default-branch contract, following merged PR #44, is authoritative. This note contributes facts and proposed rules without changing v1. Live GitHub assignees re-read on 2026-10-18: @Mattycodes69 and @appletechie. PR #75 merged at `ec612eb14edaf63cc9caca2ab655d053c9114dd4`; merge does not establish every consuming-owner acceptance.

Deployment-mode coverage is a research decision:

| Mode | Treatment |
| --- | --- |
| API | Omit customer-owned GPU and local engine when using only a hosted model API, consistent with the [component guide](../../contracts/v1/docs/COMPONENTS.md). Provider hardware and its hidden scheduling cannot be inferred from an API model name; API behavior belongs to #5. |
| Managed | A managed component with a user-chosen instance type is in scope for sizing. Provider-operated shared or opaque capacity skips local sizing; its quota and capacity guarantees remain unknown service inputs. Runpod's selectable Pods inform candidates, but incomplete profile fields stay in this note. |
| Self-hosted / hybrid | Use hardware catalog plus host SKU, exact artifact, engine version and workload. #3 accepted operator/capacity classification in the owner review below: a customer-operated cloud engine is self-hosted. Evaluate each component of a hybrid build separately; build-level hybrid mode must not skip its local checks. |

CPU inference and edge inference are in scope for comparisons and unknown handling. This bounded first intake supplies discrete datacenter GPUs and one cloud profile. It does not claim exhaustive CPU/NPU/TPU/consumer GPU coverage. Unified memory and CPU RAM must not be relabelled dedicated VRAM; no CPU/edge CatalogItem is fabricated to fill required fields. #10/@Mattycodes69 and #40/@tynamite must decide how v1 represents shared memory and accelerator partitions before complete edge proposals. #11's CPU/Metal candidates establish possible runtime paths, not capacity guarantees.

Training memory, optimizer state, gradients, training time and training throughput are owned by #31. #31 reuses these accelerator identities; none of the inference estimates below are training estimates.

## Candidate options

All numeric hardware entries in this table are **published** vendor specifications, not project measurements. Bandwidth is peak device-memory bandwidth, in decimal GB/s; it is not application throughput. The chosen set covers a PCIe GPU, a scale-up NVIDIA module and an AMD module. The catalog versions `2026-10-16` are research snapshots, not hardware revision identifiers.

| Accelerator ID | Vendor / physical variant | Memory | Peak bandwidth | Native arithmetic precision subset in v1 | Backend / interconnect and limit | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| `nvidia-l40s` | NVIDIA L40S, Ada, PCIe | 48 GB GDDR6 ECC | 864 GB/s | fp32, tf32, bf16, fp16, fp8, int8, int4 | CUDA; PCIe Gen4 x16, 64 GB/s bidirectional; no NVLink and no MIG | C01, C04 |
| `nvidia-h100-sxm` | NVIDIA H100 SXM, Hopper; distinct from PCIe/NVL | 80 GB | 3,350 GB/s | fp32, tf32, bf16, fp16, fp8, int8 | CUDA; NVLink up to 900 GB/s; actual fabric depends on server topology. Up to 700 W configurable TDP | C02, C04 |
| `amd-mi300x` | AMD Instinct MI300X OAM, CDNA3 | Up to 192 GB HBM3 | 5,300 GB/s maximum theoretical | fp32, tf32, bf16, fp16, fp8, int8 | ROCm; seven Infinity Fabric links, each 128 GB/s; PCIe Gen5 x16 host link. Maximum board power 750 W | C03, C05 |

Arithmetic precision support is not a promise that an arbitrary quantized checkpoint runs. A checkpoint's storage format, quantization algorithm, scale representation, compute dtype and KV dtype are different inputs. vLLM 0.10.2's table, for example, lists FP8 W8A8 on Ada/Hopper/AMD GPU but AWQ/GPTQ as unsupported on AMD GPU (C12). Keep this joint engine/artifact/hardware evidence with #11. No `int4` claim is inferred for H100 or MI300X from another generation's table.

That v0.10.2 table is historical. The separately inspected v0.31.0 table retains these particular FP8 W8A8 and AMD AWQ/GPTQ entries (C20); neither table proves every architecture, weight layout, driver or plugin combination. Current engine proposals use #11's v0.31.0 evidence, while the older benchmark below retains its own engine version. AMD's datasheet labels capacity up to **192 GB**, while its ROCm 6.3 hardware table labels **192 GiB** (C03, C22). #40's review confirms decimal GB (10^9 bytes) is canonical; retain each source value/unit and normalize before comparing. These differently labelled published capacities do not establish allocatable/free bytes, so the catalog retains its datasheet source and runtime allocation stays unknown.

### Provisionable compute profiles

| Profile / snapshot | Linked host / accelerator | Published allocation and normalization | Capacity limitations | Evidence |
| --- | --- | --- | --- | --- |
| `aws-ec2-g6e-xlarge-us-east-1` / `2026-10-16` | `aws-ec2` / `nvidia-l40s`, one GPU | Default 2 CPU cores, 4 vCPUs, 2 threads/core; 32 GiB host RAM = **34.359738368 decimal GB** (project unit conversion); 250 GB local disk. `cpu_cores=2` means default cores, not vCPUs | AWS technical table reports 44 GiB GPU memory while marketing reports 48 GB. Treat 44 GiB as a published rounded allocation, not guaranteed free memory. Measure usable bytes before deployment. Network “up to 20 Gbps” is an upper bound, so no unconditional `network_gbps` value is submitted. | C06–C09 |
| Runpod L40S Pod, incomplete profile | `runpod-pods` / `nvidia-l40s` candidate only | Official price table advertises 48 GB VRAM, 94 GB RAM, 16 vCPUs | Region and physical CPU cores are not pinned by that table; cannot satisfy required `region` and `cpu_cores`. No profile JSON; priced conditions remain #9's responsibility | C10; [hosting note](hosting.md) |
| Runpod H100 SXM Pod, incomplete profile | `runpod-pods` / `nvidia-h100-sxm` candidate only | Official price table advertises 80 GB VRAM, 125 GB RAM, 20 vCPUs | Same required-field gaps; no promise of stock, exact topology or tenancy from the public table | C10; [hosting note](hosting.md) |

The AWS profile is a documented offer in `us-east-1`, not a live account capacity check. The regional launch source is historical and current account quota, Availability Zone offering, driver-visible memory, tenancy and capacity remain unknown. Recheck them during #37's deployment research; no instance was provisioned. RAM, free host memory, disk and loading peaks require separate checks; enough VRAM alone is insufficient.

The H100 SXM and MI300X rows remain sourced research candidates. Their incomplete
precision lists are now [note-only](#incomplete-precision-intake-correction-2026-10-18),
so neither identity is a current catalog-reference target. This changes intake
eligibility, not the published hardware observations above.

The current vLLM optimization guide recommends at least `2 + N` physical CPU cores for its described single-server layout (C21). With one GPU, that is three cores, above this profile's documented two default cores. This is a published performance warning for that layout, not proof the VM cannot execute inference. It reinforces why this record is a provisionable candidate rather than a validated SLO recommendation; #11/#37 must review the selected process/CPU configuration.

## Comparison fields

The following is the normalized comparison specification. It does not add fields to the frozen schema. Omitted optional JSON properties mean “not documented in this proposal”, never zero or false.

| Field / JSON pointer | Type and unit | Candidate finding | Evidence ID | Conditions / unknowns |
| --- | --- | --- | --- | --- |
| `/id`, `/version`, `/kind` | string identity and research snapshot | Separate accelerator and compute_profile records | C01–C09; contract | One version per ID under current submission policy; changing hardware form factor needs another ID |
| `/spec/accelerator_type`, `/spec/vendor`, `/spec/model_name` | enum/string/string | GPU, vendor, exact variant as above | C01–C03 | Never substitute SXM for NVL/PCIe |
| `/spec/vram_gb` | number, advertised GB per device | 48 / 80 / 192 | C01–C03 | Capacity is advertised, not free/allocatable bytes; runtime allocation is a separate finding |
| Memory bandwidth (note only) | number, decimal GB/s; peak/theoretical qualifier | 864 / 3350 / 5300 | C01–C03 | No canonical spec property; proposed #40 field below |
| `/spec/backends` | enum array | CUDA / ROCm | C04, C05 | Version/OS/driver support still required from #11 |
| `/spec/precisions` | enum array | Native arithmetic subset above | C01–C03 | No quantization algorithm or quality claim |
| `/spec/interconnect` | enum | pcie / nvlink / proprietary | C01–C03 | Single enum is lossy for host and scale-up links; note preserves both |
| `/spec/rated_power_w` | number, W | Maximum rating 350 / 700 / 750 | C01–C03 | Not measured draw, TCO, system wall power or cooling requirement |
| `/spec/hosting_ref`, `/spec/accelerator_ref` | local catalog IDs | aws-ec2 / nvidia-l40s | C06–C09 | Resolved locally; v1 spec references lack version, so pin catalog snapshot |
| `/spec/accelerator_count` | integer devices per instance | 1 | C06 | Selection counts must agree; do not multiply both counts twice |
| `/spec/cpu_cores`, `/spec/ram_gb`, `/spec/disk_gb` | integer default cores; decimal GB; decimal GB | 2; 34.359738368; 250 | C06, C07 | CPU core interpretation explicit; source RAM in GiB; local disk not persistent storage |
| `/spec/region` | provider region ID | us-east-1 | C08, C09 | Published offering, historical launch plus AWS mapping; availability now unknown |
| Weight tensor count/dtype, artifact revision, quantization algorithm/group size/scales | structured evidence in note; count, bits/element, bytes | Exact artifact metadata preferred | C11, C13 | Parameter marketing labels alone are insufficient; metadata not modeled by v1 |
| Layers, KV heads, head dimension, cache dtype and layout | positive integers / dtype / bytes | Example L=28, Hkv=4, D=128, BF16=2 bytes | C11, C14 | Architecture-specific; attention head count is not KV-head count |
| Requested context + reserved output, admitted sequences, token batch | integers, tokens and sequences | Explicit scenario inputs below | C11, C15; workload assumptions | Workload peak demand differs from engine admission and prefill token batch; queued requests do not all hold device KV |
| Runtime/adapter/activation memory and headroom | bytes and fraction; bounded project estimates | Explicit scenario inputs below | C13–C15; estimates | No universal overhead or headroom default established |
| Sizing output / ResourceEstimate metrics | decimal strings, GB; integer planned count in note | Total range and peak per device | C11–C15; calculation | Real build/selection versions needed before publishing build-bound ResourceEstimate |
| Throughput / latency | tokens/s; TTFT/ITL/end-to-end ms, distribution and test conditions | Published comparison only; new profile unknown | C16 | No error range invented; no numeric L40S SLO established |
| Provenance `/provenance/*` | public URL, RFC3339 date, verification enum, notes | Source-to-field mappings in each proposal | All cited sources | Source-checked publisher facts remain `unverified` under the adopted #41 policy; checking alone is not independent reproduction |

## Evidence

Access date for every entry: **2026-10-16**. Prices and currency are not copied into this package. Non-price hardware facts are region-independent unless a profile region is specified. Evidence classification uses the interim policy in `docs/RESEARCH_METHOD.md`: **Primary documentation**, **Vendor claim**, **Independent measurement**, **Estimate**. “Published”/“measured” describe the number; a vendor-published measurement retains the **Vendor claim** grade unless independently reproduced. No independent measurement or project GPU run is claimed here.

| ID | Publisher and URL | Access date | Version / region | Evidence grade | Limitations / reuse terms |
| --- | --- | --- | --- | --- | --- |
| C01 | NVIDIA [L40S full specifications](https://www.nvidia.com/en-us/data-center/l40s/) | 2026-10-16 | L40S, full-spec table | Primary documentation; peak rates are vendor claims | Physical specifications, no engine guarantees. Link and factual paraphrase only; rights unresolved under C18 |
| C02 | NVIDIA [H100 product specifications](https://www.nvidia.com/en-us/data-center/h100/) | 2026-10-16 | H100 SXM column only | Primary documentation; theoretical performance vendor claim | Do not combine with H100 NVL column. Terms C18 |
| C03 | AMD [MI300X accelerator datasheet](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf), pp. 1–2 | 2026-10-16 | Copyright 2025; OAM | Primary documentation; peak bandwidth vendor claim | Up-to specifications, not sustained performance; no PDF copy stored. Terms C19 |
| C04 | NVIDIA [CUDA GPU compute capability](https://developer.nvidia.com/cuda/gpus) | 2026-10-16 | Ada 8.9 / Hopper 9.0 mapping | Primary documentation | Hardware support pointer, not installed driver or full application validation |
| C05 | AMD [ROCm 6.3.0 system requirements](https://rocm.docs.amd.com/projects/install-on-linux/en/docs-6.3.0/reference/system-requirements.html) and [compatibility matrix](https://rocm.docs.amd.com/en/docs-6.3.0/compatibility/compatibility-matrix.html) | 2026-10-16 | ROCm 6.3.0, MI300X gfx942 | Primary documentation | System-requirements GPU row directly inspected; matrix retrieval remains rate-limited. No detailed OS/kernel/driver combination inferred |
| C06 | AWS [G6e product details](https://aws.amazon.com/ec2/instance-types/g6e/) and [accelerated instance technical table](https://docs.aws.amazon.com/ec2/latest/instancetypes/ac.html) | 2026-10-16 | g6e.xlarge | Primary documentation | Technical table directly inspected in continuation audit; its 44 GiB GPU figure is rounded and differs in unit from marketing; runtime bytes unknown |
| C07 | AWS [supported CPU options](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/cpu-options-supported-instances-values.html) | 2026-10-16 | g6e.xlarge default, 2 cores / 4 vCPU | Primary documentation | Documented instance CPU allocation, not dedicated physical-host tenancy |
| C08 | AWS [G6e general availability](https://aws.amazon.com/about-aws/whats-new/2024/08/amazon-ec2-g6e-instances/) | 2026-10-16 | Published 2024-08-15; N. Virginia | Primary documentation | Historical offering; not today's stock/quota |
| C09 | AWS [Regions and Availability Zones](https://docs.aws.amazon.com/global-infrastructure/latest/regions/aws-regions.html) | 2026-10-16 | US East (N. Virginia) = us-east-1 | Primary documentation | ID mapping only, not compute availability |
| C10 | Runpod [GPU pricing](https://www.runpod.io/pricing) | 2026-10-16 | Public Pods table; dated 2026-10-08 by publisher | Primary documentation | No exact region/core topology; table is not a provisionable-region guarantee; price ownership #9 |
| C11 | Qwen [version-pinned config](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct/blob/d1e200fcf95ef0d4326873ddf63e5562d5f1fdbb/config.json), [pinned tensor index](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct/resolve/d1e200fcf95ef0d4326873ddf63e5562d5f1fdbb/model.safetensors.index.json), [index upload commit](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct/commit/d1e200fcf95ef0d4326873ddf63e5562d5f1fdbb) | 2026-10-16 | Qwen2.5-7B-Instruct d1e200fcf95ef0d4326873ddf63e5562d5f1fdbb | Primary documentation | Immutable index directly fetched in continuation audit: total_size 15,231,233,024 bytes. No weights downloaded. License/redistribution confirmation stays with #6/#41 |
| C12 | vLLM [quantization hardware matrix](https://docs.vllm.ai/en/v0.10.2/features/quantization/index.html) | 2026-10-16 | v0.10.2 | Primary documentation | Version-specific implementation support, not every architecture/artifact combination |
| C13 | Hu et al. [LoRA paper](https://arxiv.org/abs/2106.09685) | 2026-10-16 | arXiv 2106.09685 | Primary documentation | Low-rank decomposition supports parameter-count derivation; not a measurement of this example |
| C14 | Hugging Face [generation cache guide](https://huggingface.co/docs/transformers/v4.46.0/en/kv_cache) | 2026-10-16 | Transformers 4.46.0 | Primary documentation | Cache strategies and layout; do not transfer full-attention formula to MLA/recurrent/hybrid models without derivation |
| C15 | vLLM [optimization and tuning](https://docs.vllm.ai/en/v0.10.2/configuration/optimization.html) | 2026-10-16 | v0.10.2 V1 | Primary documentation | Concurrency/KV/preemption, token batching and parallelism; explanatory basis only, no estimate calibrated from defaults |
| C16 | Qwen [Qwen2.5 speed benchmark](https://qwen.readthedocs.io/en/v2.5/benchmark/speed_benchmark.html) | 2026-10-16 | Historical A100 80GB benchmark, versions below | Vendor claim; publisher-measured | No confidence intervals, pinned model artifact, warmup or full timing decomposition; unsuitable for direct L40S extrapolation |
| C17 | Contract [ResourceEstimate schema](../../contracts/v1/schemas/resource-estimate.schema.json), [component guide](../../contracts/v1/docs/COMPONENTS.md) | 2026-10-16 | Imported v1 / main following #44 | Project contract, not vendor evidence | Governs fields and units, not numeric accuracy |
| C18 | NVIDIA [site terms](https://www.nvidia.com/en-eu/about-nvidia/terms-of-service/) | 2026-10-16 | Current terms, sections 2–4 | Primary documentation | Restrictions on copying/automation; do not treat public access as permission to mirror. #41 must determine permitted catalog fact reuse; no bulk corpus or images copied |
| C19 | AMD [terms of use / copyright](https://www.amd.com/en/legal/copyright.html) | 2026-10-16 | Current site terms | Primary documentation | Informational-use and republication restrictions; reuse permission unclear for product catalog, #41 follow-up; no source PDF redistributed |
| C20 | vLLM [release-pinned quantization matrix](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/features/quantization/README.md) | 2026-10-16 | v0.31.0 | Primary documentation | Current support-table entries are scoped implementation claims, not independent joint-runtime verification; #11 retains installation conflicts |
| C21 | vLLM [release-pinned optimization guide](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/configuration/optimization.md) | 2026-10-16 | v0.31.0 | Primary documentation; performance guidance is vendor claim | Cache preallocation, TP/PP/DP/MoE distinctions and CPU-process recommendation; no L40S throughput calibration |
| C22 | AMD [ROCm hardware specifications](https://rocm.docs.amd.com/en/docs-6.3.0/reference/gpu-arch-specs.html) | 2026-10-16 | ROCm 6.3.0, dated 2024-12-03 | Primary documentation | MI300X CDNA3/gfx942 row labels memory 192 GiB, unlike datasheet GB; keep conflict and runtime allocation unknown |

### Owner review and interim evidence policy

Primary project decision source: [#3/#40/#41 owner review on PR #75](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75#pullrequestreview-5550616927), @tynamite, reviewed head `9e66622a4b2698a9305274f05da9c15ae5d90b8c`, submitted 2026-10-16; accessed 2026-10-17. This is an owner position, not independently measured product evidence or an approved contract revision.

- Version-pinned support/specification facts do not expire merely with time; recheck when the selected version or source changes. Current prices, availability, regions, quotas and terms remain dated **as of** observations; no TTL is adopted.
- Resolve conflicts centrally in this order: normalize units/names; exclude out-of-scope claims and prefer the most specific coverage; use selected-version evidence for pinned facts or latest effective date for current facts; apply fact-specific authority. A publisher controls its product requirements, and its explicit requirement/limitation wins over its capability listing. Matching measurements outrank estimates, which outrank vendor claims for fit/performance. Equal-ranked numbers retain median/spread and decide conservatively in the rule's direction; opposite equally ranked yes/no claims or no eligible evidence remain `unknown` for a reproducible test. Preserve the losing claims and deciding step.
- Checked, eligible versioned documentation can yield a support `pass` while the compatibility result is **unverified** until independently reproduced. Source checking alone leaves the four compute CatalogItems' provenance `unverified` under the adopted #41 policy. This follow-up corrects the earlier stronger label without changing the cited facts, source check dates or schema.
- Short paraphrases with links remain acceptable interim reuse; automated retrieval/bulk copying awaits #41/#60's per-source rights inventory.

The review accepts the capacity-interval and memory-pool proposals into CD-2/CD-3 review and the shared memory-fit/joint-support families. It leaves default headroom with #10, and the proposed contract fields unimplemented. The suggested 20% reserve / 4 GiB runtime is not adopted or calibrated by this follow-up.

## Reproducible inference sizing method

Estimator proposal: `t2-dense-kv-memory`, version `0.2.0`, uncalibrated **Estimate**. Reproduce the worked calculations with `python research/T2-infrastructure/compute/sizing_examples.py`. It performs arithmetic only; it does not load weights, benchmark a runtime, contact a cloud or provision infrastructure.

### Inputs and units

Use bytes internally; decimal GB = bytes / 10^9, GiB = bytes / 2^30. Preserve the source unit and conversion. Pin model artifact revision and exact tensor metadata; engine version/build, attention and quantization implementation; accelerator variant; driver/runtime and host; workload/context policy; adapters and parallelism topology. Count all resident weights, including inactive MoE experts unless a particular offload strategy is evidenced. “Active parameters” can inform compute but cannot substitute resident parameter count for memory.

For an unpacked checkpoint, sum tensor `numel × stored_bytes_per_element`; use exact published tensor storage bytes only if runtime dtype/layout remains the same. For a proposed quantization, estimate `sum(ceil(N_i × bits_i / 8)) + scales + zeros + group metadata + alignment + unquantized tensors + runtime repacking`. Include decompression workspace separately. Nominal `P × 0.5` is only a lower-bound INT4 payload approximation, never a checkpoint's full resident memory. Quantization does not automatically quantize KV or guarantee acceptable quality (C11, C12).

For decoder-only dense full-attention KV cache, the **derived** byte estimate is:

```text
T_i = prompt tokens + reserved/generated output tokens for active sequence i
K = 2 × L × Hkv × D × bytes_per_KV_element × sum_i(round_up(T_i, cache_block_tokens))
M_live(device) = W_device + K_device + adapters_device + activations_peak_device
                 + runtime_workspace_device + communication_buffers_device
M_required(device) = M_live(device) / (1 - headroom_fraction)
M_total = sum over devices of M_required(device)
```

The factor 2 is keys plus values. Use KV heads for GQA/MQA, not query heads; obtain head dimension from explicit architecture metadata or justify `hidden_size / attention_heads`. Count beams and parallel sampled continuations as separate active sequences unless actual cache sharing is evidenced. Round to the engine's real cache block size. Do not assume prefix sharing or sliding-window eviction savings in an initial conservative screen. Sliding-window, encoder-decoder, multimodal, MLA, recurrent and hybrid attention need a model-specific cache derivation; missing architecture/cache data gives `unknown`, not an invented constant (C11, C14).

Batch size is the number of sequences processed together; prefill token batch and decode sequence batch differ. Workload peak concurrency is requests-in-flight **demand**; engine launch options determine **admitted sequences** with resident KV. Use the admission limit for KV sizing, counting beams and parallel samples separately. If admission is unknown, size at peak demand and record the assumption; if both are missing, demand is unknown. Requests above the limit queue and affect latency rather than necessarily holding device KV. Use `sum_i(T_i)` for the worst admitted envelope rather than average prompt length; model every replica independently. #81 proposes `peak_concurrency` and engine-build launch options; these are not new fields in frozen v1. Chunked prefill changes peak activations and scheduling (C15).

Runtime overhead includes allocator fragmentation, CUDA/ROCm context, graph capture, kernels, temporary attention/GEMM buffers, logits, quantization repacking and communication. Measure peak after loading, graph capture, longest permitted prefill and mixed-load steady state when a later authorized benchmark exists. A universal percent cannot stand in for these terms. Here the explicit overhead bracket is a scenario assumption, and headroom is unused capacity outside that bracket. Do not add another blanket overhead percentage to the same memory. The disposition below recommends explicit scenario reserve instead of a universal numeric default; co-owner review remains required.

Reconcile this formula with the engine's configured memory pool. vLLM preallocates cache using `gpu_memory_utilization` (C21): a utilization budget of `u × device_capacity` already leaves `(1-u)` outside that pool. If it is the same reserve as headroom `h`, compare `M_live <= (1-h) × capacity` once; do not divide by `(1-h)` and compare against that already-reduced budget again. A larger preallocated pool is not a second copy of the demand-derived KV bytes. Preserve demand, allocated pool and free bytes separately.

CPU offload is a separate scenario, never a free reduction in weights: `GPU_live = resident_GPU_weights + GPU_KV + runtime + transfer_buffers`; `host_peak = retained_host_weights + host_KV + load/dequantization_staging + process/pinned_buffers + other_workloads`. Loading can transiently retain a full checkpoint even when final GPU residency is smaller. If these host terms or transfer costs are unknown, host feasibility and offloaded latency remain unknown. These are project accounting equations; no offload capacity or transfer performance is measured here.

### Worked examples: assumptions, outputs and uncertainty

These are arithmetic **estimates**, not measurements or vendor-certified configurations. C11 supplies Qwen2.5-7B-Instruct metadata: 15,231,233,024 tensor bytes; 28 layers; hidden size 3584; 28 query heads; 4 KV heads; BF16. Derived head dimension is 128; KV bytes/token are `2 × 28 × 4 × 128 × 2 = 57,344`. The pinned older config has a different advertised context setup from today's main; these examples explicitly cap context at 32,768 and do not claim quality at the maximum. T1 must approve the artifact/context policy before a real build is submitted.

Scenario assumptions: identical tensor dtype on device, no CPU offload, no prefix cache savings, full attention, cache block size 16 tokens, BF16 KV, decode batch = active sequences, no adapters unless stated. Prefill is capped to 2,048 tokens per scheduling step as a **scenario input**, with runtime/activation/workspace bracket of 2–4 GiB per device; this bracket has no measured coverage guarantee. Headroom scenarios are 10% and 20% of device capacity, not a claimed statistical interval. Hardware selection is one full L40S, with actual free bytes still unknown.

| Case | Context per sequence (prompt + output), concurrency | Weight / KV bytes (published input / derived) | Required memory, decimal GB (derived range) | Capacity interpretation |
| --- | --- | --- | --- | --- |
| A, BF16 short | 8,192 (6,144 + 2,048), 1 | W=15,231,233,024; K=469,762,048 | 19.832–24.995 | One advertised 48 GB L40S clears this arithmetic screen; runtime support, free bytes and SLO remain unverified |
| B, BF16 loaded | 32,768 (30,720 + 2,048), 8 | W=15,231,233,024; K=15,032,385,536 | 36.012–43.198 | One L40S is a candidate, not a certified recommendation; comparing to exact runtime allocation and overhead bracket is necessary |
| C, hypothetical uniform INT4 payload | 32,768, 8 | Hypothetically 7,615,616,512 elements all INT4: 3,807,808,256 payload bytes plus deliberately assumed 10% metadata = 4,188,589,081.6; same BF16 KV as B | 23.743–29.395 | Synthetic quantization sensitivity only, not a real mixed AWQ/GPTQ/GGUF checkpoint. Do not create a vendor/model catalog item from it |
| D, nonmerged LoRA sensitivity | A plus four simultaneously resident adapters, each rank 16 on Q and V only | Derived adapter payload 40,370,176 bytes total, excluding workspace/metadata | A's bounds rise by 0.045–0.050 GB | Conditional shape exercise, not an artifact from #33 |

Range endpoints use `(W+K+2GiB)/(1-0.10)` and `(W+K+4GiB)/(1-0.20)`; D adds adapter bytes first. The method has **no validated percentage error range**. Sensitivity bounds cover only specified inputs and can underpredict if workspace, quantization, fragmentation or cache behavior differs. Increase concurrency/context and recalculate rather than extrapolate a fixed “GB per billion parameters”.

Case D follows LoRA's low-rank count `r × (d_in + d_out)` per adapted linear layer (C13). For Qwen's shapes: Q has 3584→3584, V has 3584→512. Across 28 layers, rank 16 and BF16, one adapter has 10,092,544 bytes; four have 40,370,176 bytes. This is payload only. Multi-adapter residency, rank limits, staging and batching overhead are engine-specific (#11/#33). Merged weights are sized as a full distinct checkpoint; do not add the unmerged adapter again. Keeping a base and merged checkpoint loaded together requires both copies.

Two additional **synthetic estimate** checks are reproduced by the script. A merged checkpoint with A's unchanged shape/dtype has A's bounds when loaded alone, with no extra adapter payload; this assumes a hypothetical merge and no duplicated base. For a 48 GB allocation and assumed 41 GB live payload (including runtime), 10% reserve requires 45.556 GB and clears the screen, while 20% requires 51.25 GB and exceeds it. Under the owner-reviewed conservative policy, an estimate meeting the build's proposed minimum resource confidence uses the upper bound: this straddling range gives `fail`, flagged **may not fit**, displaying both bounds. It is a conditional screen decision, not a proven hardware failure. Missing confidence eligibility remains `unknown` for review; no default confidence or headroom is invented. Missing KV geometry produces an unknown estimate, and an API-only route skips local sizing; neither is encoded as numeric zero.

### Multi-GPU count and parallelism

Search supported topologies, then calculate **each** device's peak. A lower bound `ceil(total_required_bytes / capacity_bytes)` is not a valid GPU-count recommendation without a partition plan. TP shards eligible tensors; PP partitions layers. For dense models, DP replicates the model across serving replicas rather than pooling memory; vLLM v0.31.0 separately notes MoE-layer sharding across the product of TP and DP degrees (C15, C21). KV may shard, replicate, or duplicate when TP exceeds KV heads; workspaces and communication buffers do not generally shrink linearly. Attention-head divisibility, quantization kernels, vocab/output layers, node locality and topology constraints require #11's version-specific evidence.

Illustrative **synthetic** topology: an assumed 70,000,000,000-parameter dense BF16 payload is 140 GB before cache/overhead. Two advertised 80 GB devices exceed the aggregate payload; that observation alone is insufficient. If a supported two-way plan splits weights equally, KV is assumed 8 GB/device, runtime 4 GB/device and headroom 10%, each requires `(70+8+4)/0.9 = 91.111 GB`, so two such devices fail the screen. A four-way plan with weights 35 GB, KV 4 GB, runtime 4 GB/device requires 47.778 GB/device; it passes only the stated screen, conditional on actual sharding. These are invented scenarios demonstrating arithmetic, not facts about a particular 70B model.

Topology must record device count per model replica, replica count, node count, TP/PP/EP/DP degrees, per-rank tensors/KV, fabric and measured collective behavior. An L40S PCIe link is not NVLink; an H100 SXM's published link rating is not proof that a rented VM connects its assigned GPUs that way (C01, C02). Cross-node networking and CPU offload change latency and need separate measurements. No automatic sum of VRAM or linear throughput scaling is proposed.

### Throughput, latency and published measurements

C16 reports a **publisher-measured / Vendor claim** historical comparison for Qwen2.5-7B-Instruct BF16: one A100 80GB, batch 1, 2,048 generated tokens. At input lengths 1 / 30,720, its Transformers results are 40.38 / 18.83 tokens/s and memory 14.38 / 19.97 “GB” as labelled by the publisher. Transformers environment: CUDA 12.1, PyTorch 2.3.1, Flash Attention 2.5.8, Transformers 4.46.0. The vLLM 0.6.3 rows report 84.28 / 70.33 tokens/s with CUDA 12.1, PyTorch 2.4.0 and Flash Attention 2.6.3; defaults include utilization 0.9, max length 32,768, non-eager execution. Source memory units and timing scope are insufficiently specified for calibration. These numbers are not TTFT, an SLO, independent reproduction or predictions for vLLM 0.10.2/L40S/MI300X.

For a future estimate, first find a measurement matching exact artifact, engine build, quantization, backend, device topology, prompt/output distributions and load. Preserve TTFT (including queue), inter-token latency, end-to-end latency, per-user decode rate and aggregate output tokens/s separately, with p50/p95/p99 and run counts. Fit only within a measured envelope; reserve holdout scenarios and report observed residuals before calling the estimator `calibrated`. Published peak FLOPs/bandwidth are diagnostic ceilings, not a deployment prediction. There is no defensible numeric throughput or latency interval for the new profile in this submission; its result is **unknown**. Do not invent zero throughput or a numeric confidence percentage.

The proposed load-to-count procedure is: bound prompt/output distributions, arrival rate and admitted concurrency from #2/#7; screen each evidenced device/topology for memory; then use matching published or later authorized measurements to find the largest per-replica load meeting both latency and throughput targets. A capacity lower bound is `ceil(target_output_tokens_per_second / evidenced_sustainable_output_tokens_per_second_per_replica)`, with source-matched workload and a separately chosen utilization margin. Check queueing/burst behavior and repeat the per-device screen at the resulting admission limit; reserve/failover replicas are a separate policy quantity. If sustainable rate or tail-latency evidence is missing, GPU count for the target SLO is unknown even if the memory lower bound is known. This is an uncalibrated project method, not a benchmark prediction or a training estimate.

## Compatibility proposals

The [compute rules](rules/compute-capacity.md) follow the rule-proposal template for #40 review. They distinguish a proven assertion from a conditional estimate and separate outcome (`pass/fail/unknown/skipped`) from severity (`info/warning/error`). Four proposed groups cover shared memory-fit screening, joint model/engine/backend support, KV accounting and topology. Former COMPUTE-05 is shared component applicability; context-limit checking stays with #7's `rule.model.context.fit`. An outcome for one assertion is not a universal compatible boolean. #40's review accepts these families into its queue, subject to versioned CD-1/CD-2/CD-3 decisions.

### ResourceEstimate contract mapping and #40 questions

The v1 schema C17 permits scalar decimal values for `inference.estimated_required_vram_gb`, `inference.estimated_peak_per_device_vram_gb`, `inference.estimated_tokens_per_second`, and power/training metrics. It requires real `build_id`, `build_revision`, timestamp and `selection_ids`, plus estimator identity/version, confidence and assumptions. Proposal:

1. Generate only after a real version-pinned build and selections exist. Use `confidence="estimated"` for this uncalibrated method. Preserve GB conversions, complete model/cache/parallelism/overhead inputs, source URLs and runtime conditions in assumptions/source URI. Tie every influenced selection (model, context, engine, accelerator, profile and optional adapter/workload) to the result.
2. Report upper-bound scenario memory as the conservative scalar, and preserve the full sensitivity table and input manifest in the source note. `estimated_required_vram_gb` is sum across ranks; `estimated_peak_per_device_vram_gb` is maximum rank. State that convention explicitly until #40 confirms it. For one device the two are identical. Do not take a single-device estimate and multiply/divide blindly.
3. Leave unsupported throughput/power metrics absent. A missing metric is not a zero; the evaluation should report unknown for the dependent assertion. TDP is not estimated operating power, and no training GPU-hours are emitted by this method.
4. No new ResourceEstimate JSON is claimed: merged T1 catalog records now exist, but this historical scenario is not bound to a real BuildSnapshot and selection IDs, and the note-only consumption/future-placement proposal below still needs Mattycodes69's disposition and agreement on future placement. appletechie's scoped note-only acceptance is recorded separately. The reproducible calculation output remains a research calculation, not a build artifact. The synthetic fixture checks shape only, not this method or a vendor deployment.

Requested extensions for #40/@tynamite, with #6/@zwright8, #10/#11/@Mattycodes69 and #39/@PUSHINGSQUARES as affected consumers: interval/scenario identity and unknown reason for ResourceEstimate; artifact tensor/quantization metadata; per-device allocatable memory and partition profile distinct from advertised capacity; bandwidth with units and peak/sustained qualifier; multiple interconnects/topology; physical cores versus vCPU and host RAM unit semantics; TP/PP/EP/DP and KV-sharding metadata. Examples are the 48 GB/44 GiB L40S allocation, Case B's 36.012–43.198 GB range and unknown throughput. Proposed version/migration: additive draft for a next contract version with explicit reader support; preserve imported v1, do not add unrecognized spec fields or silently reinterpret historical values. Namespaced intake annotations do not become approved canonical fields.

## Headroom and measurement handoff disposition (2026-10-18)

This contribution recommends **explicit scenario headroom, with no universal numeric default**. It retains #61's full experimental acceptance scope. These are reviewable methodology decisions for the live #10/#61 co-owners, @Mattycodes69 and @appletechie, with coordinator @CompleteDotTech; this text does not manufacture their acceptance. Sources inspected on 2026-10-18: [live #10](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10), [live #61 and its scoped receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/61#issuecomment-6242699281), the [committed measurement record](../market/sizing-validation.md), and frozen v1 C17. This is a repository/evidence audit, not a new hardware measurement.

- Specify a headroom fraction `h` for each device/admission domain, with `0 <= h < 1`, its rationale, and the capacity basis before that reserve. An explicitly justified zero is distinguishable from a missing input. Missing headroom, runtime coverage, capacity evidence or confidence eligibility leaves the fit conclusion `unknown` for review. The worked 10%/20% cases remain sensitivity examples; neither the small dense cohort nor an engine's utilization default calibrates a general reserve.
- Account for resident weights, cache, adapters, workspace and communication first. Apply unused-capacity reserve once: `required_upper = live_upper / (1-h)`, or equivalently `live_upper <= (1-h) * capacity_lower`. State whether capacity is an instance entitlement, partition allocation, observed budget or advertised specification. A specification-only comparison remains a conditional arithmetic screen. Exclude other workloads once, and reconcile the engine's preallocated pool rather than adding a second KV allocation or a second reserve.
- Keep confidence and headroom independent. `confidence="estimated"` describes this uncalibrated estimator when a real build is later bound; it is not a promise that the scenario bounds cover runtime error. No numeric confidence threshold is adopted here. Missing eligibility cannot be repaired by selecting a larger reserve.
- Offer #61's existing observations to #10 as **note-only accounting evidence**: actual prompt/cache/predicted lengths, active sequences, exact artifact/runtime/backend, and separate phase peaks. Retain raw records at `research/market/measurements/` and their limitations. Allocated and reserved overlap; they are not additive. Nine native KV layout checks are not total-memory calibration, and zero matched competitor/runtime pairs supply no competitor error range.
- Do not convert these observations into ResourceEstimate JSON. The v1 schema has estimate metrics and requires a real build revision and selection IDs. For future qualifying build-bound estimates, the proposed #10-owned placement and intake gates are [compute/resource-estimates/README.md](compute/resource-estimates/README.md). That path is a proposal pending the co-owners' disposition, not evidence that records already exist or that the schema can encode measured allocator counters.

**Experiment disposition:** retain dense/MoE/topology and comparable-estimator requirements unless the accountable experiment/coordinator owners explicitly narrow them. This pass adds no hardware authorization, weights download or experiment. Historical failed spare-capacity screens are not current availability. The [#61 continuation table](../market/sizing-validation.md#coverage-and-authority-disposition-2026-10-18) names the missing hardware and comparison inputs. An interface receipt does not waive them.

**Review still required:** [@appletechie's 2026-10-18 co-owner response](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10#issuecomment-6245668221), reviewing main `66b46d4`, accepts explicit headroom with no universal default and note-only #61 consumption with constraints; it supplies no calibrated default, ResourceEstimate, runtime result or future-placement approval. Mattycodes69's methodology disposition and agreement on future build-bound placement remain open. #61 co-owners and coordinator retain experiment scope/evidence acceptance; #9/#11 interface receipts and appletechie's constrained #39 response do not decide those matters or speak for PUSHINGSQUARES. [#31's existing hardware-reuse receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10#issuecomment-6230482484) remains accepted only within its stated scope. #40 retains versioned contract/rule review. Shared market handoff ledgers remain with #59's writer.

### Research arithmetic check for the headroom proposal

The [memory-screen helper](compute/memory_screen.py) makes the proposed reserve accounting reviewable without running a device or changing the historical `t2-dense-kv-memory` v0.2.0 examples. Its [synthetic regression cases](../../tests/test_t2_memory_screen.py) exercise the documented sensitivity boundary, exact equality/one-byte excess, already reduced pools, missing inputs and invalid values. They are arithmetic fixtures, not research measurements or approved compatibility rules.

The caller must provide integer byte bounds for upper live demand and lower capacity, a finite Decimal headroom fraction, an explicit before/after-reserve capacity basis, confidence eligibility and matching-domain assertions. There are no default reserves or implicit confidence/domain approvals. A pre-reserve capacity is reduced once; an already reduced engine pool is compared directly. The traceable reserve fraction is still required for either basis. Missing/unsatisfied eligibility or domain agreement gives `unknown`; invalid/non-finite inputs are rejected. Exact rational arithmetic prevents rounding at a capacity boundary from hiding an excess.

A helper `pass` means only that the supplied upper bound clears the supplied budget; `fail` means **may not fit under those inputs**. Inputs are caller assertions: the helper does not verify provenance, discover missing memory terms, decide applicability, calibrate error, select a GPU count, prove engine support or establish a throughput/latency target. A positive arithmetic result must not be presented as measured fit. The proposal still needs the named co-owner decisions and #40's versioned rule review; no ResourceEstimate is emitted.

## Pricing and capacity

Hosting, rates, commitment periods, billed units, regional availability and storage costs are in [hosting.md](hosting.md) and #9; cost aggregation is #39. Accelerator records have `billing_class="unknown"` because chip identity has no universal hosting rate. The AWS profile also preserves unknown billing classification pending #9/#39's exact purchasing scenario. No physical GPU acquisition quote or cost/token estimate is invented. Regional offering is not stock; compute needed for an SLO remains uncertain until the load is evidenced.

## Recommendation and rationale

Adopt separate physical and host-profile identities, exact unit conversions, byte-based tensor/KV arithmetic and per-rank memory screening. Use a source-complete AWS profile as a linked intake example while preserving Runpod's missing facts. Carry uncertainty as named scenario inputs; keep runtime support and quality separate from memory. Require later measurements before making latency or throughput recommendations. This avoids treating a marketing parameter count, GPU name or nominal bit width as sufficient evidence.

## Structured artifacts

- [L40S CatalogItem](../../catalog/proposals/t2-compute-nvidia-l40s-2026-10-16.json)
- [RTX 4090 CatalogItem](../../catalog/proposals/t2-compute-nvidia-geforce-rtx-4090-2026-10-18.json)
- [A100 80GB CatalogItem](../../catalog/proposals/t2-compute-nvidia-a100-80gb-2026-10-18.json) and [P4de profile](../../catalog/proposals/t2-compute-aws-p4de-24xlarge-us-east-1-2026-10-18.json), with the separate scoped native-precision assessment below
- [H100 SXM and MI300X note-only candidates](#incomplete-precision-intake-correction-2026-10-18), with the original sourced facts and immutable prior proposal identities retained
- [AWS regional compute profile](../../catalog/proposals/t2-compute-aws-g6e-xlarge-us-east-1-2026-10-16.json), resolving `aws-ec2` from #9's same submission
- [Sizing calculation script](compute/sizing_examples.py); [proposed rules](rules/compute-capacity.md)

No model weights, source PDFs, raw benchmark datasets, large downloads or new external binary artifacts are committed, so no evidence manifest is needed for this package. There is no asserted right to mirror publisher material. #41 must review terms and factual reuse separately from source accuracy; a checked source does not settle licensing.

## Open questions and handoffs

The table retains its 2026-10-16 input questions, with live owners, directional receipts and the separate #10/#61 proposal state refreshed on 2026-10-18. Required consumers #9/#11/#31 have scoped historical receipts; appletechie supplies a constrained #39 response, and PUSHINGSQUARES's later narrowing identifies the still-missing headroom input in the cost model. The changed H100/MI300X intake eligibility needs its own receiving review; earlier hardware-reuse receipts are not approval of that correction. Interface acceptance does not decide calibration, measurement scope or ResourceEstimate placement, and does not accept another co-owner's scope. A proposal or review request is not confirmation.

| Follow-up / exact question | Responsible issue / owner | Impact / handoff state |
| --- | --- | --- |
| Accept accelerator/profile boundary, physical core interpretation, historical region scope and unknown stock? | #9, @Mattycodes69 / @appletechie | [#10 -> #9 accepted with constraints by @Mattycodes69](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/9#issuecomment-6245204225): preserve distinct IDs/units and regional offering versus deployability; [@appletechie separately accepts with constraints](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/9#issuecomment-6245668047), reviewing main `66b46d4`: preserve IDs, source/normalized units and offering versus deployability |
| Confirm current v0.31.0 versus historical v0.10.2 constraints, per-rank KV/adapter placement and engine-version invalidation? | #11, @zwright8 / @Mattycodes69 | [#10 -> #11 accepted with constraints by @Mattycodes69](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/11#issuecomment-6245204677): exact tuple, per-device allocation/topology, resident demand/admission and uncertainty; no pooled VRAM, inherited results or SLO assertion |
| Reuse these physical IDs without treating inference capacity as training memory/time? | #31, @tynamite / @appletechie | [Accepted hardware-reuse boundary](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10#issuecomment-6230482484); missing records and training estimates remain separate |
| Accept GB conversion, scenario bounds, replica/device count and absent throughput instead of inferred token economics? | #39, @appletechie / @PUSHINGSQUARES | [@appletechie accepts with constraints](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10#issuecomment-6245668221), reviewing main `66b46d4`. [@PUSHINGSQUARES narrows](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10#issuecomment-6247689665), checking `9192d5d`: quantity/utilization boundaries are documented, but #39 has no headroom term; capacity lines must disclose **headroom not applied** until an explicit input is adopted. Neither response calibrates a reserve or creates a ResourceEstimate |
| Approve exact tensor/artifact revision and context policy; provide resident tensors and model-specific cache geometry? | #6, @zwright8 / @PUSHINGSQUARES; #7, @zwright8 / @appletechie | Informational compatibility handoff pending; calculations remain conditional |
| Confirm adapter versus merged-checkpoint lineage, target modules, rank and simultaneous residency? | #33, @Mattycodes69 / @appletechie | [@appletechie accepts with narrowing](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10#issuecomment-6245668221): #33 supplies artifact lineage/rank/targets/variant/added-token tensors; resident adapter count is #11/#37 configuration, not an artifact fact |
| Accept explicit scenario headroom and note-only #61 consumption, with future build-bound placement? | #10, @Mattycodes69 and @appletechie; #61 co-owners and coordinator for experiment scope | [@appletechie accepts explicit headroom and note-only observations with constraints](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10#issuecomment-6245668221); Mattycodes69's disposition and future placement remain open. No universal reserve, calibration or ResourceEstimate emitted |
| Finalize proposed rules, ResourceEstimate intervals/unknowns and bandwidth/topology/partition fields? | #40, @tynamite and @zwright8 | Accepted into central queue, narrowed in linked PR #75 review; CD-1/CD-2/CD-3 and affected-owner version review remain; no schema edits/final ruleset |
| Complete per-source rights inventory and final evidence policy? | #41, @tynamite and @PUSHINGSQUARES | Interim freshness/conflict/short-paraphrase policy adopted in linked review; no automation/mirroring permission presumed |
| Confirm current account/region offer, quotas, runtime free memory and deployment measurement procedure? | #37, @appletechie / @PUSHINGSQUARES | Deployment research input only; no provisioning performed |

The [#10 receiving-owner comment](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10#issuecomment-6245205057), reviewing main `9344f99325510adfe678382a4672246d028e87bc`, separately accepts **#9 -> #10 and #11 -> #10 with constraints from @Mattycodes69's scope**. The host binding reuses `aws-ec2` and `aws-ec2-g6e-xlarge-us-east-1` version `2026-10-16`, with `nvidia-l40s` distinct, two default CPU cores/four vCPUs, and source 32 GiB = 34.359738368 decimal GB RAM. Runtime inputs retain exact-release loader/backend/format/quantization/kernel constraints, separate weight/activation/KV dtypes, adapter rank/targets/residency, per-rank topology and expanded resident-sequence/admission scope. Historical vLLM v0.10.2 calculations remain historical; v0.31.0 requires its own eligible build/hardware evidence, including the resolved Volta exclusion. Missing free memory, geometry or admission stays explicit; memory fit does not establish serving support, quality or SLO performance. These incoming receipts are separate from the outgoing rows above, do not speak for @appletechie, and accept no headroom default, ResourceEstimate, runtime result or #61 placement.

## Acceptance assessment and validation

| Live #10 criterion (preserved) | Evidence/artifact | Assessment before review |
| --- | --- | --- |
| Sizing method with assumptions and uncertainty documented | Method, worked examples, script | Research draft supplied; uncalibrated uncertainty explicit |
| Measured values cite their source and conditions; estimates are labelled | C16 conditions; every calculation marked Estimate | Supplied; no local measurements claimed |
| Model ↔ GPU rules in the #40 format | rules/compute-capacity.md | Proposed; #40 approval pending |
| Decision record merged at required path following research method | This record; PR #75 | Merged; this follow-up and full issue acceptance remain pending |
| Candidate set covers relevant API / managed / self-hosted modes or states why a mode does not apply | Mode table, physical candidates and profile | Supplied; CPU/edge gaps explicit |
| Comparison fields defined with type, unit, evidence requirement | Comparison table | Supplied |
| Compatibility rules/warnings shared format; verified rules separated from hypotheses | Rule classifications and examples | Supplied as proposals; central review pending |
| Every factual/numeric claim primary source + access date and relevant conditions | C01–C22; source-mapped catalog provenance; derived formulas | Prepared for independent evidence review; source rendering and unit conflicts disclosed |
| Each handoff confirmed by consuming issue owner with link | Handoff table | Historical #9/#11/#31 receipts and both actual #39 responses are linked. PUSHINGSQUARES identifies unapplied headroom, and changed H100/MI300X intake eligibility needs receiving review. Methodology, calibration, full #61 evidence and future placement remain separate |
| Open questions with named follow-up owner | Table above | Supplied |

Validation is recorded by the integrating orchestrator after all same-submission host references exist. Required baseline commands remain `pip install -r requirements-research.txt`, contract tests, research tests and `scripts/validate_research.py` under Python 3.12. In addition, run the sizing script and explicitly validate `contracts/v1/examples/resource-estimate.json` against its schema. No validation pass alone establishes source accuracy, fit, rights, current supply, compatibility approval or consuming-owner acceptance.

Follow-up validation, 2026-10-17 (Python 3.12.14): pinned dependency installation, 21 contract tests, 24 research tests, research intake (30 CatalogItems / two Pricebooks), market integrity (32 entities / 1,536 cells / 20 issues), sizing arithmetic and `git diff --check` pass. Research tests required an unsandboxed rerun because Windows sandbox temporary-directory permissions failed before assertions; the rerun passed all 24. The arithmetic implementation and imported v1 are unchanged. These checks establish structural integrity and reproducible arithmetic, not rule approval or empirical fit. #10 still needs its default headroom/confidence decision, consuming-owner acknowledgements and agreed #61 ResourceEstimate placement before closure.


## Additional hardware and profile capture (2026-10-18)

This source-checked, runtime-unverified supplement records evidence for #31’s missing-record request. At the initial capture, the hardware and dependent profile remained note-only: frozen v1 precision membership treats an omitted precision as unsupported, so a researched subset cannot safely be emitted as a CatalogItem. The follow-up below resolves the RTX 4090 precision gap; A100/P4de remain note-only. No runtime compatibility is asserted here.

| Note-only candidate | Published facts and precise scope | Primary evidence, accessed 2026-10-18 |
| --- | --- | --- |
| `nvidia-a100-80gb` | 80GB; FP32/TF32/BF16/FP16/INT8 subset shared by PCIe and SXM. Variant-specific power/fabric deliberately absent | [NVIDIA datasheet 2188504, p1](https://www.nvidia.com/content/dam/en-zz/Solutions/Data-Center/a100/pdf/nvidia-a100-datasheet-nvidia-us-2188504-web.pdf); [CUDA GPU table](https://developer.nvidia.com/cuda/gpus) |
| `nvidia-geforce-rtx-4090` | Reference design: 24GB, PCIe, 450W graphics rating; CUDA compute capability 8.9; researched FP32 subset, not an exhaustive precision list | [NVIDIA specifications](https://www.nvidia.com/en-us/geforce/graphics-cards/40-series/rtx-4090/); [Ada guide 13.4, §1.4.1.3](https://docs.nvidia.com/cuda/ada-tuning-guide/index.html) |
| `aws-ec2-p4de-24xlarge-us-east-1` | Eight A100 80GB,48 default CPU cores(96vCPU),1152GiB RAM =1236.950581248 decimal GB,8000GB aggregate local storage; region listing is not provisioning proof | [P4 specification](https://aws.amazon.com/ec2/instance-types/p4/); [CPU options](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/cpu-options-supported-instances-values.html); [region table](https://docs.aws.amazon.com/ec2/latest/instancetypes/ec2-instance-regions.html) |

The A100 reference supplies only cross-variant facts; it cannot establish a particular board’s power or interconnect. The precision lists in this initial capture were non-exhaustive. Their omissions were research unknowns, but frozen v1 cannot express that distinction for accelerator precision membership; this prevented accelerator/profile promotion at that point. The RTX 4090 follow-up below supplies its complete v1 precision coverage; the later [A100/P4de follow-up](#a100-and-p4de-precision-and-profile-follow-up--2026-10-18) records additional native-precision evidence and scoped proposals. Advertised device memory is not measured free allocation, and eight devices do not form one freely addressable 640GB allocation. No throughput, training fit, price, runtime result or independent verification is claimed. Current lifecycle/stock, account quota and AZ capacity remain unverified. The PDF is identified by publisher document 2188504; no immutable content hash was obtained. Other URLs are mutable dated captures. Exact host/device/runtime evidence is still needed before deployment.

#31 can use the initial notes as research inputs, but could not reference the then-missing catalog IDs. The RTX 4090 record is supplied below, and the later A100/P4de follow-up adds those two proposals after the precision check. Other priced SKUs still need matching profile evidence. Unsupported training-memory metrics and price meters remain #40/#39 work, independent of these catalog facts.


## Precision follow-up and bounded retrieval (2026-10-18)

The [RTX 4090 proposal](../../catalog/proposals/t2-compute-nvidia-geforce-rtx-4090-2026-10-18.json)
resolves its initial absence. [NVIDIA Ada whitepaper v2.02](https://images.nvidia.com/aem-dam/Solutions/geforce/ada/nvidia-ada-gpu-architecture.pdf),
Appendix A, printed pp29–31, documents every v1 precision in the RTX 4090 column;
the separate [CUDA GPU table](https://developer.nvidia.com/cuda/gpus) supports its
CUDA identity. Both were accessed 2026-10-18. This is hardware arithmetic support,
not permission to run every quantized artifact or an engine compatibility result.
No negative precision inference is needed because all seven enum values have
positive evidence. Keep engine/backend, quantizer, kernel, model and cache dtype
checks separate.

The [A100 architecture whitepaper](https://images.nvidia.com/aem-dam/en-zz/Solutions/data-center/nvidia-ampere-architecture-whitepaper.pdf),
printed pp15/26, accessed 2026-10-18, adds explicit INT4 evidence to the earlier
subset. It does not resolve the FP8 entry: absence from that older document is not
a universal negative. The attempted TensorRT 10.5 archive URL redirected to
current documentation, so it was not treated as a pinned historical support
matrix. The Transformer Engine FP8 primer retrieval failed; no fact is inferred
from that failure. A100 therefore remained note-only at that earlier check under
the frozen-v1 negative membership behavior. The later follow-up supplies separate
eligible architecture evidence; it does not change v1 completeness semantics.

Re-reading the [P4 specification](https://aws.amazon.com/ec2/instance-types/p4/),
[CPU-options row](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/cpu-options-supported-instances-values.html)
and [regional table](https://docs.aws.amazon.com/ec2/latest/instancetypes/ec2-instance-regions.html)
on 2026-10-18 confirmed the P4de note's default CPU/RAM/disk values and the
us-east-1 family listing. At that point the A100 catalog identity was still absent.
The later profile retains the GPU reference to its companion A100 proposal; it
does not remove that material dependency merely to pass intake.

PDF source text and table views were inspected through the web reader. Direct
PDF download returned HTTP 403 from the environment proxy; no hash, local PDF
capture or redistribution permission is claimed. Dates/document versions are
recorded; mutable URLs are not immutable evidence. No source freshness guarantee,
current stock, rate binding or runtime measurement follows from this research.


## Explicit-headroom arithmetic follow-up validation (2026-10-18)

Prepared from main `fb434fd75685d9c5788a8181548af6ecbd5cce81` with Python **3.12.14**. Pinned requirements were checked with `python -m pip install -r requirements-research.txt --target <temporary-directory>`; `PYTHONPATH` selected that directory and `PYTHONUTF8=1` made Windows text handling explicit.

| Command | Actual result |
| --- | --- |
| `python -m unittest discover -s contracts/v1/tests -v` | 21 passed |
| `python -m unittest discover -s tests -v` | 192 passed, including 8 new synthetic memory-screen tests |
| `python scripts/validate_research.py` | Passed: 74 CatalogItems, 3 Pricebooks and evidence metadata |
| `python scripts/validate_market_research.py` | Passed: 33 entities / 1,584 cells / 20 issues |
| `python scripts/validate_handoff_audit.py` | Passed: 101 rows / 98 declared pairs; human acceptance not certified |
| `python prompts/mobile/validate_prompts.py` | Passed: 258 issues / 36 epics / 906 criteria / 880 steps |
| `python research/T2-infrastructure/compute/sizing_examples.py` | Historical v0.2.0 arithmetic assertions passed; no device execution |
| `python contracts/v1/reference/validate_payload.py contracts/v1/schemas/resource-estimate.schema.json contracts/v1/examples/resource-estimate.json` | Synthetic imported example valid; no real estimate created |
| `git diff --check` | Passed |

The focused regressions verify conditional arithmetic, not measurements, evidence eligibility or an executable approved ruleset. They use synthetic values only under `tests/`. Catalog facts, pricebooks, v1, historical sizing examples and the shared market evidence ledger are unchanged. Source truth, rights, calibration, Mattycodes69's methodology disposition, future placement and the remaining consumer scopes require evidence/owner review.

## A100 and P4de precision and profile follow-up — 2026-10-18

The [A100 80GB accelerator proposal](../../catalog/proposals/t2-compute-nvidia-a100-80gb-2026-10-18.json)
and [P4de profile proposal](../../catalog/proposals/t2-compute-aws-p4de-24xlarge-us-east-1-2026-10-18.json)
use the identities from the earlier notes. Additional official sources establish
the native-arithmetic scope of the remaining precision value. All source checks
below occurred on **2026-10-18**. The earlier capture dates, retrieval failures,
frozen-v1 definitions and #31's receiving criteria are retained.

| Source ID | Primary source and inspected section | Claim and scope |
| --- | --- | --- |
| A100-P1 | [NVIDIA A100 datasheet 2188504](https://www.nvidia.com/content/dam/en-zz/Solutions/Data-Center/a100/pdf/nvidia-a100-datasheet-nvidia-us-2188504-web.pdf), printed p1, 80GB PCIe and SXM columns | Both columns advertise 80GB and FP32, TF32, BF16, FP16 and INT8 arithmetic. The proposal takes only these common facts; power, bandwidth and interconnect differ by variant and are omitted. Advertised capacity is not measured free memory. |
| A100-P2 | [NVIDIA Ampere architecture whitepaper](https://images.nvidia.com/aem-dam/en-zz/Solutions/data-center/nvidia-ampere-architecture-whitepaper.pdf), printed pp15 and 26 | Explicit INT4 Tensor Core support supplies the sixth positive v1 precision value. This older paper's omission of FP8 is not used as a negative claim. |
| A100-P3 | [NVIDIA CUDA GPU table](https://developer.nvidia.com/cuda/gpus), A100 row | A100 has compute capability 8.0. This supplies the architecture identity for the instruction comparison and the CUDA backend, not a tested driver/runtime tuple. |
| A100-P4 | [PTX ISA 8.7, CUDA 12.8.1 archive](https://docs.nvidia.com/cuda/archive/12.8.1/parallel-thread-execution/index.html), MMA Target ISA Notes | FP8 `e4m3`/`e5m2` MMA requires `sm_89` or higher. Combined with A100's `sm_80` identity, this supports the inference that A100 lacks that native FP8 matrix arithmetic. It does not establish a universal software or artifact prohibition. |
| A100-P5 | [NVIDIA Hopper architecture article](https://developer.nvidia.com/blog/nvidia-hopper-architecture-in-depth/), 2022-03-22, Table 3 | Both FP8 Tensor Core rows are `N/A` for the article's A100 comparison. That column describes a **40GB** A100; it corroborates the architecture distinction only. Its memory, power and preliminary H100 performance figures are not copied into the 80GB proposal. |
| P4DE-P1 | [AWS P4 product details](https://aws.amazon.com/ec2/instance-types/p4/), `p4de.24xlarge` row and GPU-memory paragraph | Eight A100 devices with 80GB each, 1152GiB system RAM and eight 1000GB local NVMe devices. The product description supports the allocation, not present account capacity, persistent storage, fit or throughput. |
| P4DE-P2 | [AWS CPU options](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/cpu-options-supported-instances-values.html), accelerated-computing `p4de.24xlarge` row | 48 default CPU cores, 96 vCPUs and two threads per core. The proposal records default cores; it does not claim dedicated physical-host tenancy. |
| P4DE-P3 | [AWS instance types by Region](https://docs.aws.amazon.com/ec2/latest/instancetypes/ec2-instance-regions.html), US East (N. Virginia), `us-east-1` | The accelerated-computing list includes P4de. This is a dated regional family offering, not availability in every AZ, current stock, quota or account authorization. |

**Precision assessment.** All seven v1 precision enum values now have an explicit
disposition for native A100 arithmetic: FP32, TF32, BF16, FP16 and INT8 have
positive 80GB product evidence; INT4 has positive architecture evidence; FP8 is
excluded by the A100/PTX architecture inference, corroborated within A100-P5's
stated scope. This is source-checked research, and every provenance entry remains
`unverified`. FP64 is also documented but is outside the frozen v1 precision enum.

The native precision list does not describe storage encodings, software
conversion, emulation, mixed-precision execution or every engine's quantized
artifact path. A v1 membership result alone cannot qualify that joint path;
#11/#40 still need its exact artifact, quantizer, kernel, engine and driver
constraints. No engine run or hardware compatibility result is supplied here.
The A100 identity contains common full-device PCIe/SXM facts only; board-specific
power/fabric and actual partitioned or free allocation require their own evidence.

**Profile and units.** The profile retains `hosting_ref: aws-ec2`, the companion
`accelerator_ref: nvidia-a100-80gb`, eight devices and the exact region. System RAM
is converted from the retained source unit as
`1152 × 2^30 / 10^9 = 1236.950581248` decimal GB. Advertised local storage is
`8 × 1000 = 8000` GB; it is not a persistent-storage service. The eight GPU
allocations are not one freely pooled 640GB allocation. Billing classification
stays unknown; no current quote, reservation, training/inference fit, measured
allocation or SLO is introduced. #9/#31/#39 receiving and price-scenario binding
remain separate from these catalog proposals.

The PDF source text and HTML rows were inspected. No new local source copy,
immutable content hash or source-redistribution permission is claimed. This
follow-up adds two catalog proposals and this research assessment; it changes no
rule, pricebook, frozen contract, shared handoff ledger or issue acceptance state.

## Incomplete precision intake correction (2026-10-18)

Independent review at accepted main
`ce388d7d4d38539eeccc5a0a8e740e74a17d96d2` reproduced the known
[executable-consumption limit](README.md#contributions-for-40-review) for two
actual proposals. H100 SXM and MI300X each recorded six positively sourced
native arithmetic precisions and omitted `int4`. Their provenance explicitly
described those lists as subsets. Frozen v1 requires `/spec/precisions`, and
`rule.precision.accelerator` compares that list directly with the model
selection's `/settings/precision`. It does not read list completeness,
provenance eligibility or distinct artifact/storage/compute dtypes.

Two independently reproduced, schema-valid synthetic builds used the unchanged
historical proposals and selected `int4`. The unchanged frozen evaluator
returned `fail/error`, overall `invalid` and readiness `blocked` in both cases,
including with the original `unverified` provenance. This establishes reader
behavior only. It establishes neither native INT4 support nor an actual engine
failure. The proposed COMPUTE-02 unknown handling and prose consumption gate
do not change those frozen bytes.

Both incomplete proposals are therefore withdrawn from **current intake**.
Their factual rows, source dates, unit conflicts and limitations remain above;
the exact prior bytes remain in Git:

| Note-only identity / version | Preserved prior proposal | Historical blob |
| --- | --- | --- |
| `nvidia-h100-sxm` / `2026-10-16` | [H100 SXM at the reviewed revision](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/ce388d7d4d38539eeccc5a0a8e740e74a17d96d2/catalog/proposals/t2-compute-nvidia-h100-sxm-2026-10-16.json) | `202f7cf61b5ea46e34b933b759aa7e37e18f5948` |
| `amd-mi300x` / `2026-10-16` | [MI300X at the reviewed revision](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/ce388d7d4d38539eeccc5a0a8e740e74a17d96d2/catalog/proposals/t2-compute-amd-mi300x-2026-10-16.json) | `510f0087c3fa29c51ad30a4e0f337304f7c68400` |

The correction applies the documented note-only gate while native-precision
coverage remains incomplete. It neither inserts an unsupported precision nor
removes a required field to satisfy validation. L40S and RTX 4090 retain positive
evidence for all seven v1 enum values. The accepted [A100/P4de follow-up](#a100-and-p4de-precision-and-profile-follow-up--2026-10-18)
now gives A100 six positive values and a scoped native-FP8 exclusion, with its
companion profile. Those records, the L40S/RTX 4090 records and the L40S EC2
profile are unchanged. Complete native-precision coverage still does not
establish joint artifact/engine/runtime compatibility.

A current catalog/pricebook reference audit found no structured dependent
reference to either withdrawn ID. The existing T5 availability statements are
updated to preserve the hardware facts as research inputs without offering a
missing catalog target. The publication inventory remains pinned to its
original `7115e77` tree and is unchanged. Older receiving receipts and saved
historical bytes are preserved; they do not approve this new intake disposition
or justify rewriting a historical outcome.

The coordinator rechecked C01/C02/C03 hardware tables, C06/C07 CPU/RAM/disk
allocation, C11's exact config and 15,231,233,024-byte tensor index, C16's
historical Qwen benchmark rows/conditions, and C20/C21's pinned v0.31.0 source
on 2026-10-18. These were source reads and arithmetic review, with no weights
download or device execution. The original capture dates remain unchanged.
The separate arithmetic reviewer passed all eight explicit-reserve cases and
the historical sizing assertions. No source read supplies missing precision
scope, rights, allocatable memory, calibration or an SLO.

Before these identities return to intake, #10 and #11 must specify which dtype
the claim describes and its exact evidence scope, and #40 must reconcile
complete-list/explicit-negative semantics with the selected artifact and engine
tuple. A versioned reader/ruleset needs its own reviewed migration and affected
consumer decisions. #31's current hardware-reuse statement also needs review
of this changed availability. These are named follow-ups; this correction does
not complete #10 or waive #61's empirical criteria.
