# Model research coverage - draft snapshot

Status: **in progress; partial research, not accepted completion**. Captured 2026-10-17 for publication on the research branch.

This index describes the captured [research inventory](model-research-inventory.json), containing 248 records and 189 primary-source groups in the [source register](model-research-sources.md). The counts below are derived from that inventory, not external measurements. Records may describe model variants, families, bundles or recipes; they are not a count of distinct deployment-ready artifacts. A record may participate in more than one task family.

## Research pages

- [Language, code, encoders and moderation](language-models.md)
- [Perception, OCR and document models](perception-models.md)
- [Embeddings and rerankers](retrieval-models.md)
- [Image, video, 3D and motion generation](generative-media-models.md)
- [Speech, music and audio models](audio-models.md)
- [Forecasting, tabular, scientific and robotics models](specialized-models.md)

The row-to-source mapping is preserved in the inventory and the [machine-readable source register](model-research-sources.json). Publisher statements remain source checked, not independently exercised capabilities. Access, licence, version, route and missing-limit caveats remain attached to their rows.

## Captured task-family coverage

| Task family | Inventory rows |
| --- | --- |
| `3d_assets` | 6 |
| `anomaly_detection` | 2 |
| `atomistic_materials` | 1 |
| `audio_classification` | 4 |
| `audio_enhancement` | 1 |
| `audio_generation` | 3 |
| `audio_separation` | 4 |
| `audio_understanding` | 4 |
| `biomolecular` | 3 |
| `classification` | 5 |
| `code_generation` | 10 |
| `depth_geometry` | 3 |
| `diarization` | 6 |
| `document_layout` | 1 |
| `encoder_understanding` | 1 |
| `forced_alignment` | 1 |
| `genomics` | 1 |
| `geospatial` | 1 |
| `graph_learning` | 1 |
| `image_editing` | 30 |
| `image_generation` | 35 |
| `image_restoration` | 1 |
| `language_reasoning` | 12 |
| `language_translation` | 1 |
| `moderation` | 1 |
| `motion_avatar` | 3 |
| `multimodal_embedding` | 12 |
| `multimodal_understanding` | 13 |
| `music_generation` | 8 |
| `object_detection` | 11 |
| `ocr_document` | 6 |
| `pose` | 5 |
| `realtime_speech` | 7 |
| `recommendation` | 1 |
| `reranking` | 10 |
| `robotics_action` | 5 |
| `segmentation` | 3 |
| `sparse_multivector` | 7 |
| `speech_recognition` | 17 |
| `speech_synthesis` | 21 |
| `speech_translation` | 6 |
| `tabular_prediction` | 4 |
| `text_embedding` | 14 |
| `time_series` | 3 |
| `token_classification` | 1 |
| `tracking` | 3 |
| `video_editing` | 12 |
| `video_generation` | 22 |
| `visual_representation` | 1 |
| `voice_activity` | 1 |
| `voice_conversion` | 5 |
| `voice_design` | 1 |
| `weather_forecasting` | 1 |
| `world_spatial` | 4 |

## Remaining work and acceptance

This is a publication checkpoint for ongoing research. It does not establish exhaustive enumeration, complete provider-route coverage, comparative quality, permission to reuse artifacts, hardware fit, or a complete cost estimate.

The existing [model](ai-model.md), [provider](model-provider.md), [context](context-window.md), [acceptance](acceptance-matrix.md) and [handoff](handoffs.md) records remain authoritative for the ongoing T1 submission. Embedding and reranking product decisions retain their T3 ownership. Unsupported task types, modalities and limit units require versioned central review through issue #40; frozen v1 is unchanged.

Issues #4-7 and #49 remain open until their live acceptance criteria and real consuming-owner decisions are satisfied. Further source verification, taxonomy refinement and integration of the expanded findings into the decision records remain in progress. Use Refs for this partial checkpoint.
