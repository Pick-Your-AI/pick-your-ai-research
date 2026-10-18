# Inference engine: release-scoped serving support

Issue: #11 · Contract: 1.0.0 · Kind: `inference_engine`
Status: partial research and central corrections merged in #75/#101; scoped receipts reconciled; runtime tuples remain unverified
Last vendor research: 2026-10-16 (main matrix); 2026-10-18 (build supplement; lifecycle source recheck) · Owner-decision reconciliation: 2026-10-18 · Research owners: @Mattycodes69, @zwright8 (live GitHub assignees)

## User decision

Which runtime can serve the selected model artifact, on the selected hardware, with the request behavior the application needs? Choose an **engine version + artifact revision + backend/build + configuration**. An engine name, file suffix, shared API route, or accelerator precision list alone cannot establish this choice.

This note compares a bounded current candidate set and retains explicit historical comparisons. GitHub's latest-release endpoints returned vLLM `v0.31.0`, llama.cpp `v0.7.0`, and TGI `v3.3.7` when checked on 2026-10-16 [E01]. These are latest releases *observed in that check*, not a claim that every wheel, container, plugin, or managed endpoint runs them. No inference service was deployed and no runtime benchmark or compatibility experiment was run.

| Deployment mode | Treatment |
| --- | --- |
| API | A model-provider API can omit a local engine and GPU under the canonical component guide. Provider behavior, model versions, API quotas, retention, and prices remain with #5. A route described as OpenAI-compatible is insufficient evidence of a particular serving engine/version. |
| Managed | Evaluate the exposed API and provider guarantees separately. Use this matrix only if the endpoint exposes a verifiable engine version, build/plugins, model revision, and relevant flags. llama.cpp documents a Hugging Face Inference Endpoints hosting path [E13]; TGI describes its use in Hugging Face services [E20]. Neither proves the current managed product's deployed version or every feature. Undisclosed versions/configurations remain unknown; #9 owns hosting comparison. |
| Self-hosted | All three candidates have source and serving instructions [E02, E05, E11, E14, E20]. The matrices below describe published capability under stated conditions, not installation success or production readiness. #37 owns packaging, rollout and readiness procedures; #10 owns capacity. |

Sources are primary, release-pinned documentation or source. Matrix cells are documentation findings, not independently verified joint compatibility. The adopted #41 interim policy [E27] separates the rule outcome from its evidence status: eligible versioned publisher documentation can support `pass`, labelled **unverified** until independently reproduced or corroborated under [governance](../../docs/governance.md). Repeated pages from one publisher are not independent reproduction. Missing eligible evidence remains `unknown`; independent reproduction is not required for every documentation-supported constraint to pass.

The [GGUF plugin and ROCm build supplement](engine-build-evidence.md), source-checked
2026-10-18, pins plugin v0.0.5 and the vLLM v0.31.0 ROCm recipe defaults. It
distinguishes CUDA release wheels from the documented ROCm source path; exact joint
compatibility and a reproducible selected binary/runtime tuple remain unknown.

## Candidate options

### Current release inventory and scope

The following commits were resolved from the publishers' release tags [E01]. llama.cpp's annotated tag was dereferenced to its commit. The commit column and catalog provenance preserve immutable source revisions; release-tag links in the comparison evidence identify the documented release, while mutable `latest` endpoints are used only to date the inventory observation.

| Catalog ID | Examined release | Resolved source commit | Proposed catalog lifecycle |
| --- | --- | --- | --- |
| `inference-vllm` | `v0.31.0` | `db9527a46873454610df6dbedf79a36d6bf1a7f6` | `active`, a proposed catalog classification |
| `inference-llama-cpp` | `v0.7.0` | `620d2225cc436ab0b001e3200e590e3b286ef9ab` | `active`, a proposed catalog classification |
| `inference-tgi` | `v3.3.7` | `dfb3fbe78e0d1d69251bd33065591c61bafdfaa8` | `deprecated` for new-build recommendations, proposed because the release README says maintenance mode [E20] |

These lifecycle values are research-catalog choices accepted with constraints by @zwright8 at the reviewed revision linked in the retention section; @Mattycodes69's concurrence remains proposed in this follow-up. They do not assert an upstream support window or security certification. The GitHub repository API reported TGI as archived in the original check [E26] and again on 2026-10-18 [E28]; this repository lifecycle observation is separate from the pinned release's contents. TGI remains relevant to existing and managed installations. SGLang, TensorRT-LLM, Ollama and MLX are expansion candidates, not evaluated entries here; their unknown status must not be interpreted as lack of support.

### Release-keyed artifact and hardware matrix

Lists are bounded documented examples, not exhaustive architecture registries or Cartesian products of compatible choices. `unknown` means this research lacks sufficiently scoped evidence. A documented feature is not a performance result. Engine licenses below concern engine source; they do not replace model, adapter, dependency, container, or service terms [E04, E12, E21].

