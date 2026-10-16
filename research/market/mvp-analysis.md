# MVP alternatives

Status: recommendation for validation only, not implementation approval.

Ratings are analyst judgements based on the catalog and feasibility notes. User value and monetization remain hypotheses; no implementation effort or delivery time is estimated.

| Approach | User value hypothesis | Differentiation | Data availability | Feasibility / research | Integration / maintenance | Monetization | Time-to-value hypothesis |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Model-first | Quick model/provider shortlist | Low versus AA/OpenRouter/BenchLM | Relatively accessible, terms vary | Bounded but task-quality validation needed | Moderate, rapidly changing metadata | Unproven, many free substitutes | Shortest comparison flow |
| Hardware-first | Avoid failed local installs | Low–medium versus llmfit/ModelFit | Metadata exists; performance sparse | Runtime measurements needed | Hardware/runtime matrix expensive | Referral possible, conflict risk | Fast when hardware known |
| Workload-first | Reduce expertise required | Medium hypothesis, Flocci counterexample | Intent-to-quality evidence sparse | Requires demand and recommendation tests | Broad integrations create maintenance | Unproven | Fast interface, slower trusted answer |
| Cost-first | Avoid cost surprises | Low for list prices; potential in uncertainty | Prices available, workload inputs missing | Full bill models and scenario validation | High freshness burden | Potential qualified referrals | Depends on user supplying workloads |
| End-to-end stack | Coordinate every tier | Potentially higher, unproven | Fragmented and rights-constrained | Very broad research burden | Highest compatibility surface | Team/enterprise hypothesis | Slowest credible coverage |
| Hybrid bounded workflow | Explain one local/API decision with a shareable record | Medium hypothesis | Reuse a small rights-cleared subset | Testable scope; still needs real measurements | Constrained adapters and explicit unknowns | Test team artifact value | Faster credible learning than full stack |

Recommended next validation: a hybrid local-versus-API inference decision for a narrowly defined workload, carrying explicit context/concurrency, runtime, evidence date, uncertainty and a shareable versioned decision record. Reuse model and hardware evidence where licensed. Keep retrieval, agents and fine-tuning visible as optional future requirements; do not pretend the MVP covers them.

Minimum data: workload constraints (#2), deployment preference (#3), identified model/provider (#5/#6), context policy (#7), hardware/runtime (#10/#11), dated cost units (#39), provenance (#41), versioned selection and rule semantics (#40/#42). Missing performance or rights must surface as unknown, not a compatibility pass.

Validation gates: confirm recurring user pain versus existing tools; reconcile direct substitute flows; verify data rights; demonstrate acceptable sizing/cost uncertainty on pinned examples; obtain owner acceptance of the record. A failed gate calls for narrowing, partnership or stopping, not adding features. No numeric product success threshold is claimed approved; the coordinator must set thresholds before experiments.
