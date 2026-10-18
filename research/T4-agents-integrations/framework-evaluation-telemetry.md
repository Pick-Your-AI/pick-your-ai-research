# Framework evaluation hooks and telemetry boundaries

Refs #25, #35, #36 and #38. Source access and synthetic probes: 2026-10-18.
Status: bounded research contribution; receiving-owner adoption remains open.

## Decision to support

Which evaluation mechanism is actually present in a selected framework, what
does its result establish, and which collectors may send data when it runs?

The three candidates below already occur in the #25 comparison. This follow-up
closes specific unread source gaps for their pinned Python releases. It does not
survey every framework, run a complete evaluator, or establish model quality,
network behaviour, retention, regional availability, price or a deployment gate.

Two details change the proposed consumer checks. Agno's inspected evaluator
telemetry is controlled separately from the Agent environment override. CrewAI's
experimental metric comparator can return true while an expected metric is
missing. The latter is reproduced below with synthetic values in the exact
isolated function body; it is not a benchmark result.

## Pinned candidates and method

| Candidate | Release and immutable revision | Scope of inspection |
| --- | --- | --- |
| OpenAI Agents Python | `0.24.0`, `17d994bd3045dae71acda676a4ef4762ed8ecd94` | Testing/tracing guides, tracing setup and processor API; the existing A86 release pin is retained |
| CrewAI Python | `1.15.28`, `eb15c66cef12073d8d06d6942eecc35e7fd6c783` | Annotated release tag, package metadata, versioned testing/telemetry docs, telemetry implementation and experimental evaluators; metadata pins `crewai-core` and `crewai-cli` to `1.15.28` |
| Agno Python | `3.1.3`, `4c969bc5fd88c3b1e6e7d3aa470ba0cd19252a8a` | Release ref, package metadata, Agent telemetry, telemetry API, and Accuracy/Reliability/Performance evaluator code |

The primary sources are listed below. Raw UTF-8 content was read, and locally
cached source bytes were checked against the publisher's Git blob identities
before the isolated probes. No framework was installed. No Agent, complete
evaluator, model, tool, paid API, GPU or network-producing provider was executed.
The probe replaces Agno's API import with an in-process recorder.

Grade: **Primary documentation / source code, source-checked and unverified** for
package claims. The retained probe outputs establish only the observed behaviour
of those isolated functions with synthetic inputs. They do not upgrade a
framework's product claims to independently verified quality or privacy.

Rights treatment: links and bounded paraphrase under the existing #41/#60
research-note policy. No upstream source bodies, hosted traces, benchmark data,
credentials or production user content are redistributed here; this is not a new
commercial-display or redistribution permission decision.

## Evaluation mechanisms and limits

