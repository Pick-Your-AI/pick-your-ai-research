# Post-training ONNX conversion boundary

Refs #30, #33 and #11. Source checked 2026-10-18; no model export or inference was run. This narrows the ONNX question in the training-framework record without adding ONNX to any framework's native output formats.

## Published mechanisms

- Hugging Face's [PEFT checkpoint guide](https://huggingface.co/docs/peft/developer_guides/checkpoint), mutable documentation accessed 2026-10-18, documents merging eligible adapter weights into the base model and saving the resulting ordinary model. An adapter checkpoint alone omits the base weights. Merge support depends on the PEFT method and settings, including quantization; it is not universal. The merged artifact loses PEFT-specific adapter management and contains the base weights as well. Evidence: primary documentation, source checked, not reproduced.
- Hugging Face's [Optimum ONNX export guide](https://huggingface.co/docs/optimum-onnx/onnx/usage_guides/export_a_model), mutable documentation accessed 2026-10-18, documents export from a local model directory. A local checkpoint needs an explicit supported task to retain the intended task-specific head. Architecture/task support, opset, precision and exporter configuration matter. Its example validates output names, shapes and numerical agreement; this is a publisher example, not our test. Some optional graph optimizations target ONNX Runtime specifically and can restrict portability to other engines. Evidence: primary documentation, source checked, not reproduced.

## Bounded inference and remaining proof

These two documented mechanisms support a candidate conversion workflow: an eligible merged Transformers checkpoint may be exported through a separately compatible Optimum ONNX configuration. They do not establish that every PEFT checkpoint, every training framework, quantized base or model architecture exports successfully. Treat the composition as a hypothesis until an exact tuple is exercised. Native training output and downstream conversion are separate capabilities; the existing framework catalog formats remain unchanged.

For a reproducible test, #30/#33 should supply base and adapter revisions, method, precision, merge settings, tokenizer/configuration, and exported artifact hashes. Pin PEFT, Transformers, PyTorch, Optimum ONNX, ONNX/opset and target runtime versions. Record the selected task/head, input shapes and dynamic axes, export diagnostics, numerical tolerance and parity inputs. #11/#36 need target-runtime loading, inference and task-quality evidence beyond file creation. Preserve base/adapter provenance and applicable rights; conversion grants no redistribution permission. Do not enable remote model code merely to complete this test without its separate security review.

Disposition: a public post-processing route is documented; native candidate-specific ONNX support and successful end-to-end conversion remain unresolved. This note neither completes #30 nor supplies receiving-owner acceptance.
