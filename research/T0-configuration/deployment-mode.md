# T0: Deployment Mode

Issue: #3 · Contract: v1 1.0.0 (adopted in PR #44; inspected at `a222013`) · Kinds: `deployment_mode`
Status: draft, revision 4 (after three internal reviews) · Last researched: 2026-10-16
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
  - One eligibility predicate (EV-1) decides whether evidence may be used, with checks specific to each type of evidence. Eligible results that disagree leave the value unresolved.
  - A newer release alone never invalidates a record.
- **CPU-only and mixed CPU+GPU builds are in scope.** For single-batch generation, memory bandwidth is reported as a main bottleneck (D27–D29), so bandwidth, instruction sets and offload support are key inputs. Measured fit records, not this note, decide how far that holds for a given machine.
- **Crowdsourced fit reports are a possible additional evidence source.** Several community databases already exist (D36–D41). Agreement between reports is shown, but doesn't decide compatibility until #41 defines an acceptance policy (CD-8).
- **Self-hosting enables local inference, but doesn't by itself keep data local.** Residency is checked over the build's data flows, including external destinations (D-R6).
- **Open contract decisions.** Ten are recorded for #40 and #41 rather than solved here (CD-1 to CD-10).

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
- the engine: ID, version, fork or commit, and launch options that affect memory or speed (threads, batch limits, KV cache precision, parallelism);
- the decoding method and draft artifact;
- the devices: model, memory capacity and configuration (including channel population and NUMA layout), instruction-set features, driver;
- the placement;
- the OS;
- the workload distribution: input and output lengths, concurrency and arrival process;
- the cache state (warm or cold).

Which fields are essential for comparison and which are display-only is decided in CD-3.

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
| Estimate | v1 resource estimates; memory calculated from artifact size, context and concurrency; figures labelled estimated in a fit record | W-R6 | Its inputs (artifact, engine build, placement, lengths, concurrency) equal the build's selection and workload, its method and version are recorded, and its v1 confidence (`estimated`, `calibrated` or `verified`) meets the build's `min_resource_confidence` (C5, C9). Estimates are not used for latency or throughput targets, which need `service_level` measurements. Estimated figures in community reports stay informative, like the rest of the report (CD-8). |
| Support documentation | Engine support matrices, instruction-set requirements, a draft model's stated target and hardware | D-R3, D-R7a, D-R7b, D-R8 | It is primary documentation from the publisher of the engine, artifact or hardware, and the selection falls within the coverage it declares, such as an engine version, hardware generation or platform. |
| Legal and provider documents | Licences, model cards stating weight access, terms of service, data-handling pages, region lists | D-R1, D-R2a, D-R2b, D-R5, D-R6 | It is primary documentation from the licensor or provider, and it matches the selected offering, its version or effective date, the jurisdiction, and any account conditions it states (for example paid or unpaid use, or approval for zero retention). |

**Transfers between workloads.** A performance figure carried over from a different workload distribution, for example by a transfer model, is a derived estimate, not a measurement of the build's configuration. Until CD-3 defines how such estimates are assessed, they are not eligible, and W-R7 gives `unknown`.

**Conflicting evidence.** Eligible evidence can disagree about a rule's verdict: one measurement or estimate meets a target while another misses it, or one primary document lists a combination as supported while another doesn't. The value is then unresolved, so the outcome is `unknown`, until CD-3 and #41's acceptance policy define how results are selected or aggregated. A rule never passes on one eligible result while ignoring another.

Ineligible evidence is shown but leaves the dependent value unresolved, so the rule's outcome is `unknown`. Eligibility is recomputed whenever any of these change: the selection, the evidence's status, the policy, or the date. A newer engine release alone changes nothing; it is shown separately as "newer build available".

### CPU-only and hybrid CPU+GPU self-hosting (Proposal)

Many people already own capacity without a GPU. #10 asks "Is CPU or edge inference in scope?". This note answers yes from the configuration side; #10 owns sizing.

