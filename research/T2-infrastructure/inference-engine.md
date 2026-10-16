# Inference engine: release-scoped serving support

Issue: #11 · Contract: 1.0.0 · Kind: `inference_engine`
Status: ready for owner and cross-tier review; proposed compatibility remains unverified
Last researched: 2026-10-16 · Research owner: @Mattycodes69 (live GitHub assignee)

## User decision

Which runtime can serve the selected model artifact, on the selected hardware, with the request behavior the application needs? Choose an **engine version + artifact revision + backend/build + configuration**. An engine name, file suffix, shared API route, or accelerator precision list alone cannot establish this choice.

This note compares a bounded current candidate set and retains explicit historical comparisons. GitHub's latest-release endpoints returned vLLM `v0.31.0`, llama.cpp `v0.7.0`, and TGI `v3.3.7` when checked on 2026-10-16 [E01]. These are latest releases *observed in that check*, not a claim that every wheel, container, plugin, or managed endpoint runs them. No inference service was deployed and no runtime benchmark or compatibility experiment was run.

| Deployment mode | Treatment |
| --- | --- |
| API | A model-provider API can omit a local engine and GPU under the canonical component guide. Provider behavior, model versions, API quotas, retention, and prices remain with #5. A route described as OpenAI-compatible is insufficient evidence of a particular serving engine/version. |
| Managed | Evaluate the exposed API and provider guarantees separately. Use this matrix only if the endpoint exposes a verifiable engine version, build/plugins, model revision, and relevant flags. llama.cpp documents a Hugging Face Inference Endpoints hosting path [E13]; TGI describes its use in Hugging Face services [E20]. Neither proves the current managed product's deployed version or every feature. Undisclosed versions/configurations remain unknown; #9 owns hosting comparison. |
| Self-hosted | All three candidates have source and serving instructions [E02, E05, E11, E14, E20]. The matrices below describe published capability under stated conditions, not installation success or production readiness. #37 owns packaging, rollout and readiness procedures; #10 owns capacity. |

Sources are primary, release-pinned documentation or source. Matrix cells are documentation findings, not independently verified joint compatibility. Per [governance](../../docs/governance.md), a compatibility claim remains unverified until a second source or reproducible test confirms it. Repeated pages from one publisher are not independent reproduction. The interim grades in [RESEARCH_METHOD.md](../../docs/RESEARCH_METHOD.md) apply while #41 remains open.

## Candidate options

### Current release inventory and scope

The following commits were resolved from the publishers' release tags [E01]. llama.cpp's annotated tag was dereferenced to its commit. The commit column and catalog provenance preserve immutable source revisions; release-tag links in the comparison evidence identify the documented release, while mutable `latest` endpoints are used only to date the inventory observation.

| Catalog ID | Examined release | Resolved source commit | Proposed catalog lifecycle |
| --- | --- | --- | --- |
| `inference-vllm` | `v0.31.0` | `db9527a46873454610df6dbedf79a36d6bf1a7f6` | `active`, a proposed catalog classification |
| `inference-llama-cpp` | `v0.7.0` | `620d2225cc436ab0b001e3200e590e3b286ef9ab` | `active`, a proposed catalog classification |
| `inference-tgi` | `v3.3.7` | `dfb3fbe78e0d1d69251bd33065591c61bafdfaa8` | `deprecated` for new-build recommendations, proposed because the release README says maintenance mode [E20] |

These lifecycle values are proposed research-catalog choices for owner review; they do not assert an upstream support window or security certification. The current GitHub repository API also reports TGI as archived [E26]; this repository lifecycle observation is separate from the pinned release's contents. TGI remains relevant to existing and managed installations. SGLang, TensorRT-LLM, Ollama and MLX are expansion candidates, not evaluated entries here; their unknown status must not be interpreted as lack of support.

### Release-keyed artifact and hardware matrix

Lists are bounded documented examples, not exhaustive architecture registries or Cartesian products of compatible choices. `unknown` means this research lacks sufficiently scoped evidence. A documented feature is not a performance result. Engine licenses below concern engine source; they do not replace model, adapter, dependency, container, or service terms [E04, E12, E21].

