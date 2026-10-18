# Context fit and route constraint proposals

Issue: #7 · Contract review: #40 · Status: proposed

Evidence IDs refer to [context-window.md](../context-window.md). These proposals apply documented constraints; they are not an approved Ruleset. `pass/fail/unknown/skipped` are outcomes; `error/warning/info` are severities. All examples are synthetic arithmetic scenarios, not calls or benchmarks.

Follow-up to the [#3/#40/#41 owner's review of PR #88 at `dbfa7dd`](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/88#pullrequestreview-5554964868), accessed 2026-10-17: the bounded estimate uses its upper bound, and unknown extension configuration falls back to the evidenced native limit. These owner positions do not approve a new contract or executable ruleset.

## CTX-01: request fits the selected route

- Participating kinds, roles, and JSON pointers: enabled `model` and its corresponding `context_policy`, bound by role/selection IDs rather than arbitrary first item. Model `/spec/context_window_tokens`, `/spec/max_output_tokens`; policy selection `/settings/requested_context_tokens` (input P), `/settings/reserved_output_tokens` (generation O); optional policy `/spec/max_allowed_tokens` (C). Offering identity and independent input-limit semantics are research operands pending #40, not invented v1 pointers.
- Applicability condition: selected generation route and known count semantics. Disabled selections are skipped. Shared-window predicate applies only to shared semantics; separate-budget predicate requires evidenced independent limits.
- Assertion and source evidence: for shared capacity W, require P + O <= W and O <= output cap, plus separately evidenced input and policy ceilings if present. C is proposed as total P + O ceiling and requires #40 confirmation; no ceiling is assumed when absent. CW01/CW02 and CW03/CW04 support shared semantics. For Gemini 2.5 use P <= input cap and O <= output cap (CW06/CW07), never manufacture W. Route cap from CW09 cannot be replaced by direct-provider CW10. A reserved generation amount includes thinking where applicable, not just visible prose. This is a proposed conservative reservation screen, not a promise that the API reserves all requested output.
- Severity: `error` (fixed independently of pass/fail/unknown/skipped). The outcome carries fit/uncertainty; no severity change is implied by a pass.
- Missing-data behavior (`unknown`) and proposed policy: absent model/route/semantics or unbounded input yields unknown. With valid bounds Plo/Phi, decide on Phi: pass only when Phi passes every applicable predicate; fail when Phi violates any applicable cap or O alone exceeds output cap. If only the upper end violates a cap, flag the fail as **may not fit** and show the full range; an estimated failure is not a measured API rejection. An explicitly non-applicable combined predicate is skipped for separate semantics, not silently passed. Partial successful predicates cannot hide an unknown overall fit.
- Explanation and remediation: report the violated limit, requested budget, source and scope. Reduce input/reserve, select another evidenced route, or obtain a supported complete count. Do not silently truncate or change provider.
- Dependency edges and affected consumers: model/provider/context -> fit -> #16/#28 assembly, #10 capacity, #39 cost. Invalidate after route/model/version/template, modality or budget changes. These are information/compatibility edges, not issue blockers.
- Passing example: shared W=1000, output cap=200, P=700, O=200 gives 900 <=1000 and 200 <=200. Separate input cap=1000/output cap=200 with P=1000/O=200 passes the separate predicates even though their sum is 1200; no shared-cap assertion exists.
- Failing example: same shared limits with P=900/O=200 fails the sum; P=500/O=201 fails output. A route with cap=100 rejects a reserve of 150 in the proposal even if a different provider publishes 200.
- Bounded / unknown / non-applicable examples: P in [750,850], O=200, W=1000 gives a total range [950,1050]; upper-bound 1050 >1000 returns `fail`, flagged **may not fit**, with both ranges shown. An unbounded input remains unknown. Missing output cap on Qwen prevents an unconditional overall route-fit pass; a known violated constraint can still fail. Disabled selection is skipped.
- Version and migration impact: v1's sum metric cannot encode independent input semantics or route overrides safely. #40 must introduce explicit operands/semantics and migrate readers before machine evaluation of Gemini separate-budget records. Existing shared-window v1 records retain their meaning. Do not patch generated schemas or emit final rule JSON here.

## CTX-02: long-context runtime configuration is evidenced

- Participating kinds, roles, and JSON pointers: `model` `/spec/context_window_tokens`, `context_policy` selection budgets, `inference_engine` catalog identity/version and settings, `accelerator`/`compute_profile` bindings. Exact YaRN/config/tokenizer and cache settings are research evidence, pending typed operands through #40.
- Applicability condition: self-hosted or managed dedicated runtime with an exposed configuration; skip local sizing for provider-owned API serving.
- Assertion and source evidence: selected context must stay within the evidenced runtime/model configuration, and #10 must separately evaluate memory. CW11 distinguishes Qwen native context, conditional YaRN extension and static-scaling caveat; CW12's max-position setting does not prove quality or runtime capacity. When extension configuration is unknown, evaluate the limit predicate against the evidenced native limit; missing configuration never upgrades native to extended context. A documented lower runtime ceiling also applies. T2's method is a referenced proposal, not approved universal fit.
- Severity: `error` (fixed). Exceeding the applicable evidenced limit fails, including a native-limit failure when extension evidence is missing. A supported configuration predicate can pass without implying quality.
- Missing-data behavior (`unknown`) and proposed policy: missing native limit leaves the limit predicate unknown. Unknown extension setup uses the known native limit rather than making that predicate unknown. Unknown engine version, cache layout or allocation leaves its separate runtime-support or memory result unknown (`on_unknown: review` for the shared memory-fit family). Do not encode unknown memory as zero. Passing the native-limit predicate is not a runtime-support, quality or SLO pass.
- Explanation and remediation: provide pinned model/runtime configuration, matching tokenizer and T2 manifest; reduce the budget or obtain measured workload evidence. Do not enable YaRN silently.
- Dependency edges and affected consumers: #6/#7 -> #11 configuration -> #10 per-device sizing; #16/#28 quality and #39 cost receive assumptions. Configuration changes invalidate dependent estimates.
- Passing example: hypothetical runtime documents/configures combined 32,768 and has P=20,000/O=8,000; the limit predicate passes. Memory and quality remain separate results.
- Failing example: same configured maximum with P=30,000/O=8,000 fails that maximum even if a model card advertises a conditional 131,072 extension.
- Native fallback / unknown / non-applicable examples: Qwen request for 100,000 against evidenced native 32,768 with no YaRN/runtime proof returns `fail`; remediation is to evidence an extended configuration or reduce the request. A request at or below 32,768 can pass this native-limit predicate while separate runtime/memory checks remain unknown. Missing native-limit evidence yields unknown; API-only local KV check is skipped.
- Version and migration impact: central review must add configuration provenance/conditional operands before automated extension approval. Keep existing v1 values and T2 methodology intact; no final Ruleset emitted.

## Executable synthetic cases (CD-11)

The [test-only prototype](../../../tests/context_budget_prototype.py) and
[executable cases](../../../tests/test_context_budget.py) exercise these proposed
semantics over normalized eligible facts. They distinguish a shared-window sum
failure from independent input/output passes, use the upper estimate bound,
flag a straddling failure as `may_not_fit`, preserve equality at a cap, and retain
unknown when only some required predicates pass. A known violated cap can fail
even when another operand is missing. Separate-budget combined checks are skipped.
Explicit policy ceilings remain additional proposed predicates, not vendor limits.

The runtime-limit cases exercise native fallback and a lower known runtime ceiling.
They do not establish runtime support, KV fit, quality or latency. Missing tuple
matching evidence cannot borrow another route's limits. Disabled selections skip.
All numbers are synthetic; no provider request or model execution occurs.

Run `python -m unittest discover -s tests -p test_context_budget.py -v`.
The prototype accepts only internally constructed, normalized nonnegative token
counts with ordered bounds. `None` means missing fixture evidence, not a proposed
wire value. Real selection binding, count eligibility, answer-state encoding,
source conflicts and migration remain #40 decisions. No frozen evaluator or
schema changes and no released compatibility ruleset are supplied.
