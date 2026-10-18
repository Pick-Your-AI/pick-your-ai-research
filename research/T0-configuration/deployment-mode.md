# T0: Deployment Mode

Issue: #3 · Contract: v1 1.0.0 (adopted in PR #44; inspected at `a222013`) · Kinds: `deployment_mode`
Status: research decision record, revision 7 (current receiving reconciliation 2026-10-18; final delivery and issue acceptance recorded in the PR) · Original research date: 2026-10-16; later source access dates are explicit below
Deliverable path: `research/T0-configuration/deployment-mode.md` · Companion note: [`research/T0-configuration/workload-use-case.md`](workload-use-case.md)

Labels used in this note:
- **Evidence grades** (from the research method): Primary documentation, Vendor claim, Independent measurement, Estimate.
- **Proposal:** a design choice made in this note, not a sourced fact.
- **C-** IDs cite the v1 contract; **D-** IDs cite external sources; **CD-** IDs are [open contract decisions](#open-contract-decisions); **EV-1** is the [evidence eligibility predicate](#evidence-eligibility-ev-1).

## Scope

This note is written **local-first**: the T0 owner has chosen to prioritise self-hosting, meaning running open-weight models with an inference engine you operate. API and managed modes are defined precisely for comparison, and their vendor terms are covered only as far as a fair comparison needs. This is a choice of emphasis; 17 of the contract's 45 baseline rules apply only to self-hosting (C3). The other workstream owners should confirm it.

## Summary

- **Mode is decided by who operates the serving runtime, and by what capacity it runs on.** Billing is recorded separately and never decides the mode.
  - You operate it: **self-hosted**.
  - A provider operates it on reserved or dedicated capacity: **managed**.
  - A provider operates it on shared capacity: **API**.
  - Serving components in different modes: **hybrid**.
  - Not known: **unknown**.
- **Mode is set per serving component, and relationships come from v1's existing `build.links`** (C9). This fixes a v1 defect: the 17 self-hosting rules check the literal value `mode == "self_hosted"`, so hybrid builds skip them all (C3, C4).
- **Self-hosted fit depends on several things at once:** the artifact, the engine build, the decoding method, the devices and their memory configuration, the context and the concurrency.
  - Fit evidence is kept as records that are immutable while retained.
  - One eligibility predicate (EV-1) decides whether evidence may be used, with checks specific to each type of evidence. Eligible results that disagree are resolved by #41's conflict order; the value stays unresolved only for genuine ties.
  - A newer release alone never invalidates a record.
- **CPU-only and mixed CPU+GPU builds are in scope.** For single-batch generation, memory bandwidth is reported as a main bottleneck (D27–D29), so bandwidth, instruction sets and offload support are key inputs. Measured fit records, not this note, decide how far that holds for a given machine.
- **Crowdsourced fit reports are a possible additional evidence source.** Several community databases already exist (D36–D41). Agreement between reports is shown, but doesn't decide compatibility until #41 defines an acceptance policy (CD-8).
- **Self-hosting enables local inference, but doesn't by itself keep data local.** Residency is checked over the build's data flows, including external destinations (D-R6).
- **Open contract decisions.** Thirteen are recorded for #40 and #41 rather than solved here (CD-1 to CD-13; CD-11 was raised on #88, CD-12 in T5's review of #81, and CD-13 by T4 on #40).

## User decision

For each component that serves a model or retrieval, who runs it, where, and on what capacity? The build's overall mode follows from those answers.

## Definitions (Proposal)

### The classification test

1. **Who operates the serving runtime?** That is, who installs, configures, updates and keeps running the process that serves requests: `self` (the user or their contractor), or `provider`. If unknown, the mode is `unknown`.
   - If the customer supplies a custom serving container but the provider runs the platform (scheduling, scaling, restarts), the operator is `provider`, with `runtime_supplied_by: customer`.
   - Google, for example, lets customers "build and deploy your own custom serving containers" on dedicated endpoints (D15).
2. **If the provider operates it, what capacity?**
   - `shared`: a pool shared with other customers.
   - `reserved_throughput`: throughput reserved for one customer on provider-run infrastructure, such as Azure PTUs or Bedrock Provisioned Throughput.
   - `dedicated_instances`: instances allocated to one customer, such as Hugging Face Inference Endpoints, SageMaker endpoints or Google's dedicated endpoints.

| `runtime_operator` | `capacity` | Mode |
| --- | --- | --- |
| `self` | any | `self_hosted` |
| `provider` | `reserved_throughput` or `dedicated_instances` | `managed` |
| `provider` | `shared` | `api` |
| `unknown`, or `provider` with unknown capacity | — | `unknown` |

**Billing never decides the mode** (see [Pricing and capacity](#pricing-and-capacity)). For example, an API's free quota is still `api`.

**Which components count** (the deployment units):
- `model` (any `model_type`);
- `embedding_model`;
- `vector_database`;
- `fine_tuned_model`:
  - A full fine-tuned model is its own serving component.
  - An adapter is loaded into a base model's deployment. It inherits that deployment, and needs an engine that supports adapters (to be confirmed with #11 and #33).

Tools, MCP servers, storage and monitoring don't decide the mode. They are still checked for isolation (W-R8 in the companion note) and residency (D-R6).

**The mode applies to serving components only.** Training and fine-tuning runs are out of its scope; T5 classifies them (#30–#33). A serverless fine-tuning service is therefore not "API" under this test. Only the fine-tuned model it produces, once served, gets a mode. Training services and rented training compute that receive data still participate in the separate [D-R6 residency check](#d-r6-residency-covers-processing-and-storage-across-the-data-flows); their exclusion from mode does not exclude their data flows.

**Build-level mode:**
- If every serving component has the same mode, the build has that mode.
- If they differ, it is `hybrid`.
- If any is `unknown`, the build mode is `unknown`.

**Where self-hosted hardware is** (Proposal):
- `hardware_location.kind` is `personal_device`, `own_server` or `rented_server` (a cloud VM or bare-metal machine you administer).
- Each location records a `jurisdiction` (an ISO 3166 code) rather than a cloud region.
- v1's `hosting_type` values (`cloud`, `on_prem`, `edge`, `colocation`, `managed_api`) don't define a personal device, and `edge` and `on_prem` have no stated meaning that would settle it (C1).

### Boundary examples (one for each pair of modes)

| Pair | Example | Classification |
| --- | --- | --- |
| self-hosted ↔ managed | The same open-weight model run with vLLM on a rented VM you administer, versus on a Hugging Face Inference Endpoint (instance type at an hourly rate calculated by the minute; chosen cloud and region; D13). | VM: **self-hosted**. Endpoint: **managed** (`dedicated_instances`). |
| self-hosted ↔ managed (vendor terminology) | Google calls open models on dedicated endpoints in your project "self-deployed models" (D15). | **Managed**: Google's endpoint service operates them. Classify by the test, not by vendor terminology. |
| managed ↔ API | Azure "Standard" deployments (per token) versus "Provisioned" deployments (hourly per PTU) (D16, D17). Google's open models offered as "serverless managed APIs" (MaaS) versus on dedicated endpoints (D15). | Standard and MaaS: **API**. PTU: **managed** (`reserved_throughput`). Dedicated endpoints: **managed** (`dedicated_instances`). |
| self-hosted ↔ API | Gemma 4 is published as open weights with Apache-2.0 licence metadata (D10); Gemini models are offered through the Gemini API (D20). | Weight availability is per model. Gemma 4 can be **self-hosted**; Gemini is used through the **API**. |
| self-hosted ↔ API (protocol trap) | vLLM serves an OpenAI-compatible API (D8); Ollama serves a subset of the OpenAI API on `localhost:11434` by default (D6). | Still **self-hosted**: protocol compatibility says nothing about the operator. |
| hybrid ↔ self-hosted | A local LLM and vector database, with the embedding model called through a shared provider API. | **Hybrid**. If the embedding model also runs locally, **self-hosted**. Telemetry doesn't change the mode (it's checked by W-R8 and D-R6). |
| hybrid ↔ API | An API LLM with a self-hosted vector database, versus with a provider-run shared vector-search service. | **Hybrid** versus **API**. |
| hybrid ↔ managed | An LLM on a dedicated endpoint with a shared embedding API, versus both on dedicated endpoints. | **Hybrid** versus **managed**. |

### Per-component mode and relationships (decision proposal)

**v1 already records relationships between selections.**
- `build.links` connects a `from_selection_id` to a `to_selection_id`, with relations including `runs_on`, `served_by`, `uses`, `derived_from` and `feeds` (C9).
- Rule references can target a specific `selection_id` (C10).
- The gap is that the baseline rules don't evaluate deployment checks per component through these links, and that some needed facts aren't recorded at all.

**Proposal: links remain the only representation of relationships.** Each serving component's selection gains a `deployment` object holding only facts that aren't relationships:

| Field | Meaning |
| --- | --- |
| `runtime_operator`, `runtime_supplied_by`, `capacity` | As defined above |
| `placement` | Typed shares per device: `{device_selection_id, share: whole \| {layers: [first, last]} \| {experts: [IDs]} \| {tensors: pattern}, resident: always \| on_demand}`. Allocation in bytes is CD-2. |

Relationships are read from links:

| Relationship | Link |
| --- | --- |
| Host | A `runs_on` link to a `hosting_platform` |
| Devices | `runs_on` links to `accelerator` or `compute_profile` selections |
| Engine | A `served_by` link to an `inference_engine` |
| Fine-tuned adapter (`spec.adapter_only: true`, C1) | A `derived_from` link to its base model, and the base model's `served_by` engine. The catalog item also names its base in `spec.base_model_ref` (C1); whether the two must match is CD-6. |

**Consistency rule:** if a component has more than one candidate host or engine link without a role that disambiguates it, the deployment is unresolved (`unknown`). The draft-to-target relation, licence answers and the mapping from the hardware inventory to selections are left to CD-6.

**Why per component:**
1. **Real builds mix modes.** A local LLM with a hosted embedding API is an ordinary configuration.
2. **v1 already records a per-model serving path.** `settings_model.serving_mode` takes `api` or `weights`, and catalog items record access modes: `access_modes` on models and embedding models, `supported_access_modes` on fine-tuned models (C1, C2).
3. **Build-level gating fails for hybrid builds** (C3, C4).

## Self-hosted fit: what it depends on

| Factor | Evidence |
| --- | --- |
| **Quantization × engine × hardware generation** | vLLM's chart (D1): AWQ is unsupported on Volta and AMD GPUs, supported from Turing to Hopper. llm-compressor FP8 (W8A8) is supported only on Ada, Hopper and AMD GPUs. GGUF is supported on NVIDIA and AMD GPUs, not on Intel GPUs or CPUs. |
| **Format × engine** | llama.cpp requires GGUF (`docs/models.md`) and lists CPU, Metal, CUDA, HIP, Vulkan, SYCL and other backends (D3). GGUF can run on a CPU through llama.cpp but not through vLLM (D1). |
| **Engine × platform** | vLLM lists NVIDIA CUDA, AMD ROCm, Intel XPU and Apple Silicon (via vLLM-Metal) GPUs, several CPU architectures, and out-of-tree plugins (D2). |
| **One model, several published artifacts** | Gemma 4 QAT checkpoints are published as a Q4_0 GGUF, as w4a16 compressed-tensors "for native, optimized inference with vLLM", and as a mobile scheme (D10). |
| **Third-party derivatives and engine forks** | Ternary Bonsai 2 27B is derived from Qwen3.8-27B (D11). Its ternary weights are 1.72 bits ideal, stored as 1.75 bits (PTQ1_0, 5.95 GB) or 2.13 bits (PQ2_0, 7.21 GB) for the language model, plus an optional 0.63 GB vision component. Its low-bit kernels are forks of llama.cpp and MLX (D24). |
| **Native low precision × hardware generation** | The NVFP4 Nemotron 3.5 Super VL card says inference "uses W4A4 on Blackwell and W4A16 on non-Blackwell platforms" (D23). v1's precision enum has no FP4 or ternary value (C1). |
| **Architecture × offloading** | Qwen3.8-Flash-Next has 125B parameters (6B activated) plus 51B of n-gram embeddings, described as "more amenable to offloading than Mixture-of-Experts". Its card lists SGLang, KTransformers and vLLM as serving engines (D11). |
| **Decoding methods** | Mistral Medium 3.5's EAGLE draft asks for a vLLM nightly build (D25). NVIDIA's LiLiCorr draft lists "NVIDIA Blackwell, SM 120 only" (D25). A Gemma 4 QAT target needs a QAT assistant "with the same precision" (D10). |
| **Documented vs tested support** | Voxtral Realtime's card says it is "currently only support[ed] in vLLM", yet later documents Transformers support "Starting with `transformers >= 5.2.0`". A ggml-org GGUF repository created 16 Oct 2026 gives a `llama serve` command and links a llama.cpp pull request (D26). None of these was tested here. |
| **Context × concurrency × memory** | The KV cache for OPT-13B in FP16 is calculated at 800 KB per token, and grows during generation (D9). |
| **Rate of change** | vLLM v0.28.0 to v0.31.0 came about two weeks apart (D4). llama.cpp has 17 build tags with commits dated 16 Oct 2026 UTC (`b11676`–`b11696`); not every tag became a published release (D5). vLLM's chart "is subject to change" (D1). |

### Fit records

**Fit records are immutable while retained.** A correction creates a new record that supersedes the old one. Each record holds an outcome, memory and speed figures labelled measured or estimated, the protocol identity, the evidence grade, the source and the date.

**The configuration key for self-hosted components covers:**
- the model artifact: ID, version, file hash, format, quantization, logical and stored bits, and the components loaded;
- the engine: ID, version, fork or commit, and launch options that affect memory or speed (threads, batch limits, KV cache precision, parallelism), including the sequence admission limit, its domain (engine instance, replica or shared scheduler), and whether queued/preempted KV is retained outside that limit;
- the decoding method and draft artifact, with mode-specific live sequence expansion per request (parallel samples, live beams or other candidates); returned output count alone is insufficient, and `n * num_beams` is not a universal expansion;
- the devices: model, memory capacity and configuration (including channel population and NUMA layout), instruction-set features, driver;
- the placement;
- the OS;
- the workload distribution: input and output lengths, request concurrency and arrival process, plus request allocation to each admission domain, derived peak sequence demand and the resident sequence envelope (W-R6 in the companion note);
- the cache state (warm or cold).

Which fields are essential for comparison and which are display-only is decided in CD-3.

For W-R6, request demand and sequence admission must have matching component, workload and scheduler scope. Expand request demand using the recorded decoding mode before applying the sequence admission cap. If admission is unknown, use expanded peak sequence demand only when expansion is known; missing expansion or scope allocation leaves sizing `unknown`. A per-step scheduler batch limit cannot cap KV retained outside the active batch. The companion note defines the arithmetic, synthetic examples and #10/#11 handoffs; these assumptions are part of evidence matching, not approved contract fields.

**The configuration key for opaque API and managed endpoints covers:**
- the provider;
- the endpoint or deployment type;
- the model ID and revision, or the alias policy;
- the region and service tier;
- the request configuration (lengths, streaming, concurrency);
- the observation window.

Hidden variables, such as the provider's engine and hardware, are recorded as unknown, and confidence is limited accordingly (#41).

### Evidence eligibility (EV-1)

EV-1 decides whether a piece of evidence may be used by a rule. Every piece of evidence passes a common gate, then an applicability check that depends on its type.

**Common gate:**
1. **Provenance:** the source, the publisher or reporter, the date and the evidence grade are recorded.
2. **Status:** it has not been corrected, retracted or flagged.
3. **Freshness:** it is within #41's freshness policy for its type.

**Applicability, by type of evidence:**

| Type | Examples | Read by | Applies to the build when |
| --- | --- | --- | --- |
| Measurement | Fit records, crowdsourced reports, project measurements, quality evaluation results | W-R6, W-R7, W-R10 | Every essential key field equals the build's selection, using the key that suits the component's mode. It was produced under the same protocol identity, or one #41 declares compatible (CD-3). Its grade meets #41's acceptance policy. Until that policy exists, only `project_measured` records qualify, and community reports are informative only (CD-8). |
| Estimate | v1 resource estimates; memory calculated from artifact size, context and sequence occupancy; figures labelled estimated in a fit record | W-R6 | Its inputs (artifact, engine build, placement, lengths, request concurrency, mode-specific sequence expansion, admission scope/limit or explicit peak-demand fallback, and KV retention/sharing assumptions) equal the build's selection and workload, its method and version are recorded, and its v1 confidence (`estimated`, `calibrated` or `verified`) meets the build's `min_resource_confidence` (C5, C9). Estimates are not used for latency or throughput targets, which need `service_level` measurements. Estimated figures in community reports stay informative, like the rest of the report (CD-8). |
| Support documentation | Engine support matrices, instruction-set requirements, a draft model's stated target and hardware | D-R3, D-R7a, D-R7b, D-R8 | It is primary documentation from the publisher of the engine, artifact or hardware, and the selection falls within the coverage it declares, such as an engine version, hardware generation or platform. |
| Legal and provider documents | Licences, model cards stating weight access, terms of service, data-handling pages, region lists | D-R1, D-R2a, D-R2b, D-R5, D-R6 | It is primary documentation from the licensor or provider, and it matches the selected offering, its version or effective date, the jurisdiction, and any account conditions it states (for example paid or unpaid use, or approval for zero retention). |

**Transfers between workloads.** A performance figure carried over from a different workload distribution, for example by a transfer model, is a derived estimate, not a measurement of the build's configuration. Until CD-3 defines how such estimates are assessed, they are not eligible, and W-R7 gives `unknown`.

**Conflicting evidence.** Eligible evidence can disagree about a rule's verdict: one measurement or estimate meets a target while another misses it, or one primary document lists a combination as supported while another doesn't. #41's interim conflict order, set in the #75 owner review, resolves it:

1. **Normalise.** Differences in units, rounding, currency or naming aren't conflicts.
2. **Scope.** Drop evidence whose stated coverage excludes the selection. Among the rest, the most specific coverage wins.
3. **Version and date.** For version-pinned facts, the source for the selected version wins. For current-state facts, the latest effective date wins.
4. **Authority.**
   - The publisher beats third parties for facts it controls.
   - Within one publisher, a stated requirement or limitation beats a capability listing.
   - For fit and performance, a matching measurement beats an estimate, which beats a vendor claim.
5. **Numbers of equal rank.** The conservative value in the rule's direction decides: highest memory, highest latency, lowest throughput, or largest quality loss. The result is flagged as disputed.

The value stays unresolved, and the outcome `unknown`, only when equally ranked evidence still gives opposite yes/no answers after these steps. A rule never passes on one eligible result while ignoring another. How the evaluator encodes this order is CD-3.

Ineligible evidence is shown but leaves the dependent value unresolved, so the rule's outcome is `unknown`. Eligibility is recomputed whenever any of these change: the selection, the evidence's status, the policy, or the date. A newer engine release alone changes nothing; it is shown separately as "newer build available".

### CPU-only and hybrid CPU+GPU self-hosting (Proposal)

Many people already own capacity without a GPU. #10 asks "Is CPU or edge inference in scope?". This note answers yes from the configuration side; #10 owns sizing.

| Factor | Evidence |
| --- | --- |
| **Decode is described as memory-bound** | Arm's llama.cpp guide says "the Decode stage is memory-bound" (D27, Vendor claim). NVIDIA describes decode the same way for GPUs (D28, Vendor claim). SqueezeLLM reports memory bandwidth as "the main bottleneck … specifically for single batch inference" (D29). Batching, caching, sparse activation, speculative decoding and placement change the picture; fit records show how far it holds for a given machine. |
| **Server CPUs differ widely in bandwidth** | Vendor peak figures per socket: AMD EPYC 9755, 12 channels and 614 GB/s; AMD EPYC 9996, 16 channels and 1024 GB/s with DDR5 RDIMMs or 1638 GB/s with MRDIMMs. Intel lists the Xeon 6980P with 12 channels and DDR5-6400 or MRDIMM-8800, without a bandwidth figure (D30). These are peak specifications, not inference measurements. |
| **Instruction sets gate engines** | vLLM's CPU backend recommends `avx512f` on x86 and gives `avx2` "limited features". It requires NEON on Arm, marks Apple silicon and IBM Z as experimental, and recommends tensor parallelism equal to the number of NUMA nodes (D31). llama.cpp lists "AVX, AVX2, AVX512 and AMX support for x86 architectures" and Arm NEON (D3). Intel says AMX improves inference "with no additional hardware" (D33, Vendor claim). |
| **Quantization support differs on CPUs** | In vLLM's quantization chart (D1), AWQ and GPTQ are supported on x86 CPUs but not Arm CPUs. llm-compressor INT8 (W8A8) is marked as supported on both, INT8 (W4A8) only on Arm, and GGUF on neither. vLLM's CPU page lists AWQ and GPTQ for "x86, s390x, Power", and compressed-tensor INT8 W8A8 for "x86, s390x only" (D31). The two pages therefore disagree on Arm W8A8. Under #41's conflict order the CPU page decides: it is the more specific source for CPU backends (step 2), and "x86, s390x only" is a stated limitation (step 4). D-R3 therefore gives `fail` for W8A8 on Arm, flagged as disputed. Neither page was tested here. llama.cpp runs GGUF on CPUs (D3). |
| **Hybrid CPU+GPU offload** | llama.cpp's server can cap the layers held in VRAM (`--n-gpu-layers`) and "keep all Mixture of Experts (MoE) weights in the CPU" (`--cpu-moe`) (D32). KTransformers targets "CPU-GPU heterogeneous computing", for example "hot experts on GPU, cold experts on CPU" (D34). Whether a modest GPU plus a large-memory server can host models neither could alone is a hypothesis for fit records. |
| **Measurement** | `llama-bench` reports prompt-processing and generation speed as "average tokens per second (t/s) and standard deviation". It excludes tokenization and sampling (D35). That is kernel throughput, not a service-level latency measurement (see [What a report contains](#what-a-report-contains)). |

**v1 gaps for CPU builds (for #10 and #40):**
- Accelerators have `vram_gb`, but no memory bandwidth, channel population, NUMA nodes or instruction-set flags (C1).
- Recording a CPU with `vram_gb` conflates VRAM with system memory.
- Compute profiles require a cloud `region` (C1).
- There is no field for a CPU+GPU split; see `placement` and CD-2.

## Crowdsourced fit reports (Proposal)

### Why

Community reports are a possible additional source of fit evidence, alongside publisher documentation and the project's own measurements (#61). Whether they would cover combinations the other sources miss is a research hypothesis for #48 and #57, not an established fact.

**This is not a new idea.** Several projects already collect user-submitted local-LLM results:

| Project | How results are collected | Checks and curation |
| --- | --- | --- |
| LocalScore (a Mozilla Builders project) | Open-source benchmark CLI; users "optionally submit" results to its public database (D36) | None stated |
| llama.cpp performance threads (Apple Silicon, Vulkan, CUDA) | Users post results from a specified `llama-bench` command, with the git hash. The Apple Silicon thread prescribes a commit. The Vulkan and CUDA threads accept different commits and "prioritize newer commits with substantial" backend updates (D37). | Maintainers curate scoreboards, choosing among entries at their discretion. The CUDA scoreboard credits contributors in a "Thanks to" column. |
| LocalMaxxing | CLI or web form, after signing in with GitHub or Hugging Face (D38) | Automatic checks, including "a physical speed ceiling". Implausible results are "marked suspicious and hidden from leaderboards". |
| Rapid-MLX (Apple Silicon) | A `benchmark run + share` command; the page states "Submissions: CC0" (D39) | Each submission is "one locked run"; its protocols are versioned separately |
| MetriLLM | npm CLI requiring Ollama or LM Studio (D40) | "Every submitted result is displayed. We don't curate or filter benchmark data." Each run has a hash. |
| OpenBenchmarking.org (`pts/llama-cpp`) | The Phoronix Test Suite uploads only on opt-in, with detailed hardware and software information (D41) | None stated |

Wider precedents:
- Geekbench prompts users to upload results and flags timer-related invalid results (D42).
- MLPerf Client results count as valid only with its "configuration tested" notice (D43).
- PCPartPicker's Completed Builds show user builds with images, a priced part list, votes and comments (D44).
- Steam's hardware survey is "optional, and anonymous" (D45).

None of these community LLM projects appears in PR #67's competitor register at the cited commit (D46).

**What could be distinctive (hypothesis, for #48 and #57):**
- Reports keyed to the builder's compatibility model, so that each one is usable as evidence under EV-1.
- Or linking or importing existing datasets where their terms allow (#41, #60).

### What a report contains

There are two protocol types, and they are not interchangeable (CD-3):

| Protocol type | Records | Used for |
| --- | --- | --- |
| `kernel_throughput` | Prompt-processing and generation tokens per second, as mean and standard deviation over repeated runs, in the format of `llama-bench` (D35). Excludes tokenization and sampling. | Informative display, and fit checks that need only memory and load success |
| `service_level` | Request-level timing samples (TTFT, TPOT, end-to-end), the arrival schedule, warm-up handling, the measurement boundary, and quantiles with sample counts | Latency and throughput targets (W-R7 in the companion note) |

Both protocol types also record:
- the configuration key above;
- whether the model loaded (or the error);
- peak memory per device and memory pool;
- provenance: reporter pseudonym, timestamp, collection method (`harness` or `manual`), harness and protocol version, and a hash of the raw log.

### Trust grades (proposal for #41)

| Grade | Meaning |
| --- | --- |
| `self_reported` | Entered by hand |
| `harness_reported` | Produced by the reporting harness with a defined protocol, captured environment and log hash |
| `agreement_observed` | At least N harness reports with the same essential key and protocol agree within a tolerance. This is not verification: per-install keys and differing log hashes don't establish that the reporters are independent (CD-8). |
| `project_measured` | Measured under the #61 protocol |
| `flagged` | Failed an automatic check; kept for review, not used as evidence |

**Display:** show the spread (median, range, number of reports) and the grade, never a single universal "works". Showing the spread doesn't decide a verdict; when eligible results disagree, #41's conflict order decides (EV-1). Under EV-1, community grades are informative until #41's acceptance policy says otherwise.

**Sticky, not frozen:**
- Reports are immutable while retained: a correction is a new report that supersedes the old one, not an edit.
- A newer engine release doesn't remove a report or make it ineligible. Eligibility is decided by EV-1, including correction, retraction and flag status.
- A reporter can have a report, or their attribution, deleted (see [Privacy and rights](#privacy-and-rights-for-41)). What may remain afterwards, such as a tombstone with no content or attribution, or aggregate statistics, is an open decision for #41 (Q11).

### Making contributing easy

1. **One command.** A harness detects the hardware, the engine build and the artifact hash. It runs a defined protocol and writes `llama-bench`-compatible output for kernel throughput (D35). Precedents: LocalScore, the Phoronix Test Suite, Rapid-MLX, MetriLLM (D36, D39–D41).
2. **Preview and consent before upload.** Rapid-MLX previews the exact payload and asks for consent (D39). Phoronix uploads only on opt-in (D41). Geekbench prompts before uploading (D42).
3. **Accept what people already run.** Import `llama-bench` JSON (D35), with adapters for local runners such as Ollama and LM Studio, which MetriLLM relies on (D40).
4. **Report from a build.** An "I run this build" action on a saved build (#42) pre-fills the key. PCPartPicker's Completed Builds attach a real build to its part list (D44).
5. **Ask for the gaps.** Show which combinations have no reports, and offer the one-command run.
6. **Keep friction low.** Pseudonymous harness submissions with a per-install key keep contributing easy, but they are not evidence of independence (CD-8).

### Incentives

These are hypotheses to test in customer research (#52):
1. **Personal payoff first.** After a run, users see how their result compares with others on the same configuration.
2. **"What runs on my machine" alerts**, opt-in.
3. **Credit.** Named or pseudonymous credit, as in the llama.cpp CUDA scoreboard (D37). Contributor profiles, and recognition for the first report on a new combination.
4. **Build showcases**, in the style of PCPartPicker's Completed Builds (D44).
5. **Ecosystem pull.** Maintainers and publishers get a version-labelled regression signal. The data would be openly licensed (Rapid-MLX states CC0, D39); #41 decides the licence.
6. **No pay per report at first.** Paying per report would likely reward fabricated runs.

### Integrity

- **Automatic checks:**
  - defined protocols;
  - duplicate and log-hash checks;
  - outlier detection within the same key;
  - rate limits.
- **Plausibility heuristic, not a filter.** LocalMaxxing uses "a physical speed ceiling" (D38). A bandwidth-based estimate could flag results for review. It needs #10's model of the memory traffic per emitted token, which depends on memory level, batching, sparsity, speculative decoding and placement. Until that model exists, the check reports "check unavailable", and it never hides a result automatically.
- **Curation:** MetriLLM shows everything (D40), while llama.cpp maintainers curate (D37). Proposal: show every report with its grade.
- **Conflicts of interest:** reports from vendor-affiliated accounts are labelled.
- **Validity flags:** Geekbench marks invalid results (D42); MLPerf Client limits valid scores to its tested configuration (D43). The harness should flag equivalent conditions (to define).

### Privacy and rights (for #41)

- **Collect model names, not identifiers.**
  - Never collect prompts, files, serial numbers, hostnames, usernames or paths.
  - Use IP addresses only transiently.
  - Precedents: LocalScore lists the "non personally identifiable system information" it collects (D36). Rapid-MLX says prompts, files and hardware serials are never sent and IP addresses are not stored (D39). The Phoronix Test Suite can sanitise hardware strings (D41).
- **Pseudonymous by default, with deletion on request.** Deletion removes the report or its attribution. Pseudonymity doesn't settle whether a reporter ID is personal data; it can be (see the companion note's GDPR reference). Retention periods, and what survives a deletion, are for #41 (Q11).
- **State a licence at submission,** decided by #41. Import third-party data only where its terms allow (#41, #60).

### Contract implications (for #40 and #41)

- Research intake requires a public source URL on every provenance entry (C7). A user's run has none, so either v1 gains a report provenance type, or reports live in a separate store (Q6).
- ResourceEstimate's `confidence` enum (C5) has no grade or report count.

## Field dictionary

These fields sit on a serving component's `deployment`, on device selections, on artifacts, or on the build, as noted. Answer states follow the companion note and CD-1. Fields marked CD-n are not yet complete.

| Field | Where | Type and allowed values | Constraints | Evidence requirement | v1 today |
| --- | --- | --- | --- | --- | --- |
| `runtime_operator` | deployment | enum `self`, `provider` | Required for serving components | Offering documentation (D13, D15, D16) | — |
| `runtime_supplied_by` | deployment | enum `operator`, `customer` | Provider-operated only | D15 | — |
| `capacity` | deployment | enum `shared`, `reserved_throughput`, `dedicated_instances` | Required when the operator is `provider` | D13, D16–D18 | — |
| Host, devices, engine | `build.links` | `runs_on` and `served_by` links | Unambiguous per component, otherwise `unknown` | — | `build.links` (C9) |
| `placement` | deployment | typed shares (see above) | Devices must be linked through `runs_on` | Engine settings (D32, D34) | — (byte allocation: CD-2) |
| `hardware_location` | host | `{kind: personal_device \| own_server \| rented_server \| provider, jurisdiction: ISO 3166 code, site_label: string}` | `jurisdiction` required when residency is constrained | User input; provider region documentation | `hosting_type`; compute profile `region` (C1) |
| `memory_kind` | device | enum `dedicated`, `unified`, `system` | — | D7 for unified | — |
| `memory_bandwidth` | device | `{value_gb_per_s: decimal > 0, basis: vendor_peak \| measured}`, gigabytes (10⁹ bytes) per second | — | D30 or measurement | — |
| `isa_features` | device | set, e.g. `avx2`, `avx512f`, `amx`, `neon`, `sve` | CPUs | Specification or harness | — |
| `numa_nodes` | device | integer ≥ 1 | CPUs | Harness | — |
| `engine_build` | engine selection | `{version: string, fork_repo: URL, commit: string, launch_options: object}` | `fork_repo` and `commit` required for forks; launch options record sequence admission limit and domain, distinct from request demand and per-step batch limits; unknown limit uses W-R6's expanded-demand fallback only when expansion is known | D4, D5, D24; exact launch configuration and engine-version admission semantics needed for W-R6 | Engine item version |
| Sequence accounting inputs | decoding configuration and workload-to-engine allocation (CD-2/CD-3) | decoding mode/settings; integer live sequences per request ≥ 1; admission domain; peak requests per domain ≥ 1; sequence admission limit ≥ 1 when known | Derive sequence demand before admission per W-R6; mode-specific expansion, KV retention/sharing and whole-request admission assumptions explicit; missing expansion or allocation leaves sizing unknown | #11: exact engine semantics; #10: derived envelope and eligible memory model | — |
| `artifact_format` | artifact | Serialization: `gguf`, `safetensors`, `onnx`, `pytorch`, `other` | — | Repository files | `model_formats` (C1) |
| `package_convention` | artifact | `mlx`, `transformers`, `other`, `none` | Separate from serialization: IBM's MLX repository holds safetensors files (D47) | Repository files | — |
| `quantization` | artifact | `{method: open vocabulary, logical_bits_per_weight: decimal, stored_bits_per_weight: decimal, packing: string}` | bits > 0 | Artifact card (D10, D23, D24) | Fixed enum without bits (C2) |
| `components` | artifact | list of `{role: language_model \| vision \| draft \| other, size_gb: decimal > 0, required: boolean}` | — | D24 | — |
| `license_conditions` | model catalog | list of `{condition_id, text, source, kind: eligibility \| obligation, question}` | Qualify the selected terms, subject and activity; an absent inventory is unknown, and a short condition ID is not globally unique (CD-6) | Licence text (D12); exact source-condition binding under the accepted #40 receiving scope below | `license` booleans and SPDX ID; opaque `license_ref` (C1) |
| `licence_answers` | build | list of `{model_selection_id, condition_id, answer, grant_ref}`. The allowed `answer` values depend on the condition's `kind`: `met`, `not_met` or `unknown` for `eligibility`; `acknowledged`, `not_acknowledged` or `unknown` for `obligation` | `grant_ref` only for `eligibility`; a locator alone is not a qualified exception for the actual subject, condition, activity and period. `unknown` is an answer state (CD-1) | User input; any claimed grant requires its separately qualified evidence | — (location and exact binding: CD-6) |
| `external_connections` | every component | list of `{destination_id, purpose: weights_download \| telemetry \| licence_check \| remote_api \| backup \| other, lifecycle: provisioning \| runtime, state: enabled \| disabled \| unknown, carries_workload_data: boolean, required: boolean}` | An absent list is unresolved, not empty | Component documentation (e.g. D6) | — (boundary model: CD-4) |
| `destinations` | build | list of `{destination_id, host, processing_locations: [codes], storage_locations: [codes], data_scope: string}` | — | Destination documentation | — |
| `data_terms` | provider-operated components | `{training_use_default: no \| yes \| opt_in \| conditional, retention: {application_state: [entry], abuse_monitoring: [entry]}, zero_retention: available \| by_approval \| no, processing_locations, storage_locations, conditions: [typed predicate or text]}` | Each retention entry: `{basis: no_storage \| duration \| until_deletion \| conditional \| unknown, days: integer (when basis is duration), scope: {endpoints, data_categories}, source_id, accessed}`. Free-text conditions make automated comparison `unknown` until reviewed. | Provider terms (D19–D22) | — |
| `billing` | deployment | `{charge_basis: per_use \| per_time \| flat_subscription \| none, ownership: owned \| rented \| provider, commitment: {kind: none \| reservation, term_months: integer ≥ 0}}` | — | Billing basis only (D13, D14, D17, D18) | `billing_class` (C1) |

### Data handling

**Self-hosting enables local inference; it doesn't guarantee that data stays local.**
- Runners and engines can have cloud features. Ollama documents a cloud service alongside its local server (D6).
- Rented servers are subject to host terms.
- Data flows are recorded per component (`external_connections`, `destinations`) and checked against residency (D-R6) and isolation (W-R8 in the companion note).
- Licence obligations still apply (D12).

**For API and managed components, terms differ by provider, model, access path, account and jurisdiction.** Examples, accessed 2026-10-16:
- **OpenAI** says API data is not used for training unless the customer opts in. Its page separates abuse-monitoring logs, kept up to 30 days by default, from application state that depends on the endpoint. Zero data retention needs prior approval. Storage and processing are separate: "Support for regional storage does not imply support for regional processing" (D19).
- **Google's Gemini API terms:**
  - For unpaid services, including unpaid quota, Google uses content and responses "to provide, improve, and develop Google products and services and machine learning technologies".
  - For paid services, it doesn't use prompts or responses to improve its products.
  - In the EEA, Switzerland and the UK, the paid-service data-use terms "apply to all Services, including Google AI Studio and unpaid quota".
  - Google AI Studio counts as paid when the account has access to a Cloud project with an active billing account, or is a Workspace enterprise account (D20).
- **Azure** states that prompts and completions for the models it sells are not available to OpenAI or other model providers (D21). "Data Zone" deployments process data within a Microsoft-specified zone (US, EU or Asia Pacific); "Global" deployments may use any Azure region (D16).
- **Amazon Bedrock** documents per-model retention controls (D22).

These terms belong to #5 and #9. This note only defines the comparison fields.

## Component requirements by function and mode (Proposal)

**Build-level fields** (not component selections):
- the workload profile (companion note);
- the derived deployment mode;
- residency.

The context policy remains a v1 selection (C3).

**Component requirements** use these labels:
- **R:** required.
- **C:** conditional (shown only when the offering exposes the choice).
- **H:** hidden.
- **O:** optional.

| Function (kinds) | Self-hosted | Managed | API |
| --- | --- | --- | --- |
| Model serving (`model`, `embedding_model`, full `fine_tuned_model`) | Host with location: R. Devices and placement: R. Engine with build: R. Weights and licence: R (D-R1, D-R2a). | Platform with location: R (D-R5). Instance type: C. Engine: C (only when the customer supplies the runtime). | Provider: R. Processing location: R when residency is constrained (D-R6). |
| Fine-tuned adapters | Inherit the exact base model's deployment; the selected engine must support the adapter/base tuple (#11/#33). | Same | Same inheritance where the selected provider offering supports the adapter/base composition; no API adapter support is inferred. Training capability remains #30 and does not set serving mode. |
| Retrieval backend (`vector_database`) | Host with location: R. Devices: R (a CPU is fine). Inference engine: H. Runtime requirements: CD-10. | Service with location: R | Service with location when residency is constrained |
| Storage | Per #9 | Per #9 | Per #9 |
| Tools, MCP servers | `external_connections`: R | Same | Same |
| Optional tiers (T3–T5) | Present when selected; selection-authoritative (companion note) | Same | Same |
| Operations | O; production requirements per #35–#39 | O | O |

v1 today: when the build mode is `self_hosted`, `rule.selfhost.requires.infrastructure` requires a hosting platform, accelerator, compute profile and inference engine for the whole build (C3).

## Compatibility proposals

All rules are hypotheses for #40 review.
- Each rule has one fixed severity, as the ruleset schema requires (C10).
- A known violation is `fail`. Ineligible or missing evidence leaves the dependent value unresolved, so the outcome is `unknown`. Eligible evidence that conflicts is resolved by #41's conflict order (EV-1); `unknown` remains only for genuine ties.
- Examples are synthetic.
- After review, D-R4 and D-R9 have been withdrawn and replaced by EV-1, which governs evidence rather than compatibility. D-R2 and D-R7 have each been split in two, because one rule can't carry two severities. Each half states its own scope, or names the fields it shares with its companion.
- None of these rules is approved or executable yet. They need the new fields and CD-1, and #41's evidence policies for EV-1.

**Template fields.** Each proposal covers the fields of the repository's rule-proposal template (C8). Fields that are the same for every rule are stated once here rather than repeated:
- **Severity and missing-data policy:** the table below.
- **Explanation:** the builder shows the rule's title, the part of the assertion that failed or couldn't be resolved, and the inputs involved. Each rule's remediation follows.
- **Affected consumers:** the builder's compatibility results, #40's ruleset, and the issues under each rule's dependencies.
- **Version and migration impact:** CD-7, for every rule.
- **Source evidence:** cited in the assertion or examples, and checked through EV-1.

| ID | Rule | Severity | `on_unknown` |
| --- | --- | --- | --- |
| D-R1 | Self-hosted model weights and rights | `error` | `review` |
| D-R2a | Licence eligibility conditions are met | `error` | `review` |
| D-R2b | Licence obligations are acknowledged | `warning` | `defer` |
| D-R3 | Quantization supported by the engine build on this hardware | `error` | `review` |
| D-R5 | Managed components have a platform and location | `error` | `review` |
| D-R6 | Residency covers processing and storage across the data flows | `error` | `review` (#41 may require `block`) |
| D-R7a | CPU meets the engine build's required instruction sets | `error` | `review` |
| D-R7b | CPU has the engine build's recommended instruction sets | `warning` | `defer` |
| D-R8 | Speculative draft matches its target | `error` | `review` |

Air-gap isolation is checked by W-R8 in the companion note. The version and migration impact is left to #40 (CD-7).

### D-R1 Self-hosted model weights and rights

- **Roles and pointers:**
  - selections of kind `model`, `embedding_model` or `fine_tuned_model`, with `/deployment/runtime_operator`;
  - the catalog access-mode field, which differs by kind (C1): `/spec/access_modes` for `model` and `embedding_model`, and `/spec/supported_access_modes` for `fine_tuned_model`;
  - catalog `/license/self_hosting_allowed` (C1);
  - for an adapter (`/spec/adapter_only: true`), also the base model selection reached through its `derived_from` link.
- **Applies when:** the component's `runtime_operator` is `self`.
- **Assertion:** the kind's access-mode field contains `weights`, and `self_hosting_allowed` is `true`. For an adapter, both hold for the adapter and for its base model.
- **Missing data:** `unknown`. `supported_access_modes` is optional in v1, so a fine-tuned item without it is unresolved.
- **Remediation:** choose an artifact whose weights are available and licensed for self-hosting, or change who operates the component.
- **Dependencies:** #5, #6, #33; CD-6 for the adapter's link to its base. Replaces the build-mode gating in `rule.selfhost.requires.weights` and `rule.model.selfhost.license` (C3).
- **Examples:**
  - Pass: an open-weight model run locally.
  - Fail: an API-only model with `runtime_operator: self`.
  - Unknown: licence fields absent.
  - Unknown: a full fine-tuned model with no `supported_access_modes`.
  - Skipped: a vector database.

### D-R2a Licence eligibility conditions are met

- **Roles and pointers:** model `/license_conditions` where `kind` is `eligibility`; build `/licence_answers`; for a `fine_tuned_model`, its base model's conditions, reached through its `derived_from` link.
- **Applies when:** the selected weights' licence binds the user, whatever the mode, and a qualified condition inventory establishes at least one applicable `eligibility` condition. User-operated weights and user-supplied weights or derivatives on provider-operated infrastructure require the applicable selected-terms assessment; provider-operated serving alone does not bypass it. A provider serving its own model under its API terms falls under those terms instead (#5, D-R5), without exempting a user's supplied derivative. Unresolved applicability or absent/incomplete condition coverage cannot establish a pass or skip. A known violation of an eligible applicable condition retains its failure while other unresolved conditions remain visible; skipping requires qualified complete absence of applicable eligibility conditions.
- **Inheritance:** follow a `fine_tuned_model`'s qualified `derived_from` lineage to retain and assess applicable base conditions across modes. The edge supplies provenance, not a rights grant or a conclusion that every condition applies to every act or derived artifact; unresolved legal applicability remains unknown. For example, Mistral Medium 3.5's licence withholds all rights from companies above a monthly revenue threshold, and applies that to the model and any derivatives, whoever provides them (D48).
- **Scope decision:** recorded under CD-6, with #30, including inherited base-model conditions.
- **Assertion:** every applicable eligibility condition is answered `met`, or separately qualified grant evidence establishes an exception for the actual subject, condition, activity and period. A `grant_ref` locator alone cannot satisfy the condition or acknowledge an obligation. These predicates follow the [actual #40 → #3 receiving decision](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/3#issuecomment-6254660533), not a new legal assessment.
- **Example condition** (Llama 3.1, D12): "If, on the Llama 3.1 version release date, the monthly active users of the products or services made available by or for Licensee, or Licensee's affiliates, is greater than 700 million monthly active users in the preceding calendar month, you must request a license from Meta". The release date is 23 July 2024. The question therefore covers the licensee and its affiliates, for the calendar month before that date.
- **Missing data:** `unknown` for unresolved applicable terms/condition coverage, unanswered eligibility, or unqualified grant evidence where an exception is needed.
- **Remediation:** supply the scoped answer or qualified grant evidence, or choose another model.
- **Dependencies:** #5, #6, #30; where licence answers live, and the scope across modes, is CD-6. Organisation-level answers are CD-12.
- **Examples:**
  - Pass: the applicable scoped condition is answered `met`.
  - Pass: the standard condition is `not_met`, but qualified grant evidence establishes the applicable exception.
  - Fail: answered `not_met`, with an explicit absence of a qualifying grant.
  - Fail: a fine-tune of a revenue-capped base model, served on a managed endpoint, with the applicable base-model revenue condition answered `not_met` and no qualifying exception. Provider-operated serving does not bypass it.
  - Unknown: unanswered, an absent condition inventory, unresolved applicability, or only a grant locator without qualified evidence.
  - Skipped: qualified complete evidence establishes no applicable eligibility conditions.

### D-R2b Licence obligations are acknowledged

- **Roles and pointers:** model `/license_conditions` where `kind` is `obligation`, such as Llama 3.1's incorporated acceptable use policy (D12); build `/licence_answers`.
- **Applies when:** the selected weights' licence binds the user, with D-R2a's qualified terms/lineage and condition-inventory assessment, and at least one applicable `obligation` condition is established. Unresolved applicability or condition coverage cannot establish a pass or skip; a known unacknowledged applicable obligation retains its failure.
- **Assertion:** every obligation is answered `acknowledged`.
- **Missing data:** `unknown`.
- **Remediation:** acknowledge the obligation, or choose another model.
- **Dependencies:** as D-R2a.
- **Examples:**
  - Pass: answered `acknowledged`.
  - Fail: answered `not_acknowledged`.
  - Unknown: no answer, an absent/incomplete obligation inventory, or unresolved applicability.
  - Skipped: qualified complete evidence establishes no applicable obligations.

### D-R3 Quantization supported by the engine build on this hardware

- **Roles and pointers:**
  - artifact `/quantization`;
  - the `engine_build` linked through `served_by`;
  - the devices' generation or backend;
  - eligible support documentation (EV-1; matrix format: CD-3).
- **Applies when:** a self-hosted model uses a quantized artifact.
- **Assertion:** eligible support documentation lists the combination as supported, once #41's conflict order has resolved any disagreement between documents (EV-1).
- **Missing data:** `unknown` when no eligible document covers the combination; absence from a list not marked complete is not "unsupported". A known "unsupported" entry, including one that wins under the conflict order, is `fail`.
- **Remediation:** choose a supported quantization, engine build or device.
- **Dependencies:** #11, #10. v1 checks precision against the engine and against the accelerator separately (C3).
- **Examples** (from D1):
  - Pass: AWQ with vLLM on an Ampere GPU.
  - Fail: AWQ with vLLM on an AMD GPU.
  - Unknown: no entry for a new method.
  - Fail, flagged as disputed: W8A8 with vLLM on an Arm CPU. vLLM's CPU page (D31) is more specific than its chart (D1) and limits W8A8 to x86 and s390x.
  - Skipped: an unquantized artifact.

### D-R5 Managed components have a platform and location

- **Roles and pointers:** `/deployment/capacity`; the `runs_on` link to a `hosting_platform`; its `hardware_location`.
- **Applies when:** a component's mode is `managed`.
- **Assertion:** a `runs_on` link to a `hosting_platform` exists, and that platform has a location.
- **Missing data:** `unknown` only when facts are unresolved, for example a region not mapped to a jurisdiction (CD-9). An absent link is a known violation, so it is `fail`.
- **Remediation:** link the component to its hosting platform, and record the platform's location.
- **Dependencies:** #9. v1 has no rule specific to managed mode (C3).
- **Examples:**
  - Pass: a dedicated endpoint with platform and region.
  - Fail: no host link.
  - Unknown: the region isn't mapped.
  - Skipped: an API component.

### D-R6 Residency covers processing and storage across the data flows

- **Roles and pointers:**
  - build `/workload/residency/processing` and `/workload/residency/storage`;
  - every selected component's locations (`data_terms` for provider-operated components, `hardware_location` for owned or rented hardware);
  - every enabled `external_connections` entry with `carries_workload_data: true`, resolved through `destinations`.
- **Training coverage:** the [actual T0 owner decision of 2026-10-18](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/3#issuecomment-6252011942) includes every component or destination that receives workload or training data, including managed training services and rented training compute, whether or not it has a serving mode. The [subsequent #40 → #3 receiving decision](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/3#issuecomment-6254660533) retains that boundary. A serving-only connection inventory cannot establish that training data has no external destination. Coverage of those transfers remains a representation requirement for #40/CD-4; this clarification does not introduce a v1 field or change the `carries_workload_data` field definition.
- **Applies when:** evaluated separately for each dimension. A dimension whose value is `none` is skipped. An unresolved dimension is `unknown`.
- **Assertion:** for each constrained dimension, every location of every component and destination in the data flow is contained in the allowed set. Containment follows the jurisdiction hierarchy, for example a subdivision within a country (CD-9).
- **Missing data:**
  - A destination with no recorded locations is `unknown`.
  - A known disallowed location is `fail`.
- **Remediation:** choose components or destinations in allowed locations, disable the connection, or change the constraint.
- **Dependencies:** #9, #5, #37, #41. Extends `rule.host.region` and `rule.deployment.target.region` (C3).
- **Examples:**
  - Pass: storage-only constraint; data is stored in an allowed country, and processing isn't checked.
  - Fail: processing-only constraint; a local engine sends logs to an external host processing elsewhere.
  - Fail: an offering that stores data in-region but processes it elsewhere (D19).
  - Fail: evaluating a fine-tuned model on Foundry's `Developer` deployment type with a processing constraint. D16 says it processes in any Azure region, with no data-residency guarantee.
  - Unknown: a telemetry destination with no locations.
  - Fail (synthetic): a self-hosted serving build sends training data to a managed training service whose processing location is known to be outside the processing constraint. The training service does not change the serving mode; its processing location still fails D-R6.
  - Unknown (synthetic): rented training compute receives data, but its location for a constrained dimension is not recorded. Excluding the training run from mode does not make that residency check pass or skip it.
  - Skipped: both dimensions are `none`.

### D-R7a CPU meets the engine build's required instruction sets

- **Roles and pointers:** device `/isa_features`; the required features of the engine build linked through `served_by` (Proposal field on engine items).
- **Applies when:** a model-kind component's engine runs on a CPU device. Runtime requirements for non-model services are left to CD-10.
- **Assertion:** the required features are a subset of the device's features.
- **Missing data:** `unknown`.
- **Remediation:** choose an engine build that supports the CPU's instruction sets, or another device.
- **Dependencies:** #10, #11; CD-10.
- **Examples:**
  - Pass: vLLM on Arm with NEON (D31).
  - Fail: vLLM on Arm without NEON.
  - Unknown: features not detected.
  - Skipped: a GPU-only placement.

### D-R7b CPU has the engine build's recommended instruction sets

- **Roles, applicability, missing data and dependencies:** the same as D-R7a, reading the engine build's recommended features instead of its required ones.
- **Assertion:** the recommended features are a subset of the device's features.
- **Remediation:** choose a CPU with the recommended features, or accept the documented limitations.
- **Examples:**
  - Pass: vLLM on x86 with `avx512f`.
  - Fail (warning): an `avx2`-only x86 CPU, which vLLM documents as "limited features" (D31).
  - Unknown: not detected.
  - Skipped: no recommendation recorded.

### D-R8 Speculative draft matches its target

- **Roles and pointers:** the draft artifact's declared target, precision, engine and hardware; the draft-to-target relation (CD-6).
- **Applies when:** a draft is selected.
- **Assertion:** all of the following:
  - the draft declares the selected target artifact;
  - where the publisher requires it, the precision matches (Gemma 4 QAT, D10);
  - the engine build and hardware the draft lists are selected (D25).
- **Missing data:** `unknown`.
- **Remediation:** choose the draft published for the selected target, precision, engine and hardware, or remove the draft.
- **Dependencies:** #6, #11; CD-6.
- **Examples:**
  - Pass: a QAT target with a QAT assistant of the same precision.
  - Fail: a QAT target with a non-QAT assistant.
  - Fail: a draft listing "SM 120 only" on another GPU generation.
  - Unknown: the draft declares no target.
  - Skipped: no draft selected.

## Open contract decisions

These are decisions for #40 and #41, recorded rather than solved in these notes. Each ID is shared with the companion note.

| ID | Decision | Raised by | Accountable |
| --- | --- | --- | --- |
| CD-1 | A typed answer-state representation, and how the evaluator normalises it. v1 treats the string `"unknown"` as known (C11 probe). The design must distinguish "not relevant", "not yet known" and "not selected". | Workload note | #40 |
| CD-2 | Physical memory pools, device instances, co-residency scenarios, and byte allocation for `placement` | W-R6 | #40 (with #10) |
| CD-3 | Protocol identity, the canonical configuration key (essential vs display fields), protocol compatibility, result schemas for `kernel_throughput` vs `service_level`, coverage matching for support documentation, how derived estimates are assessed, and how the evaluator encodes #41's conflict order for eligible results | EV-1, reports, W-R7 | #41 (with #10, #62) |
| CD-4 | The isolation-boundary model: endpoint membership, connection lifecycle and state, and artifact readiness manifests | W-R8 | #40 |
| CD-5 | Per-stage load and length records for pipelines | Workload note | #40 (with #10) |
| CD-6 | Relationship details: the draft-to-target link, where `licence_answers` live, mapping the hardware inventory to device selections, roles that disambiguate multiple links, whether an adapter's `derived_from` link must match its `base_model_ref`, and the effective serving capabilities of fine-tuned models and adapter/base compositions; the scope of licence conditions across modes, including conditions inherited through `derived_from` | Bindings, D-R1, D-R2, D-R8, W-R1 | #40 (with #6, #30, #33) |
| CD-7 | The migration strategy: what is additive vs replacement, the treatment of the three workload copies, adapters and deprecation, how legacy build-level mode is interpreted, and the contract version | All rules | #40 |
| CD-8 | Reporter and execution independence, and the acceptance policy that would let community evidence decide verdicts | Trust grades | #41 |
| CD-9 | The jurisdiction hierarchy, containment, named groups, and mapping provider regions to jurisdictions | D-R5, D-R6 | #41 (with #9) |
| CD-10 | Runtime requirements for non-model services such as vector databases | D-R7a, matrix | #40 (with #11, #15) |
| CD-11 | Context budget semantics: shared vs separate input and output limits, a maximum-input field, and route-specific overrides | T1 (#88) | #40 (with #7) |
| CD-12 | Private scope-qualified organisation attestations: establishment jurisdiction, model/system-specific EU market placement, dataset/purpose-specific lawful-basis reference, revenue and monthly active users. Reuse requires matching subject, definition, use and temporal scope; private answers/grants do not transfer on fork. The accepted #40 receiving scope below chooses the research representation; actual assessments and successor encoding remain separate | T5 review of #81, D-R2a; actual #40 → #3 receipt | #40 (with #30 and #32; #31's K-series reads no CD-12 attestation) |
| CD-13 | Rules over several selections of one kind: a quantifier over all enabled selections, and semantic rejection of duplicate `primary` roles before evaluation, so "not selected", "not relevant" and "not yet known" are not collapsed into `skipped` | T4 on #40 | #40 |

## Pricing and capacity

No prices are recorded. Charge basis, ownership and commitment are independent:
- **Bedrock Provisioned Throughput** is billed hourly, with optional commitment terms (D18).
- **Azure PTU** is billed hourly per PTU, with optional reservations (D17).
- **Hugging Face Inference Endpoints** charge an hourly rate calculated by the minute (D13).
- **SageMaker AI** charges for the instance type chosen, on its instance-based inference path (D14).
- **Owned hardware** has ownership `owned` and charge basis `none`; its costs go to #39.

## Recommendation and rationale

1. **Adopt the operator and capacity test,** with billing kept separate, explicit capacity semantics, `unknown` handling, and classification by the test rather than by vendor terminology.
2. **Make mode per component.** Use `build.links` as the only representation of relationships, and add a `deployment` object for the facts that aren't relationships.
3. **Keep fit records immutable while retained,** with mode-appropriate keys, and use one eligibility predicate (EV-1), with checks by evidence type, wherever evidence is consumed. Eligible evidence that disagrees is resolved by #41's conflict order.
4. **Treat CPU-only and hybrid CPU+GPU builds as first-class,** adding bandwidth (in GB/s), instruction sets, NUMA nodes, memory kind and typed placement.
5. **Adopt crowdsourced reports as informative evidence,** with two protocol types, trust grades, facilitation, incentives (as hypotheses), integrity checks and privacy rules. Let #41 decide when they may decide verdicts (CD-8). Ask #48 and #57 to assess the existing projects, and #41 and #60 whether their data can be linked.
6. **Take CD-1 to CD-13 to #40 and #41,** alongside D-R1 to D-R8.
7. **Store deployment mode on the build and its selections, not as catalog items.** In v1 it is a catalog kind (C6) needing provenance with a public URL (C7).

## Structured artifacts

None (Recommendation 7).

## Open questions and handoffs

Each question has one accountable issue (its assignee is the owner); others are consulted. Contract design questions are listed separately as CDs. Q8 and Q9 ownership was refreshed from live issue assignees on 2026-10-18: [#52](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/52) is assigned to @appletechie/@PUSHINGSQUARES and [#48](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/48) to @Mattycodes69/@appletechie. This records routing, not receiving acceptance.

| # | Question | Accountable | Consulted |
| --- | --- | --- | --- |
| Q1 | Who maintains fit records and support matrices? | #41 | #10, #11 |
| Q2 | How should unified memory, CPU-only devices and CPU+GPU placement be sized? | #10 | #40 |
| Q3 | For each managed platform, can the customer choose or supply the runtime? | #9 | #11 |
| Q4 | Which `data_terms` fields are mandatory before an API or managed component is shown? | #5 | #9, #41 |
| Q5 | Does a fit record carry quality impact, or only memory and speed? | #36 | #11 |
| Q6 | Where do fit reports live, and under what licence? | #41 | #40 |
| Q7 | Should existing community datasets (D36–D41) be linked or imported, and do their terms allow it? | #41 | #60 |
| Q8 | Do the proposed incentives work? | #52 (@appletechie, @PUSHINGSQUARES) | — |
| Q9 | How do the existing community projects change the differentiation case? | #48 (@Mattycodes69, @appletechie) | #57 |
| Q10 | How are hybrid builds saved, shared and compared? | #42 | — |
| Q11 | What remains after a report or its attribution is deleted (nothing, a tombstone, or aggregate statistics), and how long are reports and raw logs kept? | #41 | #60 |

### Recorded receiving dispositions

This subsection and the coverage table that follows preserve the earlier receiving record. The [current reconciliation](#current-research-reconciliation--2026-10-18) records later actual decisions and their retained limits; an old pending label is not a new request for an already received interface.

The [#3 handoff request](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/3#issuecomment-6238501962) includes @tynamite's **#60 acceptance of the community-dataset-rights handoff**, with #60's own handoffs retained. This is routing/ownership acceptance, not a blanket import or redistribution grant.

[@zwright8's scoped response](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/3#issuecomment-6242696588), reviewed against main `7acbefbf4e4e700231e88be272bc89e3a73dde15`, records:

| Consumer | Accepted scope and retained constraint |
| --- | --- |
| #5 | Per-offering API/managed data terms, region and account conditions; unavailable entitlements remain unknown |
| #6/#30 | Source-specific licence, weight-access and derivative-lineage evidence; `derived_from` grants no rights, and generic capability does not establish fine-tuning permission |
| #11 | Exact artifact/base/tokenizer/template, engine/build/plugins, backend/kernel, precision, ISA and draft-model tuple; missing evidence unresolved and incomplete lists cannot manufacture negatives |
| #40 | D-R1–D-R8, EV-1 and CD-1–CD-12 proceed through reviewed version/migration proposals; frozen v1 and historical outcomes stay unchanged |

The response retains operator/capacity mode classification and the training/serving distinction; it does not approve every external claim. Remaining scopes are #9, #10, #31, #32, #33, #36, #37, #39, #41, #42, #48, #52, #57 and #62, plus other co-assignees' scopes in the accepted rows. #30/#31/#32 retain their distinct CD-12 and derivative-permission decisions. No receiving disposition is inferred from authorship.

## Acceptance criteria coverage

| Criterion (issue #3) | Where | Status |
| --- | --- | --- |
| Definitions and a boundary example per pair | [Definitions](#definitions-proposal) | Reviewer: met |
| Mode × component matrix | [Component requirements](#component-requirements-by-function-and-mode-proposal) | Revised: fine-tuned access-mode field corrected in D-R1; D-R7a scoped to model engines |
| Per-build vs per-component decision | [Per-component mode](#per-component-mode-and-relationships-decision-proposal) | Reviewer: met; v1 links claim corrected |
| Comparison fields | [Field dictionary](#field-dictionary), [EV-1](#evidence-eligibility-ev-1) | Revised: licence answers typed by condition kind; evidence checked by type; remaining items recorded as CDs |
| Rules in the shared format; hypotheses separated | [Compatibility proposals](#compatibility-proposals) | Revised: common template fields; split rules state their scope; evidence moved to EV-1 |
| Primary sources with access dates | [Evidence](#evidence) | Revised: contract cited as adopted; vLLM CPU documentation conflict resolved by #41's conflict order |
| Handoffs confirmed | [Recorded dispositions](#recorded-receiving-dispositions) | Partial, scoped receipts only |
| Open questions with owners | [Open questions](#open-questions-and-handoffs) | Accountable issues identified; Q8/Q9 live assignees recorded 2026-10-18. Receiving dispositions remain separate |
| Decision record merged | PR #81 | Merged research; remaining criteria and handoffs separate |

## Current research reconciliation — 2026-10-18

This assessment reads the **ten unchanged research criteria in [issue #3](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/3)** and the complete [original receiving request](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/3#issuecomment-6238501962). The original #81 record and later corrections are delivered research. The [final #81 source review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/81#pullrequestreview-5558965388), [actual #126 example/routing review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/126#pullrequestreview-5560506323), [correcting #126 acceptance](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/126#pullrequestreview-5560765303) and [#398 delivery](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/398#issuecomment-6255169867) retain their own revisions and validation scope.

The ChatGPT research agent performed the current receiving reconciliation through the CompleteDotTech account under the user's delegated project engineering authority. These are attributed technical decisions, not replies by absent assignees. Review of this amendment, its actual required validation and normal main delivery remain the PR gates before final issue acceptance. No runtime, released successor contract, actual training/deployment result or source-use permission follows from this research assessment.

### Six minimum comparison fields

The issue's conceptual minimum fields map to the existing definitions and dictionary; this table introduces no additional wire field.

| Minimum field | Recorded type / unit and decision | Evidence and unresolved boundary |
| --- | --- | --- |
| Mode | Serving enum `api` / `managed` / `self_hosted` / `unknown`; the build additionally derives `hybrid` | [Classification test](#the-classification-test) and qualified operator/capacity facts. Billing, transport protocol, a legacy label and training do not supply them. |
| Operator of weights / runtime | `runtime_operator` and `runtime_supplied_by` enums; weight access and applicable licence conditions are separate facts | [Field dictionary](#field-dictionary), D-R1/D-R2, C1/C9 and D13/D15/D16; #5/#6 retain publisher/distributor/licensor and offering identity. A supplier is not automatically the runtime operator or rights holder. |
| Data-retention and training-use controls | Typed training-use and zero-retention eligibility enums; purpose/endpoint/data-category retention entries, including integer days for duration | `data_terms` and D19–D22 retain effective offering, account, model, feature and agreement scope. Unknown approval is not zero retention or permission. |
| Residency options | Separate processing/storage location-code sets and explicit constrained / unconstrained / unresolved inputs | D-R6, `hardware_location`, `destinations` and CD-9. A provider region, hint or organisation domicile does not establish a complete data-flow inventory. Training destinations remain included. |
| Scaling responsibility | The runtime operator's documented responsibility, with the separate customer-supplied-runtime fact; no numeric unit | The classification test explicitly distinguishes platform scheduling/scaling/restarts from supplying a container (D15). Actual offering controls, limits, account capacity and selected operating configuration remain #9/#37 evidence; a mode alone supplies none of those values. |
| Billing basis | Existing `charge_basis`, `ownership` and minimal `commitment` descriptor; integer months only where that descriptor applies | [Pricing and capacity](#pricing-and-capacity), D13/D14/D17/D18 and the actual #39 narrowing below. No price is recorded here; richer terms stay dated Pricebook facts rather than being coerced into this descriptor. |

### Required outgoing directions

The current receiving-source comparison used delivered main [`c942f180`](https://github.com/Pick-Your-AI/pick-your-ai-research/commit/c942f18059f1bb0eb76f8e5687c60cbd515bc3ab); the Deployment Mode producer there is blob `f95c3ec1773e10183cd325f87e2040c7954a9385`. Earlier named-owner receipts keep their original source revisions; the current review confirms the retained interface within those conditions. An issue's closed state is not used as a substitute for a receipt.

| Declared direction | Actual receiving evidence | Accepted interface and retained condition |
| --- | --- | --- |
| #3 → #5 | [zwright8's scoped receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/3#issuecomment-6242696588), 2026-10-17; current [provider note](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/c942f18059f1bb0eb76f8e5687c60cbd515bc3ab/research/T1-model-selection/model-provider.md) | Accept per-offering API/managed `data_terms`, operator/capacity, location and account conditions. Unknown entitlement remains unknown. Provider/publisher/distributor, billing and training lifecycle remain distinct; Q4's display/admission detail stays with #5/#41. |
| #3 → #9 | [appletechie's actual receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/3#issuecomment-6245701946), 2026-10-18; current [hosting note](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/c942f18059f1bb0eb76f8e5687c60cbd515bc3ab/research/T2-infrastructure/hosting.md) | Accept the operator/capacity test, per-offering runtime supplier, platform and actual location. `personal_device` is not a new v1 `hosting_type`; serving capacity must be evidenced. Offering membership, quota, stock and a complete processing/storage mapping are separate. |
| #3 → #10 | [appletechie's actual receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/3#issuecomment-6245701946); current [compute note](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/c942f18059f1bb0eb76f8e5687c60cbd515bc3ab/research/T2-infrastructure/gpu-compute.md) | Accept CPU/unified/system-memory scope and typed placement. Q2 is an accepted #10 follow-up, not a supplied CPU measurement. Preserve GPU-live versus host-peak accounting, physical pools, per-device plans, expanded sequence/admission scope and explicit missing bytes; CD-2 retains its own representation work. |
| #3 → #11 | [zwright8's scoped receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/3#issuecomment-6242696588); current [engine note](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/c942f18059f1bb0eb76f8e5687c60cbd515bc3ab/research/T2-infrastructure/inference-engine.md) and [build supplement](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/c942f18059f1bb0eb76f8e5687c60cbd515bc3ab/research/T2-infrastructure/engine-build-evidence.md) | Accept exact artifact/base/tokenizer/template, engine/build/plugin, backend/kernel, precision, ISA and draft tuple inputs. Missing evidence stays unresolved; omission from an incomplete list creates no negative, and a versioned documentary pass does not become a reproduced runtime result. |
| #3 → #37 | [Original storage narrowing](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/3#issuecomment-6247690365); [actual new receiving decision](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/37#issuecomment-6255222753), 2026-10-18 | Accept the delivered R36 storage requirement separately from R6/S17/S28 processing/endpoint evidence, with #38 P5/M-R67 for sinks/logs and the explicit T0 D-R6 prefix. This satisfies the prior missing-storage representation condition. Complete actual locations, training transfers, isolation evidence and selected-target readback remain required for a configured build. |
| #3 → #39 | [appletechie's narrowing](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/3#issuecomment-6245701946) and [PUSHINGSQUARES's concrete decision](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/3#issuecomment-6247690365), 2026-10-18; current [cost note](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/c942f18059f1bb0eb76f8e5687c60cbd515bc3ab/research/T6-deployment-operations/cost-estimate.md) | Accept the narrowing: keep `billing` minimal and independent of mode. One-week commitments, non-cancellable terms, prepaid-credit fees, minimums and allowances remain Pricebook facts. Do not invent an integer-month conversion, a new meter, an amortisation policy or a complete cost total. |
| #3 → #40 | [Earlier routing receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/3#issuecomment-6242696588), [#126 example review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/126#pullrequestreview-5560506323), [correcting acceptance](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/126#pullrequestreview-5560765303) and [current conditional receiving decision](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40#issuecomment-6255452448) | Accept the defined deployment, exact-link, evidence and D-R proposal interface into the versioned central process under the qualified-condition/grant policy in the reverse receipt below. The receiving decision requires the D-R2 and adapter-matrix corrections in this amendment to be reviewed and delivered before whole #3 acceptance. The current field dictionary and M1–M5 retain component evidence, ambiguity and historical v1 behavior. This neither releases a successor nor treats all CD implementation/integration work as finished. |

**The reverse direction remains separate.** [#40 → #3 receipt 6254660533](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/3#issuecomment-6254660533) accepts the selected CD-1/CD-6/CD-10/CD-12 research representations at proposed source `45b20960cbc4652fb3341c977a025821c96595f9`, blob `375506eea95bd7fc30883c0e4f2a2f5496f77cfd`. The source was not delivered by that receipt. Its complete link/condition/runtime/private-answer boundaries were read for this reconciliation: D-R2 now distinguishes qualified condition absence from a missing inventory, a qualified exception from a bare grant locator, and source-qualified inheritance from a legal conclusion based only on a lineage edge. CD-12 now states scope-qualified reuse. These refinements change no field name, primitive type, rule ID, severity or frozen file.

### Wider original request and resolved questions

The original owner request included additional consumers beyond the seven declared in the issue body. Their decisions remain visible here instead of being discarded by a seven-row checklist.

| Scope | Actual evidence and current disposition | Finite remaining owner scope |
| --- | --- | --- |
| #6 / #30 rights and training boundary | [zwright8](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/3#issuecomment-6242696588) and [appletechie](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/3#issuecomment-6245701946) accept applicable selected-terms/derivative inputs across modes. D-R2 and the accepted incoming #40 scope preserve qualified conditions, grants and unknowns; provider operation supplies no exemption. | #30/#33 own actual method, derivative, commercial/production-use, NOTICE and applicable obligation assessment; #40 owns exact bindings and successor representation. |
| #31 training destinations | The [actual T0 owner clarification](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/3#issuecomment-6252011942) answers the [specific #31 narrowing](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/3#issuecomment-6245701946), and #398 delivers it in D-R6. Training is outside serving mode and inside applicable processing/storage coverage. | #31's K-series reads no CD-12 attestation; #31/#37 still need actual training locations and #40/CD-4 their complete representation. No training run or performance is supplied. |
| #32 scoped attestations | The [actual narrowing](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/3#issuecomment-6245701946) and [incoming #40 decision](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/3#issuecomment-6254660533) separate model/system EU placement and dataset/version/purpose lawful basis from workload categories. Private answers and grants do not copy on fork. | #32 and the responsible dataset/source-rights/privacy assessor retain actual assessments; #40 owns condition/subject/definition/use/time binding. A reference or boolean supplies no independent legal conclusion. |
| #33 adapter deployment | [appletechie's receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/3#issuecomment-6245701946) accepts exact-base deployment inheritance while retaining adapter support, full revision and licence conditions. The component matrix now applies that serving rule consistently in every column; it asserts no shared-API adapter offering. | #11/#33 own the actual base/artifact/engine/provider support tuple. A merged full model has its own serving deployment; provider training remains #30. |
| #36 Q5 and #62 protocol identity | Both [appletechie](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/3#issuecomment-6245701946) and [PUSHINGSQUARES](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/3#issuecomment-6247690365) answer Q5 **no**: fit records carry memory, load success and speed; quality is a separate exact-tuple result, optionally referenced. #62's narrowed serving protocol receipt additionally preserves task content-lock, run count and grader revision for quality evidence. | #36/#62 own the separate quality tuple, uncertainty and any future experiment; #40 owns an optional result-reference field. The [later #62 decision](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/62#issuecomment-6253421648) selects no replication for its desk result; this does not invent measurements or fill missing publisher pins. |
| #48 / #52 / #57 community projects and incentives | The [original narrowing](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/3#issuecomment-6245701946) is retained. [Current #48 scope](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/48#issuecomment-6249724402) leaves the six community resources as source leads; [#52](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/52#issuecomment-6250471522) retains untested contributor incentives; [#57](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/57#issuecomment-6249255630) rejects broad H5 and retains H5b as an untested optional hypothesis. D46 describes its pinned historical register, not current novelty. | #48 owns further discovery/classification, #52/#63 actual incentive/recruitment/consent research, and #57 scoped differentiation. No interviews, willingness-to-pay result, independent run or universal advantage is asserted. |
| #60 community-data rights | [tynamite's original receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/3#issuecomment-6238501962) accepts ownership/routing of Q7/Q11. It is not a permission grant; [current #60 acceptance](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/60#issuecomment-6248616771) retains material/use-specific exclusions and conditions. | #41/#60 retain each source, material, intended use and permission basis. A source citation, code licence or historical report is not authorization to import, display or redistribute another artifact. |
| #41 EV-1 and community evidence | [Current #3 → #41 receiving decision](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/41#issuecomment-6255452946) accepts the exact evidence/protocol, freshness/conflict and informative-community-report interface. Checked, reproduced, comparable and permitted remain separate. | Q1/Q6/Q7/Q11 and CD-3/CD-8 retain explicit evidence custody, report storage/licensing, admission and deletion/retention follow-ups; no arbitrary TTL or new right is supplied. |
| #42 Q10 and report-from-build | The [original provisional response](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/3#issuecomment-6245701946) is followed by [the current receiving decision](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/42#issuecomment-6255453677) on delivered per-component comparison and the complete disclosure boundary. Receive only view-eligible configuration evidence for a report; withheld/private values and derived disclosures cannot transfer. | #42 retains its actual #40 prerequisite, retention/share access, permitted history and complete projection/replay decisions. A partial configuration view is not a qualified fit report or the original artifact's exact bytes. |

### Named follow-up owners

Live assignees were read on 2026-10-18. These rows keep the remaining questions finite; accepting a research interface does not fabricate its later configuration or measurement.

| Question / scope | Existing accountable owners | Current decision or remaining input |
| --- | --- | --- |
| Q1 / Q6 / Q7 / Q11 — evidence custody, reports, source use, deletion and retention | #41: @tynamite / @PUSHINGSQUARES; #60: @tynamite / @appletechie for material/use decisions | Informative reports and qualified source use are accepted boundaries; actual report-store/licence/retention/admission choices remain explicit. |
| Q2 — CPU, unified memory and placement | #10: @Mattycodes69 / @appletechie, with #40 CD-2 | CPU/system/unified scope and separate pools are accepted. Missing measured capacity, host peak and byte allocation remain missing; #61's actual evidence criteria are separate. |
| Q3 — customer-supplied runtime per offering | #9: @Mattycodes69 / @appletechie | The recorded per-offering answer in 6245701946 is accepted; a new offering needs its own runtime/capacity evidence. |
| Q4 — provider data-term display/admission | #5: @zwright8 / @tynamite, with #41 | Preserve each term's exact offering/account/feature/location scope and visible unknowns; no blanket eligibility or zero-retention claim. |
| Q5 — quality in fit records | #36: @appletechie / @PUSHINGSQUARES; #40 for the optional reference | Answered **no** by both actual co-owner receipts. Quality remains a separate result with its own matched protocol and evidence. |
| Q8 — contributor incentives | #52: @appletechie / @PUSHINGSQUARES | Untested hypotheses; contributor incentives and the #63 interview incentive are distinct. |
| Q9 — community-project differentiation | #48: @Mattycodes69 / @appletechie; #57: @tynamite / @appletechie | Historical absence from D46 is not novelty. Current discovery scope and the untested H5b distinction remain explicit. |
| Q10 — hybrid saved/shared comparisons | #42: @tynamite / @appletechie | Per-component modes and comparison limitations are received; actual source bindings, share/fork disclosure, retention and successor integration retain #42/#40 ownership. |
| CD-1–CD-13 — central representations and policy | #40: @zwright8 / @tynamite; #41: @tynamite / @PUSHINGSQUARES for evidence/admission | Preserve the selected research representations and their actual receipts. Frozen v1 and historical results remain unchanged; no open prototype or consumer issue is completed by this note. |

### Literal issue #3 criteria

| Original criterion | Evidence in this record and current assessment |
| --- | --- |
| 3.1 Definitions with a boundary example per pair | The operator/capacity definition and all six unordered pairs among API, managed, self-hosted and hybrid are covered; extra vendor-terminology and protocol examples retain source scope. |
| 3.2 Mode × component matrix | The R/C/H/O matrix covers serving, adapters, retrieval, storage, tools, optional tiers and operations; hybrid composes the per-serving-component rows. The adapter cell now consistently describes serving rather than a training channel. |
| 3.3 Per-build versus per-component proposal | The recorded decision uses one qualified `build.links` authority and derives overall mode; ambiguity and missing component facts stay unknown. Actual #126 M1–M5 review retains historical v1 labels/outcomes. |
| 3.4 Merged canonical decision record following the research method | #81 delivered the original canonical note; #398 delivered the training/residency correction. This amendment preserves the method sections and needs its own reviewed main delivery before final acceptance. |
| 3.5 Relevant deployment-mode coverage | API/shared, managed/reserved-or-dedicated and self-operated candidates plus hybrid composition are present. Training, storage, tools and MCP do not set serving mode and retain their separate applicable checks. |
| 3.6 Typed/unit/evidence comparison fields | The complete dictionary and six-minimum-field map specify enums, identities, locations, durations, counts, memory units and evidence/unknown handling. New source-condition bindings remain explicit #40 research representations. |
| 3.7 Shared-format rules and separated hypotheses | D-R proposals retain their common template, roles, applicability, assertion, remediation, dependencies, fixed severity and missing-data policy. All remain labelled proposals; EV-1 governs evidence and D-R2 now follows the actual qualified-condition/grant receipt. |
| 3.8 Primary sources, dates and numerical conditions | C1–C11 and D1–D48 retain their primary locators, original date/version/region scope and claim-level grades. Hardware/model figures are published observations, calculations retain their basis and examples remain synthetic. D48's explicit 2026-10-17 date is preserved; the current repository/receiving review does not advance a vendor access date or recertify every historical claim as current. No monetary price is added. |
| 3.9 Each declared handoff confirmed | The seven directional rows link actual named-owner or delegated receiving decisions, including the delivered R36 remedy and the concrete minimal-billing narrowing. The broader owner request is separately reconciled above. Reverse receipts and source merges are not substituted for outgoing acceptance. |
| 3.10 Named open-question owners | Q1–Q11 and CD-1–CD-13 retain accountable issues, current assignees and finite remaining questions. Resolved Q5, training-residency and billing decisions are recorded explicitly. No generic implementation, numerical default, rights grant or fieldwork requirement is invented as an extra research criterion. |

## Evidence

The original external-source inventory was accessed on 2026-10-16 except where an entry explicitly records another date; D48 was accessed on 2026-10-17. The 2026-10-18 receiving and repository reconciliation records project decisions, not a fresh vendor-source sweep or a new measurement. Vendor terms change often; re-check them before relying on this note. Relative "updated" labels are not used as versions.

**Contract (v1, adopted in PR #44).** Links are pinned to the inspected revision `a222013c1f0106159132564d05e5d24666ad6342`. Its file tree is identical to the merge commit `9769fcd9ea380b1211669b2753181c7782444178`. C- entries are Primary documentation.

| ID | Source | Location |
| --- | --- | --- |
| C1 | [`contracts/v1/schemas/catalog-item.schema.json`](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/a222013c1f0106159132564d05e5d24666ad6342/contracts/v1/schemas/catalog-item.schema.json) | `spec_deployment_mode`, `spec_model`, `spec_embedding_model` (`access_modes`), `spec_fine_tuned_model` (`supported_access_modes`, `adapter_only`, `base_model_ref`), `spec_hosting_platform`, `spec_accelerator`, `spec_compute_profile`, `spec_inference_engine`; `license`, `billing_class` |
| C2 | [`contracts/v1/schemas/selection.schema.json`](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/a222013c1f0106159132564d05e5d24666ad6342/contracts/v1/schemas/selection.schema.json) | `settings_model.serving_mode`, `settings_inference_engine.quantization`, `settings_hosting_platform.network_isolation` |
| C3 | [`contracts/v1/baseline/core-ruleset.json`](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/a222013c1f0106159132564d05e5d24666ad6342/contracts/v1/baseline/core-ruleset.json) | 45 rules, 17 gated on `mode == "self_hosted"`; rules cited in the text |
| C4 | [`contracts/v1/docs/DEPENDENCIES.md`](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/a222013c1f0106159132564d05e5d24666ad6342/contracts/v1/docs/DEPENDENCIES.md) | Line 13 ("`self_hosted` or `hybrid`") |
| C5 | [`contracts/v1/schemas/resource-estimate.schema.json`](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/a222013c1f0106159132564d05e5d24666ad6342/contracts/v1/schemas/resource-estimate.schema.json) | `estimates/items` |
| C6 | [`contracts/v1/schemas/component-registry.json`](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/a222013c1f0106159132564d05e5d24666ad6342/contracts/v1/schemas/component-registry.json) | `kinds/deployment_mode` |
| C7 | [`docs/RESEARCH_WORKFLOW.md`](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/a222013c1f0106159132564d05e5d24666ad6342/docs/RESEARCH_WORKFLOW.md) | Line 26 |
| C8 | [`templates/rule-proposal.md`](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/a222013c1f0106159132564d05e5d24666ad6342/templates/rule-proposal.md) | Rule proposal fields |
| C9 | [`contracts/v1/schemas/build.schema.json`](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/a222013c1f0106159132564d05e5d24666ad6342/contracts/v1/schemas/build.schema.json) | `links`: `from_selection_id`, `to_selection_id`, `relation` (including `runs_on`, `served_by`, `uses`, `derived_from`, `feeds`); `policy.min_resource_confidence` |
| C10 | [`contracts/v1/schemas/ruleset.schema.json`](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/a222013c1f0106159132564d05e5d24666ad6342/contracts/v1/schemas/ruleset.schema.json) | One `severity` per rule; `on_unknown` enum; references by `selection_id` |
| C11 | [`contracts/v1/reference/evaluate.py`](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/a222013c1f0106159132564d05e5d24666ad6342/contracts/v1/reference/evaluate.py) | `UNKNOWN` sentinel (line 14); `selection_id` resolution (line 66); an expression probe confirmed that a string `"unknown"` evaluates as a known value |

**External sources.**

| ID | Publisher, title and URL | Version / date shown | Evidence grade | Limitations |
| --- | --- | --- | --- | --- |
| D1 | vLLM project, "Quantization": <https://docs.vllm.ai/en/latest/features/quantization/> | "Last update: September 14, 2026" | Primary documentation | vLLM only; "subject to change"; disagrees with D31 on Arm W8A8, where D31 governs under #41's conflict order |
| D2 | vLLM project, "Installation": <https://docs.vllm.ai/en/latest/getting_started/installation/> | "Last update: May 11, 2026" | Primary documentation | — |
| D3 | ggml-org, llama.cpp README: <https://github.com/ggml-org/llama.cpp/blob/f3363593f457169cdfbdfe22ea399b1cc139ba18/README.md>; `docs/models.md`: <https://github.com/ggml-org/llama.cpp/blob/f3363593f457169cdfbdfe22ea399b1cc139ba18/docs/models.md> | Commit `f336359` | Primary documentation | — |
| D4 | vLLM releases: <https://github.com/vllm-project/vllm/releases> | As shown at access | Primary documentation (release metadata) | — |
| D5 | llama.cpp build tags, read with git from <https://github.com/ggml-org/llama.cpp> | Inventory checked 2026-10-16: `b11676`–`b11696`, with `b11686`, `b11689`, `b11692` and `b11694` absent; commit times in UTC | Primary documentation (repository metadata) | Commit timestamps, not release-publication timestamps |
| D6 | Ollama, FAQ: <https://docs.ollama.com/faq>; OpenAI compatibility: <https://docs.ollama.com/api/openai-compatibility> | Live documentation; no revision pinned | Primary documentation | Ollama also documents a cloud service |
| D7 | ml-explore (Apple), MLX README: <https://github.com/ml-explore/mlx/blob/b6642e604843776705b57b1eaecb6f57e519b793/README.md> | Commit `b6642e6` | Primary documentation | — |
| D8 | vLLM project, "OpenAI-Compatible Server": <https://docs.vllm.ai/en/latest/serving/online_serving/openai_compatible_server/> | "latest" | Primary documentation | — |
| D9 | Kwon et al., PagedAttention, §3: <https://arxiv.org/abs/2309.06180> | arXiv v1 | Primary documentation (calculation) | OPT-13B, FP16 |
| D10 | Google DeepMind, Gemma 4: <https://huggingface.co/google/gemma-4-26B-A4B-it>; QAT Q4_0 GGUF: <https://huggingface.co/google/gemma-4-12B-it-qat-q4_0-gguf> | Created 2026-03-11 and 2026-06-05 | Primary documentation | Licence metadata: apache-2.0 |
| D11 | Qwen, Qwen3.8-27B: <https://huggingface.co/Qwen/Qwen3.8-27B>; Qwen3.8-Flash-Next: <https://huggingface.co/Qwen/Qwen3.8-Flash-Next> | Created 2026-08-05 and 2026-08-24 | Primary documentation; Vendor claim (offloading) | — |
| D12 | Meta, Llama 3.1 Community License, §2: <https://raw.githubusercontent.com/meta-llama/llama-models/main/models/llama3_1/LICENSE> | Release date 23 July 2024 | Primary documentation (licence) | Repository copy |
| D13 | Hugging Face, Inference Endpoints pricing: <https://huggingface.co/docs/inference-endpoints/pricing>; configuration: <https://huggingface.co/docs/inference-endpoints/guides/configuration> | None shown | Primary documentation | Billing basis only |
| D14 | AWS, "SageMaker Pricing": <https://aws.amazon.com/sagemaker/ai/pricing/> | None shown | Primary documentation | Instance-based path only |
| D15 | Google Cloud, "Open models overview": <https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/open-models/choose-serving-option>; "Overview of self-deployed models": <https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/model-garden/self-deployed-models> | Self-deployed page last updated 2026-10-15 | Primary documentation | — |
| D16 | Microsoft Learn, "Deployment types for Microsoft Foundry Models": <https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/deployment-types> | Last updated 08/12/2026 | Primary documentation | — |
| D17 | Microsoft Learn, "Provisioned throughput billing and cost management": <https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/provisioned-throughput-billing> | Last updated 05/26/2026 | Primary documentation | Billing basis only |
| D18 | AWS, Bedrock Provisioned Throughput: <https://docs.aws.amazon.com/bedrock/latest/userguide/prov-throughput.html> | None shown | Primary documentation | Billing basis only |
| D19 | OpenAI, "Data controls in the OpenAI platform": <https://developers.openai.com/api/docs/guides/your-data> | None shown | Primary documentation | Varies by endpoint and model |
| D20 | Google, "Gemini API Additional Terms of Service": <https://ai.google.dev/gemini-api/terms> | Last updated 2026-04-28 | Primary documentation (terms) | — |
| D21 | Microsoft Learn, "Data, privacy, and security for Models sold by Azure in Microsoft Foundry": <https://learn.microsoft.com/en-us/azure/foundry/responsible-ai/openai/data-privacy> | Last updated 05/19/2026 | Primary documentation | — |
| D22 | AWS, Bedrock data retention: <https://docs.aws.amazon.com/bedrock/latest/userguide/data-retention.html> | None shown | Primary documentation | Per model |
| D23 | NVIDIA, Nemotron-3.5-Super-VL-120B-A12B-NVFP4: <https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Super-VL-120B-A12B-NVFP4> | Created 2026-10-12 | Primary documentation | Licence metadata: other |
| D24 | Prism ML, Ternary-Bonsai-2-27B-gguf: <https://huggingface.co/prism-ml/Ternary-Bonsai-2-27B-gguf> | Created 2026-09-16; last modified 2026-09-25 | Primary documentation; Vendor claim (quality, speed; not relied on) | Third-party derivative |
| D25 | Mistral AI, Mistral-Medium-3.5-128B-EAGLE: <https://huggingface.co/mistralai/Mistral-Medium-3.5-128B-EAGLE>; NVIDIA, Nemotron-3.5-Bolt-74B-A9B-24GB-LiLiCorr: <https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Bolt-74B-A9B-24GB-LiLiCorr> | Created 2026-04-27 and 2026-10-12 | Primary documentation | Draft models |
| D26 | Mistral AI, Voxtral-Mini-4B-Realtime-2602: <https://huggingface.co/mistralai/Voxtral-Mini-4B-Realtime-2602>; ggml-org GGUF: <https://huggingface.co/ggml-org/Voxtral-Mini-4B-Realtime-2602-GGUF> | Card last modified 2026-03-11; GGUF repository created 2026-10-16 | Primary documentation | No path tested |
| D27 | Arm Learning Paths, "Explore llama.cpp architecture and the inference workflow": <https://learn.arm.com/learning-paths/servers-and-cloud-computing/llama_cpp_streamline/2_llama.cpp_intro/>; parent: <https://learn.arm.com/learning-paths/servers-and-cloud-computing/llama_cpp_streamline/> | Parent page "Last updated: 17 Sep 2026" | Vendor claim | — |
| D28 | NVIDIA Technical Blog, "Mastering LLM Techniques: Inference Optimization": <https://developer.nvidia.com/blog/mastering-llm-techniques-inference-optimization/> | Published 17 Nov 2023; modified 27 Dec 2025 | Vendor claim | GPU-focused |
| D29 | Kim et al., "SqueezeLLM" (ICML 2024): <https://arxiv.org/abs/2306.07629> | arXiv v4 | Independent measurement (author-reported) | GPU; single-batch scope |
| D30 | AMD, EPYC 9755: <https://www.amd.com/en/products/processors/server/epyc/9005-series/amd-epyc-9755.html>; EPYC 9996: <https://www.amd.com/en/products/processors/server/epyc/9006-series/amd-epyc-9996.html>; Intel, Xeon 6980P: <https://www.intel.com/content/www/us/en/products/sku/240777/intel-xeon-6980p-processor-504m-cache-2-00-ghz/specifications.html> | As shown at access | Primary documentation (specifications) | Peak figures |
| D31 | vLLM project, "CPU": <https://docs.vllm.ai/en/latest/getting_started/installation/cpu/>; quantization FAQ: <https://docs.vllm.ai/en/latest/getting_started/installation/cpu/#which-quantization-configs-does-vllm-cpu-support> | Revision date 15 Oct 2026 | Primary documentation | Disagrees with D1 on Arm W8A8; governs as the more specific source with a stated limitation (#41 conflict order, steps 2 and 4) |
| D32 | ggml-org, llama.cpp server README: <https://github.com/ggml-org/llama.cpp/blob/f3363593f457169cdfbdfe22ea399b1cc139ba18/tools/server/README.md> | Commit `f336359` | Primary documentation | — |
| D33 | Intel, "Intel Advanced Matrix Extensions Overview": <https://www.intel.com/content/www/us/en/products/details/processors/xeon/features/advanced-matrix-extensions.html> | No page date confirmed | Vendor claim | No LLM-specific claim |
| D34 | kvcache-ai, KTransformers README: <https://github.com/kvcache-ai/ktransformers/blob/7fbbc20d31265b266a16dd4a3929f2abf76681e6/README.md> | Commit `7fbbc20` | Primary documentation (purpose) | Research project |
| D35 | ggml-org, llama-bench README: <https://github.com/ggml-org/llama.cpp/blob/f3363593f457169cdfbdfe22ea399b1cc139ba18/tools/llama-bench/README.md> | Commit `f336359` | Primary documentation | Kernel throughput; excludes tokenization and sampling |
| D36 | LocalScore: About <https://www.localscore.ai/about>; blog <https://www.localscore.ai/blog>; latest results <https://www.localscore.ai/latest>; CLI <https://github.com/Mozilla-Ocho/llamafile/tree/main/localscore> | Launch post 3 Apr 2025 | Primary documentation | No verification process stated |
| D37 | llama.cpp Discussions: #4167 <https://github.com/ggml-org/llama.cpp/discussions/4167>; #10879 <https://github.com/ggml-org/llama.cpp/discussions/10879>; #15013 <https://github.com/ggml-org/llama.cpp/discussions/15013> | Active in Oct 2026 | Primary documentation (thread instructions) | Version policies differ per thread; curated |
| D38 | LocalMaxxing: home <https://www.localmaxxing.com/en>; privacy policy <https://www.localmaxxing.com/en/privacy> | Privacy policy last updated 4 Oct 2026 | Primary documentation (policy) | Live counters not used |
| D39 | Rapid-MLX, leaderboard: <https://rapidmlx.com/leaderboard> | As shown at access | Primary documentation | Apple Silicon only |
| D40 | MetriLLM: home <https://metrillm.dev/>; methodology <https://metrillm.dev/methodology> | As shown at access | Vendor claim | — |
| D41 | OpenBenchmarking.org, `pts/llama-cpp`: <https://openbenchmarking.org/test/pts/llama-cpp>; Phoronix Test Suite documentation: <https://github.com/phoronix-test-suite/phoronix-test-suite/blob/master/documentation/phoronix-test-suite.md> | Profile `pts/llama-cpp-2.5.0`, added 10 January 2024, updated 25 April 2026 | Primary documentation | — |
| D42 | Geekbench Browser: <https://browser.geekbench.com/>; Geekbench 6 CLI: <https://support.primatelabs.com/kb/geekbench/geekbench-6-command-line-tool>; valid and invalid tags: <https://support.primatelabs.com/kb/geekbench/geekbench-valid-and-invalid-tags> | Tags page updated 23 Jun 2025 | Primary documentation | Geekbench 6 behaviour only; tags concern timers |
| D43 | MLCommons, "MLPerf Client Benchmark": <https://mlcommons.org/benchmarks/client/> | Modified 18 Aug 2026 | Primary documentation | — |
| D44 | PCPartPicker, Completed Builds: <https://pcpartpicker.com/builds/> | As shown at access | Primary documentation (what pages show) | Moderation not verified |
| D45 | Valve, "Steam Hardware & Software Survey": <https://store.steampowered.com/hwsurvey> | September 2026 | Primary documentation | Selection not described |
| D46 | PR #67 competitor register at commit `4a3fa17`: <https://github.com/Pick-Your-AI/pick-your-ai-research/blob/4a3fa17aa22b38c088f224358681817166c1ecb5/research/market/competitors.json> | Commit `4a3fa17`; the file is identical at PR head `6511dea` (checked 2026-10-16) | Primary documentation (project file) | Open PR; may change |
| D47 | IBM, granite-4.2-30b-q4-mlx repository file list: <https://huggingface.co/ibm-granite/granite-4.2-30b-q4-mlx/tree/main> | As shown at access | Primary documentation | Shows `.safetensors` weight files |
| D48 | Mistral AI, Mistral-Medium-3.5-128B licence ("Modified MIT License"): <https://huggingface.co/mistralai/Mistral-Medium-3.5-128B/raw/main/LICENSE> | Accessed 2026-10-17 | Primary documentation (licence text) | Revenue condition applies to the model and its derivatives; not legal advice |