| Engine/version | Engine license | Architecture examples | Artifact formats | Quantization and precision | Hardware backends and limits | Claim sources |
| --- | --- | --- | --- | --- | --- | --- |
| vLLM `v0.31.0` | Apache-2.0 | Llama/Qwen/Gemma decoders; Mixtral/DeepSeek-V3 MoE; Mamba/hybrid; LLaVA/Qwen-VL; embedding/retrieval families. Exact architecture/revision and feature combinations still require the supported-model entry. | Safetensors and PyTorch weight loaders. GGUF is documented but now requires a separately installed out-of-tree plugin; its version and compatibility are unknown here. | FP32/FP16/BF16 dtype options; documented quantization families include FP8, INT8, INT4, GPTQ/AWQ, compressed-tensors, ModelOpt and TorchAO. MXFP4/NVFP4/MXFP8 names in upstream do not become new v1 precision enums. Weight, activation and KV dtypes are distinct. | Core NVIDIA CUDA, AMD ROCm, Intel GPU, CPU paths; additional devices via plugins. CUDA installation requires compute capability **7.5 or higher** and a matching binary stack. ROCm docs list MI300 (`gfx942`) and ROCm **6.3 or above**; wheel variant requirements differ. | E02–E10 |
| llama.cpp `v0.7.0` | MIT | Source registry includes `llama`, `llama4`, `qwen2`, `qwen3`, `gemma2`, `gemma3` and other architecture identifiers. Registry presence does not verify every conversion, modality, operator or quant/backend tuple. | GGUF required; upstream conversion tools are a separate artifact transformation. GGUF LoRA adapters are distinct from base GGUF weights. | GGML F32/F16/BF16 types; named GGUF quantizations including Q4_K_M and Q8_0. Mixed/block quantizations must retain their exact scheme, rather than being reduced to an assumed uniform bit width. | CPU, CUDA, AMD HIP, Metal, SYCL and Vulkan documented; other backends also listed. CPU+GPU offload documented. Backend compilation and operator support remain build-specific; no blanket memory pooling or edge latency guarantee. | E11–E17 |
| TGI `v3.3.7` | Apache-2.0 | Tagged model list includes Llama, Gemma, Mistral/Mixtral, Qwen2, DeepSeek V2/V3, T5 and selected multimodal families. Fallback Transformers loading is best effort, not guaranteed optimization. | Safetensors loading documented. Do not infer GGUF support in the default backend from the existence of optional alternative backend code. | Launcher dtype options FP16/BF16. Quantization docs list GPTQ/AWQ/Marlin/EXL2, bitsandbytes, EETQ and FP8; EXL2 explicitly does not support tensor parallelism with more than one shard. | README documents NVIDIA and AMD paths plus integrations for additional devices. Its explicit AMD note names MI210/MI250, so MI300X for this release remains unknown in this survey. CPU fallback is described as outside its intended platform. | E20–E25 |

The canonical proposals deliberately contain conservative subsets of formats/backends/precisions supported by inspected sources. Omitted entries are **not negative evidence**. In particular, llama.cpp's proposal records only F32/F16/BF16 as canonical precision entries; its mixed GGUF quantizations remain named findings above. vLLM's proposal excludes GGUF pending a separately pinned plugin. Optional global booleans and `max_batch_size` are omitted: they would hide model/parser/configuration conditions or imply a universal capacity ceiling.

For deployment consumers, vLLM v0.31.0's GPU installation page specifies Linux and Python **3.10–3.13**, and says Windows is not supported natively [E05]. Its ROCm include gives a general **6.3+** requirement, but the prebuilt-wheel table names older release ranges and a nightly commit; it does **not** establish a v0.31.0 ROCm wheel, digest, or tested Python/runtime combination [E05]. The selected build must therefore supply that evidence before #37 can treat the AMD path as a reproducible package. This is a source/version gap, not evidence that the AMD backend is unsupported. The CUDA include also distinguishes source builds from binary-compatible PyTorch/CUDA combinations; the engine release string alone does not pin that stack [E05].

**Consumer gate for #40:** the imported reference `precision.engine` and `engine.model.format` membership rules can emit hard failures for missing list entries. Those reference rules are unapproved baselines, and cannot implement this submission's unknown semantics for researched subsets. For example, omitted `int4` is not evidence that vLLM cannot run documented INT4 schemes. Keep these proposals as reviewed research, and require #40 to resolve evidence completeness and conditional negative checks before using them in an executable compatibility catalog. See T2-C04/C05; the frozen reference implementation is preserved.

### Release-keyed serving and adapter matrix

