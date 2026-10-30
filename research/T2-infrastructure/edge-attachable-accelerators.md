# Edge and attachable accelerators (USB and M.2)

Issue: Refs #10 · Contract: 1.0.0 · Kinds: `accelerator`
Status: draft research note · Last researched: 2026-10-30

This note covers a gap that [gpu-compute.md](gpu-compute.md) records: CPU and edge inference are in scope, but the
structured subset has no edge catalog items. Before complete edge proposals, #10 and #40 must decide how v1 represents
shared memory and accelerator partitions. This note adds evidence for attachable accelerators with **dedicated
on-module memory**, which do not raise the shared-memory question. It proposes no catalog item and no rule change.

## User decision

I have a laptop, mini PC, single-board computer or phone and no discrete GPU. Can I add an accelerator over USB-C or M.2
to run small models locally, and what will it hold?

Deployment modes: self-hosted (local device). Hybrid builds may also use one for local embedding or speech alongside a
hosted model.

## Candidate options

| Candidate | Chip | Form factor and link | Status |
| --- | --- | --- | --- |
| ASUS UGen300 USB (`UGen300-USB-8G`) | Hailo-10H | USB stick, USB 3.1 Gen2 Type-C | Announced 2026-04-01 (A2) |
| Hailo-10H M.2 AI acceleration module | Hailo-10H | M.2 Key M 2242 / 2280, PCIe Gen3 x4 | Commercially available since 2025-07-22 (A3) |
| Google Coral (first-generation Edge TPU, USB) | Edge TPU | USB | Google now lists the first-generation Edge TPU separately from Coral NPU, its open-source RISC-V NPU design (A5). Current availability not established |

## Comparison fields

| Field / JSON pointer | Type and unit | Candidate finding | Evidence ID | Conditions / unknowns |
| --- | --- | --- | --- | --- |
| peak compute | TOPS by precision | UGen300: 40 TOPS INT4, 20 TOPS INT8. Hailo-10H M.2: 40/20 TOPS (INT4/INT8) | A1, A4 | Vendor claim. Peak TOPS do not predict LLM throughput (A4 links the vendor's own caveat) |
| dedicated on-device memory | GB and type | UGen300: 8 GB LPDDR4 at 4266 MT/s. M.2: 4 or 8 GB LPDDR4/4X | A1, A4 | Primary documentation. This is **dedicated** module memory, not host RAM or unified memory, so it must not be relabelled VRAM or added to host memory (see gpu-compute.md) |
| host interface | enum + rate | UGen300: USB 3.1 Gen2 Type-C, 10 Gbps. M.2: PCIe Gen3 x4 | A1, A4 | Primary documentation. Link rate limits model load time and any host-side data exchange, not on-module compute |
| typical power | W | 2.5 W typical (both) | A1, A2, A4 | Vendor claim; the measurement conditions aren't published |
| host OS and architecture | list | UGen300: Windows, Linux, Android; x86 and ARM | A1 | Primary documentation; driver and runtime versions not pinned |
| supported frameworks | list | M.2: TensorFlow, TensorFlow Lite, Keras, PyTorch, ONNX | A4 | Models need the vendor's compilation flow and model zoo; arbitrary checkpoints are not supported as-is |
| generative throughput | tokens/s, s to first token | "first-token latency of under 1 second and over 10 Tokens per Second on a variety of 2B language and vision-language models" | A3 | Vendor claim. The models, quantization, context length and prompt are not pinned, so it is **not comparable** under the #41 benchmark rule. It needs an independent measurement |
| operating temperature | °C | M.2: −40 °C to 85 °C (industrial grade) | A4 | Primary documentation |

## Evidence

| ID | Publisher and URL | Access date | Version / region | Evidence grade | Limitations / reuse terms |
| --- | --- | --- | --- | --- | --- |
| A1 | ASUS, UGen300 USB tech specs: <https://www.asus.com/motherboards-components/ai-accelerator/ugen/ugen300-usb-8g/techspec/> | 2026-10-30 | Model `UGen300-USB-8G` | Primary documentation (specs); vendor claim (TOPS, power) | Facts only; no page text reused |
| A2 | ASUS press release, UGen300: <https://press.asus.com/news/press-releases/asus-ugen300-usb-ai-accelerator-generative-ai-edge/> | 2026-10-30 | — | Vendor claim | Marketing source; it states an M.2 version also exists |
| A3 | Hailo, Hailo-10H general availability: <https://hailo.ai/company-overview/newsroom/news/hailo-announces-general-availability-of-hailo-10h-edge-ai-accelerator-with-generative-ai-capabilities/> | 2026-10-30 | Release dated 2025-07-22 | Vendor claim | Throughput claim not reproducible as published |
| A4 | Hailo, Hailo-10H M.2 module: <https://hailo.ai/products/ai-accelerators/hailo-10h-m-2-ai-acceleration-module/> | 2026-10-30 | — | Primary documentation (form factor, interface, memory, temperature); vendor claim (TOPS, power) | — |
| A5 | Google for Developers, Coral: <https://developers.google.com/coral> | 2026-10-30 | Page last updated 2026-10-19 | Primary documentation | Confirms that Coral NPU is an open-source RISC-V NPU design and that the first-generation Edge TPU is listed separately. First-generation USB stick specs were not checked here |

## Compatibility proposals

No rule is submitted. These are candidate rule ideas for #10 and #40 to accept or reject:

1. **Model fits dedicated memory** (`accelerator` ↔ `model`): if the model artifact (weights at the chosen precision)
   plus its runtime and KV allowance exceeds the accelerator's dedicated on-device memory, the outcome is `fail` with
   severity `error` for on-accelerator execution. If either value is missing, the outcome is `unknown`.
2. **Model is in the vendor's supported set** (`accelerator` ↔ `model`, `inference_engine`): these accelerators run
   models compiled through the vendor's toolchain. A model with no published compiled artifact or supported
   architecture is `unknown`, not `pass`.
3. **Link is not memory**: the host link rate (USB or PCIe) must never be treated as a way to extend accelerator memory
   by streaming weights. A dense model reads all its weights per generated token. At 10 Gbps (about 1.25 GB/s raw), a
   4.5 GB artifact would take several seconds per token (estimate by arithmetic). Any build that relies on this should
   be `fail` for interactive generation workloads.

## Pricing and capacity

Unpriced. Retail prices were seen on resellers but not on a publisher's price page, so no pricebook is proposed. A
capacity estimate is out of scope until an independent measurement exists (see the open questions).

## Recommendation and rationale

Represent these devices as `accelerator` items with **dedicated** memory and a host-link field, distinct from GPUs and
from shared or unified memory devices. They are a practical option for small (about 2B-class) language and
vision-language models, embedding, speech and vision on machines without a GPU, at about 2.5 W (vendor claim). They do
not let a host run models larger than their on-module memory.

## Structured artifacts

None. Required facts that are missing for a complete `CatalogItem`: independently measured generative throughput, a
pinned runtime and driver version, and a publisher price.

## Open questions and handoffs

| Question | Owner |
| --- | --- |
| Does v1 need a `memory_kind` (dedicated / shared / unified) and a `host_link` field on `accelerator`, or does the #40 contract already cover them? | #40 (@tynamite) with #10 (@Mattycodes69) |
| Independent measurement protocol for small-model throughput on attachable accelerators, pinned under the #41 comparability rule | #10 co-owners; T6 evaluation (#115) |
| Should the builder offer "add an accelerator" as an upgrade step for CPU-only builds from deployment-mode.md? | T0 (@tynamite) |
| First-generation Coral Edge TPU: current availability and specs from a primary source | Open; any contributor |
