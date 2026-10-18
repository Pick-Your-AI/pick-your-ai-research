# Blackwell accelerator proposals

Status: source-checked research, 2026-10-18. These thirteen proposals extend the
[GPU/compute decision record](gpu-compute.md). They preserve the contributor's
separate hardware variants while correcting source attribution and precision
descriptions. Every new catalog provenance entry is `unverified`: a direct
vendor-source read does not establish independent hardware verification.

Original contribution:
[MrTrenchTrucker, 63aac759](https://github.com/MrTrenchTrucker/pick-your-ai-research/commit/63aac7598a441f364b7701fa5d86e9c8cb47a65a).
The [intake disposition](measurements/blackwell-intake-review-2026-10-18.json)
pins every original catalog blob and both reported runtime records. Original
content remains in Git; corrected proposals do not backdate the new source reads.

## Hardware identities and source mapping

Memory is the vendor's advertised GB value. Power is a reference rating, not
measured operating consumption. The workstation editions and memory variants
remain separate IDs; neither multiple cards nor a product family imply one
addressable memory pool.

| Catalog ID | Advertised memory, GB | Rated power, W | Primary specification source |
| --- | ---: | ---: | --- |
| `nvidia-geforce-rtx-5060` | 8 | 145 | G |
| `nvidia-geforce-rtx-5060-ti-8gb` | 8 | 180 | G |
| `nvidia-geforce-rtx-5060-ti-16gb` | 16 | 180 | G |
| `nvidia-geforce-rtx-5070` | 12 | 250 | G |
| `nvidia-geforce-rtx-5070-ti` | 16 | 300 | G |
| `nvidia-geforce-rtx-5080` | 16 | 360 | G |
| `nvidia-geforce-rtx-5090` | 32 | 575 | G |
| `nvidia-rtx-pro-2000-blackwell` | 16 | 70 | P2 |
| `nvidia-rtx-pro-4000-blackwell` | 24 | 145 | P4 |
| `nvidia-rtx-pro-4000-blackwell-sff` | 24 | 70 | PS |
| `nvidia-rtx-pro-5000-blackwell-48gb` | 48 | 300 | P5 |
| `nvidia-rtx-pro-5000-blackwell-72gb` | 72 | 300 | P5 |
| `nvidia-rtx-pro-6000-blackwell-workstation` | 96 | 600 | P6 |

All sources below were directly read on 2026-10-18. Catalog `checked_at` records
the current review; URLs are mutable and no immutable vendor-document hash is
claimed.

| Source | Publisher and exact scope |
| --- | --- |
| [G: GeForce comparison](https://www.nvidia.com/en-us/geforce/graphics-cards/compare/) | NVIDIA, the seven corresponding 50-series columns, including the two 5060 Ti memory variants. Reference-design memory/power and PCIe; manufacturer cards may differ. |
| [P2: RTX PRO 2000 datasheet](https://www.nvidia.com/content/dam/en-zz/Solutions/products/workstations/professional-desktop-gpus/rtx-pro-2000/workstation-datasheet-blackwell-rtx-pro-2000-nvidia-us-4016661.pdf) | NVIDIA, specifications p3: this card's capacity, power, PCIe and native single-precision arithmetic. |
| [P4: RTX PRO 4000 datasheet](https://www.nvidia.com/content/dam/en-zz/Solutions/products/workstations/professional-desktop-gpus/rtx-pro-4000/workstation-datasheet-rtx-pro-4000-nvidia-us-web.pdf) | NVIDIA, June 2026, specifications p3: full-height card, PCIe 5 x16, single slot. |
| [PS: RTX PRO 4000 SFF datasheet](https://www.nvidia.com/content/dam/en-zz/Solutions/products/workstations/professional-desktop-gpus/rtx-pro-4000-sff/workstation-datasheet-blackwell-rtx-pro-4000-sff-nvidia-us-4016700.pdf) | NVIDIA, June 2026, specifications p3: half-height card, PCIe 5 x8 and dual slot. |
| [P5: RTX PRO 5000 datasheet](https://www.nvidia.com/content/dam/en-zz/Solutions/products/workstations/professional-desktop-gpus/rtx-pro-5000-blackwell/workstation-datasheet-blackwell-rtx-pro-5000-5488550-nvidia.pdf) | NVIDIA, July 2026, specifications p3: separate 48/72 GB columns; shared power and PCIe 5 x16 specification. |
| [P6: RTX PRO 6000 family](https://www.nvidia.com/en-us/products/workstations/professional-desktop-gpus/rtx-pro-6000-family/) | NVIDIA, Workstation Edition column only. Server and Max-Q power specifications do not apply to this proposal. |
| [C: CUDA GPU identities](https://developer.nvidia.com/cuda/gpus) | NVIDIA, the named cards/families map to compute capability 12.0. |
| [T: CUDA compute-capability tables](https://docs.nvidia.com/cuda/cuda-programming-guide/05-appendices/compute-capabilities.html) | NVIDIA, Tables 30/33, page updated 2026-09-10; arithmetic scope assessed below. |

## Complete frozen-v1 precision disposition

For these CC 12.0 cards, the seven-value v1 enum has six documented native
arithmetic values: `fp32`, `tf32`, `bf16`, `fp16`, `fp8` and `int8`.
T Table 33 lists the latter five as Tensor Core inputs and leaves INT4 blank.
FP32 is supported outside that Tensor-input table, as reflected in T Table 30
and the product arithmetic specifications. The omitted `int4` therefore has a
scoped native-arithmetic disposition; it is not merely an unchecked omission.

FP4 and FP6 are floating formats outside the frozen enum, and FP6 has its own
Table 33 column. FP4 is not integer INT4. The original reference also incorrectly
described CC 10.0's FP64 Tensor cell as blank; T marks it supported. The corrected
[precision note](measurements/precision-reference-blackwell-2026-10-18.json)
preserves those distinctions.

This coverage follows the existing [native-arithmetic boundary](gpu-compute.md#incomplete-precision-intake-correction-2026-10-18).
A stored Q4/GGUF/AWQ/GPTQ checkpoint is not itself a native instruction dtype.
Neither this list nor the unchanged frozen membership rule establishes the
converter, mixed dtype, engine, kernel, driver or selected runtime's support.
A hardware fact cannot substitute for the joint tuple's evidence.

## Corrections and retained limitations

The original full-size 4000 proposal withheld power because it contained an
unverified older 140 W quotation and a 145 W product-page statement. The current
P4 datasheet and current product page agree on 145 W; this dated proposal uses
that current reference rating. The older quoted PDF was not successfully
retrieved in this review, so its purported 140 W row is not independently
confirmed or silently relabeled as a successful source read. The exact original
quotation and URL remain in the contributor commit.

The SFF proposal now describes a vendor reference identity with unverified
provenance. The prior single-slot description is corrected to the PS dual-slot
specification. Its separately reported local driver/device observations do not
become a vendor-source measurement or independent verification. The reported
24,467 MiB counter and advertised 24 GB are retained in their separate roles;
neither is evidence of free allocatable capacity.

No B100/B200/B300 catalog proposal is added. Current stock, regional access,
actual board/partition allocation, pricing, runtime support, training fit,
throughput and deployment approval are unqualified here. Existing catalog
records and the frozen v1 schema/evaluator are unchanged. Production promotion,
source/use permissions for a chosen payload and affected-client admission keep
their existing review requirements.

The [sizing and reported-observation assessment](gpu-compute-catalog-extension.md)
records the original arithmetic defects and why the submitted observations do
not establish calibration or any additional #61 whole-runtime peak pair.
