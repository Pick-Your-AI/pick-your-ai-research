# MR09 OLMoE artifact and copy plan — 2026-10-19

This dated, unexecuted engineering plan resolves the shard inventory and selects
an explicit future loader and copy budget for **M1–M4** in the
[original MoE coverage plan](mr09-moe-plan.json). It adds publisher metadata and
source-derived allowances. It does not add a model run, measured memory peak,
reserved device, accepted estimator pair or ResourceEstimate. The original
2026-10-16 plan and every recorded observation retain their original bytes.

The machine-readable [version 1 plan](mr09-olmoe-artifact-copy-plan-v1.json) uses a
[research-only schema](../../../schemas/mr09-olmoe-artifact-copy-plan.schema.json).
It is separate from frozen AI Builder v1 contracts. Refs
[#61](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/61); that issue's
remaining empirical coverage and receiving criteria remain open.

## Immutable inventory and observed scope

The model is `allenai/OLMoE-1B-7B-0924-Instruct` at
`7f1c97f440f06ce36705e4f2b843edb5925f4498`, with BF16 safetensors and no weight
quantization. At **2026-10-19T18:14:16.779205+00:00**, the
[revision-specific publisher API](https://huggingface.co/api/models/allenai/OLMoE-1B-7B-0924-Instruct/revision/7f1c97f440f06ce36705e4f2b843edb5925f4498?blobs=true)
returned this exact revision. Its 3,843-byte response has SHA-256
`7ddb8aea77c0e462e696ca723d032f29d0d9713b27449238a0e4504947f035ef`.
The model card's Apache-2.0 label is publisher metadata, not a grant inferred
from a checksum. Only small metadata and project-derived planning are submitted.

| Weight shard | Publisher file bytes | Publisher LFS SHA-256 | External manifest |
| --- | ---: | --- | --- |
| `model-00001-of-00003.safetensors` | 4,997,744,872 | `6c79ac0487c3f23e8ee3d38752197d1e4a1a39d6c1438ec5fd7862874bb19321` | [Shard 1](../../../evidence/mr09-olmoe-0924-instruct-shard-01.json) |
| `model-00002-of-00003.safetensors` | 4,997,235,176 | `b58ca7a9f28f35d76b56b0ec40fc46c356fd84ccf078083b251a3ad6a2da9a35` | [Shard 2](../../../evidence/mr09-olmoe-0924-instruct-shard-02.json) |
| `model-00003-of-00003.safetensors` | 3,843,741,912 | `e93653ed509223e63eabae6f72ac8ea5a41115c5c7785574b9b2068ca0961c45` | [Shard 3](../../../evidence/mr09-olmoe-0924-instruct-shard-03.json) |

**No weight shard was downloaded or locally checksum-verified.** These three
hashes and lengths come from the publisher's LFS metadata. The external
manifests say so explicitly and require eventual complete-file length and
checksum verification before loading. They use immutable, credential-free
locators; they do not contain model data.

| Other loading file | Publisher bytes | Observation on this date |
| --- | ---: | --- |
| `config.json` | 759 | Complete small file read; SHA-256 recorded and Git blob matched |
| `generation_config.json` | 120 | Complete small file read; SHA-256 recorded and Git blob matched |
| `model.safetensors.index.json` | 287,214 | Complete small file read; SHA-256 recorded and Git blob matched |
| `special_tokens_map.json` | 433 | Complete small file read; SHA-256 recorded and Git blob matched |
| `tokenizer.json` | 2,115,598 | Publisher size/Git blob only; payload was not downloaded |
| `tokenizer_config.json` | 5,986 | Complete small file read; SHA-256 recorded and Git blob matched |

The separately read 6,550-byte model card is provenance, outside the six-file
loading allowance. Each observed small-file SHA-256 and publisher Git blob is
recorded in the plan. The
[config](https://huggingface.co/allenai/OLMoE-1B-7B-0924-Instruct/blob/7f1c97f440f06ce36705e4f2b843edb5925f4498/config.json)
and complete
[weight index](https://huggingface.co/allenai/OLMoE-1B-7B-0924-Instruct/blob/7f1c97f440f06ce36705e4f2b843edb5925f4498/model.safetensors.index.json)
agree with **16 layers, 64 experts per layer, three expert projections and
3,219 tensor names**. All 3,072 expected expert names are present, with 147
shared tensors. Every index entry names one of the three listed shards.

The weight files total **F = 13,838,721,960 bytes**. The index declares
**W = 13,838,323,712 tensor bytes**, leaving 398,248 bytes of file/header
overhead. The six metadata files total 2,410,110 bytes, so the full loading
artifact set is **B = 13,841,132,070 bytes**. Repository-wide storage counters
and active-expert counts are not substituted for these complete stored weights.

## Selected loader and copy behavior

The selected future profile retains Python 3.12.11, PyTorch 2.10.0+cu130,
Transformers 5.0.0 and safetensors 0.7.0. This preparation did not install or
execute that ML stack. The reviewed Transformers source is literal commit
`08810b1e278938278c50153ee1edfd7a20a759da`; the plan pins the complete five
reviewed source files. This is upstream source review, not verification of an
earlier installed wheel or a future executable.

The source basis is:

- [`modeling_utils.py`](https://github.com/huggingface/transformers/blob/08810b1e278938278c50153ee1edfd7a20a759da/src/transformers/modeling_utils.py): the ordinary model skeleton uses meta initialization; the safetensors route opens the checkpoint files and prepares lazy tensor slices. The old `low_cpu_mem_usage` argument is not a reliable copy-control switch in this version.
- [`core_model_loading.py`](https://github.com/huggingface/transformers/blob/08810b1e278938278c50153ee1edfd7a20a759da/src/transformers/core_model_loading.py): default asynchronous materialization can hold more work concurrently. `HF_DEACTIVATE_ASYNC_LOAD=1` selects deferred sequential materialization; absent device mapping, conversion targets CPU. `MergeModulelist` and `Concatenate` use stack/cat allocations.
- [`conversion_mapping.py`](https://github.com/huggingface/transformers/blob/08810b1e278938278c50153ee1edfd7a20a759da/src/transformers/conversion_mapping.py): OLMoE uses the MoE conversion route that stacks per-expert projections and concatenates gate/up tensors.
- [`modeling_olmoe.py`](https://github.com/huggingface/transformers/blob/08810b1e278938278c50153ee1edfd7a20a759da/src/transformers/models/olmoe/modeling_olmoe.py) and [`configuration_olmoe.py`](https://github.com/huggingface/transformers/blob/08810b1e278938278c50153ee1edfd7a20a759da/src/transformers/models/olmoe/configuration_olmoe.py): the packed expert dimensions and attention geometry determine the explicit payload terms; routing, masks and backend workspaces still require observation.

The chosen future controls are `HF_DEACTIVATE_ASYNC_LOAD=1` and
`HF_HUB_OFFLINE=1`; `from_pretrained` uses a pre-verified local directory,
`local_files_only=True`, `use_safetensors=True`, `trust_remote_code=False`,
BF16 dtype, SDPA attention, **explicit eager experts**, and no `device_map`.
After CPU conversion, the model moves to `cuda:0`. Attention selection does not
implicitly select the expert backend. There is one visible device and no
inference offload in this profile. Actual backend support remains unexecuted.

A future downloader would use exactly the nine loading files above, serial
same-volume partial files followed by verified rename, with no additional Hub
cache. That downloader and model runner are not supplied here. An eventual
runner must bind its own exact source, installed runtime and executable before
use; it must not reinterpret this data file as current hardware admission.

## Engineering allowances

The following are **selected planning allowances, not measured upper bounds or
fit guarantees**. They deliberately count a complete file-mapping allowance
and a complete parameter allowance separately, even where physical pages may
be shared. The sequential conversion allowance accounts for one packed
gate/up group of `64 × 2,048 × (2 × 1,024) × 2` = 536,870,912 bytes during
stack/cat overlap. It is additional to the final parameter payload.

| Planned resource term | Bytes |
| --- | ---: |
| Two complete loading artifact copies, `2B` | 27,682,264,140 |
| Storage reserve, 2 GiB | 2,147,483,648 |
| Derived storage budget | **29,829,747,788** |
| Selected available-storage screen, 28 GiB | **30,064,771,072** |
| Host file mapping allowance, `F` | 13,838,721,960 |
| Host parameter allowance, `W` | 13,838,323,712 |
| Additional one-group conversion allowance | 536,870,912 |
| Unmeasured host process reserve, 4 GiB | 4,294,967,296 |
| Derived host budget | **32,508,883,880** |
| Selected available-physical-RAM screen, 32 GiB | **34,359,738,368** |

The second full artifact copy is a conservative staging/recovery allowance,
not an observed duplicate. No current machine's available disk or RAM was
measured for this plan. The 4 GiB host reserve is an engineering choice; it is
not calibrated to the Python heap, native allocator, page residency or other
processes. A future run must observe the actual load peak and retain failures
even when these initial screens pass.

There is **no selected GPU process cap, GPU workspace allowance or device
reservation**. The old dense experiment's roughly 2 GiB process cap is unchanged
and is not sufficient for these weights. The old dense wrapper is not a MoE
runner: its model identity and small single-file download cap remain separate.
No resource-cap change or model download follows from this note.

## Preserved M1–M4 scope

For BF16 KV storage, the derived tensor payload per cached position and active
sequence is `2 × 16 layers × 16 KV heads × 128 head dimensions × 2 bytes`
= **131,072 bytes**. The original protocol's terminal cache positions are
prompt positions plus 32 decode forwards. These are accounting floors that
exclude runtime, allocator and expert/attention workspace.

| Cell | Prompt / terminal cache positions | Active sequences | Cache | Derived KV bytes | Stored weights + KV floor |
| --- | --- | ---: | --- | ---: | ---: |
| M1 | 256 / 288 | 1 | BF16 | 37,748,736 | 13,876,072,448 |
| M2 | 2,048 / 2,080 | 1 | BF16 | 272,629,760 | 14,110,953,472 |
| M3 | 2,048 / 2,080 | 2 | BF16 | 545,259,520 | 14,383,583,232 |
| M4 | 2,048 / 2,080 | 1 | Int4 if supported | Unknown | Unknown |

M4 does not receive a guessed quarter-size BF16 result. All four cells remain
unexecuted. The pinned config supports 4,096 positions, so an 8,192-position
claim is outside this plan. Multi-GPU topology is also outside this single-device
design and retains its separate evidence requirement.

## Repeatable local validation and remaining evidence

Using the repository's pinned Python validation dependencies, run from the
repository root:

```sh
python scripts/validate_mr09_olmoe_plan.py
python -m unittest discover -s tests -p test_mr09_olmoe_plan.py -v
python scripts/validate_research.py
```

The checker reads local JSON only. It validates schema, exact integer tokens,
unique named inventory, immutable manifest relationships, observed-versus-
publisher-only checksum scope, arithmetic, copy allowances, and unchanged
historical workload definitions. The normal repository test discovery includes
the new tests; no new workflow or native gate is added. Synthetic corruptions
and optimization-mode CLI controls stay in tests.

Passing these checks verifies internal consistency, not the truth of external
metadata, the future loader's runtime behavior or any model fit. Remaining work
still needs an authorized device/cap receipt, a separately pinned runner and
installed runtime, complete weight bytes and local checksums, observed host and
GPU peaks/workspaces, actual optional-cache support, the applicable multi-GPU
evidence, and matched estimator/runtime comparison acceptance. No existing
participant, publisher or hardware requirement is closed by this preparation.
