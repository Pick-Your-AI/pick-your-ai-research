# Technical feasibility and uncertainty

Status: initial desk assessment; no benchmark was executed. Access date: 2026-10-16.

## Fit is a conditional estimate

The [Local AI planner](https://logarithmicspirals.com/tools/local-ai-vram-calculator-gpu-planner/) describes weights + KV cache + runtime overhead and exposes runtime, quantization, context and multi-GPU inputs. [llmfit](https://github.com/AlexsJones/llmfit) documents hardware-aware estimates and local measurements. [ModelFit](https://modelfit.io/) describes bandwidth-derived speed estimates. These are useful starting points, not mutually validated accuracy guarantees.

For conventional attention, an analytical cache approximation is 2 × layers × KV heads × head dimension × cached tokens × bytes per element × concurrent sequences. Record architecture exceptions, shared prefixes, sliding windows and allocator behavior before using it. Weight quantization and cache quantization are separate parameters. MoE active parameters do not by themselves establish resident weight memory; offloading and runtime behavior must be known.

The [vLLM parallelism guide](https://docs.vllm.ai/en/latest/serving/parallelism_scaling/) distinguishes execution configurations. Summing GPU VRAM and multiplying bandwidth is not a sufficient proof of fit or throughput: per-device shard requirements, interconnect and parallelism strategy need measurement. These are risk hypotheses to test, not new universal compatibility rules.

## Evaluation is configuration-specific

[Harness Bench's site](https://www.harness-bench.ai/) and [repository](https://github.com/Qihoo360/harness-bench) describe 300 tasks, while the retrieved [arXiv v2 abstract](https://arxiv.org/abs/2605.27922v2) describes 106 tasks and 5,194 trajectories. Do not merge these into one dataset or repeat a single count as universally current. Reconcile release, paper and result identities before using comparative numbers. Its model-harness premise supports evaluating systems, but no result is reproduced here.

## Compatibility and economics

Connector existence does not prove matching schemas, embedding dimensions, tool-call formats, authentication or transport. Route candidate rules to #40 using the existing outcome/severity distinction. Keep optional T3–T5 capabilities optional. Market research identifies risk and user requirements; #10 owns sizing, #11 runtimes, #16 retrieval, #25/#27 agent/MCP behavior, #33 fine-tuned artifacts, #36 evaluations and #39 economics.

Local-versus-hosted comparison needs workload volume, prompt/output distribution, cache behavior, concurrency, utilization, idle capacity, energy, hardware amortization, storage, egress and operator time. No single token price or GPU-hour rate measures total cost. Use ranges and show unknown line items rather than inventing them.