| Engine/version | Batching / streaming | Structured output | Tool calling / API surface | Adapters, multi-adapter and merged weights | Conditions / unknowns |
| --- | --- | --- | --- | --- | --- |
| vLLM `v0.31.0` | Continuous batching and streaming documented [E02]. Request token limits, active sequences and LoRA batch limits remain configuration/capacity inputs. | `structured_outputs` request object; xgrammar or guidance backends documented. Old `guided_*` fields were removed in `v0.12.0` [E07]. Validate the actual schema/backend; no claim all JSON Schema constructs work. | Chat/Completions/Responses and other documented routes. `user` ignored; `suffix` unsupported. `parallel_tool_calls=false` constrains responses to at most one call in this release; true permits multiple but model behavior varies [E06]. Parser, template, strictness settings and model-specific behavior qualify tool support [E08]. | Models must implement `SupportsLoRA`; startup modules and per-request model routing; multiple adapters can be batched subject to `max_loras`. Rank/layout/target modules matter. Current docs still limit default multimodal selection to one LoRA per prompt; new MoE layouts are explicitly distinguished [E09]. | Multi-LoRA serving is not arbitrary adapter composition. A provider-locked fine-tune is not automatically a downloadable adapter. Merged weights use the normal loader only after architecture/tokenizer/format/revision checks. Plugin and artifact combinations without evidence remain unknown. |
| llama.cpp `v0.7.0` | Continuous batching, slots and streaming routes documented [E14]. Requests with **different LoRA configurations are not batched together**; documented performance impact is qualitative, not measured here [E14]. | Grammar/JSON-schema-constrained output; supported-schema subset must be checked, with request `response_format` semantics [E14, E18]. | Chat/Completions and embeddings routes; upstream disclaims full OpenAI specification compatibility. Tool use uses Jinja/template handlers; parallel calls apply to some models and must be enabled [E14, E17]. | Startup adapters, per-request adapter ID/scale lists, and global scale endpoint documented. GGUF conversion is required for portable PEFT artifacts; correctness of any particular conversion remains unknown [E13, E14]. | Multiple active scales are different semantics from vLLM's per-request adapter routing. Do not transfer batching behavior between engines. Merged GGUF remains a complete model artifact with lineage, not `adapter_only=true`. |
| TGI `v3.3.7` | Continuous batching, SSE token streaming, tensor parallelism documented [E20]. | `/generate` grammar and tool-guidance flows documented [E23]. Exact schema keyword support and combined adapter/grammar behavior remain unknown here. | Messages API claims Chat Completions compatibility; native `/generate` and `/generate_stream` also documented [E20]. This is not evidence for full OpenAI API equivalence. Parallel tool-call behavior is unknown in this survey. | PEFT LoRA models can be loaded at startup via `LORA_ADAPTERS`, including pinned revisions/local paths, then selected by `adapter_id` [E22]. Source contains adapter-specific prefix-cache decisions [E25]. | Adapter composition and every quant/backend combination remain unknown. Maintenance mode affects a new-build recommendation [E20]; source examples still using container `3.3.5` do not establish a `3.3.7` container digest. |

For #25's schema acceptance cases, vLLM v0.31.0 distinguishes tool-call envelopes from argument-schema enforcement. With structural-tag parsers, required/named calls constrain the envelope; omitted or false per-tool `strict` does not by itself enforce that tool's declared argument schema. Record `strict`, `--tool-strict-level` and the structural-tag enforcement override, along with parser/template, before assuming schema enforcement [E08]. This published distinction is not a consumer test result.

### Historical rows and observed migration implications

Historical versions below are research-note comparisons only, not duplicate versions of catalog IDs. They are not proposed production deployments or evidence for later releases.

| Engine/version | Inspected published baseline | Current-release difference / research implication | Sources |
| --- | --- | --- | --- |
| vLLM `v0.10.2` (`01efc7ef781391e744ed08c3292817a773d654e6`) | FP32/FP16/BF16 options, Safetensors/PyTorch loaders; quantization hardware table; continuous batching and streaming. `guided_json`/other guided fields documented; Chat API says `parallel_tool_calls` ignored. GPU docs require NVIDIA capability at least 7.0. LoRA support is model-specific. | `v0.31.0` has a different structured-output request contract, honors the parallel-call limiting flag, raises the general CUDA requirement, and moves GGUF to a plugin. A saved build must retain its exact engine and request contract. | H01–H05; E05–E10 |
| llama.cpp `b6500` (`a7a98e0fffed794396b3fbad4dcdbbc184963645`) | MIT, GGUF, CPU/CUDA/HIP/Metal/SYCL/Vulkan paths; F16/quantized serving, continuous batching, streaming, schema output and conditional tools; multiple LoRA startup/per-request scales documented. | Current release has updated server slot/KV and split-mode controls. The `v0.7.0` adapter batching limitation is sourced at that release; no inference about undocumented b6500 behavior. | H06–H08; E14 |
| TGI `v3.3.5` (`8d029d2fc36c814e1464278b414d2d414f71cacf`) | Apache-2.0, Safetensors, FP16/BF16 launcher options, documented quantizations, continuous batching/SSE, Messages API, startup PEFT multi-adapter routing. | `v3.3.7` is the latest release observed and explicitly declares maintenance mode. LoRA/guidance/quantization documents were fetched at both tags; matching blob hashes corroborate unchanged documents, not unchanged runtime behavior. | H09; E20–E25 |

## Comparison fields

Every populated research value must reference a source ID and conditions from the matrices; unknown values stay in notes. Normative schema pointers refer to CatalogItem unless `selection` is stated. Note-only fields below are proposed comparison requirements, **not additions to the frozen v1 schema**.

