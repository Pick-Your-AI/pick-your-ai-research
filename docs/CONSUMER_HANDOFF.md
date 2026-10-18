# Consumer integration handoff

Delivery readback: 2026-10-18. Refs #40, #41, #39, #42. This is an index of existing artifacts and gates, not a new service contract or an acceptance receipt. Android, Apple and website consumers should record the exact research commit they consume; leaderboard metrics retain their own contract and do not confer research acceptance.

The [earlier open-PR snapshot](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/637957347c54d215f9ef27f2af122a5b9129d0fd/docs/CONSUMER_HANDOFF.md) and revision-specific review records remain historical evidence. The delivered records below update that snapshot's open-PR statuses; receiving requirements still follow the live issues and scoped owner receipts.

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
| Cost | #39 retains currency, units, applicability and uncovered-meter decisions. Missing costs are not zero; mixed currencies cannot be summed without an accepted conversion policy. #121 delivered the research calculator; its merge supplies no service implementation or remaining receiving acceptance |
| Saved/shared builds | [#114](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/114) delivered the partial proposal at [649f5870](https://github.com/Pick-Your-AI/pick-your-ai-research/commit/649f5870e9729ec1aaf1b5f07e9290ce0f777833). #42 retains its native #40 prerequisite and pending SB/CD, retention, sharing and receiving-owner decisions |
| Rights | [#60 source-by-use inventory](../research/market/rights-validation.md) controls the evidenced uses. Schema validity, a source URL and a checksum grant no redistribution rights |

## Delivery status and remaining receiving gates

- **#40:** @tynamite/@zwright8 and affected owners retain next-version schema, rule, migration and consumer decisions. Accepted routing/worked examples and a passing prototype do not fulfill the remaining handoffs.
- **#41/#39:** @tynamite/@PUSHINGSQUARES retain #41 policy acceptance; @appletechie/@PUSHINGSQUARES retain #39 cost decisions and receiving dispositions. The price supplement is reviewable at the pinned revision above.
- **#111:** [mobile migration guidance](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/111) merged at [da3c6045](https://github.com/Pick-Your-AI/pick-your-ai-research/commit/da3c6045f84260506bd326bb24ddfa8a7e6a23e8). Its delivered guidance preserves the [canonical receiving paths](../prompts/mobile/MIGRATION.md); application implementation and receiving acceptance still require their own evidence.
- **#121:** [T6 consolidation](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/121) merged at [913c9b1e](https://github.com/Pick-Your-AI/pick-your-ai-research/commit/913c9b1e974aff3b1a3a22a8ed339b99fa8e95b4). The original change requests, sibling PRs and later reconciliation records retain their revision-specific evidence. Individual T6 issue criteria and scoped receiving dispositions still apply.
- **#83:** [benchmark desk analysis](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/83) merged at [51a5c552](https://github.com/Pick-Your-AI/pick-your-ai-research/commit/51a5c552bd8dbf6fa6a11d07d6772a3ce9d305b6). Desk/source analysis is separate from benchmark replication and #36/#39 receiving acceptance.

Refresh these live gates before integration or merge. This snapshot does not appoint owners, supply missing service infrastructure, or change issue/Project completion. A consumer receipt should identify the immutable research revision, consumed artifacts and accepted scope, test evidence, unresolved conditions, and the receiving issue/owner.

## Reproduce repository checks

Run the complete [submission validation commands](RESEARCH_WORKFLOW.md#validation) with Python 3.12. They check frozen import hashes, generator consistency, schemas, references and synthetic semantics. They do not fetch sources, establish rights, run model benchmarks, deploy `/v1`, or validate a client's live integration.
