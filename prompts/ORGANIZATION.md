# Pick Your AI organization maintenance prompt

## Mission and invocation

Maintain accurate, consistent public descriptions, repository topics, links, and organization profile content across the live Pick-Your-AI organization. Execute this prompt only when explicitly assigned organization maintenance; a research workstream invocation does not start this work.

Read applicable AGENTS.md, repository contribution guidance, and prompts/SHARED.md. Follow its authority, concurrent-work, evidence, and review safeguards. Research-specific schemas, workstream deliverables, and completion gates apply only when changing research artifacts. This maintenance task does not authorize research campaigns, deployments, permission changes, or a new schedule.

## Inspect before changing

1. Enumerate live organization repositories and inspect their descriptions, topics, homepage links, README files, and applicable instructions. Inspect the organization description, website link, and .github/profile/README.md.
2. Find existing maintenance issues, pull requests, and active owners before creating work. Reuse the canonical tracking issue and coordinate with any active run. Preserve assignees, labels, milestones, Project fields, issue relationships, and research acceptance criteria.
3. Verify claims against current repository artifacts, merged decisions, and the observable website. Distinguish researched, proposed, implemented, deployed, and verified behavior. A merged research finding is not an implemented feature.
4. Save a scoped before-state for metadata and issue bodies. Record evidence links and observation dates in the tracking issue; do not publish secrets or personal information.

## Public metadata and profile

- Use Pick Your AI consistently as the product name, preserving repository names and the pickyour.ai domain.
- Give repositories shared discovery topics such as pick-your-ai, ai, and ai-stack, plus a small set reflecting their actual role and technology. Topics are repository metadata, not issue labels or Project fields. Preserve useful existing topics; remove a topic only when it is demonstrably inaccurate or redundant.
- Describe pick-your-ai-research as research, evidence, and shared data contracts covering component catalogs, compatibility, and pricing. Keep its homepage pointing to the research Project unless an accepted decision changes that destination.
- Describe pickyour.ai as the AI stack builder. Preserve the synthetic-data preview qualification while applicable. Do not imply its prices, component catalog, or compatibility results are validated real-world evidence.
- Describe .github as the organization profile and shared community guidance. Link it to the organization page. Set the organization website to the verified product URL.
- Align the organization profile with current product status. If a preview exists, replace outdated statements that no application exists with an accurate preview/research distinction. Include direct links to the builder, research repository, and research Project.
- Change tracked profile or documentation files through the repository's branch, PR, and review workflow. Metadata edits may be applied directly when authorized. Never infer deployment authorization from a documentation task.

## Research handoffs and issue updates

Research owners retain their existing scope. When accepted findings make public wording inaccurate, record the evidence and affected surface in the organization-maintenance issue. Route the change to its owner; do not launch maintenance separately from every research workstream.

Update only relevant issue handoff sections. Use stable commit-pinned prompt links and the publication PR; explicitly state whether guidance is proposed or merged. Preserve all other issue content and metadata. Re-read immediately before each write, stop to reconcile concurrent body changes, and verify the result afterward. Do not turn informational maintenance handoffs into native research blockers.

## Validation and completion

Verify each metadata write through a fresh API read. Review public organization/repository pages and link destinations for consistency. For file changes, run that repository's required checks; changes in this research repository require the commands in docs/RESEARCH_WORKFLOW.md. Automated schema checks do not validate public claims, rendering, or link accuracy.

Report changed surfaces, before/after values or diffs, evidence, verification results, and remaining blockers in the tracking issue. Separate applied metadata from proposed profile/documentation changes. Close the bounded maintenance issue only after its acceptance criteria and required reviews are satisfied; never close research issues merely because their public descriptions or prompt links were updated.
