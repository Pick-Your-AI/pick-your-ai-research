# Proposed release-scoped inference-engine rules

Issue: #11 · Contract review: #40 · Status: proposed / unverified · Version: 0.1.0

Evidence IDs refer to [inference-engine.md](../inference-engine.md), accessed 2026-10-16. These proposals follow [the shared template](../../../templates/rule-proposal.md). Publisher documentation is evidence for stated premises; it does not independently reproduce a joint runtime. Every example below is a synthetic rule illustration. Outcomes `pass/fail/unknown/skipped` are distinct from severities `info/warning/error`.

## ENGINE-01: exact artifact loader and architecture

- Participating kinds, roles, and JSON pointers: primary `model` `/version`, `/spec/model_formats`; `inference_engine` `/version`, `/spec/model_formats`; optional `fine_tuned_model` `/spec/artifact_format`. Exact architecture/artifact revision and plugin/build versions remain note-only inputs.
- Applicability condition: enabled customer-controlled engine loads a local model artifact.
- Assertion and source evidence: require an evidenced loader and architecture path for the exact release/artifact. E03/E10 describe vLLM loaders and separate GGUF plugin; E13 requires GGUF for llama.cpp; E20/E24 describe TGI's bounded optimized support and best-effort fallback.
- Severity: `error` for a proven unsupported loader; `warning` for an unverified tuple; `info` for a corroborated scoped pass. Split these assertions if #40 requires fixed severity per rule.
- Missing-data behavior (`unknown`) and proposed policy: intersecting file-format lists alone cannot pass. Missing plugin/version, architecture support, conversion correctness or evidence yields unknown.
- Explanation and remediation: name the mismatched layer; choose an evidenced loader/plugin or convert and validate the artifact with immutable lineage. A suffix rename is not conversion.
- Dependency edges and affected consumers: #6 ↔ #11 ↔ #33; #10/#37/#40/#42; selection changes invalidate the scoped result.
- Passing example: a matching, independently reproduced GGUF architecture with pinned llama.cpp build gives the scoped loader assertion `pass/info`.
- Failing example: directly feeding a Safetensors checkpoint to the documented GGUF-only llama.cpp loader gives proposed `fail/error`.
- Unknown / non-applicable example: vLLM v0.31.0 + GGUF with no plugin pin gives `unknown/warning`; provider API with no local runtime gives `skipped/info`.
- Version and migration impact: no v1 mutation. Preserve exact support tuples, plugin revisions and saved-build loader contracts in a reviewed next-version design.

## ENGINE-02: joint backend and precision implementation

- Participating kinds, roles, and JSON pointers: engine `/spec/backends`, `/spec/supported_precisions`; accelerator `/spec/backends`, `/spec/precisions`; selected model/engine precision and quantization. Model architecture, kernel/driver and weight/activation/KV roles require note evidence.
- Applicability condition: selected hardware executes the model through the chosen release/build.
- Assertion and source evidence: require joint release, architecture, quantization and device support; E05/E10/E15/E25 supply conditional requirements. vLLM v0.31.0 CUDA minimum is 7.5 while older matrix Volta cells conflict; preserve that combination as unknown.
- Severity: `error` for explicit unsupported constraints; `warning` for missing/conflicting tuple evidence; `info` for an independently corroborated scoped support check.
- Missing-data behavior (`unknown`) and proposed policy: flat enum intersections are insufficient. An `other` enum or native INT4/FP8 capability cannot establish a particular kernel path.
- Explanation and remediation: report exact precision role, scheme and device/build constraint; select an evidenced alternative or obtain a reproducible check. Capacity remains #10.
- Dependency edges and affected consumers: #6/#10/#11/#33/#37/#40; recompute the cycle without imposing a research delivery order.
- Passing example: exact artifact/backend/device/build tuple independently reproduced gives scoped support `pass/info`.
- Failing example: TGI v3.3.7 EXL2 with more than one shard contradicts E25's documented restriction: proposed `fail/error`.
- Unknown / non-applicable example: “FP8 + AMD” without layout/kernel/driver gives `unknown/warning`; opaque provider API GPU gives `skipped/info` for local hardware checking.
- Version and migration impact: maintain release-specific evidence; no global support boolean or new precision enum. Historical results do not apply automatically to current releases.