| Candidate / mechanism | What the inspected source supplies | What a consumer must retain or qualify |
| --- | --- | --- |
| OpenAI `ScriptedModel` and testing helpers | Deterministic model responses and recorded SDK-normalized calls can exercise the application's tool loop, handoffs, guardrails, streaming and sessions. The guide separately covers scripted sandbox, realtime and voice boundaries. Its examples disable tracing to avoid uploading test activity when a tracing key is configured. [FET-03] | These are orchestration tests. They do not establish that a real model selects the right tool, that a real provider protocol works, or that a sandbox/audio provider performs the requested operation. Keep the script, assertions, SDK revision and tracing settings with the result. |
| CrewAI `crewai test` | The versioned guide documents repeated crew execution, task scores and execution time. The CLI wrapper invokes the project's test entry point through `uv run test` with the requested iteration count/model and an environment populated with tool credentials. [FET-08] | This may execute the configured crew and tools. A named evaluator model or command is not a frozen judge snapshot, approved tool action, or comparable quality measurement. Record task inputs, actual judge/provider identity, criteria, tool effects and run conditions. No test command was run in this research. |
| CrewAI experimental `AgentEvaluator` / `ExperimentRunner` | Event hooks collect task/agent completion evidence; experiment cases carry inputs and expected scores. The testing helper can compare against a baseline and reports missing baseline cases as a warning. [FET-09, FET-10] | Preserve individual metric coverage. The source predicate compares the intersection of expected and actual metric keys, so its returned boolean alone cannot establish complete coverage; see the synthetic probe. Missing baseline cases also need an explicit consumer policy. These experimental interfaces are not a project-wide quality bar. |
| Agno `AccuracyEval` | Compares an Agent/Team answer with a supplied expected answer through an evaluator Agent. A custom model/evaluator can be supplied; otherwise the inspected factory selects OpenAI `o4-mini`. Its rubric uses integer scores from 1 to 10 and treats the supplied expected answer as correct. [FET-13] | This is judge-based agreement with the expected answer. Pin the judge, rubric, expected-answer source and target route; do not infer truth of the reference, calibration or portability of a score. Target execution and judge execution have their own data, telemetry and cost boundaries. |
| Agno `ReliabilityEval` | Reads supplied run output and checks actual tool-execution records, expected tool names and optional arguments; request-side calls alone do not satisfy an execution expectation. The default rejects additional tool names unless subset matching is enabled. [FET-14] | Name/argument checks are narrower than correctness of a tool's external effect, authorization, idempotency or answer quality. Retain failed/missing/additional calls and the chosen matching policy. |
| Agno `PerformanceEval` | Times the supplied function and measures Python traced allocation peaks through `tracemalloc`; the memory calculation converts the peak to MiB and subtracts its supplied baseline. [FET-15] | This is a host-function/Python-allocation quantity. It cannot be relabelled as whole-process RSS, GPU allocation, VRAM capacity or the #61 runtime measurement target. Record the function, instrumentation, baseline, repetitions and environment; no performance sample is produced here. |

These categories are not mutually comparable scores. The proposed #36 input is
an explicit evidence record for the selected mechanism, not a general
`supports_evaluation` boolean or a ranking across these libraries.

## Telemetry controls are scoped to their producers

| Producer | Pinned source finding | Proposed consumer treatment |
| --- | --- | --- |
| OpenAI Agents tracing | Tracing is enabled by default. The default processor exports to OpenAI; the provider is created lazily on first access. Controls include `OPENAI_AGENTS_DISABLE_TRACING=1`, global `set_tracing_disabled(True)` and per-run `tracing_disabled=True`. [FET-01, FET-02] | Set the intended policy before creating traces. A successful export additionally depends on credentials, endpoint and delivery; source inspection does not observe a network request. Model-provider choice and trace destination are separate. |
| OpenAI content/export lifecycle | Sensitive-data capture defaults to enabled. `add_trace_processor()` keeps the default exporter, while `set_trace_processors()` replaces the processor list. Disabling tracing prevents new records but does not erase already buffered data; the guide explicitly says flush can still export it. [FET-01] | Capture suppression, processor replacement and queue disposition need separate evidence. A metadata-only processor added alongside an existing exporter is not an egress boundary. Inspect caller-supplied metadata and any separate audio/custom processors; do not infer universal redaction from one flag. |
| CrewAI metadata telemetry | The inspected telemetry collector uses `https://telemetry.crewai.com:4319/v1/traces` and an owned OTel provider. Default metadata includes roles/tool names, model/settings and test scores/timing; `share_crew=True` additionally includes crew/task content. [FET-05, FET-07] | Treat metadata as data-bearing: user-chosen names may be sensitive. The documentation's anonymous/non-personal characterisation is a vendor claim, not a permission or data-residency finding. Turning off `share_crew` alone does not disable ordinary telemetry. |
| CrewAI disable controls | The pinned core checks `CREWAI_DISABLE_TELEMETRY`, `CREWAI_DISABLE_TRACKING` and `OTEL_SDK_DISABLED`; recognized true values are `true`, `1`, `yes`, `on`, ignoring case/outer whitespace. Unknown values retain the default. [FET-06] | Prefer an explicit documented value before initialization. CrewAI's guide distinguishes its own broad flag parser from the OTel SDK's `true` spelling for other instrumentation. No one setting here certifies application exporters, AMP trace-sharing, retained data or a network boundary. [FET-05] |
| Agno Agent telemetry | `Agent.telemetry` defaults to true. `set_telemetry` reads `AGNO_TELEMETRY`, and an existing value overrides the Agent setting through a case-insensitive equality check with `true`. Agent run telemetry includes IDs, model/DB identity and capability/configuration metadata. [FET-11] | Record both the constructor setting and effective environment. For example, a true environment override takes precedence over `telemetry=False` on that Agent. The override is not evidence about every other producer. |
| Agno evaluator telemetry | Accuracy, Reliability and Performance each declare `telemetry=True`; their run methods call the eval telemetry helper when that field is true. The inspected helper/API path has no `AGNO_TELEMETRY` check. [FET-13–FET-16] | Set and verify the evaluator's own `telemetry=False` as well as the target/judge Agent policy when those collectors must be off. The synthetic helper probe confirms only that helper boundary, not an actual production transmission. |
| Agno delivery/lifecycle | The inspected API uses `https://os-api.agno.com` by default and a bounded background queue. Overflow and bounded shutdown can drop events; enqueue is not a delivery receipt. [FET-12] | Keep created, queued, exported and accepted counts distinct, and record destination/runtime configuration. Disabling a producer does not by itself certify a previously queued event was discarded. Database result storage and configured tracing exporters require their own policy. |

