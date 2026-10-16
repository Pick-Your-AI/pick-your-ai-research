# Proposed hosting compatibility rules

Issue: #9 · Contract review: #40 · Status: proposed / unverified · Version: 0.2.0

Evidence IDs refer to [hosting.md](../hosting.md), accessed 2026-10-16. These follow [the proposal template](../../../templates/rule-proposal.md). Documentation supports premises; no rule is an approved Ruleset or independently verified joint deployment. Examples are synthetic policy examples. Outcomes and severities are separate.

Each group below separates a constraint, an evidence diagnostic and an applicability diagnostic. Each has its own proposed rule ID and **fixed severity**, as required by v1; none changes severity when its outcome changes. A passing constraint with severity `error` does not constitute a failure; the evaluator can still emit a finding retaining that rule's severity. An unknown constraint is not a failure: the separate `warning` diagnostic explains the missing evidence. #40 still reviews the assertions and note-only inputs before adoption.

## t2-hosting-private-networking

- Participating kinds, roles, and JSON pointers: selected `hosting_platform` catalog `/spec/supports_private_networking`; hosting selection `/settings/network_isolation`; exact host version and service/region scope.
- Applicability condition: enabled host selection requests `network_isolation=private`. `air_gapped` requires a separate deployment assessment.
- Assertion and source evidence: require documented private-network capability for the scoped service. AWS VPC H15 and HF intra-region PrivateLink H14 support positive capability findings; neither proves a particular route, identity policy or full residency.
- Fixed rule/diagnostic clauses: `t2-hosting-private-networking` has severity `error` and tests the documented capability when private isolation is requested; `t2-hosting-private-networking-evidence` has severity `warning` and reports unresolved scoped capability evidence; `t2-hosting-private-networking-applicability` has severity `info` and reports whether this narrow private-capability check applies. The applicability diagnostic is `pass` for a known private request, `skipped` for known non-private requests, and `unknown` if the request is missing.
- Missing-data behavior (`unknown`) and proposed policy: omitted booleans are unknown, not false. `true` does not establish configured isolation or air-gapped operation.
- Explanation and remediation: name the service/region and missing capability/configuration; choose an evidenced private-capable host or obtain a deployment/network review in #37.
- Dependency edges and affected consumers: deployment mode ↔ host ↔ network plan; #3/#9/#27/#35/#37. No native blocker introduced.
- Passing example: a private request plus a scoped documented `true` gives constraint `pass` (fixed severity `error`); applicability is `pass/info` and the constraint does not fail. Network configuration still requires evidence.
- Failing example: private request plus explicitly evidenced `false` gives constraint `fail/error`.
- Unknown / non-applicable example: private request with absent evidence gives constraint `unknown` and evidence diagnostic `unknown/warning`; public isolation gives constraint `skipped` and applicability diagnostic `skipped/info`. An air-gap request remains outside this positive private-capability assertion.
- Version and migration impact: existing v1 pointers suffice for this narrow assertion; retain evidence scope and service version, invalidate on changes; no schema edit or final rule publication.

## t2-hosting-runpod-volume-locality

