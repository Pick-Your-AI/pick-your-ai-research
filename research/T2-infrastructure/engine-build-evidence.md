# vLLM GGUF plugin and ROCm build evidence

Supplement to [the #11 decision record](inference-engine.md). Sources inspected
2026-10-18 UTC. Grade: primary publisher source, source checked / **unverified**.
This is documentation research: no wheel, inference engine, model weights or GPU
workload was installed or executed. Published requirements do not establish a
working joint configuration.

## Immutable source identities

| Component | Examined identity | Meaning |
| --- | --- | --- |
| vLLM | `v0.31.0`, commit `db9527a46873454610df6dbedf79a36d6bf1a7f6` | Source release used by the existing engine proposal |
| vLLM GGUF plugin | `v0.0.5`, commit `d358f564fc8f470cddd7c141a149b4ebafafa01f` | Plugin release examined here; published 2026-08-10, according to [release metadata](https://api.github.com/repos/vllm-project/vllm-gguf-plugin/releases/tags/v0.0.5) |

The source identities can be checked through the [engine tag](https://api.github.com/repos/vllm-project/vllm/git/ref/tags/v0.31.0)
and [plugin tag](https://api.github.com/repos/vllm-project/vllm-gguf-plugin/git/ref/tags/v0.0.5).
These two releases were selected for inspection, not established as a tested pair.

## GGUF requirements and unresolved compatibility

The engine's [GGUF documentation](https://github.com/vllm-project/vllm/blob/db9527a46873454610df6dbedf79a36d6bf1a7f6/docs/features/quantization/gguf.md)
calls the feature experimental and requires the out-of-tree plugin. Its install
example leaves the plugin version unspecified. It recommends the base model's
tokenizer because GGUF tokenizer conversion can be unstable; a separate model
configuration may also be needed. A file suffix alone is insufficient evidence.

The plugin's [release metadata in pyproject.toml](https://github.com/vllm-project/vllm-gguf-plugin/blob/d358f564fc8f470cddd7c141a149b4ebafafa01f/pyproject.toml)
declares Python >=3.10, torch >=2.9, gguf >=0.17.0 and an **unversioned vllm
dependency**. It registers a vLLM general plugin. These lower bounds and the
absence of an engine pin do not prove ABI compatibility with vLLM v0.31.0, nor
prove incompatibility. The code license is Apache-2.0; model rights remain separate.

The [plugin README](https://github.com/vllm-project/vllm-gguf-plugin/blob/d358f564fc8f470cddd7c141a149b4ebafafa01f/README.md)
describes CUDA or ROCm prerequisites and recommends building against the same
PyTorch as the vLLM runtime, without build isolation. Its bounded model/quantization
examples do not certify every architecture supported by vLLM. The
[build script](https://github.com/vllm-project/vllm-gguf-plugin/blob/d358f564fc8f470cddd7c141a149b4ebafafa01f/setup.py)
detects HIP through PyTorch and omits a CUDA-only fast-math flag on that path.
This is source evidence for a conditional ROCm build path, not a successful AMD run.

### Published artifacts are backend-specific

The pinned [release workflow](https://github.com/vllm-project/vllm-gguf-plugin/blob/d358f564fc8f470cddd7c141a149b4ebafafa01f/.github/workflows/release.yml)
builds CUDA 12.9 and 13.0 variants on x86_64 and aarch64 with Python 3.11. The
12.9 variant gets a `+cu129` suffix; unsuffixed wheels come from the CUDA 13.0
jobs. Their `cp310-abi3` filename is not a claim that the build used Python 3.10.
No ROCm wheel was identified in the inspected release asset list or this workflow.
That scoped observation does not negate the documented source-build path.

Two x86_64 assets illustrate the distinction. Sizes and SHA-256 values below are
**publisher-reported API metadata**, not locally downloaded or recomputed hashes.
They are not a verified evidence manifest or an installation recommendation.

| Asset | Published bytes | Published SHA-256 |
| --- | ---: | --- |
| `vllm_gguf_plugin-0.0.5+cu129-cp310-abi3-manylinux_2_28_x86_64.whl` | 4,967,134 | `ce7f8a61bcd5d882e11aada37dabb0066a68b1d18e6816c144fe738bce54ad15` |
| `vllm_gguf_plugin-0.0.5-cp310-abi3-manylinux_2_28_x86_64.whl` | 6,406,192 | `e795779830ad8907cb0e51bf661dd7784ebaf244b0b324af07a8d3925b6a9739` |

Source: [v0.0.5 release assets](https://api.github.com/repos/vllm-project/vllm-gguf-plugin/releases/tags/v0.0.5),
accessed 2026-10-18. The same response lists aarch64 variants and a source archive.
The consumer must identify and verify its selected artifact independently.

## ROCm installation and build scope

The pinned [ROCm installation include](https://github.com/vllm-project/vllm/blob/db9527a46873454610df6dbedf79a36d6bf1a7f6/docs/getting_started/installation/gpu.rocm.inc.md)
gives a general ROCm 6.3 minimum, with stricter device-specific requirements:
MI350 requires 7.0+ and Ryzen AI requires 7.0.2+. Its wheels require Python 3.12
and glibc >=2.35. The `rocm700` table is scoped to vLLM v0.14.0–v0.18.0;
`rocm721` describes a nightly transition after commit
`171775f306a333a9cf105bfd533bf3e113d401d9`. Neither row identifies a tested
v0.31.0 wheel/digest. The page warns that a Python mismatch can select a CUDA
wheel. Source and precompiled development paths also have different prerequisites.

The two recipe files give more precise *declared build defaults*:

| Source at vLLM's pinned commit | Observed defaults | Reproducibility limit |
| --- | --- | --- |
| [Dockerfile.rocm](https://github.com/vllm-project/vllm/blob/db9527a46873454610df6dbedf79a36d6bf1a7f6/docker/Dockerfile.rocm) | `REMOTE_VLLM=0`; remote mode defaults to branch `main`; base tags `rocm/vllm-dev:base` and `rocm/vllm-dev:ci_base`; Triton kernels ref `669b31acc1dd1b3fd93286afd5db67f65d9f7557` | Local mode uses the supplied source tree. Selecting remote mode without overriding its branch can build a different engine revision. Mutable base tags do not identify image contents. |
| [Dockerfile.rocm_base](https://github.com/vllm-project/vllm/blob/db9527a46873454610df6dbedf79a36d6bf1a7f6/docker/Dockerfile.rocm_base) | `rocm/dev-ubuntu-22.04:7.2.3-complete`; Python 3.12; PyTorch ref `733fca1`; Triton ref `669b31a`; FlashAttention ref `0e60e394`; AITER `v0.1.23`; MORI `v1.1.0` | These are recipe defaults, including short refs and tags, not a complete immutable dependency lock or a tested stack. |

Pinning the recipe source does not pin its base image digest, package resolution,
local build context or every dependency. No image digest, driver compatibility,
actual GPU architecture, runtime success or performance measurement is asserted.

## Consumer decision and next evidence

Keep GGUF out of the existing flat vLLM CatalogItem format subset. A plugin source
pin is now available, but that array cannot express plugin/backend/model conditions.
Adding `gguf` would overstate what this work establishes. Do not infer a Cartesian
product between the plugin's ROCm source path, the engine's GPU list and every GGUF.
The conditional tuple and migration belong to #40; the imported v1 contract is
unchanged.

For an actual selected build, #11/#10/#37 need a manifest retaining the engine and
plugin revisions, selected artifact hashes, Python/PyTorch/ROCm/kernel/compiler
versions, source context and resolved dependencies, GPU architecture/driver/topology,
model and tokenizer revisions, quantization details, adapter lineage and serving
configuration. #33 owns adapter lineage; #10 owns admission/KV/capacity. Keep
documentation-supported constraints distinct from installation and behavioral tests.

The plugin source-version gap is narrowed. Joint vLLM v0.31.0/plugin v0.0.5
compatibility and the exact ROCm binary/runtime tuple remain **unknown**. A later
authorized experiment must record its actual inputs and outcomes; this note supplies
neither hardware authorization nor an independently verified support result.