## ENGINE-03: adapter lineage and loading semantics

- Participating kinds, roles, and JSON pointers: `fine_tuned_model` `/spec/base_model_ref`, `/spec/artifact_format`, `/spec/adapter_only`; primary model ID/version; engine ID/version. Base revision/tokenizer, adapter method/rank/targets/layout and routing/composition are additional evidence inputs.
- Applicability condition: an enabled unmerged adapter is loaded, or a fine-tuned artifact is claimed portable to this engine.
- Assertion and source evidence: require immutable compatible base/tokenizer lineage and exact engine adapter-loading support. E09, E14 and E22 distinguish per-request routing, multi-adapter batching and simultaneous scales; these are different capabilities.
- Severity: `error` for proven base/format contradiction; `warning` for missing lineage or unsupported evidence; `info` for a corroborated scoped loader result.
- Missing-data behavior (`unknown`) and proposed policy: no adapter support boolean inferred from Safetensors/GGUF alone. Provider-locked output or unknown base revision stays unknown.
- Explanation and remediation: obtain #33's artifact manifest, matching base/tokenizer and supported conversion/layout; treat merged weights as a full checkpoint and size them once.
- Dependency edges and affected consumers: #6/#10/#11/#30/#33/#37/#40. #33 owns artifact identity; #11 serving; #10 residency; #31 training.
- Passing example: an adapter pinned to the selected immutable base, validated on the exact engine/backend/loading mode, gives `pass/info` for that loader path.
- Failing example: an adapter with an explicitly different required base/target tensor shape gives scoped `fail/error`.
- Unknown / non-applicable example: unpinned PEFT adapter conversion gives `unknown/warning`; `adapter_only=false` merged checkpoint gives `skipped/info` for unmerged-adapter loading and still runs ENGINE-01/02.
- Version and migration impact: #40 must review lineage/conditional-support fields. Preserve historical adapter semantics and do not reinterpret routing as composition.

## ENGINE-04: required API feature and request contract

- Participating kinds, roles, and JSON pointers: engine ID/version and optional `/spec/supports_tool_calling`; agent/RAG consumer selections. Required endpoint, schema dialect, parser/template, tool mode, streaming/error/cancellation behavior are note-only consumer requirements.
- Applicability condition: the application requires structured output, tools, streaming or an API feature on a particular endpoint.
- Assertion and source evidence: match the actual request contract and release configuration; E06–E08/E14/E17/E18/E23 preserve limits. vLLM guided-field removal and parallel-call behavior differ across historical/current releases. “OpenAI-compatible” is not whole-API equivalence.
- Severity: `error` for an explicitly incompatible required contract; `warning` for untested model/parser/schema combinations; `info` for a corroborated consumer check.
- Missing-data behavior (`unknown`) and proposed policy: omitted feature booleans, undisclosed managed versions or missing acceptance cases yield unknown; do not infer unsupported from omission.
- Explanation and remediation: identify failing endpoint/field/parser/template/schema constraint; use a supported request contract or obtain consumer acceptance evidence in #25/#16/#37.
- Dependency edges and affected consumers: #7/#11/#16/#25/#27/#33/#37/#38/#40; tool execution/authorization and knowledge ACLs remain with their owners.
- Passing example: exact release/model/template/parser and required tool/schema/stream behavior reproduced with consumer fixtures gives `pass/info`.
- Failing example: requiring legacy `guided_json` on vLLM v0.31.0 after documented removal gives proposed `fail/error`; migrate to release-supported fields.
- Unknown / non-applicable example: an undisclosed managed engine advertising generic chat compatibility gives `unknown/warning`; application requiring none of this rule's features gives `skipped/info`.
- Version and migration impact: retain request-contract versions and consumer evidence; invalidate only affected tuples after an engine/template/parser change. No approved runtime acceptance tests or new canonical feature fields are introduced here.
