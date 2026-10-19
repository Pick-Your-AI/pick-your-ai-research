# Experimental MR-09 initialization estimator

This is the minimal project derivative selected by [D61-02](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/61#issuecomment-6249525648). It patches GPUStack gguf-parser-go v0.26.4 at `637cd9a7a03993ab30ace3c53dd8af5c37f46a94`; the complete source tree, patch, tests, dependency files and upstream MIT license have explicit pins. The [comparison specification](../mr09-comparison-spec-2026-10-18.md) retains the original upstream estimate as unmatched. This preparation provides CPU semantics tests, not a native measurement or accepted estimator comparison.

## Scoped change

The new API requires an explicit `MR09InitBufferProfile` and hashes and parses the same private snapshot of the complete GGUF bytes. It supports bounded ordinary dense causal llama models, F16 matrices and F16/F32 vectors, one CUDA0 with all layers/output offloaded, mmap and KV/operation offload, F16 K/V, and completed initialization before free. Embeddings, Flash Attention and backend samplers must explicitly be disabled. Specialized architectures, unsupported tensor shapes and controls fail with errors. No model or GPU code executes.

For the pinned llama.cpp runtime `620d2225cc436ab0b001e3200e590e3b286ef9ab`, initial host logits readback has `sequence_capacity` rows. The output graph has `min(context_size, physical_batch_size, outputs_max)` rows and belongs to the output weight's CUDA0 backend. The per-sequence output maximum remains distinct from the global maximum. H3 retains total context 512, sequence capacity 2, per-sequence context 256 and zero declared populated cache, active requests and generated tokens. Those zero values describe the selected initialization stage; they are not observed telemetry.

The ordinary upstream API remains unchanged when the profile is absent. Complete JSON hashes preserve its development/H1/H2/H3 estimates. Existing `Footprint + Input + max(Compute, Output)` aggregation, graph allocator/lifetime approximations, CPU-mapped embedding terms, wrapper/copy exclusions and all non-output calculations remain unchanged. No additive correction is fitted to the historical native total. This estimator still needs prospective held-out observations, an independently selected tolerance and explicit receiving review before any accepted comparison.

## Reproduce CPU preparation

Use Python 3.12+, Git, a local checkout containing the exact upstream commit and Go 1.22.9. No model weights are required. Run from this research repository:

```bash
python scripts/mr09_prepare_estimator.py \
  --upstream /path/to/gguf-parser-go \
  --go /path/to/go/bin/go \
  --module-cache /path/to/existing/go/pkg/mod \
  --build-cache /path/to/owned/go-build-cache \
  --output-dir /tmp/mr09-estimator-preparation
```

The output directory must be new. The default preparation uses cached dependencies with `GOPROXY=off`; `--allow-module-download` explicitly permits fetching dependencies named by the pinned upstream module files. It never downloads an artifact, invokes upstream tests that fetch models, runs the native capture harness or contacts participants. Preserve sufficient local space for the compiler cache and executable.

The runner independently archives the pinned upstream tree, reproduces the original three failing semantic assertions with the original fixture, applies the small patch, runs only the meaningful `TestMR09` CPU regressions and builds the experimental command. It then executes ten actual CLI admission cases using a complete tiny synthetic file, including alias-only and canonical-plus-alias rejection. The resulting `candidate-manifest.json` pins the actual compiler, module files, complete package, effective build controls, executable bytes/hash, commands and the actual CPU log and CLI admission hashes. Preserve that manifest and its raw output outside Git. Build paths can affect the executable identity; a new build must retain its own actual manifest and cannot inherit another executable's receipt.

## Prepare a prediction

The built command accepts a separately pinned lowercase SHA-256 and complete flat JSON profile through `--sha256` and `--profile`. Supply the actual local GGUF as a **regular file on standard input**; pipes, empty files, files above 512 MiB, duplicate/unknown JSON fields, missing controls, artifact drift and unsupported profiles reject. All profile fields and spellings appear in the synthetic regression source and the patch. Pin the independently reviewed artifact and declared controls before invoking the command; a hash match does not authenticate a caller's record or establish that a native run used those controls.

```bash
/path/to/mr09-init-estimate \
  --sha256 "$ARTIFACT_SHA256" \
  --profile "$EXPLICIT_PROFILE_JSON" \
  < /path/to/pinned-artifact.gguf \
  > /path/to/prediction.json
```

Before any future hardware comparison, retain the candidate executable manifest, this exact package and profile, the actual artifact pin, command and unmodified prediction output. Separately satisfy the comparison specification's native source/build/raw-artifact and held-out tuple requirements. The original whole-runtime, named comparator, dense/MoE/context/KV/concurrency/multi-GPU and empirical error-bound criteria remain open. No native measurement has been produced by this package.
