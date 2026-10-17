# T1-TAX1: task-specific model evidence and limits

Issues:#6/#7; central entry:#40; consumers:#2/#3/#10/#11/#14/#16/#25/#30/#35/#36/#37/#39/#41/#42. Status:**proposal**, not accepted contract. Preserve the complete imported v1.

## Concrete problem and evidence

The [source-backed taxonomy](model-taxonomy.md) identifies text generators alongside discriminative perception, embeddings/rankers, speech/music, editable media, spatial/world, predictive/scientific and action models. [`spec_model`](../../contracts/v1/schemas/catalog-item.schema.json) requires two positive token ceilings even when a source documents only image dimensions, audio duration, table rows, forecast steps or geometry. Model type and output semantics are also insufficient for several tasks. No fake value or semantic cast is proposed to pass validation.

Examples with primary sources: [gpt-image2.5 dimensions](https://developers.openai.com/api/docs/guides/image-generation); [ElevenLabs character/speech tasks](https://elevenlabs.io/docs/overview/models); [ColPali multivectors/backbone](https://huggingface.co/vidore/colpali-v1.3/blob/b5c6dd62125326e6f0b540c1f7b36e901cdc0a11/README.md); [TimesFM weights/serving distinction](https://github.com/google-research/timesfm/blob/e51928e27119cb17bebc005be2696b75e0a9e688/README.md); [TRELLIS2 mesh/PBR](https://huggingface.co/microsoft/TRELLIS.2-4B/blob/af44b45f2e35a493886929c6d786e563ec68364d/README.md). Accessed2026-10-17; checked publisher facts, no inference measurement.

## Proposed next-version design questions

1. Separate **task tags**, input/output representation schemas and architecture from a small model-type enum. Use an extensible registry with affected-owner review; do not copy the research tags into canonical enums without agreement.
2. Make limit applicability explicit: name, value/range, unit, role/stage, semantics, hard/recommended/example/training qualifier and conditions. Reuse CD-11 shared/separate token semantics where appropriate; token fields are not mandatory for a non-token task merely because it is an AI model.
3. Preserve exact artifact composition: base/adapter/head/codec/processor/upsampler/pipeline/bundle; checkpoint and code/runtime revisions; provider alias policy; voice and robot embodiment. Build on CD-6 and existing `provided_by`, not a parallel provider relationship.
4. Extend representations deliberately for PDF, SVG, masks/boxes, sparse and multivector outputs, mesh/splat/PBR, numeric time series, biomolecular/atomic and action payloads. `structured` serialization alone must not imply semantic compatibility.
5. Capture code, checkpoint, backbone, adapter, data/reference and service/output rights separately, with answerable conditions and source versions. Do not replace #30 interpretation or #41 reuse review with a universal boolean.
6. Price model-specific meters only after #39 defines units and aggregation, then central versioning/migration through CD-7. This proposal adds no rates and does not hide uncovered costs.

## Illustrative research-only fixtures

- Image generator: admitted width/height/pixel area and reference roles; no invented language-output ceiling. A shape rejected by a documented hard image budget fails that shape predicate, not an unrelated text context test.
- Speech model: character or seconds/sample/channel bounds scoped to file/stream route. A training-sequence length does not become an inference maximum; unknown source terms remain unresolved.
- Retrieval: ColPali adapter/backbone identity plus multivector similarity. A consumer accepting one dense vector cannot silently accept a token matrix simply because both expose a dimension.
- Forecast model: time-step window, future covariates and prediction horizon. Do not encode8192 time steps as8192 text tokens. User data/schema compatibility is separate from pretrained-weight access.
- Action model: explicit observation/action coordinates, calibration and embodiment. A video output is not a motor-control policy; no robot execution or physical suitability is inferred.

These examples are synthetic design cases tied to real source constraints; none is a production CatalogItem or observed runtime result. Outcomes remain pass/fail/unknown/skipped independently of severity. Continue the accepted owner policy: component-scoped applicability, conservative bounded estimates, native limits without extension evidence, and review for missing resource evidence.

## Migration and review

#40 owns the versioned design; #14 representation/index handoff, #30 conditional rights, #10/#11 capacity and support, #36 task metrics, #39 billing, #41 provenance/reuse, #42 saved-build invalidation and #37 deployment artifacts must review affected changes. Keep original v1 bytes and existing valid records; intake new tasks note-only until the new semantics/readers/tests are agreed. Supply versioned examples, backwards compatibility rules and a migration plan together. Schema validity will not certify truth, rights, quality or deployment.
