# Mobile issue repository migration

The maintainer authorized transferring the existing Android and Apple delivery issues into their corresponding client repositories. The [complete mapping](issue-migration.json) records all 258 old/new URLs and node IDs: 129 Android and 129 Apple issues. GitHub redirects old URLs. No issues were recreated and no delivery work was completed by this change.

## Identity and graph preservation

The pre-transfer audit captured every body, comment, assignee, label, type, milestone, native parent, blocker, and both Projects' fields/options and item metadata. Labels were prepared before transfer. GitHub changes issue node IDs and can drop parent links; the migration restores missing native relationships from that snapshot and verifies all 256 parent and 432 prerequisite edges. External consumers remain attached to the same logical issues.

Observed repairs: three parent links and ten prerequisite links required restoration. Original sibling ordering was restored and checked as well. No new dependency or ownership decision was introduced.

GitHub also rewrites references during transfers, including ambiguous research labels. The migration reconciles bodies from the original snapshot, resolving Markdown labels from their linked target and explicitly qualifying unlinked research and mobile references. Acceptance criteria, checkboxes, scope, ownership and deliverable paths are preserved apart from reference qualification. Comments remain attached; historical comments and immutable old publications may still show original references.

## Placement and shared authority

Planning now belongs in the corresponding mobile repository. This does not move the Android acceptance records: their existing `docs/delivery/android/...` paths remain in `Pick-Your-AI/pickyour.ai` until explicitly changed through the placement decision. Apple named outputs still require their accepted ADR/file paths. Repository location is established; framework, package identity, modules, hosting and additional-platform decisions remain open.

Canonical website issues `Pick-Your-AI/pickyour.ai#15`–`Pick-Your-AI/pickyour.ai#18` and research authorities stay in their original repositories. Android shared-service tracking does not assign a second backend to Apple. Frozen v1, evidence boundaries, optional T3–T5/core T6, ownership and release authority are unchanged.

## Maintainer tooling

Use repository-qualified `issue`/`parent`/`children` keys in coverage schema v2; issue numbers alone are not unique. `project-fields.json` lists fully qualified program/member identities. `migrate_references.py` applies the recorded transfer map to mutable text; it does not create issues. The previous local prompt-generation script is retired so it cannot overwrite this set using website-only identities.

Run `python prompts/mobile/validate_prompts.py` and the required research workflow checks. The optional `--audit-dir` comparison expects fresh `issues.json`, `items4.json`, `items5.json`, `fields4.json` and `fields5.json`. Automation checks mapping, criteria, graph and fields; manual review checks reference meaning, shared-service scope and preservation of acceptance boundaries. No application/device/store validation is claimed.

Publication checks passed with Python 3.12: requirements installation, 21 contract tests, 24 repository tests, six namespace-rewrite regression tests, the research validator (30 catalog proposals and two pricebooks), and the mobile validator (258 issues, 36 epics, 906 criteria and 880 steps). The coverage comparison retains every acceptance path, scope coordinate, assignee and triage value. This author review does not substitute for independent receiving review.

The migration is live. The accompanying prompt/guidance revision is proposed through a PR and must receive independent review; it is not merged by this task. Publication starts no implementation campaign and grants no deployment, app release, infrastructure, spending or outreach authority.
