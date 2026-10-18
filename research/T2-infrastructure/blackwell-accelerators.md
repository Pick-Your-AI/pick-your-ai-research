# Blackwell (GeForce RTX 50-series / RTX PRO Blackwell / B-series) accelerator research note

This is a **research note**, not a catalog proposal. It records the subset of
Blackwell facts that are quotably sourced, discloses missing/unspecified fields,
and opens questions it could not resolve. Every number carries its source URI and
an access date; every non-sourced claim is labeled `not sourced`. Nothing here
certifies runtime compatibility or independent verification. Source-checked,
runtime-unverified — same evidence grade as the A100/4090 supplement in
[gpu-compute.md](./gpu-compute.md). Author did not re-fetch quotes; they were
supplied by a spec-sourcing sub-agent and remain `unverified`.

## Scope and method

Scope: single-accelerator Blackwell facts (VRAM, rated power, compute capability,
interconnect, precisions) plus open conflicts. Method: read-only inspection of the
12 per-card spec files supplied by the research coordinator (not committed here) and
of NVIDIA's primary pages/datasheets cited there. Access date 2026-10-18. Per repo
policy, missing or ambiguous per-card values are recorded as `not sourced`, never
guessed; the spec files are third-party output (sub-agent supplied), so all facts
are `unverified` until a human reviews them.

## Catalog items

These twelve cards meet the catalog proposal bar (VRAM, power, compute capability and
interconnect sourced, or power omitted by decision where sources conflict) and are candidates for promotion:

| Item id | VRAM (GB) | Rated power (W) | Compute cap | Interconnect | Precisions | Sources | Notes / gap |
| --- | --- | --- | --- | --- | --- | --- | --- |
| nvidia-geforce-rtx-5090 | 32 | 575 | 12.0 | pcie | fp32, tf32, bf16, fp16, fp8, int8 | VRAM [compare](https://www.nvidia.com/en-us/geforce/graphics-cards/compare/) "Standard Memory Config | 32 GB GDDR7"; power [compare](https://www.nvidia.com/en-us/geforce/graphics-cards/compare/) "Total Graphics Power (W) | 575" | VRAM, power, cap and interconnect sourced. |
| nvidia-geforce-rtx-5080 | 16 | 360 | 12.0 | pcie | fp32, tf32, bf16, fp16, fp8, int8 | VRAM [compare](https://www.nvidia.com/en-us/geforce/graphics-cards/compare/); power [compare](https://www.nvidia.com/en-us/geforce/graphics-cards/compare/) "Total Graphics Power (W) 360" | VRAM, power, cap and interconnect sourced. |
| nvidia-geforce-rtx-5070-ti | 16 | 300 | 12.0 | pcie | fp32, tf32, bf16, fp16, fp8, int8 | VRAM [compare](https://www.nvidia.com/en-us/geforce/graphics-cards/compare/) "16 GB GDDR7"; power [compare](https://www.nvidia.com/en-us/geforce/graphics-cards/compare/) "300" | VRAM, power, cap and interconnect sourced. |
| nvidia-rtx-pro-2000-blackwell | 16 | 70 | 12.0 | pcie | fp32, tf32, bf16, fp16, fp8, int8 | datasheet [4016661](https://www.nvidia.com/content/dam/en-zz/Solutions/products/workstations/professional-desktop-gpus/rtx-pro-2000/workstation-datasheet-blackwell-rtx-pro-2000-nvidia-us-4016661.pdf) "70 W"; product [page](https://www.nvidia.com/en-eu/products/workstations/professional-desktop-gpus/rtx-pro-2000) | VRAM, power, cap and interconnect sourced. |
| nvidia-rtx-pro-6000-blackwell-workstation | 96 | 600 | 12.0 | pcie | fp32, tf32, bf16, fp16, fp8, int8 | product [page](https://www.nvidia.com/en-us/products/workstations/professional-desktop-gpus/rtx-pro-6000-family) "96 GB ... Max Power Consumption 600 W (Workstation Edition)" | Workstation Edition; Max-Q up to 300 W, Server up to 600 W configurable — editions differ. |
| nvidia-rtx-pro-4000-blackwell (full-size) | 24 | omitted (conflict) | 12.0 | pcie | fp32, tf32, bf16, fp16, fp8, int8 | VRAM [datasheet 3662515](https://www.nvidia.com/content/dam/en-zz/Solutions/design-visualization/quadro-product-literature/workstation-datasheet-blackwell-rtx-pro-4000-nvidia-us-3662515.pdf) "Total board power: 140 W"; product [page](https://www.nvidia.com/en-us/products/workstations/professional-desktop-gpus/rtx-pro-4000/) "Max Power Consumption 145 W" | **Power conflict**: datasheet 140 W vs product page 145 W (D3). rated_power_w omitted per policy. Distinct from the SFF edition Router measures separately. |
| nvidia-rtx-pro-5000-blackwell-48gb | 48 | 300 | 12.0 | pcie | fp32, tf32, bf16, fp16, fp8, int8 | [page](https://www.nvidia.com/en-us/products/workstations/professional-desktop-gpus/rtx-pro-5000/) and [datasheet](https://www.nvidia.com/content/dam/en-zz/Solutions/products/workstations/professional-desktop-gpus/rtx-pro-5000-blackwell/workstation-datasheet-blackwell-rtx-pro-5000-5488550-nvidia.pdf) "Memory Interface 384-bit", "Total board power: 300 W" | Two SKUs, two items; page and datasheet agree on 300 W; 384-bit bus recorded in provenance notes (no schema field). |
| nvidia-rtx-pro-5000-blackwell-72gb | 72 | 300 | 12.0 | pcie | fp32, tf32, bf16, fp16, fp8, int8 | same page and datasheet | Second SKU of the RTX PRO 5000. |
| nvidia-geforce-rtx-5070 | 12 | 250 | 12.0 | pcie | fp32, tf32, bf16, fp16, fp8, int8 | [5070 family](https://www.nvidia.com/en-us/geforce/graphics-cards/50-series/rtx-5070-family/) "Total Graphics Power (W) | 300 | 250" | 192-bit bus; reference-design power, AIB cards vary. |
| nvidia-geforce-rtx-5060-ti-16gb | 16 | 180 | 12.0 | pcie | fp32, tf32, bf16, fp16, fp8, int8 | [5060 family](https://www.nvidia.com/en-us/geforce/graphics-cards/50-series/rtx-5060-family/) "Standard Memory Config | 16 GB / 8 GB GDDR7" | NVIDIA lists ONE 180 W figure for both 5060 Ti SKUs. |
| nvidia-geforce-rtx-5060-ti-8gb | 8 | 180 | 12.0 | pcie | fp32, tf32, bf16, fp16, fp8, int8 | same page | Same single 180 W figure. |
| nvidia-geforce-rtx-5060 | 8 | 145 | 12.0 | pcie | fp32, tf32, bf16, fp16, fp8, int8 | [5060 family](https://www.nvidia.com/en-us/geforce/graphics-cards/50-series/rtx-5060-family/) "Total Graphics Power (W) | 180 | 145" | 128-bit bus. |

### Precision and the FP4/FP6 gap (applies to all Blackwell cards above)

Every Blackwell card's list follows precision-reference.json CC-12.x: TF32, BF16,
FP16, FP8, INT8 plus FP32 carried in by CUDA cores; **int4 is correctly omitted**.
The omission is a claim-bearing decision, not silence. From the precision reference
`fp4_fp6_note`: NVIDIA's Blackwell brief and Tensor Cores page list FP6 and FP4 as
native Tensor Core formats ("Total FP8/FP6", "supported ... FP6, FP4"), but they do
NOT map to any v1 enum value — FP6 is not representable in the enum, and FP4 (E2M1 /
NVFP4 float) does not equal signed int4. The CUDA Table 33 lists INT4 as unsupported
(empty) while listing FP6/FP4 present; so `int4` must be dropped from every Blackwell
card, and a standalone 'FP6' column is never enumerated (it co-appears with FP8).

## Research-note-only cards

These three do not meet the catalog bar because required fields are missing or ambiguous:

| Item id | compute_cap | interconnect | vram_gb | rated_power_w | Why not in catalog |
| --- | --- | --- | --- | --- | --- |
| nvidia-b100 | null (`not sourced`) | null (`not sourced`) | null (`not sourced`) | null (`not sourced`) | The B100 spec file carries B200 data (its notes say 'B200 compute capability = 10.0'; its sources are the B200 pages), so nothing in it is quotable for a B100. Everything is `not sourced` until a B100 primary source is read. Do not read the B200 row as B100. |
| nvidia-b200 | 10.0 (`sourced`) | nvlink (`sourced`) | null (`not sourced`) | null (`not sourced`) | compute_cap and interconnect quotable (CUDA table "B200 -> 10.0"; datasheet "NVLink ... 1.8 TB/s"); vram_gb/rated_power_w absent as per-GPU quote on the page. |
| nvidia-b300 | 10.3 (`sourced`) | nvlink (`sourced`) | null (`not sourced`) | null (`not sourced`) | compute_cap + interconnect quotable (CUDA table row '10.3 | NVIDIA GB300 | NVIDIA B300 (DGX Station)'; HGX B300 reference architecture, NVLink, 'Up to 8 TB/s'). The 288 GB figure appears only per node on the source page, so it is not counted as per-GPU VRAM; no power quote. |

## Conflicts and open questions

- **RTX PRO 4000 Blackwell full-size power** — datasheet says "Total board power:
  140 W" while the product page says "Max Power Consumption 145 W". Per D3,
  rated_power_w is omitted (optional in schema) and both values are recorded; no
  single value was chosen.
- **RTX PRO 6000 Blackwell editions** — Workstation Edition 600 W is quotable; the
  Max-Q Workstation Edition clamps to 300 W and the Server edition reaches 600 W
  configurable (D4). Editions differ in power; the note records only what is quotable.
- **int4 dropped** — three spec files list int4 against the precision reference, which
  marks INT4 blank for CC 12.x. Resolved per D1: int4 omitted from every Blackwell
  card's precisions; FP4/FP6 remain as absent-slot float formats (see Catalog gap).
- **VRAM-variant gaps closed** - the RTX 5070 (12 GB), RTX 5060 Ti (16 GB and 8 GB), RTX 5060 (8 GB) and RTX PRO 5000 (48 GB and 72 GB, two items) are now catalog items. VRAM, bus width and power were re-read on nvidia.com by Router; the PRO 5000 bus width (384-bit) comes from its datasheet. NVIDIA lists one 180 W figure for both 5060 Ti SKUs.

## Router measured card

The repo's own measurement is cited once and once only: **'NVIDIA RTX PRO 4000
Blackwell SFF Edition'**, 70 W, compute_cap sm_120. This is a distinct product from
the full-size RTX PRO 4000 (D5); Router's `research/T2-infrastructure/measurements/*2026-10-18.json`
live on branch `fix/issue-10-blackwell-measurements`, not on this repo.

## Sizing

Point to `compute/sizing_generic.py`: llama.cpp profile overhead 0.4447 GB calibrated
on M1; held-out M2 -4.45%, M3 pool -2.39%, M3 peak/device -2.40%; n=1 each; SSM state
and compute buffers unmodelled; host RAM observed-only. These figures come from the
module output (run `python research/T2-infrastructure/compute/sizing_generic.py`),
not from measurement of this Blackwell hardware, and assert no runtime result.
