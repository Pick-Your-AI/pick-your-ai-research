# Research and application delivery roadmap

Phases describe order of work, not dates. No deadlines have been set. The first three
phases below govern research; application release gates are recorded separately.

## Phase 1: Foundation

- T0 requirements: workload categories, deployment modes.
- Shared contract (`contracts/v1/`, [CONTRACT_MAPPING.md](CONTRACT_MAPPING.md)) adopted and reviewed by all tier owners.
- Source standards and research method ([RESEARCH_METHOD.md](RESEARCH_METHOD.md)).

## Phase 2: Parallel research

- T1, T2, T3, T4 and T5 proceed in parallel wherever prerequisites permit, producing proposals that pass the contract validation.
- T6 (guardrails, evaluation, deployment, monitoring, cost) starts in parallel and does not wait for the other tiers to finish.

## Phase 3: Integration

- Compatibility validation across tiers, evaluation methodology, deployment feasibility, cost modelling.
- Promote validated rules into product requirements ([governance.md](governance.md)).

Execution prerequisites between issues are tracked with GitHub's native blocking relationships; compatibility feedback loops are not.

## Apple application delivery

The [Apple/iOS plan](APPLE_DELIVERY_PLAN.md) uses the Android plan's **1 program →
18 epics → 110 feature/task work packages → subtasks** hierarchy. It supersedes the
earlier 19-workstream Apple outline with a documented coverage mapping. The plan
does not create a GitHub Project, assign work or establish completion.

| Phase | Gate |
| --- | --- |
| Foundation | Scope and architecture decisions, reproducible native build, CI and contract conformance |
| Synthetic preview alpha | Core client journeys, persistence and failure handling work with explicit fixture labels |
| Reviewed real-data beta | Supported path uses reviewed, rights-cleared published data; included services and privacy flows work; TestFlight feedback triaged |
| Production launch | Device, accessibility, security and release qualification; support and operations ready; App Store review and release approval; installed-release verification |
| Selected expansion | Explicit decisions and acceptance gates for alerts, monetization, community, advanced recommendations, execution or additional platforms |

Design, security, persistence and testing run throughout. Shared catalog/backend work
is reused across Apple, Android and web; existing issues keep their owners and
hierarchy. Implementation can proceed against fixtures while evidence is incomplete,
but fixture success and merged research do not establish production readiness.
