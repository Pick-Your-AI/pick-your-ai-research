# CanIRun.ai — device-first model discovery

Draft intake, accessed 2026-10-16. Research: #48/#49/#50; scenario validation: #66. Live GitHub assignees remain authoritative.

## Source and boundary

Primary source: [device directory](https://www.canirun.ai/devices), publisher CanIRun.ai, source ID `src-canirun-ai`. Public web text retrieved on 2026-10-16; software version unpinned, global website, plan entitlements untested. Legal operator and relationships to similarly named services are unknown. Keep `canirun-ai` distinct from `canrun` (canrunllm.com) and `canitrun` (canitrun.dev).

## Workflow evidence

| Stage | Finding | Evidence class |
| --- | --- | --- |
| Input | Device directory with search and hardware categories | Observed static page structure; interaction untested |
| Recommendation | Links offer local model recommendations for individual devices | Vendor claim; results and accuracy untested |
| Memory | Entries display device memory capacities | Documented values; not verified specifications or measured model requirements |
| Explanation, save/share/export | Unknown from this inspection | Unverified; no absence inferred |

Matrix: `hardware_fit`, `hardware_catalog`, `vram_ram` are Documented; the other 45 dimensions are Unknown. A directory entry does not satisfy the bounded execution tests in `features.json`.

## Commercial access, code and data rights

The directory was publicly readable without an account. Pricing, paid access, code licence, data licence, API availability and commercial display/redistribution permission remain unknown. No dataset was downloaded or promoted to catalog proposals. #41/#60 must review rights before downstream reuse.

## Counterexample and limits

Hypothesis: device-first local model selection may already meet a user's narrow selection need. Test alongside ModelFit/llmfit under #66 before treating it as a substitute. Full-stack composition, performance, deployment and reusable configuration export are unverified. This intake is neither an independent measurement nor an accepted differentiation decision.

## Review checklist and routing

- [ ] #48: confirm identity boundary and partial-competitor classification.
- [ ] #49: review the three documentary cells and retain unknowns until sourced.
- [ ] #50: review this profile and its inclusion within the 10–15 profile target.
- [ ] #66: run the shared public scenario and contradictory constraints; record inability to express an input without inferring universal lack of support. Preserve the existing test order and acceptance gates.
- [ ] #6/#10: assess model and device recommendations against pinned inputs before accepting technical implications.
- [ ] #41/#60: establish operator, methodology, freshness and reuse rights if proposed for ingestion.

No new blocking relationships or completion claims are introduced. Consumer acceptance remains pending.
