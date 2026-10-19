# Prospective H1 attempt admission

Refs [#61](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/61) and
[the #476 review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/476#pullrequestreview-5568342327).
This is the authoritative entry point for any **future** cohort using the fixed
H1 initialization kernel. It adds process fencing and prelaunch packet checks;
it records no new prediction, model observation, capacity measurement or
receiving acceptance.

## Preserve the captured cohort

The [2026-10-19 protocol](local-comparison-2026-10-19/protocol.md), prediction
freeze, source identities, raw captures and reports retain their original bytes
and chronology. Their launcher is `scripts/mr09_local_compare_run.py`, SHA-256
`6027d57b5d902955245defd19cbdf937be8b1b3a8b1cc7d6eefcea8e7b97c40a`.
Its historical CLI targets the already occupied dated cohort; its functions
also support the existing offline report. Preserve this file as the historical
kernel and offline verification dependency. Do not call its `run()` or CLI
directly for a future cohort, clear its occupied output paths, or modify its
captured hash to adopt these later controls.

Review found that the historical launcher checked output existence without an
exclusive reservation and could leave no attempt receipt on a prelaunch
exception. A CPU-only mocked witness reproduced both a missing admission-failure
record and two simultaneous mocked launches for one repetition. The historical
freeze also omitted the four delegated Python guard sources. Those findings do
not establish that concurrency, unrecorded model execution or source drift
occurred in the actual three recorded observations. They remain limitations of
the original admission/freeze closure; this later protocol does not backdate or
repair that historical closure.

## Prepare and review a distinct future freeze

Use a new, existing cohort directory inside the reviewed repository and a
separate task-owned temporary directory containing the pinned native runtime
artifacts. Have the source, preparation, effective controls and prediction
reviewed before invoking the launcher. This change creates no such cohort and
does not authorize a new hardware run or change the existing resource envelope.

The future `prediction-freeze.json` must hash all of these files:

| Required group | Exact contents |
| --- | --- |
| Launchers and guards | `scripts/mr09_local_compare_admission.py`, the unchanged `scripts/mr09_local_compare_run.py`, `scripts/mr09_preflight.py`, `scripts/mr09_native_capture.py`, `scripts/mr09_native_qualify.py`, `scripts/mr09_total_memory_setup.py` |
| Native source | `research/market/measurements/native/mr09_native_h1.cpp` and `mr09_quota.hpp` in that directory |
| Estimator package | All eight `package_sha256` entries in `estimator-source-preparation.json`: the package license, README, derivative patch, source manifest, preparation script and three native test sources |
| Cohort packet | `build.json`, `runtime-artifacts.json`, `protocol.md`, `estimator-source-preparation.json`, `estimator-windows-adaptation.json`, `estimator-profile.json`, `estimator-prediction.json`, `prediction-receipt.json`, `estimator-manifest.json`, `semantic-review.json` |

Every hash is checked against current local bytes before the historical kernel
is called. The package source manifest, preparation and build manifest must
agree; preparation, prediction and semantic-review candidate revisions must
match. The Windows adaptation must bind the original preparation source and
retain its adapted-source hash and actual diff. These identities preserve the
reviewable preparation record; the launcher does not reproduce the CPU build,
authenticate a review author, or turn a self-authored review JSON into approval.

The prediction must name the pinned SmolLM2 artifact, experimental estimator
identity `gguf-parser-go-v0.26.4+mr09-output.2-experimental` and upstream revision.
This maintained prospective identity follows the reviewed parser correction in
[#483](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/483). It requires
a separate future prediction and coherent preparation/build/source packet; the
captured `.1` prediction and its offline report retain their historical identity.
All 20 H1 profile fields are exact and typed:
for example, integer sequence capacity `1` cannot be replaced by `true` or
`1.0`. Declared controls and estimate placement must agree. The prediction must
contain the host plus CUDA0 estimate, complete nonnegative integer CUDA0 byte
terms, and the matching raw-output/aggregation receipt. Both inputs to the
graph/output maximum are checked. The receipt's successful CPU prediction must
finish before the freeze, and the freeze must declare integer zero prior model
observations. Hashes alone do not establish these semantic relationships.

After review, the future command is:

```sh
python scripts/mr09_local_compare_admission.py \
  --cohort-dir research/market/measurements/REVIEWED-NEW-H1-COHORT \
  --temporary-dir PATH-TO-EXISTING-PINNED-TASK-ARTIFACTS \
  --repetition 1
```

The placeholders intentionally refer to no existing run. Repetitions 2 and 3
use the same cohort and temporary artifacts, one at a time, only after the
preceding invocation completes successfully. The original artifact admission,
RTX 5070 Ti / driver 610.88 identity, fresh capacity screen, fixed native tuple,
allocation cap, graph refusal, child timeout and post-run telemetry remain in
the preserved kernel. No arbitrary command, model, profile or inference option
is added.

## Reservation and failure behavior

Before temporary-artifact validation, source admission, a driver query or any
child, the launcher exclusively creates and file-syncs
`H1-active-attempt.json`, followed by the repetition's `H1-rN-attempt.json`.
The cohort reservation prevents simultaneous attempts even when callers choose
different repetitions. An existing reservation, attempt, preflight or result
is preserved. Successful earlier outputs are eligible predecessors only when
their completed wrapper receipts bind the same freeze and exact output bytes;
historical outputs without those receipts cannot be adopted.

The attempt records its phase, source/freeze identities and terminal outcome.
The kernel still saves native output before post-run telemetry. The wrapper
releases its own cohort reservation only after the successful retained result
and its hash have been durably recorded in a completed attempt receipt.
Failure, interruption, disk-write failure, a changed reservation, or an
unfinished process leaves a blocking fence. No automatic retry or stale-lock
cleanup exists. A later investigator must preserve and review the complete
attempt and outcome before proposing any separate cohort; deleting the fence
to retry would defeat this protocol.

Persisted failures contain the phase and exception type, without exception
text, private paths, command arguments or payloads. The CLI likewise emits only
a fixed failure status and exception type. The Python API re-raises the
original exception for its caller. A pending `guarded_kernel` phase with
`native_status: not_recorded` cannot establish whether a child started: a
process may die after launch or after writing native output. Treat that state
as indeterminate and blocked.

Exclusive file creation and file `fsync` are tested across ordinary processes,
hard process exits and injected persistence failures. These controls do not
claim storage durability across hardware power loss on every filesystem. They
serialize this declared cohort, not unrelated cohorts or other applications;
capacity screens remain observations rather than device reservations.

## CPU-only verification

```sh
python -m unittest discover -s tests -p test_mr09_local_compare_admission.py -v
python -m unittest discover -s tests -p test_mr09_local_compare_run.py -v
```

The prospective tests copy the reviewed current source/package bytes and replay
only the historical prediction's numerical/control terms in a separately labeled
synthetic current-package packet. Synthetic preparation, build and review keys
and a tiny non-executable estimator stand-in carry no historical execution or
approval claim. The tests preserve every historical file, retain exact numeric
fixture terms, and reject mixed historical/current package identities or hashes.
They use tiny non-executable runtime/model stand-ins, explicit model/ledger pin
substitutions and mocked driver/preflight/native responses. They exercise the
real admission and result validators. Separate Python child processes prove the exclusive
claim and persistent fences after hard process exits; those witnesses cannot
invoke a model, estimator, GPU command or native binary. No synthetic fixture
is committed to the measurement directory or promoted as research evidence.
