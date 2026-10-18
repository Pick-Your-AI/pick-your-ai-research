# Total-memory setup validation — 2026-10-18

Branch `codex/issue61-total-memory-setup`, base main
`a05035c1faeaf573b0a0dc8db83e0a09551817fe`. The setup remains a proposed
managed-buffer snapshot experiment, not a qualified native GPU run or a
whole-process/peak calibration result.

Validation environment: bundled Python **3.12.14** on Windows/PowerShell.
Installed `requirements-research.txt` with `--target $TASK_VALIDATION_DEPS` and
set PYTHONPATH to that isolated task dependency directory. Existing-target
warnings did not replace existing packages. No CUDA package or driver changed.

| Required command / check | Result |
| --- | --- |
| `python -m pip install -r requirements-research.txt --target $TASK_VALIDATION_DEPS` | Passed |
| `python -m unittest discover -s contracts/v1/tests -v` | 21 passed |
| `python -m unittest discover -s tests -v` | 249 passed; final guarded version rerun with `-q` |
| `python scripts/validate_research.py` | 74 catalog proposals, 3 pricebooks and external evidence metadata passed |
| `python scripts/validate_market_research.py` | 33 entities, 1,584 cells and 20 issues passed |
| `python scripts/validate_handoff_audit.py` | 101 rows / 98 declared pairs passed; ledgers unchanged |
| `python prompts/mobile/validate_prompts.py` | 2 Projects, 258 issues, 36 epic prompts, 906 criteria and 880 steps passed |
| `python scripts/mr09_total_memory_setup.py` | Prepared, execution disabled; runtime observations and pairs zero |
| `git diff --check` and local protocol targets | Passed |

Ten new tests use synthetic future log records and the real CPU-only estimate.
They check scoped metric/no_alloc rejection, per-device selection, integer-MiB
rounding, interval/error denominators, effective-config and allowance drift,
retained execution gates, fabricated-pair rejection, output checksums and strict
JSON duplicate/non-finite/overflow rejection. Synthetic logs remain only in the
test module; none is committed as a runtime observation. Tests never run a GPU,
call a remote endpoint or download a model.

Actual preparation is recorded separately: pinned estimator version/help and
one successful CPU estimation of the locally hash/size-verified real GGUF.
Native runtime archives/driver, allocation-cap enforcement and actual allocated
buffer exporter remain unqualified. Prior dense/GM1 observations and instruments
are unchanged, and no new tolerance or human acceptance is claimed.

Automation checks record shape, consistency and arithmetic, not physical GPU
execution, process-wide peak completeness, source rights/freshness or estimator
accuracy. #61 co-owners, #7/#10/#11 receivers and coordinator retain those reviews.
The cleanup receipt covers only this task's external model/binary/source files;
no weights or large artifacts enter Git.
