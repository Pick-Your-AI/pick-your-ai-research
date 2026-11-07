# Repository coverage snapshot

Refs [#509](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/509).
This is a reproducible baseline for the coverage-ledger proposal, not an accepted
definition of near-exhaustiveness. It counts existing local records; it does not
add entities, resolve model aliases or change the frozen builder contract.

[`repository-snapshot.json`](repository-snapshot.json) records:

- Proposal file counts for every canonical builder kind, including zero counts.
- Pricebook file and rate counts.
- The recorded competitor-by-feature matrix denominator and each existing status.
- SHA-256 hashes of the exact input bytes, including every counted proposal file.

The current inputs yield 124 catalog proposals across 19 of 29 builder kinds,
three pricebooks containing 14 rates, and 1,872 cells (39 products × 48 features):
121 Documented and 1,751 Unknown. Exercised and Unsupported both have zero cells.
A zero proposal count does not mean the kind lacks a research decision record;
the [contract mapping](../../docs/CONTRACT_MAPPING.md) covers all 29 kinds.
Proposal files are not deduplicated ecosystem entities. A Documented cell is not
an independently exercised capability, and Unknown is not Unsupported.

## Reproduce and update

From the repository root with the [research dependencies](../../requirements-research.txt):

```bash
python scripts/research_coverage.py
python scripts/research_coverage.py --check research/coverage/repository-snapshot.json
python -m unittest discover -s tests -p test_research_coverage.py -v
```

The first command emits deterministic JSON without a wall-clock timestamp or
network access. The check compares the complete rendered snapshot, including
input hashes: even source-only or whitespace changes are visible. The ordinary
repository test suite also checks this committed snapshot. After a deliberate
input change, regenerate and review the new counts and hashes:

```bash
python scripts/research_coverage.py > research/coverage/repository-snapshot.json
```

Missing, duplicate or unknown matrix cells fail instead of shrinking the
denominator. Unknown status names, duplicate product identities, unknown catalog
kinds and ambiguous JSON also fail. This report does not replace the schema,
reference, source or evidence checks in the [submission workflow](../../docs/RESEARCH_WORKFLOW.md).

## Unmeasured dimensions and routing

No global ecosystem denominator, entity deduplication, source freshness,
independent measurement, reviewer acceptance, publication eligibility or website
adoption is inferred from these counts. In particular, eligibility remains
unmeasured rather than zero or approved. The existing
[publication handoff](../../docs/PUBLICATION_ELIGIBILITY_HANDOFF.md) retains its own
dated scope and source-use decisions. This report does not refresh them.

Scope/inclusion rules and broader entity mapping remain research #509 decisions;
the existing [T1 inventory](../T1-model-selection/model-research-inventory.json)
and its source-integrity work remain separate. Benchmark and capacity evidence
remain with research #61/#62, customer evidence with #63, and the narrower
commercial-validation decision with [the market synthesis](../market/synthesis.md).
Website publication and implementation remain with its existing #15/#16/#24
work. No owner, live issue status, repository-placement decision or research
acceptance criterion changes here.
