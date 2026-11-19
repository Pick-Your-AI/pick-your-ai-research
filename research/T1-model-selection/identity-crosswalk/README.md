# T1 identity crosswalk, version 1

Refs #509 and #524. **Partial research assessment; no catalog promotion.**
This closed cohort contains every one of the 248 candidate rows already committed
at `d58106750bb76f72c270653993edf808f29c49bb`. It adds no candidates, broader
reference-directory scope, new contract, publication pilot or production data.
It can be reviewed independently of the unmerged Stage 0 proposal in #513.

`manifest.json` binds the exact inventory, source register and six comparison
notes by SHA-256. `rows.jsonl` has one UTF-8 JSON object per candidate in inventory
order. `row_index` is zero based; `row_sha256` hashes the entire inventory record
serialized with sorted keys, UTF-8, no ASCII escaping and compact separators.
These identify a historical research row, never a canonical model or checkpoint.
The source register's existing `accessed_on`, evidence grade and verification text
remain authoritative for the inherited observation. The manifest's `assessed_on`
is only the date of this local derivation. No new vendor retrieval, source check,
inference, API execution, rights decision or independent measurement is claimed.

Each row preserves the recorded artifact type and source IDs, adds exact local
claim-note path/line pointers and qualifies its identity references. A source
citation means the existing research claim was read; it does not mean the primary
page was fetched again. Both input hashes and claim-note references must match
before this version passes validation. `verification: local_derivation_only`
applies to every row, including the hand-interpreted composite cases.

| Assessment | Candidate rows | What the recorded evidence establishes here |
| --- | ---: | --- |
| `recorded_repository_locator` | 80 | Candidate spelling equals a Hugging Face repository path in its own recorded pinned document URL. This establishes a recorded locator, without re-reading the remote document or selecting weight bytes. |
| `recorded_api_selector` | 11 | Six Runway B16 and five BytePlus B32 API/route names are recorded in the existing claim notes. Their selector strings do not establish immutable releases or complete offerings; this assessment retains the dated observations without fresh corroboration. |
| `recorded_snapshot_name` | 1 | R26 distinguishes `omni-moderation-2024-09-26` from `latest`; its source URL names the alias. Route/snapshot binding remains open. |
| Composite/family/recipe dispositions | 15 | Three bundles, four pipelines, three recipes, two model families, one service, one UI family and one artifact family need distinct identity treatment. Each carries its own `disposition_note`. |
| `candidate_requires_identity_review` | 141 | Retained candidate and source pointers; family/release/artifact/offering relations remain unresolved by this assessment. |

These are candidate-row counts, not counts of deduplicated entities, publishable
records or deployed models. Unique names and shared source groups prove neither
identity nor difference. No duplicate, alias, deprecation or canonical-family
relation is inferred from spelling, branding or the date-like suffix of an ID.
Every row retains unresolved semantic duplicate/alias review. Existing candidate
caveats, including lifecycle observations, stay in the pinned inventory/notes;
this crosswalk does not upgrade their cutoff or settle them.

`identity_refs` permits only recorded repository locators, component **labels**,
API selectors and the named snapshot. A document commit is stored only as
`document_revision`. It is never a checkpoint hash, release pin, weight license
or proof that every file at that repository revision was selected or inspected.
Component labels record the source note's names/roles, without inventing exact
constituent artifacts. Unselected constituents, releases and offers stay open.
For example, the MediaPipe `.task` rows preserve detector/landmarker composition;
Hunyuan shape/paint and MiniMax FL2VA/Ref2VA remain separate labels; Graphormer is
an unselected recipe here, without claiming that no pretrained checkpoints exist.

The following versioned vocabulary factors repeated follow-up text out of rows.
`known_unknowns` names a profile; `next_action` names its required action. All
profiles also retain semantic duplicate/alias review and field/intended-use rights.
The row's pinned `selection_caveat` and any `disposition_note` add specific limits.

| Unknown profile | Unresolved identity fields | Action code and meaning |
| --- | --- | --- |
| `identity_unresolved` | Family relation, exact release, selected artifact or offering | `review_identity`: review the cited claim/source scope and resolve each applicable identity without filling unsupported fields. |
| `checkpoint_unresolved` | Selected checkpoint filenames/bytes/hashes, release and offering relations | `select_checkpoint`: select exact artifacts independently of source-document revisions and match runtime/terms. |
| `offering_unresolved` | Immutable release, endpoint/operator, region, entitlement and selector lifecycle | `bind_offering`: bind the recorded selector to the selected offering; preserve publisher/reseller distinctions. |
| `snapshot_route_unresolved` | Route/snapshot binding, alias target at selection, region and entitlement | `bind_snapshot`: retain snapshot versus alias and obtain the exact selected route binding. |
| `composition_unresolved` | Constituent artifacts/revisions, composition, dependency terms and selected offer | `resolve_constituents`: identify the selected components separately, then bind their composition. |
| `trained_artifact_unresolved` | Fitted artifact, dataset/features/preprocessor, serialization/runtime and artifact rights | `select_fitted_artifact`: select actual trained bytes; an algorithm/library/package release is insufficient. |
| `family_unresolved` | Selected family member/release/checkpoint or service selector | `select_family_member`: select the intended family/member before counting or promoting an entity. |
| `service_release_unresolved` | Endpoint/interface versus model release, task/export version and offering conditions | `bind_service_release`: bind these separately; an API v2 label is not an immutable model version. |
| `ui_identity_unresolved` | UI generation/editing identity, permitted access and supported representation | `select_ui_identity`: establish the selected UI identity; route representation questions through #40. |

No frozen-v1 mapping is attempted. Required `spec_model` fields such as
`provider_ref`, supported `model_type`, input/output modalities, token maxima,
`access_modes` and `model_formats` require their own exact claim evidence and
applicable kind/consumer decisions. This file supplies none of those missing
required fields and makes no assertion that the primary sources lack them.
T1/#5–#7 retain model/route decisions; T3/#14 retains embeddings; #40 owns schema
and identity/projection review; #41/#60 retain source/field/use rights. Consumer
acceptance, rights eligibility and #61/#62 runtime/evaluation evidence remain
separate. This partial contribution cannot close #509 or #524.

Run `python scripts/validate_t1_identity_crosswalk.py` from the repository root.
The standard repository unittest discovery also runs
`tests/test_t1_identity_crosswalk.py`, including a current-input check and
synthetic negative controls. Run the focused suite in both interpreter modes:

```bash
python -m unittest discover -s tests -p test_t1_identity_crosswalk.py -v
python -O -m unittest discover -s tests -p test_t1_identity_crosswalk.py -v
```

Validation is offline and read-only. It rejects changed input bytes, missing or
reordered rows, broken claim pointers, unsupported states and attempts to turn
source-document revisions into artifact identities. It checks structural
consistency, not the truth of manual interpretations or vendor claims. Review
new inputs and dispositions through a successor version; do not merely replace
hashes to clear a stale-input diagnostic. This version is deliberately closed to
its dated cohort, without a freshness guarantee or recurring retrieval process.