| Factor | Evidence |
| --- | --- |
| **Decode is described as memory-bound** | Arm's llama.cpp guide says "the Decode stage is memory-bound" (D27, Vendor claim). NVIDIA describes decode the same way for GPUs (D28, Vendor claim). SqueezeLLM reports memory bandwidth as "the main bottleneck … specifically for single batch inference" (D29). Batching, caching, sparse activation, speculative decoding and placement change the picture; fit records show how far it holds for a given machine. |
| **Server CPUs differ widely in bandwidth** | Vendor peak figures per socket: AMD EPYC 9755, 12 channels and 614 GB/s; AMD EPYC 9996, 16 channels and 1024 GB/s with DDR5 RDIMMs or 1638 GB/s with MRDIMMs. Intel lists the Xeon 6980P with 12 channels and DDR5-6400 or MRDIMM-8800, without a bandwidth figure (D30). These are peak specifications, not inference measurements. |
| **Instruction sets gate engines** | vLLM's CPU backend recommends `avx512f` on x86 and gives `avx2` "limited features". It requires NEON on Arm, marks Apple silicon and IBM Z as experimental, and recommends tensor parallelism equal to the number of NUMA nodes (D31). llama.cpp lists "AVX, AVX2, AVX512 and AMX support for x86 architectures" and Arm NEON (D3). Intel says AMX improves inference "with no additional hardware" (D33, Vendor claim). |
| **Quantization support differs on CPUs** | In vLLM's quantization chart (D1), AWQ and GPTQ are supported on x86 CPUs but not Arm CPUs. llm-compressor INT8 (W8A8) is marked as supported on both, INT8 (W4A8) only on Arm, and GGUF on neither. vLLM's CPU page lists AWQ and GPTQ for "x86, s390x, Power", and compressed-tensor INT8 W8A8 for "x86, s390x only" (D31). The two pages therefore disagree on Arm W8A8, or differ in scope without saying so. Neither was tested here. Until #11 or #41 reconciles them for a pinned vLLM version, Arm W8A8 stays unresolved for automatic checks (D-R3 gives `unknown`). llama.cpp runs GGUF on CPUs (D3). |
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

**Display:** show the spread (median, range, number of reports) and the grade, never a single universal "works". Showing the spread doesn't decide a verdict: eligible results that disagree leave it unresolved (EV-1). Under EV-1, community grades are informative until #41's acceptance policy says otherwise.

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
| `engine_build` | engine selection | `{version: string, fork_repo: URL, commit: string, launch_options: object}` | `fork_repo` and `commit` required for forks | D4, D5, D24 | Engine item version |
| `artifact_format` | artifact | Serialization: `gguf`, `safetensors`, `onnx`, `pytorch`, `other` | — | Repository files | `model_formats` (C1) |
| `package_convention` | artifact | `mlx`, `transformers`, `other`, `none` | Separate from serialization: IBM's MLX repository holds safetensors files (D47) | Repository files | — |
| `quantization` | artifact | `{method: open vocabulary, logical_bits_per_weight: decimal, stored_bits_per_weight: decimal, packing: string}` | bits > 0 | Artifact card (D10, D23, D24) | Fixed enum without bits (C2) |
| `components` | artifact | list of `{role: language_model \| vision \| draft \| other, size_gb: decimal > 0, required: boolean}` | — | D24 | — |
| `license_conditions` | model catalog | list of `{condition_id, text, source, kind: eligibility \| obligation, question}` | — | Licence text (D12) | `license` booleans and SPDX ID; opaque `license_ref` (C1) |
| `licence_answers` | build | list of `{model_selection_id, condition_id, answer, grant_ref}`. The allowed `answer` values depend on the condition's `kind`: `met`, `not_met` or `unknown` for `eligibility`; `acknowledged`, `not_acknowledged` or `unknown` for `obligation` | `grant_ref` only for `eligibility`; `unknown` is an answer state (CD-1) | User input | — (location: CD-6) |
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
| Fine-tuned adapters | Inherit the base model's deployment. The engine must support adapters (#11). | Same | Provider-hosted fine-tuning per #30 |
| Retrieval backend (`vector_database`) | Host with location: R. Devices: R (a CPU is fine). Inference engine: H. Runtime requirements: CD-10. | Service with location: R | Service with location when residency is constrained |
| Storage | Per #9 | Per #9 | Per #9 |
| Tools, MCP servers | `external_connections`: R | Same | Same |
| Optional tiers (T3–T5) | Present when selected; selection-authoritative (companion note) | Same | Same |
| Operations | O; production requirements per #35–#39 | O | O |

v1 today: when the build mode is `self_hosted`, `rule.selfhost.requires.infrastructure` requires a hosting platform, accelerator, compute profile and inference engine for the whole build (C3).

## Compatibility proposals

All rules are hypotheses for #40 review.
- Each rule has one fixed severity, as the ruleset schema requires (C10).
- A known violation is `fail`. Ineligible, missing or conflicting evidence leaves the dependent value unresolved, so the outcome is `unknown`.
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

