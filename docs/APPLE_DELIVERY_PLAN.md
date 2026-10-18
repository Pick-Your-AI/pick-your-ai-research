# Apple/iOS application delivery plan

Mobile planning issues now live in `Pick-Your-AI/pick-your-ai-android` and `Pick-Your-AI/pick-your-ai-apple`. See the [migration record](../prompts/mobile/MIGRATION.md). Repository creation resolves location only; framework, modules and service placement remain gated. Existing acceptance-record paths are preserved. Historical snapshots below do not override the live migration.

Published delivery structure: [Project #5](https://github.com/orgs/Pick-Your-AI/projects/5),
[program Pick-Your-AI/pick-your-ai-apple#1](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/1).
The [issue index and triage record](APPLE_DELIVERY_TRACKING.md) records the publication
snapshot and structural conventions. GitHub owns current status, ownership and native
relationships. Planning publication does not establish application implementation.

The plan follows the Android planning session's **1 program → 18 epics → 110
feature/task work packages → implementation and validation subtasks** structure.
The same numeric coordinates identify corresponding capabilities on both platforms;
use the `IOS-` prefix when referring to an Apple work package, for example
`IOS-11.04`. These are planning identifiers, not GitHub issue numbers.

Source: user-designated Android planning session
`01a14760-a1b1-73b2-ba80-fb42046c1abc`, reviewed 2026-10-16. This plan supersedes the
earlier 19-workstream Apple outline by regrouping its scope, not dropping it.
Repository and service placement, framework choice, supported OS versions, accounts,
and monetization remain explicit decisions. iPhone and adaptive iPad experiences
are the proposed baseline; Mac and other Apple platforms are decision-dependent.

The product should feel like a parts picker: a persistent stack list, category
selection, understandable compatibility findings, comparable costs, and saved or
shared configurations. It uses original branding, wording and assets. The Apple
client plans AI stacks; running models or provisioning infrastructure is a separate
capability under 18.5.

## Delivery hierarchy

```text
Pick Your AI — Apple/iOS Application Delivery
│
├── 01. Product scope and decisions
│   ├── 01.1 Target users and primary iPhone and iPad journeys
│   ├── 01.2 MVP scope and phased capabilities
│   ├── 01.3 Apple platform scope, technology and repository structure
│   ├── 01.4 Backend architecture and hosting
│   ├── 01.5 Accounts and monetization decisions
│   └── 01.6 Acceptance criteria, ownership and release gates
│
├── 02. Apple application foundation
│   ├── 02.1 Xcode toolchain, dependencies and modules
│   ├── 02.2 Preview, staging and production environments
│   ├── 02.3 Navigation, lifecycle and state restoration
│   ├── 02.4 UI, domain and data boundaries
│   ├── 02.5 macOS continuous integration and required checks
│   └── 02.6 Clearly identified synthetic fixtures
│
├── 03. Shared contracts and mobile conformance
│   ├── 03.1 Adopt versioned contracts and generate models
│   ├── 03.2 Separate incomplete drafts from saved snapshots
│   ├── 03.3 Define required versioned API extensions
│   ├── 03.4 Model component placement and relationships
│   ├── 03.5 Define evidence, unknowns and rule semantics
│   └── 03.6 Cross-client conformance and migration fixtures
│
├── 04. Research-to-production catalog pipeline
│   ├── 04.1 Source access, display and redistribution rights
│   ├── 04.2 Normalize and validate component facts
│   ├── 04.3 Evidence review and production approval
│   ├── 04.4 Publish immutable catalog and rule releases
│   ├── 04.5 Freshness, corrections and retractions
│   └── 04.6 Publish the first complete supported real-data path
│
├── 05. Shared application services
│   ├── 05.1 API foundation, database and migrations
│   ├── 05.2 Catalog discovery, search and delivery
│   ├── 05.3 Build creation, revisions, history and deletion
│   ├── 05.4 Compatibility evaluation and pricing services
│   ├── 05.5 Share creation, access and revocation
│   ├── 05.6 Resource estimates and quality evidence
│   ├── 05.7 Authorization and optional account authentication
│   ├── 05.8 Limits, auditability, secrets and recovery
│   └── 05.9 Integration with the existing website
│
├── 06. Mobile experience and design system
│   ├── 06.1 Information architecture and interaction prototypes
│   ├── 06.2 Accessible components and design tokens
│   ├── 06.3 Adaptive iPhone and iPad layouts
│   ├── 06.4 Builder guidance and understandable status labels
│   ├── 06.5 Loading, empty, offline and failure states
│   └── 06.6 Themes, localization, units and presentation
│
├── 07. Component discovery and comparison
│   ├── 07.1 Browse, search, filter and sort the catalog
│   ├── 07.2 Compatibility-aware component picker
│   ├── 07.3 Component details, conditions and evidence
│   ├── 07.4 Side-by-side component comparison
│   └── 07.5 Select components from search and deep links
│
├── 08. AI stack builder
│   ├── 08.1 Workload, constraints and deployment inputs
│   ├── 08.2 Model and infrastructure selection
│   ├── 08.3 Enable and disable optional tiers
│   ├── 08.4 Edit component settings and build objectives
│   ├── 08.5 Persistent summary and suggested next steps
│   └── 08.6 Undo, autosave and revision restoration
│
├── 09. Compatibility and capacity
│   ├── 09.1 Integrate the governed evaluator
│   ├── 09.2 Recheck affected components after changes
│   ├── 09.3 Explain findings and possible fixes
│   ├── 09.4 Consume qualified capacity estimates
│   ├── 09.5 Suggest alternatives with stated tradeoffs
│   └── 09.6 Handle stale and out-of-order results
│
├── 10. Cost estimation
│   ├── 10.1 Select applicable dated rates
│   ├── 10.2 Calculate costs from explicit usage scenarios
│   ├── 10.3 Show missing costs, coverage and uncertainty
│   └── 10.4 Compare scenarios and preserve price provenance
│
├── 11. Saved builds, comparison and sharing
│   ├── 11.1 Local build library
│   ├── 11.2 Compare complete builds and revisions
│   ├── 11.3 Safe import and export
│   ├── 11.4 Read-only shared builds with pinned evidence
│   ├── 11.5 Fork builds and optional cross-device continuity
│   └── 11.6 Universal Links, associated domains and browser fallback
│
├── 12. Offline storage and synchronization
│   ├── 12.1 Durable local database and migrations
│   ├── 12.2 Cached catalogs and offline draft editing
│   ├── 12.3 Atomic refresh and background scheduling
│   ├── 12.4 Queued writes and retry reconciliation
│   ├── 12.5 Conflict resolution without lost edits
│   └── 12.6 Logout, deletion and unavailable-version handling
│
├── 13. Optional tiers and operational capabilities
│   ├── 13.1 Knowledge and retrieval configuration — T3
│   ├── 13.2 Agents, tools, MCP and memory — T4
│   ├── 13.3 Training and fine-tuned models — T5
│   ├── 13.4 Guardrails and evaluation guidance — T6
│   ├── 13.5 Deployment plans and monitoring choices — T6
│   └── 13.6 Validate supported combinations across tiers
│
├── 14. Privacy, security and trust
│   ├── 14.1 Data inventory and threat model
│   ├── 14.2 Keychain, data protection and secure networking
│   ├── 14.3 Account and associated-data lifecycle, if included
│   ├── 14.4 Privacy disclosures and third-party SDK controls
│   ├── 14.5 Adversarial testing of sharing, imports and APIs
│   └── 14.6 Dependency security and vulnerability response
│
├── 15. Quality and performance
│   ├── 15.1 Contract and domain regression tests
│   ├── 15.2 Apple UI and accessibility tests
│   ├── 15.3 Network failure and recovery tests
│   ├── 15.4 Device, OS and lifecycle test matrix
│   ├── 15.5 Apple, Android, web and backend conformance tests
│   ├── 15.6 Measured startup, rendering and resource budgets
│   ├── 15.7 Security and release-build regression tests
│   └── 15.8 Authorized user validation and acceptance
│
├── 16. TestFlight, App Store delivery and launch
│   ├── 16.1 Apple Developer team and App Store Connect identity
│   ├── 16.2 Platform and store-policy requirements
│   ├── 16.3 Signing, provisioning, entitlements and key management
│   ├── 16.4 Internal and external TestFlight testing
│   ├── 16.5 App Store listing, screenshots and privacy declarations
│   ├── 16.6 Launch readiness and controlled rollout
│   └── 16.7 Verify the installed production release
│
├── 17. Product and data operations
│   ├── 17.1 Application and service monitoring
│   ├── 17.2 Incident response and restore drills
│   ├── 17.3 Catalog, evidence and pricing maintenance
│   ├── 17.4 Support, corrections and contribution workflow
│   └── 17.5 Compatibility maintenance and release cadence
│
└── 18. Decision-dependent expansion
    ├── 18.1 Favorites and price/compatibility alerts
    ├── 18.2 Paid plans and entitlements
    ├── 18.3 Community build publishing and moderation
    ├── 18.4 Advanced recommendations and personalization
    ├── 18.5 Actual runtime execution or provisioning
    └── 18.6 Additional markets and platforms
```

## Product tiers are not delivery levels

| Product tier | What users configure | Scope |
| --- | --- | --- |
| T0 — Configuration | Workload, constraints, deployment mode and objectives | Core |
| T1 — Model Selection | Providers, models and context policies | Core |
| T2 — Infrastructure | Hosting, compute, storage and inference engines | Applicable to selected components and deployment |
| T3 — Knowledge & Retrieval | Data sources, knowledge bases, embeddings, vector databases and RAG | Optional |
| T4 — Agents & Integrations | Frameworks, tools, APIs, integrations, MCP and memory | Optional |
| T5 — Training & Fine-Tuning | Frameworks, compute, datasets and resulting models | Optional |
| T6 — Deployment & Operations | Guardrails, evaluation, costs, deployment planning and monitoring | Core guidance; depth follows release scope |

All 29 canonical kinds retain their existing definitions and [issue mapping](CONTRACT_MAPPING.md).
Dependencies run in both directions. Selecting a model affects compute requirements;
selecting available compute affects model options. A compatibility cycle must never
be turned into a cycle of GitHub delivery blockers. Optional T3–T5 capabilities remain
optional for an individual build, even when their UI is supported by the application.

## Tasks and subtasks

Create native sub-issues for separately owned or independently reviewed work.
Keep small implementation and verification steps as checklists; do not duplicate
native child links as a second checklist of the same work.

```text
Program: Apple/iOS Application Delivery
└── Epic 11: Saved builds, comparison and sharing
    └── Feature 11.4: Read-only shared builds with pinned evidence
        ├── Task: Define the sharing contract
        │   ├── Specify visibility and permitted fields
        │   ├── Define expiration and revocation behavior
        │   └── Obtain contract and privacy review
        ├── Task: Implement the shared-build service
        │   ├── Resolve the exact build revision
        │   ├── Retain referenced catalog, rules and prices
        │   └── Enforce access and payload limits
        ├── Task: Implement the Apple viewer
        │   ├── Display the original evidence and results
        │   ├── Handle unavailable or revoked shares
        │   └── Allow an explicit fork into a new build
        ├── Task: Implement browser fallback
        └── Task: Verify the complete sharing journey
            ├── Open on another supported Apple device
            ├── Open in a browser without installation
            ├── Confirm private fields are excluded
            └── Confirm later catalog changes preserve history
```

Every work package must identify:

- User outcome and in/out scope, including whether it is conditional.
- Existing canonical issue, source evidence, contract versions, and consuming clients.
- Deliverables and proposed ownership; GitHub assignees remain authoritative.
- Genuine prerequisites separately from information inputs and compatibility relationships.
- Measurable acceptance criteria, implementation tasks, and validation evidence.
- Unknowns, decision owner, review requirements, and release gate.

Do not invent dates, estimates, assignee commitments, API behavior, research acceptance,
or production readiness. Apply the live fields of the destination Project when it is
created; this plan does not rename fields or reset existing boards.

## Shared work and existing issue ownership

The published 110 feature/task issues represent distinct Apple outcomes, including
client integration and receiving acceptance of shared outputs. They do not commission
110 independent Apple services. The [tracking index](APPLE_DELIVERY_TRACKING.md) maps
canonical shared delivery slices to their Apple consumers. Before adding work, refresh
open/closed issues, PRs and related projects. Preserve existing parents, owners and
triage metadata; add an existing issue or a distinct integration task as appropriate.

| Work | Canonical coordination point | Apple plan consumers |
| --- | --- | --- |
| Shared schemas, rules, versioned API changes | [Research Pick-Your-AI/pick-your-ai-research#40](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40) | 03, 05, 09 |
| Source policy, evidence and freshness | [Research Pick-Your-AI/pick-your-ai-research#41](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/41) and [Pick-Your-AI/pick-your-ai-research#60](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/60) | 04, 07, 17 |
| Pricing semantics | [Research Pick-Your-AI/pick-your-ai-research#39](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/39) | 05.4, 10 |
| Saved/shared build semantics | [Research Pick-Your-AI/pick-your-ai-research#42](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/42) | 05.3, 05.5, 11, 12 |
| Real catalog/pricebook integration | [Website Pick-Your-AI/pickyour.ai#15](https://github.com/Pick-Your-AI/pickyour.ai/issues/15) | 04.6, 05.9 |
| Capacity evidence and read API | [Website Pick-Your-AI/pickyour.ai#16](https://github.com/Pick-Your-AI/pickyour.ai/issues/16), [Research Pick-Your-AI/pick-your-ai-research#10](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10) | 05.6, 09.4 |
| Persistent accounts and shared builds | [Website Pick-Your-AI/pickyour.ai#17](https://github.com/Pick-Your-AI/pickyour.ai/issues/17) | 05.3, 05.5, 05.7, 11 |
| Canonical display labels | [Website Pick-Your-AI/pickyour.ai#18](https://github.com/Pick-Your-AI/pickyour.ai/issues/18) | 03.1, 06.6 |
| Incomplete versus incompatible presentation | [Website Pick-Your-AI/pickyour.ai#31](https://github.com/Pick-Your-AI/pickyour.ai/issues/31) | 06.4, 08.5, 09.3 |
| Current visual direction | [Website Pick-Your-AI/pickyour.ai#32](https://github.com/Pick-Your-AI/pickyour.ai/issues/32) and [Pick-Your-AI/pickyour.ai#33](https://github.com/Pick-Your-AI/pickyour.ai/issues/33) | 06 |
| Product and market decisions | [Research Pick-Your-AI/pick-your-ai-research#47](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/47), [Pick-Your-AI/pick-your-ai-research#58](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/58) | 01, 18 |

Epics 03–05 and shared parts of 09–12 and 17 should consume one governed service/data
implementation across Apple, Android and web. Each client still needs its own adapter,
UI, lifecycle and conformance verification. A shared issue cannot be closed merely
because one client integrates it. Research completion, service delivery, client
integration and release approval are distinct milestones.

Research and shared-contract decisions remain in this repository. Application runtime
code belongs in the implementation repository selected in 01.3; production services
belong in the location selected in 01.4. The existing website is a static preview,
not evidence that a production backend or mobile application already exists.

## Apple-specific acceptance details

| Work packages | Required detail when expanding into tasks |
| --- | --- |
| 01.3, 02.1, 02.5 | Decide SwiftUI/framework and minimum OS; pin Xcode and dependencies; use macOS CI; separate preview, staging and production |
| 02.3, 06.3 | Restore navigation and drafts after termination; adapt iPhone/iPad layouts, multitasking and keyboard interaction |
| 06.2, 06.6, 15.2 | VoiceOver, Dynamic Type, contrast, Reduce Motion, dark/light themes, localization and right-to-left layouts |
| 03.1–03.6 | Validate all 29 kinds, decimal-string money, draft versus snapshot boundaries, version locks, and outcome/severity semantics; test parity rather than inventing a separate policy |
| 05.7, 14.3 | Decide guest/account scope and Sign in with Apple applicability; cover session renewal, revocation, guest migration and associated-data deletion |
| 11.3, 11.6 | System share sheet, safe file import/export, Universal Links, associated-domain hosting and browser fallback; verify the existing web format |
| 12.1–12.6 | Durable local storage and migrations; bounded platform background work; retry reconciliation, conflict UX, unavailable versions and account isolation |
| 14.2, 14.4 | Keychain, local data protection, secure networking, SDK inventory, privacy manifests and accurate privacy disclosures |
| 15.4–15.8 | Physical-device and OS coverage; accessibility, offline, deletion and conflict journeys; measured performance/energy budgets and release-build checks |
| 16.1–16.7 | Developer-team access, bundle identity, signing, entitlements, TestFlight, support/privacy URLs, age ratings, review access, submission, staged launch and installed-release readback |
| 18.1–18.6 | Notifications require opt-in; paid features require a commerce decision and purchase/restore lifecycle; public community requires moderation; execution requires separate authorization; Mac and other platforms require scope decisions |

Store and SDK requirements must be checked against current Apple documentation when
implementing and before submission; this plan does not freeze a toolchain requirement
or guarantee approval. Primary references: [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/),
[App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/),
[submission requirements](https://developer.apple.com/app-store/submitting/),
[TestFlight](https://developer.apple.com/testflight/), and
[third-party SDK requirements](https://developer.apple.com/support/third-party-SDK-requirements/).

## Release phases and exit evidence

| Phase | Exit evidence |
| --- | --- |
| Foundation | Scope/repository decisions, reproducible Apple build, CI and contract conformance harness; owners and unresolved prerequisites recorded |
| Synthetic preview alpha | Core browse/build/compare/save/share journeys work with explicit synthetic labels; local lifecycle and failure behavior tested |
| Reviewed real-data beta | A bounded supported path uses rights-cleared, reviewed, published data; evidence/cost gaps remain explicit; included services, privacy and sync work end to end; TestFlight feedback is triaged |
| Production launch | Supported-device, accessibility, security and release tests pass; support and operations are ready; store requirements, review and release approval complete; installed production build verified |
| Selected expansion | Each conditional capability has an accepted scope decision, evidence, owners, dependencies, tests and its own release gate |

These phases describe dependency order, not dates or estimates. Design, security,
persistence and testing begin early and continue through every phase. Individual
features can proceed against fixtures while research is pending; production claims
and promotion depend on accepted evidence. Frozen v1 stays unchanged until a reviewed,
versioned successor is adopted. Merged research alone does not satisfy a release gate.

## Coverage of the earlier Apple outline

| Earlier workstream | Destination in the aligned structure |
| --- | --- |
| Product definition; governance and architecture | 01, with ownership and issue rules in this document |
| Apple engineering foundation | 02 and signing/release work in 16 |
| Native design and navigation | 06 |
| Contracts and domain models | 03 |
| Production catalog and evidence | 04 |
| Backend and service infrastructure | 05 |
| Accounts, security and privacy | 05.7 and 14 |
| Catalog browsing and comparison | 07 |
| T0–T6 builder | 08 and 13 |
| Compatibility and capacity | 09 |
| Pricing and scenarios | 10 |
| Persistence and offline operation | 12 |
| Saved builds and sharing | 11 |
| Guides, starters and advanced planning | 06.4, 08.5, 13.5 and conditional recommendations in 18.4 |
| Growth and commerce | 18 |
| Quality and release qualification | 15 |
| Operations and maintenance | 17 |
| TestFlight and App Store delivery | 16 |

## Documentation verification

The 2026-10-17 publication snapshot contains 18 epic IDs and 110 unique feature IDs.
Reconcile against live GitHub; these are not fixed quotas for future triage. Check for
each feature under its matching epic. Verify relative links and cross-document
scope/status language. Run the [research workflow checks](RESEARCH_WORKFLOW.md)
before publication. Those checks validate research structure and contract integrity;
they do not implement the plan, validate Apple binaries, accept evidence, or create
GitHub tracking items.
