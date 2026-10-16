# Supplemental Granite 3.1 short MoE protocol — 2026-10-16

Written before download or GPU inference. User direction: use spare local
capacity and record remaining coverage gaps. Do not evict workloads, delete
other files, buy compute or enlarge the device reservation.

The prior Granite3.0 profile remains unexecuted: its official preflight failed
the 12 GiB disk guard. A newly identified official BF16 artifact avoids its
5.54 GB FP32 source download. This is a separate supplemental candidate and
does not replace the unexecuted OLMoE matrix or waive the original disk guard.

Candidate `ibm-granite/granite-3.1-1b-a400m-instruct`, revision
`0da7a48b0276d500ce5922fd2b33944091fc6c09`; publisher IBM Granite;
Apache-2.0, public ungated trained model. Metadata accessed 2026-10-16:
[card](https://huggingface.co/ibm-granite/granite-3.1-1b-a400m-instruct/blob/0da7a48b0276d500ce5922fd2b33944091fc6c09/README.md),
[config](https://huggingface.co/ibm-granite/granite-3.1-1b-a400m-instruct/blob/0da7a48b0276d500ce5922fd2b33944091fc6c09/config.json),
[pinned artifact metadata](https://huggingface.co/api/models/ibm-granite/granite-3.1-1b-a400m-instruct/revision/0da7a48b0276d500ce5922fd2b33944091fc6c09?blobs=true).
The config identifies `GraniteMoeForCausalLM`, 24 layers, hidden1,024, 16
attention heads, 8 KV heads, derived head dimension64, intermediate512,
32 experts/top-k8, tied embeddings and maximum131,072 positions. Card prose
contains a dense-architecture description inconsistent with its model class
and MoE configuration/table; retain that discrepancy and use the pinned
implementation/configuration as the architecture input.

The BF16 safetensors contains 1,334,628,352 parameter elements, predicting
2,669,256,704 parameter bytes. File `model.safetensors` is 2,669,283,096 bytes,
publisher LFS SHA-256
`ac02591061f1344027a7e7b11dbb4143f75f166c47dc09b742f5de3ab1dde1d1`.
Verify local size/hash after download; do not present publisher metadata as a
local observation before that. The only download is this single weight file,
the pinned tokenizer/config and small model card. No other formats or datasets.
Keep the weights outside Git and publish only permitted metadata/counters.

Pre-download screen: `nvidia-smi` free >=4,096 MiB, host available physical RAM
>=12 GiB, temporary-volume free >=6,412,308,016 bytes. This disk threshold is
2×exact artifact size +1 GiB; it is specific to this smaller artifact and
preserves headroom rather than reusing the 12 GiB FP32-transfer guard. If any
screen fails, record the exact observation and do not download or run.

If admitted, supplemental cell **GM1** only: prompt256/active1/queue0, native
BF16 KV, BF16 weights without quantization, 32 decode forwards and 33 predicted
tokens (288 terminal cache positions). Three serial fresh Python processes;
same seed6109, synthetic input text, SDPA eager, no graph/compile/offload,
TP1/PP1 and phase-specific synchronized allocated/reserved counters as dense.
Reuse Python3.12.11/PyTorch2.10.0+cu130/Transformers5.0.0. The supplemental
runner has a separate hash and protocol hash; the original dense source and
15 dense run pins remain unchanged.

Recheck `nvidia-smi` >=4,096 MiB before each process. Own allocator cap <=3 GiB.
Predicted weights +12,582,912-byte prefill KV +256 MiB workspace scenario is
below 3 GiB. The workspace allowance is an estimate, not measured Granite
overhead. Actual errors or OOM are preserved and stop further repetitions;
there is no hidden cap increase or parameter change. Compare only native KV
tensor payload with its formula; competitor/runtime error pairs remain zero
unless a semantically matching estimate is actually obtained.

OLMoE M1–M4 and Granite3.0 remain distinct unexecuted cases. Granite3.1
2,048-token, active2 and INT4 cells are deferred: this small shared-device
envelope does not establish workspace/allocator capacity for them. GM1 is
real short-case MoE evidence if successful, not completion of varied MoE
coverage or universal device fit. All review and acceptance remain with live
#7/#10/#11 owners and the coordinator. No ResourceEstimate is created.
