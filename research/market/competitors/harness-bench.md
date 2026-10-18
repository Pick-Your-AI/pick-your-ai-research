# Harness Bench — competitor profile

## 2026-10-18 review reconciliation

The [current fourteen-profile review](README.md#2026-10-18-current-profile-review)
retains paper v2 and site-suite release identities separately.
Accepted [#60](../rights-validation.md) distinguishes the licensed paper from
the separate repository task/code/trajectory collection: the bounded root check
found no repository-wide grant, not that every nested file lacks a licence.
That unestablished reuse stays excluded. Historical “no build save/share”
wording describes the inspected surface, not a universal absence claim.
[#62](../benchmark-validation.md) comparability and reproducibility limits
remain; no task, benchmark or result reconstruction ran here.

## Historical profile retained

The following dated record is unchanged; current interpretation is above.


Status: draft for owner review ([#50](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/50)). Entity ID: `harness-bench`. Classification: Benchmark provider, Open-source integration candidate (analyst judgement). Evidence classes are defined in the [index](README.md#evidence-classes).

| Field | Value |
| --- | --- |
| Product | Harness Bench model-harness benchmark (site, leaderboard, repository, paper) |
| Operator | Harness Bench team; repository under the Qihoo360 GitHub organization |
| URLs | [site](https://www.harness-bench.ai/), [repository](https://github.com/Qihoo360/harness-bench), [arXiv abstract](https://arxiv.org/abs/2605.27922) |
| Access date | 2026-10-16 |
| Version / revision | Repository `main` head `b8d8963` (2026-10-09), no tagged releases; arXiv v2 (revised 2026-10-15) |
| Access tier observed | Public site, public repository metadata via GitHub API, arXiv abstract page; nothing executed |
| robots.txt | harness-bench.ai serves no robots.txt (HTML fallback); arXiv allows `/abs` with crawl delay |

## Workflow

Harness Bench is not a selection tool. Its user workflow is reading results.

| Stage | Finding | Class | Source |
| --- | --- | --- | --- |
| Inputs | None from the user; the reader browses categories, tasks and a leaderboard | Observed | [site](https://www.harness-bench.ai/) |
| Constraints | Fixed by the benchmark: shared task inputs, 200K-token context threshold, 150-turn limit, recorded token use and API cost | Documented | [site](https://www.harness-bench.ai/) |
| Selection logic | None; results are reported per model × harness pairing (7 harnesses × 10 model backends on the general suite) | Documented | [site](https://www.harness-bench.ai/) |
| Explanation | Key findings, e.g. "No Harness Is Best on Every Model" and the gap between ≥0.80 partial credit and full credit | Observed (page content); results are publisher measurements, not reproduced | [site](https://www.harness-bench.ai/) |
| Save/share/export | Repository contains `catalog`, `suites`, `tasks`, `dashboard` directories and `CITATION.cff`; no build save/share | Observed (repository tree) | [repository](https://github.com/Qihoo360/harness-bench) |

## Architecture and data

- Tasks are reconstructed as sandboxed workspaces from "de-identified user logs, public workflows, and resource collections"; hidden task-specific oracles score final artifacts with no LLM judge. Documented, [site](https://www.harness-bench.ai/).
- Source conflict (retained from the prior profile): the site describes 300 tasks (274 general, 26 multimodal) and 20,454 runs; the arXiv v2 abstract describes 106 tasks and 5,194 trajectories. Record them as separate releases; see [benchmark validation](../benchmark-validation.md).
- Freshness: repository pushed 2026-10-11; site and paper carry no shared release identifier. Observed.

## Commercial access, code licence and data rights

| Layer | Finding | Class | Source |
| --- | --- | --- | --- |
| (a) Commercial access | Free public site and repository; no paid tier found | Observed (no pricing page found; not proof of absence) | [site](https://www.harness-bench.ai/) |
| (b) Code licence | `gh api repos/Qihoo360/harness-bench/license` returned 404; repository metadata `license: null`. No licence grant | Observed | [repository](https://github.com/Qihoo360/harness-bench) |
| (c) Data reuse | Paper is CC BY 4.0 (arXiv licence link). Repository tasks, trajectories and catalogue carry no licence | Observed | [arXiv](https://arxiv.org/abs/2605.27922) |

Historical comparison with merged [PR #82](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/82): display only results and text published in the paper, attributed and pinned to v2; repository content not reusable. This profile agrees.

## Counterexample

- **Suffices (hypothesis):** a team that has already chosen a model and must pick a coding-agent harness for repository or operations work can read the per-model harness results directly. Pick Your AI adds nothing for that narrow question unless it reuses these results.
- **Falls short (hypothesis):** it takes no user constraints, covers seven harnesses and ten backends, and does not address hardware, retrieval, hosting or cost for the user's workload. It is evidence for #36, not a substitute for a configuration decision.

## Matrix consistency

Historical comparison with merged [PR #87](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/87): `benchmarks` and `harness_eval` Documented; `saved`, `share`, `export`, `model_versions` Unknown. Agrees. The repository tree is a code artifact, not a build export.

## Open questions and routing

- #36/#62: reproducibility, contamination and which release (paper v2 or site 300-task suite) a citation uses.
- #41/#60: request licence clarification before any task reuse.