| Field / JSON pointer | Type and unit | Evidence requirement / populated finding |
| --- | --- | --- |
| `/id`, `/version`, `/kind` | Stable string; release string; enum `inference_engine` | Publisher release/tag ref and resolved commit [E01]. Version is mandatory when checking support. |
| `/license/spdx_id` | SPDX string; no unit | License file at the exact release [E04, E12, E21]; model/dependency terms reviewed separately. |
| `/spec/backends` | Array of canonical backend enum strings | Release installation/source docs; map HIP to `rocm`, SYCL/Intel XPU to `oneapi` only with source context. A list is not a cross-product compatibility certificate. |
| `/spec/model_formats` | Array of canonical format enums | Exact loader/source docs [E03, E10, E13, E20]; record plugin requirement and conversion boundaries. |
| `/spec/supported_precisions` | Array of canonical precision enums | Exact dtype definition / quant implementation, with hardware and weight/activation/KV scope. No invented FP4 enum [E03, E15, E25]. |
| `selection.settings.quantization`, `.precision` | v1 enums; no unit | Selected scheme and dtype must match artifact metadata and release/backend evidence. `other` does not prove which implementation is available. |
| `selection.settings.tensor_parallel_size`, `.max_batch_tokens` | Integer GPUs/ranks; integer tokens | Release configuration plus selected hardware; values are selected inputs, not engine-wide maxima. Capacity and ResourceEstimate belong to #10. |
| Architecture/model revision (note-only) | String identifier + immutable revision | Tagged architecture registry/support docs and exact model metadata [E02, E16, E24]. Model-family examples do not establish every model's support. |
| Quantization detail (note-only) | Exact scheme, group/block/layout, plugin/kernel revision, dtype role | Artifact metadata and matching loader/kernel docs [E10, E15, E19, E25]. Mixed formats retain their names and effective storage overhead. |
| Batching / streaming (note-only) | Published capability + conditions; request/token count; SSE/event semantics | Versioned serving docs [E02, E14, E20]. No universal batch-size or throughput number. |
| Structured output / tools / API (note-only) | Endpoint and protocol; schema dialect/backend; parser/template/strictness; supported/unsupported/unknown | Exact release request docs and later consumer acceptance tests [E06–E08, E14, E17, E18, E23]. |
| Adapter support (note-only) | Adapter format/method, base revision, rank, target modules, startup/dynamic loading, routing/composition behavior | Engine and artifact lineage docs; multi-adapter batching distinguished from simultaneous composition [E09, E14, E22]. |
| Deployment constraints (note-only) | OS/runtime/build/plugin versions; networking/auth/logging conditions | Release install/security/serving docs [E05, E06, E09, E14, E20]. Separate documented requirement from untested packaging. |
| `/provenance/*` | Public URI, RFC3339 checked time, verification-status enum, notes | Claim-level pointer/condition mapping. `verified` in proposals means cited source fact was checked, not end-to-end compatibility. |

## Evidence

All entries accessed **2026-10-16**. Prices are not asserted, so currency and region are not applicable. Unless stated otherwise, grade is **Primary documentation**: publisher source/config/license inspected at the named release. README serving-capability summaries are **Vendor claim** until corroborated; this work contains no independent measurements. Support tables are publisher statements, not reproduced compatibility results. Links and short factual paraphrases are recorded; no raw evidence archives, weights or private inputs are redistributed. License references do not grant blanket rights to model artifacts or hosted-service content; reuse and refresh approval remain with #41.