## Isolated synthetic probes

The [retained output](../../tests/fixtures/framework-evaluation-probes.json) records
Python 3.12.14 execution at `2026-10-18T06:48:30.023404+00:00`, three exact source
SHA-256 values, synthetic inputs and results. The
[offline reproducer](../../scripts/reproduce_framework_probes.py) checks fixed
source hashes before parsing/compiling only the named function bodies. It makes
no download and does not import installed framework code.

### Missing expected metric

The exact `ExperimentRunner._assert_scores` body produced:

| Synthetic case | Expected metrics | Actual metrics | Upstream boolean | Consumer implication |
| --- | --- | --- | --- | --- |
| Complete passing pair | goal ≥ 7, tools ≥ 7 | goal 8, tools 8 | true | Complete for these two fabricated predicates only |
| Known low value | goal ≥ 7, tools ≥ 7 | goal 6, tools 8 | false | One supplied metric is below its synthetic threshold |
| Missing expected metric | goal ≥ 7, tools ≥ 7 | goal 8; tools absent | true | Boolean does not establish the missing tools result |
| No matching metric | goal ≥ 7, tools ≥ 7 | other 8 | false | No expected metric has a matching result |

The names and numbers are deliberately synthetic, not adopted criteria or
thresholds. The proposed #36 consumer first checks required metric coverage and
eligibility, then interprets per-metric values. An absent result remains missing
evidence rather than a score, a successful full evaluation, or proof that the
model failed the task. This proposal does not alter a v1 outcome or define a
successor wire field. [FET-09, retained output]

### Agent override versus evaluator helper

With `AGNO_TELEMETRY=false`, the exact `set_telemetry` body changed a synthetic
Agent-like object's telemetry from true to false. In the same environment, a
direct call to the exact `log_eval_telemetry` body invoked the in-process API
recorder once. The full evaluator was not invoked; its separate default and
`if self.telemetry` call sites are source evidence, not part of this execution.
No network request occurred. [FET-11, FET-16, retained output]

To reproduce, obtain only the three source files listed under `sources` in the
fixture from their pinned raw GitHub URLs. Save the exact UTF-8 bytes as
`crew-evalrunner.txt`, `agno-init.txt` and `agno-evalutils.txt` in a local directory.
Run:

```bash
python scripts/reproduce_framework_probes.py --source-dir /tmp/pinned-framework-sources --verify
```

The command compares the observed synthetic outputs with the retained fixture
without rewriting its historical timestamp. A source mismatch fails before that
source is compiled. This manual probe is separate from the normal repository
validation suite; passing schema/fixture checks does not execute a framework.

## Proposed handoffs and remaining work

