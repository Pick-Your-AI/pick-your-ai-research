# Pick Your AI organization redesign prompt

## Mission and invocation

Redesign the public face of the [Pick-Your-AI GitHub organization](https://github.com/Pick-Your-AI) so that a first-time visitor understands within ten seconds what Pick Your AI is, what state it is in, and where to go next: try the builder, read the research, or contribute. The result must look like one product family across the organization page, every public repository, and the Projects, and it must stay truthful about preview, research, and implementation status.

Execute this prompt only when explicitly assigned the redesign. It extends [ORGANIZATION.md](ORGANIZATION.md) and does not replace it. Track the work in the canonical organization-maintenance issue ([.github#2](https://github.com/Pick-Your-AI/.github/issues/2)) or in a sub-issue of it; do not open a parallel tracker. Read applicable AGENTS.md files, each touched repository's contribution guidance, prompts/SHARED.md, and ORGANIZATION.md, and follow their authority, concurrent-work, and review safeguards. This prompt does not authorize research campaigns, application feature work, deployments, permission or membership changes, repository renames, transfers, archival, or deletion.

## Phase 1: Audit the current state

1. Enumerate live organization repositories, Projects, and settings. For each public repository record its description, homepage, topics, social preview image, README header, license, community health files, issue and PR templates, label set, and whether Wiki, Discussions, and Projects are enabled.
2. Record the organization display name, avatar, description, website, verified-domain status, social accounts, public profile README (`.github/profile/README.md`), any members-only README (`.github-private/profile/README.md`), and the public and member pinned repositories.
3. Capture a dated before-state: screenshots of the organization page in light and dark themes, at desktop and phone widths, viewed as Public and as Member; plus a JSON dump of the metadata above. Attach or link it from the tracking issue.
4. Read the current `pickyour.ai` application for its brand assets (`public/favicon.svg`, `public/og-card.jpg`, theme tokens) and its status wording, so the organization matches the product rather than inventing a second identity.
5. List every problem you find, each with evidence: inconsistent naming, stale or unverifiable claims, walls of text, missing or broken links, repositories without social previews, missing community defaults, and copy that would mislead a newcomer about what exists today.

## Phase 2: Learn from strong organization pages

Study several well-regarded organization profiles and GitHub's own guidance before designing. Good references include [GitHub's organization profile documentation](https://docs.github.com/en/organizations/collaborating-with-groups-in-organizations/customizing-your-organizations-profile), the [LangChain organization profile](https://github.com/langchain-ai), and curated lists such as [awesome-readme](https://github.com/matiassingers/awesome-readme). Note in the tracking issue which patterns you adopt and why. Patterns that work well and fit this project:

- A centered logo with separate light and dark variants delivered through `<picture>` and `prefers-color-scheme`, followed by a one-line tagline.
- A short row of primary calls to action (Try the preview, Research, Contribute) instead of a long link sentence.
- Repositories grouped by role, each with one line of plain-language purpose.
- Detailed governance, metrics, and process moved into the owning repository's docs and linked rather than restated on the profile.
- Pinned repositories that mirror the profile's grouping and order.
- Consistent repository README headers and social preview cards so a shared link looks like the same product.

Avoid patterns that conflict with this project's evidence rules: dynamic third-party stat widgets, star or visitor counters, invented adoption numbers, decorative badges that claim a build, coverage, or release state the repository cannot show, and animated content that hurts readability or accessibility.

## Phase 3: Proposal for owner approval

Before writing to any live surface, publish a proposal in the tracking issue and get explicit approval from the organization owners. The proposal contains:

1. **Information architecture.** The section order of the public profile README, which content moves elsewhere, and where each moved paragraph will live. A newcomer should reach the builder, the research board, and the contribution guide without scrolling past the first screen.
2. **Copy deck.** Final wording for the organization description (at most 160 characters), the tagline, each repository description, each Project's short description and README, and the profile README. Use "Pick Your AI" as the product name; keep repository names and the `pickyour.ai` domain unchanged. Keep the synthetic-data preview qualification visible near the top while it applies.
3. **Visual system.** Logo lockups (light, dark, square avatar), a colour palette and type taken from the application's tokens, a social preview template (1280×640 PNG, under 1 MB, safe area for GitHub's cropping) with one variant per public repository, and a consistent README header block. All images carry meaningful alt text and keep sufficient contrast in both themes. Generate concept artwork with Codex as described in [Generating images with Codex](#generating-images-with-codex), and include the selected candidates and their prompts in the proposal.
4. **Repository map.** For every public repository: description, homepage, topics (shared `pick-your-ai`, `ai`, `ai-stack` plus a small set reflecting its real role and technology), social preview, README header, and the pinned order. Mark the Android, Apple, and leaderboard repositories as planning or delivery repositories unless their artifacts show otherwise.
5. **Community defaults.** Which files `.github` should provide as organization-wide defaults (for example CONTRIBUTING, SECURITY, SUPPORT, issue and PR templates, a LICENSE for the `.github` repository itself) and which repositories already override them. Defaults must not contradict a repository's own rules.
6. **Owner decisions.** List each choice that belongs to the owners rather than to you, with a recommendation: replacing the avatar, adding social accounts, verifying the `pickyour.ai` domain, enabling Discussions, adding a members-only README and member pins, and any label harmonization across repositories.

Present before-and-after mockups for the profile page at desktop and phone widths in both themes. Do not proceed past this phase on assumed approval.

## Generating images with Codex

Use the [Codex CLI](https://github.com/openai/codex) and its built-in image generation (the `$imagegen` skill, or a plain-language request such as "generate an image…") to produce raster artwork for the redesign. Confirm before starting that `codex --version` runs and that `codex features list` shows `image_generation` enabled; if it is unavailable, report that and continue with hand-built SVG assets rather than substituting another service without owner approval.

**What to generate.** Text-free artwork only: the profile banner or hero background, social preview backgrounds for each public repository, the square avatar's background or mark concept, and optional section illustrations. Generate light and dark variants where an image appears inside the profile README. Do not ask the model for final logos, wordmarks, repository names, or other text; image models misspell and distort type. Composite exact text and the existing logo onto the artwork afterwards with an SVG template or a deterministic script, so every repository's card can be regenerated from the same source.

**How to run it.**

1. Write a short image brief per asset: purpose, final size and aspect ratio, light or dark theme, palette hex values from the application's tokens, the safe area to keep empty for overlaid text, and the mood (for example "modular components snapping together into a stack", in keeping with the PC-builder metaphor).
2. Attach the existing brand references so results match the product: `codex --image public/favicon.svg --image public/og-card.jpg` (from a `pickyour.ai` checkout), plus a screenshot of the application's home page. In scripts, use `codex exec` with the same brief so runs are repeatable.
3. Generate three to five candidates per asset, keep the prompt with each, and iterate by editing the strongest candidate rather than starting over. Note the output path Codex reports for each image.
4. Pick finalists for the owner proposal. After approval, crop or resize to exact dimensions, composite text and logo, check contrast in both themes, and compress (social previews under 1 MB; profile images small enough to load quickly on mobile).

**Provenance and limits.**

- Commit only approved final assets, not every iteration. Store them under `.github/profile/assets/` with a sidecar `assets/PROVENANCE.md` that lists each file's prompt, reference images, Codex version, model reported by Codex, generation date, and the post-processing applied. State in the PR that the artwork is AI-generated.
- Do not depict real people, other companies' logos or products, vendor trademarks from the catalog, or anything that imitates another brand's identity. Generated imagery must not imply endorsements, partnerships, benchmark results, or features that do not exist.
- Image generation counts against the operator's Codex usage limits. Use an `OPENAI_API_KEY` for larger batches only when the owners approve that billing; never commit, paste, or log the key.
- Replacing the organization avatar or the application's logo remains an owner decision. Generated concepts are proposals until approved.

## Phase 4: Implement

- Make file changes (profile README, assets, community defaults, repository README headers) through each repository's branch, PR, and review workflow. Keep one focused PR per repository; store organization image assets in the `.github` repository and reference them with stable raw URLs.
- Apply approved metadata (descriptions, homepages, topics, pinned repositories, organization fields) directly only when your account is authorized. Re-read each value immediately before writing and verify it with a fresh API read afterwards. Social preview images and pinned repositories may require the web interface; record who applied them and when.
- Preserve existing assignees, labels, milestones, Project fields, issue relationships, and research acceptance criteria. Do not change Project field schemas or bulk-edit issues as part of the redesign.
- Keep claims traceable. Every status statement on the profile (preview, research, planned, deployed) must link to an artifact that supports it. A plan is not a shipped feature; a merged research finding is not production data.
- Do not commit credentials, personal information, tracking pixels, or third-party scripts.

## Phase 5: Verify and report

1. Review the live organization page as Public and as Member, in light and dark themes, at desktop and phone widths, and capture after-screenshots matching the before-state.
2. Check every link and image on the profile and repository headers; confirm social previews render when a repository link is shared.
3. Confirm with fresh API reads that each metadata value matches the approved copy deck.
4. Run each touched repository's required checks. Changes in this research repository require the commands in docs/RESEARCH_WORKFLOW.md. Schema and CI checks do not validate wording, rendering, accessibility, or link accuracy; review those separately and say so.
5. Post a report in the tracking issue: changed surfaces with before and after values, PR links and their state (proposed, merged), screenshots, owner decisions taken and still pending, and any remaining blockers.

## Acceptance checklist

- [ ] Audit, before-state, and reference patterns are recorded in the tracking issue.
- [ ] Owners approved the information architecture, copy deck, visual system, and repository map.
- [ ] The profile README fits its primary calls to action and status in the first screen, renders correctly in both themes and at phone width, and links only to existing artifacts.
- [ ] Every public repository has an accurate description, homepage, topics, social preview, and consistent README header.
- [ ] Codex-generated artwork is text-free, owner-approved, composited with exact text and logo, sized and compressed, and recorded in `PROVENANCE.md`.
- [ ] Pinned repositories match the approved order.
- [ ] Organization-wide community defaults exist and do not contradict repository-specific rules.
- [ ] Preview, research, planned, and deployed status are distinguished everywhere they are mentioned.
- [ ] After-state screenshots, API read-backs, and check results are posted; pending owner decisions are listed.

Close the redesign sub-issue only when this checklist and the required reviews are satisfied. Do not close the canonical maintenance issue or any research issue as part of the redesign; ongoing upkeep returns to [ORGANIZATION.md](ORGANIZATION.md).
