# Complete Pick-Your-AI/.github issue #17

## Mission and invocation

Work through https://github.com/Pick-Your-AI/.github/issues/17 in its entirety: implement dynamic escalation routing, a maintained team/role directory, and consistent contributor and agent guidance across the applicable Pick-Your-AI repositories.

This is an implementation-and-verification assignment, not an audit-only task or a request for another proposal. Continue through scoped implementation, meaningful tests, documentation, publication, required independent review, permitted merges, deployment of the directory-refresh mechanism, and authoritative acceptance readback. Do not call a static directory, an open PR, a configured-but-unexecuted workflow, or a queued review completion.

Reading or editing this prompt does not invoke it. Execute it only when the user assigns its execution. Once invoked, carry out the issue's requested work within existing authority. Ask only for a genuinely missing policy decision, credential, access grant, or action-specific authority; finish independent work while awaiting it.

## 1. Establish the current source of truth

Read the complete live issue body, every comment, native relationships, current assignees and Project metadata. Convert every acceptance checkbox and substantive requirement into an acceptance ledger with implementation path, verification method, evidence, and remaining blocker.

Read applicable AGENTS.md files, repository contribution guides and templates, and the accepted organization governance. In the research repository also read docs/RESEARCH_WORKFLOW.md. The local checkout named pickyour.ai may actually track pick-your-ai-research: verify remotes before editing. Archived IMPLEMENTATION_* documents are not authorization for runtime work.

Refresh these related issues, including their comments:
- .github#13: parent governance tracker.
- .github#14: research peer-review exception.
- .github#15: research freshness policy.
- .github#16: maintainer permissions and Review Leads.
- .github#18: accepted delegation and intentionally deferred future delegation.

Read the existing naming receipt:
https://github.com/Pick-Your-AI/.github/issues/17#issuecomment-6513853436

Refresh the following existing PRs before deciding what remains:
- .github#22: canonical naming register and organization contribution guidance.
- pick-your-ai-research#516.
- pick-your-ai-website#331.
- pick-your-ai-leaderboard#526.
- pick-your-ai-android#761.
- pick-your-ai-apple#455.
- .github#21: dated organization-chart proposal.

These references are starting points, not claims about their current state. Compare exact live heads, reviews, checks and merged contents. Reuse sufficient existing implementation and preserve its ownership. Do not open competing PRs for the same change, overwrite another author's branch, or regenerate historical charts as though they were current. Search the organization for additional overlapping issues and PRs and record a concise Prior work note before publication.

Check for an existing active owner, controller or implementation run. Coordinate with it rather than creating a duplicate. Use isolated branches/worktrees and exact-path staging; preserve unrelated changes.

## 2. Preserve accepted decisions and distinguish authorities

Keep the accepted escalation order:

repository team → repository maintainer → repository lead maintainer → applicable parent teams → CompleteDotTech.

Model repository maintenance, GitHub team membership/settings administration, effective repository permissions, Project permissions, independent review, and accepted operational ownership separately. Team membership, a maintainer title, or Admin access does not prove that someone accepted an operational assignment.

Resolve current roles from live data and accepted policy. Names and rosters in older issue text are historical baselines. Use stable organization, repository and team IDs for identity, refreshing display names and slugs.

Preserve the approved naming alignment. In particular, AI Applications replaces AI Tools & Platforms; Contributor Leaderboard no longer carries the Website suffix; Main Website, Mobile Apps and Education use their accepted names. Do not repeat renames already applied. Keep repository names and the pickyour.ai domain unchanged. Project category labels do not authorize reparenting teams. Preserve documented functional Team Workstream labels.

Preserve these exceptions and boundaries:
- CompleteDotTech's placeholder memberships do not automatically establish operational ownership. Do not route directly to the owner because intermediate data is missing.
- Shared Research administration and unfilled specialty leadership remain as currently accepted in #18. Do not populate vacancies, remove interim coverage or invent assignments.
- Review Leads is a review-coordination role. Refresh #16 and #17's comments for its stable ID, grants and any acceptance of responsibilities; an invitation or membership alone is not acceptance.
- Internal Discussion remains the accepted private exception. Do not add management teams or protections, publish its contents, or report the accepted arrangement as a control defect.
- Preserve owner-controlled .github governance and any specifically accepted reviewer grants.
- Do not change membership, permissions, rulesets, bypass actors, required checks, research review policy or research-refresh cadence as a side effect of #17. Implement only already accepted related decisions. Keep unresolved decisions explicitly unresolved.