- **Roles and pointers:** model `/license_conditions` where `kind` is `eligibility`; build `/licence_answers`.
- **Applies when:** a component that D-R1 applies to has at least one condition of kind `eligibility`.
- **Assertion:** every eligibility condition is answered `met`, or a grant is recorded.
- **Example condition** (Llama 3.1, D12): "If, on the Llama 3.1 version release date, the monthly active users of the products or services made available by or for Licensee, or Licensee's affiliates, is greater than 700 million monthly active users in the preceding calendar month, you must request a license from Meta". The release date is 23 July 2024. The question therefore covers the licensee and its affiliates, for the calendar month before that date.
- **Missing data:** `unknown`.
- **Remediation:** answer the condition, record a grant, or choose another model.
- **Dependencies:** #5, #6; where licence answers live is CD-6.
- **Examples:**
  - Pass: answered `met`.
  - Fail: answered `not_met`, with no grant.
  - Unknown: unanswered.
  - Skipped: no conditions recorded.

### D-R2b Licence obligations are acknowledged

- **Roles and pointers:** model `/license_conditions` where `kind` is `obligation`, such as Llama 3.1's incorporated acceptable use policy (D12); build `/licence_answers`.
- **Applies when:** a component that D-R1 applies to has at least one condition of kind `obligation`. This is D-R2a's scope, for obligations instead of eligibility conditions.
- **Assertion:** every obligation is answered `acknowledged`.
- **Missing data:** `unknown`.
- **Remediation:** acknowledge the obligation, or choose another model.
- **Dependencies:** as D-R2a.
- **Examples:**
  - Pass: answered `acknowledged`.
  - Fail: answered `not_acknowledged`.
  - Unknown: no answer.
  - Skipped: no obligations recorded.

### D-R3 Quantization supported by the engine build on this hardware

- **Roles and pointers:**
  - artifact `/quantization`;
  - the `engine_build` linked through `served_by`;
  - the devices' generation or backend;
  - eligible support documentation (EV-1; matrix format: CD-3).
- **Applies when:** a self-hosted model uses a quantized artifact.
- **Assertion:** eligible support documentation lists the combination as supported, and none lists it as unsupported.
- **Missing data:** `unknown`, including when eligible documents disagree. A known "unsupported" entry, with no eligible document saying otherwise, is `fail`.
- **Remediation:** choose a supported quantization, engine build or device.
- **Dependencies:** #11, #10. v1 checks precision against the engine and against the accelerator separately (C3).
- **Examples** (from D1):
  - Pass: AWQ with vLLM on an Ampere GPU.
  - Fail: AWQ with vLLM on an AMD GPU.
  - Unknown: no entry for a new method.
  - Unknown: W8A8 with vLLM on an Arm CPU, where vLLM's two pages disagree (D1, D31).
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
  - Unknown: a telemetry destination with no locations.
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
| CD-3 | Protocol identity, the canonical configuration key (essential vs display fields), protocol compatibility, result schemas for `kernel_throughput` vs `service_level`, coverage matching for support documentation, how derived estimates are assessed, and how conflicting eligible results are selected or aggregated | EV-1, reports, W-R7 | #41 (with #10, #62) |
| CD-4 | The isolation-boundary model: endpoint membership, connection lifecycle and state, and artifact readiness manifests | W-R8 | #40 |
| CD-5 | Per-stage load and length records for pipelines | Workload note | #40 (with #10) |
| CD-6 | Relationship details: the draft-to-target link, where `licence_answers` live, mapping the hardware inventory to device selections, roles that disambiguate multiple links, whether an adapter's `derived_from` link must match its `base_model_ref`, and the effective serving capabilities of fine-tuned models and adapter/base compositions | Bindings, D-R1, D-R2, D-R8, W-R1 | #40 (with #6, #33) |
| CD-7 | The migration strategy: what is additive vs replacement, the treatment of the three workload copies, adapters and deprecation, how legacy build-level mode is interpreted, and the contract version | All rules | #40 |
| CD-8 | Reporter and execution independence, and the acceptance policy that would let community evidence decide verdicts | Trust grades | #41 |
| CD-9 | The jurisdiction hierarchy, containment, named groups, and mapping provider regions to jurisdictions | D-R5, D-R6 | #41 (with #9) |
| CD-10 | Runtime requirements for non-model services such as vector databases | D-R7a, matrix | #40 (with #11, #15) |

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
3. **Keep fit records immutable while retained,** with mode-appropriate keys, and use one eligibility predicate (EV-1), with checks by evidence type, wherever evidence is consumed. Eligible evidence that disagrees leaves the value unresolved.
4. **Treat CPU-only and hybrid CPU+GPU builds as first-class,** adding bandwidth (in GB/s), instruction sets, NUMA nodes, memory kind and typed placement.
5. **Adopt crowdsourced reports as informative evidence,** with two protocol types, trust grades, facilitation, incentives (as hypotheses), integrity checks and privacy rules. Let #41 decide when they may decide verdicts (CD-8). Ask #48 and #57 to assess the existing projects, and #41 and #60 whether their data can be linked.
6. **Take CD-1 to CD-10 to #40 and #41,** alongside D-R1 to D-R8.
7. **Store deployment mode on the build and its selections, not as catalog items.** In v1 it is a catalog kind (C6) needing provenance with a public URL (C7).

