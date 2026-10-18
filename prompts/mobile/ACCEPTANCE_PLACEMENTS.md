# Accepted mobile record placements

Checked 2026-10-18 against Android's [current v6 acceptance ledger at
ae61cfcb](https://github.com/Pick-Your-AI/pick-your-ai-android/blob/ae61cfcb16eefe96e058b044deba833dac27d3ae/docs/delivery/criterion-evidence.json).
The five independently reviewed and merged ADRs below establish seven Android
receiving-record locations. [The register](acceptance-placements.json) records
their actual accepted commits, Git trees, receiving reviews, immutable ADR and
receipt URLs, and SHA-256 digests recomputed from the accepted Git bytes. Its
source-snapshot entry identifies the inspected ledger version and digest.

## Current destination amendments

Every listed record is in `Pick-Your-AI/pick-your-ai-android`, under
`docs/delivery/android/work-packages/`, at its original relative path. The
historical intended repository was `Pick-Your-AI/pickyour.ai`.

| Android issue / record | Accepted placement authority | Normal delivery | Receiving composition review |
| --- | --- | --- | --- |
| #23 / `14.01.md` | [ADR 0001](https://github.com/Pick-Your-AI/pick-your-ai-android/blob/e86e8bd7645234e12b9887f1e6a0148a2d52073e/docs/decisions/0001-android-23-acceptance-record.md) | [#279](https://github.com/Pick-Your-AI/pick-your-ai-android/pull/279), `e86e8bd7` | [5562386507](https://github.com/Pick-Your-AI/pick-your-ai-android/pull/279#pullrequestreview-5562386507) |
| #20 / `01.01.md`, #24 / `01.02.md`, #34 / `01.03.md` | [ADR 0002](https://github.com/Pick-Your-AI/pick-your-ai-android/blob/93bebf787a091fe4858c1c70fd07cabefe17170f/docs/decisions/0002-android-foundation-records.md) | [#297](https://github.com/Pick-Your-AI/pick-your-ai-android/pull/297), `93bebf78` | [5562661670](https://github.com/Pick-Your-AI/pick-your-ai-android/pull/297#pullrequestreview-5562661670) |
| #25 / `01.05.md` | [ADR 0003](https://github.com/Pick-Your-AI/pick-your-ai-android/blob/68e52dd9c79cefe97af65e8fd1e86e4b72d2c42c/docs/decisions/0003-android-25-acceptance-record.md) | [#322](https://github.com/Pick-Your-AI/pick-your-ai-android/pull/322), `68e52dd9` | [5563048963](https://github.com/Pick-Your-AI/pick-your-ai-android/pull/322#pullrequestreview-5563048963) |
| #47 / `01.06.md` | [ADR 0004](https://github.com/Pick-Your-AI/pick-your-ai-android/blob/b6935a8ee7843831f90b0219c8794071557c71d4/docs/decisions/0004-android-47-acceptance-record.md) | [#318](https://github.com/Pick-Your-AI/pick-your-ai-android/pull/318), `b6935a8e` | [5563081505](https://github.com/Pick-Your-AI/pick-your-ai-android/pull/318#pullrequestreview-5563081505) |
| #35 / `01.04.md` | [ADR 0005](https://github.com/Pick-Your-AI/pick-your-ai-android/blob/4c753bd69f3857d9b15051be86078948e61074ac/docs/decisions/0005-android-35-acceptance-record.md) | [#347](https://github.com/Pick-Your-AI/pick-your-ai-android/pull/347), `4c753bd6` | [5563464371](https://github.com/Pick-Your-AI/pick-your-ai-android/pull/347#pullrequestreview-5563464371) |

The receiving reviews retain their substantive source-review links and exact
composition limits. These accepted commits supply the ADRs' stated effective
events; their prospective pre-merge wording is preserved in the immutable
documents. The register pins placement-adoption evidence. It does not assert that
every receipt's current contents still equal that original version: Android #23's
receipt has later changes. Refresh the destination's current accepted record and
its review history before consuming a new implementation or decision revision.

## Preserved history and authority

[INDEX.md](INDEX.md) shows the seven adopted destinations with pinned receipt
links. [coverage.json](coverage.json) changes only `acceptance_repository` and
adds `acceptance_placement_amendment` on those seven issue rows. The original
relative paths, named outputs, captured body digests, acceptance criteria, steps,
validation, review text, ownership and Project fields remain the publication
snapshot. The top-level note explains the distinction between current placement
and captured history; the historical `delivery_review_boundary` is retained.

Every other Android coordinate remains at its original intended website location,
including #48 / `02.01.md`. Apple named-output and ADR/path gates remain as
captured. No receipt location follows merely from issue closure, code placement
or a passing test. [MIGRATION.md](MIGRATION.md), the
[issue migration map](issue-migration.json) and [Project snapshot](project-fields.json)
retain their original statements and identities. The placement rule in that
history explicitly permits later accepted decisions; this register supplies the
dated exceptions without rewriting that history.

Android's current criterion ledger remains the authority for its criterion-level
acceptance and limitations. This research index is a location handoff, not a
second completion ledger. Each client's runtime, physical-device, service,
operating and release acceptance retains its own evidence. The canonical shared
website and research authorities in [SHARED.md](SHARED.md) remain in their existing
repositories; the #35 decision-record move does not move the shared backend into
Android or establish a live operating commitment.

## Validation and subsequent amendments

`python prompts/mobile/validate_prompts.py` reads the register and coverage with
duplicate-key, non-finite-number and overflow rejection. The placement helper
uses explicit checks under normal and optimized Python. It permits exactly these
five amendments and seven issue/path pairs, requires their known accepted Git,
PR and review identities, and checks closed shapes, immutable URL relationships,
digest syntax, coverage markers and exact index destinations.

Restoring the seven previous repositories and removing only their new amendment
markers must reproduce the canonical digest of all 258 original issue records.
That check preserves every captured field and row order, including all other
Android and Apple coordinates. It prevents an unrelated source, criterion, owner
or valid-looking filename change from being hidden in a placement amendment.
The optional live Project/source audit remains a separate comparison and was not
run or replaced by this bounded handoff.

Offline validation does not contact GitHub, authenticate review authors or merge
state, recompute remote artifact hashes, approve source rights, or establish
current issue completion. A reviewer must read the actual delivering PR and
receiving reviews, verify the accepted commit/tree, and hash `git show
COMMIT:PATH` bytes for every pinned ADR and receipt. A digest is an identity check,
not acceptance authority.

For another accepted placement, first identify its explicit ADR, delivered record
and independent receiving review. Refresh all current destinations and active
work, then extend this finite register and the helper's reviewed scope through a
normal research PR. Preserve every earlier accepted exception, exact historical
coordinate and snapshot field. Any intentional new source snapshot requires its
own explicit review; changing the preservation digest is not a way to infer an
unreviewed relocation. Run the focused negative tests and all commands in
[RESEARCH_WORKFLOW.md](../../docs/RESEARCH_WORKFLOW.md) before publication.
