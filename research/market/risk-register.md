# Risk and unresolved decision register

Status: draft. Each row has a concrete validation owner in the Project; no risk is closed by this document.

| Risk | Evidence / uncertainty | Impact | Next action / consumer |
| --- | --- | --- | --- |
| False differentiation | Flocci, ModelFit and llmfit overlap entry workflows | Product direction | Direct substitute test; MR-03 and MR-10 |
| No recurring paid demand | No interviews or conversion experiment | Business viability | Customer validation; MR-05, #2 |
| Data rights | BenchLM separates access and display permission | Ingestion/product release | Rights review; MR-08, #41 |
| Source/license ambiguity | Harness repository license endpoint absent; seed llmfit operator unknown | Integration | Verify publisher and rights before reuse |
| Benchmark version conflict | Harness paper abstract 106 versus site/repo 300 tasks | Incorrect comparison | Reconcile exact result release; #36 |
| Contamination / selection bias | Benchmark tasks may not represent target workloads | Ranking quality | Independent evaluation design; #36 |
| Memory and speed uncertainty | Context/cache/concurrency, topology, runtime | Failed installations / bad purchasing | Pinned measurement protocol; #10/#11 |
| Pricing drift / incomplete bills | List rates omit workload and operational cost | Cost advice | Price freshness validation; #39/#41 |
| Provider-specific behavior | Connector availability is insufficient | Runtime failure | Interoperability review; #16/#25/#27 |
| Monetization incentives | Affiliate and sponsorship models | User trust | Publish neutral ranking policy; MR-07 |
| Authenticated UX gap | PCPartPicker list inaccessible in current session | Incomplete reference study | Authorized walkthrough; MR-04 |
| Schema adoption | Resolved: PR #44 merged; PR #67 rebased onto `main` | None remaining | Use `docs/RESEARCH_WORKFLOW.md` for any catalog/pricebook proposals |

Owner decisions: approve customer recruitment/consent; define experiment success thresholds; resolve display/data licensing; accept or reject bounded MVP hypothesis; accept technical handoffs. No deadlines are invented.