- Participating kinds, roles, and JSON pointers: `storage` `/spec/storage_type`, `/spec/region`, `/spec/hosting_ref`; `compute_profile` `/spec/region`, `/spec/hosting_ref`; selected IDs and the intended mount relationship. The latter relationship and serverless placement constraints are note-only inputs pending T2-C05.
- Applicability condition: the selected Runpod standard network volume will be directly mounted by a Pod or serverless worker; not an arbitrary remote object download.
- Assertion and source evidence: H21 documents location-constrained attachments and the Secure Cloud Pod limitation. A single serverless volume constrains worker placement to its datacenter; multiple volumes do not imply replication.
- Fixed rule/diagnostic clauses: `t2-hosting-runpod-volume-locality` has severity `error` and tests a proven direct-mount placement constraint; `t2-hosting-runpod-volume-locality-evidence` has severity `warning` and reports unresolved mount/location evidence; `t2-hosting-runpod-volume-locality-applicability` has severity `info` and reports whether this direct-mount check applies. The applicability diagnostic is `pass` for a known relevant Runpod mount, `skipped` for a known remote-download-only relationship, and `unknown` if the relationship is missing.
- Missing-data behavior (`unknown`) and proposed policy: missing datacenter, cloud type, placement guarantee or mount relationship gives unknown. Provider geographies cannot be compared by arbitrary free text.
- Explanation and remediation: co-locate supported compute and storage, use an evidenced supported attachment strategy, or choose separate storage; preserve data consistency and capacity questions.
- Dependency edges and affected consumers: #9/#10/#13/#15/#27/#28/#31/#37; #13/#28 retain ACL, retention and memory semantics.
- Passing example: evidenced Secure Cloud Pod and directly mounted standard volume both in `US-KS-2` gives locality-only constraint `pass` (fixed severity `error`); applicability is `pass/info` and no failure diagnostic is emitted. Current GPU stock remains unknown.
- Failing example: direct mount of a single `US-KS-2` volume to a worker pinned in another datacenter gives proposed constraint `fail/error`.
- Unknown / non-applicable example: worker placement unspecified gives constraint `unknown` and evidence diagnostic `unknown/warning`; a remote download with no direct mount gives constraint `skipped` and applicability diagnostic `skipped/info` for this mount assertion.
- Version and migration impact: #40 must review explicit mount/placement semantics before implementation. Preserve v1; do not infer mount edges merely because components share a build.

## t2-hosting-offering-membership

- Participating kinds, roles, and JSON pointers: host `/spec/regions`, `/spec/accelerator_refs`; selected hosting `/settings/region`; profile `/spec/hosting_ref`, `/spec/region`, `/spec/accelerator_ref`; deployment mode `/spec/allowed_regions`. Evidence completeness and account entitlement are note-only.
- Applicability condition: a particular region/device offering is being evaluated; API-only hidden hardware does not acquire a local device requirement.
- Assertion and source evidence: H02/H03/H05/H16/H18 show why region lists, price tables, quotas and current capacity are different facts. Positive scoped evidence can support an offering-presence assertion; a researched subset cannot establish absence.
- Fixed rule/diagnostic clauses: `t2-hosting-offering-membership` has severity `error` and tests scoped offering or validated allowed-region constraints; `t2-hosting-offering-membership-evidence` has severity `warning` and reports incomplete offering/completeness evidence, with quota/stock uncertainty explicitly separate from offering presence; `t2-hosting-offering-membership-applicability` has severity `info` and reports whether the requested region/device membership check applies. The applicability diagnostic is `pass` for a known explicit local offering request, `skipped` for provider-owned hidden hardware, and `unknown` if the request is unspecified.
- Missing-data behavior (`unknown`) and proposed policy: absent from an incomplete list means unknown. Published presence is not available quota, stock or a reserved allocation.
- Explanation and remediation: show requested location/device, evidence scope/date and unknown account capacity; obtain current authorized offer/quota evidence or select an evidenced alternative.
- Dependency edges and affected consumers: #3/#9/#10/#14/#15/#27/#31/#37/#39/#40; informational compatibility cycle, no delivery blocker.
- Passing example: a documented offering in the requested provider region gives offering-only constraint `pass` (fixed severity `error`); applicability is `pass/info` and no failure diagnostic is emitted. Stock remains separately unknown.
- Failing example: a canonical, explicitly allowed region set excludes the selected location, or an authoritative complete offering list explicitly excludes it, gives scoped constraint `fail/error`.
- Unknown / non-applicable example: the two-region researched host subset omits a third region, giving constraint `unknown` and evidence diagnostic `unknown/warning`; provider-owned API GPU selection gives constraint `skipped` and applicability diagnostic `skipped/info` for local accelerator membership.
- Version and migration impact: #40 must adopt evidence completeness and provider-location mapping before negative membership checks. No new enum, blanket compatibility boolean or schema change is made here.