Unresolved #14/#15 decisions do not block independent resolver, directory and entrypoint work. Preserve current enforcement until the responsible owner resolves a policy question.

## 3. Inventory all applicable surfaces

Discover the current complete organization inventory; do not hardcode the earlier counts of 92 teams, 15 repositories or 13 Projects.

Use authenticated, paginated reads for repositories, nested teams, relevant members/managers, repository and Project grants where supported, current default branches, applicable rules and existing automation. Detect truncation, inaccessible endpoints and permission gaps explicitly. A 403, 404, missing page or private membership must not become an empty authoritative result.

Create a coverage matrix for each repository:
- Canonical area, team IDs, lead/maintainer roles, parent chains and intentional exceptions.
- Existing README, CONTRIBUTING, SUPPORT, AGENTS.md and other actual agent entrypoints.
- Organization defaults versus repository-local issue/PR templates and overrides.
- CODEOWNERS eligibility and current review routing.
- Documentation/automation owner, deployment destination, and tests.

Do not create meaningless duplicate files merely to fill a matrix. Explain genuinely inapplicable surfaces and keep useful repository-specific guidance.

## 4. Implement one governed policy and mapping

Maintain the canonical escalation policy and repository/path-to-role mapping in Pick-Your-AI/.github, reusing accepted naming documentation and existing code where suitable. Define a versioned, validated format with clear ownership and a controlled review path.

Include stable IDs, current display metadata, role meanings, scoped path overrides where justified, parent relationships, declared exceptions, acceptance evidence where required, and policy provenance. Keep policy separate from observed membership snapshots.

A membership lookup must never invent policy, silently assign people, promote access, or resolve a deferred owner decision. Invalid, ambiguous or removed mappings should produce an actionable diagnostic.

Choose the smallest implementation that fits the repository. Avoid a separate service, dependency stack or duplicated registry when the existing tools can meet the requirements.

## 5. Implement the live resolver

Provide a documented CLI or existing equivalent that accepts a repository, optional path and decision context, and produces both machine-readable and human-readable routing results.

Resolve the accepted policy against live GitHub data. Handle pagination, nested and inherited membership, multiple roles held by the same person, renamed teams, deleted teams, unfilled roles, permission restrictions and rate limits.

The result must:
- Preserve escalation order and explain which role each candidate represents.
- Deduplicate people without losing their role provenance.
- Distinguish configured access from accepted operational responsibility.
- Exclude placeholder owner memberships from intermediate recipients, retaining CompleteDotTech at the final escalation level.
- Record the disposition of unresolved intermediate roles.
- Expose source identity, policy revision, observation time, freshness and coverage gaps.
- Support private/internal detail separately from approved public output.

Set and document a configurable freshness policy with its approval basis. Do not misrepresent an implementation default as an existing organization decision. On unavailable or stale data, retain the last verified timestamp, mark uncertainty and offer the safe next step; do not claim current recipients or silently jump to the owner.

Resolving a route does not send a message. Provide drafts or explicit next-recipient instructions; never automatically contact, mention, assign or notify people without applicable authorization.

## 6. Generate and operate the directory refresh

Generate the human-readable directory from the same policy and resolver data. Include useful role distinctions, current names/links, freshness and unresolved coverage. Keep historical snapshots distinctly dated.

Use deterministic output and change detection so unchanged input does not create repeated commits, PRs or notifications. Preserve the last known good output on failed refresh; report failure without replacing it with a misleading empty directory.

Implement the automatic refresh required by #17:
- Verify which relevant GitHub change events are actually available with the selected deployment and credentials.
- Use supported events where feasible and bounded periodic reconciliation as fallback.
- Include a safe manual refresh path, concurrency control and clear failure reporting.
- Follow the approved repository workflow, including PR review for generated changes where required.
- Keep membership, grants and branch protections read-only.
- Never execute untrusted PR code with organization credentials, expose secrets, or broaden a token merely for convenience.

Execution of this prompt authorizes the issue-scoped directory automation within existing permissions. It does not authorize the unrelated research-refresh schedule in #15, paid infrastructure, new organization-wide access, or bypassing protected publication. If a new installation, secret, webhook permission or explicit schedule activation decision is genuinely needed, prepare and test the exact configuration before requesting that specific decision.

An enabled cron expression alone is not proof of operation. Verify the deployed revision, configured triggers, a successful real supported event, fallback reconciliation, generated output and visible timestamp. Distinguish event replay from actual webhook delivery. Use an authorized disposable test organization/repository for mutation-based tests; do not change production membership or permissions just to produce an event.

