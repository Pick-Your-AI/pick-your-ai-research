# Pinned checkpoint NOTICE evidence

Issue: #6; consumer: #30/#33; contract routing: #40. Source check:
**2026-10-18 UTC**. Grade: primary publisher metadata and licence text,
source checked / unverified. This addresses the bounded file-presence question
raised in [the #30 sufficiency review](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/30#issuecomment-6245639699).
It is not a determination of permission for a proposed training or redistribution.

## Inspected repository distribution

| Identity / observation | Finding |
| --- | --- |
| Repository | `Qwen/Qwen3-8B` |
| Immutable revision | `b968826d9c46dd6066d109eabc6255188de91218` |
| Primary file inventory | [Revision-specific model API](https://huggingface.co/api/models/Qwen/Qwen3-8B/revision/b968826d9c46dd6066d109eabc6255188de91218); returned SHA matches the requested revision. The [recursive tree API](https://huggingface.co/api/models/Qwen/Qwen3-8B/tree/b968826d9c46dd6066d109eabc6255188de91218?recursive=true&expand=false) independently returns the same 15 file paths, with no pagination link |
| Listed paths | 15; reproduced below |
| Separate NOTICE text file | **Not present in the inspected repository inventory**; no listed filename is `NOTICE` or a `NOTICE.*` variant |
| Licence text | [Pinned LICENSE](https://huggingface.co/Qwen/Qwen3-8B/blob/b968826d9c46dd6066d109eabc6255188de91218/LICENSE), Apache-2.0 |
| Locally fetched licence bytes | 11,343; SHA-256 `832dd9e00a68dd83b3c3fb9f5588dad7dcf337a0db50f7d9483f310cd292e92e` |

Only public metadata and the small licence text were fetched for this check.
The filenames identify the distribution; none of the weight shards, tokenizer
or model configuration files was downloaded by this follow-up. An earlier
tokenizer-only experiment has its own evidence and does not supply weight evidence.

Complete `siblings[].rfilename` inventory returned by the pinned API:

```text
.gitattributes
LICENSE
README.md
config.json
generation_config.json
merges.txt
model-00001-of-00005.safetensors
model-00002-of-00005.safetensors
model-00003-of-00005.safetensors
model-00004-of-00005.safetensors
model-00005-of-00005.safetensors
model.safetensors.index.json
tokenizer.json
tokenizer_config.json
vocab.json
```

## Meaning for the proposed notice predicate

[Apache-2.0 section 4(d)](https://www.apache.org/licenses/LICENSE-2.0)
conditions the NOTICE-copy requirement on a NOTICE text file being included in
the distribution. The finding here is a file-inventory observation for one
exact repository revision. It does not establish that a converter, packaged
runtime, adapter, downstream derivative or another distribution lacks notices.
Retaining the licence, change indications and applicable source notices under
sections 4(a)–(c) remains a separate question; a missing separate NOTICE file
does not erase those requirements or grant broader rights.

For #33's proposed `base_notice_file_present`, this inventory supports a
note-only **false for this inspected repository distribution**, not a global
false for Qwen or an executable v1 field. A different artifact/revision needs
its own inventory and lineage. Missing or incomplete inventory evidence must
stay unknown rather than borrowing this result. The normalized licence
identifier, obligation answers, inheritance and migration remain #30/#40 work.

API-only GPT-5.4, Sonnet 5.5 and Gemini 2.5 entries in the earlier T1 slice do
not identify a downloadable checkpoint distribution in the inspected sources;
their NOTICE-file presence is not assessed here. The expanded research inventory
is not audited by this one-checkpoint follow-up. No catalogue proposal,
provenance grade, frozen schema, issue acceptance or receiving-owner receipt is
changed by publication of this note.
