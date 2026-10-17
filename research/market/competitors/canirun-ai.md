# CanIRun.ai — device-first model discovery

Draft intake, accessed 2026-10-16. Research: #48/#49/#50; scenario validation: #66. Live GitHub assignees remain authoritative.

## Source and boundary

Primary sources: [device directory](https://www.canirun.ai/devices) (`src-canirun-ai`) and the [`midudev/canirun.ai` repository](https://github.com/midudev/canirun.ai) (`src-canirun-ai-repo`), both accessed 2026-10-16. The repository's homepage field is `https://canirun.ai` and its owner is the individual GitHub account midudev (Miguel Ángel Durán), so the operator is that maintainer; no legal entity is named. Software version unpinned (default branch pushed 2026-10-16T23:27Z). robots.txt allows all paths except `/api/` and `/og/`; a later automated re-check of the site returned HTTP 403 (bot challenge) and was not bypassed. Relationships to similarly named services remain unknown. Keep `canirun-ai` distinct from `canrun` (canrunllm.com) and `canitrun` (canitrun.dev).

## Workflow evidence

| Stage | Finding | Evidence class |
| --- | --- | --- |
| Input | Device directory with search and hardware categories | Observed static page structure; interaction untested |
| Recommendation | Links offer local model recommendations for individual devices | Vendor claim; results and accuracy untested |
| Memory | Entries display device memory capacities | Documented values; not verified specifications or measured model requirements |
| Detection and recommendation (product scope) | Repository README: the browser detects CPU, RAM and GPU, then recommends open models to run locally per use case (coding, chat, reasoning, vision) | Vendor claim (README); untested |
| Explanation, save/share/export | Unknown from this inspection | Unverified; no absence inferred |

Matrix: `hardware_fit`, `hardware_catalog`, `vram_ram` are Documented; the other 45 dimensions are Unknown. A directory entry does not satisfy the bounded execution tests in `features.json`.

## Commercial access, code and data rights

The directory was publicly readable without an account. Code licence: the public repository has no licence file (GitHub API `license: null`, checked 2026-10-16), so no code or data reuse grant is established. Pricing, paid access, data licence, API availability and commercial display/redistribution permission remain unknown. No dataset was downloaded or promoted to catalog proposals. #41/#60 must review rights before downstream reuse.

## Counterexample and limits

Hypothesis: hardware-detected local model selection may already meet a user's narrow selection need; per its README this is a direct-substitute candidate for single-device local model choice, comparable to ModelFit/llmfit. Matrix follow-up for #49: the `vram_ram` cell's current basis is device memory capacity, which is not a model memory requirement; it should be re-based on product evidence or set Unknown. Test alongside ModelFit/llmfit under #66 before treating it as a substitute. Full-stack composition, performance, deployment and reusable configuration export are unverified. This intake is neither an independent measurement nor an accepted differentiation decision.

## Review checklist and routing

- [ ] #48: confirm identity boundary and partial-competitor classification.
- [ ] #49: review the three documentary cells and retain unknowns until sourced.
- [ ] #50: review this profile and its inclusion within the 10–15 profile target.
- [ ] #66: run the shared public scenario and contradictory constraints; record inability to express an input without inferring universal lack of support. Preserve the existing test order and acceptance gates.
- [ ] #6/#10: assess model and device recommendations against pinned inputs before accepting technical implications.
- [ ] #41/#60: establish operator, methodology, freshness and reuse rights if proposed for ingestion.

No new blocking relationships or completion claims are introduced. Consumer acceptance remains pending.
