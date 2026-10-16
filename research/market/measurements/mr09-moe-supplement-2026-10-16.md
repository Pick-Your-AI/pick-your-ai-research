# Supplemental small trained-MoE feasibility screen — 2026-10-16

Prepared before any supplemental weight download or GPU inference. The user
authorizes spare local capacity only; no other workload may be evicted. The
completed dense matrix's runner/protocol hashes remain unchanged.

Candidate: `ibm-granite/granite-3.0-1b-a400m-base`, immutable revision
`d91cbed802d85eb1b32374623331f6ab2b37403a`. Publisher IBM Granite;
Apache-2.0 label, public ungated trained MoE. Accessed 2026-10-16.
Primary [pinned metadata](https://huggingface.co/api/models/ibm-granite/granite-3.0-1b-a400m-base/revision/d91cbed802d85eb1b32374623331f6ab2b37403a?blobs=true),
[model card](https://huggingface.co/ibm-granite/granite-3.0-1b-a400m-base/blob/d91cbed802d85eb1b32374623331f6ab2b37403a/README.md),
[config](https://huggingface.co/ibm-granite/granite-3.0-1b-a400m-base/blob/d91cbed802d85eb1b32374623331f6ab2b37403a/config.json),
and [weight index](https://huggingface.co/ibm-granite/granite-3.0-1b-a400m-base/blob/d91cbed802d85eb1b32374623331f6ab2b37403a/model.safetensors.index.json)
are metadata evidence, not reproduced memory evidence. Shard checksums below
are publisher LFS metadata; they become local verified checksums only after
actual download and comparison.

- 1,384,956,928 stored FP32 parameter elements; 5,539,827,712 tensor bytes.
  Explicit BF16 loading predicts 2,769,913,856 parameter bytes. This is a dtype
  conversion, not four-bit weight quantization or KV quantization.
- 24 layers, hidden 1,024, 16 attention heads, 8 KV heads, derived head dimension
  64, intermediate 512, 32 local experts and 8 selected per token; 4,096 positions.
  Full resident weights include all experts. Native BF16 KV is 49,152 bytes per
  cached token and active sequence: 12,582,912 bytes at prompt256/active1.
- `model-00001-of-00002.safetensors`: 4,897,844,128 file bytes; publisher SHA-256
  `acc1df483e5094838cf127a8e8f301b058a1f5d6ec51adbb0702c2dd92bb6980`.
- `model-00002-of-00002.safetensors`: 642,009,944 file bytes; publisher SHA-256
  `0e59bf9c47f471d140f740f824ed361407cffca07b2affc8d8f759d3451b932d`.
  Total download 5,539,854,072 bytes including safetensors headers, plus bounded
  config/tokenizer/index files only. No alternate formats, datasets or extras.

Before downloading weights, capture one official post-dense-matrix preflight:
`nvidia-smi` reported free at least 4,096 MiB; host available physical RAM at
least 12 GiB via Windows `GlobalMemoryStatusEx`; temporary-volume free disk at
least 12 GiB via `shutil.disk_usage`. Otherwise record unexecuted capacity/access
gap and do not download. Recheck GPU guards immediately before each run. These
conservative screens are task boundaries, not a calibrated fit prediction.

If admitted: one new supplemental cell `GM1`, prompt256, active1, zero queue,
BF16 runtime weights and native BF16 dynamic KV, 32 decode forwards (33 predicted
tokens; 288 final cache positions). Three serial fresh-process repetitions,
seed6109, same synthetic text, SDPA eager/no compile/no graph/no offload, exact
same phase synchronization/counter semantics as dense protocol. Allocate at
most 3 GiB in this process. Leave existing processes untouched. Stop on a failed
guard or first OOM/runtime error and preserve its exact phase and counters;
do not force a successful repeat by silently changing settings.

Screen only the short cell: predicted BF16 weights + short KV + a predeclared
256 MiB workspace allowance is below 3 GiB; the allowance is a safety scenario,
not independently measured Granite overhead. Source inspection shows routing
expands token activations by top-k=8, so long context/batch workspace differs.
The dense 2,048-token observations already exceed 400 MiB above model payload
at prefill; the remaining ~430 MiB after this MoE's weights does not justify
assuming longer context or active2 fits. Defer Granite2048/active2/INT4 unless
its measured short-case results and a separately dated safe protocol warrant
expansion. OLMoE and multi-GPU gaps remain separately recorded.

Use the existing Python3.12.11/PyTorch2.10.0+cu130/Transformers5.0.0 build. The
installed `granitemoe` source contains `GraniteMoeForCausalLM`, SDPA support,
DynamicCache and logits-to-keep; source existence is not an executed support
claim. Pin the supplemental runner source and protocol hash before execution;
retain the original dense runner if a parameterized revision is needed.
No competitor error pair exists merely by changing model architecture.
Record failed/unexecuted cells without numerical errors. No acceptance or
MVP threshold is invented. #7/#10/#11 human review remains pending.
