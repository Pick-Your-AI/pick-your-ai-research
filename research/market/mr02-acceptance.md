# MR-02 acceptance and evidence audit

## Current documentary review — 2026-10-18

This amendment reviews the accepted **33-entity, 48-dimension** matrix as documentary research. Its input is signed main `774a3cca38dcb7c90af9db31ff1619e7fe91becb`, with matrix `00dbb8d94488ad73bae58d5ee934520e95b4862f`, guide `c8c558c392f742bb04fe2b55bd8fd3f68751c1cf` and prior audit `bcaebf4fd30df66be46bc437cfaafadd7b70603a`. Those three inputs are unchanged from accepted `aeb9f35f5113297db44b230f59a8cdf778379a24`, the basis of the in-session native receiving reviews below. The later sections are preserved as their original dated records; historical pending statements do not override this separately scoped current review.

The in-session research engineer read all 48 definitions/scenarios and the 122 incoming Documented claim records, opened their 42 distinct primary URLs, and inspected the relevant published fields, methods and limitations. Targeted follow-ups distinguish a returned explanation from ranking inputs and reconcile the later Flocci observation and Flowise lifecycle notice. This is a public-document source pass, not an execution of 1,584 product tests or independent replication of vendor claims. A sandboxed direct JSON transport attempt was unavailable; no successful direct transport, hash verification or raw dataset import is claimed from it. The readable publisher dataset page and web JSON representation retain their documentary scope.

### Current classifications and preserved observations