| Engine/version | Engine license | Architecture examples | Artifact formats | Quantization and precision | Hardware backends and limits | Claim sources |
| --- | --- | --- | --- | --- | --- | --- |
| vLLM `v0.31.0` | Apache-2.0 | Llama/Qwen/Gemma decoders; Mixtral/DeepSeek-V3 MoE; Mamba/hybrid; LLaVA/Qwen-VL; embedding/retrieval families. Exact architecture/revision and feature combinations still require the supported-model entry. | Safetensors and PyTorch weight loaders. GGUF is documented but now requires a separately installed out-of-tree plugin; plugin v0.0.5 is source-pinned in the supplement, while joint compatibility remains unknown. | FP32/FP16/BF16 dtype options; documented quantization families include FP8, INT8, INT4, GPTQ/AWQ, compressed-tensors, ModelOpt and TorchAO. MXFP4/NVFP4/MXFP8 names in upstream do not become new v1 precision enums. Weight, activation and KV dtypes are distinct. | Core NVIDIA CUDA, AMD ROCm, Intel GPU, CPU paths; additional devices via plugins. CUDA installation requires compute capability **7.5 or higher** and a matching binary stack. ROCm docs list MI300 (`gfx942`) and ROCm **6.3 or above**; wheel variant requirements differ. | E02–E10 |
| llama.cpp `v0.7.0` | MIT | Source registry includes `llama`, `llama4`, `qwen2`, `qwen3`, `gemma2`, `gemma3` and other architecture identifiers. Registry presence does not verify every conversion, modality, operator or quant/backend tuple. | GGUF required; upstream conversion tools are a separate artifact transformation. GGUF LoRA adapters are distinct from base GGUF weights. | GGML F32/F16/BF16 types; named GGUF quantizations including Q4_K_M and Q8_0. Mixed/block quantizations must retain their exact scheme, rather than being reduced to an assumed uniform bit width. | CPU, CUDA, AMD HIP, Metal, SYCL and Vulkan documented; other backends also listed. CPU+GPU offload documented. Backend compilation and operator support remain build-specific; no blanket memory pooling or edge latency guarantee. | E11–E17 |
| TGI `v3.3.7` | Apache-2.0 | Tagged model list includes Llama, Gemma, Mistral/Mixtral, Qwen2, DeepSeek V2/V3, T5 and selected multimodal families. Fallback Transformers loading is best effort, not guaranteed optimization. | Safetensors loading documented. Do not infer GGUF support in the default backend from the existence of optional alternative backend code. | Launcher dtype options FP16/BF16. Quantization docs list GPTQ/AWQ/Marlin/EXL2, bitsandbytes, EETQ and FP8; EXL2 explicitly does not support tensor parallelism with more than one shard. | README documents NVIDIA and AMD paths plus integrations for additional devices. Its explicit AMD note names MI210/MI250, so MI300X for this release remains unknown in this survey. CPU fallback is described as outside its intended platform. | E20–E25 |

The canonical proposals deliberately contain conservative subsets of formats/backends/precisions supported by inspected sources. Omission from an **unmarked** list is not negative evidence. The scoped completeness finding below is the exception authorized by #40 [E27]. In particular, llama.cpp's proposal records only F32/F16/BF16 as canonical precision entries; its mixed GGUF quantizations remain named findings above. vLLM's proposal excludes GGUF because the flat list cannot express the plugin/backend/model conditions detailed in the build supplement. Optional global booleans and `max_batch_size` are omitted: they would hide model/parser/configuration conditions or imply a universal capacity ceiling.

| Release and list | Coverage finding | Effect of absence |
| --- | --- | --- |
| llama.cpp `v0.7.0`, direct model-loader formats | **Complete: GGUF only**, scoped to the direct loader's file format [E13, E27]. Conversion tools and adapter/architecture support are separate. | A directly supplied Safetensors or other non-GGUF model fails the loader-format constraint; valid GGUF alone does not establish architecture/backend support. |
| All other format, architecture, backend and precision lists in this note | **Unmarked**; bounded documented entries, without an exhaustiveness claim | Absence yields `unknown`. An explicit unsupported statement in eligible release-scoped documentation can still yield `fail`. |

For deployment consumers, vLLM v0.31.0's GPU installation page specifies Linux and Python **3.10–3.13**, and says Windows is not supported natively [E05]. Its ROCm include gives a general **6.3+** requirement, but the prebuilt-wheel table names older release ranges and a nightly commit; it does **not** establish a v0.31.0 ROCm wheel, digest, or tested Python/runtime combination [E05]. The selected build must therefore supply that evidence before #37 can treat the AMD path as a reproducible package. The build supplement narrows the source gap with pinned recipe defaults; selected binary reproducibility remains unknown, without implying AMD is unsupported. The CUDA include also distinguishes source builds from binary-compatible PyTorch/CUDA combinations; the engine release string alone does not pin that stack [E05].

**Consumer gate for #40:** the imported reference `precision.engine` and `engine.model.format` membership rules can emit hard failures for missing list entries. The owner accepted the completeness distinction above, but executable use still waits on CD-1/CD-3 and a versioned ruleset [E27]. Until coverage metadata exists, the imported membership checks must not be treated as authoritative negative evidence for an unmarked list. For example, omitted `int4` is not evidence that vLLM cannot run documented INT4 schemes. T2-C04/C05 are accepted into the central queue with constraints; the frozen reference implementation is preserved.

**Resolved conflict: vLLM `v0.31.0` on Volta.** E10's positive Volta matrix cells are **superseded for this release** by E05's explicit CUDA minimum of compute capability 7.5; Volta is 7.0 [E27]. Under #41's conflict order, a stated requirement outranks a capability listing from the same publisher and version. The resulting joint-support constraint is `fail`, with evidence labelled unverified; it is not a runtime measurement or a conclusion about historical v0.10.2.

### Release-keyed serving and adapter matrix

