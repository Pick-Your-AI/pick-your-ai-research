# Context quality, content-loss and price warnings

Issue: #7 · Contract review: #40 · Status: proposed

Evidence IDs refer to [context-window.md](../context-window.md). These are proposed decision policies, not empirical model guarantees. All examples are synthetic.

## CTX-03: fit does not prove usable quality; transformations require recounting

- Participating kinds, roles, and JSON pointers: `context_policy` selection `/settings/truncation_strategy`, catalog `/spec/supported_truncation`; matching `model`, optional `rag_pipeline` and `memory_store` selections. Task-quality evidence/estimate bounds are research operands pending #40, not new v1 fields.
- Applicability condition: every context-fit result; transformation check additionally applies if truncate/summarize/sliding-window behavior is requested.
- Assertion and source evidence: report usable quality unknown unless a matching task-specific evaluation envelope exists. CW04's context-degradation discussion and CW11's static-YaRN caveat motivate this policy but cannot produce a universal safe token count. A transformed request must be recounted, preserve required instructions and satisfy #16/#28's content policy. A supported transformation is not evidence of semantic preservation.
- Severity: `warning` (fixed). Unsupported transformations fail this warning-level assertion; #40 may define a separate fixed-error enforcement rule. Passing/unknown outcomes do not change severity, and task quality is assessed separately.
- Missing-data behavior (`unknown`) and proposed policy: absent task, metric, tokenizer, transform support or complete resulting payload yields unknown. Unsupported does not mean undocumented: only explicit evidence produces fail. No percentage safety margin is adopted.
- Explanation and remediation: show the documented limit and separate unverified quality status. Retain critical content or ask the assembly owner to approve a smaller request; then recount and re-evaluate. Do not present compaction as infinite usable context.
- Dependency edges and affected consumers: #16/#28 own assembly/memory preservation; #36 owns evaluation methodology; #7 owns display proposal; #40 approves rules. Any transformation invalidates previous fit and cost assumptions.
- Passing example: synthetic policy explicitly supports `reject`; request fits and unchanged content is counted. The transform-support predicate passes; task quality remains unknown unless independently evidenced.
- Failing example: policy explicitly permits only `reject`, but selected strategy is `truncate_oldest`; fail that support predicate.
- Unknown / non-applicable example: advertised 1M capacity with no matching task evaluation produces unknown usable quality, even when a 900,000-token request fits. A transform-specific predicate is skipped when no transformation is requested.
- Version and migration impact: retain v1 truncation enum; propose quality-evidence references and recount provenance for next version. Do not fabricate a `usable_context_tokens` scalar or redefine context capacity.

## CTX-04: context-dependent price classification is complete

- Participating kinds, roles, and JSON pointers: `model` identity/version, `context_policy` selected input/output budgets, `cost_policy`; exact Pricebook rate references and meter identity. Token-threshold comparator, request/session scope and tier eligibility are research operands requiring #39/#40 agreement.
- Applicability condition: route has documented prompt-dependent prices or the selected service scope is uncertain. Token reservation alone does not establish actual billed usage.
- Assertion and source evidence: resolve the correct whole-request/session price condition before presenting a total. CW01 applies GPT-5.4's >272,000 input predicate to full-session prices; CW08 uses prompt length to choose Gemini Pro input and output rates. CW04 says standard long-context pricing for scoped Sonnet5.5. Do not apply Pro thresholds to Flash or legacy Claude tiers to current routes.
- Severity: `warning` (fixed). Classification can pass, fail or remain unknown at that severity; exceeding a price threshold is not itself a compatibility failure.
- Missing-data behavior (`unknown`) and proposed policy: missing route/version, actual input estimate, currency/region or full-session accounting makes cost classification unknown. If an estimate interval crosses a threshold, show conditional scenarios rather than a single guaranteed rate. Missing rate is not zero.
- Explanation and remediation: state comparator, billed meter, currency, service tier and scope; obtain exact counts/rate conditions or present separately labelled scenarios. #39 retains cost aggregation ownership.
- Dependency edges and affected consumers: context/route -> #39 price selection; #16/#28 assembly changes invalidate it. Rate changes invalidate cost estimates without automatically changing fit.
- Passing example: synthetic exact prompt count 200,000 selects Gemini Pro's documented <=200,000 tier. Exact 200,001 selects its >200,000 tier and generates a warning about the higher rate, not a fit failure.
- Failing example: an estimator applying the low rate to an exact 200,001-token Pro prompt fails this **classification assertion**, not model compatibility. Such an error needs correction before a cost total is presented.
- Unknown / non-applicable example: input estimate [199,000,201,000] is unknown tier; both conditional cost scenarios are permitted. Threshold-specific check is skipped for a proven flat rate, while ordinary cost validation still applies.
- Version and migration impact: #39/#40 must agree rate condition representation, full-session accounting and invalidation in a future version. No conditional rate is flattened into a misleading unconditional v1 price; frozen Pricebook/schema remain unchanged.
