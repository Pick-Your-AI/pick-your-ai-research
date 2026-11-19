# Edge and attachable accelerators (USB and M.2)

Issue: Refs #10 · Contract: 1.0.0 · Kinds: `accelerator`
Status: draft research note · Last researched: 2026-10-30

This note covers a gap that [gpu-compute.md](gpu-compute.md) records: CPU and edge inference are in scope, but the
structured subset has no edge catalog items. Before complete edge proposals, #10 and #40 must decide how v1 represents
shared memory and accelerator partitions. This note adds evidence for attachable accelerators with **dedicated
on-module memory**, which do not raise the shared-memory question. It proposes no catalog item, no new rule and no
contract change. Its rule-relevant findings are inputs to the existing COMPUTE-01 and COMPUTE-02 families
([compute-capacity rules](rules/compute-capacity.md)).

#10 closed as completed on 2026-10-18. Following the T2 README's guidance for bounded subsequent work, this note uses
`Refs #10`. Whether it should instead sit under a new edge/CPU follow-up issue is a question for the #10 co-owners
(see the open questions).

## User decision

I have a laptop, mini PC, single-board computer or phone and no discrete GPU. Can I add an accelerator over USB-C or M.2
to run small models locally, and what will it hold? For phones, Android access is currently limited (see the OS row).

Deployment modes: self-hosted (local device). Hybrid builds may also use one for local embedding or speech alongside a
hosted model.

## Candidate options

| Candidate | Chip | Form factor and link | Status |
| --- | --- | --- | --- |
| ASUS UGen300 USB (`UGen300-USB-8G`) | Hailo-10H | USB stick, USB 3.1 Gen2 Type-C | Announced 2026-04-01 (A2). The announcement says Windows driver support was expected in mid-May 2026 and Android support is currently for B2B customers (A2, footnotes [i] and [ii]) |
| Hailo-10H M.2 AI acceleration module | Hailo-10H | M.2 Key M 2242 / 2280, PCIe Gen3 x4 | Listed on the publisher's product page (A4, accessed 2026-10-30). The 2025-07-22 commercial-availability date applies to the Hailo-10H processor family (orders and software, A3); no module-specific availability date was found |
| Google Coral (first-generation Edge TPU, USB) | Edge TPU | USB | Google now lists the first-generation Edge TPU separately from Coral NPU, its open-source RISC-V NPU design (A5). Current availability not established |

## Comparison fields