| Item | Reviewed disposition | Consequence |
| --- | --- | --- |
| Artificial Analysis `explanation` | Documented → Unknown. The original basis advertises recommender priorities; the inspected homepage/recommender material does not establish a returned reason | Retain the original URL, date, basis, method, grade, confidence and audit scope; change only status and limitation. A rationale field, described explanation UI or worked result could support a later P; absence of capability is not inferred |
| ModelFit `explanation` | Documented remains Documented, using a newly inspected, exact published result instead of the insufficient homepage-factor basis | The [published result](https://modelfit.io/can-i-run/gpt-oss-20b-on-rtx-4060-ti/) ties a model/GPU verdict to weights versus usable memory and gives workload reasons. The page also contains inconsistent fit/context statements. Its estimates, feasibility and thresholds are not accepted as correct |
| Complete matrix | 1,584 cells: **121 Documented, 1,463 Unknown, zero Exercised, zero Unsupported** | Exactly two cells receive the changes above; all 1,582 other cell objects, all 48 definitions/tests and the original audit-scope object remain unchanged. The new ModelFit record alone adds a current source scope |
| Original #42 requested subset | 13 original profiles × four dimensions = 52 cells, **26 Documented / 26 Unknown** | Every guide mark agrees with JSON; these two explanation changes affect none of the 52 cells |
| CanIRun.ai | Two Documented / 46 Unknown, unchanged from the delivered memory correction | The separate hardware-capacity observation remains intact. No new requirement or execution is supplied |

The ModelFit update records an access date of 2026-10-18 and the page's stated October 14 publication revision; it does not refresh any other claim. Its prior complete record is retained here so the former source, wording and date remain explicit:

```json
{
  "product_id": "modelfit",
  "feature": "explanation",
  "status": "Documented",
  "evidence_ids": [
    "src-modelfit"
  ],
  "basis": "Site describes hardware-fit recommendations with speed/quality estimates; rationale output was not exercised.",
  "verification_method": "Primary page read 2026-10-16; documentation/claim inspection only; bounded execution test not performed.",
  "access_date": "2026-10-16",
  "evidence_grade": "Vendor claim",
  "evidence_url": "https://modelfit.io/",
  "confidence": "Medium for the stated documentary boundary; execution unverified",
  "limitations": "P records only the basis above; it does not pass the full capability test or certify compatibility, performance, persistence, price accuracy or rights.",
  "audit_scope": "public-docs-2026-10-16"
}
```

No competitor is added or removed. The six staged community resources and their possible 288 cells remain a separate future intake under the [accepted #48 working-scope decision](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/48#issuecomment-6249724402). They are not missing rows from this accepted 33-entity denominator. Source-register IDs, rights decisions, integration exclusions and all frozen contracts remain unchanged.

### Source-to-claim review and material limits

The following table covers all **43 current claim URLs** after the more precise ModelFit explanation source is added. Dimension IDs map directly to the corresponding cell records and their existing publishers/source IDs. The review date for this table is **2026-10-18**; original claim access dates and evidence classes remain those in JSON except for the explicitly replaced ModelFit record. Vendor statements remain vendor statements, even when checked against the publisher's page. API/catalog data, a benchmark publication and a model run are different artifacts.

The common method is unauthenticated primary-page/documentation text inspection. Product versions are the dated public surfaces unless a particular version is named; plan entitlements, regional availability, source-price accuracy and runtime execution remain unverified. Numeric prices, model scores, speed figures, product catalog counts and fit estimates in these pages are not adopted as project measurements or rates. This table contains original analytical paraphrases and links; it supplies no permission to redistribute datasets, screenshots or publisher text and changes none of the accepted #41/#60 material/use decisions. The GPUs.io product exclusion remains literal false for retrieval, display and redistribution in the existing integration record.

| Product | Current Documented dimensions | Inspected source | Exact documentary support and remaining limit |
| --- | --- | --- | --- |
| benchlm | `model_search`, `model_compare`, `explanation`, `model_versions`, `benchmarks`, `api_pricing`, `share`, `export` | [Primary source](https://benchlm.ai/) | Published filters, comparison fields, confidence labels, named releases, price surfaces, filter-state URLs and CSV/API descriptions. No personalized rationale, benchmark replication, exact serving pin or bill is proved. |
| benchlm | `api_access` | [Primary source](https://benchlm.ai/data/access) | REST/MCP access and authentication are documented. No authenticated request, paid-plan entitlement or MCP exchange was performed. |
| harness-bench | `benchmarks`, `harness_eval` | [Primary source](https://www.harness-bench.ai/) | Named model-harness/task pairings and scoring-oracle methodology are published. No task execution or score replication. |
| llmfit | `model_search`, `model_compare`, `hardware_fit`, `explanation`, `cpu`, `quantization`, `context`, `inference_engine`, `multi_gpu`, `saved`, `share`, `export`, `api_access` | [Primary source](https://github.com/AlexsJones/llmfit) | README documents selectors, hardware/runtime assumptions, info/estimate output, JSON/API interfaces and saved benchmark sharing. No complete BuildSnapshot restore, measured fit or universal multi-GPU support. |
| local-ai-planner | `hardware_fit`, `constraints`, `explanation`, `cpu`, `quantization`, `context`, `kv_cache`, `inference_engine`, `multi_gpu` | [Primary source](https://logarithmicspirals.com/tools/local-ai-vram-calculator-gpu-planner/) | Published selectors, reason section and memory/KV assumptions support the named boundaries. Missing model context metadata and identical-GPU multiplication remain explicit limitations. |
| flocci | `natural_language` | [Primary source](https://aitools.flocci.in/ask) | Natural-language request surface is described. Generated answers are distinct from performing their proposed work. |
| flocci | `guided_selection` | [Primary source](https://aitools.flocci.in/stack) | Ordered tool/workflow advice is described. Neither a compatible selected stack nor execution follows. |
| flocci | `model_search`, `saved` | [Primary source](https://aitools.flocci.in/) | Catalog and guest bookmark descriptions remain documentary; later #66 observation has its own reviewed capture and guest-path limits. |
| artificial-analysis | `model_compare`, `model_versions`, `benchmarks` | [Primary source](https://artificialanalysis.ai/) | Comparison fields, named releases and published benchmark composition remain documentary. Advertised recommender priorities do not establish returned explanations. |
| artificial-analysis | `api_pricing`, `export`, `api_access` | [Primary source](https://artificialanalysis.ai/api-reference) | Structured model endpoint, key requirement and token-price fields are documented. No API execution, immutable serving revision or supplier-price qualification. |
| openrouter | `model_search`, `model_compare`, `model_versions`, `context`, `hosting`, `tool_calling`, `api_pricing`, `export`, `api_access` | [Primary source](https://openrouter.ai/docs/guides/overview/models) | Model/provider identity, context, supported-parameter and pricing fields document the catalog/API surface. Provider overrides and shared input/output context remain distinct; flags do not prove a tool exchange. |
| hugging-face | `model_search`, `model_compare` | [Primary source](https://huggingface.co/models) | Task/library/name filters and model repository entries support discovery/comparison. Repository information is not an exercised model or serving identity. |
| hugging-face | `model_versions`, `export` | [Primary source](https://huggingface.co/docs/hub/repositories-getting-started) | Git history, commits and repository transfer are documented. A repository export is not a saved complete user configuration. |
| arena | `model_compare`, `benchmarks` | [Primary source](https://arena.ai/leaderboard) | Named model/system comparisons and category rankings are published. No result is replicated or used as an eligible quality ranking here. |
| llm-stats | `model_compare`, `benchmarks`, `api_pricing` | [Primary source](https://llm-stats.com/) | Published model comparisons, benchmark fields and price fields support documentary coverage only. |
| models-dev | `model_search`, `model_compare`, `model_versions`, `context`, `api_pricing`, `export`, `api_access` | [Primary source](https://models.dev/) | Catalog search/comparison, release/context/price fields and JSON/SDK data access are published. An offline catalog snapshot is not an immutable serving pin or a qualified rate. |
| canrun | `hardware_fit` | [Primary source](https://canrunllm.com/) | Hardware-conditioned model-fit estimates are described with assumptions. No model/device accuracy or feasibility measurement. |
| canitrun | `hardware_fit` | [Primary source](https://canitrun.dev/) | Model-fit tables state cache/overhead assumptions. Their numerical estimates were not reproduced or adopted. |
| modelfit | `model_search`, `hardware_fit`, `mcp` | [Primary source](https://modelfit.io/) | Hardware/name intake, local-fit estimates and MCP/CLI access are described. General factors alone do not establish a returned reason. |
| modelfit | `explanation` | [Primary source](https://modelfit.io/can-i-run/gpt-oss-20b-on-rtx-4060-ti/) | A published model/GPU result contains reasons. Its internal fit/context inconsistency is retained; no sizing correctness or execution is accepted. |
| modelfit | `model_versions`, `quantization`, `export`, `api_access` | [Primary source](https://modelfit.io/api/dataset/) | JSON endpoint and publisher-linked dataset describe named variants and quantization records. The separately read data page exposes those columns; immutable weights and runtime compatibility remain unverified. |
| ollama | `model_search` | [Primary source](https://ollama.com/library) | Named model library entries support discovery. No model was downloaded or run. |
| ollama | `inference_engine` | [Primary source](https://docs.ollama.com/quickstart) | The documented local run procedure names a model. No runtime/model pairing was exercised. |
| gpus-io | `hosting_pricing` | [Primary source](https://gpus.io/) | Per-GPU/time rental fields and offering filters are published. No regional quote or price truth is certified; the adopted product-use exclusion remains in force. |
| vast | `hosting`, `hosting_pricing` | [Primary source](https://vast.ai/) | Compute hosting and rental/filter surfaces are described. No instance, market quote, availability or billing result was obtained. |
| runpod | `hosting`, `deployment`, `hosting_pricing` | [Primary source](https://www.runpod.io/) | Pods/Serverless deployment and compute-price surfaces are described. No deployment, workload bill or offering-specific fit is established. |
| dify | `rag`, `agents`, `deployment` | [Primary source](https://dify.ai/) | Agent/RAG construction and cloud/self-hosted offerings are described. No workflow or retrieval answer was executed. |
| dify | `saved`, `share`, `export` | [Primary source](https://docs.dify.ai/en/cloud/use-dify/workspace/app-management) | DSL import/export and retained configuration are documented. Knowledge data and tool keys are excluded; secret environment variables can be included. No reconstruction or sanitization was tested. |
| langflow | `rag`, `agents` | [Primary source](https://www.langflow.org/) | Agent and RAG construction are described. No configured flow, retrieval quality or tool execution is established. |
| flowise | `agents` | [Primary source](https://flowiseai.com/) | Visual agent construction remains a documented claim. The separate wind-down notice prevents inferring continuing support or hosted availability. |
| n8n | `agents`, `deployment` | [Primary source](https://n8n.io/) | Agent workflows and Docker/on-premises/managed deployment are described. No deployment or workflow execution. |
| n8n | `saved`, `share`, `export` | [Primary source](https://docs.n8n.io/build/manage-workflows/export-and-import.md) | JSON save/download/clipboard/file/URL transfer is documented; credential names/IDs and imported authentication headers require care. No second-workspace recovery or sanitization was exercised. |
| skypilot | `deployment`, `saved`, `share`, `export` | [Primary source](https://docs.skypilot.ai/en/latest/reference/yaml-spec.html) | Named task YAML and resource/cloud/region fields are documented. Reusable task configuration is distinct from SkyPilot supplying the rented compute. |
| bentoml | `hosting`, `deployment` | [Primary source](https://www.bentoml.com/) | Model packaging/deployment, own-cloud operation and GPU hosting are described. No deployment, hosting availability or performance test. |
| langfuse | `evaluation`, `monitoring` | [Primary source](https://langfuse.com/) | Trace/cost/latency surfaces and evaluation/experiment methods are described. No trace from our own application or evaluation run. |
| ragas | `rag`, `evaluation` | [Primary source](https://docs.ragas.io/en/stable/) | Application/RAG evaluation, datasets and named metrics are documented. Retrieval evaluation is distinct from constructing a retrieval backend or executing a score. |
| llamaindex | `rag`, `agents` | [Primary source](https://www.llamaindex.ai/) | Document retrieval/indexing and agent workflows are described. No retrieval-quality, permission-enforcement or agent-run result. |
| langchain | `agents` | [Primary source](https://www.langchain.com/) | Agent construction with model/context choices is described. No specific configured model/tool tuple was exercised. |
| qdrant-bench | `benchmarks` | [Primary source](https://qdrant.tech/benchmarks/) | Published vector-search results identify methods, datasets and precision/latency tradeoffs. Publication is not our benchmark replication or universal system comparison. |
| lm-eval | `benchmarks` | [Primary source](https://github.com/EleutherAI/lm-evaluation-harness) | Model benchmark tasks and execution procedures are published. They do not establish the stronger application-evaluation cell. |
| mcp-registry | `mcp`, `api_access` | [Primary source](https://github.com/modelcontextprotocol/registry) | Registry discovery and its API are documented. No client/server transport, auth, trust or tool-execution qualification follows from a server record. |
| unsloth | `inference_engine`, `fine_tuning` | [Primary source](https://unsloth.ai/) | Local inference and training are vendor-described. No inference or training job, permitted dataset or deployable fine-tuned artifact is established. |
| canirun-ai | `hardware_fit`, `hardware_catalog` | [Primary source](https://www.canirun.ai/devices) | Device entries and model-recommendation links support hardware discovery/fit-documentation boundaries. Available capacity does not establish a model/runtime memory requirement. |

The [ModelFit data page](https://modelfit.io/data/) explicitly describes and displays the named variant/quantization columns behind its linked JSON distribution; no immutable model-file identity is inferred. The [Flowise notice](https://flowiseai.com/sunset) separately announces a code freeze, archival and end of core-team support. That does not erase its historical construction description, and this review does not verify a currently operating cloud service or endorse its maintenance status. Neither follow-up adds another product or promotes a capability to Exercised.

### Taxonomy, overlap and conclusion boundaries

The 48 existing IDs form a complete working comparison vocabulary. Each has one bounded scenario, an observable, required version/plan/access/input/output conditions and an explicit missing-evidence policy. Compound labels are received only with their named branch and artifact: RAG construction versus retrieval evaluation; MCP registry record versus tool exchange; catalog/benchmark data versus reusable configuration. The guide now makes the same distinction explicit for `harness_eval` and `evaluation`: reading a procedure or published score is documentary P, while a future executed evaluation must identify its actual run. A `benchmarks` retrieval test would establish retrieval only. No dimension IDs or frozen fields change.

Likewise, `tco` permits stated exclusions in its bounded comparison test; its label does not certify complete priced coverage. Unknown costs remain not priced/not sized. Explanation requires a reason tied to a choice/input or compared field, rather than merely listing ranking priorities. These interpretations preserve the original tests while limiting the conclusions available from them.

Documented comparison/context fields, conditional hardware planners, configurable workflows and data/configuration transfer are concrete overlap. Their precise cell bases and primary links support those findings. The matrix has no Unsupported cells and establishes no empty market, unique feature advantage, complete feasible stack, demonstrated customer demand or measured willingness to pay. The 33 × 48 inventory is a documentary denominator, not a product ranking or statistical sample of the market. Versioned decision-record differentiation and the value of a combined workflow remain hypotheses received under the existing #57/#58 rules, not conclusions drawn from Unknown.

The original #42 subset distinguishes BenchLM filter views/CSV, llmfit benchmark/recommendation outputs, Flocci tool bookmarks, API/catalog JSON, repository revisions, Dify/n8n workflow formats and SkyPilot task YAML. None can be substituted for a complete BuildSnapshot simply because it is called saved, shared or exported. A model name, release date or alias is not an immutable serving revision.

### Later accepted Flocci observation

The [actual #66 receiving review 6248861238](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/66#issuecomment-6248861238), submitted through CompleteDotTech at `2026-10-18T10:40:31Z`, reviewed note blob `fbaff0a01df683fd7444769118d18ba0f2d5a473`, the 10,424-byte original capture and two screenshots with independent length/hash checks. This amendment read that receipt and the accepted scope; it did not rerun the product, reinspect the capture files or convert that other reviewer's execution into its own.

Its accepted #2/#40/#42 dispositions distinguish original hard requirements from proposed relaxations, a displayed contradiction explanation from whole-stack feasibility, and a guest tool bookmark from a reusable configuration. That tested guest path produced no reusable stack. It does not establish absence of export or persistence in untested tiers. The older audit's unavailable-capture and rerun statements below remain historical; the current guide now points to this later accepted observation. No Flocci grade is promoted and that same guest test need not be repeated to receive this documentary matrix.

### Current technical intake and remaining decisions

These decisions are offered and recorded under the user's delegated project engineering mandate, with actual in-session roles identified separately from live assignees. They do not impersonate absent co-owners, grant publisher permission or complete a consumer's own implementation/research criteria. The canonical #59 ledger retains its original 101 ordered mappings and 02:50:05Z snapshot; later actual receipts are separate records, not changes to its historical 44/55/2 counts.

| Consumer | Actual current scope / retained receipt | Remaining boundary |
| --- | --- | --- |
| #6 / #7 | Original author-integration receipt remains historical. [Actual root receipt 6251641610](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/49#issuecomment-6251641610) accepts model/limit discovery and field/test vocabulary with narrowing on `fcc29c51` / `25bfa13b2d8b38dc15e811e7f8528ec55b4c8071` | No model catalog identity, immutable serving pin, licensed weight access, enforced context/output limit, tokenizer, KV default or compatibility rule follows from these cells |
| #10 | [Actual root receipt 6251641610](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/49#issuecomment-6251641610) accepts conditional compute discovery and test design against the accepted sizing method, preserving completed #10 and separate empirical #61 scope | Hardware capacity, a fit estimate and calibrated model/runtime demand remain distinct; no ResourceEstimate or device feasibility is supplied |
| #16 | [Actual root receipt 6251641610](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/49#issuecomment-6251641610) accepts the three construction pointers and one separately identified Ragas evaluation pointer with narrowing | No backend choice, retrieval quality, permission enforcement, citation correctness or context-budget agreement is supplied |
| #25 / #27 | [Actual T4 review 6248122696](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/59#issuecomment-6248122696) at `2026-10-18T09:15:34Z` accepts documentary discovery and bounded test design on the five T4 tests. Its nine Documented / 156 Unknown cells are unchanged by this amendment | Retain exact original reviewed revisions `9192d5d6` / `f0387630` and matrix blob `a5e6a088`; no server/client protocol, transport, auth, trust or executed model/tool tuple is certified |
| #30, separately dated informational intake | Actual in-session Apple technical review on accepted `aeb9f35f`: **accept with narrowing** the sole Unsloth training P as a discovery lead and the existing test as a future configuration-test definition. It read the exact 165-cell T5 slice and accepted #30 field/permission/channel/handoff sections, blob `236f72a8` | No pinned framework/model/method/backend tuple, training/weight rights, dataset compatibility, job, export path, lifecycle availability or price. Training channel does not decide serving mode. Record this current positive-cell mapping outside the frozen 101-row history; do not infer when it was promoted |
| #33 and the historical #30–#32 mapping | The same actual current review: **accept with narrowing** the 165-cell T5 slice as documentary discovery/test context, after reading accepted #33 field/provenance/admission/evaluation sections, blob `dc5cb3c7`. [Original review 5554129449](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/67#pullrequestreview-5554129449) and [reaffirmation 6230504818](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/59#issuecomment-6230504818) retain their literal historical scope and 159/160 counts | Today's one Unsloth P / 164 Unknown cells supply no user-specific fine-tuned artifact, lineage, adapter/merged/provider classification, resolved dataset/framework references, serving tuple, evaluation or licence applicability. All 33 `fine_tuned_deploy` cells remain Unknown. Training data/compute/cost remain missing evidence; no optional T5/MVP adoption follows |
| #36 | Actual in-session Apple technical review on accepted `aeb9f35f`: **accept with narrowing** as discovery/test-design vocabulary. It read all 48 tests and relevant accepted R1–R15/display method, including seven benchmark, one harness, two application-evaluation, four RAG and one monitoring documentary pointers; all guardrail cells remain Unknown | Withhold `evaluation_suite` execution, benchmark rankings/thresholds, regression/deployment gates and measured latency/cost. Actual comparisons still need the accepted full identity/attempt/measurement/uncertainty/grade/intended-use tuple |
| #39 | The same actual in-session review: **accept with narrowing** as price-source discovery and field/test vocabulary; five API-price and three hosting-price documentary pointers | No numerical Pricebook/cost-policy/CostEstimate, source-price truth/freshness/rights, billing semantics, quantity or FX/currency/region defaults. Hardware, recurring, training and TCO cost cells remain Unknown; partial coverage cannot become complete cost or savings |
| #42 | Actual in-session Android technical review on accepted `aeb9f35f`: **accept with constraints** the 52-cell documentary comparison. It checked every guide mark and the accepted frozen-field/revisit/privacy/replay requirements | Use each named artifact only within its basis; no complete selection/settings/link/workload preservation, exact dependency pins, recipient authority, redaction or original/current separation is inferred. The accepted #66 observation keeps its own scope |
| #57 / #58 program feeds | [Actual root receipt 6251641610](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/49#issuecomment-6251641610) accepts concrete overlap/counterexamples as constraints on hypotheses and inputs to the already accepted decision-record comparison; H5 rejection, existing-tool/manifest baseline and joint D-57-1/2/3 rules remain unchanged | No exclusive advantage, demand, experiment, participant, measured fit or broadened optional-stack adoption follows from documentary coverage |

The in-session reviews above are actual engineering work. The [root receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/49#issuecomment-6251641610), [Apple current-source review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/357#pullrequestreview-5563733075) and [Android current-source review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/357#pullrequestreview-5563689928) now anchor the stated receiving decisions, with exact inputs and attribution retained below. Those records are separate from this author's source checks and a test runner's execution. Current technical intake is complete within each stated documentary scope; final amendment review and delivery remain separate gates.

Before a future Exercised configuration-recovery claim, #42 can choose one meaningful Dify or n8n case: explicit synthetic selected values, end/reopen, parse export, second authorized workspace/viewer, exact retained-value/identity/pin comparison and synthetic credential-sentinel exclusions, with release/plan/access/input/output locators. Real #42 application integration separately requires an old immutable revision after source/price/rule changes and unavailable-pin/redacted-recipient behavior. These are future promotion and implementation gates, not unperformed tasks needed merely to accept current documentary research. Existing #40 shared-lifecycle and #41/#60 source-use decisions remain separate.

### Literal #49 criterion map and delivery gates

| Original criterion | Concrete current artifact / interpretation | Acceptance status |
| --- | --- | --- |
| Define atomic capability tests | All 48 original scenarios/observables/required conditions and the explicit branch limitations above | All 48 scenarios/observables independently read in the actual root/native reviews; the final receipt amendment requires its own review |
| Link every supported cell to evidence | All 121 current P records retain claim metadata; 43 current claim URLs are mapped above; corrected ModelFit source is dated separately | Source pass complete within documentary scope; no numerical/rights/runtime certification |
| Keep silence Unknown | 1,463 Unknown; no N or F invented, one unsupported explanation basis narrowed | Complete within this matrix scope |
| Review overlap and compare coverage | Full 33 × 48 identity set, selected guide coverage and exact 13 × 4 subset, with noninterchangeable artifacts | Actual #42 constrained documentary intake completed; no market-gap inference |
| Link significant conclusions to evidence or explicit hypothesis | Source table, specific overlap and explanation/fit/cost/portability limits, explicit unproved differentiation/demand | Source/claim review complete within the stated scope; actual #57/#58 intake accepted with narrowing by the root receipt |
| Relevant technical owners review handoffs; unresolved decisions named | Actual scoped reviews and original receipts above; no invented author/owner acceptance | The ten stated current intakes and separate #30/#57/#58 scopes now have actual linked receiving decisions; historical authors and unresolved implementation/evidence limits remain explicit |
| Additional CanIRun intake: review 48 cells | Preserve the original 2026-10-16 checkbox wording and its 3 Documented / 45 Unknown snapshot. Accepted #340 correction and current review retain 2 Documented / 46 Unknown | All 48 CanIRun records and the capacity-versus-requirement boundary are reviewed; no scenario execution, requirement estimate, rights or accuracy certification is inferred |
| Checks pass; reviewer accepts evidence before Done | Exact committed-tree workflow and configured hosted checks must pass, followed by independent source review, ordinary merge and signed-main validation | Exact original source passed 21 contract and 733 repository tests plus four validators; current receipt/main composition and hosted/signed delivery are recorded in PR #357 before completion |

Current live assignees, all original issue criteria, native relationships and source-use decisions remain unchanged. Project custom fields are not available through the current connector; no Project readback or write is claimed. Research #49 remains open until the remaining concrete receiving/review/delivery gates above are met. The work does not close #6/#7/#16/#25/#27/#30–#33/#36/#39/#40/#42/#47/#59 or reopen completed #10/#48/#57/#58/#66.

### Exact public receipts and current-source preservation

The root receipt was posted through `CompleteDotTech` at **2026-10-18T15:24:09Z** and names prepared `fcc29c518037e0f47e94e1a22f34f846a93cf227`, tree `25bfa13b2d8b38dc15e811e7f8528ec55b4c8071`. Its current model/context/compute/retrieval/differentiation/MVP input blobs are respectively `652bee45`, `f4f2d73e`, `32f2e8a4`, `60a79b04`, `02632ffe` and `aa04388e`. It read all 48 tests and relevant 53 Documented bases and independently checked the exact ModelFit result, Artificial Analysis material and Flowise notice; it did not repeat this author's other primary-page inspections.

The Apple receipt was submitted at **2026-10-18T15:45:40Z** on `5f3765e1a53b52541fa3b27417215685f99961a0`. Its #30/#33/#36/#39 decisions retain the earlier accepted `aeb9f35f` / matrix `00dbb8d94488ad73bae58d5ee934520e95b4862f` input and the stated current-source preservation extension. The separately inspected ModelFit page establishes documentary reasons only; internally inconsistent fit/context claims remain unaccepted. The original T5 owner review and reaffirmation are not rewritten as acceptance of today's 165 cells.

The Android receipt was submitted at **2026-10-18T15:32:19Z** on `5f3765e1a53b52541fa3b27417215685f99961a0`. It directly read the published commit/tree/current files, compared all 52 complete scoped records with the original `aeb9f35f` input and matched every guide mark: 26 Documented / 26 Unknown. Its actual #42 intake and earlier #66 scope inspection do not claim a new product/capture/native/full-suite run or source review of the explanation corrections.

Direct Git Data and raw-byte checks prove published `5f3765e1a53b52541fa3b27417215685f99961a0` has all 647 entries of the locally reviewed source tree: matrix `b511e2e895bd75bbaf7d2bf7d15f196d4f753b04`, guide `0dccc6b15c10005f9cb22022a39e434cf129965f` and audit `fb34e1c0325fadfa23c2130951bd765916e89d35`. That original source passed an isolated exact-tree run under Python 3.12.14 / jsonschema 4.25.1 with the required idna 3.20 pin: **21 frozen-contract tests and 733 repository tests, zero failures/errors/skips, plus all four validators**. Each step preserved the complete input inventory. The later accepted-main code and this receipt amendment receive their own final checks in [PR #357](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/357); earlier execution is never relabelled onto a changed tree.

The [canonical post-cutoff ledger amendment](handoffs.md#mr-02-current-technical-intake-2026-10-18), coordinated in [#59 notice 6251698377](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/59#issuecomment-6251698377), changes only current dispositions for the ten existing #49 rows and appends their real receipts. All historical fields, prior reviews/responses, owners and 44/55/2 cutoff fields remain exact. The separately dated #49-to-#30 discovery record sits outside those 101 historical mappings. Neither these records nor final #49 research completion complete its technical consumers or grant runtime/source-use permissions.

## Preserved earlier audit sections

All sections below retain the literal prior record at blob `bcaebf4fd30df66be46bc437cfaafadd7b70603a`, including historical counts, source dates, review authors and test receipts. The current review above supplies only its separately dated scope.


## Memory-boundary correction — 2026-10-18

Prepared from accepted research main `387e3ff639fc65c125ccd1716507acc2ae43c3bc`, matrix blob `a5e6a0887516b47cd7077a2b7471622cced8f73b`. The later sections retain their literal historical revision, counts, owners and validation; they are not rewritten as current acceptance.

The existing `canirun-ai` / `vram_ram` cell had status Documented, although its own basis describes device memory capacities and explicitly separates them from model memory requirements. The unchanged dimension test requires a requirement for a pinned model/runtime configuration, with units and assumptions. Available device capacity is not partial evidence of that required quantity. The current repair sets this one cell to Unknown and updates its limitation; the previous source identity, URL, access date, reading method, documentary grade, confidence and capacity observation remain exact as historical context.

| Classification | Before this correction | After this correction |
| --- | --- | --- |
| Complete matrix | 33 entities × 48 dimensions = 1,584 cells | Unchanged |
| Documented / Unknown | 123 / 1,461 | 122 / 1,462 |
| Exercised / Unsupported | 0 / 0 | Unchanged |
| CanIRun.ai Documented / Unknown | 3 / 45 | 2 / 46 |
| Other cells and capability-test definitions | 1,583 other cells; 48 tests | Exact preservation required |

This resolves the specific memory-cell mismatch identified in the earlier [shared-file agreement](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/49#issuecomment-6245977192), without adding the six separately staged discovery candidates or their 288 cells. Their catalog/source integration remains a distinct #48 decision. No current source retrieval, product test, model sizing, source-use permission, capability absence or matrix-wide evidence acceptance is asserted by this repair.

The scope supports the #10 distinction between hardware capacity and a model/runtime memory requirement. Actual independent review of this changed cell and guide remains required before delivery; it is not a substitute for the other #49 receiving decisions or review of the remaining supported claims. The completed #66 research may inform a separately reviewed matrix update; its observations are not relabelled as this author's execution and no Flocci grade changes here. All source-register, catalog, canonical handoff, frozen-contract and issue/Project metadata remain outside this patch.

Required checks, exact current-head review and normal canonical delivery are recorded in the contribution's PR. Until those checks and the remaining literal #49 criteria and receiving decisions are met, #49 remains open.

## Delivery and evidence readback — 2026-10-18

Readback basis: research main `ac5e5844dd1cd01366a1b51a0054afa71a340aca` and GitHub
responses read through 2026-10-18T05:19:30Z. PR #87's matrix audit reached canonical main through
#67; #98 added CanIRun.ai. At this revision there are 33 entities, 48 dimensions,
1,584 cells, 123 Documented and 1,461 Unknown; no Exercised or Unsupported cells.
The 48 capability tests cover exactly the 48 dimension IDs. These are coverage
counts, not a product capability score or an acceptance receipt.

The validator uses explicit `MarketValidationError` checks under normal and
optimized Python. The current correction also requires every non-Unknown cell's
existing claim metadata: basis, verification method, evidence grade, exact HTTP(S)
URL without credentials, actual YYYY-MM-DD access date, confidence, limitations
and audit scope. A resolvable source-register ID alone is insufficient. These
offline checks reject incomplete records; they do not retrieve the source or
verify that its text supports the feature's bounded test. Unknown cells can stay
incomplete without fabricated evidence. No grade taxonomy or frozen v1 field is
changed.

### Current acceptance map

| Issue #49 criterion | Evidence at the readback revision | Remaining acceptance or action |
| --- | --- | --- |
| Define atomic capability tests | `features.json` contains 48 scenarios, observables, required conditions and failure policies; the validator checks exact dimension coverage | Independent taxonomy review remains required; compound RAG/MCP/export branches are not interchangeable |
| Link every supported cell to evidence | All 123 Documented cells contain the existing claim metadata; the validator now rejects missing, blank or nontext metadata, invalid URLs and impossible access dates | A valid URL/date is not source accuracy, freshness or intended-use permission; claim review remains separate |
| Keep silence Unknown | 1,461 cells remain Unknown; no new positive or negative cell is introduced by this correction | Do not infer absent capabilities or market gaps from Unknown |
| Review overlap and compare coverage | Existing guide records the 13-profile × four-column saved/share/export/version review and documentary counterexamples | #42's original narrowing is not acceptance of the later cells; current receiver review and selected round-trip tests remain |
| Link conclusions to evidence or hypothesis | Existing matrix records and guide distinguish documentary claims from runtime behavior; the new Flocci evidence is reconciled below without changing grades | Reproducible configurations, measured fit, rights and market demand are still distinct unknowns |
| Obtain technical-owner handoffs and name unresolved decisions | Actual scoped receipts and live co-owners are recorded below, with links to their reviewed revisions | Preserve the canonical #59 writer; author integration cannot supply independent acceptance |
| Pass checks and obtain reviewer acceptance before Done | Current correction runs the complete Python 3.12 workflow and rejection regressions in both Python modes | Exact-head hosted CI, independent review of this correction and remaining research handoffs are required; #49 remains open |

### Actual receiving dispositions and next decisions

These are issue #49's acceptance-map references, not a replacement for the
[canonical handoff ledger](handoffs.json). Its ten #49 pairs at the pinned base
contain two author-integration-only rows, two scoped-response rows and six without
receiving responses. That is recorded receipt coverage, not ten accepted handoffs.
Live GitHub assignees were read for every consumer below; preserve all co-owners.

| Consumers / live co-owners | Actual receipt and retained scope | Next decision |
| --- | --- | --- |
| #6: @zwright8, @PUSHINGSQUARES; #7: @zwright8, @appletechie | [zwright8's 6242699859](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/59#issuecomment-6242699859), reviewing main `7acbefbf4e4e700231e88be272bc89e3a73dde15`: author integration only | Obtain independent taxonomy/claim acceptance; this author cannot approve their own matrix as a receiving reviewer |
| #10: @Mattycodes69, @appletechie | No receiving receipt recorded for the #49 pair at this base | Accept/narrow hardware-estimate coverage; a device capacity or recommendation is not measured model sizing |
| #16: @zabyxc01, @appletechie | No receiving receipt recorded for the #49 pair at this base | Accept/narrow RAG construction versus advice versus evaluation |
| #25: @CompleteDotTech, @Mattycodes69; #27: @CompleteDotTech, @tynamite | No receiving receipts recorded for these #49 pairs at this base | Accept/narrow agent and MCP coverage; a registry listing is not a successful tool exchange |
| #33: @Mattycodes69, @appletechie; relevant #30–#32 context | [appletechie's review 5554129449](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/67#pullrequestreview-5554129449) at `6511dea2a5102b13df1e47378a31f31230ecb494` narrows T5 to information only; [6230504818](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/59#issuecomment-6230504818) reaffirms the #30–#32 mapping | See the exact reaffirmation and conditions immediately below |
| #36 / #39: @PUSHINGSQUARES, @appletechie | No receiving receipts recorded for these #49 pairs at this base | Accept/narrow benchmark/application-evaluation and price-field boundaries; no new measurements or complete cost model are delivered |
| #42: @tynamite, @appletechie | [tynamite's review 5550697545](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/67#pullrequestreview-5550697545) at `6511dea2a5102b13df1e47378a31f31230ecb494` requests the four columns across 13 profiles | The later 52-cell audit answers coverage, not independent acceptance of every cell or execution of a round trip |

The exact T5 reaffirmation is [comment 6230504818](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/59#issuecomment-6230504818).
It explicitly extends the #33 information-only disposition to `fine_tuning`,
`training_compute` and `training_data` context for #30/#31/#32, without new rows
while that limited scope remains. It names no new reviewed SHA, so none is
inferred. A newly promoted finding needs the specific affected-consumer handoff;
`fine_tuned_deploy` must distinguish adapter, merged weights, GGUF or provider-hosted
artifacts. This does not accept a later matrix revision or include training in MVP.

The independent program/evidence review remains with @CompleteDotTech. #48 and
#59 are currently co-owned by @Mattycodes69/@appletechie; #57 by
@tynamite/@appletechie; #58 by @appletechie/@PUSHINGSQUARES. Their historical
"Unassigned" entries below describe the 2026-10-16 snapshot only. No issue owner,
Project status, native relationship or canonical ledger receipt is changed here.

### Reserved matrix correction and later Flocci evidence

The [shared-file agreement 6245977192](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/49#issuecomment-6245977192)
leaves @appletechie the six staged community resources, their 288 cells, the
specific CanIRun `vram_ram` correction and derived guide/count reconciliation.
Device memory capacity alone does not satisfy the model-memory-requirements
dimension. That known cell remains a pending correction until their reviewed
change lands. This submission preserves all matrix cells, taxonomy IDs, source
records and the guide to avoid a competing implementation of that reserved slice.
No additional deep-dive profile or evidence grade is pre-accepted.

[PR #227](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/227), submitted
head `ef685e30af7c1c3a447f4732e1647075b23a3b2b`, merged as
`49896b41b6e0add6f333406112e8d009e7ad9ee6`, adds a dated Flocci guest contradiction,
bookmark and return-navigation observation in [substitute-validation.md](substitute-validation.md).
The older request below to rerun a sign-in-blocked test is historical. The new
note reports recognition of the offline/hosted-model conflict and one saved tool
bookmark without a recovered stack; generated fit/privacy/runtime claims remain
unverified. The distinction between detecting an impossible conjunction and
satisfying a coherent workload is preserved.

[Receiving review 5561540382](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/227#pullrequestreview-5561540382)
accepts only the #40 explanation-versus-compatibility evidence boundary. Its #50
exercised-result acceptance needs review locations for three retained captures;
this author has not independently inspected those screenshots or verified their
hashes. The note's report and other reviewers' evidence scopes are not converted
into this author's observation. No Flocci cell is promoted to Exercised, and no
general absence of export, measured fit or market gap follows. #66's owners and
the actual #42/#50/#57/#58 receivers retain their own acceptance decisions.

### Validation of this correction

Python 3.12.12 with the pinned requirements, run on 2026-10-18:

| Command or observation | Result |
| --- | --- |
| `python -m pip install -r requirements-research.txt` | Pinned dependencies installed in the external audit environment |
| `python -m unittest discover -s contracts/v1/tests -v` | 21 pass |
| `python -m unittest discover -s tests -v` | 184 pass, including four added market-test methods |
| `python scripts/validate_research.py` | 74 catalog proposals and three pricebooks validate |
| `python scripts/validate_market_research.py` and `python -O scripts/validate_market_research.py` | Both pass: 33 entities, 1,584 cells and 20 issues |
| `python scripts/validate_handoff_audit.py` | Pass: 101 rows and 98 declared pairs; human acceptance not certified |
| `python prompts/mobile/validate_prompts.py` | Pass: 258 issues, 36 epics, 906 criteria and 880 steps |
| Controlled baseline/corrected CLI comparison on synthetic records | Missing claim URL, blank grade, URL with credentials and impossible February date each pass the unchanged validator and fail the correction, in both Python modes |

Valid complete synthetic Documented/Exercised/Unsupported cells pass, and an
Unknown cell still passes without invented provenance. Additional regressions
cover every required field missing/blank/nontext, malformed URLs and invalid or
noncanonical dates. This is record-integrity validation; no vendor capability,
freshness, source rights or receiving-owner decision is newly verified. All real
matrix/source records, the guide, canonical handoffs and frozen contracts are
unchanged by this correction. Independent exact-head review remains required.

## Historical submission record — 2026-10-16

The remainder preserves the original proposal-branch audit, counts, owner snapshot
and executed validation. Its present-tense branch/review statements describe that
submission date, not current repository state. No historical test was rerun or
receiving acceptance inferred by this status correction.

Issue: [#49](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/49). Assignee: @zwright8. Audit date: 2026-10-16. Status: corrected draft, awaiting evidence and consuming-owner review; **not Done**.

## Revision and boundary

This contribution starts from `6511dea2a5102b13df1e47378a31f31230ecb494` on the unmerged `research/market-intelligence` branch (PR #67, base main). It changes the matrix and its guide, plus status wording in the market methodology. It does not approve or merge the parent package. Canonical-main delivery remains outstanding.

The live issue and PR review were read before edits. The [2026-10-16 review by @tynamite](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/67#pullrequestreview-5550697545) requests the neutral statuses and narrows the #42 handoff until saved/share/export/model_versions are examined for the 13 profiled products. This audit follows that request. Other issue files, source registrations and the canonical handoff ledger remain owned by their respective contributors.

## Criterion map

| Live criterion | Reviewable artifact and evidence | Exact check / observable | Required review and remaining gap |
| --- | --- | --- | --- |
| Define atomic capability tests | features.json capability_tests: all 48 IDs have bounded scenario, binary capture condition and required version/plan/access inputs | audit-check.log: 48 test definitions, key set equal to dimensions | @CompleteDotTech accepts taxonomy. Compound RAG/MCP/export labels retain explicit branches; a taxonomy split needs review |
| Link every supported cell to evidence | All 120 P cells have resolvable source ID, exact evidence_url, basis, method, evidence class and audit_scope | market-validation.log: 1,536 cells resolve; audit-check.log: all 120 documentary cells include claim metadata | @CompleteDotTech reviews claim truth and scope; source-register URL refinements go to #48 |
| Keep silence Unknown | 1,416 ? cells, no N; inaccessible/unperformed checks remain ? | audit-check.log status histogram and preserved pre-existing unknowns outside explicitly documented additions | No negative market-gap inference permitted |
| Review overlap and compare coverage | feature-matrix.md selected coverage, all 13 profile rows and counterexamples; every cell carries its narrower basis | audit-check.log: 13 × 4 targeted profile checks recorded | #42 owner @tynamite accepts/narrows documentary coverage and chooses required round-trip tests |
| Link significant conclusions to evidence or hypothesis | Guide links primary docs and machine cells; differentiating versioned history explicitly remains hypothesis | Source review manifest and claim-by-claim URLs in matrix | #57/#58 must decide positioning; no acceptance inferred |
| Technical owners review handoffs; name unresolved decisions | Owner/gap table below, refreshed live assignees | issue/pr snapshots; actual #42 review is narrowing only | All final-revision dispositions remain pending; #59 integrates accepted evidence |
| Checks pass and reviewer accepts evidence before Done | Python 3.12 workflow and market integrity results below | Each command exit 0 with captured output | Independent reviewer acceptance, qualifying merge to main, issue/Project readback remain open |

## Evidence collection and corrections

Read-only web text inspection covered the existing 32 entities' primary pages, with targeted documentation for the materially ambiguous cells. It did not execute product capability tests, request model output, deploy compute, pay for access, or reproduce third-party benchmark results. Thus this revision has no F cells. Claim-level classes are **Primary documentation** or **Vendor claim**, not a combined class. All numeric product performance, catalog counts and price examples were excluded from conclusions; no source-rate truth is certified.

All documentary claims inherit the dated public-page scope in features.json, including unpinned software versions, untested entitlements and no permission for downstream dataset display/redistribution. Exact URLs, publishers (existing source IDs), access date, methods, confidence and limitations are preserved in the matrix. This does not resolve #41/#60 rights review.

| Material prior claim | Audit disposition | Evidence / reason |
| --- | --- | --- |
| Flocci natural_language and explanation were F | natural_language becomes P; explanation becomes ? | Public Ask describes natural-language intake. Prior profile/substitute reports describe an observed answer, but their cited records contain no replayable capture locator; this pass did not independently verify that answer |
| Flocci constraints and rag were P from generated Windows/16 GB/no-GPU PDF advice | Both become ? | Generated advice does not establish constraint response correctness or an executed/evaluated retrieval flow |
| Flocci saved had a generic discovery basis | P narrowed to documented bookmarking | Public FAQ explicitly describes bookmarks without an account; persistence and versioned configurations remain untested |
| SkyPilot hosting was P | ? | Compute orchestration documentation does not establish SkyPilot as the actual hosted compute provider for a named offering |
| LM Evaluation Harness evaluation was P | ? | Cited repository establishes model benchmark evaluation, not the application-evaluation scenario; benchmarks remains P |
| MCP Registry mcp was P | P narrowed to registry discovery only | Server metadata registration does not establish a functioning MCP tool exchange |
| Local AI Planner context/multi_gpu were broad P | P narrowed to selector and identical-GPU heuristic | Page explicitly says current model context metadata is unavailable; multiplying VRAM/bandwidth is not topology/parallelism validation |

The original Flocci narrative remains in `competitors/flocci.md` and `substitute-validation.md` at the base revision: a private-laptop prompt reportedly returned local tools, and a Windows/16 GB/no-GPU PDF prompt reportedly returned Docling, txtai, Chroma, Ollama, Gemma and Open WebUI. This is preserved historical reporting, not a newly reproduced observation. #66/@CompleteDotTech should provide the captured interaction or rerun the bounded prompt before reinstating F. This correction neither declares the tools absent nor rejects the original observer's report.

The public ModelFit MCP link was discoverable, but a subsequent text fetch was inaccessible. Its cell remains documentary P for the advertised endpoint, never F or N. Arena's root text showed an app-building surface; the dedicated leaderboard URL was inspected to substantiate its ranking/comparison cells instead.

## #42 scope and counterexample review

All 52 requested cells across the 13 existing profiles carry a targeted check record. Documentary support was added where available, with boundaries in each cell; unanswered tests remain ?. This satisfies coverage of the audit, not a promise of affirmative capability grades.

Dify documents DSL transfer and exclusions; n8n documents JSON transfer and credential-metadata caveats; BenchLM describes filter URLs and a CSV surface; llmfit documents recommendation JSON and benchmark sharing; Models.dev documents catalog JSON; SkyPilot documents task YAML; Hugging Face documents versioned repository history. These mechanisms are heterogeneous and cannot be equated with BuildSnapshot. Account-specific saved selections, import/restore behavior, model revision pinning and recipient authorization still need bounded execution where the receiving owner considers them material. Unknowns cannot support a claim that competitors lack sharing/export.

## Required owner dispositions

Live assignees were read on 2026-10-16. No acceptance is fabricated from an assignment, agent review, PR comment or this table.

| Consumer | Live owner | Exact decision requested for final revision |
| --- | --- | --- |
| #6, #7 | @zwright8 | Accept model identity/context field comparisons as documentary inputs; do not equate displayed context with enforced limits |
| #10 | @Mattycodes69 | Accept/narrow fit-estimate coverage and explicitly reject treating estimated fit as measured sizing |
| #16 | @zabyxc01 | Accept distinction between RAG construction, advice and evaluation |
| #25, #27 | @CompleteDotTech | Accept agent/MCP boundaries; registry presence is not executed interoperability |
| #33 | @appletechie | Accept fine-tuning documentation as coverage only; no fine-tuned deployment proof supplied |
| #36, #39 | @PUSHINGSQUARES | Accept benchmark/evaluation and price-field boundaries; no measurement or complete cost model delivered |
| #42 | @tynamite | Accept/narrow the 13-product saved/share/export/version audit; select required execution cases |
| #48 | Unassigned | Program coordinator routes claim-specific URL refinements into the existing source register; do not assign an owner from stale prose |
| #57, #58 | Unassigned | Program coordinator routes overlap/counterexamples; differentiated versioned history remains a hypothesis |
| #59 | Unassigned | Program coordinator routes final accepted dispositions into the canonical handoff ledger |

The issue names @CompleteDotTech as program evidence reviewer. That review remains required. Source and handoff files were not rewritten by this issue. Project synchronization cannot be claimed from this draft; the coordinating run reported missing GitHub read:project scope, so live board readback remains an external gate.

## Validation and reproducibility

Executed with Python **3.12.12** in a local disposable venv, from this worktree. For each command, the observable is its exit code and the nonempty log below, not a historical report:

| Invocation | Observable | Captured local artifact |
| --- | --- | --- |
| python -m pip install -r requirements-research.txt | Exit 0 | .omo/evidence/mr02-feature-audit/install.log |
| python -m unittest discover -s contracts/v1/tests -v | Exit 0; 21 tests OK | .omo/evidence/mr02-feature-audit/contracts-tests.log |
| python -m unittest discover -s tests -v | Exit 0; 24 tests OK | .omo/evidence/mr02-feature-audit/research-tests.log |
| python scripts/validate_research.py | Exit 0; 0 catalog proposals, 0 pricebooks; external metadata checked | .omo/evidence/mr02-feature-audit/research-validation.log |
| python scripts/validate_market_research.py | Exit 0; 32 entities, 1,536 cells, 20 issues | .omo/evidence/mr02-feature-audit/market-validation.log |
| Recorded read-only matrix audit invocation | Exit 0; all bounded structural checks PASS | .omo/evidence/mr02-feature-audit/audit-check.log |
| git diff --check | Exit 0 | .omo/evidence/mr02-feature-audit/diff-check.log |

The python executable is `.omo/evidence/mr02-feature-audit/venv/bin/python`. Actual audit invocation and source-review manifest are retained in the same evidence directory. No repository Python code was changed, so no new test suite was introduced. Existing market checks derive allowed statuses from status_semantics; the label migration requires no validator rewrite.

Automation checks structure, references, metadata and imported-contract integrity. It does not prove source truth, rights, freshness, actual product execution or owner acceptance. The existing market validator uses Python assertions: run it normally, not with -O; replacing its assertions and changing sparse/not-applicable matrix policy are separate follow-ups from the review, outside this bounded artifact correction.

## Remaining delivery

Use **Refs #49**, not Closes. Coordinate this focused stack with PR #67; review and merge into the proposal branch alone is not delivery to main. Refresh source/owner state and final head before review. After actual evidence and owner acceptance, verify the qualifying main merge, issue closure and Project values. Until those actions occur, this remains an auditable local contribution to an open goal.