| Consumer and current owners | Concrete input | Remaining disposition or evidence |
| --- | --- | --- |
| #25 — CompleteDotTech / Mattycodes69 | Three pinned evaluation/telemetry slices extend the existing candidate comparison | Review the bounded coverage; other framework hooks and managed offerings remain unreviewed |
| #35 — appletechie / PUSHINGSQUARES | Producer-specific capture, data-bearing metadata, and initialization/queue boundaries | Accept/narrow controls for the selected data boundary; no new permission, retention or universal privacy claim |
| #36 — appletechie / PUSHINGSQUARES | Distinct orchestration, judge, execution-record and host-allocation mechanisms; missing-metric counterexample | Adopt/narrow the input/completeness checks; choose real dataset, judge, criteria, placement and authorized tool effects before execution |
| #38 — appletechie / PUSHINGSQUARES | Effective producer controls and destination/delivery semantics | Adopt/narrow monitoring fields; obtain actual collector/configuration/queue evidence for a chosen deployment |
| #40 — zwright8 / tynamite | Evidence that one framework-wide telemetry/evaluation boolean cannot express these conditions | Decide any versioned field/rule representation; frozen v1 remains unchanged |

No receiving-owner acceptance is supplied by this note. Existing assignees,
native relationships, Project fields, #59 ledgers, catalog proposals and pricebooks
are unaffected. These findings do not settle #25/#35/#36/#38 in their entirety.

## Primary source register

All entries were accessed on **2026-10-18**. Primary documentation/source code;
source-checked/unverified, except for the explicitly isolated synthetic probes.
Revision abbreviations in prose expand to the full immutable URL in each row.
All named runtime/package versions are as inspected, not a latest-version claim.