## 7. Integrate contributor and agent entrypoints

Add concise, consistent guidance to applicable README, CONTRIBUTING, SUPPORT, AGENTS.md and equivalent agent entrypoints. Link the canonical policy/resolver instead of copying changing rosters into every repository.

Explain when to escalate, how to resolve the next role, how to record prior disposition, and how to handle unavailable routing data. Preserve each repository's research, legal, privacy, licensing, release and evidence requirements.

Add lightweight fields to applicable issue and PR templates:
- Decision needed.
- Current responsible role.
- Prior disposition.
- Next recipient.

Keep ordinary contributions easy to submit. Do not require a full escalation history for every typo or routine PR.

Respect local templates that override organization defaults. Use team-based CODEOWNERS only when eligible and appropriate; it is review routing, not permission assignment or policy enforcement. Do not silently change the separate research peer-review decision. Keep private guidance and evidence out of public defaults.

## 8. Verify behavior and publication

Use a disposable fresh test VM for reproducible implementation verification before publishing claims. Preserve the machine-wide prohibition on shutting down or terminating the shared WSL VM. If fresh-VM evidence is unavailable, say exactly what remains unverified; do not substitute local success for VM verification.

Test meaningful failure modes:
- Multiple API pages and truncated or cyclic pagination.
- Nested membership, inherited grants and duplicate recipients.
- Renamed/removed teams and stable-ID continuity.
- Vacant roles, unaccepted responsibilities and owner placeholders.
- Private or inaccessible data, authentication failure and rate limits.
- Stale data, corrupt cache and last-known-good recovery.
- Deterministic generation and unchanged-refresh no-op.
- Concurrent refreshes, retry/reconciliation and publication failure.
- Unsupported event coverage and fallback operation.
- Local template overrides and valid CODEOWNERS targets.

Use synthetic fixtures only for tests and label them accordingly. Never publish raw private API exports, invitation data, tokens, emails, customer content or unapproved private membership.

Start genuinely fresh agent sessions in representative research, website and native-client contexts. Verify that each loads the intended entrypoint, invokes the current resolver and begins with the repository team without needing an owner prompt. A simulated transcript or editing AGENTS.md is not proof of discovery.

Exercise a real contributor-facing issue/PR form without unsolicited mentions or external messages. Verify required context is clear and the route is usable. Test actual automation operation and observe its output; do not infer it from YAML syntax or mocks.

Run each changed repository's applicable checks. Distinguish automated structure tests, VM behavior, hosted CI, independent review, automation activation and live acceptance. Do not weaken checks or fix unrelated baseline failures to make a documentation lane appear green.

## 9. Deliver through the existing review process

Keep PRs scoped and reuse the six existing naming PRs where they already cover required work. Link implementation PRs to #17 with Refs while acceptance remains partial. Use exact-head independent review and required CI; any material head change invalidates stale review evidence.

Do not self-approve, fabricate a reviewer, bypass required review, force-push another contributor's work, or treat queued approval as acceptance. Finish all independent work while genuine reviews or decisions are pending.

Publish only authorized scoped changes. Re-read live state immediately before writes and verify afterward. Do not overwrite concurrent issue bodies, assignments, labels, Project values or native relationships. Store large/private evidence outside public repositories with sanitized references.

After authorized merges, read back merged commits and current default-branch contents. Verify deployed automation against the merged revision, then synchronize only clean local checkouts. Preserve historical receipt and chart provenance.

## 10. Acceptance and final report

Map every original and additional #17 criterion to concrete evidence. Required outcomes are:
- Governed, validated role/path mapping and naming continuity.
- Working live resolver and generated directory.
- Operational, verified refresh triggers and fallback.
- Integrated and tested human/agent entrypoints and local overrides.
- Passing meaningful tests, applicable CI and required independent reviews.
- Live readback with declared freshness, privacy and access limitations.

Close #17 only when its complete acceptance criteria are satisfied, required merges and activation are verified, and no mandatory work remains. Update only its corresponding disposition in #13 when appropriate; do not close #13 or the separate policy issues.

If blocked, report the exact unsatisfied criterion, evidence, responsible role, completed independent work and smallest next action. Never call an unimplemented trigger, open PR or missing owner decision complete.

Finish with a concise report: what is live, merged PRs and commits, resolver usage, canonical directory location, actual refresh operation, verification results, and remaining limitations. Include the acceptance-ledger link so completion can be audited.