| ID | Publisher and primary URL | Version / evidence scope / limitations |
| --- | --- | --- |
| E01 | GitHub APIs: [vLLM latest](https://api.github.com/repos/vllm-project/vllm/releases/latest), [llama.cpp latest](https://api.github.com/repos/ggml-org/llama.cpp/releases/latest), [TGI latest](https://api.github.com/repos/huggingface/text-generation-inference/releases/latest); [vLLM tag](https://api.github.com/repos/vllm-project/vllm/git/ref/tags/v0.31.0), [llama tag object](https://api.github.com/repos/ggml-org/llama.cpp/git/tags/757cad021b357f417065ddbc41a6e8f87c1f8136), [TGI tag](https://api.github.com/repos/huggingface/text-generation-inference/git/ref/tags/v3.3.7) | Current release inventory and commit resolutions only. Latest endpoints are mutable; checked date is essential. |
| E02 | vLLM [README](https://github.com/vllm-project/vllm/blob/v0.31.0/README.md) | v0.31.0; Vendor claim for broad model families, batching, streaming, parallelism, APIs and hardware/plugin list. No throughput figure adopted. |
| E03 | vLLM [model config](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/config/model.py) and [load config](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/config/load.py) | v0.31.0; dtype and format definitions; model/pipeline parallel validation conditions. |
| E04 | vLLM [LICENSE](https://github.com/vllm-project/vllm/blob/v0.31.0/LICENSE) | v0.31.0; Apache-2.0 engine source. Preserve notices/conditions; no model license inference. |
| E05 | vLLM [GPU installation](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/getting_started/installation/gpu.md), [CUDA details](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/getting_started/installation/gpu.cuda.inc.md), [ROCm details](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/getting_started/installation/gpu.rocm.inc.md) | v0.31.0; Linux/Python and variant-specific GPU/build constraints. General Python 3.10–3.13; ROCm wheels specifically Python 3.12. Default CUDA binaries 12.9; other variants documented. These are published requirements, not installation results. |
| E06 | vLLM [OpenAI-compatible server](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/serving/online_serving/openai_compatible_server.md) | v0.31.0; exact endpoints/parameter caveats; `--api-key` does not protect every endpoint. |
| E07 | vLLM [structured outputs](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/features/structured_outputs.md) | v0.31.0; request migration, backend selection. Some surrounding examples mention additional backends; use the release's actual available backend/config rather than assuming every example combination works. |
| E08 | vLLM [tool calling](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/features/tool_calling.md) | v0.31.0; parsers, templates, auto/required/named modes and strictness conditions. No semantic tool correctness guarantee. |
| E09 | vLLM [LoRA](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/features/lora.md) | v0.31.0; per-request routing, batched adapters, rank/layout, runtime load endpoints and production risk of remote/dynamic loading. |
| E10 | vLLM [quantization matrix](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/features/quantization/README.md) and [GGUF](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/features/quantization/gguf.md) | v0.31.0; scheme/hardware statements, experimental GGUF plugin requirement. Matrix still shows Volta cells despite the newer general CUDA minimum: preserve conflict as unknown for such tuples. |
| E11 | ggml-org [README](https://github.com/ggml-org/llama.cpp/blob/v0.7.0/README.md) | v0.7.0; Vendor claim for CPU/GPU hybrid and hardware support; backend inventory and CLI examples. |
| E12 | ggml-org [LICENSE](https://github.com/ggml-org/llama.cpp/blob/v0.7.0/LICENSE) | v0.7.0; MIT engine source; attribution/notice condition; model rights separate. |
| E13 | ggml-org [models](https://github.com/ggml-org/llama.cpp/blob/v0.7.0/docs/models.md) | v0.7.0; GGUF requirement, conversion and managed hosting references. Does not pin a hosted deployment. |
| E14 | ggml-org [server README](https://github.com/ggml-org/llama.cpp/blob/v0.7.0/tools/server/README.md) | v0.7.0; slots/KV controls, SSE/API caveats, LoRA routing/scales/batching, health/metrics. Documentation still mixes old and new CLI examples; do not treat every command as tested. |
| E15 | ggml-org [GGML types](https://github.com/ggml-org/llama.cpp/blob/v0.7.0/ggml/include/ggml.h) | v0.7.0; F32/F16/BF16 and named quantized tensor types. A type enum alone is not proof of complete backend operator support. |
| E16 | ggml-org [architecture registry](https://github.com/ggml-org/llama.cpp/blob/v0.7.0/src/llama-arch.cpp) | v0.7.0; architecture identifiers, not quality or conversion certification. |
| E17 | ggml-org [function calling](https://github.com/ggml-org/llama.cpp/blob/v0.7.0/docs/function-calling.md) | v0.7.0; native/generic template handlers and conditional parallel tools. Generic capability is a vendor claim, not verification of each model. |
| E18 | ggml-org [JSON-schema grammar tests](https://github.com/ggml-org/llama.cpp/blob/v0.7.0/tests/test-json-schema-to-grammar.cpp) | v0.7.0; schema conversion tests are release evidence, not tests run by this project. |
| E19 | ggml-org [quantization guide](https://github.com/ggml-org/llama.cpp/blob/v0.7.0/tools/quantize/README.md) | v0.7.0; named GGUF quantizations, high-precision source artifacts and conversion workflow. No sample benchmark figures promoted. |
| E20 | Hugging Face [README](https://github.com/huggingface/text-generation-inference/blob/v3.3.7/README.md) | v3.3.7; maintenance declaration; Vendor claim for serving features, hardware and service use. Example container commands still use 3.3.5; no invented current image digest. |
| E21 | Hugging Face [LICENSE](https://github.com/huggingface/text-generation-inference/blob/v3.3.7/LICENSE) | v3.3.7; Apache-2.0 engine source. |
| E22 | Hugging Face [LoRA](https://github.com/huggingface/text-generation-inference/blob/v3.3.7/docs/source/conceptual/lora.md) | v3.3.7; PEFT startup adapters, adapter IDs/revisions and request routing; prose has a `lora_model`/`adapter_id` naming inconsistency, so code/API payload is authoritative and consumer test required. |
| E23 | Hugging Face [guidance](https://github.com/huggingface/text-generation-inference/blob/v3.3.7/docs/source/conceptual/guidance.md) | v3.3.7; grammar/tool guidance. The conceptual chat path is not used to override the README's actual `/v1/chat/completions` route. |
| E24 | Hugging Face [supported models](https://github.com/huggingface/text-generation-inference/blob/v3.3.7/docs/source/supported_models.md) | v3.3.7; optimized architecture list and best-effort fallback caveat. |
| E25 | Hugging Face [launcher](https://github.com/huggingface/text-generation-inference/blob/v3.3.7/launcher/src/main.rs) and [quantization](https://github.com/huggingface/text-generation-inference/blob/v3.3.7/docs/source/conceptual/quantization.md) | v3.3.7; FP16/BF16 and quantization options, EXL2 multi-shard exclusion, CUDA KV dtype conditions, adapter cache decisions. Qualitative speed claims not adopted. |
| E26 | GitHub [TGI repository metadata](https://api.github.com/repos/huggingface/text-generation-inference) | Current repository, accessed 2026-10-16; `archived=true`. This does not define a release support window, deployment image or security status. |
| H01 | vLLM [home](https://docs.vllm.ai/en/v0.10.2/), [engine arguments](https://docs.vllm.ai/en/v0.10.2/configuration/engine_args.html) | v0.10.2; historical batching/streaming, loader/dtype and configuration baseline. |
| H02 | vLLM [OpenAI server](https://docs.vllm.ai/en/v0.10.2/serving/openai_compatible_server.html), [structured output](https://docs.vllm.ai/en/v0.10.2/features/structured_outputs.html) | v0.10.2; historical ignored parameter and guided request format. |
| H03 | vLLM [GPU](https://docs.vllm.ai/en/v0.10.2/getting_started/installation/gpu.html) | v0.10.2; historical NVIDIA minimum 7.0, Linux and runtime conditions. |
| H04 | vLLM [quantization source](https://github.com/vllm-project/vllm/blob/v0.10.2/docs/features/quantization/README.md) | v0.10.2; hardware/scheme table checked in tagged source as well as versioned docs. |
| H05 | vLLM [LoRA source](https://github.com/vllm-project/vllm/blob/v0.10.2/docs/features/lora.md) | v0.10.2; historical model-specific adapter routing. |
| H06 | ggml-org [README](https://github.com/ggml-org/llama.cpp/blob/b6500/README.md) | b6500; historical GGUF/hardware baseline. |
| H07 | ggml-org [server](https://github.com/ggml-org/llama.cpp/blob/b6500/tools/server/README.md) | b6500; historical serving/adapters/API baseline. |
| H08 | ggml-org [LICENSE](https://github.com/ggml-org/llama.cpp/blob/b6500/LICENSE) | b6500; historical MIT engine source. |
| H09 | Hugging Face [README](https://github.com/huggingface/text-generation-inference/blob/v3.3.5/README.md), [launcher](https://github.com/huggingface/text-generation-inference/blob/v3.3.5/launcher/src/main.rs), [LoRA](https://github.com/huggingface/text-generation-inference/blob/v3.3.5/docs/source/conceptual/lora.md), [LICENSE](https://github.com/huggingface/text-generation-inference/blob/v3.3.5/LICENSE) | v3.3.5; historical capability/config/license baseline. |

Historical tag/commit pairs were also checked through [vLLM](https://api.github.com/repos/vllm-project/vllm/git/ref/tags/v0.10.2), [llama.cpp](https://api.github.com/repos/ggml-org/llama.cpp/git/ref/tags/b6500), and [TGI](https://api.github.com/repos/huggingface/text-generation-inference/git/ref/tags/v3.3.5) refs on 2026-10-16.

## Compatibility proposals

[Engine rules](rules/engine-compatibility.md) use the shared template, including applicability, participating pointers, assertion, severity, missing-data policy, remediation and synthetic passing/failing/unknown examples. Four groups each separate a fixed `error` constraint, `warning` evidence check and `info` applicability diagnostic; outcome never changes a rule's severity. Status is **proposed** for #40; all joint runtime claims remain unverified. Documentation-supported premises are separated from proposed policy. Schema validation does not approve a rule.

The main constraints are artifact loader + exact architecture, selected hardware + actual kernel/backend, adapter lineage/layout + loading mode, and the application's actual API request contract. Missing or conflicting tuple evidence yields `unknown`, not `pass`. An API-only build with no local runtime is `skipped` for local-engine checks. Severity (`info/warning/error`) is independent of outcome (`pass/fail/unknown/skipped`).

### Proposed #40 contract follow-up (no v1 changes)

The flat v1 format/backend/precision arrays cannot express conditional tuples, plugin requirements, architecture revisions, adapter composition, or schema/parser limitations. Submit these examples to @tynamite (#40), with @zwright8 (#6/#7), @Mattycodes69 (#10/#11), @appletechie (#33), @CompleteDotTech (#25), and @PUSHINGSQUARES (#37/#38) as affected reviewers:

- vLLM v0.31.0 + `gguf` requires a separately versioned plugin; a generic `model_formats: ["gguf"]` would conceal it.
- llama.cpp v0.7.0 can route multiple scales, but requests with different adapter configurations are not batched together. A single `adapter_support: true` would erase that constraint.
- Tool behavior requires `(engine version, model revision, template/parser, request fields, strictness, streaming mode)`; structured output also needs grammar/backend/schema scope.
- Precision needs weight/activation/KV roles and exact quantization scheme. Mixed GGUF formats and FP4 variants must not silently become v1 enum values.

Propose a versioned conditional-support record with explicit evidence status/outcome, source-date/conditions, and exact plugin/artifact revisions. The shape and canonical extension names are **open**, so no invented field is added to v1. Migration must preserve old engine selections/request contracts, let #42 re-evaluate affected saved builds, and avoid interpreting previously absent tuple data as incompatibility. #40 decides schema version and ruleset migration; #41 decides freshness/reuse metadata.

## Pricing and capacity

No engine-service price or performance rate is asserted. Engine source licensing does not imply zero hosting/operations cost. `billing_class: "unknown"` is intentional in the proposals; hosting/provider service rates remain with #9/#5 and costing semantics with #39. No engine Pricebook is warranted by this evidence set.

GPU weight/KV/runtime sizing, precision overhead, tensor-parallel memory placement, adapter residency, cold-start and load/concurrency measurements belong to #10. Handoff inputs: exact engine/build/plugins, model/tokenizer revision, quant layout and dtype roles, adapter ranks/counts/targets, active sequences and token budget. Multi-GPU support does not prove pooled usable VRAM. No ResourceEstimate is fabricated from documentation summaries.

## Recommendation and rationale

Use vLLM as the first GPU-serving candidate for a documented supported tuple, and llama.cpp as the first CPU/edge/GGUF candidate; treat this as a **research recommendation**, pending workload requirements and corroboration. Their documented feature sets explain the split [E02, E05, E11–E14]. Keep TGI visible for existing/managed environments while warning new-build reviewers about its published maintenance mode [E20]. No universal winner or latency/throughput ranking is established.

For agents (#25), obtain a consumer acceptance set for tool modes, parallel-call limiting, streaming deltas/IDs, tool-result round trips, strict schema behavior, errors and cancellation. Engine support for emitting a tool call does not itself execute a tool or provide MCP authorization. For RAG (#16/#7), preserve tokenizer/chat-template context accounting, output reservation, truncation behavior, and separate generation/embedding/reranking models. Retrieval, citations and ACL enforcement remain with T3. These are proposed handoff requirements, not already-agreed product requirements.

For deployment (#37), carry an immutable artifact/build/plugin inventory, exact API contract, model/adapter access terms, protected administrative endpoints, and model-specific loading checks. vLLM explicitly warns that API-key authentication does not cover every endpoint [E06], and dynamic/remote LoRA management has separate risk conditions [E09]. For monitoring (#38), request queue/TTFT/decode/end-to-end timing, token/concurrency/cache pressure, load/parser/schema failures, and separate startup versus steady-state signals; thresholds must come from #2 and #10, not invented constants. Do not log retrieved text, prompts or tool arguments merely to count these events; #38 owns its privacy/retention decision.

### Version retention proposal

Owner decision remains open: @Mattycodes69 (#11), with @tynamite (#40/#41) and #42 review. Proposed policy: retain every release actually referenced by a saved build, evidence record or rule; retain immutable research snapshots and migrations rather than overwriting old support with `latest`; prioritize fresh research for the current stable release and deployed builds; archive superseded comparisons in notes until multi-version intake is approved. A new release changes no existing tuple outcome automatically. Do not impose an unsupported arbitrary number of historical versions or freshness days. Current intake allows one version per catalog ID [RESEARCH_WORKFLOW.md](../../docs/RESEARCH_WORKFLOW.md); historical versions above therefore stay out of `catalog/proposals/`.

## Structured artifacts

- [vLLM v0.31.0 CatalogItem](../../catalog/proposals/t2-engine-vllm-v0.31.0.json)
- [llama.cpp v0.7.0 CatalogItem](../../catalog/proposals/t2-engine-llama-cpp-v0.7.0.json)
- [TGI v3.3.7 CatalogItem](../../catalog/proposals/t2-engine-tgi-v3.3.7.json)
- [Proposed rules for #40](rules/engine-compatibility.md)

Required canonical fields are populated from the inspected sources, with explicit source-to-field notes. No source, host or model references are required by the inference-engine spec, so these records introduce no unresolved catalog references. No resource/evaluation payload or external binary evidence artifact is submitted; public pinned source links suffice here. Evidence manifests would be needed if a later experiment records external model/test artifacts. No synthetic vendor record or runtime result is presented.

## Open questions and handoffs

All ownership below was read from live GitHub assignees on 2026-10-16. No consuming-owner confirmation was present when inspected; requests and PR reviews must be linked by the orchestrator when received. Shared ownership by the same assignee does not count as an acknowledgment.

| Required #11 consumer | Live owner | Concrete handoff / required confirmation | State |
| --- | --- | --- | --- |
| #10 GPU / Compute | @Mattycodes69 | Accept exact-release hardware/kernel caveats, adapter/KV inputs and non-pooling assumption for sizing. Reconcile v0.31.0 CUDA minimum against historical v0.10.2 estimates. | Pending owner acknowledgment |
| #25 Agent Framework | @CompleteDotTech | Accept conditional tool/schema/API contract, propose consumer request/response fixtures and required endpoints. | Pending owner acknowledgment |
| #33 Fine-Tuned Model | @appletechie | Confirm adapter vs merged artifact semantics, immutable base/tokenizer lineage, rank/layout/targets and provider lock-in treatment. | Pending owner acknowledgment |
| #37 Deployment | @PUSHINGSQUARES | Accept version/build/plugin pins, model/adapter loading checks and admin endpoint exposure constraints. | Pending owner acknowledgment |
| #38 Monitoring | @PUSHINGSQUARES | Accept release-specific signal mapping and measurement/privacy inputs; define thresholds from workload evidence. | Pending owner acknowledgment |

| Open decision / missing evidence | Follow-up owner and issue | Impact / independent work |
| --- | --- | --- |
| Approve retention policy, lifecycle choices and candidate breadth | @Mattycodes69 #11; @tynamite #40/#41 | Historical and current rows remain traceable; do not label pending policy as adopted. |
| Corroborate actual model/backend/quant/adapter tuples | @Mattycodes69 #11/#10; @zwright8 #6 | No combination is certified by this note; owner can add a second source or reproducible test. Documentation research proceeds. |
| Resolve v0.31.0 Volta cells versus CUDA minimum 7.5 | @Mattycodes69 #11, @tynamite #40/#41 | Such combinations are unknown despite positive quantization-table cells; current installation requirement is separately recorded. |
| Pin vLLM GGUF plugin and evaluate exact compatibility | @Mattycodes69 #11; @appletechie #33 | GGUF excluded from current vLLM canonical proposal; llama.cpp remains a separately sourced candidate. |
| Pin the vLLM v0.31.0 ROCm package/build and Python/runtime combination | @Mattycodes69 #11/#10; @PUSHINGSQUARES #37 | Tagged installation prose and older/nightly wheel examples do not identify a tested release binary. AMD capability stays documented, while package reproducibility remains unknown. |
| Preserve adapter lineage, merged licenses and non-portable API fine-tunes | @appletechie #33; @zwright8 #6; #5 @zwright8 | Required before an artifact-level serving compatibility result. |
| Agree context budget/tokenizer behavior and retrieval checks | @zwright8 #7; @zabyxc01 #16 | T3 ACL/citation ownership preserved; no retrieval semantics moved into the engine. |
| Exposed managed engine versions/configuration and rate limits | @Mattycodes69 #9; #5 @zwright8 | Unknown managed tuple remains unknown; provider API evaluation proceeds independently. |
| Approve source reuse and freshness thresholds | @tynamite #41 | No fixed refresh interval or unrestricted redistribution claim is invented. Recheck release/config/source changes before promotion. |

## Validation and acceptance assessment

Validation results are recorded after the files are written and independently checked; the integrated PR must include the repository baseline checks from Python 3.12. Schema validation checks structure, provenance shape and reference consistency; it cannot verify source freshness, license interpretation, actual runtime support or consuming-owner acceptance.

Targeted recheck on 2026-10-16 used Python **3.12.14** from the repository `.venv`: each of the three listed engine proposals passed `contracts/v1/reference/validate_payload.py` against `catalog-item.schema.json`; `git diff --check` passed for this note and its rules. The Markdown rule clauses are review proposals and are not presented as schema-validated executable rules. The orchestrator records the integrated baseline checks separately after all T2 edits settle.

| Exact #11 acceptance criterion | Evidence / artifact | Current assessment |
| --- | --- | --- |
| Support matrix keyed by engine version with sources | Current/historical matrices, E01–E25/H01–H09 | Authored; bounded documented support, unverified combinations explicit; owner evidence review pending |
| Rules in the #40 format, including `unknown` for unverified combinations | `rules/engine-compatibility.md` | Authored; proposed/unverified; #40 acceptance pending |
| Decision record merged at `research/T2-infrastructure/inference-engine.md` following research method | This template-based record | Not merged; PR/reviewer/merge required |
| Candidate set covers relevant API / managed / self-hosted modes or explains non-applicability | Deployment-mode table and version exposure conditions | Authored; owner review pending |
| Comparison fields defined with type, unit and evidence requirement | Comparison-fields table | Authored; canonical versus note-only fields distinguished |
| Compatibility rules/warnings shared format; verified rules separated from hypotheses | Proposed rules, sourced premises, evidence status | Authored; no verified joint compatibility rule claimed |
| Every factual/numeric claim primary-sourced with access date and relevant conditions | Claim-source matrices and dated evidence table | Source inspection completed for cited findings; no runtime measurements; independent evidence review pending |
| Each downstream handoff confirmed by consuming owner, linked | Required-consumer table | Unsatisfied: five acknowledgments pending |
| Open questions recorded with named follow-up owner | Open-decision table | Authored; owner decisions remain open |

This issue is not complete: merged reviewed work and confirmed handoffs are still required. The main orchestrator owns PRs, GitHub checklists/Project status and the workstream summary.
