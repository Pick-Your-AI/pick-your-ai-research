# Consumer integration handoff

Snapshot: 2026-10-18. Refs #40, #41, #39, #42. This is an index of existing artifacts and gates, not a new service contract or an acceptance receipt. Android, Apple and website consumers should record the exact research commit they consume; leaderboard metrics retain their own contract and do not confer research acceptance.

## Immutable baseline

The inspected research revision is [`4addb4d45d3eadb4598262532823634980b8a1b5`](https://github.com/Pick-Your-AI/pick-your-ai-research/tree/4addb4d45d3eadb4598262532823634980b8a1b5). Use one revision consistently rather than mixing schemas, rules and examples from changing branches.

| Artifact at that revision | Use and boundary |
| --- | --- |
| [Frozen v1 package](https://github.com/Pick-Your-AI/pick-your-ai-research/tree/4addb4d45d3eadb4598262532823634980b8a1b5/contracts/v1) | Contract version `1.0.0`; schemas, generators, baseline rules, examples and reference evaluator travel together |
| [Import manifest](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/4addb4d45d3eadb4598262532823634980b8a1b5/contracts/v1/IMPORT_MANIFEST.json) | SHA-256 hashes for the 43 imported files; adoption metadata explains relocated paths |
| [OpenAPI reference](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/4addb4d45d3eadb4598262532823634980b8a1b5/contracts/v1/api/openapi.yaml) | Relative server `/v1` describes the interface. It supplies no deployed host, credentials, service availability or integration acceptance |
| [Synthetic examples](https://github.com/Pick-Your-AI/pick-your-ai-research/tree/4addb4d45d3eadb4598262532823634980b8a1b5/contracts/v1/examples) | Parser/fixture work only; these are not vendor facts, production catalogs or benchmark results |
| [Research proposals](https://github.com/Pick-Your-AI/pick-your-ai-research/tree/4addb4d45d3eadb4598262532823634980b8a1b5/catalog/proposals) and [pricebooks](https://github.com/Pick-Your-AI/pick-your-ai-research/tree/4addb4d45d3eadb4598262532823634980b8a1b5/pricing/proposals) | Dated, scoped research intake. Publication, source-specific rights and current quote eligibility remain separate decisions |

Schema `$id` values under `schemas.ai-builder.example` are local identifiers, not network endpoints. Follow [adoption limitations](../contracts/v1/ADOPTION.md). Preserve frozen bytes; new fields and rule behavior go through a separately reviewed version.

## Semantics consumers must keep distinct

| Concern | Existing evidence and implementation boundary |
| --- | --- |
| Compatibility | v1's reference evaluator is illustrative. Its baseline can fail membership checks on incomplete lists and uses build-level mode gates. [#40's record](../research/T0-configuration/component-schema-compatibility.md) proposes completeness-aware outcomes and component-level modes; it has not released a replacement ruleset |
| Migration | [#134](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/134) added test-only projections under `x_t0_*`. They consume normalized synthetic inputs, not arbitrary real builds or source evidence; they do not constitute a v1.1 reader |
| Outcomes | `pass/fail/unknown/skipped` and fixed `info/warning/error` severity are separate axes. Neither a passing error-severity rule nor an unknown outcome is a verified compatibility claim |
| Evidence | [Merged #127 mapping](../research/T0-configuration/catalog-data-sources.md#mapping-evidence-labels-to-frozen-v1): source-checked-only new claims use `unverified`; historical `verified` values do not establish independent reproduction. [T4 receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/41#issuecomment-6242626857) accepts that interface, not every consumer handoff |
| Freshness | No invented TTL. Preserve capture dates and selected revisions. The [#137 price-policy supplement](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/137) is a merged proposal pending scoped owner acceptance; it does not make old rates current or decide default currency |
| Cost | #39 retains currency, units, applicability and uncovered-meter decisions. Missing costs are not zero; mixed currencies cannot be summed without an accepted conversion policy. #113/#121 remain proposed research; no service implementation follows from their calculator |
| Saved/shared builds | [#114](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/114) remains a draft explicitly held until #40 is complete. Partial #40 merges do not release that hold or accept retention/sharing semantics |
| Rights | [#60 source-by-use inventory](../research/market/rights-validation.md) controls the evidenced uses. Schema validity, a source URL and a checksum grant no redistribution rights |

## Remaining receiving gates

- **#40:** @tynamite/@zwright8 and affected owners retain next-version schema, rule, migration and consumer decisions. Accepted routing/worked examples and a passing prototype do not fulfill the remaining handoffs.
- **#41/#39:** @tynamite/@PUSHINGSQUARES retain #41 policy acceptance; @appletechie/@PUSHINGSQUARES retain #39 cost decisions and receiving dispositions. The price supplement is reviewable at the pinned revision above.
- **#111:** [mobile migration guidance](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/111) still has the explicit maintainer no-merge hold and independent mobile receiving-review gap. The T0 review explicitly left mobile review to others. Companion mobile PR merges do not satisfy this research gate.
- **#121:** [T6 consolidation](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/121) retains @appletechie's change request. Corrections and re-review evidence are posted; the reviewer's disposition remains necessary. Keep #113/#115/#116/#118/#120 until their unique findings are preserved after the agreed #121-first sequence.
- **#83:** [benchmark desk analysis](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/83) now targets main and has one renewed approval, but @appletechie's change request and explicitly withheld #36/#39 receiving acceptance remain. No replication is claimed.

Refresh these live gates before integration or merge. This snapshot does not appoint owners, supply missing service infrastructure, or change issue/Project completion. A consumer receipt should identify the immutable research revision, consumed artifacts and accepted scope, test evidence, unresolved conditions, and the receiving issue/owner.

## Reproduce repository checks

Run the complete [submission validation commands](RESEARCH_WORKFLOW.md#validation) with Python 3.12. They check frozen import hashes, generator consistency, schemas, references and synthetic semantics. They do not fetch sources, establish rights, run model benchmarks, deploy `/v1`, or validate a client's live integration.