## Structured artifacts

None (Recommendation 7).

## Open questions and handoffs

Each question has one accountable issue (its assignee is the owner); others are consulted. Contract design questions are listed separately as CDs. Q8 and Q9 point to issues that had no assignee set when checked on 2026-10-16; their owners are to be confirmed in owner review.

| # | Question | Accountable | Consulted |
| --- | --- | --- | --- |
| Q1 | Who maintains fit records and support matrices? | #41 | #10, #11 |
| Q2 | How should unified memory, CPU-only devices and CPU+GPU placement be sized? | #10 | #40 |
| Q3 | For each managed platform, can the customer choose or supply the runtime? | #9 | #11 |
| Q4 | Which `data_terms` fields are mandatory before an API or managed component is shown? | #5 | #9, #41 |
| Q5 | Does a fit record carry quality impact, or only memory and speed? | #36 | #11 |
| Q6 | Where do fit reports live, and under what licence? | #41 | #40 |
| Q7 | Should existing community datasets (D36–D41) be linked or imported, and do their terms allow it? | #41 | #60 |
| Q8 | Do the proposed incentives work? | #52 (no assignee set) | — |
| Q9 | How do the existing community projects change the differentiation case? | #48 (no assignee set) | #57 |
| Q10 | How are hybrid builds saved, shared and compared? | #42 | — |
| Q11 | What remains after a report or its attribution is deleted (nothing, a tombstone, or aggregate statistics), and how long are reports and raw logs kept? | #41 | #60 |

Handoffs to confirm (none confirmed yet): #5, #6, #9, #10, #11, #33, #36, #37, #39, #40, #41, #42, #48, #52, #57, #60, #62.

## Acceptance criteria coverage

| Criterion (issue #3) | Where | Status |
| --- | --- | --- |
| Definitions and a boundary example per pair | [Definitions](#definitions-proposal) | Reviewer: met |
| Mode × component matrix | [Component requirements](#component-requirements-by-function-and-mode-proposal) | Revised: fine-tuned access-mode field corrected in D-R1; D-R7a scoped to model engines |
| Per-build vs per-component decision | [Per-component mode](#per-component-mode-and-relationships-decision-proposal) | Reviewer: met; v1 links claim corrected |
| Comparison fields | [Field dictionary](#field-dictionary), [EV-1](#evidence-eligibility-ev-1) | Revised: licence answers typed by condition kind; evidence checked by type; remaining items recorded as CDs |
| Rules in the shared format; hypotheses separated | [Compatibility proposals](#compatibility-proposals) | Revised: common template fields; split rules state their scope; evidence moved to EV-1 |
| Primary sources with access dates | [Evidence](#evidence) | Revised: contract cited as adopted; vLLM CPU documentation conflict recorded |
| Handoffs confirmed | [Open questions](#open-questions-and-handoffs) | Open |
| Open questions with owners | [Open questions](#open-questions-and-handoffs) | Partly met: Q8 and Q9 point to issues with no assignee set |
| Decision record merged | — | Open |

## Evidence

All sources were accessed on 2026-10-16. Vendor terms change often; re-check them before relying on this note. Relative "updated" labels are not used as versions.

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
| D1 | vLLM project, "Quantization": <https://docs.vllm.ai/en/latest/features/quantization/> | "Last update: September 14, 2026" | Primary documentation | vLLM only; "subject to change"; disagrees with D31 on Arm W8A8 |
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
| D31 | vLLM project, "CPU": <https://docs.vllm.ai/en/latest/getting_started/installation/cpu/>; quantization FAQ: <https://docs.vllm.ai/en/latest/getting_started/installation/cpu/#which-quantization-configs-does-vllm-cpu-support> | Revision date 15 Oct 2026 | Primary documentation | Disagrees with D1 on Arm W8A8 |
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