| Engine/version | Batching / streaming | Structured output | Tool calling / API surface | Adapters, multi-adapter and merged weights | Conditions / unknowns |
| --- | --- | --- | --- | --- | --- |
| vLLM `v0.31.0` | Continuous batching and streaming documented [E02]. Request token limits, admitted sequences and LoRA batch limits remain configuration/capacity inputs. | `structured_outputs` request object; xgrammar or guidance backends documented. Old `guided_*` fields were removed in `v0.12.0` [E07]. Validate the actual schema/backend; no claim all JSON Schema constructs work. | Chat/Completions/Responses and other documented routes. `user` ignored; `suffix` unsupported. `parallel_tool_calls=false` constrains responses to at most one call in this release; true permits multiple but model behavior varies [E06]. Parser, template, strictness settings and model-specific behavior qualify tool support [E08]. | Models must implement `SupportsLoRA`; startup modules and per-request model routing; multiple adapters can be batched subject to `max_loras`. Rank/layout/target modules matter. Current docs still limit default multimodal selection to one LoRA per prompt; new MoE layouts are explicitly distinguished [E09]. | Multi-LoRA serving is not arbitrary adapter composition. A provider-locked fine-tune is not automatically a downloadable adapter. Merged weights use the normal loader only after architecture/tokenizer/format/revision checks. Plugin and artifact combinations without evidence remain unknown. |
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
| Structured output requirement (proposed #81 W-R1) | Workload `output_format`; build `output_enforcement`; no new v1 JSON pointer | ENGINE-04 reads these centrally proposed requirements, then matches schema/backend/parser support [E27]. They are not fields added to the frozen contract. |
| Tools / API and implementation details (note-only) | Endpoint and protocol; schema dialect/backend; parser/template/strictness; supported/unsupported/unknown | Exact release request docs and later consumer acceptance tests [E06–E08, E14, E17, E18, E23]. |
| Adapter support (note-only) | Adapter format/method, base revision, rank, target modules, startup/dynamic loading, routing/composition behavior | Engine and artifact lineage docs; multi-adapter batching distinguished from simultaneous composition [E09, E14, E22]. |
| Deployment constraints (note-only) | OS/runtime/build/plugin versions; networking/auth/logging conditions | Release install/security/serving docs [E05, E06, E09, E14, E20]. Separate documented requirement from untested packaging. |
| `/provenance/*` | Public URI, RFC3339 checked time, verification-status enum, notes | Claim-level pointer/condition mapping. Source checking alone leaves evidence `unverified`; `verified` requires independent corroboration or reproduction under the adopted #41 policy [E27]. |

## Evidence

Vendor entries E01–E26 and historical entries H01–H09 were accessed **2026-10-16**; the owner review E27 was accessed **2026-10-17**. The new E28 lifecycle check is separately dated 2026-10-18; it does not refresh the main matrix, E01 latest-release inventory, other evidence access dates or catalog provenance. Prices are not asserted, so currency and region are not applicable. Unless stated otherwise, grade is **Primary documentation**: publisher source/config/license inspected at the named release. README serving-capability summaries are **Vendor claim** until corroborated; this work contains no independent measurements. Support tables are publisher statements, not reproduced compatibility results. Links and short factual paraphrases are recorded; no raw evidence archives, weights or private inputs are redistributed. License references do not grant blanket rights to model artifacts or hosted-service content.

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
| E10 | vLLM [quantization matrix](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/features/quantization/README.md) and [GGUF](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/features/quantization/gguf.md) | v0.31.0; scheme/hardware statements, experimental GGUF plugin requirement. Positive Volta cells are superseded by E05's explicit CUDA minimum 7.5 under E27's conflict decision: `fail` on Volta 7.0 for this release. |
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
| E27 | @tynamite [central #3/#40/#41 owner review of PR #75](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75#pullrequestreview-5550616927) | Review of merged head `9e66622a4b2698a9305274f05da9c15ae5d90b8c`, submitted 2026-10-16; accessed through GitHub API 2026-10-17. Project owner decisions: checked support may pass unverified; complete-list negatives; conflict order and Volta resolution; shared joint-support family; W-R1 output requirements; retention and interim freshness/reuse. Not independent vendor corroboration or approval of a versioned executable ruleset. |
| E28 | Hugging Face [TGI repository metadata](https://api.github.com/repos/huggingface/text-generation-inference) and [README at the existing v3.3.7 source pin](https://github.com/huggingface/text-generation-inference/blob/dfb3fbe78e0d1d69251bd33065591c61bafdfaa8/README.md) | Accessed through the GitHub API 2026-10-18. Metadata: `archived=true`, `disabled=false`. Pinned README limits maintenance to minor fixes/documentation/lightweight tasks and points new users toward other engines. Primary publisher documentation, source checked / unverified; no installed service, security or EOL conclusion. |
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

[Engine rules](rules/engine-compatibility.md) use the shared template, including applicability, participating pointers, assertion, severity, missing-data policy, remediation and synthetic passing/failing/unknown examples. Four legacy proposal groups retain a fixed `error` constraint, `warning` evidence check and `info` applicability diagnostic; outcome never changes a rule's severity. E27 accepts ENGINE-01/03 and narrows ENGINE-04's input source; ENGINE-02, COMPUTE-02 and #81 D-R3 become **one joint-support family**, rather than three independent final rules. #40 will collapse duplicate evidence/applicability clauses under CD-1; no clause rewrite is required in this follow-up. Status remains **proposed** until a versioned ruleset is reviewed. Schema validation does not approve a rule.

The main constraints are artifact loader + exact architecture, selected hardware + actual kernel/backend, adapter lineage/layout + loading mode, and the application's actual API request contract. Eligible scoped documentation can decide `pass` or `fail` while evidence stays unverified. Apply the E27 conflict order: normalize units/names, select eligible and most-specific scope, prefer the selected version or latest effective current-state claim, then rank authority by fact type. A stated requirement beats a same-publisher capability listing. Equal-ranked numbers retain median/spread and decide conservatively; `unknown` remains for no eligible evidence or unresolved equally ranked opposite yes/no claims. Those unknowns require review or a reproducible check.

Applicability is evaluated per serving component, including the local component of a hybrid build. Adapters inherit their base model's deployment. Provider-operated shared or opaque capacity is `skipped` for local-engine checks; a managed component exposing a user-selected runtime/instance remains in scope. Unknown ownership/configuration is `unknown`, not an automatic skip. E27 routes the richer component deployment/configuration key to #81/CD-3; this note does not reinterpret the frozen build-level mode field. Structured-output needs come from the proposed workload `output_format` and build `output_enforcement` (#81 W-R1), with endpoint/parser details supplying implementation evidence.

### Proposed #40 contract follow-up (no v1 changes)

The flat v1 format/backend/precision arrays cannot express conditional tuples, plugin requirements, architecture revisions, adapter composition, or schema/parser limitations. Submit these examples to @tynamite (#40), with @zwright8 (#6/#7), @Mattycodes69 (#10/#11), @appletechie (#33), @CompleteDotTech (#25), and @PUSHINGSQUARES (#37/#38) as affected reviewers:

- vLLM v0.31.0 + `gguf` requires a separately versioned plugin; a generic `model_formats: ["gguf"]` would conceal it.
- llama.cpp v0.7.0 can route multiple scales, but requests with different adapter configurations are not batched together. A single `adapter_support: true` would erase that constraint.
- Tool behavior requires `(engine version, model revision, template/parser, request fields, strictness, streaming mode)`; structured output also needs grammar/backend/schema scope.
- Precision needs weight/activation/KV roles and exact quantization scheme. Mixed GGUF formats and FP4 variants must not silently become v1 enum values.

E27 accepts T2-C04 into CD-3/CD-6: the joint tuple uses #81's configuration key, with artifact quantization metadata and adapter lineage. Exact extension schemas and executable migration remain in #40's queue; no invented field is added to v1. Migration must preserve old engine selections/request contracts, let #42 re-evaluate affected saved builds, and avoid interpreting previously absent tuple data as incompatibility. #40 owns schema version and ruleset migration; E27's interim #41 policy applies to evidence handling.

## Pricing and capacity

No engine-service price or performance rate is asserted. Engine source licensing does not imply zero hosting/operations cost. `billing_class: "unknown"` is intentional in the proposals; hosting/provider service rates remain with #9/#5 and costing semantics with #39. No engine Pricebook is warranted by this evidence set.

GPU weight/KV/runtime sizing, precision overhead, tensor-parallel memory placement, adapter residency, cold-start and load/concurrency measurements belong to #10. Handoff inputs: exact engine/build/plugins, model/tokenizer revision, quant layout and dtype roles, adapter ranks/counts/targets, admitted sequences and token budget. Engine launch admission is distinct from workload `peak_concurrency` demand in #81: queued demand does not automatically hold KV memory; #10 sizes at peak demand when admission is unknown [E27]. Multi-GPU support does not prove pooled usable VRAM. No ResourceEstimate is fabricated from documentation summaries.

## Recommendation and rationale

Use vLLM as the first GPU-serving candidate for a documented supported tuple, and llama.cpp as the first CPU/edge/GGUF candidate; treat this as a **research recommendation**, pending workload requirements and corroboration. Their documented feature sets explain the split [E02, E05, E11–E14]. Keep TGI visible for existing/managed environments while warning new-build reviewers about its published maintenance mode [E20]. No universal winner or latency/throughput ranking is established.

For agents (#25), the reciprocal owner receipts below accept the conditional interface and [FC-1–FC-6 baseline consumer specification](../../tests/fixtures/t4-engine-consumer.md), covering tool modes, parallel-call limiting, streaming deltas/IDs, tool-result round trips and strict schema behavior. The specification now also distinguishes a constrained tool envelope from argument-schema enforcement and adds FC-7 for incomplete/error/cancellation behavior, as requested in the co-owner disposition. These synthetic cases are specifications, not executed results; concrete runtime tuples and evidence placement remain to be agreed with #11/#36. Engine support for emitting a tool call does not itself execute a tool or provide MCP authorization. For RAG (#16/#7), preserve tokenizer/chat-template context accounting, output reservation, truncation behavior, and separate generation/embedding/reranking models. Retrieval, citations and ACL enforcement remain with T3; those retrieval handoffs still require their own dispositions.

For deployment (#37), carry an immutable artifact/build/plugin inventory, exact API contract, model/adapter access terms, protected administrative endpoints, and model-specific loading checks. vLLM explicitly warns that API-key authentication does not cover every endpoint [E06], and dynamic/remote LoRA management has separate risk conditions [E09]. For monitoring (#38), request queue/TTFT/decode/end-to-end timing, token/concurrency/cache pressure, load/parser/schema failures, and separate startup versus steady-state signals; thresholds must come from #2 and #10, not invented constants. Do not log retrieved text, prompts or tool arguments merely to count these events; #38 owns its privacy/retention decision.

<a id="version-retention-proposal"></a>

### Version retention and bounded candidate recommendation — 2026-10-18

@tynamite accepted this policy as proposed for #40/#41 in E27: retain every release actually referenced by a saved build, evidence record or rule; retain immutable research snapshots and migrations rather than overwriting old support with `latest`; prioritize fresh research for the current stable release and deployed builds; archive superseded comparisons in notes until multi-version intake is approved. A new release changes no existing tuple outcome automatically. Current intake allows one version per catalog ID [RESEARCH_WORKFLOW.md](../../docs/RESEARCH_WORKFLOW.md); historical versions above therefore stay out of `catalog/proposals/`. [@zwright8's #11 co-owner receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/11#issuecomment-6245442705), submitted 2026-10-18 after reviewing `39ddc2bad7bc154e345f169bec479a4e2c2ae87a` (merged through #205), accepts retention and the bounded vLLM/llama.cpp active / TGI deprecated research classifications with constraints. This is an actual scoped co-owner decision. @Mattycodes69's concurrence and #42's receiving decision remain separate; this contribution proposes the same policy for their review rather than supplying their acceptance.

The proposed continuation for @Mattycodes69's review is **retain by reference, refresh by use, and keep candidate breadth bounded**. It answers how far back to track versions by the presence of a reference, rather than an invented number of releases, age cutoff or upstream support promise.

| Decision situation | Proposed research treatment | Evidence / limit |
| --- | --- | --- |
| A saved build, evidence record or rule references an older engine release | Retain the immutable source identity, original support evidence, request/configuration tuple, evaluation outcome and migration history. A later release gets separate findings; never relabel old evidence as a new run. | E27 and zwright8's scoped receipt; #42 still decides its receiving representation. |
| A new stable release or changed deployed configuration needs research | Prioritize a source check for that selected release/configuration; record its own evidence dates and tuple. A changed current-state fact is shown as of its access date. | E27; this contribution does not discover a newer release or refresh E01. |
| An old comparison has no known build/evidence/rule reference | Keep it as dated historical notes outside the single-version-per-ID catalog intake; do not infer deletion permission or a retention duration. | Existing workflow and E27; no automatic deletion, new archive or multi-version catalog is implemented. |
| A new build is considering TGI | Keep the existing `deprecated` research recommendation and show the maintenance/archival evidence. Evaluate alternatives against the actual workload; do not silently rewrite an existing TGI selection. | E20/E28. Archive state is not a vulnerability finding, proof an installation stopped working, or a universal incompatible outcome. |
| A candidate has not been evaluated here | Leave SGLang, TensorRT-LLM, Ollama and MLX as unevaluated expansion candidates. Add research only for a named workload gap or material counterexample, with version-scoped sources and affected-owner review. | Bounded research choice, not a claim about these products' capabilities or exclusion from future consideration. |

For the existing inventory, retain vLLM as the first documented GPU-serving candidate and llama.cpp as the first CPU/offload/GGUF candidate under the conditional recommendation above. The API and managed-mode boundaries remain in the deployment table; a hidden managed engine cannot be assigned a version from this inventory. There is no new universal winner, runtime certification or security/support-window promise. Current catalog JSON lifecycle values, component versions and provenance dates are unchanged.

**Requested #42 disposition — @tynamite / @appletechie:** accept, narrow or reject retaining the original engine release, tuple, evidence and outcome for a historical saved build, with any later reevaluation and migration recorded separately. Confirm how unavailable historical dependencies and unsupported successor evaluation are distinguished. E27 routes multi-version intake through CD-7 with #41/#42; this note neither defines a successor schema nor approves a migration. The receiving decision must identify its reviewed revision; shared assignment or central retention acceptance is insufficient.

The adopted interim freshness policy distinguishes version-pinned support/specification facts, which do not expire and are rechecked when the version or source changes, from current-state prices/availability/terms, which show their access date with no invented TTL [E27]. Short paraphrases with links are permitted; automated retrieval or bulk table copying waits for #41/#60's per-source terms inventory.

## Structured artifacts

- [vLLM v0.31.0 CatalogItem](../../catalog/proposals/t2-engine-vllm-v0.31.0.json)
- [llama.cpp v0.7.0 CatalogItem](../../catalog/proposals/t2-engine-llama-cpp-v0.7.0.json)
- [TGI v3.3.7 CatalogItem](../../catalog/proposals/t2-engine-tgi-v3.3.7.json)
- [Proposed rules for #40](rules/engine-compatibility.md)

Required canonical fields are populated from the inspected sources, with explicit source-to-field notes. No source, host or model references are required by the inference-engine spec, so these records introduce no unresolved catalog references. No resource/evaluation payload or external binary evidence artifact is submitted; public pinned source links suffice here. Evidence manifests would be needed if a later experiment records external model/test artifacts. No synthetic vendor record or runtime result is presented.

This follow-up corrects all **11 provenance entries** across the three engine proposals from `verified` to `unverified` under E27's adopted #41 policy. It preserves every source URL, `checked_at`, component version, specification and licence fact. The later `updated_at` records this evidence-status correction, not a new vendor-source fetch or independent engine reproduction.

## Open questions and handoffs

The 2026-10-18 live issue/comment readback preserves #11 coassignees @Mattycodes69 and @zwright8. Scoped receiving-owner receipts exist for #10, #25 and #33; both T6 co-owners' #37/#38 responses are recorded below with their individual pins and limits. The links record the actual commenter and direction, without treating shared assignment, E27 central decisions or an incoming receipt as another owner's acceptance. Main-matrix vendor-source access dates and the historical validation paragraphs remain unchanged.

| Required #11 consumer | Live assignees | Concrete handoff / required confirmation | State |
| --- | --- | --- | --- |
| #10 GPU / Compute | @Mattycodes69, @appletechie | Accept exact-release hardware/kernel caveats, adapter/KV inputs and non-pooling assumption for sizing. Reconcile v0.31.0 CUDA minimum against historical v0.10.2 estimates. | [Accepted with constraints by @Mattycodes69](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10#issuecomment-6245205057), from that co-owner's scope; [@appletechie's later scoped acceptance](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10#issuecomment-6245668221) separately preserves exact-release build/quantization/KV/adapter constraints and non-pooling. Historical calculations remain pinned; a fit screen does not establish engine support or an SLO. |
| #25 Agent Framework | @CompleteDotTech, @Mattycodes69 | Accept conditional tool/schema/API contract, propose consumer request/response fixtures and required endpoints. | [Accepted with constraints by @CompleteDotTech](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/11#issuecomment-6233323334): preserve the complete request/runtime tuple; synthetic consumer specifications do not certify execution. |
| #33 Fine-Tuned Model | @appletechie, @Mattycodes69 | Confirm adapter vs merged artifact semantics, immutable base/tokenizer lineage, rank/layout/targets and provider lock-in treatment. | [Accepted with tokenizer/template narrowing by @appletechie](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/11#issuecomment-6230482684): #33 records added tokens and training template; #32 owns the training-data template; #11 determines engine support. |
| #37 Deployment | @appletechie, @PUSHINGSQUARES | Accept version/build/plugin pins, model/adapter loading checks and admin endpoint exposure constraints. | [@appletechie's historical accept, integration-pending response](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/11#issuecomment-6245668428) retains `66b46d4`. [@PUSHINGSQUARES confirms with constraints](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/11#issuecomment-6247689868), checking `9192d5d`: #246's ENGINE map is delivered; engine routes use S45/R30 rather than tool/MCP check R18. Research mapping is accepted without an executable rule, selected tuple or actual deployment result. |
| #38 Monitoring | @appletechie, @PUSHINGSQUARES | Accept release-specific signal mapping and measurement/privacy inputs; define thresholds from workload evidence. | [@appletechie's historical narrowing](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/11#issuecomment-6245668428) retains `66b46d4`. [@PUSHINGSQUARES narrows](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/11#issuecomment-6247689868), checking `9192d5d`: source-reconciled signals and version/build/config evidence fields are inputs, not required metric labels. `_total` exposition still needs a live scrape; missing series are unavailable, not zero. New llama.cpp signal IDs wait for a selected build/tuple. |

For the reciprocal **#25 → #11** direction, [@zwright8's scoped receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/11#issuecomment-6242698282) and [@Mattycodes69's co-owner receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/11#issuecomment-6245204677) each accept with constraints. Preserve engine/build/plugins/backend, model/tokenizer revisions, quantization and adapter/base lineage, template/parser, endpoint, request controls/`tool_choice`, strictness/schema/grammar, streaming/parallel behavior and decoding mode. T4 supplies consumer specifications; #11 retains support evidence and execution scope. Unsupported controls stay scoped exclusions and missing eligible evidence stays unknown. Historical minimum-version or Ollama statements are not adopted as current T2 support or a new candidate selection. FC-5/FC-7 below the linked baseline address the requested additional specification details; no runtime case was executed here.

For **#10 → #11**, [@Mattycodes69 accepts with constraints from the receiving-owner scope](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/11#issuecomment-6245204677): reuse distinct accelerator/profile IDs, per-device allocation and named uncertainty without pooling nominal VRAM. Carry exact artifact/quantization/kernel/backend/build, driver/topology and per-rank KV/adapter placement. Expanded resident sequence demand and engine admission must share a domain; unknown admission or geometry remains explicit. Capacity screens remain separate from engine support and SLO evidence. Changed releases/configurations require eligible scoped evidence; @appletechie's #10 co-owner scope is not inferred.

| Open decision / missing evidence | Follow-up owner and issue | Impact / independent work |
| --- | --- | --- |
| Confirm T2 retention/lifecycle choices and candidate breadth | @Mattycodes69 and @zwright8 #11; #42 owner | E27 central acceptance and zwright8's scoped co-owner receipt are recorded; Mattycodes69 concurrence is proposed above, and #42 receiving disposition remains pending. |
| Corroborate actual model/backend/quant/adapter tuples | @Mattycodes69 #11/#10; @zwright8 #6 | No combination is certified by this note; owner can add a second source or reproducible test. Documentation research proceeds. |
| Apply resolved v0.31.0 Volta conflict to selected tuples | @Mattycodes69 and @zwright8 #11; @tynamite #40 | E27 resolves `fail`: the CUDA minimum supersedes Volta matrix cells. No further policy decision is needed for this conflict; executable ruleset work stays with #40. |
| Evaluate exact vLLM/GGUF plugin compatibility | @Mattycodes69 #11; @appletechie #33 | [Plugin v0.0.5 source pinned](engine-build-evidence.md); vLLM dependency is unversioned. Joint compatibility remains unknown, so GGUF stays out of the flat canonical subset. |
| Pin the selected vLLM v0.31.0 ROCm binary and Python/runtime combination | @Mattycodes69 #11/#10; @PUSHINGSQUARES #37 | [Release recipe defaults inspected](engine-build-evidence.md), including mutable image/branch hazards. No tested release binary or resolved dependency lock is established. |
| Preserve adapter lineage, merged licenses and non-portable API fine-tunes | @appletechie #33; @zwright8 #6; #5 @zwright8 | Required before an artifact-level serving compatibility result. |
| Agree context budget/tokenizer behavior and retrieval checks | @zwright8 #7; @zabyxc01 #16 | T3 ACL/citation ownership preserved; no retrieval semantics moved into the engine. |
| Exposed managed engine versions/configuration and rate limits | @Mattycodes69 #9; #5 @zwright8 | Unknown managed tuple remains unknown; provider API evaluation proceeds independently. |
| Complete per-source reuse inventory and final freshness record | @tynamite #41, with #60 | Apply E27's adopted interim policy now; no TTL, bulk-retrieval permission or unrestricted redistribution claim is inferred. |

## Validation and acceptance assessment

Build-evidence follow-up on **2026-10-18**, Python **3.12.12**: workflow dependency
installation succeeded; all **21 contract tests** and **107 research tests** passed;
research intake validated **74 CatalogItems and 3 Pricebooks**; market validation
passed (**33 entities, 1,584 cells, 20 issues**); mobile prompt validation and
`git diff --check` passed. Only the two linked Markdown notes change. The frozen
contract and catalog facts are unchanged. These checks establish repository
integrity; source inspection supports the stated documentation findings, while
independent evidence review, actual runtime execution and remaining owner
decisions are separate.

Validation results are recorded after the files are written and independently checked; the integrated PR must include the repository baseline checks from Python 3.12. Schema validation checks structure, provenance shape and reference consistency; it cannot verify source freshness, license interpretation, actual runtime support or consuming-owner acceptance.

Targeted recheck on 2026-10-16 used Python **3.12.14** from the repository `.venv`: each of the three listed engine proposals passed `contracts/v1/reference/validate_payload.py` against `catalog-item.schema.json`; `git diff --check` passed for this note and its rules. The Markdown rule clauses are review proposals and are not presented as schema-validated executable rules. The orchestrator records the integrated baseline checks separately after all T2 edits settle.

Follow-up validation on **2026-10-17**, Python **3.12.14**: the shared runtime's workflow dependency installation completed; all **21 contract tests** and **24 research tests** passed; `scripts/validate_research.py` validated **30 CatalogItems and 2 Pricebooks** plus external evidence metadata, including a rerun after the 11 engine provenance corrections; `scripts/validate_market_research.py` passed (**32 entities, 1,536 cells, 20 issues**); `git diff --check` passed. A comparison with the base revision confirms that the engine JSON changes are limited to provenance verification status and `updated_at`. The research tests required an unsandboxed rerun because Windows denied writes to the sandbox's temporary directories; no repository test or runtime code was changed. These checks validate structure/import integrity/reference consistency and existing test behavior, not the proposed Markdown rule outcomes, source truth, actual engine execution or human handoff acceptance. E27 was read through the GitHub API; vendor claims retain their original access dates.

| Exact #11 acceptance criterion | Evidence / artifact | Current assessment |
| --- | --- | --- |
| Support matrix keyed by engine version with sources | Current/historical matrices, E01–E25/H01–H09 | Research artifact criterion satisfied: three examined releases and three historical rows retain version-scoped sources, conditions and unknowns. No runtime tuple is certified. |
| Rules in the #40 format, including `unknown` for unverified combinations | `rules/engine-compatibility.md`; E27 | Research artifact criterion satisfied: four proposal groups use the shared template and central owner decisions. Missing eligible evidence stays unknown; E27 permits eligible documentation to decide a scoped outcome while its evidence remains unverified. Executable approval is separate. |
| Decision record merged at `research/T2-infrastructure/inference-engine.md` following research method | This template-based record; PRs #75/#101 | Original record and central corrections merged; no repeated merge is required for this delivery criterion. Full issue acceptance remains separate. |
| Candidate set covers relevant API / managed / self-hosted modes or explains non-applicability | Deployment-mode table and version exposure conditions | Research artifact criterion satisfied: all three modes are addressed; a provider's undisclosed engine remains unknown. Candidate expansion and lifecycle concurrence remain named decisions. |
| Comparison fields defined with type, unit and evidence requirement | Comparison-fields table | Research artifact criterion satisfied: 15 field groups define types, units or non-numeric semantics, and evidence requirements; canonical fields are distinguished from note-only proposals. |
| Compatibility rules/warnings shared format; verified rules separated from hypotheses | Proposed rules, sourced premises, evidence status | Research artifact criterion satisfied: fixed severities, outcomes, applicability, unknown policy and synthetic examples are explicit. The proposals make no independently verified joint-compatibility claim. |
| Every factual/numeric claim primary-sourced with access date and relevant conditions | Claim-source matrices and dated evidence table; build supplement | Research artifact criterion satisfied for the bounded documentation findings: E01–E28/H01–H09 and the separately dated supplement preserve primary locators, versions, access dates and claim conditions. No fresh vendor measurement or blanket source recheck is claimed by this criterion audit. |
| Each downstream handoff confirmed by consuming owner, linked | Required-consumer table; final five-consumer assessment below | Research handoff criterion satisfied: current consuming owners explicitly confirm all five declared research interfaces with their original constraints and narrowing. Both T6 revisions remain separately attributed; no runtime or another owner's acceptance is inferred. |
| Open questions recorded with named follow-up owner | Open-decision table | Research artifact criterion satisfied: retention, exact tuples, plugins/builds, lineage, context, managed-version disclosure and source policy each have named follow-up owners. Recording a question does not accept the owner's decision. |

All nine literal research criteria are satisfied by the previously reviewed artifact assessment and the final five-consumer handoff assessment below. The #246 source integration is delivered, and PUSHINGSQUARES's #37 confirmation and #38 narrowing retain their own revision without rewriting appletechie's earlier response. Mattycodes69's retention/lifecycle concurrence and #42's receiving decision remain named follow-ups; recording them satisfies the open-question criterion without adopting those decisions. Exact installed tuples, live metric exposition and a versioned executable ruleset remain future work in their owning scopes. Research completion does not certify them or add an engine-execution requirement. GitHub completion records should follow reviewed delivery of this assessment; downstream issues, assignments and native relationships retain their existing scope.

### Criterion and integration audit — 2026-10-18

The nine live #11 criteria were checked against main
`227f44049444fd77bac083dd65bd7e7b461f31bf`, the current record, the shared rule
template and actual linked owner responses. The eight artifact criteria above are
supplied by the merged record and its reviewed corrections. The consuming-owner
criterion was pending at that checkpoint; that historical assessment did not
supply a new receipt from another owner or complete the issue. The later final
assessment below uses the subsequently received confirmations.

[#246](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/246), merged as
`1ab7bf9715c577dfec05e0d2d90b853e0d3c7d2a`, supplies the
[ENGINE-to-T6 integration](../T6-deployment-operations/engine-input-integration.md).
Its [independent review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/246#pullrequestreview-5561658476)
checks the source mapping and loader-policy distinctions. That technical review
does not rewrite appletechie's earlier receiving response or itself supply
PUSHINGSQUARES's later decision recorded below. Live exposition, thresholds and deployment execution
remain unclaimed. The matrix's vendor access dates and all catalog provenance
remain unchanged by this audit.


### T6 receiving disposition — 2026-10-18

[@PUSHINGSQUARES's comment 6247689868](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/11#issuecomment-6247689868),
posted at 2026-10-18T08:34:32Z after checking main
`9192d5d6994b644ebbb81344300fda48db6d29a8`, supplies the previously missing T6
co-owner response. It credits appletechie's earlier `66b46d4` receipt without
claiming that co-owner reviewed the later integration.

| Direction | Actual disposition and correction | Retained boundary |
| --- | --- | --- |
| #11 → #37 | Confirm with constraints: #246's ENGINE-01–04 readiness/source map is delivered. The receipt identifies engine-route coverage at S45/R30; R18 is the separate tool/MCP credential check. | Research mapping only. No tuple is selected and each selected service still needs its own exact build/runtime evidence; no executable rule is approved. |
| #11 → #38 | Narrow to exact-release source/evidence inputs. Version/build/config are evidence-record fields, not required exported metric labels; the vLLM V1 logger's actual `model_name`/`engine` labels stay distinct. | SG74/SG75 `_total` forms still need live scrape confirmation. Missing series remain unavailable, not zero; client headers do not supply labels. New llama.cpp SG IDs wait for a selected build/tuple. |

The receipt explicitly identifies these as consuming co-owner research
dispositions, not an independent runtime check or completion of #11/#37/#38.
It supersedes statements that PUSHINGSQUARES has supplied no #37/#38 response;
it does not broaden the earlier appletechie pin or convert source mapping into
metric exposition. The #285 attribution correction supplied the actual scoped
receipt for the final criterion assessment below. Recording that response alone
introduced no execution requirement, source fact, lifecycle adoption or issue
completion. The canonical market #59 ledger remains with its existing owners.

### Final research handoff assessment — 2026-10-18

This final assessment reads the unchanged nine live #11 criteria, the five
declared downstream consumers, their current assignees and the actual linked
responses against accepted main
`2f307a10ef98a8c7c711ef28ba35c6246d36f9fd`. The earlier
[#266 final review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/266#pullrequestreview-5561924936)
accepted the eight artifact criteria while leaving only criterion11.8 pending.
[#285](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/285) subsequently
delivered the T6 attribution correction at
`6190cc96282ef0efe192c110917bbc684bec0b08`. No original criterion, source
observation or historical review is replaced by this assessment.

| Required consumer | Actual consuming-owner confirmation | Accepted research scope and retained limit |
| --- | --- | --- |
| #10 GPU / Compute | [Mattycodes69 6245205057](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10#issuecomment-6245205057) and [appletechie 6245668221](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10#issuecomment-6245668221), both accept with constraints | Exact-release loader/backend/dtype and adapter inputs for sizing; historical tuples, per-device memory and training estimates remain distinct. No fit or SLO result is certified. |
| #25 Agent Framework | [CompleteDotTech 6233323334](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/11#issuecomment-6233323334), accept with constraints | Conditional engine/tool/parser/schema/API interface, with complete request/runtime tuple and explicit unknowns. Consumer specifications do not establish executed compatibility. |
| #33 Fine-Tuned Model | [appletechie 6230482684](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/11#issuecomment-6230482684), accept with narrowing | Artifact/base lineage and adapter/merged distinctions; #33 records added tokens and the training template, #32 owns the training-data side, and #11 retains engine-support evidence. The response requires no T2 correction. |
| #37 Deployment | [PUSHINGSQUARES 6247689868](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/11#issuecomment-6247689868), confirm with constraints | Accepts the delivered #246 ENGINE research map and S45/R30 correction at `9192d5d`; appletechie's earlier `66b46d4` integration-pending receipt remains historical. Selected-service execution is separate. |
| #38 Monitoring | [PUSHINGSQUARES 6247689868](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/11#issuecomment-6247689868), accept source/evidence inputs with explicit narrowing | Version/build/config are evidence fields, not required exported labels. Live `_total` forms remain unverified, missing series remain unavailable, and new llama.cpp signal IDs wait for a selected build/tuple. |

Each receipt author remains an assignee of the identified consuming issue at
this readback. No declared downstream research interface remains unconfirmed
or rejected. The #38 narrowing defines the accepted input boundary; it does not
withhold confirmation until a service is selected or scraped. The literal
criterion requires confirmation by a consuming owner, not repeated approval by
every co-assignee or completion of the consuming issue's runtime work.

Criterion11.8 is therefore satisfied within the same research scope as the eight
already accepted criteria. Mattycodes69's lifecycle concurrence, #42 retention
and sharing decisions, selected runtime evidence and central executable-rule
approval remain named follow-ups under their existing owners. #42 is not one
of #11's five declared downstream handoffs. No lifecycle policy, publisher
authority, reuse permission, production deployment or native application
acceptance is supplied by this completion assessment.

### Lifecycle and receipt follow-up validation — 2026-10-18

This follow-up was prepared from main `ac5e5844dd1cd01366a1b51a0054afa71a340aca` with Python **3.12.14**. Pinned requirements were installed/checked with `python -m pip install -r requirements-research.txt --target <temporary-directory>`; `PYTHONPATH` selected that directory and `PYTHONUTF8=1` made Windows text handling explicit.

| Command | Actual result |
| --- | --- |
| `python -m unittest discover -s contracts/v1/tests -v` | 21 passed |
| `python -m unittest discover -s tests -v` | 180 passed |
| `python scripts/validate_research.py` | Passed: 74 CatalogItems, 3 Pricebooks and evidence metadata |
| `python scripts/validate_market_research.py` | Passed: 33 entities, 1,584 cells, 20 issues |
| `python scripts/validate_handoff_audit.py` | Passed: 101 rows / 98 declared pairs; human acceptance not certified |
| `python prompts/mobile/validate_prompts.py` | Passed: 258 issues / 36 epics / 906 criteria / 880 steps |
| `git diff --check` | Passed |

Only this note, the T2 handoff ledger and the #11 acceptance-map entries change. No catalog fact, frozen contract, source date outside E28, runtime configuration or measured result changes. No new test was added for this documentation-only proposal. Automation checks structural integrity; source truth, rights, freshness and owner evidence acceptance remain review requirements. The E28 primary-source check is documented separately from those checks, and no inference engine or GPU workload was run.
