# Agent run bounds: evidence for the G-H7 follow-up

Refs #35, #25, #38 and #39. Research note, 2026-10-18; receiving owners remain the live issue assignees. This supports the open G-H7 source question in [the #121 guardrails draft](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/33f87a5750be1a31ad5f9ccd9e9cfbbf4e8a42d0/research/T6-deployment-operations/guardrails.md). It does not replace that decision record, change G-H7's hypothesis status, or claim execution of an agent.

## Evidence inspected

| ID | Source and exact scope | Access date / revision | Grade and finding |
| --- | --- | --- | --- |
| RB-1 | [OWASP LLM10:2025 Unbounded Consumption](https://genai.owasp.org/llmrisk/llm102025-unbounded-consumption/), Prevention and Mitigation Strategies | 2026-10-18; page identifies the 2025 taxonomy, no commit/version for page content | Primary documentation of OWASP guidance. Recommends input-size validation, per-user request quotas, resource management, timeouts/throttling, monitoring, and bounds on queued and total actions. It identifies financial exhaustion as a risk. It does not supply a universal per-agent token or currency threshold. |
| RB-2 | OpenAI Agents Python [running guide](https://github.com/openai/openai-agents-python/blob/9abc9182d06dbd28330af888306031269d57a175/docs/running_agents.md), agent loop and error handlers | 2026-10-18; commit `9abc9182d06dbd28330af888306031269d57a175` | Primary documentation, source checked. `max_turns` limits the loop; `None` disables it. Exceeding it raises `MaxTurnsExceeded` unless a configured handler returns a controlled final result. Inspect the configured error handling when determining the observed failure path. |
| RB-3 | OpenAI Agents Python [Runner implementation and argument contract](https://github.com/openai/openai-agents-python/blob/9abc9182d06dbd28330af888306031269d57a175/src/agents/run.py), `Runner.run` argument documentation | 2026-10-18; same commit as RB-2 | Primary documentation/source inspection, not runtime reproduction. A turn counts an AI invocation, including associated tool calls. Therefore the turn counter alone is not evidence of an individual tool-action count, token allowance, or monetary ceiling. |

The rendered [running guide](https://openai.github.io/openai-agents-python/running_agents/) was opened on the same access date; the two pinned repository files were separately retrieved and read. No package was installed or agent/model request executed. These observations describe this inspected repository revision; they do not establish behavior for the different package versions selected in existing T4 catalog proposals. That requires version-specific reconciliation.

## Consequence for the pending rule

The G-H7 note that OWASP was identified only by name can now be replaced by an actual source citation when the T6 owners integrate this evidence. RB-1 supports resource and action bounds as a safety practice. RB-2/RB-3 provide a concrete implementation example with narrower semantics than an aggregate budget.

Keep the universal choice of required controls, thresholds, scope and warning severity as a policy proposal. Neither the documents nor this inspection prove that a turn limit prevents all runaway tool use or spend. Do not mark G-H7 independently verified, introduce a fabricated numeric default, or turn absence of configured evidence into a claim of observed runaway behavior.

The distinction is material for comparisons: a bounded number of model invocations may contain several tool calls and differing token/output sizes. A token or request measure also needs its own price/rate conditions before it can express currency. This is dimensional reasoning, not a measured cost result.

## Proposed receiving evidence checklist

This checklist is a research handoff, not new frozen-v1 fields or an executable ruleset.

| Receiver | Evidence to request | Missing or unresolved case |
| --- | --- | --- |
| #25 / #35 | Selected framework revision, counter unit, run/nested-agent scope, configured limit, enforcement point and handling of limit exhaustion | A documented `max_turns` option is not proof that the selected build enables it; keep unknown unless configuration is evidenced |
| #35 / #37 | Distinguish model turns, individual tool actions, queue limits, execution timeouts and aggregate token/spend policies | Do not claim cross-process or nested-run coverage from a local loop counter; inspect the actual enclosing runtime |
| #38 | Content-free observations of configured limit, exhaustion event, action/usage counters and stop or controlled-result outcome | Telemetry alone is not enforcement; content capture is not needed merely to report an exhaustion event |
| #39 | Workload scope, tokens by billing class, tool meters, applicable dated rates and uncovered costs for a proposed monetary bound | A turn cap or missing price does not imply a known upper-cost ceiling; unpriced scope remains named and unknown |

## Disposition and sequencing

- The source-discovery portion of the G-H7 question is now answered narrowly; product-specific configuration, aggregate enforcement and policy adoption remain open for #35 with #25/#37/#38/#39.
- This new supporting note leaves the five overlapping canonical records and appletechie's agreed #121-first recuts untouched. It does not carry the Vertex defaults, OpenLLMetry, lm-eval or training harm-screen changes owned by those follow-ups.
- No source-use permission, consumer acceptance, deployment approval, runtime availability or whole-issue completion is implied. This note can be reviewed independently; integration into the candidate rule remains a separate recorded decision.
