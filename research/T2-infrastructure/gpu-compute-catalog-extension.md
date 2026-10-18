# GPU / Compute: Blackwell family catalog extension + generic sizing model

Issue: [#10](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10) · Contract: 1.0.0 · Kinds: `accelerator`, `resource-estimate`
Status: research extension to the merged [gpu-compute.md](gpu-compute.md) decision record · Last researched: 2026-10-18
Refs #10 (partial: catalog extension + calibrated estimates + generic sizing model; CPU/edge and shared-memory representation remain open per the decision record's handoffs)

## Scope of this extension

The merged decision record (PR #75) supplied discrete datacenter GPUs (L40S, H100 SXM, MI300X) and one cloud profile. This extension adds the **NVIDIA Blackwell family** — datacenter, workstation (RTX PRO), and consumer (GeForce RTX 50) — plus a **generic parameterized sizing function** validated against **three real measurements** on a measured card. It is an extension, not a rewrite: it reuses the existing `accelerator` catalog-item shape, the `resource-estimate` contract, and the `sizing_examples.py` arithmetic.

Two conventions from the decision record are carried forward:
- **Capacity screen, not a fit guarantee.** A memory calculation passing does not establish model quality, engine support, an SLO, regional stock, or a reservation.
- **Incomplete precision = research note, not frozen catalog** (commit 43e8011). A card whose required fields are not fully sourced from a primary source is recorded here as a research note, not added to `catalog/proposals/`.

## What was added to the catalog (7 items)

Twelve cards are **fully sourced** from a primary source (all of `vram_gb`, `precisions`, `rated_power_w`, `interconnect` quotable — or power omitted by decision where the sources conflict) and are added as `accelerator` catalog items under `catalog/proposals/`. The per-card sourced facts, quotes, and conflict record live in the companion note [blackwell-accelerators.md](blackwell-accelerators.md):

| Catalog ID | Variant | VRAM | Rated power | Compute cap | Interconnect |
| --- | --- | --- | --- | --- | --- |
| `nvidia-geforce-rtx-5090` | GeForce RTX 5090 | 32 GB | 575 W | 12.0 | PCIe |
| `nvidia-geforce-rtx-5080` | GeForce RTX 5080 | 16 GB | 360 W | 12.0 | PCIe |
| `nvidia-geforce-rtx-5070-ti` | GeForce RTX 5070 Ti | 16 GB | 300 W | 12.0 | PCIe |
| `nvidia-rtx-pro-6000-blackwell-workstation` | RTX PRO 6000 Blackwell (Workstation Edition) | 96 GB | 600 W | 12.0 | PCIe |
| `nvidia-rtx-pro-4000-blackwell` | RTX PRO 4000 Blackwell (full-size) | 24 GB | omitted (140 W datasheet / 145 W page conflict) | 12.0 | PCIe |
| `nvidia-rtx-pro-2000-blackwell` | RTX PRO 2000 Blackwell | 16 GB | 70 W | 12.0 | PCIe |
| `nvidia-rtx-pro-5000-blackwell-48gb` | RTX PRO 5000 Blackwell 48 GB | 48 GB | 300 W | 12.0 | PCIe |
| `nvidia-rtx-pro-5000-blackwell-72gb` | RTX PRO 5000 Blackwell 72 GB | 72 GB | 300 W | 12.0 | PCIe |
| `nvidia-geforce-rtx-5070` | GeForce RTX 5070 | 12 GB | 250 W | 12.0 | PCIe |
| `nvidia-geforce-rtx-5060-ti-16gb` | GeForce RTX 5060 Ti 16 GB | 16 GB | 180 W | 12.0 | PCIe |
| `nvidia-geforce-rtx-5060-ti-8gb` | GeForce RTX 5060 Ti 8 GB | 8 GB | 180 W | 12.0 | PCIe |
| `nvidia-geforce-rtx-5060` | GeForce RTX 5060 | 8 GB | 145 W | 12.0 | PCIe |

Plus one **measured** card, `nvidia-rtx-pro-4000-blackwell-sff` (the RTX PRO 4000 Blackwell **SFF** variant, 24 GiB / 70 W / sm_120), grounded in a local `nvidia-smi` reading of the exact card used for the measurements below — a distinct item from the full-size `nvidia-rtx-pro-4000-blackwell` above.

Each item follows the 4090/L40S field convention (`accelerator_type`, `vendor`, `model_name`, `vram_gb`, `backends`, `precisions`, `rated_power_w`, `interconnect`), `billing_class: unknown`, and a `provenance[]` entry per primary source with an access date. `verification_status` is `unverified` for published-spec items (a published spec is not an independent measurement) and `verified` for the locally measured SFF card.

## Research-note cards (7, not in the catalog)

Per the 43e8011 convention, these three cards have one or more required field that could not be quoted from a primary source and are therefore recorded here, not frozen into the catalog:

| ID | Variant | Sourced | Un-sourced (why) |
| --- | --- | --- | --- |
| `nvidia-b100` | B100 (Blackwell SXM) | compute cap 10.0, NVLink, precisions | `vram_gb`, `rated_power_w` (nvidia.com `/data-center/b100/` 301-redirects; no quotable per-GPU figure) |
| `nvidia-b200` | B200 (Blackwell SXM) | compute cap 10.0, NVLink, precisions | `vram_gb`, `rated_power_w` (per-GPU figures not quotable; the 1.4 TB HGX total is a node figure, not a per-GPU quote — see companion note) |
| `nvidia-b300` | B300 (Blackwell Ultra SXM) | compute cap 10.3, NVLink, precisions | `vram_gb`, `rated_power_w` (the 288 GB / 2.1 TB figures are per-node on the source page, not per-GPU; no power quote) |

The RTX 5070, RTX 5060 Ti (16 GB and 8 GB), RTX 5060 and RTX PRO 5000 (48 GB and 72 GB) were listed here earlier as unquotable; they are now catalog items (VRAM, bus width and power re-read on nvidia.com, PRO 5000 from its datasheet), see `blackwell-accelerators.md`.

B200/B300 `vram_gb` is recorded as `not sourced`: the quotable HGX "Total Memory" figures (1.4 TB / 2.1 TB) are **per-node** board totals, not per-GPU quotes, and a 1-step ÷8 division (175 / 262.5 GB) does not match the per-GPU HBM figures, so per the never-guess rule the value is left `null` rather than presented as a derived per-GPU number. Both cards stay research-note-only regardless (no per-GPU board-watt figure is quotable).

## Precision convention (v1 enum)

All Blackwell items use the 6-value v1 precision set `[fp32, tf32, bf16, fp16, fp8, int8]`. Per the CUDA Programming Guide Table 33 (Tensor Core input types), the **tensor-core** subset is `tf32, bf16, fp16, fp8, int8`; `fp32` is a CUDA-core precision. **`int4` is omitted from every Blackwell card** (a deliberate correction from the initial 7-value 4090-convention draft): Table 33 marks the INT4 cell **blank** for CC 10.0 / 10.3 / 12.0, and `precision-reference.json`'s own `fp4_fp6_note` states "int4 must be omitted from every Blackwell card's precisions list." Blackwell's native **FP6** and **FP4** (incl. MXFP4/NVFP4 microscaling) are **absent from the v1 enum** and are recorded in the item notes, not mapped to `int4` (FP4 is E2M1 4-bit float, not signed int4). See `precision-reference.json` (in the measurement evidence) for the per-compute-capability table and the FP4/FP6 mapping note. A precision listing does not assert that an arbitrary quantized checkpoint runs.

## Generic sizing model

`research/T2-infrastructure/compute/sizing_generic.py` is a parameterized sizing function that extends `sizing_examples.py` (it imports `kv_bytes`/`capacity_range`; no copy-paste). It takes any model — total size, quantized or not, dense vs MoE-offloadable — and any accelerator count, and returns `{fits, resident_vram_gb, pool_vram_gb, peak_per_device_vram_gb, host_ram_gb, needs_devices, latency_cost_estimate, quant}`.

Key design points (round 5, gated):
- **Per-engine runtime-overhead parameter.** The module default stays 3 GiB; a named profile `LLAMACPP_RTX_PRO_4000_N1` carries the measured values (overhead 0.414149 GiB, transfer-buffer ratio 0, two-way layer split fraction 0.5825), calibrated on the M1 dense measurement (n=1).
- **Per-device peak output** via a `split_fraction` parameter (required when `n_devices > 1`), so a sizing rule uses **peak-per-device**, not `total/n_devices` (the M3 measurement shows a 58.3/41.7 split, not 50/50).
- **Host RAM reported as observed-only** (`host_ram_gb: None`, `host_ram_note: "observed RSS (mmap/page cache), not predicted"`), because the M2 MoE offload's host footprint is mmap/page-cache, not a resident copy.
- **MoE offload** (`offload_policy="experts_to_cpu"`) reduces `resident_vram_gb` by the offloaded expert bytes; `needs_devices` and the pool/peak outputs follow `GPU_live = resident_weights + GPU_KV + n·overhead + transfer_buffers`.
- Validation is `ValueError`-based (not `assert`) so it fails loudly under `python -O`; `main()` carries assert-based self-checks plus the predicted-vs-measured table.

## Validation against the three measurements

`python3 research/T2-infrastructure/compute/sizing_generic.py` (exit 0) reproduces:

| Scenario | Predicted | Measured | Δ% | Note |
| --- | --- | --- | --- | --- |
| M1 dense (calibration point) | 3.238003 GB | 3.238003 GB | +0.000% | agrees by construction |
| M2 MoE offload (held-out) | 3.009820 GB | 3.150 GB | −4.45% | n=1; SSM recurrent state + compute buffers unmodelled |
| M3 pool (held-out) | 3.682692 GB | 3.772776 GB | −2.39% | n=1 |
| M3 peak/device (held-out) | 2.145168 GB | 2.197815 GB | −2.40% | n=1 |

The held-out deltas (M2 −4.45%, M3 −2.39%/−2.40%) are at **n=1** each and are arithmetic checks, not a calibrated error range; the function is `calibrated` (validated against a real reading), not `verified`. SSM recurrent state and compute buffers are unmodelled for the hybrid SSM+MoE M2 card.

## The three measurements (ground truth)

Measured on **2× NVIDIA RTX PRO 4000 Blackwell SFF** (24467 MiB each, sm_120 / compute capability 12.0, 70 W board limit, driver 580.126.09), `llama.cpp llama-server`, `--flash-attn off` (sm_120 flash-attn segfault), f16 KV, fixed 129-token temp-0 prompt. VRAM is **per-PID** (`nvidia-smi --query-compute-apps=pid,used_memory,gpu_uuid`) with the two background services (a live model on GPU0 + a sub-agent model on GPU1) subtracted. Full raw per-PID readings and conditions are in `research/T2-infrastructure/measurements/rtx-pro-4000-blackwell-sff-measurements-2026-10-18.json`; the calibrated estimates are in `resource-estimate-rtx-pro-4000-blackwell-sff-2026-10-18.json` (confidence `calibrated`).

| ID | Model (real arch) | Knobs | Result |
| --- | --- | --- | --- |
| M1 dense fit | Qwen3 4B Instruct Awq, Q4_K_M (arch `qwen3`, dense, 2.491 dec GB) | `-ngl 999 --ctx-size 2048`, GPU 0 | required VRAM **3.238 dec GB**, 28.4 tok/s, TTFT 0.131 s |
| M3 multi-GPU | same model | `--dev 0,1 --split-mode layer`, ctx 2048 | pool 3.773 dec GB, **peak/device 2.198 dec GB**, split 58.3/41.7, 23.5 tok/s |
| M2 MoE offload | Qwen-Agentworld-35B-A3B, Q4_K_M (arch `qwen35moe`, **hybrid SSM+MoE**: 256 experts top-8, full_attention_interval 4, 22.314 dec GB) | `-ngl 999 --cpu-moe --ctx-size 1024`, GPU 0 | resident VRAM **3.150 dec GB** + ~8.4 dec GB host RAM (mmap, observed), 7.3 tok/s, TTFT 1.737 s |

The M2 result is the headline MoE-offload finding: a **22.314 dec GB** model is resident in **3.150 dec GB** of VRAM because the routed+shared experts (19.770 dec GB) are offloaded to host RAM. The card is a hybrid SSM+MoE, so its per-token KV grows ~4× slower than a dense model at equal depth (only 1 of 4 blocks is full attention).

## Remaining unknowns / handoffs

- All measurements are **n=1** per scenario; no calibrated error range is claimed.
- `billing_class` is `unknown` for every new item (no pricing asserted).
- No training estimates (owned by #31); no SLO claim (capacity screen only).
- **Handoff to #11 (inference engine):** the `--flash-attn off` condition for sm_120 should be reviewed before any engine-compatibility claim. **Handoff to #40:** the memory-bandwidth field is note-only here (not a spec field), per the decision record.
- The 7 research-note cards become catalog items only when their un-sourced fields are quoted from a primary source (B100/B200/B300 need a per-GPU board-watt figure; the consumer/pro cards need a quotable `vram_gb`).

## Validation

- `python scripts/validate_research.py` — 85 catalog proposals (78 baseline at `83b565d` + 7 new: 6 fully-sourced + measured SFF), 3 pricebooks, exit 0.
- `python -m unittest discover -s contracts/v1/tests` and `-s tests` — OK.
- `python scripts/validate_market_research.py` — market integrity OK.
- `python prompts/mobile/validate_prompts.py` — OK.
- `sizing_generic.py` self-check + break-test (mutant rejected) — exit 0 / non-zero respectively.
- Break-test on a catalog item (required field removed → validator rejects) — confirmed.