| Field / JSON pointer | Type and unit | Candidate finding | Evidence ID | Conditions / unknowns |
| --- | --- | --- | --- | --- |
| peak compute | TOPS by precision | UGen300: 40 TOPS INT4, 20 TOPS INT8. Hailo-10H M.2: 40/20 TOPS (INT4/INT8) | A1, A4 | Vendor claim. Peak TOPS do not predict LLM throughput (A4 links the vendor's own caveat) |
| dedicated on-device memory | GB and type | UGen300: 8 GB LPDDR4 at 4266 MT/s. M.2: 4 or 8 GB LPDDR4/4X | A1, A4 | Primary documentation. This is **dedicated** module memory, not host RAM or unified memory, so it must not be relabelled VRAM or added to host memory (see gpu-compute.md) |
| host interface | enum + rate | UGen300: USB 3.1 Gen2 Type-C, 10 Gbps. M.2: PCIe Gen3 x4 | A1, A4 | Primary documentation. Link rate limits model load time and any host-side data exchange, not on-module compute |
| typical power | W | 2.5 W typical (both) | A1, A2, A4 | Vendor claim; the measurement conditions aren't published |
| host OS and architecture | list | UGen300 spec sheet: Windows, Linux, Android; x86 and ARM (A1). The announcement qualifies this: Windows driver support "expected to be available mid-May 2026" (footnote [i]); Android "currently available for B2B customers, with broader availability planned" (footnote [ii]) | A1, A2 | Spec-sheet compatibility, not verified, version-pinned consumer availability. Treat Windows availability as unknown until a pinned driver release is cited, and Android as not generally available to consumers |
| supported frameworks | list | M.2: TensorFlow, TensorFlow Lite, Keras, PyTorch, ONNX | A4 | Models need the vendor's compilation flow and model zoo; arbitrary checkpoints are not supported as-is |
| generative throughput | tokens/s, s to first token | "first-token latency of under 1 second and over 10 Tokens per Second on a variety of 2B language and vision-language models" | A3 | Vendor claim. The models, quantization, context length and prompt are not pinned, so it is **not comparable** under the #41 benchmark rule. It needs an independent measurement |
| operating temperature | °C | M.2: −40 °C to 85 °C (industrial grade) | A4 | Primary documentation |

## Evidence

| ID | Publisher and URL | Access date | Version / region | Evidence grade | Limitations / reuse terms |
| --- | --- | --- | --- | --- | --- |
| A1 | ASUS, UGen300 USB tech specs: <https://www.asus.com/motherboards-components/ai-accelerator/ugen/ugen300-usb-8g/techspec/> | 2026-10-30 | Model `UGen300-USB-8G` | Primary documentation (specs); vendor claim (TOPS, power) | Facts only; no page text reused |
| A2 | ASUS press release, UGen300: <https://press.asus.com/news/press-releases/asus-ugen300-usb-ai-accelerator-generative-ai-edge/> | 2026-10-30 | — | Primary documentation (OS footnotes); vendor claim (performance) | Marketing source; it states an M.2 version also exists. Footnotes [i] (Windows driver expected mid-May 2026) and [ii] (Android currently B2B) qualify A1's OS list |
| A3 | Hailo, Hailo-10H general availability: <https://hailo.ai/company-overview/newsroom/news/hailo-announces-general-availability-of-hailo-10h-edge-ai-accelerator-with-generative-ai-capabilities/> | 2026-10-30 | Release dated 2025-07-22 | Primary documentation (family availability date); vendor claim (throughput) | The date covers ordering the Hailo-10H processor and downloading its software; it does not establish when the M.2 module SKU became available. Throughput claim not reproducible as published |
| A4 | Hailo, Hailo-10H M.2 module: <https://hailo.ai/products/ai-accelerators/hailo-10h-m-2-ai-acceleration-module/> | 2026-10-30 | — | Primary documentation (form factor, interface, memory, temperature); vendor claim (TOPS, power) | — |
| A5 | Google for Developers, Coral: <https://developers.google.com/coral> | 2026-10-30 | Page last updated 2026-10-19 | Primary documentation | Confirms that Coral NPU is an open-source RISC-V NPU design and that the first-generation Edge TPU is listed separately. First-generation USB stick specs were not checked here |

## Compatibility proposals

No new rule is proposed. The findings below are inputs to the existing rule families in
[rules/compute-capacity.md](rules/compute-capacity.md), and keep their decision semantics unchanged.

1. **Input to COMPUTE-01 (per-device memory feasibility; the shared memory-fit family).** The module's dedicated
   on-module memory (4 or 8 GB LPDDR4/4X, A1/A4) is a separate **memory pool** for per-pool co-residency under the
   proposed CD-2. It is not host RAM, unified memory or a share of either. COMPUTE-01 then decides as it already does:
   - a proven resident-weight lower bound above the pool gives `fail`;
   - an estimate meeting the build's `min_resource_confidence` decides on its **upper bound**, so a range straddling
     the pool gives `fail`, flagged *may not fit*, with the range shown;
   - missing or unmet confidence eligibility gives `unknown` for review.

   Whether v1's existing accelerator memory field can carry this dedicated pool, or whether a memory-kind
   distinction is needed, is left to #40 (see the open questions).
2. **Vendor-toolchain case of COMPUTE-02 (model, engine and accelerator backend intersection).** These accelerators
   run models compiled through the vendor's toolchain; A4 lists the supported source frameworks and a model zoo. A
   joint path therefore needs the compiled artifact for the exact model, toolchain/runtime version and device. Under
   COMPUTE-02's existing rules, absence from an unmarked subset such as a model zoo gives `unknown`, explicit
   unsupported documentation gives `fail`, and a checked, versioned joint path can `pass`, labelled unverified until
   reproduced.
3. **Context for COMPUTE-01 remediation: the host link is not part of the pool.** COMPUTE-01 already forbids assuming
   memory pools. Streaming weights over the host link is not a validated offload plan: a dense model reads all its
   weights per generated token, and at 10 Gbps (about 1.25 GB/s raw) a 4.5 GB artifact would take several seconds per
   token (estimate by arithmetic). This is an explanation for remediation text, not a separate rule.

## Pricing and capacity

Unpriced. Retail prices were seen on resellers but not on a publisher's price page, so no pricebook is proposed. A
capacity estimate is out of scope until an independent measurement exists (see the open questions).

## Recommendation and rationale

Represent these devices as `accelerator` items with **dedicated** memory and a host-link field, distinct from GPUs and
from shared or unified memory devices. On hosts with a supported driver, they are a practical option for small (about
2B-class) language and vision-language models, embedding, speech and vision on machines without a GPU, at about 2.5 W
(vendor claim). They do not let a host run models larger than their on-module memory. For the USB stick, confirm a
pinned driver for the target OS before recommending it: Windows support was announced as expected, and Android is
currently B2B only (A2).

## Structured artifacts

None. Required facts that are missing for a complete `CatalogItem`: independently measured generative throughput, a
pinned runtime and driver version, and a publisher price.

## Open questions and handoffs

| Question | Owner |
| --- | --- |
| Placement: keep this note under the closed #10 (`Refs #10`, per the T2 README), or open a new edge/CPU follow-up issue? | #10 co-owners (@Mattycodes69, @appletechie) |
| Can the existing accelerator memory field represent a dedicated on-module pool for COMPUTE-01, or is a memory-kind distinction needed? | #40 (@tynamite) with #10 |
| Which Windows driver and runtime release (if any) supports the UGen300, and when Android support becomes generally available | Open; any contributor, from a primary source |
| Does v1 need a `host_link` field on `accelerator` (link type and rate), or does the #40 contract already cover it? | #40 (@tynamite) with #10 (@Mattycodes69) |
| Independent measurement protocol for small-model throughput on attachable accelerators, pinned under the #41 comparability rule | #10 co-owners; T6 evaluation (#115) |
| Should the builder offer "add an accelerator" as an upgrade step for CPU-only builds from deployment-mode.md? | T0 (@tynamite) |
| First-generation Coral Edge TPU: current availability and specs from a primary source | Open; any contributor |