| ID | Publisher / immutable source | Claim scope |
| --- | --- | --- |
| FET-01 | OpenAI, [tracing guide](https://github.com/openai/openai-agents-python/blob/17d994bd3045dae71acda676a4ef4762ed8ecd94/docs/tracing.md) | Defaults, disable/content controls, processor replacement and buffered data |
| FET-02 | OpenAI, [provider setup](https://github.com/openai/openai-agents-python/blob/17d994bd3045dae71acda676a4ef4762ed8ecd94/src/agents/tracing/setup.py), [tracing API](https://github.com/openai/openai-agents-python/blob/17d994bd3045dae71acda676a4ef4762ed8ecd94/src/agents/tracing/__init__.py) | Lazy initialization and processor API |
| FET-03 | OpenAI, [testing guide](https://github.com/openai/openai-agents-python/blob/17d994bd3045dae71acda676a4ef4762ed8ecd94/docs/testing.md) | Scripted SDK boundary and limitations |
| FET-04 | CrewAI, [annotated release tag](https://api.github.com/repos/crewAIInc/crewAI/git/tags/bacf4ef3bd74fdcb956a8f2490ce910f0716ddf9), [package metadata](https://github.com/crewAIInc/crewAI/blob/eb15c66cef12073d8d06d6942eecc35e7fd6c783/lib/crewai/pyproject.toml) | Release and core/CLI pins |
| FET-05 | CrewAI, [versioned telemetry guide](https://github.com/crewAIInc/crewAI/blob/eb15c66cef12073d8d06d6942eecc35e7fd6c783/docs/v1.15.28/en/telemetry.mdx) | Metadata, optional content sharing and documented control scope |
| FET-06 | CrewAI, [core telemetry source](https://github.com/crewAIInc/crewAI/blob/eb15c66cef12073d8d06d6942eecc35e7fd6c783/lib/crewai-core/src/crewai_core/telemetry.py) | Exact disable-flag parser and checks |
| FET-07 | CrewAI, [telemetry source](https://github.com/crewAIInc/crewAI/blob/eb15c66cef12073d8d06d6942eecc35e7fd6c783/lib/crewai/src/crewai/telemetry/telemetry.py), [constants](https://github.com/crewAIInc/crewAI/blob/eb15c66cef12073d8d06d6942eecc35e7fd6c783/lib/crewai/src/crewai/telemetry/constants.py) | Owned provider, endpoint and data fields |
| FET-08 | CrewAI, [versioned testing guide](https://github.com/crewAIInc/crewAI/blob/eb15c66cef12073d8d06d6942eecc35e7fd6c783/docs/v1.15.28/en/concepts/testing.mdx), [test CLI wrapper](https://github.com/crewAIInc/crewAI/blob/eb15c66cef12073d8d06d6942eecc35e7fd6c783/lib/cli/src/crewai_cli/evaluate_crew.py) | Repeated crew execution and invocation boundary |
| FET-09 | CrewAI, [AgentEvaluator](https://github.com/crewAIInc/crewAI/blob/eb15c66cef12073d8d06d6942eecc35e7fd6c783/lib/crewai/src/crewai/experimental/evaluation/agent_evaluator.py), [ExperimentRunner](https://github.com/crewAIInc/crewAI/blob/eb15c66cef12073d8d06d6942eecc35e7fd6c783/lib/crewai/src/crewai/experimental/evaluation/experiment/runner.py) | Event hooks, input cases and metric-intersection predicate |
| FET-10 | CrewAI, [experimental testing helper](https://github.com/crewAIInc/crewAI/blob/eb15c66cef12073d8d06d6942eecc35e7fd6c783/lib/crewai/src/crewai/experimental/evaluation/testing.py) | Baseline regression and missing-case warning |
| FET-11 | Agno, [Agent definition](https://github.com/agno-agi/agno/blob/4c969bc5fd88c3b1e6e7d3aa470ba0cd19252a8a/libs/agno/agno/agent/agent.py), [environment override](https://github.com/agno-agi/agno/blob/4c969bc5fd88c3b1e6e7d3aa470ba0cd19252a8a/libs/agno/agno/agent/_init.py), [Agent telemetry](https://github.com/agno-agi/agno/blob/4c969bc5fd88c3b1e6e7d3aa470ba0cd19252a8a/libs/agno/agno/agent/_telemetry.py) | Agent default, override and payload |
| FET-12 | Agno, [API dispatcher](https://github.com/agno-agi/agno/blob/4c969bc5fd88c3b1e6e7d3aa470ba0cd19252a8a/libs/agno/agno/api/api.py), [settings](https://github.com/agno-agi/agno/blob/4c969bc5fd88c3b1e6e7d3aa470ba0cd19252a8a/libs/agno/agno/api/settings.py) | Destination, background queue and delivery limits |
| FET-13 | Agno, [AccuracyEval](https://github.com/agno-agi/agno/blob/4c969bc5fd88c3b1e6e7d3aa470ba0cd19252a8a/libs/agno/agno/eval/accuracy.py) | Judge construction/rubric and evaluator telemetry |
| FET-14 | Agno, [ReliabilityEval](https://github.com/agno-agi/agno/blob/4c969bc5fd88c3b1e6e7d3aa470ba0cd19252a8a/libs/agno/agno/eval/reliability.py) | Execution expectations, matching and evaluator telemetry |
| FET-15 | Agno, [PerformanceEval](https://github.com/agno-agi/agno/blob/4c969bc5fd88c3b1e6e7d3aa470ba0cd19252a8a/libs/agno/agno/eval/performance.py) | Function timing, traced memory and evaluator telemetry |
| FET-16 | Agno, [eval helpers](https://github.com/agno-agi/agno/blob/4c969bc5fd88c3b1e6e7d3aa470ba0cd19252a8a/libs/agno/agno/eval/utils.py), [eval API](https://github.com/agno-agi/agno/blob/4c969bc5fd88c3b1e6e7d3aa470ba0cd19252a8a/libs/agno/agno/api/evals.py) | Independent helper/enqueue path |
| FET-17 | Agno, [release ref](https://api.github.com/repos/agno-agi/agno/git/ref/tags/v3.1.3), [package metadata](https://github.com/agno-agi/agno/blob/4c969bc5fd88c3b1e6e7d3aa470ba0cd19252a8a/libs/agno/pyproject.toml) | Version/revision identity |
